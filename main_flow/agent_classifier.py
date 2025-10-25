from main_flow.agent_config.MainFlowState import MainFlowState
from main_flow.prompt.agent_classifier_prompt_template import CLASSIFIER_SYSTEM_PROMPT, AgentClassifierOutput
from app.llm.invoke_gemini_llm_streaming import invoke_gemini_llm_streaming
 
   
def agent_classifier_node(state: MainFlowState):
    print("[INVOKE][agent_classifier_node]")
  
    system_prompt = CLASSIFIER_SYSTEM_PROMPT.format(user_input=state.user_input)
    parsed_response = invoke_gemini_llm_streaming(system_prompt, AgentClassifierOutput)

    try:
        identified_agents = parsed_response.get("identified_agents", []) or ["unknown"]
        llm_result_msg = parsed_response.get("classifier_msg", "")
        human_clarification_flag = parsed_response.get("human_clarification_flag", False)

        return {
            "identified_agents": identified_agents,
            "classifier_msg": llm_result_msg,  # Store classifier message for logging
            "human_clarification_flag": human_clarification_flag
        }

    except Exception as e:
        error_msg = "[Error][agent_classifier_node]: " + str(e)
        print(error_msg)
        
        return {
            "identified_agents": ["unknown"],
            "classifier_msg": error_msg,  # Store error message
        }

 

    
  
    