# app/core/aggregation_agent.py

from typing import Any, Dict, List, Tuple, Literal
import json

from app.core.agent_config.MainFlowState import MainFlowState
from app.prompt.aggregation_prompt_template import (
    AGGREGATION_PROMPT_TEMPLATE,
    AggregationOutput,
)
from app.llm.invoke_claude_llm import invoke_claude_llm
from app.core.response_models.FinalResponseModel import FinalResponseModel


# ======================================================================
#                   MAIN: aggregation_agent_node
# ======================================================================

def aggregation_agent_node(state: MainFlowState):
    """
    Aggregation agent:
    - 唔再拆各个 agent 嘅 raw data 结构
    - 只依赖每个 agent 提供嘅「status + 一段可读 summary」
    - 最终写入 state.final_response (FinalResponseModel)
    """
    print("[INVOKE][aggregation_agent_node]")

    agent_responses: Dict[str, Any] = state.agent_responses or {}

    # ------------------------------------------------------------------
    # 情况 1：完全冇任何 agent response（例如 non-financial test）
    # ------------------------------------------------------------------
    if not agent_responses:
        print("[AGGREGATION] No agent responses found")

        final_response = FinalResponseModel(
            # 给「最终 user」看的文案（更易理解）
            message=(
                "I can currently only help with finance-related tasks "
                "(jobs, quotations, invoices, receipts, etc.). "
                "This request looks non-financial, so I didn’t route it "
                "to any internal finance agent."
            ),
            status="empty",
            agent_responses={},
            # 保留给 unittest / developer 用的稳定字段
            test_result="No responses to aggregate.",
        )

        print(f"\n{'=' * 80}")
        print("[AGGREGATION] FINAL RESPONSE TO CLIENT (empty):")
        print(f"{'=' * 80}")
        print(json.dumps(final_response.model_dump(), indent=2, ensure_ascii=False))
        print(f"{'=' * 80}\n")

        return {
            "final_response": final_response
        } 

    # ------------------------------------------------------------------
    # 情况 2：有一个或多个 agent responses，要做综合
    # ------------------------------------------------------------------

    formatted_blocks: List[str] = []
    statuses: List[str] = []

    for agent_name, response in agent_responses.items():
        print(f"\n[AGGREGATION] Processing {agent_name} response:")

        status, summary_text = _extract_agent_summary(response)
        statuses.append(status)
        print(f"[AGGREGATION] Status: {status}")

        formatted_blocks.append(f"**{agent_name}**:\n{summary_text}")

    responses_text = "\n\n".join(formatted_blocks)
    print(f"\n[AGGREGATION] Formatted responses:\n{responses_text}")

    # 调 LLM 做综合
    synthesis_prompt = AGGREGATION_PROMPT_TEMPLATE.format(responses=responses_text)
    print("\n[AGGREGATION] Invoking LLM for synthesis...")
    aggregation_result = invoke_claude_llm(synthesis_prompt, AggregationOutput)

    # 从 LLM 结果中抽 synthesized_message
    synthesized_message = _extract_synthesized_message(aggregation_result)

    # 计算 overall_status
    overall_status = _compute_overall_status(statuses)
    print(f"[AGGREGATION] Overall status: {overall_status} (from {len(statuses)} agents)")

    # 用 FinalResponseModel + test_result
    final_response = FinalResponseModel(
        message=synthesized_message,
        status=overall_status, 
        agent_responses=agent_responses,
        test_result=synthesized_message,
    )

    print(f"\n{'=' * 80}") 
    print("[AGGREGATION] FINAL RESPONSE TO CLIENT:")
    print(f"{'=' * 80}")
    print(json.dumps(final_response.model_dump(), indent=2, ensure_ascii=False))
    print(f"{'=' * 80}\n")

    return {
        "final_response": final_response
    }


# ======================================================================
#                           HELPERS
# ======================================================================

def _extract_agent_summary(response: Any) -> Tuple[str, str]:
    """
    从「各个 agent 的返回」中抽取：
      - status: 用嚟计算 overall_status
      - text:   用嚟拼入 LLM prompt(总结用)

    约定（推荐每个 agent 返回类似结构）：
      {
        "status": "success" | "partial" | "error" | "empty" | "unknown",
        "message": "人睇得明嘅总结文字",
        "test_result": "比 unittest 用嘅 summary(可选)",
        "data": {...}
      }
    """
    status = "unknown"

    # dict 情况（最常见）
    if isinstance(response, dict):
        status = str(response.get("status", "unknown"))
        text = (
            response.get("test_result")
            or response.get("message")
            or str(response)
        )
        return status, text

    # pydantic model / 其他 object 情况
    for attr in ("test_result", "message"):
        if hasattr(response, attr):
            value = getattr(response, attr)
            if isinstance(value, str) and value.strip():
                return status, value

    # 兜底
    return status, str(response)


def _extract_synthesized_message(aggregation_result: Any) -> str:
    """
    尝试从 aggregation_result 取出 synthesized_message，
    如果冇就 fallback 做 str(result)。
    """
    if isinstance(aggregation_result, dict):
        synthesized_message = aggregation_result.get("synthesized_message", "")
    else:
        synthesized_message = getattr(aggregation_result, "synthesized_message", "")

    if not synthesized_message:
        print("[AGGREGATION] Warning: synthesized_message missing; using stringified result")
        synthesized_message = str(aggregation_result)

    print(f"\n[AGGREGATION] Synthesized message:\n{synthesized_message}")
    return synthesized_message


def _compute_overall_status(statuses: List[str]) -> Literal["success", "partial", "error", "empty"]:
    if any(s == "success" for s in statuses) and not any(s == "error" for s in statuses):
        return "success"
    if any(s in ("success", "partial") for s in statuses):
        return "partial"
    if any(s == "error" for s in statuses):
        return "error"
    return "empty"
