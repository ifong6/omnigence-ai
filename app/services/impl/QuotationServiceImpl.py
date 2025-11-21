from typing import Optional, List, Dict, Any, Sequence
from datetime import date
from decimal import Decimal

from sqlmodel import Session, select

from app.models.quotation_models import (
    QuotationSchema,
    QuotationCreate,
    QuotationUpdate,
    QuotationItemSchema,
)
from app.models.job_models import DesignJobSchema, InspectionJobSchema
from app.services import QuotationService
from app.services.helpers.quotation_service_helper import (
    payload_to_dict,
    compose_quo_no,
    parse_quo_no,
    get_next_quotation_index_for_job,
    get_next_revision_for_job_and_index,
    get_latest_quotation_for_job,
)


class QuotationServiceImpl(QuotationService):
    """
    Concrete implementation of QuotationService using SQLModel.

    - Supports both DESIGN and INSPECTION jobs (by job_no prefix)
    - Handles quotation headers and line items
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.session: Session = session

        # ORM models – overridable in tests
        self.quotation_model = QuotationSchema
        self.quotation_item_model = QuotationItemSchema
        self.design_job_model = DesignJobSchema
        self.inspection_job_model = InspectionJobSchema

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_job_model(self, job_no: str):
        """
        Decide which job table to use based on job_no prefix.

        - Q-JCP-...   -> Design job
        - Q-JICP-...  -> Inspection job
        """
        if job_no.startswith("Q-JICP-"):
            return self.inspection_job_model
        return self.design_job_model

    def _get_job_by_job_no(self, job_no: str):
        job_model = self._resolve_job_model(job_no)
        stmt = select(job_model).where(job_model.job_no == job_no)  # type: ignore[attr-defined]
        job = self.session.exec(stmt).first()
        if not job:
            job_type = "Inspection" if job_model is self.inspection_job_model else "Design"
            raise ValueError(f"{job_type} job with job_no '{job_no}' not found")
        return job

    # ------------------------------------------------------------------
    # Basic queries
    # ------------------------------------------------------------------
    def get_quotation_by_id(self, quotation_id: int) -> Optional[QuotationSchema]:
        return self.session.get(self.quotation_model, quotation_id)

    def get_quotation_by_quo_no(self, quo_no: str) -> Optional[QuotationSchema]:
        stmt = select(self.quotation_model).where(
            self.quotation_model.quo_no == quo_no  # type: ignore[attr-defined]
        )
        return self.session.exec(stmt).first()

    def get_quotations_by_client(
        self,
        client_id: int,
        limit: Optional[int] = None,
        order_by: str | None = None,
    ) -> Sequence[QuotationSchema]:
        stmt = select(self.quotation_model).where(
            self.quotation_model.client_id == client_id  # type: ignore[attr-defined]
        )

        if order_by and hasattr(self.quotation_model, order_by):
            stmt = stmt.order_by(getattr(self.quotation_model, order_by).desc())
        else:
            stmt = stmt.order_by(self.quotation_model.date_created.desc())  # type: ignore[attr-defined]

        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    def get_quotations_by_project(
        self,
        project_name: str,
        limit: Optional[int] = None,
        order_by: str | None = None,
    ) -> Sequence[QuotationSchema]:
        """
        Filter by job title via join (project_name == job.title).
        Currently joins DESIGN jobs; extend if you need INSPECTION too.
        """
        job_model = self.design_job_model
        stmt = (
            select(self.quotation_model)
            .join(
                job_model,
                self.quotation_model.job_id == job_model.id,  # type: ignore[attr-defined]
            )
            .where(job_model.title == project_name)  # type: ignore[attr-defined]
        )

        if order_by and hasattr(self.quotation_model, order_by):
            stmt = stmt.order_by(getattr(self.quotation_model, order_by).desc())
        else:
            stmt = stmt.order_by(self.quotation_model.date_created.desc())  # type: ignore[attr-defined]

        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    def get_quotation_total(self, quo_no: str) -> Dict[str, Any]:
        """
        Return total amount and item count for a quotation.

        For now we trust the `total_amount` on the header; if in the
        future you wire up a proper relationship to items, you can
        recalculate from there.
        """
        quotation = self.get_quotation_by_quo_no(quo_no)
        if not quotation:
            return {"total": Decimal("0"), "item_count": 0}

        total = getattr(quotation, "total_amount", None)
        if total is None:
            total = Decimal("0")
        else:
            total = Decimal(str(total))

        return {
            "total": total,
            "item_count": 0,  # you can update this once you track item count
        }

    def list_all(
        self,
        order_by: str = "date_created",
        descending: bool = True,
        limit: Optional[int] = None,
    ) -> List[QuotationSchema]:
        stmt = select(self.quotation_model)
        if hasattr(self.quotation_model, order_by):
            col = getattr(self.quotation_model, order_by)
            stmt = stmt.order_by(col.desc() if descending else col.asc())

        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    def get_by_job_no(
        self,
        job_no: str,
        order_by: str | None = None,
    ) -> Sequence[QuotationSchema]:
        stmt = select(self.quotation_model).where(
            self.quotation_model.quo_no.like(f"{job_no}-%")  # type: ignore[attr-defined]
        )

        if order_by and hasattr(self.quotation_model, order_by):
            stmt = stmt.order_by(getattr(self.quotation_model, order_by).desc())
        else:
            stmt = stmt.order_by(self.quotation_model.quo_no.desc())  # type: ignore[attr-defined]

        return list(self.session.exec(stmt).all())

    def search_by_project(
        self,
        project_name_pattern: str,
        limit: Optional[int] = 10,
        order_by: str | None = None,
    ) -> Sequence[QuotationSchema]:
        job_model = self.design_job_model
        stmt = (
            select(self.quotation_model)
            .join(
                job_model,
                self.quotation_model.job_id == job_model.id,  # type: ignore[attr-defined]
            )
            .where(job_model.title.ilike(f"%{project_name_pattern}%"))  # type: ignore[attr-defined]
        )

        if order_by and hasattr(self.quotation_model, order_by):
            stmt = stmt.order_by(getattr(self.quotation_model, order_by).desc())
        else:
            stmt = stmt.order_by(self.quotation_model.date_created.desc())  # type: ignore[attr-defined]

        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    # ------------------------------------------------------------------
    # CREATE: new quotation (index 01, 02, ...; always R00)
    # ------------------------------------------------------------------
    def create_quotation(
        self,
        *,
        job_no: str,
        company_id: int,
        project_name: str,
        currency: str = "MOP",
        items: List[Dict[str, Any]],
        date_issued: Optional[date] = None,
        revision_no: str = "00",  # ignored for create; always R00
        valid_until: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not date_issued:
            date_issued = date.today()

        # 1) Find job & job_id
        job = self._get_job_by_job_no(job_no)
        job_id = job.id

        # 2) Next quotation index for this job
        next_index = get_next_quotation_index_for_job(
            self.session,
            self.quotation_model,
            job_no,
        )

        # 3) Compose quo_no – new quotation always R00
        quo_no = compose_quo_no(job_no, next_index, revision_no_int=0)

        # 4) Compute line items and total
        total_amount = Decimal("0")
        prepared_items: List[Dict[str, Any]] = []

        for raw in items:
            desc = (
                raw.get("item_desc")
                or raw.get("project_item_description")
                or ""
            )
            unit = raw.get("unit") or ""
            quantity = Decimal(str(raw.get("quantity", 0)))
            unit_price = Decimal(
                str(
                    raw.get("unit_price", raw.get("unit_rate", 0))
                )
            )
            amount = quantity * unit_price
            total_amount += amount

            prepared_items.append(
                {
                    "item_desc": desc,
                    "unit": unit,
                    "quantity": int(quantity),
                    "unit_price": float(unit_price),
                    "amount": float(amount),
                }
            )

        # 5) Create quotation header (using QuotationCreate + extra fields)
        header_payload = QuotationCreate(
            quo_no=quo_no,
            client_id=company_id,
            project_name=project_name,
            date_issued=date_issued,
            status="DRAFTED",
            currency=currency,
            revision_no=0,  # R00
            valid_until=valid_until,
            notes=notes,
        )
        header_data = payload_to_dict(header_payload)
        header_data.update(
            {
                "job_id": job_id,
                "company_id": company_id,
                "total_amount": float(total_amount),
            }
        )

        quotation = self.quotation_model(**header_data)
        self.session.add(quotation)
        self.session.flush()   # get quotation.id
        self.session.refresh(quotation)

        # 6) Insert line items
        for item_data in prepared_items:
            item_record = self.quotation_item_model(
                quotation_id=quotation.id,  # type: ignore[attr-defined]
                **item_data,
            )
            self.session.add(item_record)

        # Flush items; caller (e.g. tests) may choose when to commit
        self.session.flush()

        total_info = {
            "total": total_amount,
            "item_count": len(prepared_items),
        }

        return {
            "quotations": [quotation],
            "quo_no": quo_no,
            "total": total_info["total"],
            "item_count": total_info["item_count"],
        }

    # ------------------------------------------------------------------
    # UPDATE: create new revision (R00 → R01 → R02...)
    # ------------------------------------------------------------------
    def update_quotation(
        self,
        base_quotation_id: int,
        update_payload: QuotationUpdate,
    ) -> QuotationSchema:
        base = self.session.get(self.quotation_model, base_quotation_id)
        if not base:
            raise ValueError(f"Base quotation {base_quotation_id} not found")

        if not getattr(base, "quo_no", None):
            raise ValueError("Base quotation has no quo_no")

        job_no, quotation_index, _ = parse_quo_no(base.quo_no)  # type: ignore[attr-defined]

        new_data = payload_to_dict(update_payload)
        if not new_data:
            raise ValueError("No fields to update")

        ignore_fields = {"id", "quo_no", "revision_no", "date_created", "job_id"}
        changed: Dict[str, Any] = {}

        for key, value in new_data.items():
            if key in ignore_fields:
                continue
            if getattr(base, key, None) != value:
                changed[key] = value

        if not changed:
            raise ValueError("No metadata changes detected; revision not created")

        next_rev = get_next_revision_for_job_and_index(
            self.session,
            self.quotation_model,
            job_no,
            quotation_index,
        )

        new_quo_no = compose_quo_no(job_no, quotation_index, next_rev)

        base_dict = base.model_dump()
        base_dict.update(changed)
        base_dict["quo_no"] = new_quo_no
        base_dict["revision_no"] = next_rev
        base_dict.pop("id", None)

        new_q = self.quotation_model(**base_dict)
        self.session.add(new_q)
        self.session.flush()
        self.session.refresh(new_q)
        return new_q

    # ------------------------------------------------------------------
    # Public API: simple wrapper for generating a quo_no
    # ------------------------------------------------------------------
    def generate_quotation_number(self, job_no: str, revision_no: str = "00") -> str:
        return compose_quo_no(job_no, 1, int(revision_no))
