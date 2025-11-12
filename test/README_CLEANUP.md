# Database Cleanup Utilities

This document explains the database cleanup utilities for managing test data in the product_v01 project.

## Problem Overview

When running tests multiple times, jobs accumulate in the database because:
1. Tests don't automatically clean up after themselves
2. Each test run creates new jobs with incrementing job numbers
3. Old jobs may have incorrect statuses from previous code versions

## Available Cleanup Tools

### 1. Standalone Cleanup Script

**File:** `test/cleanup_test_data.py`

A dedicated script for database maintenance operations.

#### Usage Examples

```bash
# Show all current jobs in database
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --show

# Fix incorrect job statuses (IN_PROGRESS → NEW for jobs without quotations)
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --fix-status

# Delete all jobs (with confirmation prompt)
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --cleanup

# Delete all jobs (no confirmation)
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --cleanup --no-confirm

# Do everything: fix statuses, cleanup, and show results
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --fix-status --cleanup --show --no-confirm
```

### 2. Integrated Test Cleanup

**File:** `test/test_uc1_create_job.py`

The UC1 test now has built-in cleanup options.

#### Usage Examples

```bash
# Run tests with status fix before testing
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/test_uc1_create_job.py --fix-status

# Run tests with full cleanup (will prompt for confirmation)
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/test_uc1_create_job.py --cleanup

# Run tests with full cleanup (no confirmation)
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/test_uc1_create_job.py --cleanup --no-confirm

# Fix statuses and clean up before running tests
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/test_uc1_create_job.py --fix-status --cleanup --no-confirm
```

## Common Issues & Solutions

### Issue 1: Tests show more jobs than expected

**Symptom:** TEST_DATA has 2 entries but database shows 4+ jobs

**Cause:** Multiple test runs without cleanup

**Solution:**
```bash
# Clean up before running tests
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --cleanup --no-confirm
```

### Issue 2: Jobs have IN_PROGRESS status when created

**Symptom:** New jobs created with `status="IN_PROGRESS"` instead of `status="NEW"`

**Cause:** Old jobs from previous code versions or manual updates

**Solution:**
```bash
# Fix all incorrect statuses
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --fix-status
```

**Verification:**
```bash
# Show current status of all jobs
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --show
```

## Cleanup Functions

### `cleanup_all_jobs(confirm=True)`

Deletes all DESIGN and INSPECTION jobs from the database.

**Parameters:**
- `confirm` (bool): If True, prompts for user confirmation before deletion

**Returns:**
- Tuple of (design_count, inspection_count) deleted

### `fix_job_statuses()`

Fixes jobs that have `status="IN_PROGRESS"` but `quotation_status="NOT_CREATED"`.
Sets their status to `"NEW"`.

**Returns:**
- Number of jobs fixed

### `show_current_jobs()`

Displays all current jobs in the database with full details:
- Job number
- Title
- Company ID
- Status
- Quotation status
- Creation date

## Best Practices

### Before Running Tests

Always clean up or fix statuses before running tests to ensure consistent results:

```bash
# Recommended: Clean everything and start fresh
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/test_uc1_create_job.py --cleanup --no-confirm
```

### After Code Changes

If you've modified job creation logic, fix existing jobs to match new behavior:

```bash
# Fix statuses without deleting jobs
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --fix-status
```

### Checking Database State

Before debugging issues, always check the current database state:

```bash
# Show all jobs
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --show
```

## Quick Reference

| Task | Command |
|------|---------|
| Show all jobs | `python test/cleanup_test_data.py --show` |
| Fix wrong statuses | `python test/cleanup_test_data.py --fix-status` |
| Delete all jobs (confirm) | `python test/cleanup_test_data.py --cleanup` |
| Delete all jobs (no confirm) | `python test/cleanup_test_data.py --cleanup --no-confirm` |
| Full cleanup + show | `python test/cleanup_test_data.py --fix-status --cleanup --show --no-confirm` |
| Run tests with cleanup | `python test/test_uc1_create_job.py --cleanup --no-confirm` |
| Run tests with status fix | `python test/test_uc1_create_job.py --fix-status` |

## Technical Details

### Job Status Flow

Correct job status progression:
```
NEW → IN_PROGRESS → COMPLETED
     ↓
   CANCELLED
```

### When to Use Each Status

- **NEW**: Job just created, no quotation yet
- **IN_PROGRESS**: Quotation created/being worked on
- **COMPLETED**: All work finished
- **CANCELLED**: Job cancelled

### Database Tables

- **DESIGN Jobs**: Table `"Finance".design_job`, Prefix: `JCP-`
- **INSPECTION Jobs**: Table `"Finance".inspection_job`, Prefix: `JICP-`

### Default Values

From [job_service.py:332](../app/finance_agent/services/job_service.py#L332):
```python
def create_job(
    self,
    *,
    company_id: int,
    title: str,
    job_type: str,
    index: int = 1,
    status: str = "NEW",  # ← Default status
    quotation_status: str = "NOT_CREATED"
) -> DesignJob | InspectionJob:
    ...
```

## Troubleshooting

### Script not found error

Make sure you're in the project root and using the correct PYTHONPATH:

```bash
cd /Users/keven/Desktop/product_v01
PYTHONPATH=/Users/keven/Desktop/product_v01 .venv/bin/python test/cleanup_test_data.py --show
```

### Permission denied

Make the script executable:

```bash
chmod +x test/cleanup_test_data.py
```

### Database connection error

Ensure PostgreSQL is running and database credentials are correct in your `.env` file.
