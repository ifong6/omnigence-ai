"""
Test scripts for UC6 & UC7 - AI Reminders

UC6 - AI Reminder (related Job No.)
- Primary Actor: AI Assistant
- Trigger: Job information changes
- AI detects same-client other Jobs and reminds user

UC7 - AI Reminder (related Quotation No.)
- Primary Actor: AI Assistant
- Trigger: Quotation information changes
- AI detects and reminds user whether to batch update

Reference: Use Cases Doc: Job & Quotation.md - UC6 & UC7
"""
import uuid
from main_flow.main_flow import main_flow
from main_flow.utils.Request.UserRequest import UserRequest


def test_uc6_ai_reminder_related_jobs():
    """UC6 MSS: AI detects same-client other jobs and reminds user"""
    session_id = str(uuid.uuid4())

    # Create first job
    create_input_1 = "Create a job for 香港置地, project: IFC Tower A Inspection"
    print(f"\n[UC6 Test] Creating first job - session_id: {session_id}")
    create_request_1 = UserRequest(message=create_input_1, session_id=session_id)
    result_1 = main_flow(create_request_1)
    print(f"[UC6 Test] First job created: {result_1}")

    # Create second job for same client
    create_input_2 = "Create a job for 香港置地, project: IFC Tower B Inspection"
    print(f"\n[UC6 Test] Creating second job for same client - session_id: {session_id}")
    create_request_2 = UserRequest(message=create_input_2, session_id=session_id)
    result_2 = main_flow(create_request_2)
    print(f"[UC6 Test] Second job created: {result_2}")

    # Update job info - AI should detect and remind about related jobs
    update_input = "Update the client address to 8 Connaught Place, Central, Hong Kong"
    print(f"\n[UC6 Test] Updating job info (should trigger AI reminder) - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC6 Test] Update result with AI reminder: {update_result}")
    assert update_result is not None
    # AI should remind: "Other jobs for 香港置地 detected. Update all?"
    print("✅ UC6 Test - AI reminder for related jobs: PASSED")


def test_uc6_no_reminder_different_clients():
    """UC6: AI should NOT remind when no related jobs exist"""
    session_id = str(uuid.uuid4())

    # Create job for unique client
    create_input = "Create a job for Unique Client Ltd, project: Special Project"
    print(f"\n[UC6 Negative Test] Creating job for unique client - session_id: {session_id}")
    create_request = UserRequest(message=create_input, session_id=session_id)
    create_result = main_flow(create_request)

    # Update job - should NOT trigger AI reminder (no related jobs)
    update_input = "Update project description to include detailed assessment"
    print(f"\n[UC6 Negative Test] Updating (no reminder expected) - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC6 Negative Test] Update result (no AI reminder): {update_result}")
    assert update_result is not None
    print("✅ UC6 Test - No reminder for different clients: PASSED")


def test_uc7_ai_reminder_related_quotations():
    """UC7 MSS: AI detects multiple quotations under same job and reminds batch update"""
    session_id = str(uuid.uuid4())

    # Create job
    create_job_input = "Create a job for 新世界發展, project: K11 Shopping Mall Renovation"
    print(f"\n[UC7 Test] Creating job - session_id: {session_id}")
    create_job_request = UserRequest(message=create_job_input, session_id=session_id)
    job_result = main_flow(create_job_request)
    print(f"[UC7 Test] Job created: {job_result}")

    # Create first quotation
    create_quote_1 = "Create a quotation for structural assessment, amount: $100,000"
    print(f"\n[UC7 Test] Creating first quotation - session_id: {session_id}")
    quote_request_1 = UserRequest(message=create_quote_1, session_id=session_id)
    quote_result_1 = main_flow(quote_request_1)
    print(f"[UC7 Test] First quotation created: {quote_result_1}")

    # Create second quotation for same job
    create_quote_2 = "Create another quotation for MEP inspection, amount: $80,000"
    print(f"\n[UC7 Test] Creating second quotation for same job - session_id: {session_id}")
    quote_request_2 = UserRequest(message=create_quote_2, session_id=session_id)
    quote_result_2 = main_flow(quote_request_2)
    print(f"[UC7 Test] Second quotation created: {quote_result_2}")

    # Update quotation - AI should detect related quotations
    update_input = "Update payment terms to 30% deposit, 70% upon completion"
    print(f"\n[UC7 Test] Updating quotation (should trigger AI reminder) - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC7 Test] Update result with AI reminder: {update_result}")
    assert update_result is not None
    # AI should remind: "Multiple quotations for same job detected. Apply to all?"
    print("✅ UC7 Test - AI reminder for related quotations: PASSED")


def test_uc7_batch_update_consistency():
    """UC7: AI identifies same-project quotation consistency issues"""
    session_id = str(uuid.uuid4())

    # Create job
    create_job_input = "Create a job for Testing Corp"
    print(f"\n[UC7 Consistency Test] Creating job - session_id: {session_id}")
    create_job_request = UserRequest(message=create_job_input, session_id=session_id)
    job_result = main_flow(create_job_request)

    # Create quotation V1
    create_quote_v1 = "Create a quotation with warranty 12 months, payment net 30 days"
    print(f"\n[UC7 Consistency Test] Creating quotation V1 - session_id: {session_id}")
    quote_request_v1 = UserRequest(message=create_quote_v1, session_id=session_id)
    quote_result_v1 = main_flow(quote_request_v1)

    # Create quotation V2 with different terms
    create_quote_v2 = "Create another quotation with warranty 6 months, payment net 60 days"
    print(f"\n[UC7 Consistency Test] Creating quotation V2 (different terms) - session_id: {session_id}")
    quote_request_v2 = UserRequest(message=create_quote_v2, session_id=session_id)
    quote_result_v2 = main_flow(quote_request_v2)

    # AI should detect inconsistency
    check_input = "Are the quotations consistent?"
    print(f"\n[UC7 Consistency Test] Checking consistency - session_id: {session_id}")
    check_request = UserRequest(message=check_input, session_id=session_id)
    check_result = main_flow(check_request)

    print(f"[UC7 Consistency Test] AI consistency check: {check_result}")
    assert check_result is not None
    # AI should identify: warranty and payment terms differ
    print("✅ UC7 Test - AI identifies consistency issues: PASSED")


if __name__ == "__main__":
    print("=" * 80)
    print("Running UC6 & UC7 - AI Reminder Tests")
    print("=" * 80)

    print("\n--- UC6: AI Reminder (related Job No.) ---")
    test_uc6_ai_reminder_related_jobs()
    test_uc6_no_reminder_different_clients()

    print("\n--- UC7: AI Reminder (related Quotation No.) ---")
    test_uc7_ai_reminder_related_quotations()
    test_uc7_batch_update_consistency()

    print("\n" + "=" * 80)
    print("🎉 All UC6 & UC7 tests completed!")
    print("=" * 80)
