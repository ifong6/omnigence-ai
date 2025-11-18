# main_server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.orchestrator_agent import orchestrator_agent_flow
from app.utils.requests import UserRequest
from app.utils.exceptions import InterruptException
from app.core.agent_config.MainFlowState import MainFlowState
from app.core.response_models.FinalResponseModel import FinalResponseModel
from app.dto.aggregation_dto import AggregationResponseDTO
from app.dto.orchestrator_dto import (
    OrchestratorInterruptResponseDTO,
    OrchestratorErrorResponseDTO,
)

app = FastAPI(
    title="Product v01 - Finance Task Orchestrator API",
    version="1.0.0",
    description="Multi-agent system with finance task orchestration workflows",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/call-orchestrator-agent",
    response_model=(
        AggregationResponseDTO
        | OrchestratorInterruptResponseDTO
        | OrchestratorErrorResponseDTO
    ),
)
def call_orchestrator_agent(user_request: UserRequest):
    """
    Orchestrator HTTP 入口：
    - 调用 LangGraph workflow
    - 用 aggregation_agent_node 写入嘅 state.final_response
      组装 AggregationResponseDTO
    """
    print(
        f"[ORCHESTRATOR FLOW] Received request: "
        f"{user_request.session_id} {user_request.message}\n"
    )

    try:
        # 1) 跑整条 LangGraph workflow，返回 MainFlowState
        state: MainFlowState = orchestrator_agent_flow(user_request)

        # 2) 从 state.final_response 拿 aggregation agent 的最终结果
        final: FinalResponseModel | None = state.final_response

        # 3) 如果 aggregator 冇写到 final_response，就兜个默认
        if final is None:
            return AggregationResponseDTO(
                message="No responses to aggregate.",
                status="empty",
                agent_responses={},
                session_id=state.session_id,
                flow_uuid=state.flow_uuid,
                identified_agents=state.identified_agents or [],
            )

        # 4) 正常情况：final 系 FinalResponseModel
        return AggregationResponseDTO(
            message=final.message,
            status=final.status,
            agent_responses=final.agent_responses,
            session_id=state.session_id,
            flow_uuid=state.flow_uuid,
            identified_agents=state.identified_agents or [],
        )

    except InterruptException as interrupt:
        # HITL 中断场景
        return OrchestratorInterruptResponseDTO(
            status="interrupt",
            session_id=user_request.session_id,
            result=interrupt.value,
        )

    except Exception as e:
        # 未预期错误场景
        print(f"[ERROR][main_flow]: {str(e)}")
        return OrchestratorErrorResponseDTO(
            status="fail",
            result=str(e),
        )
