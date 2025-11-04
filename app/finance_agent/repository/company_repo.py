"""
Company Repository for CRUD operations on Finance.company table.

Provides type-safe database operations with validation and business logic.
"""

from typing import Dict, Any, Optional, List
from database.supabase.repo.base import BaseRepository
from database.supabase.db_enum import DBTable_Enum
from app.postgres.supabase.sql.identifiers import validate_columns
from app.finance_agent.models.company import CompanyCreate, CompanyUpdate, CompanyRow

# All columns in the company table
ALLOWED_COLS = {
    "id",
    "name",
    "alias",
    "address",
    "phone"
}


class CompanyRepo(BaseRepository):
    """
    Repository for managing companies in Finance.company table.

    Provides type-safe CRUD operations with business logic like upserts.
    """

    def __init__(self):
        """Initialize repository with company table."""
        super().__init__(
            table=DBTable_Enum.COMPANY_TABLE,
            allowed_cols=ALLOWED_COLS
        )

    def create(self, payload: CompanyCreate) -> CompanyRow:
        """
        Create a new company.

        Args:
            payload: Company creation data

        Returns:
            Created company record

        Example:
            >>> repo = CompanyRepo()
            >>> company = repo.create({
            ...     'name': '澳門科技大學',
            ...     'address': 'Macau',
            ...     'phone': '853-1234-5678'
            ... })
        """
        # Filter out None values from TypedDict
        data = {k: v for k, v in payload.items() if v is not None}
        return self.insert(data)

    def update_by_id(self, company_id: int, payload: CompanyUpdate) -> Optional[CompanyRow]:
        """
        Update a company by its ID.

        Args:
            company_id: Company ID to update
            payload: Fields to update

        Returns:
            Updated company record, or None if not found

        Example:
            >>> repo.update_by_id(5, {'alias': '科大'})
        """
        # Filter out None values
        data = {k: v for k, v in payload.items() if v is not None}

        if not data:
            return None

        rows = self.update_where(data, "id = %s", (company_id,))
        return rows[0] if rows else None

    def update_by_name(self, name: str, payload: CompanyUpdate) -> Optional[CompanyRow]:
        """
        Update a company by its name.

        Args:
            name: Company name
            payload: Fields to update

        Returns:
            Updated company record, or None if not found
        """
        data = {k: v for k, v in payload.items() if v is not None}

        if not data:
            return None

        rows = self.update_where(data, "name = %s", (name,))
        return rows[0] if rows else None

    def find_by_id(self, company_id: int) -> Optional[CompanyRow]:
        """
        Find a company by its ID.

        Args:
            company_id: Company ID to find

        Returns:
            Company record if found, None otherwise
        """
        return self.find_one_by("id", company_id)

    def find_by_name(self, name: str) -> Optional[CompanyRow]:
        """
        Find a company by its name.

        Args:
            name: Company name (exact match)

        Returns:
            Company record if found, None otherwise

        Example:
            >>> repo.find_by_name('澳門科技大學')
        """
        return self.find_one_by("name", name)

    def find_by_alias(self, alias: str) -> Optional[CompanyRow]:
        """
        Find a company by its alias.

        Args:
            alias: Company alias (exact match)

        Returns:
            Company record if found, None otherwise

        Example:
            >>> repo.find_by_alias('科大')
        """
        return self.find_one_by("alias", alias)

    def search_by_name(self, search_term: str, limit: Optional[int] = 10) -> List[CompanyRow]:
        """
        Search companies by name using ILIKE pattern matching.

        Args:
            search_term: Search term (will be wrapped with % for partial matching)
            limit: Maximum number of results

        Returns:
            List of matching company records

        Example:
            >>> repo.search_by_name('科技')  # Finds '澳門科技大學', etc.
        """
        query = f"""
            SELECT * FROM {self.table}
            WHERE name ILIKE %s OR alias ILIKE %s
            ORDER BY name
        """

        if limit:
            query += f" LIMIT {limit}"

        pattern = f"%{search_term}%"
        return self._fetch(query, (pattern, pattern))

    def find_all(
        self,
        order_by: str = "name ASC",
        limit: Optional[int] = None
    ) -> List[CompanyRow]:
        """
        Find all companies.

        Args:
            order_by: ORDER BY clause
            limit: Optional limit

        Returns:
            List of all company records
        """
        # Validate order_by column
        order_col = order_by.split()[0]
        validate_columns([order_col], self.allowed_cols)

        query = f'SELECT * FROM {self.table} ORDER BY {order_by}'

        if limit:
            query += f' LIMIT {limit}'

        return self._fetch(query)

    def upsert_by_name(self, data: Dict[str, Any]) -> CompanyRow:
        """
        Insert or update a company based on name conflict.

        If name already exists, updates all fields except name.

        Args:
            data: Company data including name

        Returns:
            Upserted company record

        Raises:
            ValueError: If name not provided

        Example:
            >>> repo.upsert_by_name({
            ...     'name': 'ABC Company',
            ...     'address': 'New Address',
            ...     'phone': '123-456'
            ... })
        """
        if 'name' not in data:
            raise ValueError("name is required for upsert_by_name")

        cols = validate_columns(list(data.keys()), self.allowed_cols)
        vals = [data[c] for c in cols]
        placeholders = ", ".join(["%s"] * len(cols))

        # Update all provided columns except 'name' on conflict
        update_cols = [c for c in cols if c != "name"]

        # If no update columns, just update name to itself (no-op but valid SQL)
        update_sql = ", ".join([f'{c}=EXCLUDED.{c}' for c in update_cols]) or "name=EXCLUDED.name"

        query = f'''
            INSERT INTO {self.table} ({", ".join(cols)})
            VALUES ({placeholders})
            ON CONFLICT (name) DO UPDATE SET {update_sql}
            RETURNING *
        '''

        return self._fetch(query, vals)[0]
