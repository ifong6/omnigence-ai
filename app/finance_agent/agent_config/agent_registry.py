from langgraph.constants import END
from app.finance_agent.intent_analyzer import intent_analyzer_node
from app.finance_agent.quotation_info_ETL import quotation_info_ETL_node
from app.finance_agent.quotation_html_renderer import quotation_html_renderer_node
from app.finance_agent.quotation_pdf_builder import quotation_pdf_builder_node

AGENT_NODES = {
    "intent_analyzer": intent_analyzer_node,
    "quotation_info_ETL": quotation_info_ETL_node,
    "quotation_html_renderer": quotation_html_renderer_node,
    "quotation_pdf_builder": quotation_pdf_builder_node,
    
}

STATIC_EDGES = [
    ("intent_analyzer", "quotation_info_ETL"),
    ("quotation_info_ETL", "quotation_html_renderer"),
    ("quotation_html_renderer", "quotation_pdf_builder"),
    ("quotation_pdf_builder", END)
]

CONDITIONAL_EDGES = []