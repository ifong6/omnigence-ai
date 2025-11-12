from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.db.constants import DBTable as DBTable_Enum

# 共有字段（业务层关注的“可写/可读”字段）
class FlowBase(SQLModel):
    session_id: UUID
    identified_agents: Optional[str] = None
    user_request_summary: Optional[str] = None


# 数据库表模型（与 DB 一致）
class Flow(FlowBase, table=True):
    __tablename__ = DBTable_Enum.FLOW_TABLE.split(".")[1]
    __table_args__ = {"schema": DBTable_Enum.FINANCE_SCHEMA}

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # 由数据库生成，应用侧不写入
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
    )

# 创建输入模型（可不传 id，交给 default_factory/DB 生成）
class FlowCreate(FlowBase):
    id: Optional[UUID] = None

# 更新输入模型（全部可选）
class FlowUpdate(SQLModel):
    session_id: Optional[UUID] = None
    identified_agents: Optional[str] = None
    user_request_summary: Optional[str] = None

# 读取输出模型（含只读字段）
class FlowRow(FlowBase):
    id: UUID
    created_at: datetime
