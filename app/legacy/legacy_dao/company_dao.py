"""
Company DAO for CRUD operations on Finance.company table.

Provides type-safe database operations for company records with specialized
query methods including case-insensitive name matching and search functionality.
"""

from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy import func, or_
from app.dao.base_dao import BaseDAO
from app.models.company_models import Company, CompanyCreate, CompanyUpdate


class CompanyDAO(BaseDAO[Company]):
    """
    DAO for managing companies in Finance.company table.

    Handles all database operations for company records including:
    - Company creation and updates
    - Case-insensitive name matching
    - Search by name or alias
    - Listing companies with pagination

    Example:
        >>> from sqlmodel import Session
        >>> with Session(engine) as session:
        ...     dao = CompanyDAO(session)
        ...     company = dao.create(
        ...         name="澳門科技大學",
        ...         address="澳門氹仔偉龍馬路",
        ...         phone="+853 8897 1111"
        ...     )
    """

    def __init__(self, session: Session):
        """
        Initialize DAO with database session.

        Args:
            session: Active SQLModel database session
        """
        super().__init__(model=Company, session=session)

    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================

    def get_by_name(self, name: str) -> Optional[Company]:
        """
        Get company by exact name match (case-sensitive).

        Args:
            name: Company name

        Returns:
            Company if found, None otherwise

        Example:
            >>> company = dao.get_by_name("澳門科技大學")
        """
        return self.find_one_by(name=name)

    def get_by_name_ci(self, name: str) -> Optional[Company]:
        """
        Get company by case-insensitive and whitespace-insensitive name match.

        This aligns with the database's functional unique index:
        lower(trim(name))

        Args:
            name: Company name (will be lowercased and trimmed)

        Returns:
            Company if found, None otherwise

        Example:
            >>> # Finds "澳門科技大學" even if searching for "  澳門科技大學  "
            >>> company = dao.get_by_name_ci("  澳門科技大學  ")
        """
        stmt = (
            select(Company)
            .where(func.lower(func.trim(Company.name)) == func.lower(func.trim(name)))
            .limit(1)
        )
        return self.session.exec(stmt).first()

    def search_by_name_or_alias(
        self,
        term: str,
        limit: int = 10,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[Company]:
        """
        Search companies by name or alias using case-insensitive ILIKE.

        Args:
            term: Search term (will be wrapped with % wildcards)
            limit: Maximum number of results (default: 10)
            offset: Number of results to skip (default: 0)
            order_desc: Sort by ID descending (default: True)

        Returns:
            List of matching Company instances

        Example:
            >>> # Search for companies with "科大" in name or alias
            >>> companies = dao.search_by_name_or_alias("科大", limit=5)
        """
        ilike_pattern = f"%{term}%"
        stmt = (
            select(Company)
            .where(
                or_(
                    Company.name.ilike(ilike_pattern),  # type: ignore
                    Company.alias.ilike(ilike_pattern)  # type: ignore
                )
            )
        )

        # Sort by ID (Company has no created_at field)
        stmt = stmt.order_by(
            Company.id.desc() if order_desc else Company.id.asc()  # type: ignore
        )

        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_desc: bool = True,
    ) -> List[Company]:
        """
        Get all companies with pagination.

        Args:
            limit: Maximum number of results (optional)
            offset: Number of results to skip (default: 0)
            order_desc: Sort by ID descending (default: True)

        Returns:
            List of all Company instances

        Example:
            >>> # Get first 20 companies, newest first
            >>> companies = dao.get_all(limit=20, order_desc=True)
        """
        stmt = select(Company)

        # Sort by ID
        stmt = stmt.order_by(
            Company.id.desc() if order_desc else Company.id.asc()  # type: ignore
        )

        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return list(self.session.exec(stmt).all())

    # ========================================================================
    # SPECIALIZED OPERATIONS
    # ========================================================================

    def get_or_create(
        self,
        name: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        alias: Optional[str] = None,
    ) -> tuple[Company, bool]:
        """
        Get existing company by name or create new one.

        Uses case-insensitive name matching.

        Args:
            name: Company name (required)
            address: Company address (optional)
            phone: Company phone (optional)
            alias: Company alias (optional)

        Returns:
            Tuple of (Company instance, created: bool)
            - created=True if new company was created
            - created=False if existing company was returned

        Example:
            >>> company, created = dao.get_or_create(
            ...     name="澳門科技大學",
            ...     address="澳門氹仔偉龍馬路"
            ... )
            >>> if created:
            ...     print("Created new company")
            ... else:
            ...     print("Found existing company")
        """
        # Try to find existing company (case-insensitive)
        existing = self.get_by_name_ci(name)
        if existing:
            return existing, False

        # Create new company
        company = self.create(
            name=name,
            address=address,
            phone=phone,
            alias=alias
        )
        return company, True

    def update_contact_info(
        self,
        company_id: int,
        address: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Optional[Company]:
        """
        Convenience method to update only contact information.

        Args:
            company_id: Company ID to update
            address: New address (optional)
            phone: New phone (optional)

        Returns:
            Updated Company if found, None otherwise

        Example:
            >>> updated = dao.update_contact_info(
            ...     company_id=123,
            ...     address="新地址",
            ...     phone="+853 1234 5678"
            ... )
        """
        # Build update dict with only provided values
        update_data = {}
        if address is not None:
            update_data["address"] = address
        if phone is not None:
            update_data["phone"] = phone

        if not update_data:
            # Nothing to update
            return self.get(company_id)

        return self.update(company_id, **update_data)

    def update_alias(
        self,
        company_id: int,
        alias: str,
    ) -> Optional[Company]:
        """
        Convenience method to update only the alias.

        Args:
            company_id: Company ID to update
            alias: New alias

        Returns:
            Updated Company if found, None otherwise

        Example:
            >>> updated = dao.update_alias(company_id=123, alias="澳科大")
        """
        return self.update(company_id, alias=alias)

    # ========================================================================
    # AGGREGATE OPERATIONS
    # ========================================================================

    def count_by_name_pattern(self, pattern: str) -> int:
        """
        Count companies matching a name/alias pattern.

        Args:
            pattern: Search pattern (will be wrapped with % wildcards)

        Returns:
            Count of matching companies

        Example:
            >>> count = dao.count_by_name_pattern("科大")
            >>> print(f"Found {count} companies matching '科大'")
        """
        ilike_pattern = f"%{pattern}%"
        stmt = (
            select(func.count(Company.id))  # type: ignore
            .where(
                or_(
                    Company.name.ilike(ilike_pattern),  # type: ignore
                    Company.alias.ilike(ilike_pattern)  # type: ignore
                )
            )
        )
        result = self.session.exec(stmt).first()
        return result or 0

    def exists_by_name_ci(self, name: str) -> bool:
        """
        Check if company exists with given name (case-insensitive).

        Args:
            name: Company name to check

        Returns:
            True if company exists, False otherwise

        Example:
            >>> if dao.exists_by_name_ci("澳門科技大學"):
            ...     print("Company already exists")
        """
        company = self.get_by_name_ci(name)
        return company is not None
