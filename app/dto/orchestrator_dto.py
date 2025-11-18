# app/dto/orchestrator_dto.py
from typing import Any, Literal
from pydantic import BaseModel, Field


class OrchestratorStateDTO(BaseModel):
    session_id: str
    flow_uuid: str
    identified_agents: list[str] = Field(default_factory=list)


class OrchestratorInterruptResponseDTO(BaseModel):
    """
    Human-in-the-loop 中断时的 HTTP Response DTO。
    """
    status: Literal["interrupt"]
    session_id: str
    # 中断原因 / 提示文本 / 需要用户确认的信息
    result: Any


class OrchestratorErrorResponseDTO(BaseModel):
    """
    异常时（内部错误）的 HTTP Response DTO。
    """
    status: Literal["fail"]
    result: str  # 错误信息
