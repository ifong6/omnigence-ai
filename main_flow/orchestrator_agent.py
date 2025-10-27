from main_flow.agent_config.MainFlowState import MainFlowState
from langchain_core.messages import AIMessage
import requests
from langgraph.types import interrupt
from concurrent.futures import ThreadPoolExecutor, as_completed

def orchestrator_agent_node(state: MainFlowState):
    """
    Orchestrator node that delegates tasks to worker agents in parallel.
    Uses ThreadPoolExecutor to make concurrent HTTP calls to multiple agents.
    Each agent receives the complete user context to do its own domain-specific parsing.
    """
    # Check if we have agents from classifier
    needs_human = getattr(state, 'human_clarification_flag', False)
    if needs_human:
        print(f"[ORCHESTRATOR] invoke_human")
        return interrupt(
            value={
                "message": AIMessage(content=state.messages[-1].content),
                "human_clarification_flag": False  # Reset flag for next iteration
            }
        )

    agents = getattr(state, 'identified_agents', None)
    if agents and len(agents) > 0:
        print(f"[ORCHESTRATOR] Found {agents} to delegate to")
        print(f"[ORCHESTRATOR] Making parallel HTTP calls using ThreadPoolExecutor")

        # Prepare payloads for all agents
        agent_payloads = []
        for agent_type in agents:
            payload = {
                "user_input": state.user_input,
                "agent_type": agent_type,
                "session_id": state.session_id,  # Include session_id for agent checkpointing
            }
            agent_payloads.append((agent_type, payload))

        # Make parallel HTTP calls using ThreadPoolExecutor
        agent_responses = {}
        orchestrator_log = []

        with ThreadPoolExecutor() as executor:
            # Submit all agent calls to thread pool
            future_to_agent = {
                executor.submit(call_worker_agent, payload): agent_type
                for agent_type, payload in agent_payloads
            }

            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_type = future_to_agent[future]
                try:
                    response = future.result()
                    agent_responses[agent_type] = response
                    print(f"[ORCHESTRATOR] ✓ Successfully received response from {agent_type}")
                    orchestrator_log.append(
                        AIMessage(content=f"Successfully delegated request to {agent_type}")
                    )
                except Exception as e:
                    print(f"[ORCHESTRATOR ERROR] Failed to call {agent_type}: {e}")
                    agent_responses[agent_type] = {
                        "status": "error",
                        "message": f"Failed to reach {agent_type}: {str(e)}"
                    }
                    orchestrator_log.append(
                        AIMessage(content=f"Failed to delegate request to {agent_type}: {str(e)}")
                    )

        print(f"[ORCHESTRATOR] All parallel agent calls completed")

        # Pass through all agent responses without hardcoding specific fields
        # Each agent can return different response structures based on their task
        agent_responses_summary = {}
        for agent_type, response in agent_responses.items():
            if isinstance(response, dict) and "result" in response:
                # Extract the result from the response
                agent_responses_summary[agent_type] = response["result"]
            else:
                # Pass through as-is
                agent_responses_summary[agent_type] = response

        return {
            "agent_responses_summary": agent_responses_summary
        }
    

# ------------------------------------------------------------------------------#

def call_worker_agent(payload: dict) -> dict:
    """
    Make HTTP call to worker agent endpoint with full user context.

    Args:
        payload: Dictionary containing agent_type, user_input, and other parameters

    Returns:
        dict: Response from the worker agent
    """
    # Extract agent_type from payload
    agent_type = payload.get("agent_type")
    if not agent_type:
        raise Exception("agent_type not found in payload")

    # Map agent types to endpoints
    agent_endpoints = {
        "finance_agent": "http://localhost:8001/finance-agent",
        "hr_agent": "http://localhost:8002/hr-agent",
        "human_resource_agent": "http://localhost:8003/human-resource-agent",
        # Add more agent endpoints as needed
    }

    endpoint = agent_endpoints.get(agent_type)  # get the endpoint for the agent
    if not endpoint:
        raise Exception(f"No endpoint configured for agent: {agent_type}")

    try:
        response = requests.post(  # make the HTTP call to the agent
            url=endpoint,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=90  # 90 second timeout for complex flows with dynamic routing
        )
        
        response.raise_for_status()  # raise an exception if the HTTP call fails
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP request failed: {str(e)}")  # raise an exception if the HTTP call fails if the HTTP call fails           
    
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")  # raise an exception if the HTTP call fails if the HTTP call fails