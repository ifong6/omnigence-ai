"""
PreRoutingLogger Prompt Template

This prompt is used to summarize the flow state before routing begins.
It captures what agents were identified and what the user's intent is.
"""

from pydantic import BaseModel, Field

class PreRoutingLoggerOutput(BaseModel):
    """Structured output for the pre-routing logger"""
    summary: str = Field(
        description="Concise summary of the flow state before routing"
    )
    user_intent: str = Field(
        description="Brief description of what the user wants (1 sentence)"
    )
    identified_agents: list[str] = Field(
        description="List of agents that will handle this request"
    )

PRE_ROUTING_LOGGER_PROMPT = """
    You are a logging agent that creates user-facing confirmation messages before task delegation.

    **Current Flow State:**

    User Input:
    {user_input}

    Classifier Message:
    {classifier_message}

    **Instructions:**
    Create a structured output with the following fields:

    1. **summary**: A clear, polite confirmation message DIRECTLY ADDRESSED TO THE USER.
       - Start with "You mentioned..." to acknowledge what the user said
       - Then say "I will..." to explain what you'll do next
       - Be conversational, warm, and reassuring
       - Include specific details from the user's input
       - Example: "You mentioned you want to create a new job for [company name] for [project]. I will handle this by setting up the project and associating it with the client."

    2. **user_intent**: A brief one-sentence description of what the user wants

    3. **identified_agents**: A list of agent names that will handle this request

    **Output Format:**
    ```json
    {{
        "summary": "You mentioned... I will...",
        "user_intent": "One sentence description",
        "identified_agents": ["agent_name"]
    }}
    ```
"""
