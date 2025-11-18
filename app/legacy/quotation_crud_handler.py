from app.FinanceFlowState import FinanceAgentState
from app.legacy.quotation_tools.tools.crud_tools.create_quotation_no_tool import create_quotation_no_tool    
from app.legacy.quotation_tools.tools.crud_tools.create_quotation_in_db import create_quotation_in_db
from app.legacy.quotation_tools.tools.crud_tools.update_quotation_tool import update_quotation_tool
from app.legacy.quotation_tools.tools.crud_tools.extract_quotation_info_tool import extract_quotation_info_tool
from app.legacy.quotation_tools.tools.crud_tools.get_job_no_by_project_name_tool import get_job_no_by_project_name_tool
from app.legacy.quotation_tools.tools.crud_tools.get_client_info_by_project_name_tool import get_client_info_by_project_name_tool
from app.legacy.quotation_tools.tools.query_tools.find_quotation_items_by_quo_no import find_quotation_items_by_quo_no
from app.legacy.quotation_tools.tools.output_quotation_info_for_ui import output_quotation_info_for_ui
from app.finance_agent.utils.invoke_react_agent import invoke_react_agent

def quotation_crud_handler_node(state: FinanceAgentState):
    print("[Handler][quotation_crud_handler_node]")

    # Validate user_input is present
    if not state.user_input:
        error_response = {
            "status": "error",
            "error": "user_input is required for quotation creation"
        }
        return {
            "index": state.index + 1,
            "quotation_response": error_response
        }

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


    
