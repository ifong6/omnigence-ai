from pydantic import BaseModel
from app.llm.invoke_openai_llm import invoke_openai_llm

class JobInfoOutputStructure(BaseModel):
    job_type: str
    company_name: str
    job_title: str
    job_description: str
    status: str

extract_job_info_prompt = """
    Please analyze the user input and extract the job info.

    Step 1: Analyze the user input:

        {{user_input}}

    Step 2: Output the job info, **MUST** use JobInfoOutputStructure:
    {{
        new_job_list:[
            {{
                "job_type": "<inspection" or "design" per your analysis>,
                "company_name": "<the provided company name>",
                "job_title": "<the provided job title>",
                "job_description": "<the provided job description>"
                "status": "<New>"
            }},
            ... (if there are multiple jobs) ...
        ]
    }}
"""

def extract_job_info_list_tool(user_input: str) -> list[JobInfoOutputStructure]:
    """
    Extract the job info from the user input.
    
    args:
        user_input: str
        
    returns:
        list[JobInfoOutputStructure]: The job info list
    """
    
    prompt = extract_job_info_prompt.format(user_input=user_input)
    
    job_info_list = invoke_openai_llm(prompt, config=JobInfoOutputStructure)
    
    return job_info_list
    