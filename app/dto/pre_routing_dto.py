# app/finance_agent/dtos/pre_routing_logger_dto.py
from uuid import UUID
from typing import Iterable, List, Optional
from pydantic import BaseModel

class PreRoutingLoggerRequestDTO(BaseModel):
    flow_uuid: UUID
    session_id: UUID
    user_input: str
    classifier_msg: str

class PreRoutingLoggerResultDTO(BaseModel):
    summary: str
    identified_agents: List[str]

class PreRoutingLoggerResponseDTO(BaseModel):
    flow_uuid: UUID
    # 如果以后需要，可以加: created_at, status 等字段
