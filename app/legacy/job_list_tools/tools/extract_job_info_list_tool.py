from pydantic import BaseModel
from app.llm.invoke_claude_llm import invoke_claude_llm

class JobInfoOutputStructure(BaseModel):
    job_type: str
    company_name: str
    job_title: str
    status: str

extract_job_info_prompt = """
You are extracting job information from user input.

User Input: {user_input}

CRITICAL INSTRUCTIONS:
1. Extract the EXACT company name from the input (preserve Chinese characters exactly)
2. Extract the EXACT project/job title from the input (preserve Chinese characters exactly)
3. Determine job_type based on the project description:
   - Use "inspection" if the project involves: 檢測, 檢查, inspection, checking, testing, assessment, audit, examination, verification
   - Use "design" if the project involves: 設計, 建造, 施工, design, construction, build, development, installation
4. Set status to "New"

Output ONLY the extracted information. Do NOT hallucinate or make up company names.
"""

def extract_job_info_list_tool(user_input: str):
    """
    Extract the job info from the user input.
    
    args:
        user_input: str
        
    returns:
        list[JobInfoOutputStructure]: The job info list
    """
    
    prompt = extract_job_info_prompt.format(user_input=user_input)
    
    job_info_list = invoke_claude_llm(prompt, config=JobInfoOutputStructure)
    
    return job_info_list
    