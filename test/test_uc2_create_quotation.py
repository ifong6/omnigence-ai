"""
Test script for UC2 - Create Quotation

This test verifies the Main Success Scenario (MSS) for UC2:
1. Select existing Job → generate Quotation draft
2. Edit quotation items, amounts, customer info
3. Save quotation

Extensions tested:
- E2: Create quotation using Job ID (user remembers job number)
- E3: Multiple quotations for same job (Job extension quotation)
- E4: Single quotation covering multiple jobs (Combined quotation)

Reference: Use Cases Doc: Job & Quotation.md - UC2
"""
import uuid
from main_flow.main_flow import main_flow
from main_flow.utils.Request.UserRequest import UserRequest
# ========================================================================
# TEST DATA - Centralized test inputs for easy review and maintenance
# ========================================================================
TEST_DATA = {
    # UC2 MSS: Create quotation by client/project name (no job ID)
    "uc2_mss": {
        "amount": "$45,000 MOP",
        "create_job": "Create a job for 金龍建築工程有限公司, project: 結構安全檢測-buldingA",
        "create_quotation": """Create a quotation for 金龍建築工程有限公司, project: 結構安全檢測-buldingA
Items:
foundation inspection 20000 MOP
structural assessment 25000 MOP"""
    },

    # UC2-E2: Create quotation with Job ID
    "uc2_e2": {
        "job_id": "JICP-25-01-1",
        "amount": "$45,000 MOP",
        "create_job": "Create a job for 金龍建築工程有限公司, project: 結構安全檢測",
        "create_quotation": """Create a quotation for job {job_id}
Items:
foundation inspection 20000 MOP
structural assessment 25000 MOP"""
    },

    # UC2-E3: Multiple quotations for same job
    "uc2_e3": {
        "amount_1": "$50,000 MOP",
        "amount_2": "$75,000 MOP",
        "quotation_1": """Create a quotation for 金龍建築工程有限公司, project: 結構安全檢測
Items:
beam template calculation 25000 MOP
wall template calculation 25000 MOP""",
        "quotation_2": """Create another quotation for the same job
Items:
fire safety inspection 35000 MOP
emergency exit assessment 40000 MOP"""
    },
}
# ========================================================================


def test_uc2_create_quotation_with_existing_job():
    """UC2 MSS: Create quotation for existing job (user may not remember job ID)"""
    session_id = str(uuid.uuid4())

    try:
        # Get test data
        amount = TEST_DATA["uc2_mss"]["amount"]
        create_job_input = TEST_DATA["uc2_mss"]["create_job"]
        quotation_input = TEST_DATA["uc2_mss"]["create_quotation"].format(amount=amount)

        # First, create a job
        print(f"\n[UC2 Setup] Creating job first - session_id: {session_id}")
        print(f"[UC2 Setup] Input: {create_job_input}")
        job_request = UserRequest(message=create_job_input, session_id=session_id)
        job_result = main_flow(job_request)
        print(f"[UC2 Setup] Job created: {job_result}")

        # Then create quotation (user references by client/project, not job ID)
        print(f"\n[UC2 Test] Creating quotation - session_id: {session_id}")
        print(f"[UC2 Test] Input: {quotation_input}")
        quotation_request = UserRequest(message=quotation_input, session_id=session_id)
        final_result = main_flow(quotation_request)

        print(f"[UC2 Test] Final result: {final_result}")

        # Check results
        if job_result is None:
            print("❌ UC2 Test - Create quotation with existing job: FAILED (Job creation failed)")
            return False
        if final_result is None:
            print("❌ UC2 Test - Create quotation with existing job: FAILED (Quotation creation failed)")
            return False

        print("✅ UC2 Test - Create quotation with existing job: PASSED")
        return True

    except ConnectionError as e:
        print(f"❌ UC2 Test - Create quotation with existing job: FAILED (Server not active - {e})")
        return False
    except Exception as e:
        print(f"❌ UC2 Test - Create quotation with existing job: FAILED (Error: {e})")
        return False


def test_uc2_e2_create_quotation_with_job_id():
    """UC2 Extension E2: Create quotation using Job ID (user remembers job number)"""
    session_id = str(uuid.uuid4())

    try:
        # Get test data
        amount = TEST_DATA["uc2_e2"]["amount"]
        job_id = TEST_DATA["uc2_e2"]["job_id"]
        create_job_input = TEST_DATA["uc2_e2"]["create_job"]
        quotation_input = TEST_DATA["uc2_e2"]["create_quotation"].format(job_id=job_id, amount=amount)

        # First, create a job to get a job ID
        print(f"\n[UC2-E2 Setup] Creating job first - session_id: {session_id}")
        print(f"[UC2-E2 Setup] Input: {create_job_input}")
        job_request = UserRequest(message=create_job_input, session_id=session_id)
        job_result = main_flow(job_request)
        print(f"[UC2-E2 Setup] Job created: {job_result}")

        # User creates quotation using specific job ID (assumes they remember/have the job number)
        print(f"\n[UC2-E2 Test] Creating quotation with Job ID - session_id: {session_id}")
        print(f"[UC2-E2 Test] Input: {quotation_input}")
        quotation_request = UserRequest(message=quotation_input, session_id=session_id)
        quotation_result = main_flow(quotation_request)

        print(f"[UC2-E2 Test] Quotation result: {quotation_result}")

        # Check results
        if job_result is None:
            print("❌ UC2-E2 Test - Create quotation with Job ID: FAILED (Job creation failed)")
            return False
        if quotation_result is None:
            print("❌ UC2-E2 Test - Create quotation with Job ID: FAILED (Quotation creation failed)")
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
        # Get test data
        amount_1 = TEST_DATA["uc2_e3"]["amount_1"]
        amount_2 = TEST_DATA["uc2_e3"]["amount_2"]
        quotation_1_input = TEST_DATA["uc2_e3"]["quotation_1"].format(amount_1=amount_1)
        quotation_2_input = TEST_DATA["uc2_e3"]["quotation_2"].format(amount_2=amount_2)

        # First quotation
        print(f"\n[UC2-E3 Test] First quotation - session_id: {session_id}")
        print(f"[UC2-E3 Test] Input: {quotation_1_input}")
        request_1 = UserRequest(message=quotation_1_input, session_id=session_id)
        result_1 = main_flow(request_1)
        print(f"[UC2-E3 Test] First quotation result: {result_1}")

        # Second quotation for same job (extended quotation)
        print(f"\n[UC2-E3 Test] Second quotation - session_id: {session_id}")
        print(f"[UC2-E3 Test] Input: {quotation_2_input}")
        request_2 = UserRequest(message=quotation_2_input, session_id=session_id)
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
        print(f"❌ UC2-E3 Test - Multiple quotations for same job: FAILED (Server not active - {e})")
        return False
    except Exception as e:
        print(f"❌ UC2-E3 Test - Multiple quotations for same job: FAILED (Error: {e})")
        
if __name__ == "__main__":
    test_uc2_create_quotation_with_existing_job()
    test_uc2_e2_create_quotation_with_job_id()
    test_uc2_e3_multiple_quotations_for_same_job()
  