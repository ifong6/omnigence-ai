# app/repos/orm_base_repository.py
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlmodel import SQLModel, Session, select

ModelT = TypeVar("ModelT", bound=SQLModel)

class OrmBaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT], session: Session):
        self.model = model
        self.session = session

    # --- Read ---
    def get(self, pk: Any) -> Optional[ModelT]:
        return self.session.get(self.model, pk)

    def find_one_by(self, **filters) -> Optional[ModelT]:
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
        stmt = select(self.model).filter_by(**filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        return list(self.session.exec(stmt))

    def list_all(self, *args, limit: Optional[int] = None, **kwargs) -> List[ModelT]:
        """
        List all records, optionally with a limit.

        Args:
            *args: Ignored (for compatibility with test code)
            limit: Optional limit on number of results
            **kwargs: Additional filters

        Returns:
            List of model instances
        """
        stmt = select(self.model)
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt))

    # --- Write ---
    def create(self, **data) -> ModelT:
        obj = self.model(**data)
        self.session.add(obj)
        self.session.flush()  # 拿自增/默認列
        return obj

    def update(self, pk: Any, **data) -> Optional[ModelT]:
        obj = self.get(pk)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.session.flush()
        return obj

    def delete(self, pk: Any) -> bool:
        obj = self.get(pk)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.flush()
        return True
