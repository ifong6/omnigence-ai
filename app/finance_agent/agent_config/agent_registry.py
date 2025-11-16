from langgraph.constants import END
from app.finance_agent.intent_analyzer import intent_analyzer_node
from app.finance_agent.crud_react_agent import crud_react_agent_node
from app.schemas.finance_agent_state import FinanceAgentState

AGENT_NODES = {
    "intent_analyzer": intent_analyzer_node,
    "crud_react_agent": crud_react_agent_node,
}

STATIC_EDGES = [
    ("intent_analyzer", "crud_react_agent"), # Intent Analyzer → CRUD React Agent
]

CONDITIONAL_EDGES = []

# def route_to_next_handler(state: FinanceAgentState):
#     """
#     Route to the next handler based on state.index.
#     If index exceeds the list size, route to 'end'.
#     """
#     print(f"[DEBUG][route_to_next_handler] Called")
#     print(f"[DEBUG] state.next_handlers: {state.next_handlers}")
#     print(f"[DEBUG] state.index: {state.index}")

#     if not state.next_handlers:
#         print(f"[DEBUG] No next_handlers found, routing to 'end'")
#         return "end"

#     if state.index >= len(state.next_handlers):
#         print(f"  [DEBUG] Index {state.index} >= len({len(state.next_handlers)}), routing to 'end'")
#         return "end"

#     next_handler = state.next_handlers[state.index]
#     print(f"[DEBUG] Routing to handler: {next_handler}")
#     return next_handler

# CONDITIONAL_EDGES = [
#      {
#         "source": "planner",
#         "path": route_to_next_handler,
#         "path_map": {
#             "job_crud_handler": "job_crud_handler",
#             "quotation_crud_handler": "quotation_crud_handler",
#             "company_crud_handler": "company_crud_handler", 
#             "end": END
#         }
#     }
# ]