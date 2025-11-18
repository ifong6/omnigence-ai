import unittest

from app.core.orchestrator_agent import orchestrator_agent_flow
from app.utils.requests import UserRequest
from app.core.response_models.FinalResponseModel import FinalResponseModel

class TestOrchestratorNonFinancialRequests(unittest.TestCase):
    def test_non_financial_request_not_routed_to_finance(self):
        user_request = UserRequest(
            message="Can you help me draft a polite email to my landlord about the noisy neighbors?",
            session_id="test_session_non_finance_1",
        )
        print(f"[Test][test_non_financial_request_not_routed_to_finance] user_request: {user_request.message}")

        state = orchestrator_agent_flow(user_request)

        # 1) 有 final_response
        self.assertIsNotNone(state.final_response)
        self.assertIsInstance(state.final_response, FinalResponseModel)

        final = state.final_response

        # 2) non-financial 情况：冇 agent_responses → status = "empty"
        self.assertEqual(final.status, "empty") # type: ignore
        self.assertEqual(final.agent_responses, {}) # type: ignore

        # 3) 用 test_result 做断言（稳定字段）
       
        self.assertEqual(final.test_result, "No responses to aggregate.") # type: ignore

if __name__ == "__main__":
    unittest.main()
