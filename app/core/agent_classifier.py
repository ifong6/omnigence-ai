from app.core.agent_config.MainFlowState import MainFlowState
from app.llm.invoke_claude_llm import invoke_claude_llm
from app.prompt.agent_classifier_prompt_template import CLASSIFIER_SYSTEM_PROMPT, AgentClassifierOutput


def agent_classifier_node(state: MainFlowState):
    print("[INVOKE][agent_classifier_node]")

    system_prompt = CLASSIFIER_SYSTEM_PROMPT.format(user_input=state.user_input)
    parsed_response = invoke_claude_llm(system_prompt, AgentClassifierOutput)

    try:
        # parsed_response is a Pydantic model object, access via attributes
        identified_agents = parsed_response.identified_agents or []
        llm_result_msg = parsed_response.classifier_msg or ""

        return {
            "identified_agents": identified_agents,
            "classifier_msg": llm_result_msg,  # Store classifier message for logging
        }

    except Exception as e:
        error_msg = "[Error][agent_classifier_node]: " + str(e)
        print(error_msg)

        return {
            "identified_agents": ["unknown"],
            "classifier_msg": error_msg,  # Store error message
        }

 

    
  
    