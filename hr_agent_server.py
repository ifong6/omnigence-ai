from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from typing import Optional

# Create FastAPI app
app = FastAPI(title="HR Agent API", version="1.0.0")

class RequestBody(BaseModel):
    user_input: str
    agent_type: str
    session_id: Optional[str] = None

@app.post("/hr-agent")
def call_hr_agent_flow(request: RequestBody):
    """
    HR Agent endpoint - handles human resource related requests.
    Currently returns a mock response. Will be expanded with full agent flow later.
    """
    print(f"[HR_AGENT] Received request: {request.user_input}")

    try:
        # TODO: Implement full HR agent flow with intent analyzer, planner, handlers
        # For now, return a mock response
        result = {
            "agent_output": f"HR Agent processed your request: {request.user_input[:50]}...",
            "status": "success",
            "data": {
                "processed": True,
                "agent_type": "hr_agent"
            }
        }

        return {
            "status": "success",
            "result": result
        }

    except Exception as e:
        print(f"[ERROR][hr_agent]: {str(e)}")
        return {
            "status": "fail",
            "result": str(e)
        }

if __name__ == '__main__':
    uvicorn.run(
        "hr_agent_server:app",
        host="127.0.0.1",
        port=8002,  # HR agent port
        reload=True
    )
