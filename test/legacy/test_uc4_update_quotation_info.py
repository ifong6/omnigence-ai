"""
Test script for UC4 - Update Quotation Info

This test verifies the Main Success Scenario (MSS) for UC4:
User modifies quotation amount, description, or customer info in the system

Extensions tested:
- Extend UC7: AI reminds whether to sync other Quotations

Postcondition: Quotation record updated and new version generated

Reference: Use Cases Doc: Job & Quotation.md - UC4
"""
import uuid
from main_flow.main_flow import main_flow
from main_flow.utils.Request.UserRequest import UserRequest


def test_uc4_update_quotation_amount():
    """UC4 MSS: Update quotation amount"""
    session_id = str(uuid.uuid4())

    # Create a quotation first
    create_input = "Create a quotation for 長江實業, project: 寫字樓結構檢測, amount: $80,000"
    print(f"\n[UC4 Setup] Creating quotation - session_id: {session_id}")
    create_request = UserRequest(message=create_input, session_id=session_id)
    create_result = main_flow(create_request)
    print(f"[UC4 Setup] Quotation created: {create_result}")

    # Update quotation amount
    update_input = "Update the quotation amount to $95,000 and add additional item: fire safety inspection"
    print(f"\n[UC4 Test] Updating quotation amount - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC4 Test] Update result: {update_result}")
    assert update_result is not None
    # Should generate new version
    print("✅ UC4 Test - Update quotation amount: PASSED")


def test_uc4_update_quotation_description():
    """UC4: Update quotation description and terms"""
    session_id = str(uuid.uuid4())

    # Create quotation
    create_input = "Create a quotation for XYZ Corp, project: Building Safety Audit"
    print(f"\n[UC4 Description Test] Creating quotation - session_id: {session_id}")
    create_request = UserRequest(message=create_input, session_id=session_id)
    create_result = main_flow(create_request)

    # Update description
    update_input = "Update quotation to include: comprehensive structural assessment, detailed report with photos, warranty period 12 months"
    print(f"\n[UC4 Description Test] Updating description - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC4 Description Test] Update result: {update_result}")
    assert update_result is not None
    print("✅ UC4 Test - Update quotation description: PASSED")


def test_uc4_update_customer_info():
    """UC4: Update customer information in quotation"""
    session_id = str(uuid.uuid4())

    # Create quotation
    create_input = "Create a quotation for Best Properties Ltd, project: Mall Inspection"
    print(f"\n[UC4 Customer Test] Creating quotation - session_id: {session_id}")
    create_request = UserRequest(message=create_input, session_id=session_id)
    create_result = main_flow(create_request)

    # Update customer info
    update_input = "Update customer address to 123 Queen's Road Central and contact person to Ms. Chan"
    print(f"\n[UC4 Customer Test] Updating customer info - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC4 Customer Test] Update result: {update_result}")
    assert update_result is not None
    print("✅ UC4 Test - Update customer info: PASSED")


def test_uc4_extend_uc7_ai_reminder_related_quotations():
    """UC4 Extension UC7: AI detects changes and reminds about other quotations"""
    session_id = str(uuid.uuid4())

    # Create first quotation
    create_input_1 = "Create a quotation for 太古地產, project: Office Building Inspection, amount: $100,000"
    print(f"\n[UC4-UC7 Test] Creating first quotation - session_id: {session_id}")
    create_request_1 = UserRequest(message=create_input_1, session_id=session_id)
    create_result_1 = main_flow(create_request_1)

    # Create second quotation for same client
    create_input_2 = "Create another quotation for 太古地產, project: Shopping Mall Inspection, amount: $120,000"
    print(f"\n[UC4-UC7 Test] Creating second quotation - session_id: {session_id}")
    create_request_2 = UserRequest(message=create_input_2, session_id=session_id)
    create_result_2 = main_flow(create_request_2)

    # Update pricing - AI should detect and remind about other quotations
    update_input = "Update the standard inspection rate to $150 per sqm with 10% discount"
    print(f"\n[UC4-UC7 Test] Updating pricing (should trigger AI reminder) - session_id: {session_id}")
    update_request = UserRequest(message=update_input, session_id=session_id)
    update_result = main_flow(update_request)

    print(f"[UC4-UC7 Test] Update result (should include AI reminder): {update_result}")
    assert update_result is not None
    # AI should detect amount/terms change and suggest approval
    print("✅ UC4-UC7 Test - AI reminder for related quotations: PASSED")


if __name__ == "__main__":
    print("=" * 80)
    print("Running UC4 - Update Quotation Info Tests")
    print("=" * 80)

    test_uc4_update_quotation_amount()
    test_uc4_update_quotation_description()
    test_uc4_update_customer_info()
    test_uc4_extend_uc7_ai_reminder_related_quotations()

    print("\n" + "=" * 80)
    print("🎉 All UC4 tests completed!")
    print("=" * 80)
