from pydantic import BaseModel
from typing import List

class JobInfo(BaseModel):
    """Individual job record"""
    type: str  # "Finance"."job_type" - "inspection" or "design"
    title: str
    status: str  # "Finance"."job_status", default 'New'
    job_no: str  # Generated job number like JCP-24-03-1


class NewJobNumberOutput(BaseModel):
    """Output containing one or more jobs for a company"""
    company_id: int
    jobs: List[JobInfo]  # List of job records (1 or more)
    messages: List[str]

REACT_PROMPT = '''
    Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}
'''
    
