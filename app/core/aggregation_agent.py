from app.schemas.main_flow_state import MainFlowState
from app.main_flow.prompt.aggregation_prompt_template import (
    AGGREGATION_PROMPT_TEMPLATE,
    AggregationOutput
)
from app.llm.invoke_claude_llm import invoke_claude_llm
from app.utils.response.legacy_adapter import adapt_legacy
from app.utils.response.agent_response import ResponseStatus
import json

def aggregation_agent_node(state: MainFlowState):
    """
    Aggregation agent that synthesizes multiple agent responses into a coherent message.
    Uses standardized AgentResponse contract for type-safe handling.
    """
    print("[INVOKE][aggregation_agent_node]")

    # Get agent responses from state
    agent_responses = state.agent_responses_summary or {}

    if not agent_responses:
        print("[AGGREGATION] No agent responses found")
        return {
            "final_response": {
                "message": "No responses to aggregate.",
                "status": "empty"
            }
        }

    # Normalize all responses to standard format and track statuses
    formatted_responses = []
    statuses = []

    for agent_name, response in agent_responses.items():
        print(f"\n[AGGREGATION] Processing {agent_name} response:")

        # Convert legacy response to standardized format
        normalized = adapt_legacy(agent_name, response)
        statuses.append(normalized.status)

        print(f"[AGGREGATION] Normalized status: {normalized.status}")

        # Build formatted response with agent-specific enhancements
        response_parts = [normalized.message]

        # Add critical fields for finance agent (job_type is important!)
        if agent_name == "finance_agent" and normalized.data:
            if "job_type" in normalized.data and normalized.data["job_type"]:
                response_parts.insert(0, f"Job Type: {normalized.data['job_type'].capitalize()}")
            if "intents" in normalized.data:
                response_parts.append(f"Intents: {', '.join(normalized.data['intents'])}")

        # Add warnings if present
        if normalized.warnings:
            response_parts.append(f"⚠️ Warnings: {', '.join(normalized.warnings)}")

        # Add error details if present
        if normalized.error_details:
            response_parts.append(f"❌ Error: {normalized.error_details}")

        formatted_text = "\n".join(response_parts)
        formatted_responses.append(f"**{agent_name}**:\n{formatted_text}")

    # Combine all responses with newlines
    responses_text = "\n\n".join(formatted_responses)

    print(f"\n[AGGREGATION] Formatted responses:\n{responses_text}")

    # Use LLM to synthesize responses
    synthesis_prompt = AGGREGATION_PROMPT_TEMPLATE.format(responses=responses_text)

    print("\n[AGGREGATION] Invoking LLM for synthesis...")
    aggregation_result = invoke_claude_llm(synthesis_prompt, AggregationOutput)

    # Support both dict and Pydantic BaseModel returns
    if isinstance(aggregation_result, dict):
        synthesized_message = aggregation_result.get("synthesized_message", "")
    else:
        synthesized_message = getattr(aggregation_result, "synthesized_message", "")

    if not synthesized_message:
        print("[AGGREGATION] Warning: synthesized_message missing; using stringified result")
        synthesized_message = str(aggregation_result)

    print(f"\n[AGGREGATION] Synthesized message:\n{synthesized_message}")

    # Determine overall status based on normalized responses
    overall_status = (
        "success" if any(s == ResponseStatus.SUCCESS for s in statuses) and
                    not any(s == ResponseStatus.ERROR for s in statuses) else
        "partial" if any(s in [ResponseStatus.SUCCESS, ResponseStatus.PARTIAL] for s in statuses) else
        "error" if any(s == ResponseStatus.ERROR for s in statuses) else
        "empty"
    )

    print(f"[AGGREGATION] Overall status: {overall_status} (from {len(statuses)} agents)")

    # Build final response
    final_response = {
        "message": synthesized_message,
        "status": overall_status,
        "agent_responses": agent_responses  # Include raw responses for debugging
    }

    # Print final response before returning to client
    print(f"\n{'='*80}")
    print(f"[AGGREGATION] FINAL RESPONSE TO CLIENT:")
    print(f"{'='*80}")
    print(json.dumps(final_response, indent=2, ensure_ascii=False))
    print(f"{'='*80}\n")

    # Return final response
    return {
        "final_response": final_response
    }
