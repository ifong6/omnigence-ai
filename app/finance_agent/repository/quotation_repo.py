"""
Quotation Repository for CRUD operations on Finance.quotation table.

Provides type-safe database operations with validation and business logic.
"""

from typing import Dict, Any, Optional, List
from database.supabase.repo.base import BaseRepository
from database.supabase.db_enum import DBTable_Enum
from app.postgres.supabase.sql.identifiers import validate_columns
from app.finance_agent.models.quotation import QuotationCreate, QuotationUpdate, QuotationRow

# All columns in the quotation table
ALLOWED_COLS = {
    "id",
    "quo_no",
    "date_issued",
    "client_id",
    "project_name",
    "project_item_description",
    "sub_amount",
    "total_amount",
    "currency",
    "revision",
    "quantity",
    "unit"
}


class QuotationRepo(BaseRepository):
    """
    Repository for managing quotations in Finance.quotation table.

    Provides type-safe CRUD operations with business logic.
    """

    def __init__(self):
        """Initialize repository with quotation table."""
        super().__init__(
            table=DBTable_Enum.QUOTATION_TABLE,
            allowed_cols=ALLOWED_COLS
        )

    def create(self, payload: QuotationCreate) -> QuotationRow:
        """
        Create a new quotation record.

        Args:
            payload: Quotation creation data

        Returns:
            Created quotation record

        Example:
            >>> repo = QuotationRepo()
            >>> quotation = repo.create({
            ...     'quo_no': 'Q-JCP-25-01-q1',
            ...     'client_id': 5,
            ...     'project_name': '空調系統設計'
            ... })
        """
        # Filter out None values from TypedDict
        data = {k: v for k, v in payload.items() if v is not None}
        return self.insert(data)

    def update_by_id(self, quotation_id: int, payload: QuotationUpdate) -> Optional[QuotationRow]:
        """
        Update a quotation by its ID.

        Args:
            quotation_id: Quotation ID to update
            payload: Fields to update

        Returns:
            Updated quotation record, or None if not found

        Example:
            >>> repo.update_by_id(5, {'revision': '01'})
        """
        # Filter out None values
        data = {k: v for k, v in payload.items() if v is not None}

        if not data:
            return None

        rows = self.update_where(data, "id = %s", (quotation_id,))
        return rows[0] if rows else None

    def find_by_id(self, quotation_id: int) -> Optional[QuotationRow]:
        """
        Find a quotation by its ID.

        Args:
            quotation_id: Quotation ID to find

        Returns:
            Quotation record if found, None otherwise
        """
        return self.find_one_by("id", quotation_id)

    def find_by_quo_no(self, quo_no: str) -> List[QuotationRow]:
        """
        Find all quotation items by quotation number.

        Multiple items can have the same quo_no (line items).

        Args:
            quo_no: Quotation number (e.g., "Q-JCP-25-01-q1")

        Returns:
            List of quotation records with matching quo_no

        Example:
            >>> repo.find_by_quo_no('Q-JCP-25-01-q1')
        """
        return self.find_many_by("quo_no", quo_no, order_by="id ASC")

    def find_by_client_id(
        self,
        client_id: int,
        limit: Optional[int] = None
    ) -> List[QuotationRow]:
        """
        Find all quotations for a client.

        Args:
            client_id: Client ID
            limit: Optional limit on results

        Returns:
            List of quotation records
        """
        return self.find_many_by(
            "client_id",
            client_id,
            order_by="date_issued DESC",
            limit=limit
        )

    def find_by_project_name(
        self,
        project_name: str,
        limit: Optional[int] = None
    ) -> List[QuotationRow]:
        """
        Find all quotations for a project.

        Args:
            project_name: Project name
            limit: Optional limit on results

        Returns:
            List of quotation records
        """
        return self.find_many_by(
            "project_name",
            project_name,
            order_by="date_issued DESC",
            limit=limit
        )

    def update_items_by_quo_no(
        self,
        quo_no: str,
        payload: QuotationUpdate
    ) -> List[QuotationRow]:
        """
        Update all items with the same quotation number.

        Useful for updating revision or date_issued for all line items.

        Args:
            quo_no: Quotation number
            payload: Fields to update

        Returns:
            List of updated quotation records

        Example:
            >>> repo.update_items_by_quo_no('Q-JCP-25-01-q1', {'revision': '02'})
        """
        data = {k: v for k, v in payload.items() if v is not None}

        if not data:
            return []

        return self.update_where(data, "quo_no = %s", (quo_no,))

    def delete_by_quo_no(self, quo_no: str) -> int:
        """
        Delete all items with the same quotation number.

        Args:
            quo_no: Quotation number

        Returns:
            Number of rows deleted (placeholder - enhance if needed)
        """
        return self.delete_where("quo_no = %s", (quo_no,))

    def find_all(
        self,
        order_by: str = "date_issued DESC",
        limit: Optional[int] = None
    ) -> List[QuotationRow]:
        """
        Find all quotations.

        Args:
            order_by: ORDER BY clause
            limit: Optional limit

        Returns:
            List of all quotation records
        """
        # Validate order_by column
        order_col = order_by.split()[0]
        validate_columns([order_col], self.allowed_cols)

        query = f'SELECT * FROM {self.table} ORDER BY {order_by}'

        if limit:
            query += f' LIMIT {limit}'

        return self._fetch(query)

    def get_total_by_quo_no(self, quo_no: str) -> Dict[str, Any]:
        """
        Calculate total amounts for a quotation number.

        Sums all line items for the given quo_no.

        Args:
            quo_no: Quotation number

        Returns:
            Dict with sum of total_amount and count of items

        Example:
            >>> repo.get_total_by_quo_no('Q-JCP-25-01-q1')
            {'total': Decimal('25000.00'), 'item_count': 3}
        """
        query = f"""
            SELECT
                SUM(total_amount) as total,
                COUNT(*) as item_count
            FROM {self.table}
            WHERE quo_no = %s
        """

        rows = self._fetch(query, (quo_no,))
        if rows:
            return dict(rows[0])
        return {'total': 0, 'item_count': 0}
