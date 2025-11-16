from app.schemas.finance_agent_state import FinanceAgentState
from app.finance_agent.job_list.job_crud_tools import job_crud_tools
from app.finance_agent.utils.invoke_react_agent import invoke_react_agent

def job_crud_handler_node(state: FinanceAgentState):
    print("\n" + "=" * 100)
    print("[HANDLER_INVOKE][job_crud_handler_node]")
    print("=" * 100)
    print(f"[HANDLER] User input: {state.user_input}")
    print(f"[HANDLER] Job type: {state.job_type}")
    print(f"[HANDLER] Session context: index={state.index}, next_handlers={state.next_handlers}")
    print("=" * 100)

    try:
        # Enhance the user input with job type information for the React agent
        enhanced_input = f"{state.user_input}\n\nIMPORTANT: The job type for this request is: {state.job_type}"
        print(f"[HANDLER] Enhanced input for React agent: {enhanced_input}")

        response = invoke_react_agent(tools=job_crud_tools, user_input=enhanced_input)

        print("\n" + "=" * 100)
        print("[HANDLER] REACT AGENT RESPONSE:")
        print("=" * 100)
        print(f"Response type: {type(response)}")

        if isinstance(response, dict):
            print(f"Response keys: {list(response.keys())}")

            output = response.get('output', 'NOT FOUND')
            print(f"\n[FINAL OUTPUT]: {output}")

            # Print intermediate steps to see what tools were called
            intermediate_steps = response.get('intermediate_steps', [])
            print(f"\n[TOOL EXECUTION TRACE]")
            print(f"Total steps executed: {len(intermediate_steps)}")

            if not intermediate_steps:
                print("⚠️  WARNING: No tools were executed by React agent!")

            for idx, (action, observation) in enumerate(intermediate_steps, 1):
                print(f"\n{'=' * 80}")
                print(f"Step {idx}:")
                print(f"  Tool: {action.tool}")
                print(f"  Input Type: {type(action.tool_input)}")
                print(f"  Input: {action.tool_input}")

                # Truncate long outputs for readability
                obs_str = str(observation)
                if len(obs_str) > 300:
                    print(f"  Output: {obs_str[:300]}...")
                else:
                    print(f"  Output: {obs_str}")

                # Check for errors in observation
                if "error" in obs_str.lower() or "failed" in obs_str.lower():
                    print(f"  ⚠️  ERROR DETECTED IN OBSERVATION!")

            print("=" * 80)

            # Check if job was actually created by looking for success indicators
            success_indicators = ["successfully created", "job no", "jcp-", "jicp-"]
            has_success = any(indicator in output.lower() for indicator in success_indicators)

            if not has_success:
                print(f"\n⚠️  WARNING: Job creation may have failed - no success indicators found in output")
                print(f"Output: {output}")
        else:
            print(f"⚠️  Unexpected response type: {response}")

    except Exception as e:
        print("\n" + "=" * 100)
        print(f"❌ ERROR in job_crud_handler_node: {str(e)}")
        print("=" * 100)
        import traceback
        traceback.print_exc()
        print("=" * 100)

    print(f"\n[HANDLER] Incrementing index from {state.index} to {state.index + 1}")
    print("=" * 100 + "\n")

    # Return both the incremented index and the handler result
    return {
        "index": state.index + 1,
        "handler_result": response  # Include the React agent response
    }

if __name__ == "__main__":
    print("Running job_crud_handler_node...")

    state = FinanceAgentState(
        user_input="create a new job for 金龍酒店, 結構安全檢測",
    )
    job_crud_handler_node(state)
    
    
