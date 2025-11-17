from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.finance_agent.invoice.invoice_crud_tools import invoice_crud_tools
from app.finance_agent.utils.invoke_react_agent import invoke_react_agent
from app.finance_agent.invoice.utils.format_invoice_response import (
    format_invoice_response,
    print_invoice_request
)

def invoice_crud_handler_node(state: FinanceAgentState):
    print("[Handler][invoice_crud_handler_node]")

    # Print request for logging/debugging (server-side only)
    print_invoice_request(state.user_input)

    # Execute the ReAct agent with invoice tools
    # The agent will determine which tools to use based on user input
    response = invoke_react_agent(
        tools=invoice_crud_tools,
        user_input=state.user_input
    )

    # Format response and print for logging/debugging (server-side only)
    # This prints detailed logs but returns clean data
    formatted_response = format_invoice_response(response)

    # Return clean data structure for frontend (no print output)
    return {
        "index": state.index + 1,
        "invoice_response": formatted_response  # Clean JSON data for frontend
    }
