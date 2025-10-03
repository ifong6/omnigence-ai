from app.main_agent.intent_analyzer_prompt_template import INTENT_PROMPT_TEMPLATE, IntentClassifierOutput
from langchain.schema import AIMessage
from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.llm.invoke_llm import invoke_llm

def intent_analyzer_node(state: FinanceAgentState):
    print("[INVOKE][intent_analyzer_agent]")
    
    try:
        system_prompt = INTENT_PROMPT_TEMPLATE.format(user_input=state.user_input)
        parsed_response = invoke_llm(system_prompt, IntentClassifierOutput)
        
    except Exception as e:
      print(f"[Error][intent_analyzer_agent]: {str(e)}")
        
    return {
        "intents": parsed_response.get("intents", []),
        "messages": [AIMessage(content=parsed_response.get("messages", ""))]
    }
    
    
