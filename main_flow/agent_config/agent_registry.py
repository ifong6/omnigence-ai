from main_flow.agent_classifier import agent_classifier_node
from main_flow.pre_orchestrator_logger import pre_orchestrator_logger_node
from main_flow.orchestrator_agent import orchestrator_agent_node
from main_flow.aggregation_agent import aggregation_agent_node

AGENT_NODES = {
    "classifier_agent": agent_classifier_node,
    "pre_orchestrator_logger": pre_orchestrator_logger_node,
    "orchestrator_agent": orchestrator_agent_node,
    "aggregation_agent": aggregation_agent_node,
}

# ------------ agentic_flow_config for static edges ------------
STATIC_EDGES = [
    ("classifier_agent", "pre_orchestrator_logger"),  # Classifier → Logger
    ("pre_orchestrator_logger", "orchestrator_agent"),  # Logger → Orchestrator (after DB write)
    ("orchestrator_agent", "aggregation_agent"),
]

