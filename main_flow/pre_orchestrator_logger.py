from main_flow.agent_config.MainFlowState import MainFlowState
from main_flow.prompt.pre_orchestrator_logger_prompt import (
    PRE_ORCHESTRATOR_LOGGER_PROMPT,
    PreOrchestratorLoggerOutput
)
from app.llm.invoke_openai_llm import invoke_openai_llm
from app.finance_agent.repository.flow_repo import FlowRepo
from app.finance_agent.models.flow import FlowCreate
from uuid import UUID


def pre_orchestrator_logger_node(state: MainFlowState):
    print("[INVOKE][pre_orchestrator_logger_node]")

    # Use flow_uuid from state (generated in main_flow.py)
    flow_uuid = state.flow_uuid
    print(f"[PRE_ORCHESTRATOR_LOGGER] Using flow_uuid: {flow_uuid}")

    # Extract data from state
    user_input = state.user_input or ""
    classifier_msg = state.classifier_msg or ""

    print(f"[PRE_ORCHESTRATOR_LOGGER] User input: {user_input[:100]}...")
    print(f"[PRE_ORCHESTRATOR_LOGGER] Classifier message: {classifier_msg[:100]}...")

    # Format prompt for LLM
    prompt = PRE_ORCHESTRATOR_LOGGER_PROMPT.format(
        user_input=user_input,
        classifier_message=classifier_msg
    )

    print("[PRE_ORCHESTRATOR_LOGGER] Invoking LLM for summarization...")

    try:
        # Use LLM to generate summary
        logger_output: PreOrchestratorLoggerOutput = invoke_openai_llm(prompt, PreOrchestratorLoggerOutput)

        summary = logger_output.summary
        user_intent = logger_output.user_intent
        identified_agents = logger_output.identified_agents

        print(f"[PRE_ORCHESTRATOR_LOGGER] Summary: {summary}")
        print(f"[PRE_ORCHESTRATOR_LOGGER] User intent: {user_intent}")

        # Get session_id from client.py (passed through state)
        session_id = state.session_id
        print(f"[PRE_ORCHESTRATOR_LOGGER] Using session_id from client: {session_id}")

        # Write to database using FlowRepo
        print("[PRE_ORCHESTRATOR_LOGGER] Writing to database...")
        flow_repo = FlowRepo()

        # Keep UUIDs as strings - psycopg2 will handle the conversion to uuid type
        # Avoids "can't adapt type 'UUID'" error
        flow_uuid_str = str(flow_uuid) if not isinstance(flow_uuid, str) else flow_uuid
        session_uuid_str = str(session_id) if not isinstance(session_id, str) else session_id

        flow_data: FlowCreate = {
            'id': flow_uuid_str,
            'session_id': session_uuid_str,
            'identified_agents': identified_agents,
            'user_request_summary': summary
        }
        flow_repo.create(flow_data)
        print(f"[PRE_ORCHESTRATOR_LOGGER] ✓ Successfully logged to flow_table with UUID: {flow_uuid}")

        # Return updated state with flow_uuid
        return {
            "flow_uuid": flow_uuid
        }

    except Exception as e:
        print(f"[PRE_ORCHESTRATOR_LOGGER ERROR] Failed to log: {e}")
        # Continue flow even if logging fails - don't block orchestration
        return {
            "flow_uuid": flow_uuid  # Return UUID even if logging failed
        }
