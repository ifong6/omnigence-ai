# app/core/orchestrator_agent.py
from app.core.agent_config.MainFlowState import MainFlowState
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from app.core.agent_config.agent_registry import AGENT_NODES, STATIC_EDGES
from app.utils.requests import UserRequest
from app.utils.exceptions import InterruptException
import uuid
from typing import cast

workflow_builder = StateGraph(MainFlowState)

# register nodes
for agent_name, node in AGENT_NODES.items():
    workflow_builder.add_node(agent_name, node)

# wire static edges
for source, path in STATIC_EDGES:
    workflow_builder.add_edge(source, path)

workflow_builder.set_entry_point("classifier_agent")
graph = workflow_builder.compile(checkpointer=MemorySaver())


# ==============================================================================
# Orchestrator Agent Flow (Graph Wrapper)
# ==============================================================================

def orchestrator_agent_flow(user_request: UserRequest) -> MainFlowState:
    """
    统一入口：
    - 入参:UserRequest
    - 出参:MainFlowState(其中 final_response 由 aggregation_agent_node 写入）
    """
    flow_uuid = str(uuid.uuid4())
    print(
        f"[ORCHESTRATOR FLOW] Generated flow_uuid: {flow_uuid} "
        f"for session: {user_request.session_id}"
    )

    initial_state = MainFlowState(
        user_input=user_request.message,
        messages=[HumanMessage(content=user_request.message)],
        session_id=user_request.session_id,
        flow_uuid=flow_uuid,
    )

    config = cast(
        RunnableConfig,
        {
            "configurable": {
                "thread_id": user_request.session_id,
            }
        },
    )

    print("[ORCHESTRATOR FLOW] Invoking orchestrator graph...\n")
    orchestrator_response = graph.invoke(initial_state, config=config)

    # 这里按 LangGraph interrupt 机制处理（如果有中断）
    if isinstance(orchestrator_response, dict) and "__interrupt__" in orchestrator_response:
        print(orchestrator_response["__interrupt__"])
        interrupt_info = orchestrator_response["__interrupt__"][0]
        value = interrupt_info.value
        resumable = True
        ns = None

        raise InterruptException(
            state=orchestrator_response,
            value=value,
            resumable=resumable,
            ns=ns,
        )

    # 正常情况: orchestrator_response 就是 MainFlowState
    if not isinstance(orchestrator_response, MainFlowState):
        # 兜底(极少数情况下 orchestrator_response 可能是 dict)
        orchestrator_response = MainFlowState(**orchestrator_response)  # type: ignore[arg-type]

    print(f"[ORCHESTRATOR FLOW] Final response on state:\n\n{orchestrator_response.final_response}")
    return orchestrator_response


#---------------------------------------------------------------#
#                      RESUME AGENTIC FLOW                      #
#---------------------------------------------------------------#

def resume_agent(user_request: UserRequest):
    print("[RESUME_AGENT] resume agentic graph...\n")
    config = cast(
        RunnableConfig,
        {
            "configurable": {
                "thread_id": user_request.session_id,
            }
        },
    )

    initial_state = {
        "human_feedback": [user_request.message],
    }

    print("human_feedback:", user_request.message)

    try:
        command = Command(resume=initial_state)
        result = graph.invoke(command, config)

        return {
            "status": "resumed",
            "result": result,
        }

    except Exception as e:
        print("error:", {str(e)})
        return {str(e)}