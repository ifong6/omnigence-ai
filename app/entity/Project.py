from typing import List, Optional
from pydantic import BaseModel
from app.entity.Client import Client
from app.entity.ProjectItem import ProjectItem

# Quote class to contain quote data
class Project(BaseModel):
    project_id: Optional[str] = ""
    client: Client
    project_name: Optional[str] = ""
    no: Optional[str] = ""
    date: Optional[str] = ""
    projectItems: List[ProjectItem] = None
    total_amount: Optional[str] = ""
    currency: Optional[str] = ""