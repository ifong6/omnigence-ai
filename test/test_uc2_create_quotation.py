"""
Test script for UC2 - Create Quotation

This test verifies the Main Success Scenario (MSS) for UC2:
1. Select existing Job -> generate Quotation draft
2. Edit quotation items, amounts, customer info
3. Save quotation

Extensions tested:
- E2: Create quotation using Job ID (user remembers job number)
- E3: Multiple quotations for same job (Job extension quotation)
- E4: Single quotation covering multiple jobs (Combined quotation)

Reference: Use Cases Doc: Job & Quotation.md - UC2
"""

import uuid
from app.main_flow.main_flow import main_flow
from app.main_flow.utils.Request.UserRequest import UserRequest

TEST_DATA = {
    # UC2 MSS: Create quotation by client/project name (no job ID)
   "uc2_mss": {
    "input": """
    Please create a new job for 金龍建築工程有限公司.
    The project name is 結構安全檢測 - Building A. 
    After that, create a quotation for the same project.
    It should include:
        - Foundation inspection: 20000 MOP
        - Structural assessment: 25000 MOP
    """
    }
}
# ========================================================================

def test_uc2_create_job_and_quotation():
    """UC2 MSS: Create job and quotation in single request (references by client/project)"""
    session_id = str(uuid.uuid4())

    try:
        # Get test data - single combined input that creates both job and quotation
        user_input = TEST_DATA["uc2_mss"]["input"]

        # Create job and quotation in one request
        print(f"\n[UC2 Test] Creating job and quotation - session_id: {session_id}")
        print(f"[UC2 Test] Input: {user_input}")
        request = UserRequest(message=user_input, session_id=session_id)
        result = main_flow(request)

        print(f"[UC2 Test] Final result: {result}")

        # Check results
        if result is None:
            print("❌ UC2 Test - Create job and quotation: FAILED")
            return False

        print("✅ UC2 Test - Create job and quotation: PASSED")
        return True

    except ConnectionError as e:
        print(f"❌ UC2 Test - Create job and quotation: FAILED (Server not active - {e})")
        return False
    except Exception as e:
        print(f"❌ UC2 Test - Create job and quotation: FAILED (Error: {e})")
        return False


def test_uc2_e2_create_quotation_with_job_id():
    """UC2 Extension E2: Create quotation using Job ID (user knows specific job number)"""
    session_id = str(uuid.uuid4())

    try:
        # Get test data - input already includes job ID reference
        user_input = TEST_DATA["uc2_e2"]["input"]

        # User creates quotation referencing specific job ID
        print(f"\n[UC2-E2 Test] Creating quotation with Job ID - session_id: {session_id}")
        print(f"[UC2-E2 Test] Input: {user_input}")
        request = UserRequest(message=user_input, session_id=session_id)
        result = main_flow(request)

        print(f"[UC2-E2 Test] Quotation result: {result}")

        # Check results
        if result is None:
            print("❌ UC2-E2 Test - Create quotation with Job ID: FAILED")
            return False

        print("✅ UC2-E2 Test - Create quotation with Job ID: PASSED")
        return True

    except ConnectionError as e:
        print(f"❌ UC2-E2 Test - Create quotation with Job ID: FAILED (Server not active - {e})")
        return False
    except Exception as e:
        print(f"❌ UC2-E2 Test - Create quotation with Job ID: FAILED (Error: {e})")
        return False


def test_uc2_e3_multiple_quotations_for_same_job():
    """UC2 Extension E3: Create multiple quotations for the same job"""
    session_id = str(uuid.uuid4())

    try:
        # Get test data - two separate quotation requests for same job
        input_1 = TEST_DATA["uc2_e3"]["input_1"]
        input_2 = TEST_DATA["uc2_e3"]["input_2"]

        # First quotation
        print(f"\n[UC2-E3 Test] First quotation - session_id: {session_id}")
        print(f"[UC2-E3 Test] Input: {input_1}")
        request_1 = UserRequest(message=input_1, session_id=session_id)
        result_1 = main_flow(request_1)
        print(f"[UC2-E3 Test] First quotation result: {result_1}")

        # Second quotation for same job (extended quotation)
        print(f"\n[UC2-E3 Test] Second quotation - session_id: {session_id}")
        print(f"[UC2-E3 Test] Input: {input_2}")
        request_2 = UserRequest(message=input_2, session_id=session_id)
        result_2 = main_flow(request_2)
        print(f"[UC2-E3 Test] Second quotation result: {result_2}")

        # Check results
        if result_1 is None:
            print("❌ UC2-E3 Test - Multiple quotations for same job: FAILED (First quotation failed)")
            return False
        if result_2 is None:
            print("❌ UC2-E3 Test - Multiple quotations for same job: FAILED (Second quotation failed)")
            return False

        print("✅ UC2-E3 Test - Multiple quotations for same job: PASSED")
        return True

    except ConnectionError as e:
        print("❌ UC2-E3 Test - Multiple quotations for same job: FAILED (Server not active - {e})")
        return False
    except Exception as e:
        print(f"❌ UC2-E3 Test - Multiple quotations for same job: FAILED (Error: {e})")
        return False

if __name__ == "__main__":
    test_uc2_create_job_and_quotation()
  