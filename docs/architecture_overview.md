# Architecture Overview: Controller → Service → Database

This document provides a comprehensive overview of the application's layered architecture, designed for clarity, maintainability, and type safety.

## Table of Contents

1. [Architecture Diagram](#architecture-diagram)
2. [Layer Overview](#layer-overview)
3. [Request/Response Flow](#requestresponse-flow)
4. [Detailed Component Reference](#detailed-component-reference)
5. [Data Transfer Objects (DTOs)](#data-transfer-objects-dtos)
6. [Code Examples](#code-examples)
7. [Design Principles](#design-principles)
8. [File Structure](#file-structure)

---

## Architecture Diagram

```
                              ┌─────────────────────────┐
                              │         CLIENT          │
                              │  (UI / Chat / API)      │
                              └───────────┬─────────────┘
                                          │
                     ┌────────────────────┼────────────────────┐
                     │                    │                    │
                     ▼                    ▼                    ▼
        ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐
        │  REST API Request   │  │ Natural Language    │  │ Human Feedback / HITL│
        │  (Structured Input) │  │   (Unstructured)    │  │ interrupt()          │
        └─────────┬───────────┘  └──────────┬──────────┘  └──────────┬───────────┘
                  │                         │                        │
                  ▼                         ▼                        │
     ┌──────────────────────┐     ┌──────────────────────────┐       │
     │   CRUD CONTROLLERS   │     │     AGENT CONTROLLER     │       │
     │   (/api/jobs...)     │     │   (/api/agents/orch.)    │       │
     └─────────┬────────────┘     └────────────┬─────────────┘       │
               │                               │                     │
               ▼                               ▼                     │
   ┌────────────────────────┐       ┌────────────────────────────┐   │
   │   API Controllers      │       │   ORCHESTRATOR AGENT       │   │
   │  - JobController       │       │   (Routing + Planning)     │   │
   │  - CompanyController   │       └───────────┬────────────────┘   │
   │  - QuotationController │                   │                    │
   └──────────┬─────────────┘                   │ selects agent      │
              │                                 ▼                    │
              │                    ┌─────────────────────────────────┴──┐
              │                    │  DOMAIN AGENTS (Finance / Job /    │
              │                    │   Company / Quotation Agents)      │
              │                    └───────────┬────────────────────────┘
              │                                │
              ▼                                ▼
     ┌────────────────────────┐    ┌──────────────────────────── ┐
     │  Input DTO Validation  │    │  TOOL LAYER (Agent Tools)   │
     │  Response DTO Mapping  │    │  Thin wrappers over service │
     └──────────┬─────────────┘    │  (job_create, quo_create..) │
                │                  └───────────┬─────────────── ─┘
                │                              │
                └──────────────┬───────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                              SERVICE LAYER                                 │
│                                                                            │
│  ┌────────────────────┬────────────────────┬─────────────────────────────┐ │
│  │ CompanyServiceImpl │  JobServiceImpl    │ QuotationServiceImpl        │ │
│  │                    │                    │                             │ │
│  │ - create()         │ - create_job()     │ - create_quotation()        │ │
│  │ - get_by_id()      │ - get_job_by_id()  │ - get_quo_by_id()           │ │
│  │ - search_by_name() │ - update_job()     │ - generate_quo_no()         │ │
│  │ - get_or_create()  │ - list_all_jobs()  │ - get_quo_total()           │ │
│  └────────────────────┴────────────────────┴─────────────────────────────┘ │
│                                                                            │
│  - Pure business logic                                                     │
│  - Uses Session + SQLModel models directly                                 │
│  - Transaction management                                                  │
│  - Input validation                                                        │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           SQLMODEL ORM LAYER                               │
│                                                                            │
│  ┌─────────────┬───────────────┬───────────────┬─────────────────────────┐ │
│  │   Company   │   DesignJob   │ InspectionJob │      Quotation          │ │
│  │             │               │               │                         │ │
│  │ - id        │ - id          │ - id          │ - id                    │ │
│  │ - name      │ - job_no      │ - job_no      │ - quo_no                │ │
│  │ - alias     │ - company_id  │ - company_id  │ - client_id             │ │
│  │ - address   │ - title       │ - title       │ - project_name          │ │
│  │ - phone     │ - status      │ - status      │ - items                 │ │
│  │             │ - date_created│ - date_created│ - status                │ │
│  └─────────────┴───────────────┴───────────────┴─────────────────────────┘ │
│                                                                            │
│                      ┌───────────────────┐                                 │
│                      │   QuotationItem   │                                 │
│                      │                   │                                 │
│                      │ - item_desc       │                                 │
│                      │ - quantity        │                                 │
│                      │ - unit_price      │                                 │
│                      │ - amount          │                                 │
│                      └───────────────────┘                                 │
│                                                                            │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        DATABASE (PostgreSQL / Supabase)                    │
│                                                                            │
│  ┌─────────────┬───────────────┬───────────────┬─────────────────────────┐ │
│  │   Finance.  │    Finance.   │    Finance.   │       Finance.          │ │
│  │   company   │   design_job  │ inspection_job│       quotation         │ │
│  └─────────────┴───────────────┴───────────────┴─────────────────────────┘ │
│                                                                            │
│  - Supabase hosted                                                         │
│  - Connection pooling via SQLAlchemy                                       │
│  - Server-side defaults (e.g., date_created = now())                       │
│  - Enum constraints enforced at DB level                                   │
└────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Request Flow

#### Job Creation Flow

```
┌──────────┐    POST /api/jobs       ┌────────────────┐
│  Client  │ ───────────────────────>│  JobController │
└──────────┘    CreateJobDTO         └───────┬────────┘
                                             │
                                             │ service.create_job()
                                             ▼
                                     ┌────────────────┐
                                     │ JobServiceImpl │
                                     │                │
                                     │ 1. Validate    │
                                     │ 2. Generate ID │
                                     │ 3. session.add │
                                     │ 4. Return Model│
                                     └───────┬────────┘
                                             │
                                             │ SELECT/INSERT
                                             ▼
                               ┌──────────────────────────┐
                               │   DesignJob (SQLModel)   │
                               │   or InspectionJob       │
                               └──────────────────────────┘
                                             │
                                             │ ORM mapping
                                             ▼
                               ┌──────────────────────────┐
                               │   PostgreSQL Database    │
                               │   Finance.design_job     │
                               └──────────────────────────┘
```

#### Quotation Creation Flow

```
┌──────────┐  POST /api/quotations   ┌─────────────────────┐
│  Client  │ ───────────────────────>│ QuotationController │
└──────────┘  CreateQuotationDTO     └─────────┬───────────┘
              (with items array)               │
                                               │ service.create_quotation()
                                               ▼
                                    ┌─────────────────────┐
                                    │QuotationServiceImpl │
                                    │                     │
                                    │ 1. Generate quo_no  │
                                    │ 2. Create header    │
                                    │ 3. Create items     │
                                    │ 4. Calculate totals │
                                    │ 5. session.flush()  │
                                    └─────────┬───────────┘
                                              │
                                              │ INSERT (atomic)
                                              ▼
                            ┌────────────────────────────────┐
                            │     Quotation (SQLModel)       │
                            │              │                 │
                            │              ▼                 │
                            │   ┌────────────────────┐       │
                            │   │  QuotationItem x N │       │
                            │   └────────────────────┘       │
                            └────────────────────────────────┘
                                              │
                                              │ ORM mapping
                                              ▼
                            ┌────────────────────────────────┐
                            │      PostgreSQL Database       │
                            │  Finance.quotation             │
                            │  Finance.quotation_item        │
                            └────────────────────────────────┘
```

#### Company Creation Flow

```
┌──────────┐  POST /api/companies   ┌───────────────────┐
│  Client  │ ──────────────────────>│  CompanyController│
└──────────┘  CreateCompanyDTO      └─────────┬─────────┘
              {name, alias, ...}              │
                                              │ service.create()
                                              ▼
                                    ┌───────────────────┐
                                    │ CompanyServiceImpl│
                                    │                   │
                                    │ 1. Validate name  │
                                    │ 2. Check unique   │
                                    │ 3. session.add()  │
                                    │ 4. Return Model   │
                                    └─────────┬─────────┘
                                              │
                                              │ INSERT
                                              ▼
                            ┌────────────────────────────────┐
                            │      Company (SQLModel)        │
                            │                                │
                            │  - id (auto-generated)         │
                            │  - name (unique constraint)    │
                            │  - alias, address, phone       │
                            └────────────────────────────────┘
                                              │
                                              │ ORM mapping
                                              ▼
                            ┌────────────────────────────────┐
                            │      PostgreSQL Database       │
                            │      Finance.company           │
                            └────────────────────────────────┘
```

#### Agent Orchestration + Human-in-the-Loop Flow

```
                              Client
                                │
                                │  POST /api/agents/orchestrator
                                │  body: UserRequest { session_id, message, … }
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                            AgentController                                 │
│  - log_request()                                                           │
│  - map UserRequest → AgentFlowRequestDTO                                   │
│  - call orchestrator_agent_flow(dto)                                       │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent (Main Graph)                         │
│  1. classifier_agent_node → decides "finance"                              │
│  2. pre_routing_logger_node → saves intent to state                        │
│  3. route → FinanceAgentFlow                                               │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         Finance Agent Flow                                 │
│  - uses tools:                                                             │
│      • JobServiceImpl  (create/list jobs)                                  │
│      • QuotationServiceImpl (create quotation, compute totals)             │
│      • CompanyServiceImpl   (lookup or create company)                     │
│  - builds structured result (e.g., JobDTO + QuotationDTO)                  │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            (Missing Info)            (Complete Info)
                    │                       │
                    ▼                       ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│   INTERRUPT PATH        │     │    SUCCESS PATH         │
│                         │     │                         │
│ - raise InterruptExcept │     │ - set final_response    │
│ - status="interrupt"    │     │ - status="success"      │
│ - message="Need project │     │ - return complete data  │
│   title / company name" │     │                         │
└───────────┬─────────────┘     └───────────┬─────────────┘
            │                               │
            ▼                               ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                            AgentController                                 │
│                                                                            │
│  If status="interrupt":               If status="success":                 │
│  - send clarification question        - wrap into ApiResponse[...]         │
│  - include session_id                 - send back to client                │
│  - requires_feedback: true                                                 │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            (Needs Feedback)          (Complete)
                    │                       │
                    ▼                       ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│   Client / Human User   │     │      Final Response     │
│                         │     │                         │
│ - Reads clarification   │     │ {                       │
│   question              │     │   "status": "success",  │
│ - Sends follow-up:      │     │   "result": { ... }     │
│                         │     │ }                       │
│ POST /api/agents/       │     │                         │
│   human-in-the-loop     │     └─────────────────────────┘
│ {                       │
│   session_id,           │
│   message: "The project │
│   is AC duct design..." │
│ }                       │
└───────────┬─────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                            AgentController                                 │
│  - passes same session_id                                                  │
│  - calls resume_agent(request)                                             │
│  - orchestrator_agent_flow resumes with existing MainFlowState             │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    Finance Agent Flow (Resumed)                            │
│  - continues with human_feedback filled                                    │
│  - now has all required info                                               │
│  - finishes job/quotation creation                                         │
│  - returns final_response                                                  │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
                                ▼
                        Final Response to Client
```

**Key Concepts:**
- **Controllers**: Entry/exit points, mapping DTOs, no agent logic
- **Orchestrator Agent**: Decides which agent handles the request, manages conversation state
- **Finance Agent**: Domain expert that calls services/tools to create jobs, quotations, etc.
- **HITL (Human-in-the-Loop)**: Interrupt path where agent pauses, controller returns clarification question, and resumes with updated state when user replies

---

## Layer Overview

### 1. Controller Layer (`app/controllers/`)
- **Purpose**: HTTP interface, request/response handling
- **Technology**: FastAPI, Pydantic DTOs
- **Components**:
  - `CompanyController` - Company CRUD endpoints
  - `JobController` - Job management endpoints
  - `QuotationController` - Quotation creation and management
  - `AgentController` - AI agent workflow orchestration

### 2. Service Layer (`app/services/impl/`)
- **Purpose**: Business logic and data operations
- **Technology**: SQLModel, SQLAlchemy Session
- **Components**:
  - `CompanyServiceImpl` - Company business logic
  - `JobServiceImpl` - Job creation, queries, auto-ID generation
  - `QuotationServiceImpl` - Quotation with items, total calculation

### 3. Model Layer (`app/models/`)
- **Purpose**: ORM entities mapping to database tables
- **Technology**: SQLModel
- **Components**:
  - `Company` - Company entity
  - `DesignJob` - Design job entity
  - `InspectionJob` - Inspection job entity
  - `Quotation` - Quotation header
  - `QuotationItem` - Quotation line items

### 4. Database Layer
- **Purpose**: Persistent storage
- **Technology**: PostgreSQL (Supabase), SQLModel ORM
- **Schema**: `Finance.*` tables

---

## Detailed Component Reference

### Controllers

#### CompanyController (`app/controllers/company_controller.py`)

**Router**: `/api/companies`
**Tags**: `["Companies"]`

| Endpoint | Method | Response Model | Description |
|----------|--------|----------------|-------------|
| `/` | POST | `SuccessResponse[CompanyDTO]` | Create a new company |
| `/get-or-create` | POST | `SuccessResponse[CompanyDTO]` | Get existing or create new company |
| `/{company_id}` | GET | `SuccessResponse[CompanyDTO]` | Get company by ID |
| `/by-name/{name}` | GET | `SuccessResponse[CompanyDTO]` | Get company by exact name |
| `/search/` | GET | `SuccessResponse[CompanySearchResponseDTO]` | Search companies by name/alias |
| `/{company_id}` | PATCH | `SuccessResponse[CompanyDTO]` | Update company details |
| `/` | GET | `SuccessResponse[CompanyListResponseDTO]` | List all companies (paginated) |

---

#### JobController (`app/controllers/job_controller.py`)

**Router**: `/api/jobs`
**Tags**: `["Jobs"]`

| Endpoint | Method | Response Model | Description |
|----------|--------|----------------|-------------|
| `/` | POST | `SuccessResponse[JobDTO]` | Create new job (DESIGN or INSPECTION) |
| `/{job_id}` | GET | `SuccessResponse[JobDTO]` | Get job by ID (auto-detects type) |
| `/by-number/{job_no}` | GET | `SuccessResponse[JobDTO]` | Get job by job number |
| `/company/{company_id}` | GET | `SuccessResponse[JobSearchResponseDTO]` | Get all jobs for a company |
| `/{job_id}` | PATCH | `SuccessResponse[JobDTO]` | Update job details |
| `/` | GET | `SuccessResponse[JobSearchResponseDTO]` | List all jobs (both types) |

---

#### QuotationController (`app/controllers/quotation_controller.py`)

**Router**: `/api/quotations`
**Tags**: `["Quotations"]`

| Endpoint | Method | Response Model | Description |
|----------|--------|----------------|-------------|
| `/` | POST | `SuccessResponse[QuotationCreateResponseDTO]` | Create quotation with line items |
| `/{quotation_id}` | GET | `SuccessResponse[QuotationDTO]` | Get quotation by ID |
| `/by-number/{quo_no}` | GET | `SuccessResponse[QuotationDTO]` | Get quotation by number |
| `/by-job/{job_no}` | GET | `SuccessResponse[QuotationSearchResponseDTO]` | Get quotations for a job |
| `/by-client/{client_id}` | GET | `SuccessResponse[QuotationSearchResponseDTO]` | Get quotations for a client |
| `/{quotation_id}` | PATCH | `SuccessResponse[QuotationDTO]` | Update quotation status/details |
| `/generate-number` | POST | `dict` | Generate quotation number |
| `/{quo_no}/total` | GET | `dict` | Calculate quotation total |

---

#### AgentController (`app/controllers/agent_controller.py`)

**Router**: `/api/agents`
**Tags**: `["AI Agents"]`

| Endpoint | Method | Response Model | Description |
|----------|--------|----------------|-------------|
| `/orchestrator` | POST | `dict` | Execute orchestrator agent workflow |
| `/human-in-the-loop` | POST | `dict` | Resume agent with human feedback |
| `/finance-agent` | POST | `dict` | Execute finance agent workflow |
| `/health` | GET | `dict` | Check agent services health status |
| `/status/{session_id}` | GET | `dict` | Get agent session status |

**Key Features**:
- Orchestrates AI agent workflows using LangGraph
- Handles human-in-the-loop interruptions via `InterruptException`
- Supports multiple agent types (orchestrator, finance, HR)
- Session-based workflow tracking
- Error handling for agent execution failures

---

### Services

#### CompanyServiceImpl (`app/services/impl/CompanyServiceImpl.py`)

**Key Methods**:
```python
def create(*, name: str, alias: str = None, address: str = None, phone: str = None) -> Company
def get_by_id(company_id: int) -> Optional[Company]
def get_by_name(name: str) -> Optional[Company]
def search_by_name(search_term: str, limit: int = 10) -> List[Company]
def get_or_create(*, name: str, alias: str = None, ...) -> Company
def update(company_id: int, *, name: str = None, ...) -> Optional[Company]
def list_all(limit: int = None) -> List[Company]
```

---

#### JobServiceImpl (`app/services/impl/JobServiceImpl.py`)

**Key Methods**:
```python
# Core operations (with job_type)
def create_job(*, company_id: int, title: str, job_type: str, index: int = 1, ...) -> DesignJob | InspectionJob
def update(job_id: int, job_type: str, *, title: str = None, status: str = None, ...) -> Optional[...]
def get_by_id(job_id: int, job_type: str) -> Optional[DesignJob | InspectionJob]
def list_all(job_type: str, limit: int = None, ...) -> List[DesignJob | InspectionJob]

# Convenience methods (auto-detect type)
def get_job_by_id(job_id: int) -> Optional[DesignJob | InspectionJob]
def get_job_by_job_no(job_no: str) -> Optional[DesignJob | InspectionJob]
def get_jobs_by_company_id(company_id: int, limit: int = None, offset: int = 0) -> Sequence[...]
def update_job(job_id: int, payload) -> Optional[DesignJob | InspectionJob]
def list_all_jobs(limit: int = None, offset: int = 0) -> Sequence[...]

# Utility
def _generate_job_number(job_type: str, company_id: int, index: int = 1) -> str
```

---

#### QuotationServiceImpl (`app/services/impl/QuotationServiceImpl.py`)

**Key Methods**:
```python
def create_quotation(*, job_no: str, company_id: int, project_name: str, items: List[dict], ...) -> dict
def get_quotation_by_id(quotation_id: int) -> Optional[Quotation]
def get_quotation_by_quo_no(quo_no: str) -> Optional[Quotation]
def get_quotations_by_job_no(job_no: str) -> List[Quotation]
def get_quotations_by_client_id(client_id: int, limit: int = None, offset: int = 0) -> List[Quotation]
def update_quotation(quotation_id: int, payload) -> Optional[Quotation]
def generate_quotation_number(job_no: str, revision_no: str = "00") -> str
def get_quotation_total(quo_no: str) -> dict
```

---

### SQLModel Models

#### Company (`app/models/company_model.py`)

```python
class Company(SQLModel, table=True):
    __tablename__ = "company"
    __table_args__ = {"schema": "Finance"}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., unique=True, index=True)
    alias: Optional[str] = Field(None)
    address: Optional[str] = Field(None)
    phone: Optional[str] = Field(None)
```

---

#### DesignJob (`app/models/job_models.py`)

```python
class JobBase(SQLModel):
    """Shared fields between job models"""
    company_id: int = Field(foreign_key="Finance.company.id")
    title: str
    status: str  # DB enforces enum: 'NEW'|'IN_PROGRESS'|'COMPLETED'|'CANCELLED'
    job_no: Optional[str] = None
    quotation_status: Optional[str] = None
    quotation_issued_at: Optional[datetime] = None

class DesignJob(JobBase, table=True):
    __tablename__ = "design_job"
    __table_args__ = {"schema": "Finance"}

    id: Optional[int] = Field(default=None, primary_key=True)
    date_created: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
    )
```

---

#### InspectionJob (`app/models/job_models.py`)

```python
class InspectionJob(JobBase, table=True):
    __tablename__ = "inspection_job"
    __table_args__ = {"schema": "Finance"}

    id: Optional[int] = Field(default=None, primary_key=True)
    date_created: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
    )
```

---

#### JobCreate / JobUpdate (`app/models/job_models.py`)

```python
class JobCreate(JobBase):
    """Input schema for job creation"""
    id: Optional[int] = None

class JobUpdate(SQLModel):
    """Input schema for job updates (all optional)"""
    company_id: Optional[int] = None
    title: Optional[str] = None
    status: Optional[str] = None
    job_no: Optional[str] = None
    quotation_status: Optional[str] = None
    quotation_issued_at: Optional[datetime] = None
```

---

#### Quotation (`app/models/quotation_model.py`)

```python
class Quotation(SQLModel, table=True):
    __tablename__ = "quotation"
    __table_args__ = {"schema": "Finance"}

    id: Optional[int] = Field(default=None, primary_key=True)
    quo_no: str = Field(..., unique=True, index=True)
    client_id: int = Field(..., foreign_key="Finance.company.id")
    project_name: str
    date_issued: date
    status: QuotationStatus = Field(default=QuotationStatus.DRAFTED)
    currency: str = Field(default="MOP")
    revision_no: int = Field(default=0)
    valid_until: Optional[date] = Field(None)
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

#### QuotationItem (`app/models/quotation_model.py`)

```python
class QuotationItem(SQLModel, table=True):
    __tablename__ = "quotation_item"
    __table_args__ = {"schema": "Finance"}

    id: Optional[int] = Field(default=None, primary_key=True)
    quotation_id: int = Field(..., foreign_key="Finance.quotation.id")
    item_desc: str
    quantity: int = Field(..., gt=0)
    unit: UnitType = Field(default=UnitType.Lot)
    unit_price: Decimal = Field(..., ge=0)
    amount: Decimal  # quantity × unit_price
```

---

### Enums (`app/models/enums.py`)

```python
from enum import Enum

class QuotationStatus(str, Enum):
    DRAFTED = "DRAFTED"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class UnitType(str, Enum):
    Lot = "Lot"
    day = "day"
    hour = "hour"
    piece = "piece"
    set = "set"
    sqm = "sqm"  # square meter
    lm = "lm"    # linear meter

class DBTable(Enum):
    """Database table references with schema"""
    COMPANY_TABLE = ("Finance", "company")
    DESIGN_JOB_TABLE = ("Finance", "design_job")
    INSPECTION_JOB_TABLE = ("Finance", "inspection_job")
    QUOTATION_TABLE = ("Finance", "quotation")

    @property
    def schema(self):
        return self.value[0]

    @property
    def table(self):
        return self.value[1]
```

---

## Data Transfer Objects (DTOs)

### Company DTOs (`app/dto/company_dto.py`)

```python
# Output DTO
class CompanyDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    alias: Optional[str]
    address: Optional[str]
    phone: Optional[str]

# Input DTO
class CreateCompanyDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    alias: Optional[str] = Field(None, max_length=64)
    address: Optional[str] = Field(None, max_length=300)
    phone: Optional[str] = Field(None, max_length=32)

# Collection Response
class CompanySearchResponseDTO(BaseModel):
    companies: List[CompanyDTO]
    count: int
```

---

### Job DTOs (`app/dto/job_dtos.py`)

```python
# Output DTO
class JobDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_no: str
    company_id: int
    title: str
    status: str
    quotation_status: str
    quotation_issued_at: Optional[datetime]
    date_created: datetime

# Input DTO
class CreateJobDTO(BaseModel):
    company_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    job_type: str  # "DESIGN" or "INSPECTION"
    index: int = Field(default=1, ge=1)
    status: str = Field(default="NEW")
    quotation_status: str = Field(default="NOT_CREATED")

# Collection Response
class JobSearchResponseDTO(BaseModel):
    jobs: List[JobDTO]
    count: int
    limit: Optional[int]
    offset: int = 0
```

---

### Quotation DTOs (`app/dto/quotation_dto.py`)

```python
# Output DTOs
class QuotationItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int]
    quotation_id: Optional[int]
    item_desc: str
    quantity: int
    unit: UnitType
    unit_price: Decimal
    amount: Decimal

class QuotationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int]
    quo_no: str
    client_id: int
    project_name: str
    date_issued: date
    status: QuotationStatus
    currency: str
    revision_no: int
    valid_until: Optional[date]
    notes: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

# Input DTOs
class CreateQuotationItemDTO(BaseModel):
    item_desc: str = Field(..., min_length=1, max_length=500)
    quantity: int = Field(..., gt=0)
    unit: UnitType = Field(default=UnitType.Lot)
    unit_price: Decimal = Field(..., ge=0)

class CreateQuotationDTO(BaseModel):
    job_no: str = Field(..., min_length=1)
    company_id: int = Field(..., gt=0)
    project_name: str = Field(..., min_length=1, max_length=500)
    currency: str = Field(default="MOP", min_length=3, max_length=3)
    items: List[CreateQuotationItemDTO] = Field(..., min_length=1)
    date_issued: Optional[date] = None
    revision_no: str = Field(default="00")
    valid_until: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)
```

---

## Code Examples

### Create Job Flow

**Request:**
```http
POST /api/jobs
Content-Type: application/json

{
  "company_id": 123,
  "title": "Office Renovation Design",
  "job_type": "DESIGN",
  "index": 1
}
```

**Controller:**
```python
@router.post("/", response_model=SuccessResponse[JobDTO], status_code=201)
def create_job(request: CreateJobDTO, session: Session = Depends(get_session)):
    service = JobServiceImpl(session)
    job = service.create_job(
        company_id=request.company_id,
        title=request.title,
        job_type=request.job_type,
        status=getattr(request, 'status', 'NEW')
    )
    job_dto = JobDTO.model_validate(job)
    return BaseController.success_response(
        data=job_dto.model_dump(),
        message="Job created successfully"
    )
```

**Service:**
```python
def create_job(self, *, company_id: int, title: str, job_type: str, index: int = 1, ...):
    # 1. Generate job number
    job_no = self._generate_job_number(job_type, company_id, index)
    # Result: "Q-JCP-25-11-1"

    # 2. Create SQLModel instance
    job = DesignJob(
        company_id=company_id,
        title=title,
        job_no=job_no,
        status="NEW",
        quotation_status="NOT_CREATED"
    )

    # 3. Persist to database
    self.session.add(job)
    self.session.flush()
    self.session.refresh(job)

    # 4. Return model with DB-generated fields (id, date_created)
    return job
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "job_no": "Q-JCP-25-11-1",
    "company_id": 123,
    "title": "Office Renovation Design",
    "status": "NEW",
    "quotation_status": "NOT_CREATED",
    "quotation_issued_at": null,
    "date_created": "2025-11-15T10:30:00Z"
  },
  "message": "Job created successfully"
}
```

---

### Create Quotation Flow

**Request:**
```http
POST /api/quotations
Content-Type: application/json

{
  "job_no": "JCP-25-01-1",
  "company_id": 15,
  "project_name": "Office HVAC System Design",
  "currency": "MOP",
  "revision_no": "00",
  "items": [
    {
      "item_desc": "Design Services",
      "quantity": 1,
      "unit": "Lot",
      "unit_price": 50000.00
    },
    {
      "item_desc": "Site Survey",
      "quantity": 2,
      "unit": "day",
      "unit_price": 5000.00
    }
  ]
}
```

**Controller:**
```python
@router.post("/", response_model=SuccessResponse[QuotationCreateResponseDTO], status_code=201)
def create_quotation(request: CreateQuotationDTO, session: Session = Depends(get_session)):
    service = QuotationServiceImpl(session)
    result = service.create_quotation(
        job_no=request.job_no,
        company_id=request.company_id,
        project_name=request.project_name,
        items=[item.model_dump() for item in request.items],
        currency=request.currency,
        revision_no=request.revision_no
    )

    # Convert Models to DTOs
    quotations_dto = [QuotationDTO.model_validate(q) for q in result["quotations"]]

    return BaseController.success_response(
        data={
            "quotations": [dto.model_dump() for dto in quotations_dto],
            "quo_no": result["quo_no"],
            "total": float(result["total"]),
            "item_count": result["item_count"]
        },
        message="Quotation created successfully"
    )
```

**Service:**
```python
def create_quotation(self, *, job_no: str, company_id: int, project_name: str, items: List[dict], ...):
    # 1. Generate quotation number
    quo_no = self.generate_quotation_number(job_no, revision_no)
    # Result: "Q-JCP-25-01-1-R00"

    # 2. Create quotation header
    quotation = Quotation(
        quo_no=quo_no,
        client_id=company_id,
        project_name=project_name,
        currency=currency,
        date_issued=date.today(),
        status=QuotationStatus.DRAFTED
    )
    self.session.add(quotation)
    self.session.flush()  # Get ID

    # 3. Create line items
    total = Decimal("0")
    for item_data in items:
        amount = Decimal(str(item_data["quantity"])) * Decimal(str(item_data["unit_price"]))
        item = QuotationItem(
            quotation_id=quotation.id,
            item_desc=item_data["item_desc"],
            quantity=item_data["quantity"],
            unit=item_data["unit"],
            unit_price=item_data["unit_price"],
            amount=amount
        )
        self.session.add(item)
        total += amount

    self.session.flush()

    # 4. Return result dict
    return {
        "quotations": [quotation],
        "quo_no": quo_no,
        "total": total,
        "item_count": len(items)
    }
```

**Response:**
```json
{
  "success": true,
  "data": {
    "quotations": [
      {
        "id": 101,
        "quo_no": "Q-JCP-25-01-1-R00",
        "client_id": 15,
        "project_name": "Office HVAC System Design",
        "date_issued": "2025-11-15",
        "status": "DRAFTED",
        "currency": "MOP",
        "revision_no": 0,
        "valid_until": null,
        "notes": null,
        "created_at": "2025-11-15T10:30:00Z",
        "updated_at": "2025-11-15T10:30:00Z"
      }
    ],
    "quo_no": "Q-JCP-25-01-1-R00",
    "total": 60000.00,
    "item_count": 2
  },
  "message": "Quotation created successfully"
}
```

---

## Design Principles

1. **No DAO Layer** - Services use SQLModel + Session directly
2. **Type Safety** - Full Pydantic validation and typed responses
3. **Separation of Concerns** - Controllers handle HTTP, Services handle logic
4. **Schema Independence** - DTOs decouple API from database models
5. **Server-Side Defaults** - Database generates timestamps, IDs
6. **Enum Enforcement** - Database-level constraints for status fields

---

## File Structure

```
app/
├── controllers/                 # HTTP Layer
│   ├── base_controller.py      # Common functionality
│   ├── company_controller.py   # /api/companies
│   ├── job_controller.py       # /api/jobs
│   ├── quotation_controller.py # /api/quotations
│   └── agent_controller.py     # /api/agents (AI workflows)
│
├── services/                    # Business Logic Layer
│   ├── __init__.py             # Abstract interfaces
│   └── impl/
│       ├── CompanyServiceImpl.py
│       ├── JobServiceImpl.py
│       └── QuotationServiceImpl.py
│
├── core/                        # AI Agent Orchestration
│   └── orchestrator_agent.py   # Main agent workflow coordinator
│
├── finance_agent/               # Finance-specific AI Agent
│   └── finance_agent_flow.py   # Finance workflow implementation
│
├── models/                      # SQLModel ORM Models
│   ├── enums.py                # Status enums, DBTable
│   ├── company_model.py        # Finance.company
│   ├── job_models.py           # Finance.design_job, Finance.inspection_job
│   └── quotation_model.py      # Finance.quotation, Finance.quotation_item
│
├── dto/                         # Data Transfer Objects
│   ├── base_response.py        # SuccessResponse[T]
│   ├── company_dto.py          # Company DTOs
│   ├── job_dtos.py             # Job DTOs
│   └── quotation_dto.py        # Quotation DTOs
│
├── db/                          # Database Configuration
│   └── supabase/
│       └── engine.py           # Session factory, get_session()
│
└── legacy_dao/                  # Deprecated (archived)
```

---

## Summary

**Architecture Flow:**
```
HTTP Request → Controller (validates via Input DTO)
             → Service (business logic, returns SQLModel)
             → Controller (converts to Output DTO)
             → HTTP Response
```

**Key Benefits:**
- Clean separation between layers
- Type safety throughout the stack
- Direct SQLModel operations (no DAO overhead)
- Accurate OpenAPI schema generation
- Independent evolution of API and database
