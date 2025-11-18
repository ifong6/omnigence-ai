Here's a cleaned-up, HR-free version with the broken characters fixed and the architecture described in plain ASCII. I kept your structure but simplified the diagrams and made sure they reflect the current reality: **only finance-related agents are implemented** (others are future).

---

# Main Flow Architecture

## Overview

The main flow orchestrates AI agent workflows using LangGraph. It:

1. Receives user requests via the AgentController.
2. Classifies user intent with a classifier agent.
3. Logs the flow state for audit.
4. Routes the request to domain-specific agents (currently **finance** only; other agents are planned).
5. Aggregates agent responses into a final answer.

---

## Main Flow Diagram

```text
+---------------------------+
|          CLIENT           |
|  POST /api/agents/        |
|      orchestrator         |
+-------------+-------------+
              |
              |  UserRequest { session_id, message }
              v
+---------------------------+
|     AgentController       |
| orchestrator_agent_flow() |
+-------------+-------------+
              |
              v
+-----------------------------------------------------+
|            ORCHESTRATOR AGENT GRAPH                 |
|                     (LangGraph)                     |
|                                                     |
|  State: MainFlowState                               |
|  -----------------------------------------------    |
|   - session_id: str                                 |
|   - user_input: str                                 |
|   - identified_agents: list[str]                    |
|   - agent_responses: dict[str, Any]                 |
|   - final_response: str | dict                      |
|   - flow_uuid: str                                  |
|                                                     |
|   START                                             |
|     |                                               |
|     v                                               |
|  [NODE 1] classifier_agent                          |
|     |  Input:  state.user_input                     |
|     |  Action: LLM decides which agents to call     |
|     |  Output: state.identified_agents              |
|     v                                               |
|  [NODE 2] pre_routing_logger                        |
|     |  Input:  state (after classification)         |
|     |  Action: log flow to DB                       |
|     |  Output: state.flow_uuid                      |
|     v                                               |
|  [NODE 3] workflow_router                           |
|     |  Input:  state.identified_agents              |
|     |  Action: call domain agents (HTTP)           |
|     |  Output: state.agent_responses                |
|     v                                               |
|  [NODE 4] aggregation_agent                         |
|        Input:  state.agent_responses                |
|        Action: synthesize final answer              |
|        Output: state.final_response                 |
|                                                     |
|   END                                               |
+-----------------------------------------------------+
              |
              | final_response
              v
+---------------------------+
|     AgentController       |
|  returns JSON response    |
+-------------+-------------+
              |
              v
+---------------------------+
|          CLIENT           |
|     Receives response     |
+---------------------------+
```

---

## Routing Logic Detail

```text
workflow_router
    |
    |  state.identified_agents = ["finance_agent"]
    v

+----------------------------+
|     AGENT REGISTRY         |
+----------------------------+
| agent_endpoints = {        |
|   "finance_agent": {       |
|       "url": "localhost:8001",
|       "endpoint": "/finance"
|   },                       |
|   "reporting_agent": {     |  # planned / optional
|       "url": "localhost:8003",
|       "endpoint": "/reporting"
|   }                        |
| }                          |
+----------------------------+
    |
    v
+----------------------------+
|  HTTP POST (per agent)     |
+----------------------------+
| Request body:              |
| {                          |
|   "session_id": "...",     |
|   "user_input": "...",     |
|   "flow_uuid": "..."       |
| }                          |
+----------------------------+
    |
    v
+------------------------------------------+
|           FINANCE AGENT (Block)          |
+------------------------------------------+
| FinanceAgentState                        |
|  - session_id                            |
|  - user_input                            |
|  - intent                                |
|  - job_type (DESIGN / INSPECTION)        |
|  - company_name                          |
|  - project_name                          |
|  - result                                |
+------------------------------------------+
| Nodes:                                   |
|  1. intent_analyzer → extract intent     |
|  2. crud_react_agent → execute action    |
|                                          |
| Tools used:                              |
|  - JobServiceImpl.create_job()           |
|  - QuotationServiceImpl.create_quotation() (example)
|  - CompanyServiceImpl.get_or_create()    |
+------------------------------------------+
    |
    | returns result
    v
+----------------------------+
| workflow_router collects   |
| state.agent_responses[     |
|   "finance_agent"          |
| ] = result                 |
+----------------------------+
```

---

## Classifier Agent Logic

```text
+----------------------------------------------+
|              CLASSIFIER AGENT                |
+----------------------------------------------+

LLM Prompt (simplified):

"Given the user message, identify which agents
should handle this.

Available Agents (current / near-term):
- finance_agent: quotations, invoices, jobs, billing
- reporting_agent: analytics, reports, dashboards

User Message: '{user_input}'

Return a JSON array of agent names."

Examples:

Input:  "Create a quotation for HVAC design"
Output: ["finance_agent"]

Input:  "I need an inspection job with budget analysis"
Output: ["finance_agent", "reporting_agent"]

Input:  "Show me a dashboard of monthly revenue"
Output: ["reporting_agent"]

Input:  "What's our quarterly revenue?"
Output: ["reporting_agent"]
```

*(Note: HR agent is not implemented yet, so it is intentionally omitted from the available agents and examples.)*

---

## State Flow Visualization

```text
+----------------------------------------------+
|             STATE TRANSITIONS                |
+----------------------------------------------+

INITIAL STATE
----------------------------------------------
{
  session_id: "user-123",
  user_input: "Create a quotation for ABC Company",
  identified_agents: [],
  agent_responses: {},
  final_response: "",
  flow_uuid: ""
}

    |
    v  classifier_agent

AFTER CLASSIFICATION
----------------------------------------------
{
  ...
  identified_agents: ["finance_agent"],  # UPDATED
  ...
}

    |
    v  pre_routing_logger

AFTER LOGGING
----------------------------------------------
{
  ...
  flow_uuid: "abc-123-def-456",          # UPDATED
  ...
}

    |
    v  workflow_router

AFTER ROUTING
----------------------------------------------
{
  ...
  agent_responses: {                     # UPDATED
    "finance_agent": {
      "status": "success",
      "job_no": "J-JCP-25-11-1",
      "quo_no": "Q-JCP-25-11-1-R00"
    }
  },
  ...
}

    |
    v  aggregation_agent

FINAL STATE
----------------------------------------------
{
  ...
  final_response: "I've created quotation Q-JCP-25-11-1-R00 for ABC Company..."
}
```

---

## Error Handling & HITL (User Clarification)

For missing or invalid information (e.g. empty company/project), the finance agent should **not** create a job but instead request clarification from the user.

```text
workflow_router
    |
    v
+----------------------------+
|       Finance Agent        |
+----------------------------+
| if missing_required_field: |
|    raise InterruptException|
+----------------------------+
    |
   / \
  /   \
 v     v
Success        InterruptException
 |             |
 v             v

Normal Response                 User Clarification Response
-----------------              ---------------------------
{                               {
  "status": "success",            "status": "interrupt",
  "session_id": "...",            "session_id": "...",
  "result": {...}                 "requires_feedback": true,
}                                 "result": "Need valid company and project name"
                                  }
                                   |
                                   v
                        Client (user) provides updated info
                                   |
                                   v
                     POST /api/agents/human-in-the-loop
                                   |
                                   v
                           resume_agent(request)
                                   |
                                   v
                        Finance Agent resumes with
                            updated state
```

> In this flow, “human-in-the-loop” refers to **the end user** being asked to provide missing or corrected inputs, not an internal reviewer.

---

## File References

| Component       | File Path                                 |
| --------------- | ----------------------------------------- |
| Entry Point     | `app/core/orchestrator_agent.py`          |
| Classifier Node | `app/core/agent_classifier.py`            |
| Logger Node     | `app/core/pre_routing_logger_node.py`     |
| Router Node     | `app/core/workflow_router.py`             |
| Aggregator Node | `app/core/aggregation_agent.py`           |
| Main State      | `app/schemas/main_flow_state.py`          |
| Finance Agent   | `app/finance_agent/finance_agent_flow.py` |
| Finance State   | `app/schemas/finance_agent_state.py`      |
| Controller      | `app/controllers/agent_controller.py`     |

---

## Key Design Decisions

1. **Parallel Agent Execution**
   The workflow router can use a `ThreadPoolExecutor` (or async) to call multiple agents concurrently.

2. **Stateless HTTP Dispatch**
   Each domain agent (finance, reporting, etc.) is exposed as an HTTP endpoint, making it deployable as a separate service.

3. **LLM-based Classification**
   The classifier agent uses natural language understanding to decide which agents should handle a request.

4. **Audit Trail**
   Each flow is logged with a `flow_uuid` and key metadata in the database for traceability and debugging.

5. **User-Facing HITL**
   When required inputs are missing or invalid, the graph raises an interrupt and returns a response asking the **user** to clarify before continuing.

6. **Aggregation**
   The aggregation agent merges one or more agent responses into a coherent final message for the client.

If you want, I can also generate a shorter “developer-friendly” version of this for your project README, and keep this full one as an internal architecture doc.
