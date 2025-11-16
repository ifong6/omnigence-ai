from app.main_flow.prompt.intent_analyzer_prompt_template import INTENT_PROMPT_TEMPLATE, IntentClassifierOutput
from app.schemas.finance_agent_state import FinanceAgentState
from app.llm.invoke_claude_llm import invoke_claude_llm

def intent_analyzer_node(state: FinanceAgentState):
    print("[INVOKE][intent_analyzer_agent]")
    
    try:
        system_prompt = INTENT_PROMPT_TEMPLATE.format(user_input=state.user_input)
        parsed_response = invoke_claude_llm(system_prompt, IntentClassifierOutput)
        
    except Exception as e:
      print(f"[Error][intent_analyzer_agent]: {str(e)}")
        

    return {
        "intents": parsed_response.get("intents", []),
    }
    