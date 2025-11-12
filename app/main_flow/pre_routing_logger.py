from typing import Optional, Iterable
from uuid import UUID
from sqlmodel import Session
from app.main_flow.agent_config.MainFlowState import MainFlowState
from app.main_flow.prompt.pre_routing_logger_prompt import (
    PRE_ROUTING_LOGGER_PROMPT,
    PreRoutingLoggerOutput,
)
from app.llm.invoke_claude_llm import invoke_claude_llm
from app.finance_agent.repos.flow_repo import FlowRepo
from app.db.engine import new_session

# =============================================================================
# 🌟 Main Node
# =============================================================================
def pre_routing_logger_node(state: MainFlowState):
    """
    Main orchestration node for pre-routing logging.

    NOTE:
    - Creates its own Session internally (LangGraph nodes only receive state).
    - FlowRepo 会在 create()/create_log 时统一做「干净输入」处理。
    """
    print("[INVOKE][pre_routing_logger_node]")

    flow_uuid = _to_uuid(state.flow_uuid)
    session_id = _to_uuid(state.session_id)
    user_input = state.user_input or ""
    classifier_msg = state.classifier_msg or ""

    print(f"[PRE_ROUTING_LOGGER] flow_uuid={flow_uuid}, session_id={session_id}")
    print(f"[PRE_ROUTING_LOGGER] user_input={user_input[:100]!r}")
    print(f"[PRE_ROUTING_LOGGER] classifier_msg={classifier_msg[:100]!r}")

    # Create database session for this operation
    session = new_session()

    try:
        # 1) Summarize user input with LLM
        result = summarize_user_input(user_input, classifier_msg)

        # 2) Log flow result into database
        log_flow_to_db(
            session=session,
            flow_uuid=flow_uuid,
            session_id=session_id,
            summary=result.summary,
            identified_agents=result.identified_agents,
        )

        return {"flow_uuid": str(flow_uuid)}

    except Exception as e:
        print(f"[PRE_ROUTING_LOGGER ERROR] Failed to log: {e}")
        # Continue flow even if logging fails
        return {"flow_uuid": str(flow_uuid)}

    finally:
        # Always close the session
        session.close()


# =============================================================================
# 🧠 LLM Summarization Helper
# =============================================================================
def summarize_user_input(user_input: str, classifier_msg: str) -> PreRoutingLoggerOutput:
    """Generate summary and identified agents using LLM."""
    prompt = PRE_ROUTING_LOGGER_PROMPT.format(
        user_input=user_input,
        classifier_message=classifier_msg,
    )
    print("[PRE_ROUTING_LOGGER] Invoking LLM for summarization...")
    return invoke_claude_llm(prompt, PreRoutingLoggerOutput)


# =============================================================================
# 💾 Database Logging Helper
# =============================================================================
def log_flow_to_db(*, session: Session, flow_uuid: UUID, session_id: UUID, 
    summary: str, identified_agents: Iterable[str]):
    """
    Write flow info into database via ORM repo.
    - UUID 直接用 Python 的 UUID 对象; SQLModel 会负责 DB 映射。
    - identified_agents: list[str] -> 存成逗号分隔字串（如你目前表设计）。
    """
    repo = FlowRepo(session)

    agents_str = ", ".join(identified_agents) if identified_agents else None

    repo.create_log(
        id=flow_uuid,
        session_id=session_id,
        identified_agents=agents_str,
        user_request_summary=summary,
    )

    # IMPORTANT: Commit the transaction to persist the flow record
    session.commit()
    print(f"[PRE_ROUTING_LOGGER] ✓ Logged flow with UUID: {flow_uuid}")


# =============================================================================
# 🔧 Small Utils
# =============================================================================
def _to_uuid(v: Optional[UUID | str]) -> UUID:
    """Return a valid UUID, fallback to UUID(0) if invalid or None."""
    if not v:
        return UUID(int=0)
    if isinstance(v, UUID):
        return v
    s = str(v).strip()
    return UUID(s) if s else UUID(int=0)

