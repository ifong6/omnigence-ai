# app/models/job_models.py
import os
from typing import Optional, Literal
from datetime import datetime

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import TIMESTAMP

from app.models.enums import DBTable

# Check if we should use schema prefix (default: True for production, False for testing)
USE_DB_SCHEMA = os.getenv("USE_DB_SCHEMA", "1") == "1"


# ============================================================
# Base: Shared fields (NOT a table)
# ============================================================

class JobBaseModel(SQLModel):
    """
    Shared fields, not a table.
    Used for Schema and Model to inherit common fields.
    """
    company_id: int = Field(foreign_key="Finance.company.id" if USE_DB_SCHEMA else "company.id")
    title: str
    status: str  # DB enforces enum: 'NEW'|'IN_PROGRESS'|'COMPLETED'|'CANCELLED'
    job_no: Optional[str] = None
    quotation_status: Optional[str] = None  # DB enforces enum
    quotation_issued_at: Optional[datetime] = None
    invoice_status: Optional[str] = None
    invoice_issued_at: Optional[datetime] = None
    receipt_status: Optional[str] = None
    receipt_issued_at: Optional[datetime] = None

# ============================================================
# Schema：表结构 / ORM 映射（直接对应 Finance.design_job / Finance.inspection_job）
# ============================================================

class DesignJobSchema(JobBaseModel, table=True):
    """
    ORM 映射 Finance.design_job 表的 Schema。

    注意：
    - date_created 由 DB 生成，应用不传，由 server_default(now()) 填充。
    """
    __tablename__: str = DBTable.DESIGN_JOB_TABLE.table
    __table_args__ = {"schema": DBTable.DESIGN_JOB_TABLE.schema} if USE_DB_SCHEMA else {}

    id: Optional[int] = Field(default=None, primary_key=True)

    # DB 生成时间戳，插入时不需要传
    date_created: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
    )


class InspectionJobSchema(JobBaseModel, table=True):
    """
    ORM 映射 Finance.inspection_job 表的 Schema。

    注意：
    - date_created 由 DB 生成，应用不传，由 server_default(now()) 填充。
    """
    __tablename__: str = DBTable.INSPECTION_JOB_TABLE.table
    __table_args__ = {"schema": DBTable.INSPECTION_JOB_TABLE.schema} if USE_DB_SCHEMA else {}

    id: Optional[int] = Field(default=None, primary_key=True)

    # DB 生成时间戳，插入时不需要传
    date_created: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
    )


# ============================================================
# Model：业务数据形状 / DTO
# ============================================================

class JobCreateModel(SQLModel):
    """
    DTO for creating Job records (business layer).
    Does not include id / date_created, id & date_created are handled by DB.
    """
    company_id: int
    title: str
    job_no: Optional[str] = None
    status: str = "NEW"
    quotation_status: str = "NOT_CREATED"
    quotation_issued_at: Optional[datetime] = None


class JobUpdateModel(SQLModel):
    """
    更新 Job 记录时用的 DTO（业务层）。
    所有字段都是可选的（只更新提供的字段）。
    """
    company_id: Optional[int] = None
    title: Optional[str] = None
    status: Optional[str] = None
    job_no: Optional[str] = None
    date_created: Optional[datetime] = None
    quotation_status: Optional[str] = None
    quotation_issued_at: Optional[datetime] = None


class JobReadModel(SQLModel):
    """
    Used for reading / returning Job records (business layer).
    """
    id: int
    company_id: int
    title: str
    status: str
    job_no: Optional[str] = None
    quotation_status: Optional[str] = None
    quotation_issued_at: Optional[datetime] = None
    date_created: datetime
    job_type: Literal["DESIGN", "INSPECTION"]  # 业务层需要知道类型


# ============================================================
# 向后兼容别名（保持老代码暂时不崩）
# ============================================================

# 旧代码里如果有 from app.models.job_models import DesignJob / InspectionJob
# 先用别名兜一下，后面慢慢全量替换成 DesignJobSchema / InspectionJobSchema
DesignJob = DesignJobSchema        # DEPRECATED: 请迁移到 DesignJobSchema
InspectionJob = InspectionJobSchema  # DEPRECATED: 请迁移到 InspectionJobSchema

# 旧代码里如果有 from app.models.job_models import JobCreate / JobUpdate / JobRow
# 先用别名兜一下，后面慢慢全量替换
JobCreate = JobCreateModel  # DEPRECATED: 请迁移到 JobCreateModel
JobUpdate = JobUpdateModel  # DEPRECATED: 请迁移到 JobUpdateModel
JobRow = JobReadModel       # DEPRECATED: 请迁移到 JobReadModel

# 保留旧的 JobModel 别名（之前叫 JobModel，现在改叫 JobBaseModel）
JobModel = JobBaseModel  # DEPRECATED: 请迁移到 JobBaseModel

# Also provide JobBase alias for __init__.py imports
JobBase = JobBaseModel  # DEPRECATED: 请迁移到 JobBaseModel
