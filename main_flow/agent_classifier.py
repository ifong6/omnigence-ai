from main_flow.agent_config.MainFlowState import MainFlowState
from langchain_core.messages import AIMessage
from main_flow.prompt.agent_classifier_prompt_template import CLASSIFIER_SYSTEM_PROMPT, AgentClassifierOutput
from app.llm.invoke_llm import invoke_llm
    
def agent_classifier_node(state: MainFlowState):
    print("[INVOKE][agent_classifier_node]")
  
    system_prompt = CLASSIFIER_SYSTEM_PROMPT.format(user_input=state.user_input)
    parsed_response = invoke_llm(system_prompt, AgentClassifierOutput)

    try:
        agents = parsed_response.get("agents", []) or ["unknown"]
        llm_result_msg = parsed_response.get("messages", [])[-1]
        human_clarification_flag = parsed_response.get("human_clarification_flag", False)
        
        return {
            "agents": agents,
            "messages": [AIMessage(content=llm_result_msg)],
            "human_clarification_flag": human_clarification_flag
        }

    except Exception as e:
        return {
            "agents": ["unknown"],
            "messages": [AIMessage(content="[Error][intent_agent_node]: " + str(e))],
        }

 

    
  
    