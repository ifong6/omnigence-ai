from main_flow.agent_config.MainFlowState import MainFlowState
from langchain_core.messages import AIMessage
import requests
from langgraph.types import interrupt

def routing_agent_node(state: MainFlowState):
    """
    Enhanced routing node that routes full user_input to specialized agents.
    Each agent receives the complete user context to do its own domain-specific parsing.
    """
    # Check if we have agents from classifier
    needs_human = getattr(state, 'human_clarification_flag', False)
    if needs_human:
        print(f"[ROUTING] invoke_human")
        return interrupt(
            value={
                "message": AIMessage(content=state.messages[-1].content),
                "human_clarification_flag": False  # Reset flag for next iteration
            }
        )
        
    agents = getattr(state, 'agents', None)
    if agents and len(agents) > 0:
        print(f"[ROUTING] Found {agents} to route to")
        
        # Route full user_input to each specialized agent
        agent_responses = {}
        routing_log = []
        for agent_type in agents:
            print(f"[ROUTING] Routing full user_input to {agent_type}")
            payload = {
                "user_input": state.user_input,
                "agent_type": agent_type,
            }
            try:
                # Make HTTP call to specialized agent with full context
                agent_responses[agent_type] = call_specialized_agent(payload)

                routing_log.append(
                    AIMessage(content=f"Successfully routed request to {agent_type}")
                )

            except Exception as e:
                print(f"[ROUTING ERROR] Failed to call {agent_type}: {e}")
                agent_responses[agent_type] = {
                    "status": "error",
                    "message": f"Failed to reach {agent_type}: {str(e)}"
                }
                routing_log.append(
                    AIMessage(content=f"Failed to route request to {agent_type}: {str(e)}")
                )
        
        # Simple agent summary logging
        agent_responses_summary = ""
        for (agent_type, response) in enumerate(agent_responses.items()):
            messages = response.get("messages", "no response")
            agent_responses_summary = ", ".join(f"{agent_type}: {messages}")
            
        return {
            "agent_responses_summary": agent_responses_summary,
        }
    

# ------------------------------------------------------------------------------#

def call_specialized_agent(payload: dict) -> dict:
    """
    Make HTTP call to specialized agent endpoint with full user context.

    Args:
        payload: Dictionary containing agent_type, user_input, and other parameters

    Returns:
        dict: Response from the specialized agent
    """
    # Extract agent_type from payload
    agent_type = payload.get("agent_type")
    if not agent_type:
        raise Exception("agent_type not found in payload")

    # Map agent types to endpoints
    agent_endpoints = {
        "finance_agent": "http://localhost:8002/finance-agent",
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
            timeout=30  # 30 second timeout
        )
        
        response.raise_for_status()  # raise an exception if the HTTP call fails
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP request failed: {str(e)}")  # raise an exception if the HTTP call fails if the HTTP call fails           
    
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")  # raise an exception if the HTTP call fails if the HTTP call fails