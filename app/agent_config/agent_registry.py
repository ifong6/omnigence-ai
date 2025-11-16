from app.main_flow.agent_classifier import agent_classifier_node
from app.main_flow.pre_routing_logger import pre_routing_logger_node
from app.main_flow.workflow_router import workflow_router_node
from app.main_flow.aggregation_agent import aggregation_agent_node

AGENT_NODES = {
    "classifier_agent": agent_classifier_node,
    "pre_routing_logger": pre_routing_logger_node,
    "workflow_router": workflow_router_node,
    "aggregation_agent": aggregation_agent_node,
}

# ------------ agentic_flow_config for static edges ------------
STATIC_EDGES = [
    ("classifier_agent", "pre_routing_logger"),  # Classifier → Logger
    ("pre_routing_logger", "workflow_router"),  # Logger → Workflow Router (after DB write)
    ("workflow_router", "aggregation_agent"),
]

