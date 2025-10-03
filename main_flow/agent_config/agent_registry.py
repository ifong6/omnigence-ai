from main_flow.agent_classifier import agent_classifier_node
from main_flow.routing_agent import routing_agent_node

AGENT_NODES = {
    "classifier_agent": agent_classifier_node,
    "routing_agent": routing_agent_node,
}

# ------------ agentic_flow_config for static edges ------------
STATIC_EDGES = [
    ("classifier_agent", "routing_agent"),
]

