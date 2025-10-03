from pydantic import BaseModel
from typing import Annotated, Any
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

class FinanceAgentState(BaseModel):
    user_input: str
    intents: list[str] = None
    quotation_info: list[dict] = None
    next_agents: list[str] = None       
    quotation_csv_info: list[dict] = None
    quotation_file_names: list[str] = None
    messages: Annotated[list[AnyMessage], add_messages]
    
    