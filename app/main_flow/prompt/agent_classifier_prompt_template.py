from pydantic import BaseModel

class AgentClassifierOutput(BaseModel):
    identified_agents: list[str]
    classifier_msg: str
     
CLASSIFIER_SYSTEM_PROMPT = """
    step 1:Analyze user input

        User input: 
        ```text
        {user_input}

    step 2: Identify agent categories

        Here is the list of available agent categories:

        - finance_agent (Handles: quotations, invoices, jobs/projects, clients/companies, financial documents, billing, pricing)
        - hr_agent (Handles: employee management, hiring, payroll, HR policies, employee records)

        - **IMPORTANT**: "job" in this context means a CLIENT PROJECT or WORK ORDER, NOT an employment position
        - **IMPORTANT**: use concise description for identified agent categories
        
    step 3:Output format, MUST use **AgentClassifierOutput** schema: 
        ```json
        {{
            "identified_agents": ["<a list of agent names based on your inference>"],
            "classifier_msg": "<inference result, if failure, reason why>",
        }}
        ```
"""

