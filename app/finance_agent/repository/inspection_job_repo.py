"""
Inspection Job Repository for CRUD operations on Finance.inspection_job table.

Provides type-safe database operations with validation and business logic.
"""

from typing import Dict, Any, Optional, List
from database.supabase.repo.base import BaseRepository
from database.supabase.db_enum import DBTable_Enum
from app.postgres.supabase.sql.identifiers import validate_columns
from app.finance_agent.models.job import JobCreate, JobUpdate, JobRow

# All columns in the inspection_job table
# Note: "type" column removed as it doesn't exist in DB (table name indicates job type)
ALLOWED_COLS = {
    "id",
    "company_id",
    "title",
    "status",
    "job_no",
    "date_created",
    "quotation_status",
    "quotation_issued_at"
}


class InspectionJobRepo(BaseRepository):
    """
    Repository for managing INSPECTION jobs in Finance.inspection_job table.

    Provides type-safe CRUD operations with business logic like upserts.
    """

    def __init__(self):
        """Initialize repository with inspection_job table."""
        super().__init__(
            table=DBTable_Enum.INSPECTION_JOB_TABLE,
            allowed_cols=ALLOWED_COLS
        )

    def create(self, payload: JobCreate) -> JobRow:
        """
        Create a new inspection job.

        Args:
            payload: Job creation data

        Returns:
            Created job record as JobRow with all required fields

        Example:
            >>> repo = InspectionJobRepo()
            >>> job = repo.create({
            ...     'company_id': 1,
            ...     'title': 'Safety Inspection'
            ... })
        """
        # Filter out None values from TypedDict
        data = {k: v for k, v in payload.items() if v is not None}
        result = self.insert(data)

        # Construct properly typed JobRow from database result
        # This ensures all required keys are present and properly typed
        return JobRow(
            id=result['id'],
            company_id=result['company_id'],
            title=result['title'],
            status=result['status'],
            job_no=result.get('job_no'),
            date_created=result['date_created'],
            quotation_status=result.get('quotation_status'),
            quotation_issued_at=result.get('quotation_issued_at')
        )

    def update_by_id(self, job_id: int, payload: JobUpdate) -> Optional[JobRow]:
        """
        Update a job by its ID.

        Args:
            job_id: Job ID to update
            payload: Fields to update

        Returns:
            Updated job record, or None if not found

        Example:
            >>> repo.update_by_id(5, {'status': 'Completed'})
        """
        # Filter out None values
        data = {k: v for k, v in payload.items() if v is not None}

        if not data:
            return None

        rows = self.update_where(data, "id = %s", (job_id,))
        return rows[0] if rows else None

    def find_by_id(self, job_id: int) -> Optional[JobRow]:
        """
        Find a job by its ID.

        Args:
            job_id: Job ID to find

        Returns:
            Job record if found, None otherwise
        """
        return self.find_one_by("id", job_id)

    def find_by_job_no(self, job_no: str) -> Optional[JobRow]:
        """
        Find a job by its job number.

        Args:
            job_no: Job number (e.g., "JICP-25-01-1")

        Returns:
            Job record if found, None otherwise

        Example:
            >>> repo.find_by_job_no('JICP-25-01-1')
        """
        return self.find_one_by("job_no", job_no)

    def find_by_company_id(
        self,
        company_id: int,
        limit: Optional[int] = None
    ) -> List[JobRow]:
        """
        Find all jobs for a company.

        Args:
            company_id: Company ID
            limit: Optional limit on results

        Returns:
            List of job records
        """
        return self.find_many_by(
            "company_id",
            company_id,
            order_by="date_created DESC",
            limit=limit
        )

    def upsert_by_job_no(self, data: Dict[str, Any]) -> JobRow:
        """
        Insert or update a job based on job_no conflict.

        If job_no already exists, updates all fields except job_no and status.
        This preserves the job status on conflict while updating other fields.

        Args:
            data: Job data including job_no

        Returns:
            Upserted job record

        Raises:
            ValueError: If job_no not provided

        Example:
            >>> repo.upsert_by_job_no({
            ...     'job_no': 'JICP-25-01-1',
            ...     'company_id': 1,
            ...     'title': 'Updated Title',
            ...     'status': 'New'
            ... })
        """
        if 'job_no' not in data:
            raise ValueError("job_no is required for upsert_by_job_no")

        cols = validate_columns(list(data.keys()), self.allowed_cols)
        vals = [data[c] for c in cols]
        placeholders = ", ".join(["%s"] * len(cols))

        # Update all provided columns except 'job_no' and 'status' on conflict
        update_cols = [c for c in cols if c not in {"job_no", "status"}]

        # If no update columns, just update job_no to itself (no-op but valid SQL)
        update_sql = ", ".join([f'{c}=EXCLUDED.{c}' for c in update_cols]) or "job_no=EXCLUDED.job_no"

        query = f'''
            INSERT INTO {self.table} ({", ".join(cols)})
            VALUES ({placeholders})
            ON CONFLICT (job_no) DO UPDATE SET {update_sql}
            RETURNING *
        '''

        return self._fetch(query, vals)[0]

    def find_all(
        self,
        order_by: str = "date_created DESC",
        limit: Optional[int] = None
    ) -> List[JobRow]:
        """
        Find all inspection jobs.

        Args:
            order_by: ORDER BY clause
            limit: Optional limit

        Returns:
            List of all job records
        """
        # Validate order_by column
        order_col = order_by.split()[0]
        validate_columns([order_col], self.allowed_cols)

        query = f'SELECT * FROM {self.table} ORDER BY {order_by}'

        if limit:
            query += f' LIMIT {limit}'

        return self._fetch(query)
