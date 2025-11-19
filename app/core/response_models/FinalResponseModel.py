from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field, model_validator

class FinalResponseModel(BaseModel):
    message: str
    status: Literal["success", "partial", "error", "empty"]
    agent_responses: Dict[str, Any] = Field(default_factory=dict)

    test_result: str = ""

    # @model_validator(mode="after") 是什么?
    # - model_validator:Pydantic v2 的模型级校验器(对整个 model 做处理，不是单个字段)。
    # - mode="after":在所有字段都解析完之后 才跑这个函数。
    # - 换句话说:FinalResponseModel(...) 创建完、所有字段都有值了,才会执行 _ensure_test_result
    @model_validator(mode="after")
    def _ensure_test_result(self) -> "FinalResponseModel":
        if not self.test_result:
            self.test_result = self.message
        return self