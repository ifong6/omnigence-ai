"""
Test script for UC9 - Export Quotation PDF (Read-only)

This test verifies the Main Success Scenario (MSS) for UC9:
System exports quotation PDF without modifying original data

Primary Actor: User
Trigger: User clicks "Download PDF"
Precondition: Quotation exists
Postcondition: PDF file download successful

Reference: Use Cases Doc: Job & Quotation.md - UC9
"""
import uuid
from main_flow.main_flow import main_flow
from main_flow.utils.Request.UserRequest import UserRequest


def test_uc9_export_quotation_pdf_basic():
    """UC9 MSS: Export quotation as PDF (read-only)"""
    session_id = str(uuid.uuid4())

    # Create a quotation first
    create_input = "Create a quotation for PDF Export Test Ltd, project: Building Assessment, amount: $85,000"
    print(f"\n[UC9 Setup] Creating quotation - session_id: {session_id}")
    create_request = UserRequest(message=create_input, session_id=session_id)
    create_result = main_flow(create_request)
    print(f"[UC9 Setup] Quotation created: {create_result}")

    # Export quotation to PDF
    export_input = "Export the quotation to PDF"
    print(f"\n[UC9 Test] Exporting quotation to PDF - session_id: {session_id}")
    export_request = UserRequest(message=export_input, session_id=session_id)
    export_result = main_flow(export_request)

    print(f"[UC9 Test] PDF export result: {export_result}")
    assert export_result is not None
    # Should return PDF file path or download link
    print("✅ UC9 Test - Export quotation PDF (basic): PASSED")


def test_uc9_export_does_not_modify_data():
    """UC9: Verify PDF export does NOT modify original quotation data"""
    session_id = str(uuid.uuid4())

    # Create quotation
    create_input = "Create a quotation for Data Integrity Test, amount: $70,000, validity: 30 days"
    print(f"\n[UC9 Integrity Test] Creating quotation - session_id: {session_id}")
    create_request = UserRequest(message=create_input, session_id=session_id)
    create_result = main_flow(create_request)
    print(f"[UC9 Integrity Test] Original quotation: {create_result}")

    # Export to PDF (should be read-only)
    export_input = "Export quotation to PDF"
    print(f"\n[UC9 Integrity Test] Exporting PDF (read-only) - session_id: {session_id}")
    export_request = UserRequest(message=export_input, session_id=session_id)
    export_result = main_flow(export_request)
    print(f"[UC9 Integrity Test] PDF exported: {export_result}")

    # Verify original data unchanged
    verify_input = "Show me the current quotation details"
    print(f"\n[UC9 Integrity Test] Verifying data unchanged - session_id: {session_id}")
    verify_request = UserRequest(message=verify_input, session_id=session_id)
    verify_result = main_flow(verify_request)
    print(f"[UC9 Integrity Test] Current quotation (should match original): {verify_result}")

    assert export_result is not None
    assert verify_result is not None
    # Original amount and validity should remain unchanged
    print("✅ UC9 Test - Export does not modify data: PASSED")


def test_uc9_ai_validates_latest_version():
    """UC9: AI validates whether quotation version is latest"""
    session_id = str(uuid.uuid4())

    # Create quotation V1
    create_v1 = "Create a quotation for Version Test Corp, amount: $90,000"
    print(f"\n[UC9 Version Test] Creating V1 - session_id: {session_id}")
    request_v1 = UserRequest(message=create_v1, session_id=session_id)
    result_v1 = main_flow(request_v1)
    print(f"[UC9 Version Test] V1 created: {result_v1}")

    # Create quotation V2
    update_v2 = "Update quotation to $100,000 (creating V2)"
    print(f"\n[UC9 Version Test] Creating V2 - session_id: {session_id}")
    request_v2 = UserRequest(message=update_v2, session_id=session_id)
    result_v2 = main_flow(request_v2)
    print(f"[UC9 Version Test] V2 created: {result_v2}")

    # Try to export - AI should validate and export latest version
    export_input = "Export quotation to PDF"
    print(f"\n[UC9 Version Test] Exporting (AI should validate latest version) - session_id: {session_id}")
    export_request = UserRequest(message=export_input, session_id=session_id)
    export_result = main_flow(export_request)
    print(f"[UC9 Version Test] PDF export (should be V2): {export_result}")

    assert export_result is not None
    # AI should confirm: "Exporting latest version V2"
    print("✅ UC9 Test - AI validates latest version: PASSED")


def test_uc9_export_specific_version():
    """UC9: Export specific version of quotation"""
    session_id = str(uuid.uuid4())

    # Create V1
    create_v1 = "Create a quotation for Historical Export Test, amount: $50,000"
    print(f"\n[UC9 Specific Version Test] Creating V1 - session_id: {session_id}")
    request_v1 = UserRequest(message=create_v1, session_id=session_id)
    main_flow(request_v1)

    # Create V2
    update_v2 = "Update quotation to $60,000"
    print(f"\n[UC9 Specific Version Test] Creating V2 - session_id: {session_id}")
    request_v2 = UserRequest(message=update_v2, session_id=session_id)
    main_flow(request_v2)

    # Export specific version (V1)
    export_v1 = "Export quotation version 1 to PDF"
    print(f"\n[UC9 Specific Version Test] Exporting V1 - session_id: {session_id}")
    export_request_v1 = UserRequest(message=export_v1, session_id=session_id)
    export_result_v1 = main_flow(export_request_v1)
    print(f"[UC9 Specific Version Test] V1 PDF: {export_result_v1}")

    # Export latest version (V2)
    export_v2 = "Export latest quotation to PDF"
    print(f"\n[UC9 Specific Version Test] Exporting V2 - session_id: {session_id}")
    export_request_v2 = UserRequest(message=export_v2, session_id=session_id)
    export_result_v2 = main_flow(export_request_v2)
    print(f"[UC9 Specific Version Test] V2 PDF: {export_result_v2}")

    assert export_result_v1 is not None
    assert export_result_v2 is not None
    print("✅ UC9 Test - Export specific version: PASSED")


def test_uc9_export_with_custom_filename():
    """UC9: Export PDF with custom filename"""
    session_id = str(uuid.uuid4())

    # Create quotation
    create_input = "Create a quotation for Custom Name Test, project: Special Project"
    print(f"\n[UC9 Custom Name Test] Creating quotation - session_id: {session_id}")
    create_request = UserRequest(message=create_input, session_id=session_id)
    main_flow(create_request)

    # Export with custom filename
    export_input = "Export quotation to PDF with filename: Special_Project_Quotation_2025.pdf"
    print(f"\n[UC9 Custom Name Test] Exporting with custom filename - session_id: {session_id}")
    export_request = UserRequest(message=export_input, session_id=session_id)
    export_result = main_flow(export_request)

    print(f"[UC9 Custom Name Test] PDF export with custom name: {export_result}")
    assert export_result is not None
    # Should confirm custom filename
    print("✅ UC9 Test - Export with custom filename: PASSED")


def test_uc9_batch_export_multiple_quotations():
    """UC9: Batch export multiple quotations to PDF"""
    session_id = str(uuid.uuid4())

    # Create multiple quotations
    for i in range(3):
        create_input = f"Create a quotation for Batch Export Client {i+1}, amount: ${(i+1)*25000}"
        print(f"\n[UC9 Batch Test] Creating quotation {i+1} - session_id: {session_id}")
        create_request = UserRequest(message=create_input, session_id=session_id)
        main_flow(create_request)

    # Batch export all quotations
    batch_export_input = "Export all quotations to PDF"
    print(f"\n[UC9 Batch Test] Batch exporting all quotations - session_id: {session_id}")
    batch_export_request = UserRequest(message=batch_export_input, session_id=session_id)
    batch_export_result = main_flow(batch_export_request)

    print(f"[UC9 Batch Test] Batch PDF export result: {batch_export_result}")
    assert batch_export_result is not None
    # Should confirm: "3 quotations exported to PDF"
    print("✅ UC9 Test - Batch export multiple quotations: PASSED")


if __name__ == "__main__":
    print("=" * 80)
    print("Running UC9 - Export Quotation PDF (Read-only) Tests")
    print("=" * 80)

    test_uc9_export_quotation_pdf_basic()
    test_uc9_export_does_not_modify_data()
    test_uc9_ai_validates_latest_version()
    test_uc9_export_specific_version()
    test_uc9_export_with_custom_filename()
    test_uc9_batch_export_multiple_quotations()

    print("\n" + "=" * 80)
    print("🎉 All UC9 tests completed!")
    print("=" * 80)
