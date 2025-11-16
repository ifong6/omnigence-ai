# app/main_flow/nodes/pre_routing_logger_node.py
from typing import Optional
from uuid import UUID

from app.schemas.main_flow_state import MainFlowState
from app.services.impl import PreRoutingLoggerServiceImpl
from app.dto.pre_routing_dto import PreRoutingLoggerRequestDTO, PreRoutingLoggerResultDTO, PreRoutingLoggerResponseDTO

def pre_routing_logger_node(state: MainFlowState):
    """
    Controller / Node:
    - 從 MainFlowState 抽取資料
    - 組裝 Request DTO
    - 呼叫 Service
    - 把 Response DTO 轉成 LangGraph 的 state fragment
    """
    print("[INVOKE][pre_routing_logger_node]")

    flow_uuid = _to_uuid(state.flow_uuid)
    session_id = _to_uuid(state.session_id)
    user_input = state.user_input or ""
    classifier_msg = state.classifier_msg or ""

    print(f"[PRE_ROUTING_LOGGER] flow_uuid={flow_uuid}, session_id={session_id}")
    print(f"[PRE_ROUTING_LOGGER] user_input={user_input[:100]!r}")
    print(f"[PRE_ROUTING_LOGGER] classifier_msg={classifier_msg[:100]!r}")

    service = PreRoutingLoggerServiceImpl()

    req_dto = PreRoutingLoggerRequestDTO(
        flow_uuid=flow_uuid,
        session_id=session_id,
        user_input=user_input,
        classifier_msg=classifier_msg,
    )

    resp_dto = service.handle(req_dto)

    # LangGraph 只需要 flow_uuid 繼續傳遞
    return {"flow_uuid": str(resp_dto.flow_uuid)}


# ---------- small util ----------
def _to_uuid(v: Optional[UUID | str]) -> UUID:
    """Return a valid UUID, fallback to UUID(0) if invalid or None."""
    if not v:
        return UUID(int=0)
    if isinstance(v, UUID):
        return v
    s = str(v).strip()
    return UUID(s) if s else UUID(int=0)
