from app.schemas.finance_agent_state import FinanceAgentState
from app.finance_agent.company.company_crud_tools import company_crud_tools
from app.finance_agent.utils.invoke_react_agent import invoke_react_agent

def company_crud_handler_node(state: FinanceAgentState):
    print("[Handler][company_crud_handler_node]")

    response = invoke_react_agent(tools=company_crud_tools, user_input=state.user_input)
    print("response: ", response)
    
    return {
        "index": state.index + 1
    }