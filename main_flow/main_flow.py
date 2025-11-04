from langchain_core.messages import HumanMessage
from main_flow.agent_config.MainFlowState import MainFlowState
from main_flow.agent_config.agent_registry import AGENT_NODES, STATIC_EDGES
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from main_flow.utils.Request.UserRequest import UserRequest
from main_flow.utils.Exception.InterrutpException import InterruptException
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

#---------------------------------------------------------------#
#                      MAIN AGENTIC FLOW                        #
#---------------------------------------------------------------#
def main_flow(user_request: UserRequest):
    # Generate unique flow_uuid for this flow execution
    flow_uuid = str(uuid.uuid4())
    print(f"[MAIN FLOW] Generated flow_uuid: {flow_uuid} for session: {user_request.session_id}")

    initial_state = {
        "user_input": user_request.message,
        "messages": [HumanMessage(content=user_request.message)],
        "session_id": user_request.session_id,  # Pass session_id for logging
        "flow_uuid": flow_uuid,  # Unique identifier for this flow execution
    }
    config = cast(RunnableConfig, {
        "configurable": {
            "thread_id": user_request.session_id
        }
    })
    
    print("[MAIN FLOW] Invoking main agentic graph...\n")
    result = graph.invoke(initial_state, config=config)  # receive entire MainFlowState object here
    
    # HITL
    if "__interrupt__" in result:
        print(result['__interrupt__'])
        interrupt_info = result["__interrupt__"][0]
        value = interrupt_info.value
        resumable = True
        ns = None

        # 通常是单个中断
        raise InterruptException(
            state=result,
            value=value,
            resumable=resumable,
            ns=ns
        )
        
    agent_response = result.get("final_response")
    print(f"agent_response:\n\n {agent_response}")
    return agent_response


#---------------------------------------------------------------#
#                      RESUME AGENTIC FLOW                      #
#---------------------------------------------------------------#
def resume_agent(user_request: UserRequest):
    print("[RESUME_AGENT] resume agentic graph...\n")
    config = cast(RunnableConfig, {
        "configurable": {
            "thread_id": user_request.session_id
        }
    })

    initial_state = {
        "human_feedback": [user_request.message],
    }

    print("human_feedback:", user_request.message)
    
    try:
        command = Command(resume=initial_state)
        result = graph.invoke(command, config)
        
        return {
            "status": "resumed", 
            "result": result
        }

    except Exception as e:
        print("error:", {str(e)})
        return {str(e)}

  
  

