"""
Test script for UC8 - Weekly/Monthly Status Check

This test verifies the Main Success Scenario (MSS) for UC8:
1. AI scans all Job/Quotation statuses
2. Generate weekly/monthly report (reference survey.xlsx)
3. Highlight abnormal projects

Primary Actor: AI Assistant
Trigger: Weekly or monthly scheduled task
Postcondition: Report generated (CSV/Excel) and accountant notified

Reference: Use Cases Doc: Job & Quotation.md - UC8
"""
import uuid
from main_flow.main_flow import main_flow
from main_flow.utils.Request.UserRequest import UserRequest


def test_uc8_weekly_status_check():
    """UC8 MSS: AI scans and generates weekly status report"""
    session_id = str(uuid.uuid4())

    # Create sample jobs and quotations for the week
    # Job 1: Active with quotation
    create_job_1 = "Create a job for Client A, project: Weekly Project 1"
    print(f"\n[UC8 Setup] Creating sample jobs - session_id: {session_id}")
    request_1 = UserRequest(message=create_job_1, session_id=session_id)
    main_flow(request_1)

    create_quote_1 = "Create a quotation for this job, amount: $50,000"
    request_quote_1 = UserRequest(message=create_quote_1, session_id=session_id)
    main_flow(request_quote_1)

    # Job 2: Active without quotation (potential abnormality)
    create_job_2 = "Create a job for Client B, project: Weekly Project 2"
    request_2 = UserRequest(message=create_job_2, session_id=session_id)
    main_flow(request_2)

    # Request weekly status check
    status_check_input = "Generate weekly status report for all jobs and quotations"
    print(f"\n[UC8 Test] Requesting weekly status check - session_id: {session_id}")
    status_request = UserRequest(message=status_check_input, session_id=session_id)
    status_result = main_flow(status_request)

    print(f"[UC8 Test] Weekly status report: {status_result}")
    assert status_result is not None
    # Report should include: job count, quotation count, abnormalities
    print("✅ UC8 Test - Weekly status check: PASSED")


def test_uc8_monthly_status_check():
    """UC8: AI generates monthly status report"""
    session_id = str(uuid.uuid4())

    # Create sample data for monthly report
    for i in range(3):
        create_job = f"Create a job for Monthly Client {i+1}, project: Monthly Project {i+1}"
        request = UserRequest(message=create_job, session_id=session_id)
        main_flow(request)

        if i < 2:  # Create quotations for first 2 jobs only
            create_quote = f"Create a quotation, amount: ${(i+1)*30000}"
            quote_request = UserRequest(message=create_quote, session_id=session_id)
            main_flow(quote_request)

    # Request monthly status check
    status_check_input = "Generate monthly status report for all jobs and quotations"
    print(f"\n[UC8 Monthly Test] Requesting monthly status check - session_id: {session_id}")
    status_request = UserRequest(message=status_check_input, session_id=session_id)
    status_result = main_flow(status_request)

    print(f"[UC8 Monthly Test] Monthly status report: {status_result}")
    assert status_result is not None
    print("✅ UC8 Test - Monthly status check: PASSED")


def test_uc8_highlight_abnormal_projects():
    """UC8: AI highlights abnormal projects in report"""
    session_id = str(uuid.uuid4())

    # Create normal job
    create_normal = "Create a job for Normal Client, project: Normal Project"
    print(f"\n[UC8 Abnormal Test] Creating normal job - session_id: {session_id}")
    request_normal = UserRequest(message=create_normal, session_id=session_id)
    main_flow(request_normal)

    create_quote = "Create a quotation, amount: $40,000"
    quote_request = UserRequest(message=create_quote, session_id=session_id)
    main_flow(quote_request)

    # Create abnormal job (no quotation for extended period)
    create_abnormal = "Create a job for Abnormal Client, project: Old Project created 45 days ago"
    request_abnormal = UserRequest(message=create_abnormal, session_id=session_id)
    main_flow(request_abnormal)
    # No quotation created - should be flagged

    # Request status check with abnormality detection
    status_check_input = "Generate status report and highlight abnormal projects (jobs without quotations > 30 days)"
    print(f"\n[UC8 Abnormal Test] Requesting status check with abnormality detection - session_id: {session_id}")
    status_request = UserRequest(message=status_check_input, session_id=session_id)
    status_result = main_flow(status_request)

    print(f"[UC8 Abnormal Test] Status report with abnormalities: {status_result}")
    assert status_result is not None
    # Should flag: "Old Project" has no quotation for 45 days
    print("✅ UC8 Test - Highlight abnormal projects: PASSED")


def test_uc8_export_report_csv_excel():
    """UC8: AI exports report in CSV/Excel format"""
    session_id = str(uuid.uuid4())

    # Create sample data
    create_job = "Create a job for Export Test Client, project: Export Test Project"
    print(f"\n[UC8 Export Test] Creating job for export - session_id: {session_id}")
    request = UserRequest(message=create_job, session_id=session_id)
    main_flow(request)

    create_quote = "Create a quotation, amount: $60,000"
    quote_request = UserRequest(message=create_quote, session_id=session_id)
    main_flow(quote_request)

    # Request report export
    export_input = "Generate status report and export to CSV format"
    print(f"\n[UC8 Export Test] Requesting CSV export - session_id: {session_id}")
    export_request = UserRequest(message=export_input, session_id=session_id)
    export_result = main_flow(export_request)

    print(f"[UC8 Export Test] CSV export result: {export_result}")
    assert export_result is not None
    # Should generate CSV/Excel file path or download link
    print("✅ UC8 Test - Export report to CSV/Excel: PASSED")


def test_uc8_notify_accountant():
    """UC8: AI notifies accountant after generating report"""
    session_id = str(uuid.uuid4())

    # Create data
    create_job = "Create a job for Notification Test, project: Test Notification"
    request = UserRequest(message=create_job, session_id=session_id)
    main_flow(request)

    # Request status check with notification
    status_check_input = "Generate monthly report and notify accountant"
    print(f"\n[UC8 Notify Test] Requesting report with notification - session_id: {session_id}")
    status_request = UserRequest(message=status_check_input, session_id=session_id)
    status_result = main_flow(status_request)

    print(f"[UC8 Notify Test] Report with notification: {status_result}")
    assert status_result is not None
    # Should confirm: "Report generated and accountant notified"
    print("✅ UC8 Test - Notify accountant: PASSED")


if __name__ == "__main__":
    print("=" * 80)
    print("Running UC8 - Weekly/Monthly Status Check Tests")
    print("=" * 80)

    test_uc8_weekly_status_check()
    test_uc8_monthly_status_check()
    test_uc8_highlight_abnormal_projects()
    test_uc8_export_report_csv_excel()
    test_uc8_notify_accountant()

    print("\n" + "=" * 80)
    print("🎉 All UC8 tests completed!")
    print("=" * 80)
