from pydantic import BaseModel

class IntentClassifierOutput(BaseModel):
    intents: list[str]
    messages: str # any reasoning

INTENT_PROMPT_TEMPLATE = """
    You are an intent analyzer that identifies users' underlying request intent(s).
    
    Your task:
    Step 1: Read the following input:
        ```text
        {user_input}
    
    Step 2: Identify what the user is asking for.
        
    Step 3: Output format, MUST use **IntentClassifierOutput** schema:
        ```json
        {{
            "intents": ["<summarize a list of user's intents>"],
            "messages": "<Explaining your reasoning and thought process of your intent analysis result>"
        }}
        ```
"""