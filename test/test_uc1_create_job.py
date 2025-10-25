"""
Test script for UC1 - Create Job

This test verifies the Main Success Scenario (MSS) for UC1:
1. User inputs project information (client, project name)
2. System generates unique Job No.
3. Save Job record

Reference: Use Cases Doc: Job & Quotation.md - UC1
"""
import uuid
from main_flow.main_flow import main_flow
from main_flow.utils.Request.UserRequest import UserRequest

def test_uc1_create_job():
    # UC1 Input: Client name and project name
    user_input = "Create a new job for 金龍建築工程有限公司, project: 結構安全檢測"
    session_id = str(uuid.uuid4())
    print(f"Generated session_id: {session_id}")

    # Create UserRequest object
    request = UserRequest(message=user_input, session_id=session_id)
    final_result = main_flow(request)

    print(f"Final result: {final_result}")

if __name__ == "__main__":
    test_uc1_create_job()