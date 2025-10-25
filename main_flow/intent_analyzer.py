from main_flow.prompt.intent_analyzer_prompt_template import INTENT_PROMPT_TEMPLATE, IntentClassifierOutput
from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.llm.invoke_gemini_llm_streaming import invoke_gemini_llm_streaming

def intent_analyzer_node(state: FinanceAgentState):
    print("[INVOKE][intent_analyzer_agent]")
    
    try:
        system_prompt = INTENT_PROMPT_TEMPLATE.format(user_input=state.user_input)
        parsed_response = invoke_gemini_llm_streaming(system_prompt, IntentClassifierOutput)
        
    except Exception as e:
      print(f"[Error][intent_analyzer_agent]: {str(e)}")
        

    return {
        "intents": parsed_response.get("intents", []),
    }
    