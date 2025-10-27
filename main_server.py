import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main_flow.main_flow import main_flow, resume_agent
from main_flow.utils.Exception.InterrutpException import InterruptException

# Create FastAPI app
app = FastAPI(title="Main Flow", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

thread_store = {}

class UserRequest(BaseModel):
    message: str
    session_id: str

@app.post("/call-main-flow")
def call_main_flow(user_request: UserRequest):
    print(f"Server received request:{user_request.session_id} {user_request.message}\n")
    try:
        final_result = main_flow(user_request)

        return {
            "status": "success",
            "result": final_result
        }

    except InterruptException as interrupt:
        return {
            "status": "interrupt",
            "session_id": user_request.session_id,
            "result": interrupt.value
        }

    except Exception as e:
        print(f"[ERROR][main_flow]: {str(e)}")
        return {
            "status": "fail",
            "result": str(e)
        }

# ------------------------------------------------------------------------------#

@app.post("/human-in-loop/feedback")
def handle_human_feedback(user_request: UserRequest):
    resume_result = resume_agent(user_request)
    return {
        "status": "interrupt",
        "result": resume_result
    }

if __name__ == '__main__':
    uvicorn.run(
        "main_server:app",  # Replace 'your_module_name' with the actual name of your module.
        host="127.0.0.1",  # Optional: Specify the host, default is '127.0.0.1' (localhost).
        port=8000,  # Optional: Specify the port, default is 8000.
        reload=True  # Enable the auto-reload feature.
    )