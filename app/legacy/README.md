# Legacy Tools Archive

This directory contains the original tool implementations that have been **refactored into services**.

## ⚠️ DEPRECATED

**These files are kept for reference only and should NOT be used in new code.**

All functionality has been migrated to:
- `/app/services/company_service.py`
- `/app/services/job_service.py`
- `/app/services/quotation_service.py`

## Directory Structure

```
legacy/
├── company_tools/              # Original company tool implementations
│   ├── tools/
│   │   ├── create_company_tool.py
│   │   ├── get_company_tool.py
│   │   ├── create_company_alias_tool.py
│   │   └── update_*.py
│   ├── company_crud_tools.py   # LangChain Tool registration
│   └── company_crud_handler.py # Agent handler
│
├── job_list_tools/             # Original job tool implementations
│   ├── tools/
│   │   ├── create_job_tool.py
│   │   ├── update_job_tool.py
│   │   ├── create_job_number_tool.py
│   │   └── query_tools/
│   ├── job_crud_tools.py       # LangChain Tool registration
│   ├── job_query_tools.py      # Query tool registration
│   └── job_crud_handler.py     # Agent handler
│
└── quotation_tools/            # Original quotation tool implementations
    ├── tools/
    │   ├── crud_tools/
    │   │   ├── create_quotation_no_tool.py
    │   │   ├── create_quotation_in_db.py
    │   │   ├── update_quotation_tool.py
    │   │   └── extract_quotation_info_tool.py
    │   └── output_quotation_info_for_ui.py
    ├── quotation_crud_tools.py # LangChain Tool registration
    └── quotation_crud_handler.py # Agent handler
```

## Migration Status

### ✅ Migrated to Services

All business logic from these tools has been migrated to services:

#### CompanyService (`/app/services/company_service.py`)
- ✅ `create()` - Basic company creation
- ✅ `update()` - Update company fields
- ✅ `get_by_id()` - Get by ID
- ✅ `get_by_name()` - Get by name
- ✅ `get_or_create()` - Get existing or create new
- ✅ `search_by_name()` - Search companies
- ✅ `list_all()` - List all companies
- ✅ `create_with_contact_enrichment()` - From `create_company_tool.py`
- ✅ `generate_alias_with_llm()` - From `create_company_alias_tool.py`

#### JobService (`/app/services/job_service.py`)
- ✅ `create_job()` - Create job with auto job_no
- ✅ `update()` - Update job fields
- ✅ `get_by_id()` - Get by ID
- ✅ `get_by_job_no()` - Get by job number
- ✅ `get_by_company()` - Get company jobs
- ✅ `get_by_company_with_info()` - Get jobs with company info (JOIN)
- ✅ `list_all()` - List all jobs
- ✅ `list_all_with_company()` - List jobs with company info (JOIN)
- ✅ `_next_job_no()` - Auto job number generation

#### QuotationService (`/app/services/quotation_service.py`)
- ✅ `create_quotation()` - Create quotation with items
- ✅ `update_quotation()` - Update quotation items
- ✅ `get_quotation_by_id()` - Get by ID
- ✅ `get_quotations_by_quo_no()` - Get by quotation number
- ✅ `get_quotations_by_client()` - Get client quotations
- ✅ `get_quotations_by_project()` - Get project quotations
- ✅ `get_quotation_total()` - Calculate totals
- ✅ `get_by_job_no()` - Get job quotations
- ✅ `search_by_project()` - Search by project name
- ✅ `list_all()` - List all quotations
- ✅ `generate_quotation_number()` - From `create_quotation_no_tool.py`
- ✅ `_next_quo_no()` - Auto quotation number generation with revisions

## Why These Files Are Legacy

### 1. Business Logic Scattered
```python
# OLD: Business logic in tools (❌)
def create_company_tool(company_name, address=None, phone=None):
    # 135 lines of business logic, validation, Google CSE integration
    # Mixed concerns: input parsing + business logic + DB operations
    if not company_name:
        raise ValueError("...")

    # Normalize
    name = company_name.strip()

    # Google CSE lookup
    found = search_company_contact(name)

    # Database operations
    existing = _select_company_by_name(name)
    if existing:
        # Update logic
    else:
        # Create logic
```

### 2. Not Reusable
```python
# OLD: Tools only work with LangChain agents (❌)
# Can't use in:
# - API endpoints
# - CLI tools
# - Background jobs
# - Tests

# NEW: Services work everywhere (✅)
with Session(engine) as session:
    service = CompanyService(session)
    company = service.create_with_contact_enrichment(...)
    # Use in agents, APIs, CLIs, anywhere!
```

### 3. Hard to Test
```python
# OLD: Must mock LangChain to test (❌)
# Tests are coupled to tool format

# NEW: Test services directly (✅)
def test_create_company():
    with Session(engine) as session:
        service = CompanyService(session)
        result = service.create_with_contact_enrichment(name="Test")
        assert result["status"] == "created"
```

### 4. Duplicate Code
```python
# OLD: Same logic in multiple tools (❌)
# create_company_tool.py - 135 lines
# update_company_name.py - 85 lines
# update_company_address.py - 85 lines
# All duplicate validation, normalization, error handling

# NEW: Logic in one place (✅)
# CompanyService - 417 lines, handles ALL operations
# No duplication
```

## What to Use Instead

### For Agents
Use the new service-based tools:

```python
from app.finance_agent.tools.service_tool_registry import SERVICE_TOOLS

response = invoke_react_agent(
    tools=SERVICE_TOOLS,  # CompanyService, JobService, QuotationService
    user_input=state.user_input
)
```

### For Direct Use
Use services directly:

```python
from sqlmodel import Session
from app.db.engine import engine
from app.services.company_service import CompanyService
from app.services.job_service import JobService
from app.services.quotation_service import QuotationService

with Session(engine) as session:
    # Company operations
    company_svc = CompanyService(session)
    company = company_svc.get_or_create(name="澳門科技大學")

    # Job operations
    job_svc = JobService(session)
    job = job_svc.create_job(
        company_id=company.id,
        title="消防系統設計",
        job_type="DESIGN"
    )

    # Quotation operations
    quo_svc = QuotationService(session)
    quo_no = quo_svc.generate_quotation_number(job.job_no)
    quotations = quo_svc.create_quotation(
        job_no=job.job_no,
        company_id=company.id,
        project_name="消防系統設計",
        items=[...]
    )

    session.commit()
```

## Documentation

For detailed information about the new architecture, see:

- `/docs/SERVICE_BASED_ARCHITECTURE.md` - Complete service guide
- `/docs/REFACTORING_SUMMARY.md` - Migration summary
- `/docs/FOLDER_RESTRUCTURING.md` - Before/after comparison

## Timeline

- **Created**: October 2024
- **Deprecated**: November 2024
- **Archived**: November 5, 2024

## Removal Plan

These files will be kept for **30 days** (until December 5, 2024) and then permanently deleted.

If you need to reference old implementations during this period:
1. Check this legacy folder
2. Review git history if needed
3. Migrate any remaining code to services

## Questions?

If you're unsure whether to use legacy tools or new services:

**Always use the new services!** They are:
- ✅ More maintainable
- ✅ Better tested
- ✅ More flexible
- ✅ Framework-agnostic
- ✅ Reusable everywhere

---

**Remember**: This is a legacy archive. Do NOT use these files in new code! ⛔
