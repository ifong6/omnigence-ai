from fastapi import APIRouter, HTTPException
from app.controllers.BaseController import BaseController
from app.core.orchestrator_agent import orchestrator_agent_flow, resume_agent
from app.finance_agent.finance_agent_flow import finance_agent_flow
from app.utils.exceptions import InterruptException
from app.utils.requests import UserRequest, HumanInTheLoopRequest

# Create router
router = APIRouter(prefix="/api/v1/agents", tags=["AI Agents"])

class AgentController(BaseController):
    @staticmethod
    @BaseController.handle_exceptions
    @router.post("/orchestrator", response_model=dict)
    def call_orchestrator_agent(request: UserRequest):
        BaseController.log_request(
            "/api/v1/agents/orchestrator",
            {"session_id": request.session_id, "message": request.message[:100]}
        )

        try:
            # Execute orchestrator agent workflow
            final_result = orchestrator_agent_flow(request) # <-- TRIGGERS FLOW

            response = {
                "status": "success",
                "result": final_result
            }

            BaseController.log_response("/api/v1/agents/orchestrator", response)
            return response

        except InterruptException as interrupt:
            # Agent needs human feedback
            response = {
                "status": "interrupt",
                "session_id": request.session_id,
                "result": interrupt.value,
                "requires_feedback": True
            }
            return response

        except ValueError as e:
            # Invalid request format or data
            raise BaseController.error_response(
                message="Invalid request",
                errors=[{"code": "INVALID_REQUEST", "message": str(e)}],
                status_code=400
            )

        except Exception as e:
            # Unexpected error
            print(f"[ERROR][orchestrator_agent]: {str(e)}")
            raise BaseController.error_response(
                message="Agent execution failed",
                errors=[{"code": "AGENT_ERROR", "message": str(e)}],
                status_code=500
            )

    @staticmethod
    @BaseController.handle_exceptions
    @router.post("/human-in-the-loop", response_model=dict)
    def handle_human_in_the_loop(request: HumanInTheLoopRequest):
        BaseController.log_request(
            "/api/v1/agents/human-in-the-loop",
            {"session_id": request.session_id, "message": request.message[:100]}
        )

        try:
            # Resume agent workflow with feedback
            resume_result = resume_agent(UserRequest(session_id=request.session_id, message=request.message))

            response = {
                "status": "success",
                "result": resume_result
            }

            BaseController.log_response("/api/v1/agents/human-in-the-loop", response)
            return response

        except KeyError as e:
            # Session not found or invalid
            raise BaseController.error_response(
                message="Invalid session",
                errors=[{"code": "INVALID_SESSION", "message": f"Session not found: {str(e)}"}],
                status_code=404
            )

        except Exception as e:
            # Unexpected error
            print(f"[ERROR][human-in-the-loop]: {str(e)}")
            raise BaseController.error_response(
                message="Failed to process feedback",
                errors=[{"code": "FEEDBACK_ERROR", "message": str(e)}],
                status_code=500
            )

    @staticmethod
    @BaseController.handle_exceptions
    @router.post("/finance-agent", response_model=dict)
    def call_finance_agent(request: UserRequest):
        BaseController.log_request(
            "/api/v1/agents/finance-agent",
            {"session_id": request.session_id, "message": request.message[:100]}
        )

        flow_request = UserRequest(
            session_id=request.session_id,
            message=request.message,
        )

        try:
            # Execute finance agent workflow
            result = finance_agent_flow(UserRequest(session_id=request.session_id, message=request.message))

            response = {
                "status": "success",
                "result": result
            }

            BaseController.log_response("/api/v1/agents/finance-agent", response)
            return response

        except Exception as e:
            print(f"[ERROR][finance_agent]: {str(e)}")
            raise BaseController.error_response(
                message="Finance agent execution failed",
                errors=[{"code": "FINANCE_AGENT_ERROR", "message": str(e)}],
                status_code=500
            )

    @staticmethod
    @router.get("/health", response_model=dict)
    def agent_health_check():
        return BaseController.success_response(
            data={
                "status": "success",
                "data": {
                    "agents": {
                        "orchestrator": "available",
                        "finance": "available",
                        "hr": "available"
                    },
                    "services": {
                        "job_service": "available",
                        "quotation_service": "available",
                        "company_service": "available"
                    }
                }
            },
            message="All agent services are operational"
        )

    @staticmethod
    @BaseController.handle_exceptions
    @router.get("/status/{session_id}", response_model=dict)
    def get_agent_status(session_id: str):
        # Placeholder implementation
        # In production, this would query actual session state from storage
        return BaseController.success_response(
            data={
                "session_id": session_id,
                "state": "active",
                "current_agent": "orchestrator",
                "last_update": "2025-01-15T10:30:00Z"
            },
            message=f"Session {session_id} status retrieved"
        )
    