from typing import Dict, Any, Tuple, Type, List, Optional, Sequence
from decimal import Decimal
from sqlmodel import Session, select
from sqlalchemy.sql import ColumnElement
from app.models.quotation_models import QuotationSchema, QuotationCreate, QuotationUpdate

# ------------------------------------------------------------
# Generic helpers
# ------------------------------------------------------------

def payload_to_dict(payload: QuotationCreate | QuotationUpdate) -> Dict[str, Any]:
    """Convert Pydantic model to dict, excluding None."""
    return payload.model_dump(exclude_none=True)


def compose_quo_no(job_no: str, quotation_index: int, revision_no_int: int) -> str:
    """
    Standard format:
        {job_no}-{quotation_index:02d}-R{revision_no_int:02d}
    """
    return f"{job_no}-{quotation_index:02d}-R{revision_no_int:02d}"


def parse_quo_no(quo_no: str) -> Tuple[str, int, int]:
    """
    Parse:
        Q-JCP-25-01-1-01-R00
           job_no = Q-JCP-25-01-1
           index  = 1
           rev    = 0
    """
    parts = quo_no.split("-")
    if len(parts) < 3:
        return quo_no, 1, 0

    # last example: R00
    last = parts[-1]
    # index example: 01
    index_part = parts[-2]

    job_no = "-".join(parts[:-2])  # remove index & Rxx

    try:
        idx = int(index_part)
    except ValueError:
        idx = 1

    if last.startswith("R"):
        try:
            rev = int(last[1:])
        except ValueError:
            rev = 0
    else:
        rev = 0

    return job_no, idx, rev


# ------------------------------------------------------------
# Internal: detect column name quo_no / quotation_no
# ------------------------------------------------------------

def _get_quo_no_column(quotation_model) -> ColumnElement:
    table = quotation_model.__table__
    if "quo_no" in table.c:
        return table.c["quo_no"]
    if "quotation_no" in table.c:
        return table.c["quotation_no"]
    raise AttributeError("quotation model must have 'quo_no' or 'quotation_no'")


# ------------------------------------------------------------
# Compute next quotation index: 01 → 02 → 03
# ------------------------------------------------------------

def get_next_quotation_index_for_job(
    session: Session,
    quotation_model: Type[QuotationSchema],
    job_no: str,
) -> int:
    qcol = _get_quo_no_column(quotation_model)
    stmt = select(quotation_model).where(qcol.like(f"{job_no}-%"))
    quotations: List[QuotationSchema] = list(session.exec(stmt).all())

    if not quotations:
        return 1

    max_index = 1
    for q in quotations:
        qno = getattr(q, "quo_no", None) or getattr(q, "quotation_no", None)
        if not qno:
            continue
        _, idx, _ = parse_quo_no(qno)
        if idx > max_index:
            max_index = idx

    return max_index + 1


# ------------------------------------------------------------
# Compute next revision: R00 → R01 → R02
# ------------------------------------------------------------

def get_next_revision_for_job_and_index(
    session: Session,
    quotation_model: Type[QuotationSchema],
    job_no: str,
    quotation_index: int,
) -> int:
    qcol = _get_quo_no_column(quotation_model)
    prefix = f"{job_no}-{quotation_index:02d}-"

    stmt = select(quotation_model).where(qcol.like(f"{prefix}R%"))
    quotations: List[QuotationSchema] = list(session.exec(stmt).all())

    if not quotations:
        return 1  # R01

    max_rev = 0
    for q in quotations:
        qno = getattr(q, "quo_no", None) or getattr(q, "quotation_no", None)
        if not qno:
            continue
        _, idx, rev = parse_quo_no(qno)
        if idx == quotation_index and rev > max_rev:
            max_rev = rev

    return max_rev + 1


# ------------------------------------------------------------
# Get latest revision for job
# ------------------------------------------------------------

def get_latest_quotation_for_job(
    session: Session,
    quotation_model: Type[QuotationSchema],
    job_no: str,
) -> Optional[QuotationSchema]:
    qcol = _get_quo_no_column(quotation_model)

    stmt = (
        select(quotation_model)
        .where(qcol.like(f"{job_no}-%"))
        .order_by(
            quotation_model.date_issued.desc(),  # type: ignore
            quotation_model.id.desc(),           # type: ignore
        )
    )
    return session.execute(stmt).first() # type: ignore[return-value]
