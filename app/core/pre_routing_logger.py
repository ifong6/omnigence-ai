# app/main_flow/nodes/pre_routing_logger_node.py
from typing import Optional
from uuid import UUID

from app.core.agent_config.MainFlowState import MainFlowState
from app.services.impl.PreRoutingLoggerServiceImpl import PreRoutingLoggerServiceImpl
from app.dto.pre_routing_dto import PreRoutingLoggerRequestDTO

def pre_routing_logger_node(state: MainFlowState):
    """
    Controller / Node:
    - 从 MainFlowState 提取数据
    - 组装 Request DTO
    - 调用 Service
    - 将 Response DTO 转成 LangGraph 的 state fragment
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
    if not s:
        return UUID(int=0)
    try:
        return UUID(s)
    except (ValueError, AttributeError):
        # Not a valid UUID string, return fallback
        return UUID(int=0)
