from fastapi import FastAPI, Query
import uvicorn
from app.utils.Request import RequestBody
from app.finance_agent.finance_agent_flow import finance_agent_flow
# Create FastAPI app
app = FastAPI(title="Finance Agent API", version="1.0.0")

@app.post("/finance-agent")
def call_finance_agent_flow(request: RequestBody):
    print(f"[FINANCE_AGENT] Received request: {request.user_input}")
    try:
        result = finance_agent_flow(request)

        return {
            "status": "success",
            "result": result
        }

    except Exception as e:
        print(f"[ERROR][main_flow]: {str(e)}")
        return {
            "status": "fail",
            "result": str(e)
        }

if __name__ == '__main__':
    uvicorn.run(
        "finance_agent_server:app",
        host="127.0.0.1",
        port=8001,  # Finance agent port as defined in orchestrator_agent
        reload=True
    )
