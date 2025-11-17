from langgraph.constants import END
from app.finance_agent.intent_analyzer import intent_analyzer_node
from app.finance_agent.planner import planner_node
from app.finance_agent.company.company_crud_handler import company_crud_handler_node
from app.finance_agent.job_list.job_crud_handler import job_crud_handler_node
from app.finance_agent.quotation.quotation_crud_handler import quotation_crud_handler_node
from app.finance_agent.invoice.invoice_crud_handler import invoice_crud_handler_node
from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState

AGENT_NODES = {
    "intent_analyzer": intent_analyzer_node,
    "planner": planner_node,
    "company_crud_handler": company_crud_handler_node,
    "job_crud_handler": job_crud_handler_node,
    "quotation_crud_handler": quotation_crud_handler_node,
    "invoice_crud_handler": invoice_crud_handler_node,
}

STATIC_EDGES = [
    ("intent_analyzer", "planner"),
    
]

def route_to_next_handler(state: FinanceAgentState):
    """
    Route to the next handler based on state.index.
    If index exceeds the list size, route to 'end'.
    """
    print(f"  [DEBUG][route_to_next_handler] Called")
    print(f"  [DEBUG] state.next_handlers: {state.next_handlers}")
    print(f"  [DEBUG] state.index: {state.index}")

    if not state.next_handlers:
        print(f"  [DEBUG] No next_handlers found, routing to 'end'")
        return "end"

    if state.index >= len(state.next_handlers):
        print(f"  [DEBUG] Index {state.index} >= len({len(state.next_handlers)}), routing to 'end'")
        return "end"

    next_handler = state.next_handlers[state.index]
    print(f"  [DEBUG] Routing to handler: {next_handler}")
    return next_handler

CONDITIONAL_EDGES = [
     {
        "source": "planner",
        "path": route_to_next_handler,
        "path_map": {
            "job_crud_handler": "job_crud_handler",
            "quotation_crud_handler": "quotation_crud_handler",
            "invoice_crud_handler": "invoice_crud_handler",
            "company_crud_handler": "company_crud_handler",
            "end": END
        }
    },
    {
        "source": "job_crud_handler",
        "path": route_to_next_handler,
        "path_map": {
            "job_crud_handler": "job_crud_handler",
            "quotation_crud_handler": "quotation_crud_handler",
            "invoice_crud_handler": "invoice_crud_handler",
            "company_crud_handler": "company_crud_handler",
            "end": END
        }
    },
    {
        "source": "quotation_crud_handler",
        "path": route_to_next_handler,
        "path_map": {
            "job_crud_handler": "job_crud_handler",
            "quotation_crud_handler": "quotation_crud_handler",
            "invoice_crud_handler": "invoice_crud_handler",
            "company_crud_handler": "company_crud_handler",
            "end": END
        }
    },
    {
        "source": "invoice_crud_handler",
        "path": route_to_next_handler,
        "path_map": {
            "job_crud_handler": "job_crud_handler",
            "quotation_crud_handler": "quotation_crud_handler",
            "invoice_crud_handler": "invoice_crud_handler",
            "company_crud_handler": "company_crud_handler",
            "end": END
        }
    },
    {
        "source": "company_crud_handler",
        "path": route_to_next_handler,
        "path_map": {
            "job_crud_handler": "job_crud_handler",
            "quotation_crud_handler": "quotation_crud_handler",
            "invoice_crud_handler": "invoice_crud_handler",
            "company_crud_handler": "company_crud_handler",
            "end": END
        }
    }
]