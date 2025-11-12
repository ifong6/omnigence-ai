#!/usr/bin/env python3
"""
Database Cleanup Script for Test Data

This script provides utilities to clean up test data from the database:
- Delete all jobs (DESIGN and INSPECTION)
- Validate job statuses (check for incorrect statuses - service layer should prevent this)
- Display current database state

Usage:
    # Clean up all jobs with confirmation
    python test/cleanup_test_data.py --cleanup

    # Clean up all jobs without confirmation
    python test/cleanup_test_data.py --cleanup --no-confirm

    # Validate job statuses (check for bugs in service layer)
    python test/cleanup_test_data.py --validate

    # Display current jobs
    python test/cleanup_test_data.py --show

    # Do everything
    python test/cleanup_test_data.py --validate --cleanup --show --no-confirm
"""

import argparse
import json
from sqlmodel import Session
from app.db.engine import engine
from app.finance_agent.models.job_models import DesignJob, InspectionJob
from app.finance_agent.models.flow_models import Flow
from app.finance_agent.services.job_service import JobService
from app.finance_agent.repos.flow_repo import FlowRepo


def cleanup_all_jobs(confirm: bool = True) -> tuple[int, int]:
    """
    Delete all jobs from the database.

    Args:
        confirm: If True, prompt user for confirmation

    Returns:
        Tuple of (design_count, inspection_count) deleted
    """
    if confirm:
        response = input("\n⚠️  This will DELETE all jobs in the database. Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Cleanup cancelled by user")
            return (0, 0)

    with Session(engine) as session:
        # Count before deletion
        design_jobs = session.query(DesignJob).all()
        inspection_jobs = session.query(InspectionJob).all()

        design_count = len(design_jobs)
        inspection_count = len(inspection_jobs)

        print(f"\n📊 Found {design_count} DESIGN jobs and {inspection_count} INSPECTION jobs")

        # Delete all jobs
        for job in design_jobs:
            session.delete(job)
        for job in inspection_jobs:
            session.delete(job)

        session.commit()

    print(f"✅ Cleanup complete: {design_count} DESIGN jobs and {inspection_count} INSPECTION jobs deleted\n")
    return (design_count, inspection_count)


def validate_job_statuses() -> tuple[int, int]:
    """
    Validate that all jobs have correct status based on their quotation_status.

    Jobs should have status="NEW" when quotation_status="NOT_CREATED".
    This is a validation function, NOT a fix function - the service layer
    should ensure correct status on creation.

    Returns:
        Tuple of (valid_count, invalid_count)
    """
    with Session(engine) as session:
        valid_count = 0
        invalid_count = 0

        # Check design jobs
        design_jobs = session.query(DesignJob).all()
        for job in design_jobs:
            if job.quotation_status == "NOT_CREATED" and job.status != "NEW":
                invalid_count += 1
                print(f"  ⚠️  INVALID DESIGN job {job.job_no}: status={job.status} (should be NEW)")
            else:
                valid_count += 1

        # Check inspection jobs
        inspection_jobs = session.query(InspectionJob).all()
        for job in inspection_jobs:
            if job.quotation_status == "NOT_CREATED" and job.status != "NEW":
                invalid_count += 1
                print(f"  ⚠️  INVALID INSPECTION job {job.job_no}: status={job.status} (should be NEW)")
            else:
                valid_count += 1

    if invalid_count > 0:
        print(f"\n⚠️  Found {invalid_count} job(s) with incorrect status!")
        print("This indicates a bug in the service layer - jobs should be created with status='NEW'")
        print("Solution: Clean up invalid jobs and ensure JobService.create_job() uses status='NEW' as default\n")
    else:
        print(f"✅ All {valid_count} job(s) have correct status\n")

    return (valid_count, invalid_count)


def show_current_jobs():
    """Display all current jobs in the database."""
    with Session(engine) as session:
        service = JobService(session)

        # Get design jobs
        design_jobs = service.list_all("DESIGN", limit=100)
        print("\n" + "=" * 100)
        print(f"DESIGN JOBS ({len(design_jobs)} total)")
        print("=" * 100)

        if design_jobs:
            for job in design_jobs:
                print(f"  {job.job_no}")
                print(f"    Title: {job.title}")
                print(f"    Company ID: {job.company_id}")
                print(f"    Status: {job.status}")
                print(f"    Quotation Status: {job.quotation_status}")
                print(f"    Created: {job.date_created}")
                print()
        else:
            print("  (No DESIGN jobs found)\n")

        # Get inspection jobs
        inspection_jobs = service.list_all("INSPECTION", limit=100)
        print("=" * 100)
        print(f"INSPECTION JOBS ({len(inspection_jobs)} total)")
        print("=" * 100)

        if inspection_jobs:
            for job in inspection_jobs:
                print(f"  {job.job_no}")
                print(f"    Title: {job.title}")
                print(f"    Company ID: {job.company_id}")
                print(f"    Status: {job.status}")
                print(f"    Quotation Status: {job.quotation_status}")
                print(f"    Created: {job.date_created}")
                print()
        else:
            print("  (No INSPECTION jobs found)\n")

        print("=" * 100 + "\n")


def show_current_flows():
    """Display all flow records in the database."""
    with Session(engine) as session:
        flow_repo = FlowRepo(session)
        flows = flow_repo.list_all(limit=100)

        print("=" * 100)
        print(f"FLOW RECORDS ({len(flows)} total)")
        print("=" * 100)

        if flows:
            for flow in flows:
                print(f"  Flow ID: {flow.id}")
                print(f"    Session ID: {flow.session_id}")
                print(f"    Summary: {flow.user_request_summary}")
                print(f"    Agents: {flow.identified_agents}")
                print(f"    Created: {flow.created_at}")
                print()
        else:
            print("  (No flow records found)\n")

        print("=" * 100 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Database cleanup utilities for test data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--cleanup', action='store_true',
                        help='Delete all jobs from database')
    parser.add_argument('--validate', action='store_true',
                        help='Validate job statuses (check for incorrect statuses)')
    parser.add_argument('--show', action='store_true',
                        help='Display all current jobs')
    parser.add_argument('--no-confirm', action='store_true',
                        help='Skip confirmation prompts')

    args = parser.parse_args()

    # If no arguments, show help
    if not any([args.cleanup, args.validate, args.show]):
        parser.print_help()
        return

    print("\n" + "=" * 100)
    print("DATABASE CLEANUP UTILITIES")
    print("=" * 100)

    # Validate statuses first
    if args.validate:
        print("\n📝 Validating job statuses...")
        validate_job_statuses()

    # Then cleanup if requested
    if args.cleanup:
        print("\n🗑️  Cleaning up database...")
        cleanup_all_jobs(confirm=not args.no_confirm)

    # Show current state
    if args.show:
        show_current_jobs()
        show_current_flows()

    print("✅ All operations completed\n")


if __name__ == "__main__":
    main()
