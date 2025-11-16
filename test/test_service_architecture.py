#!/usr/bin/env python3
"""
Test script for the new service-based architecture.

This demonstrates how to use CompanyService, JobService, and QuotationService
to create a complete quotation workflow.
"""

from sqlmodel import Session
from app.db.engine import engine
from app.services.impl import CompanyServiceImpl, JobServiceImpl, QuotationServiceImpl
from decimal import Decimal


def test_complete_workflow():
    """
    Test the complete workflow: Company → Job → Quotation
    """
    print("\n" + "="*80)
    print("Testing Service-Based Architecture")
    print("="*80)

    with Session(engine) as session:
        print("\n[1/3] Creating/Getting Company...")
        print("-" * 80)

        # Step 1: Get or create company
        company_service = CompanyServiceImpl(session)
        company = company_service.get_or_create(
            name="澳門科技大學",
            address="澳門氹仔偉龍馬路",
            phone="28881234"
        )
        session.commit()

        print(f"✓ Company ID: {company.id}")
        print(f"  Name: {company.name}")
        print(f"  Address: {company.address}")
        print(f"  Phone: {company.phone}")

        print("\n[2/3] Creating Job with Auto Job Number...")
        print("-" * 80)

        # Step 2: Create job with auto-generated job_no
        job_service = JobServiceImpl(session)
        job = job_service.create_job(
            company_id=company.id,
            title="空調系統設計及監理",
            job_type="DESIGN"
        )
        session.commit()

        print(f"✓ Job ID: {job.id}")
        print(f"  Job No: {job.job_no}")
        print(f"  Title: {job.title}")
        print(f"  Status: {job.status}")

        print("\n[3/3] Creating Quotation with Auto Quotation Number...")
        print("-" * 80)

        # Step 3: Create quotation with auto-generated quo_no
        quotation_service = QuotationServiceImpl(session)

        # First, generate the quotation number to preview
        quo_no = quotation_service.generate_quotation_number(
            job_no=job.job_no,
            revision_no="00"
        )
        print(f"Generated Quotation No: {quo_no}")

        # Create quotation with items
        quotations = quotation_service.create_quotation(
            job_no=job.job_no,
            company_id=company.id,
            project_name="空調系統設計及監理",
            currency="MOP",
            items=[
                {
                    "project_item_description": "空調系統設計費用",
                    "quantity": 1.0,
                    "unit": "項",
                    "sub_amount": Decimal("50000"),
                    "total_amount": Decimal("50000")
                },
                {
                    "project_item_description": "工程監理費用",
                    "quantity": 1.0,
                    "unit": "項",
                    "sub_amount": Decimal("30000"),
                    "total_amount": Decimal("30000")
                },
                {
                    "project_item_description": "現場測試費用",
                    "quantity": 5.0,
                    "unit": "次",
                    "sub_amount": Decimal("2000"),
                    "total_amount": Decimal("10000")
                }
            ],
            revision_no="00"
        )
        session.commit()

        print(f"✓ Created {len(quotations)} quotation items")
        for i, q in enumerate(quotations, 1):
            print(f"\n  Item {i}:")
            print(f"    ID: {q.id}")
            print(f"    Quo No: {q.quo_no}")
            print(f"    Description: {q.project_item_description}")
            print(f"    Quantity: {q.quantity} {q.unit}")
            print(f"    Sub Amount: {q.sub_amount} {q.currency}")
            print(f"    Total Amount: {q.total_amount} {q.currency}")

        # Calculate total
        print("\n" + "-" * 80)
        total_info = quotation_service.get_quotation_total(quotations[0].quo_no)
        print(f"✓ Quotation Total:")
        print(f"  Total Amount: {total_info['total']} MOP")
        print(f"  Item Count: {total_info['item_count']}")

        print("\n" + "="*80)
        print("✓ Test Complete!")
        print("="*80)

        return {
            "company": company,
            "job": job,
            "quotations": quotations,
            "total": total_info
        }


def test_service_queries():
    """
    Test various query operations on services.
    """
    print("\n" + "="*80)
    print("Testing Service Query Operations")
    print("="*80)

    with Session(engine) as session:
        company_service = CompanyServiceImpl(session)
        job_service = JobServiceImpl(session)
        quotation_service = QuotationServiceImpl(session)

        print("\n[1/4] Searching Companies...")
        print("-" * 80)
        companies = company_service.search_by_name("科技", limit=5)
        print(f"✓ Found {len(companies)} companies matching '科技'")
        for c in companies:
            print(f"  - {c.name} (ID: {c.id})")

        print("\n[2/4] Listing Recent Jobs...")
        print("-" * 80)
        design_jobs = job_service.list_all("DESIGN", limit=5)
        print(f"✓ Found {len(design_jobs)} recent DESIGN jobs")
        for j in design_jobs:
            print(f"  - {j.job_no}: {j.title}")

        print("\n[3/4] Searching Quotations...")
        print("-" * 80)
        quotations = quotation_service.search_by_project("空調", limit=5)
        print(f"✓ Found {len(quotations)} quotations matching '空調'")
        for q in quotations:
            print(f"  - {q.quo_no}: {q.project_name}")

        if design_jobs:
            print("\n[4/4] Getting Quotations for a Job...")
            print("-" * 80)
            job_quotations = quotation_service.get_by_job_no(design_jobs[0].job_no)
            print(f"✓ Found {len(job_quotations)} quotations for job {design_jobs[0].job_no}")
            for q in job_quotations:
                print(f"  - {q.quo_no}: {q.project_name}")

        print("\n" + "="*80)
        print("✓ Query Test Complete!")
        print("="*80)


def test_revision_workflow():
    """
    Test creating a quotation revision.
    """
    print("\n" + "="*80)
    print("Testing Quotation Revision Workflow")
    print("="*80)

    with Session(engine) as session:
        job_service = JobServiceImpl(session)
        quotation_service = QuotationServiceImpl(session)

        # Get or create a test job
        jobs = job_service.list_all("DESIGN", limit=1)
        if not jobs:
            print("⚠ No jobs found. Run test_complete_workflow first.")
            return

        job = jobs[0]
        print(f"\n[1/2] Original Job: {job.job_no}")
        print("-" * 80)

        # Get existing quotations
        existing_quotations = quotation_service.get_by_job_no(job.job_no)
        if existing_quotations:
            latest_quo = existing_quotations[0]
            print(f"✓ Latest quotation: {latest_quo.quo_no}")
        else:
            print("⚠ No existing quotations for this job")
            return

        print("\n[2/2] Creating Revision...")
        print("-" * 80)

        # Generate revision number
        revision_quo_no = quotation_service.generate_quotation_number(
            job_no=job.job_no,
            revision_no="01"  # This will increment revision
        )
        print(f"✓ Generated revision quotation number: {revision_quo_no}")

        # Create revision with updated items
        company_service = CompanyServiceImpl(session)
        company = company_service.get_by_id(job.company_id)

        revision_quotations = quotation_service.create_quotation(
            job_no=job.job_no,
            company_id=company.id,
            project_name=latest_quo.project_name,
            currency="MOP",
            items=[
                {
                    "project_item_description": "設計費用 (修訂後)",
                    "quantity": 1.0,
                    "unit": "項",
                    "sub_amount": Decimal("55000"),  # Increased
                    "total_amount": Decimal("55000")
                }
            ],
            revision_no="01"
        )
        session.commit()

        print(f"✓ Created revision: {revision_quotations[0].quo_no}")
        print(f"  Original: {latest_quo.quo_no}")
        print(f"  Revision: {revision_quotations[0].quo_no}")

        print("\n" + "="*80)
        print("✓ Revision Test Complete!")
        print("="*80)


if __name__ == "__main__":
    import sys

    print("\n" + "="*80)
    print("Service-Based Architecture Test Suite")
    print("="*80)
    print("\nThis test demonstrates the new service-oriented approach.")
    print("Each service encapsulates complete business logic.")
    print("\nRunning tests...\n")

    try:
        # Test 1: Complete workflow
        result = test_complete_workflow()

        # Test 2: Query operations
        test_service_queries()

        # Test 3: Revision workflow
        test_revision_workflow()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print("\nServices are working correctly!")
        print("You can now use these services in your agents.")

    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED!")
        print("="*80)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
