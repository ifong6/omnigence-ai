from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from app.models.flow_models import Flow
from app.finance_agent.repos.base_repo import OrmBaseRepository


class FlowRepo(OrmBaseRepository[Flow]):
    """
    ORM repository for Finance.flow.
    - 通用 CRUD 由父類提供
    - 這裡放 Flow 專屬查詢與便捷方法
    """

    def __init__(self, session: Session):
        super().__init__(Flow, session)

    # --- Specialized Queries -------------------------------------------------

    def find_by_session(
        self,
        session_id: UUID,
        *,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[Flow]:
        """
        依 session_id 取對應 flow 記錄，預設按 created_at DESC。
        """
        stmt = select(Flow).where(Flow.session_id == session_id)
        if order_desc:
            stmt = stmt.order_by(Flow.created_at.desc())  # type: ignore
        else:
            stmt = stmt.order_by(Flow.created_at.asc())  # type: ignore

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt))

    def search_by_summary(
        self,
        term: str,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Flow]:
        """
        以 ILIKE 搜索 user_request_summary（模糊查詢）。
        """
        stmt = (
            select(Flow)
            .where(Flow.user_request_summary.ilike(f"%{term}%"))  # type: ignore
            .order_by(Flow.created_at.desc())  # type: ignore
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(stmt))

    def search_by_agent(
        self,
        agent_name: str,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Flow]:
        """
        以 ILIKE 搜索 identified_agents（字串列表存於單列，以逗號分隔時同樣可匹配）。
        """
        stmt = (
            select(Flow)
            .where(Flow.identified_agents.ilike(f"%{agent_name}%"))  # type: ignore
            .order_by(Flow.created_at.desc())  # type: ignore
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(stmt))

    # --- Convenience wrappers (optional) ------------------------------------

    def create_log(
        self,
        *,
        id: Optional[UUID] = None,
        session_id: UUID,
        identified_agents: Optional[str] = None,
        user_request_summary: Optional[str] = None,
    ) -> Flow:
        """
        便捷：創建一條 flow 記錄。父類 create() 會自動做乾淨輸入（strip/空白→None/UUID→str＊如已配置）。
        若你的 Flow.id 有 default_factory（uuid4），則可不傳 id。
        """
        payload = dict(
            id=id,
            session_id=session_id,
            identified_agents=identified_agents,
            user_request_summary=user_request_summary,
        )
        return self.create(**payload)
