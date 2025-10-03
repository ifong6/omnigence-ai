from pydantic import BaseModel

class AgentClassifierOutput(BaseModel):
    agents: list[str]
    messages: list[str]
    human_clarification_flag: bool
    
#----------------------------------------------------------------------------------------------------------#

CLASSIFIER_SYSTEM_PROMPT = """
    step 1:Analyze user input

        User input: 
        
        ```text
        {user_input}

    step 2: Identify agent categories
    
        Here is the list of available agent categories:
        
        - finance_agent (Handles financial queries and operations)
        - human_resource_agent (Handles human resource queries and operations)
        
        - **IMPORTANT**: use concise description for identified agent categories
        


    step 5:Output format, MUST use **AgentClassifierOutput** schema: 
        
        ```json
        {{
            "agents": ["<a list of agent names based on your inference>"],
            "human_clarification_flag": <boolean, "True" if clarification is needed, "False" if not>
            "messages": ["<inference result, if failure, reason why>"],
        }}
        ```
"""

