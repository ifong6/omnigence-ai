from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from sqlmodel import Session
from app.models.company_models import Company


class CompanyService(ABC):
    """
    Abstract base class for managing company-related business logic.
    Uses SQLModel sessions for transactional operations.
    """

    def __init__(self, session: Session):
        """
        Initialize service with a SQLModel session.

        Args:
            session: Active SQLModel session for database operations
        """
        self.session = session

    @abstractmethod
    def get_or_create(
        self,
        *,
        name: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        alias: Optional[str] = None
    ) -> Company:
        """Get existing company by name or create new one."""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Company]:
        """Get company by exact name match."""
        pass

    @abstractmethod
    def get_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID."""
        pass

    @abstractmethod
    def create(
        self,
        *,
        name: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        alias: Optional[str] = None
    ) -> Company:
        """Create a new company."""
        pass

    @abstractmethod
    def update(
        self,
        company_id: int,
        *,
        name: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        alias: Optional[str] = None
    ) -> Optional[Company]:
        """Update an existing company."""
        pass

    @abstractmethod
    def search_by_name(self, search_term: str, limit: int = 10) -> list[Company]:
        """Search companies by name or alias."""
        pass

    @abstractmethod
    def list_all(self, limit: Optional[int] = None) -> list[Company]:
        """Get all companies."""
        pass

    @abstractmethod
    def create_with_contact_enrichment(
        self,
        *,
        name: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        google_search_fn=None
    ) -> dict:
        """Create or update company with contact info auto-enrichment."""
        pass

    @abstractmethod
    def generate_alias_with_llm(
        self,
        company_id: int,
        llm_fn
    ) -> dict:
        """Generate and assign an intelligent alias using LLM."""
        pass
