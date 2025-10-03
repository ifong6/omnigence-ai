from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.finance_agent.agent_config.agent_registry import AGENT_NODES, STATIC_EDGES, CONDITIONAL_EDGES
from langgraph.graph import StateGraph
from app.utils.Request.Request import RequestBody
from langchain_core.runnables import RunnableConfig
# from langgraph.checkpoint.memory import MemorySaver

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
graph = workflow_builder.compile()

def finance_agent_flow(request: RequestBody):
    initial_state = {
        "user_input": request.user_input,
        "agent_type": request.agent_type,
    }

    print("Invoking graph...\n")
    result = graph.invoke(initial_state)  # receive entire state here

    return result


    
  