"""
Base DAO (Data Access Object) for generic CRUD operations.

Provides a generic repository pattern for SQLModel entities with common
database operations like create, read, update, delete, and query.

This follows the Repository/DAO pattern where:
- DAO/Repository handles database access (ORM operations)
- Service layer handles business logic
- Controller layer handles HTTP/API logic
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Sequence
from sqlmodel import SQLModel, Session, select
from sqlalchemy import desc

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseDAO(Generic[ModelT]):
    """
    Generic base DAO providing CRUD operations for any SQLModel entity.

    This class uses generics to provide type-safe database operations
    without code duplication.

    Example:
        >>> class CompanyDAO(BaseDAO[Company]):
        ...     def __init__(self, session: Session):
        ...         super().__init__(model=Company, session=session)
        ...
        ...     def get_by_name(self, name: str) -> Optional[Company]:
        ...         return self.find_one_by(name=name)
    """

    def __init__(self, model: Type[ModelT], session: Session):
        """
        Initialize DAO with model type and database session.

        Args:
            model: SQLModel class (e.g., Company, Job, Quotation)
            session: Active SQLModel database session
        """
        self.model = model
        self.session = session

    # ========================================================================
    # READ OPERATIONS
    # ========================================================================

    def get(self, pk: Any) -> Optional[ModelT]:
        """
        Get a single record by primary key.

        Args:
            pk: Primary key value

        Returns:
            Model instance if found, None otherwise

        Example:
            >>> company = dao.get(123)
        """
        return self.session.get(self.model, pk)

    def find_one_by(self, **filters) -> Optional[ModelT]:
        """
        Find a single record matching the given filters.

        Args:
            **filters: Field=value pairs to filter by

        Returns:
            First matching model instance, or None

        Example:
            >>> company = dao.find_one_by(name="ACME Corp")
            >>> job = dao.find_one_by(job_no="JCP-25-01-1")
        """
        stmt = select(self.model).filter_by(**filters).limit(1)
        return self.session.exec(stmt).first()

    def find_many_by(
        self,
        *,
        order_by=None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters,
    ) -> List[ModelT]:
        """
        Find multiple records matching the given filters.

        Args:
            order_by: SQLAlchemy order_by expression (optional)
            limit: Maximum number of results (optional)
            offset: Number of results to skip (optional)
            **filters: Field=value pairs to filter by

        Returns:
            List of matching model instances

        Example:
            >>> jobs = dao.find_many_by(
            ...     company_id=123,
            ...     status="COMPLETED",
            ...     limit=10,
            ...     order_by=Job.date_created.desc()
            ... )
        """
        stmt = select(self.model).filter_by(**filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        return list(self.session.exec(stmt).all())

    def list_all(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by=None,
        **filters
    ) -> List[ModelT]:
        """
        List all records with optional filters, ordering, and pagination.

        Args:
            limit: Maximum number of results (optional)
            offset: Number of results to skip (optional)
            order_by: SQLAlchemy order_by expression (optional)
            **filters: Additional field=value filters (optional)

        Returns:
            List of all model instances

        Example:
            >>> # Get all records
            >>> all_companies = dao.list_all()
            >>>
            >>> # Get first 10 records
            >>> recent_jobs = dao.list_all(limit=10, order_by=desc("date_created"))
        """
        stmt = select(self.model)

        # Apply filters if provided
        if filters:
            stmt = stmt.filter_by(**filters)

        # Apply ordering
        if order_by is not None:
            stmt = stmt.order_by(order_by)

        # Apply pagination
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        return list(self.session.exec(stmt).all())

    def count(self, **filters) -> int:
        """
        Count records matching the given filters.

        Args:
            **filters: Field=value pairs to filter by

        Returns:
            Number of matching records

        Example:
            >>> total = dao.count()
            >>> active_jobs = dao.count(status="IN_PROGRESS")
        """
        stmt = select(self.model).filter_by(**filters)
        results = self.session.exec(stmt).all()
        return len(results)

    def exists(self, **filters) -> bool:
        """
        Check if any record exists matching the given filters.

        Args:
            **filters: Field=value pairs to filter by

        Returns:
            True if at least one record exists, False otherwise

        Example:
            >>> if dao.exists(job_no="JCP-25-01-1"):
            ...     print("Job already exists")
        """
        return self.find_one_by(**filters) is not None

    # ========================================================================
    # WRITE OPERATIONS
    # ========================================================================

    def create(self, **data) -> ModelT:
        """
        Create a new record.

        Args:
            **data: Field=value pairs for the new record

        Returns:
            Created model instance with auto-generated fields populated

        Example:
            >>> company = dao.create(
            ...     name="ACME Corp",
            ...     address="123 Main St"
            ... )
        """
        instance = self.model(**data)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def create_many(self, instances: List[ModelT]) -> List[ModelT]:
        """
        Create multiple records in a single transaction.

        Args:
            instances: List of model instances to create

        Returns:
            List of created instances with auto-generated fields populated

        Example:
            >>> items = [
            ...     QuotationItem(item_desc="Item 1", quantity=1, unit_price=100),
            ...     QuotationItem(item_desc="Item 2", quantity=2, unit_price=200),
            ... ]
            >>> created_items = dao.create_many(items)
        """
        for instance in instances:
            self.session.add(instance)
        self.session.commit()
        for instance in instances:
            self.session.refresh(instance)
        return instances

    def update(self, pk: Any, **data) -> Optional[ModelT]:
        """
        Update a record by primary key.

        Args:
            pk: Primary key value
            **data: Field=value pairs to update

        Returns:
            Updated model instance if found, None otherwise

        Example:
            >>> updated_job = dao.update(
            ...     pk=123,
            ...     status="COMPLETED",
            ...     quotation_status="ACCEPTED"
            ... )
        """
        instance = self.get(pk)
        if not instance:
            return None

        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def update_many(self, instances: List[ModelT]) -> List[ModelT]:
        """
        Update multiple records in a single transaction.

        Args:
            instances: List of model instances to update

        Returns:
            List of updated instances

        Example:
            >>> jobs = dao.find_many_by(status="NEW")
            >>> for job in jobs:
            ...     job.status = "IN_PROGRESS"
            >>> updated_jobs = dao.update_many(jobs)
        """
        for instance in instances:
            self.session.add(instance)
        self.session.commit()
        for instance in instances:
            self.session.refresh(instance)
        return instances

    def delete(self, pk: Any) -> bool:
        """
        Delete a record by primary key.

        Args:
            pk: Primary key value

        Returns:
            True if record was deleted, False if not found

        Example:
            >>> success = dao.delete(123)
            >>> if success:
            ...     print("Job deleted")
        """
        instance = self.get(pk)
        if not instance:
            return False

        self.session.delete(instance)
        self.session.commit()
        return True

    def delete_many(self, **filters) -> int:
        """
        Delete multiple records matching the given filters.

        Args:
            **filters: Field=value pairs to filter records to delete

        Returns:
            Number of records deleted

        Example:
            >>> deleted_count = dao.delete_many(status="CANCELLED")
            >>> print(f"Deleted {deleted_count} cancelled jobs")
        """
        instances = self.find_many_by(**filters)
        count = len(instances)

        for instance in instances:
            self.session.delete(instance)

        self.session.commit()
        return count

    # ========================================================================
    # UTILITY OPERATIONS
    # ========================================================================

    def refresh(self, instance: ModelT) -> ModelT:
        """
        Refresh an instance from the database.

        Args:
            instance: Model instance to refresh

        Returns:
            Refreshed instance with latest data from database

        Example:
            >>> job = dao.get(123)
            >>> # ... some time passes, data might have changed ...
            >>> fresh_job = dao.refresh(job)
        """
        self.session.refresh(instance)
        return instance

    def execute_query(self, stmt) -> Sequence[Any]:
        """
        Execute a raw SQLAlchemy select statement.

        Args:
            stmt: SQLAlchemy select statement

        Returns:
            Query results as sequence

        Example:
            >>> from sqlalchemy import func
            >>> stmt = select(func.count(Company.id))
            >>> result = dao.execute_query(stmt)
        """
        return self.session.exec(stmt).all()
