"""
DAO (Data Access Object) Package

This package contains all DAOs for database operations following the Repository pattern.

DAOs provide:
- Generic CRUD operations (Create, Read, Update, Delete)
- Type-safe database access via SQLModel
- Query methods for specific use cases
- Transaction management via SQLModel Session
- Separation between business logic (Service layer) and data access (DAO layer)

Architecture:
- BaseDAO: Generic base class with common CRUD operations
- Specific DAOs: Extend BaseDAO with entity-specific query methods

Example usage:
    # Clean imports using __init__.py exports
    from app.dao import BaseDAO, JobDAO, QuotationDAO, InvoiceDAO
    from app.dao import DesignJobDAO, InspectionJobDAO
    from sqlmodel import Session

    with Session(engine) as session:
        # Use specific DAOs for entities
        design_dao = DesignJobDAO(session)
        quotation_dao = QuotationDAO(session)

        # Or create custom DAO from BaseDAO
        class CustomDAO(BaseDAO[MyModel]):
            def __init__(self, session: Session):
                super().__init__(model=MyModel, session=session)

Layer Separation:
- Controller/API → Service → DAO → Database
- DAO handles: SQL queries, ORM operations, database transactions
- Service handles: Business logic, validation, orchestration
- Controller handles: HTTP requests, response formatting, authentication
"""

# Base DAO
from app.dao.base_dao import BaseDAO

# Company DAOs
from app.dao.company_dao import CompanyDAO

# Job DAOs
from app.dao.job_dao import DesignJobDAO, InspectionJobDAO

# Quotation DAOs
from app.dao.quotation_dao import QuotationDAO, QuotationItemDAO

# Invoice DAOs
from app.dao.invoice_dao import InvoiceDAO, InvoiceItemDAO, PaymentRecordDAO


__all__ = [
    # Base DAO
    "BaseDAO",
    # Company DAOs
    "CompanyDAO",
    # Job DAOs
    "DesignJobDAO",
    "InspectionJobDAO",
    # Quotation DAOs
    "QuotationDAO",
    "QuotationItemDAO",
    # Invoice DAOs
    "InvoiceDAO",
    "InvoiceItemDAO",
    "PaymentRecordDAO",
]
