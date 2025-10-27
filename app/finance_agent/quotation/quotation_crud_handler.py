from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.finance_agent.quotation.quotation_crud_tools import quotation_crud_tools
from app.finance_agent.utils.invoke_react_agent import invoke_react_agent
from app.finance_agent.quotation.utils.format_quotation_response import (
    format_quotation_response,
    print_quotation_request
)

def quotation_crud_handler_node(state: FinanceAgentState):
    print("[Handler][quotation_crud_handler_node]")

    # Print request for logging/debugging (server-side only)
    print_quotation_request(state.user_input)

    # Execute the agent (job_no should already exist before quotation creation)
    response = invoke_react_agent(
        tools=quotation_crud_tools,
        user_input=state.user_input
    )

    # Format response and print for logging/debugging (server-side only)
    # This prints detailed logs but returns clean data
    formatted_response = format_quotation_response(response)

    # Return clean data structure for frontend (no print output)
    return {
        "index": state.index + 1,
        "quotation_response": formatted_response  # Clean JSON data for frontend
    }


    
