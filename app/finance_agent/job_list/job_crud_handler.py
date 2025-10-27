from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.finance_agent.job_list.job_crud_tools import job_crud_tools
from app.finance_agent.utils.invoke_react_agent import invoke_react_agent

def job_crud_handler_node(state: FinanceAgentState):
    print("[HANDLER_INVOKE][job_crud_handler_node]")

    response = invoke_react_agent(tools=job_crud_tools, user_input=state.user_input)
    print("response: ", response)
    
    return {    
        "index": state.index + 1
    }

if __name__ == "__main__":
    print("Running job_crud_handler_node...")

    state = FinanceAgentState(
        user_input="create a new job for 金龍酒店, 結構安全檢測",
    )
    job_crud_handler_node(state)
    
    
