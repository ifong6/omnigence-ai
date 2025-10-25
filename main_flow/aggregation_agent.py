from main_flow.agent_config.MainFlowState import MainFlowState
from main_flow.prompt.aggregation_prompt_template import (
    AGGREGATION_PROMPT_TEMPLATE,
    AggregationOutput
)
from app.llm.invoke_openai_llm import invoke_openai_llm
import json

def aggregation_agent_node(state: MainFlowState):
    """
    Aggregation agent that synthesizes multiple agent responses into a coherent message.
    Uses LLM to combine responses from finance_agent, hr_agent, etc. into a unified narrative.
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

    # Format agent responses into a list of strings
    formatted_responses = []
    for agent_name, response in agent_responses.items():
        print(f"\n[AGGREGATION] Processing {agent_name} response:")

        # Extract relevant information from each agent's response
        if isinstance(response, dict):
            # For finance agent, extract key fields including job_type
            if agent_name == "finance_agent":
                response_parts = []

                # Add job_type if present (critical for job creation)
                if "job_type" in response and response["job_type"]:
                    response_parts.append(f"Job Type: {response['job_type'].capitalize()}")

                # Add quotation_response if present
                if "quotation_response" in response:
                    quotation_data = response["quotation_response"]
                    agent_output = quotation_data.get("agent_output", "No output")
                    response_parts.append(agent_output)

                # Add other key fields
                if "intents" in response:
                    response_parts.append(f"Intents: {', '.join(response['intents'])}")

                # Combine all parts
                formatted_response = "\n".join(response_parts) if response_parts else json.dumps(response, indent=2)
                formatted_responses.append(f"**{agent_name}**:\n{formatted_response}")

            # For HR agent or others, get agent_output or general result
            elif "agent_output" in response:
                formatted_responses.append(f"**{agent_name}**:\n{response['agent_output']}")
            elif "result" in response:
                result = response["result"]
                if isinstance(result, dict) and "agent_output" in result:
                    formatted_responses.append(f"**{agent_name}**:\n{result['agent_output']}")
                else:
                    formatted_responses.append(f"**{agent_name}**:\n{json.dumps(result, indent=2)}")
            else:
                formatted_responses.append(f"**{agent_name}**:\n{json.dumps(response, indent=2)}")
        else:
            formatted_responses.append(f"**{agent_name}**:\n{str(response)}")

    # Combine all responses with newlines
    responses_text = "\n\n".join(formatted_responses)

    print(f"\n[AGGREGATION] Formatted responses:\n{responses_text}")

    # Use LLM to synthesize responses
    synthesis_prompt = AGGREGATION_PROMPT_TEMPLATE.format(responses=responses_text)

    print("\n[AGGREGATION] Invoking LLM for synthesis...")
    aggregation_result = invoke_openai_llm(synthesis_prompt, AggregationOutput)

    synthesized_message = aggregation_result.synthesized_message

    print(f"\n[AGGREGATION] Synthesized message:\n{synthesized_message}")

    # Build final response
    final_response = {
        "message": synthesized_message,
        "status": "success",
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
