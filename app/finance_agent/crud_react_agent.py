from typing import Any
from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.finance_agent.utils.invoke_react_agent import invoke_react_agent
from app.finance_agent.tools.service_tool_registry import SERVICE_TOOLS
from app.prompt.finance_agent_react_prompt import UNIFIED_CRUD_REACT_PROMPT_TEMPLATE

def crud_react_agent_node(state: FinanceAgentState) -> dict[str, Any]:
    print(f"[INFO][crud_react_agent_node] Starting CRUD agent for user input: {state.user_input}")
    try:
        response = invoke_react_agent(
            tools=SERVICE_TOOLS,
            user_input=state.user_input or "",
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            return_intermediate_steps=True,
            prompt_template=UNIFIED_CRUD_REACT_PROMPT_TEMPLATE
        )

        print(f"[DEBUG][crud_react_agent_node] response={response}")

        # Extract output and intermediate steps
        output = response.get("output", "")
        intermediate_steps = response.get("intermediate_steps", [])

        # Build handler result
        handler_result = {
            "output": output,
            "intermediate_steps": intermediate_steps,
            "status": "success",
            "agent_type": "crud_react"
        }

        print(f"[INFO][crud_react_agent_node] Completed successfully")
        print(f"[DEBUG][crud_react_agent_node] handler_result={handler_result}")

        return {
            "handler_result": handler_result
        }

    except Exception as e:
        error_msg = f"Error in crud_react_agent_node: {str(e)}"
        print(f"[ERROR][quotation_crud_react_agent_node] {error_msg}")

        return {
            "handler_result": {
                "output": f"Failed to process CRUD request: {str(e)}",
                "status": "error",
                "error": error_msg,
                "agent_type": "crud_react"
            }
        }
