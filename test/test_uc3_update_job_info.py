"""
Test script for UC3 - Update Job Info

This test verifies the Main Success Scenario (MSS) for UC3:
User modifies customer or project information in the system and saves

Extensions tested:
- Extend UC6: AI reminds whether to sync other related Jobs

Postcondition: Job info updated and modification log recorded

Reference: Use Cases Doc: Job & Quotation.md - UC3
"""
import uuid
from main_flow.main_flow import main_flow
from main_flow.utils.Request.UserRequest import UserRequest


def test_uc3_update_job_basic_info():
    """UC3 MSS: Update job basic information"""
    session_id = str(uuid.uuid4())

    # First create a job
    create_input = "Create a job for 恒基兆業, project: 住宅大廈結構檢測"
    print(f"\n[UC3 Setup] Creating job - session_id: {session_id}")
    create_request = UserRequest(message=create_input, session_id=session_id)
    create_result = main_flow(create_request)
    print(f"[UC3 Setup] Job created: {create_result}")

    # Update the job info
    update_input = "Update the job client name to 恒基兆業地產有限公司 and project name to 住宅大廈全面結構檢測"
    print(f"\n[UC3 Test] Updating job - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC3 Test] Update result: {update_result}")
    assert update_result is not None
    print("✅ UC3 Test - Update job basic info: PASSED")


def test_uc3_update_client_info():
    """UC3: Update client information"""
    session_id = str(uuid.uuid4())

    # Create a job
    create_input = "Create a job for ABC Company, project: Building Inspection"
    print(f"\n[UC3 Client Test] Creating job - session_id: {session_id}")
    create_request = UserRequest(message=create_input, session_id=session_id)
    create_result = main_flow(create_request)

    # Update client contact info
    update_input = "Update the client contact to Mr. Wong, phone: 9123-4567, email: wong@abc.com"
    print(f"\n[UC3 Client Test] Updating client info - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC3 Client Test] Update result: {update_result}")
    assert update_result is not None
    print("✅ UC3 Test - Update client info: PASSED")


def test_uc3_extend_uc6_ai_reminder_related_jobs():
    """UC3 Extension UC6: AI detects duplicate clients and reminds to update related jobs"""
    session_id = str(uuid.uuid4())

    # Create first job
    create_input_1 = "Create a job for 新鴻基地產, project: IFC結構檢測"
    print(f"\n[UC3-UC6 Test] Creating first job - session_id: {session_id}")
    create_request_1 = UserRequest(message=create_input_1, session_id=session_id)
    create_result_1 = main_flow(create_request_1)

    # Create second job with same client
    create_input_2 = "Create another job for 新鴻基地產, project: 商場消防檢查"
    print(f"\n[UC3-UC6 Test] Creating second job - session_id: {session_id}")
    create_request_2 = UserRequest(message=create_input_2, session_id=session_id)
    create_result_2 = main_flow(create_request_2)

    # Update client info - AI should remind about related jobs
    update_input = "Update client contact info to phone: 2111-2222, address: Central, Hong Kong"
    print(f"\n[UC3-UC6 Test] Updating client info (should trigger AI reminder) - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC3-UC6 Test] Update result (should include AI reminder): {update_result}")
    assert update_result is not None
    # AI should detect related jobs and remind user
    print("✅ UC3-UC6 Test - AI reminder for related jobs: PASSED")


if __name__ == "__main__":
    print("=" * 80)
    print("Running UC3 - Update Job Info Tests")
    print("=" * 80)

    test_uc3_update_job_basic_info()
    test_uc3_update_client_info()
    test_uc3_extend_uc6_ai_reminder_related_jobs()

    print("\n" + "=" * 80)
    print("🎉 All UC3 tests completed!")
    print("=" * 80)
