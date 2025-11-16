"""
LangGraph Schemas Package

This package contains all LangGraph-related schemas, states, and memory structures.

Modules:
    main_flow_state: MainFlowState for root orchestration graph
    flow_schema: FlowCreate for DB logging payloads (append-only)
    finance_agent_state: FinanceAgentState for finance sub-agent
    quotation_flow_schema: Schemas for quotation generation sub-flow
"""

from app.schemas.main_flow_state import MainFlowState
from app.schemas.flow_schema import FlowBase, FlowCreate
from app.schemas.finance_agent_state import FinanceAgentState
from app.schemas.quotation_flow_schema import (
    QuotationItemInput,
    QuotationGenerationInput,
    QuotationGenerationOutput,
    QuotationUpdateInput,
    QuotationQueryInput,
    QuotationFlowResponse,
)

__all__ = [
    # Main flow state
    "MainFlowState",

    # Flow DB logging schemas (append-only)
    "FlowBase",
    "FlowCreate",

    # Finance agent state
    "FinanceAgentState",

    # Quotation flow schemas
    "QuotationItemInput",
    "QuotationGenerationInput",
    "QuotationGenerationOutput",
    "QuotationUpdateInput",
    "QuotationQueryInput",
    "QuotationFlowResponse",
]
