import unittest
import uuid

from app.core.orchestrator_agent import orchestrator_agent_flow
from app.utils.requests import UserRequest
from app.utils.exceptions import InterruptException
from app.core.response_models.FinalResponseModel import FinalResponseModel


class TestOrchestratorCreateJob(unittest.TestCase):
    """
    Integration-style tests for orchestrator_agent_flow:

    - Focus on correct routing to finance_agent
    - Not deeply asserting detailed finance business logic
    """

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _assert_routed_to_finance(self, state, msg: str) -> None:
        """
        Shared helper: Check if orchestrator routed to finance_agent.
        """
        identified_agents = state.identified_agents or []
        lower_agents = [a.lower() for a in identified_agents]

        self.assertTrue(
            any("finance" in a for a in lower_agents),
            f"{msg} - expected routing to finance agent, got: {identified_agents}",
        )

    def _print_final_summary(self, final: FinalResponseModel, label: str) -> None:
        """
        Shared helper: Print a brief summary of final response for debugging.
        """
        agent_keys = list((final.agent_responses or {}).keys())
        print(f"[TEST][{label}] final.status = {final.status}")
        print(f"[TEST][{label}] agents      = {agent_keys}")
        print(f"[TEST][{label}] test_result = {final.test_result!r}")

    # ---------------------------------------------------------
    # TEST CASE 1: Create design job with existing company
    # ---------------------------------------------------------

    def test_create_design_job_with_existing_company(self):
        """
        Scenario:
        - User asks to create a *design* job for an (assumed) existing company.
        Focus:
        - Orchestrator should route to finance_agent
        - final_response should be a FinalResponseModel instance
        """
        user_request = UserRequest(
            message=(
                "I need to create a design job for ABC Company. "
                "The project is Boston Building Design. "
                "The client contact is John Doe Company."
            ),
            session_id=str(uuid.uuid4()),
        )

        print(f"\n[TEST] Creating design job for existing company")
        print(f"[TEST] User request: {user_request.message}")

        try:
            # Execute orchestrator flow
            state = orchestrator_agent_flow(user_request)

            # ========== Basic State Validation ==========
            self.assertIsNotNone(
                state,
                "orchestrator_agent_flow should return MainFlowState",
            )
            self.assertIsNotNone(
                state.final_response,
                "State should have final_response",
            )
            self.assertIsInstance(
                state.final_response,
                FinalResponseModel,
                "final_response should be FinalResponseModel instance",
            )

            # ========== Finance Agent Routing Validation ==========
            self._assert_routed_to_finance(
                state,
                msg="Design job creation should be routed to finance agent",
            )

            # ========== Response Content Validation ==========
            final = state.final_response
            assert final is not None  # type: ignore[unreachable]

            # agent_responses field must exist (can be empty dict)
            self.assertIsNotNone(
                final.agent_responses,
                "Should have agent_responses for finance operations",
            )

            # If not completely empty, require at least one agent response
            if final.status != "empty" or final.agent_responses:
                self.assertGreater(
                    len(final.agent_responses),
                    0,
                    "When status is not 'empty', agent_responses should not be empty",
                )
                # test_result should be a non-empty string (LLM synthesized result)
                self.assertIsInstance(final.test_result, str)
                self.assertTrue(
                    final.test_result.strip(),
                    "test_result should contain synthesized text for tester",
                )

            # Should have finance_agent in responses (if responses exist)
            if final.agent_responses:
                agent_keys = [str(k).lower() for k in final.agent_responses.keys()]
                self.assertTrue(
                    any("finance" in k for k in agent_keys),
                    f"Should have finance_agent response, got: {list(final.agent_responses.keys())}",
                )

            # ========== Success Criteria / Logging ==========
            if final.status == "empty" and final.agent_responses == {}:
                print("[TEST] ⚠ Finance agent server not running (port 8001?)")
                print("[TEST] ✓ But routing to finance_agent was CORRECT")
            else:
                print("[TEST] ✓ Job creation completed successfully")
                print(f"[TEST] ✓ Final response status: {final.status}")

            # Brief summary for debugging
            self._print_final_summary(final, label="design_job_existing_company")
            print("[TEST] ✓ Test passed (routing validated)\n")

        except InterruptException as interrupt:
            # HITL interrupt is acceptable - agent may need clarification
            print("[TEST] ⚠ HITL interrupt triggered (acceptable for this test)")
            print(f"[TEST] Interrupt value: {interrupt.value}")
            self.assertIsNotNone(interrupt.state, "Interrupt should carry state")

    # ---------------------------------------------------------
    # TEST CASE 2: Create inspection job with new company
    # ---------------------------------------------------------

    def test_create_inspection_job_with_new_company(self):
        """
        Test creating an inspection job with company creation.

        Expected flow:
        1. Orchestrator routes to finance_agent
        2. Finance agent creates company first
        3. Agent creates inspection job
        4. Returns both company_id and job_no
        """
        user_request = UserRequest(
            message=(
                "Create an inspection job for a new company called XYZ Construction. "
                "Company address: 456 Oak Avenue, Cambridge, MA 02138. "
                "Phone: 617-555-0200. "
                "Inspection site: 789 Elm Street, Somerville, MA."
            ),
            session_id="test_session_create_inspection_job_1",
        )

        print(f"\n[TEST] Creating inspection job with new company")
        print(f"[TEST] Message: {user_request.message}")

        try:
            # Execute orchestrator flow
            state = orchestrator_agent_flow(user_request)

            # ========== Basic State Validation ==========
            self.assertIsNotNone(
                state,
                "orchestrator_agent_flow should return MainFlowState",
            )
            self.assertIsNotNone(
                state.final_response,
                "State should have final_response",
            )

            # ========== Finance Agent Routing Validation ==========
            self._assert_routed_to_finance(
                state,
                msg="Job creation with company should route to finance agent",
            )

            # ========== Response Validation ==========
            final = state.final_response
            assert final is not None  # type: ignore[unreachable]

            # Should have agent_responses (may be empty dict if server not running)
            self.assertIsNotNone(
                final.agent_responses,
                "Should have agent_responses field",
            )

            if final.status == "empty" and final.agent_responses == {}:
                print("[TEST] ⚠ Finance agent server not running (port 8001)")
                print("[TEST] ✓ But routing to finance_agent was CORRECT")
            else:
                print("[TEST] ✓ Inspection job + company creation completed")
                print(f"[TEST] ✓ Final response status: {final.status}")

            self._print_final_summary(final, label="inspection_job_new_company")
            print("[TEST] ✓ Test passed (routing validated)\n")

        except InterruptException as interrupt:
            # HITL interrupt is acceptable
            print("[TEST] ⚠ HITL interrupt triggered (acceptable)")
            print(f"[TEST] Interrupt value: {interrupt.value}")
            self.assertIsNotNone(interrupt.state, "Interrupt should carry state")

    # ---------------------------------------------------------
    # TEST CASE 3: Create job with missing required fields
    # ---------------------------------------------------------

    def test_create_job_with_missing_required_fields(self):
        user_request = UserRequest(
            message="I need to create a job for ABC Company.",
            session_id="test_session_create_job_missing_fields_1",
        )

        print(f"\n[TEST] Creating job with missing required fields")
        print(f"[TEST] Message: {user_request.message}")

        try:
            # Execute orchestrator flow
            state = orchestrator_agent_flow(user_request)

            # ========== Basic State Validation ==========
            self.assertIsNotNone(
                state,
                "orchestrator_agent_flow should return MainFlowState",
            )

            # ========== Finance Agent Routing Validation ==========
            self._assert_routed_to_finance(
                state,
                msg="Job creation with missing fields should still route to finance agent",
            )

            # If no interrupt, check if final_response indicates missing info
            if state.final_response:
                final = state.final_response
                text = (final.test_result or final.message).lower()

                # Lenient semantic assertion: should contain "need more info" type keywords
                # (can be adjusted later based on actual prompt responses)
                self.assertTrue(
                    any(word in text for word in ["missing", "require", "more info", "information"]),
                    "When fields are missing, response should hint that more information is required "
                    f"(got: {final.test_result or final.message})",
                )

                self._print_final_summary(final, label="job_missing_fields")
                print("[TEST] ✓ Job creation handled (may have requested more info)")
                print(f"[TEST] ✓ Final response status: {final.status}")
                print("[TEST] ✓ Test passed\n")

        except InterruptException as interrupt:
            # This is the EXPECTED path for missing fields
            print("[TEST] ✓ HITL interrupt triggered as expected")
            print("[TEST] ✓ Agent requesting missing information")

            self.assertIsNotNone(interrupt.state, "Interrupt should carry state")
            self.assertIsNotNone(
                interrupt.value,
                "Interrupt should have value with clarification questions",
            )

            print("[TEST] ✓ Test passed (HITL triggered correctly)\n")


if __name__ == "__main__":
    unittest.main()
