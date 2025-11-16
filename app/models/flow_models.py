from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.models.enums import DBTable

# Import schemas for base fields (moved to app/schemas)
from app.schemas.flow_schema import FlowBase

# 数据库表模型（与 DB 一致）
class Flow(FlowBase, table=True):
    __tablename__: str = DBTable.FLOW_TABLE.table
    __table_args__ = {"schema": DBTable.FLOW_TABLE.schema}

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # 由数据库生成，应用侧不写入
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
    )

# 读取输出模型（含只读字段）
class FlowRow(FlowBase):
    id: UUID
    created_at: datetime
