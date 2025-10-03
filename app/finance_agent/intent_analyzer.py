from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from langchain_core.messages import AIMessage
from pydantic import BaseModel
from typing import List, Optional
from app.llm.invoke_llm import invoke_llm

class FinanceIntentOutput(BaseModel):
    intents: List[str]
    messages: List[str]
    human_clarification_flag: bool

FINANCE_INTENT_ANALYZER_PROMPT = """
    You are a finance domain intent analyzer. Your job is to analyze user input and identify specific finance-related intents.

    Step 1: Analyze user input for finance-related queries

        User input:
        ```text
        {user_input}
        ```

    Step 2: Identify a list of financial-specific intents

    Possible intents: 
    - issue quotation
    - issue invoice
    - issue receipt
    - verify bankbook transaction

    Step 4: Output format, MUST use **FinanceIntentOutput** schema:
        ```json
        {{
            "intents": ["<list of identified finance intents>"],
            "human_clarification_flag": <boolean, "True" if clarification needed, "False" if not>,
            "messages": ["<analysis result and reasoning>"]
        }}
        ```
"""

def intent_analyzer_node(state: FinanceAgentState):
    print("[HANDLER_INVOKE][intent_analyzer_node]")

    system_prompt = FINANCE_INTENT_ANALYZER_PROMPT.format(user_input=state.user_input)
    parsed_response = invoke_llm(system_prompt, FinanceIntentOutput)

    try:
        intents = parsed_response.get("intents", [])
        llm_result_msg = parsed_response.get("messages", ["Intent analysis completed"])[-1]
        human_clarification_flag = parsed_response.get("human_clarification_flag", False)

        return {
            "intents": intents,
            "messages": [AIMessage(content=llm_result_msg)],
            "human_clarification_flag": human_clarification_flag
        }

    except Exception as e:
        print(f"[HANDLER_ERROR][finance_intent_analyzer_node]: {str(e)}")

