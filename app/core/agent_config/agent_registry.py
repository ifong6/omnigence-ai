from app.core.agent_classifier import agent_classifier_node
from app.core.workflow_router import workflow_router_node
from app.core.aggregation_agent import aggregation_agent_node
from app.core.intent_analyzer import intent_analyzer_node
from app.core.pre_routing_logger import pre_routing_logger_node
from langgraph.constants import END

AGENT_NODES = {
    "classifier_agent": agent_classifier_node,
    "intent_analyzer": intent_analyzer_node,
    "pre_routing_logger": pre_routing_logger_node,
    "workflow_router": workflow_router_node,
    "aggregation_agent": aggregation_agent_node,
}
# ------------ agentic_flow_config for static edges ------------
STATIC_EDGES = [
    ("classifier_agent", "intent_analyzer"),  # Classifier → Intent Analyzer
    ("intent_analyzer", "pre_routing_logger"),  # Intent Analyzer → Pre-Routing Logger
    ("pre_routing_logger", "workflow_router"),  # Pre-Routing Logger → Workflow Router
    ("workflow_router", "aggregation_agent"),
    ("aggregation_agent", END),
]

