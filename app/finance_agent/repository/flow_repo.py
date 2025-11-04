from typing import Dict, Any, Optional, List
from uuid import UUID
from database.supabase.repo.base import BaseRepository
from database.supabase.db_enum import DBTable_Enum
from app.postgres.supabase.sql.identifiers import validate_columns
from app.finance_agent.models.flow import FlowCreate, FlowUpdate, FlowRow

# All columns in the flow table
ALLOWED_COLS = {
    "id",
    "session_id",
    "user_request_summary",
    "created_at",
    "identified_agents"
}


class FlowRepo(BaseRepository):
    def __init__(self):
        """Initialize repository with flow table."""
        super().__init__(
            table=DBTable_Enum.FLOW_TABLE,
            allowed_cols=ALLOWED_COLS
        )

    def create(self, payload: FlowCreate) -> FlowRow:
        """
        Create a new flow log entry.

        Args:
            payload: Flow creation data (must include id and session_id)

        Returns:
            Created flow record as FlowRow with all required fields

        Example:
            >>> from uuid import uuid4
            >>> repo = FlowRepo()
            >>> flow = repo.create({
            ...     'id': uuid4(),
            ...     'session_id': uuid4(),
            ...     'user_request_summary': 'Create quotation',
            ...     'identified_agents': 'finance_agent'
            ... })
        """
        # Convert UUID objects to strings for psycopg2 compatibility
        data = {
            k: (str(v) if isinstance(v, UUID) else v)
            for k, v in payload.items()
            if v is not None
        }
        result = self.insert(data)

        # Construct properly typed FlowRow from database result
        # This ensures all required keys are present and properly typed
        return FlowRow(
            id=result['id'],
            session_id=result['session_id'],
            created_at=result['created_at'],
            user_request_summary=result.get('user_request_summary'),
            identified_agents=result.get('identified_agents')
        )

    def update_by_id(self, flow_id: UUID, payload: FlowUpdate) -> Optional[FlowRow]:
        """
        Update a flow log by its ID.

        Args:
            flow_id: Flow UUID to update
            payload: Fields to update

        Returns:
            Updated flow record, or None if not found

        Example:
            >>> repo.update_by_id(flow_uuid, {
            ...     'user_request_summary': 'Updated summary'
            ... })
        """
        # Filter out None values
        data = {k: v for k, v in payload.items() if v is not None}

        if not data:
            return None

        # Convert UUID to string for psycopg2 compatibility
        rows = self.update_where(data, "id = %s", (str(flow_id),))
        return rows[0] if rows else None  # type: ignore[return-value]

    def find_by_id(self, flow_id: UUID) -> Optional[FlowRow]:
        """
        Find a flow log by its ID.

        Args:
            flow_id: Flow UUID to find

        Returns:
            Flow record if found, None otherwise
        """
        # Convert UUID to string for psycopg2 compatibility
        return self.find_one_by("id", str(flow_id))  # type: ignore[return-value]

    def find_by_session_id(
        self,
        session_id: UUID,
        order_by: str = "created_at DESC",
        limit: Optional[int] = None
    ) -> List[FlowRow]:
        """
        Find all flow logs for a session.

        Args:
            session_id: Session UUID
            order_by: ORDER BY clause (default: newest first)
            limit: Optional limit on results

        Returns:
            List of flow records for the session

        Example:
            >>> repo.find_by_session_id(session_uuid, limit=10)
        """
        # Convert UUID to string for psycopg2 compatibility
        return self.find_many_by(  # type: ignore[return-value]
            "session_id",
            str(session_id),
            order_by=order_by,
            limit=limit
        )

    def find_recent(
        self,
        limit: int = 100
    ) -> List[FlowRow]:
        """
        Find recent flow logs.

        Args:
            limit: Maximum number of results (default: 100)

        Returns:
            List of recent flow records

        Example:
            >>> repo.find_recent(limit=50)
        """
        query = f"""
            SELECT * FROM {self.table}
            ORDER BY created_at DESC
            LIMIT {limit}
        """

        return self._fetch(query)  # type: ignore[return-value]

    def search_by_summary(
        self,
        search_term: str,
        limit: Optional[int] = 50
    ) -> List[FlowRow]:
        """
        Search flow logs by user_request_summary using ILIKE.

        Args:
            search_term: Search term (will be wrapped with % for partial matching)
            limit: Maximum number of results

        Returns:
            List of matching flow records

        Example:
            >>> repo.search_by_summary('quotation')
        """
        query = f"""
            SELECT * FROM {self.table}
            WHERE user_request_summary ILIKE %s
            ORDER BY created_at DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        pattern = f"%{search_term}%"
        return self._fetch(query, (pattern,))  # type: ignore[return-value]

    def search_by_agent(
        self,
        agent_name: str,
        limit: Optional[int] = 50
    ) -> List[FlowRow]:
        """
        Search flow logs by identified agent name.

        Args:
            agent_name: Agent name to search for
            limit: Maximum number of results

        Returns:
            List of matching flow records

        Example:
            >>> repo.search_by_agent('finance_agent')
        """
        query = f"""
            SELECT * FROM {self.table}
            WHERE identified_agents ILIKE %s
            ORDER BY created_at DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        pattern = f"%{agent_name}%"
        return self._fetch(query, (pattern,))  # type: ignore[return-value]

    def delete_by_id(self, flow_id: UUID) -> int:
        """
        Delete a flow log by its ID.

        Args:
            flow_id: Flow UUID to delete

        Returns:
            Number of rows deleted (placeholder)
        """
        # Convert UUID to string for psycopg2 compatibility
        return self.delete_where("id = %s", (str(flow_id),))

    def delete_old_logs(self, days: int = 30) -> int:
        """
        Delete flow logs older than specified days.

        Args:
            days: Number of days to retain (default: 30)

        Returns:
            Number of rows deleted (placeholder)

        Example:
            >>> repo.delete_old_logs(days=90)  # Keep last 90 days
        """
        query = f"""
            DELETE FROM {self.table}
            WHERE created_at < NOW() - INTERVAL '{days} days'
        """

        self._fetch(query)
        return 0  # Placeholder - enhance if row count needed
