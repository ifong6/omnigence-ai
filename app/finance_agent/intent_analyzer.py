from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from langchain_core.messages import AIMessage
from pydantic import BaseModel
from typing import List, Optional
from app.llm.invoke_openai_llm import invoke_openai_llm

class FinanceIntentOutput(BaseModel):
    intents: List[str]
    messages: List[str]
    human_clarification_flag: bool
    job_type: Optional[str] = None

FINANCE_INTENT_ANALYZER_PROMPT = """
    You are a finance domain intent analyzer. Your job is to analyze user input and identify specific finance-related intents.

    Step 1: Analyze user input for finance-related queries

        User input:
        ```text
        {user_input}
        ```

    Step 2: Identify a list of financial-specific intents

    Possible intents:
    - create job (when user wants to create a new job/project/work order)
    - issue quotation (when user wants to generate a quotation document)
    - issue invoice
    - issue receipt
    - verify bankbook transaction

    Step 3: Determine job type (REQUIRED for both "create job" and "issue quotation" intents)

    If the intent includes "create job" OR "issue quotation", analyze the user input to determine the job type:
    - Job type "inspection": if user input contains keywords like "inspection", "檢測", "驗收", "測試", "檢查", "查驗"
    - Job type "design": if the user input does NOT contain inspection keywords (default)

    Note: There are only two job types - inspection and design. If it's not inspection, it must be design.

    This is critical for:
    - Job creation: determines the job type stored in the database
    - Quotation: determines the quotation number format
        - Inspection jobs use: Q-JICP-YY-MM-X (e.g., Q-JICP-25-01-1)
        - Design jobs use: Q-JCP-YY-MM-X (e.g., Q-JCP-25-01-1)

    Step 4: Output format, MUST use **FinanceIntentOutput** schema:
        ```json
        {{
            "intents": ["<list of identified finance intents>"],
            "human_clarification_flag": <boolean, "True" if clarification needed, "False" if not>,
            "messages": ["<analysis result and reasoning>"],
            "job_type": "<'inspection' or 'design', null if not applicable>"
        }}
        ```
"""

def intent_analyzer_node(state: FinanceAgentState):
    print("[HANDLER_INVOKE][intent_analyzer_node]")

    system_prompt = FINANCE_INTENT_ANALYZER_PROMPT.format(user_input=state.user_input)
    parsed_response = invoke_openai_llm(system_prompt, FinanceIntentOutput)

    try:
        # parsed_response is a Pydantic object from invoke_openai_llm
        print(f"[DEBUG] parsed_response type: {type(parsed_response)}")
        print(f"[DEBUG] parsed_response: {parsed_response}")

        intents = parsed_response.intents
        llm_result_msg = parsed_response.messages[-1] if parsed_response.messages else "Intent analysis completed"
        human_clarification_flag = parsed_response.human_clarification_flag
        job_type = parsed_response.job_type

        print(f"[DEBUG] Extracted intents: {intents}")
        print(f"[DEBUG] Extracted job_type: {job_type}")

        return {
            "intents": intents,
            "messages": [AIMessage(content=llm_result_msg)],
            "human_clarification_flag": human_clarification_flag,
            "job_type": job_type
        }

    except Exception as e:
        print(f"[HANDLER_ERROR][finance_intent_analyzer_node]: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "intents": [],
            "messages": [AIMessage(content=f"Error: {str(e)}")],
            "human_clarification_flag": False
        }

