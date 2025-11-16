# app/services/impl/pre_routing_logger_service_impl.py
from typing import Callable, Iterable
from uuid import UUID
from sqlmodel import Session
from app.finance_agent.repos.flow_repo import FlowRepo
from app.main_flow.prompt.pre_routing_logger_prompt import PRE_ROUTING_LOGGER_PROMPT, PreRoutingLoggerOutput
from app.llm.invoke_claude_llm import invoke_claude_llm
from app.dto.pre_routing_dto import PreRoutingLoggerRequestDTO, PreRoutingLoggerResultDTO, PreRoutingLoggerResponseDTO
from app.services import PreRoutingLoggerService
from app.db.supabase.engine import engine

class PreRoutingLoggerServiceImpl(PreRoutingLoggerService):
    """
    Service (经理): encapsulates LLM summarization + DB logging.
    Controller / Node 只跟 DTO 交互，不直接操作 Session / Repo。
    """

    def _session_factory(self) -> Session:
        """Create a new database session."""
        return Session(engine)

    # ---------- public API ----------
    def handle(self, req: PreRoutingLoggerRequestDTO) -> PreRoutingLoggerResponseDTO:
        session = self._session_factory()
        try:
            # 1) LLM summarization
            result = self._summarize_user_input(
                user_input=req.user_input,
                classifier_msg=req.classifier_msg,
            )

            # 2) DB logging
            self._log_flow_to_db(
                session=session,
                flow_uuid=req.flow_uuid,
                session_id=req.session_id,
                summary=result.summary,
                identified_agents=result.identified_agents,
            )

            return PreRoutingLoggerResponseDTO(flow_uuid=req.flow_uuid)

        except Exception as e:
            # 这里是 service level logging，controller 决定要不要吞掉錯誤
            print(f"[PRE_ROUTING_LOGGER SERVICE] Error: {e}")
            # 需求是 “logging fail 也繼續 flow”，所以照樣返回
            return PreRoutingLoggerResponseDTO(flow_uuid=req.flow_uuid)

        finally:
            session.close()

    # ---------- private helpers ----------
    def _summarize_user_input(
        self, *, user_input: str, classifier_msg: str
    ) -> PreRoutingLoggerResultDTO:
        prompt = PRE_ROUTING_LOGGER_PROMPT.format(
            user_input=user_input,
            classifier_message=classifier_msg,
        )
        print("[PRE_ROUTING_LOGGER] Invoking LLM for summarization...")
        llm_result: PreRoutingLoggerOutput = invoke_claude_llm(
            prompt, PreRoutingLoggerOutput
        )

        return PreRoutingLoggerResultDTO(
            summary=llm_result.summary,
            identified_agents=list(llm_result.identified_agents or []),
        )

    def _log_flow_to_db(
        self,
        *,
        session: Session,
        flow_uuid: UUID,
        session_id: UUID,
        summary: str,
        identified_agents: Iterable[str],
    ) -> None:
        repo = FlowRepo(session)

        agents_str = ", ".join(identified_agents) if identified_agents else None

        repo.create_log(
            id=flow_uuid,
            session_id=session_id,
            identified_agents=agents_str,
            user_request_summary=summary,
        )

        session.commit()
        print(f"[PRE_ROUTING_LOGGER] ✓ Logged flow with UUID: {flow_uuid}")
