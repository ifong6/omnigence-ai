from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from langchain.schema import AIMessage
from pydantic import BaseModel
from app.llm.invoke_llm import invoke_llm

class QueryPlanningOutput(BaseModel):
    queries: list[str]
    reasoning: str

QUERY_PLANNING_PROMPT_TEMPLATE = """
    You are a planning agent responsible for determining: \
    a list of queries with **ORDERED PRIORITY** to be executed to answer the user's intent.

    Step 1: Read the following input:
        ```text
        {intents}
    
    Step 2: Output format, MUST use **QueryPlanningOutput** schema:
        ```json
        {
            "queries": ["a list of queries with ordered priority"],
            "reasoning": "<Explaining your reasoning and thought process of your query planning result>"
        }
        ```
"""

def query_planning_node(state: FinanceAgentState):
    print("[Handler][query_planning_node]")
    
    system_prompt = QUERY_PLANNING_PROMPT_TEMPLATE.format(intents=state.intents)
    parsed_response = invoke_llm(system_prompt, QueryPlanningOutput)
    
    try:
        queries = parsed_response.get("queries", [])
        reasoning = parsed_response.get("reasoning", "")
        print(f"reasoning: {reasoning}")
       
    except Exception as e:
        messages = f"[Error][query_planning_node]: {str(e)}"
        return {
            "messages": [AIMessage(content=messages)]
        }

    return {
        "queries": queries,
    }
    
    
    
    
    
    
    
    
    
    
    