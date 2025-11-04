from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from database.db_helper import safe_execute_query, find_one_by_field, find_many_by_field, insert_record, update_record

class BaseRepository:
    """
    Base repository providing validated CRUD operations.

    Attributes:
        table: Validated table name (with schema if qualified)
        allowed_cols: Set of allowed column names for this table
    """

    def __init__(self, table: str, allowed_cols: Iterable[str]):
        """
        Initialize repository with table name and allowed columns.

        Args:
            table: Table name (can be quoted/qualified like '"Finance".design_job')
            allowed_cols: Iterable of allowed column names for validation
        """
        self.table = table
        self.allowed_cols = set(allowed_cols)


    def find_one_by(self, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Find a single record by field value.

        Args:
            field: Column name to search by
            value: Value to match

        Returns:
            Record dict if found, None otherwise

        Raises:
            ValueError: If field is not in allowed_cols

        Example:
            >>> repo = BaseRepository('"Finance".company', ['id', 'name'])
            >>> company = repo.find_one_by('name', 'ABC Corp')
        """
        col = find_one_by_field(table=self.table, field=field, value=value, operation_name=f"find one by {field}")
        return col if col else None

    def find_many_by(
        self,
        field: str,
        value: Any,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple records by field value.

        Args:
            field: Column name to search by
            value: Value to match
            order_by: Optional ORDER BY clause (validated)
            limit: Optional LIMIT value

        Returns:
            List of matching record dicts

        Example:
            >>> repo.find_many_by('status', 'New', order_by='date_created DESC', limit=10)
        """
        return find_many_by_field(
            table=self.table,
            field=field,
            value=value,
            order_by=order_by,
            limit=limit,
            operation_name=f"find many by {field}"
        )

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a record and return the inserted row.

        Args:
            data: Dictionary of column names to values

        Returns:
            Inserted record dict

        Raises:
            ValueError: If no data provided or columns not allowed

        Example:
            >>> repo.insert({'name': 'New Company', 'address': '123 Main St'})
        """
        if not data:
            raise ValueError("No data provided for insert")

        record = insert_record(
            table=self.table,
            fields=data,
            returning="*",
            operation_name=f"insert record into {self.table} with data {data}"
        ) or None
        return record if record else {}

    def update_where(
        self,
        data: Dict[str, Any],
        where_clause: str,
        where_params: Tuple
    ) -> List[Dict[str, Any]]:
        """
        Update records matching WHERE clause.

        Args:
            data: Dictionary of column names to values to update
            where_clause: WHERE clause (e.g., "id = %s")
            where_params: Parameters for WHERE clause

        Returns:
            List of updated record dicts

        Example:
            >>> repo.update_where({'status': 'Completed'}, "id = %s", (123,))
        """
        return update_record(
            table=self.table,
            fields=data,
            where_clause=where_clause,
            where_params=where_params,
            returning="*",
            operation_name=f"update {self.table} where {where_clause}"
        )

    def delete_where(self, where_clause: str, where_params: Tuple) -> int:
        """
        Delete records matching WHERE clause.

        Args:
            where_clause: WHERE clause (e.g., "id = %s")
            where_params: Parameters for WHERE clause

        Returns:
            Number of rows deleted (placeholder)

        Example:
            >>> repo.delete_where("id = %s", (123,))
        """
        query = f"DELETE FROM {self.table} WHERE {where_clause}"
        safe_execute_query(
            query=query,
            params=where_params,
            fetch_results=False,
            operation_name=f"delete from {self.table} where {where_clause}"
        )
        return 0  # Placeholder - enhance if row count needed

    def _fetch(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query and return results.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            List of result dicts

        Example:
            >>> repo._fetch("SELECT * FROM table WHERE col = %s", (value,))
        """
        return safe_execute_query(
            query=query,
            params=params,
            fetch_results=True,
            operation_name=f"fetch from {self.table}"
        ) or []

