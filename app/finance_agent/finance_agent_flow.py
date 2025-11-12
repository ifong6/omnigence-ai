from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.finance_agent.agent_config.agent_registry import AGENT_NODES, STATIC_EDGES, CONDITIONAL_EDGES
from langgraph.graph import StateGraph
from app.utils.Request import RequestBody
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# Initialize checkpointer with SQLite persistence (survives server restarts)
conn = sqlite3.connect("./checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

workflow_builder = StateGraph(FinanceAgentState)
# register nodes
for agent_name, node in AGENT_NODES.items():
    workflow_builder.add_node(agent_name, node)
# wire static edges
for source, path in STATIC_EDGES:
    workflow_builder.add_edge(source, path)

for edge in CONDITIONAL_EDGES:
    workflow_builder.add_conditional_edges(
        source=edge["source"],
        path=edge["path"],
        path_map=edge["path_map"]
    )

workflow_builder.set_entry_point("intent_analyzer")
graph = workflow_builder.compile(checkpointer=checkpointer)

def finance_agent_flow(request: RequestBody):
    initial_state = {
        "user_input": request.user_input,
        "agent_type": request.agent_type,
    }

    # Create config with thread_id from session_id for checkpointing/resumption
    config = RunnableConfig(
        configurable={
            "thread_id": request.session_id  # Maps session_id to LangGraph's thread_id
        }
    )

    print(f"Invoking graph with session_id: {request.session_id}\n")
    result = graph.invoke(initial_state, config=config)  # Pass config for checkpoint lookup/save

    print(f"\n[DEBUG][finance_agent_flow] Graph completed")
    print(f"[DEBUG] Result type: {type(result)}")
    print(f"[DEBUG] Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
    if isinstance(result, dict):
        print(f"[DEBUG] handler_result: {result.get('handler_result', 'NOT FOUND')}")

    return result




