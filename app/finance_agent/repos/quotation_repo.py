"""
Quotation Repository for CRUD operations on Finance.quotation table.

Provides type-safe database operations with validation and business logic.
"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
from sqlmodel import Session, select
from sqlalchemy import func
from app.finance_agent.repos.base_repo import OrmBaseRepository
from app.finance_agent.models.quotation_models import Quotation, QuotationCreate, QuotationUpdate, QuotationRow

def _payload_to_dict(payload: QuotationCreate | QuotationUpdate) -> Dict[str, Any]:
    return payload.model_dump(exclude_none=True)

class QuotationRepo(OrmBaseRepository[Quotation]):
    """Repository for managing quotations in Finance.quotation table."""

    def __init__(self, session: Session):
        super().__init__(model=Quotation, session=session)

    # --- CRUD ---------------------------------------------------------------

    def create_quotation(self, payload: QuotationCreate) -> Quotation:
        data = _payload_to_dict(payload)
        return super().create(**data)

    def update_quotation(
        self, quotation_id: int, payload: QuotationUpdate
    ) -> Optional[Quotation]:
        data = _payload_to_dict(payload)
        if not data:
            return None
        return super().update(quotation_id, **data)

    def get_by_id(self, quotation_id: int) -> Optional[Quotation]:
        return super().get(quotation_id)

    def get_by_quo_no(
        self, quo_no: str, *, limit: Optional[int] = None, offset: int = 0
    ) -> List[Quotation]:
        stmt = (
            select(Quotation)
            .where(Quotation.quo_no == quo_no)
            .order_by(Quotation.id.asc())  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt))

    def get_by_client_id(
        self,
        client_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[Quotation]:
        stmt = select(Quotation).where(Quotation.client_id == client_id)
        stmt = stmt.order_by(
            Quotation.date_issued.desc() if order_desc else Quotation.date_issued.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt))

    def get_by_project_name(
        self,
        project_name: str,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[Quotation]:
        stmt = select(Quotation).where(Quotation.project_name == project_name)
        stmt = stmt.order_by(
            Quotation.date_issued.desc() if order_desc else Quotation.date_issued.asc()  # type: ignore
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt))

    def update_items_by_quo_no(
        self, quo_no: str, payload: QuotationUpdate
    ) -> List[Quotation]:
        """
        更新同一張報價單號的所有 item。
        做法：先查出，再逐筆 set 後 flush（保持 SQLModel 生命週期一致）。
        """
        data = _payload_to_dict(payload)
        if not data:
            return []

        items = self.get_by_quo_no(quo_no)
        for item in items:
            for k, v in data.items():
                setattr(item, k, v)
        self.session.flush()
        return items

    def get_all(
        self, limit: Optional[int] = None, offset: int = 0, order_desc: bool = True
    ) -> List[Quotation]:
        stmt = select(Quotation)
        stmt = stmt.order_by(
            Quotation.date_issued.desc() if order_desc else Quotation.date_issued.asc()  # type: ignore # noqa: F541
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt))

    def get_total_by_quo_no(self, quo_no: str) -> Dict[str, Any]:
        """Calculate total amount and item count for a quotation number."""
        stmt = (
            select(
                func.sum(Quotation.total_amount).label("total"),
                func.count(Quotation.id).label("item_count"),  # type: ignore # noqa: F541
            )
            .where(Quotation.quo_no == quo_no)
            .limit(1)
        )
        row = self.session.exec(stmt).first()
        if row:
            total = row[0] or Decimal("0")
            count = row[1] or 0
            return {"total": total, "item_count": count}
        return {"total": Decimal("0"), "item_count": 0}
