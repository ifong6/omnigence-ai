from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field, model_validator

class FinalResponseModel(BaseModel):
    """
    LangGraph 内部用的最终响应结构:
    - aggregation_agent_node 写入
    - MainFlowState.final_response 保存
    - HTTP 层如果需要可以再包装一层 DTO
    """

    # -----------------核心结果-----------------
    message: str
    status: Literal["success", "partial", "error", "empty"]
    agent_responses: Dict[str, Any] = Field(default_factory=dict)

    # -----------------✅ 比测试 / 调试用，更语义化的名字-----------------
    # 想表达「最终给 tester 看的结果文案」
    # (如果没设值，会自动 fallback 去 message）
    test_result: Optional[str] = None

    @model_validator(mode="after")
    def _ensure_test_result(self) -> "FinalResponseModel":
        """
        如果没显式传test_result, 就用 message 填返，
        确保 unittest 永远有个稳定字段可以断言。
        """
        if self.test_result is None:
            self.test_result = self.message
        return self

