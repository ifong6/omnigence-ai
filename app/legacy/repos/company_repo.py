# from typing import List, Optional
# from sqlmodel import Session, select
# from sqlalchemy import func
# from app.models.company_models import Company
# from app.finance_agent.repos.base_repo import OrmBaseRepository


# class CompanyRepo(OrmBaseRepository[Company]):
#     """
#     ORM repository for Finance.company.
#     - 依賴 OrmBaseRepository 提供的通用 CRUD（create/update/delete/get/find_*）
#     - 這裡只放 Company 專屬的查詢或便捷方法
#     """

#     def __init__(self, session: Session):
#         super().__init__(Company, session)

#     # --- Specialized Queries -------------------------------------------------

#     def get_by_name_ci(self, name: str) -> Optional[Company]:
#         """
#         Case/space-insensitive exact match for 'name'.
#         與 DB 端 functional unique index (lower(trim(name))) 對齊。
#         """
#         stmt = (
#             select(Company)
#             .where(func.lower(func.trim(Company.name)) == func.lower(func.trim(name)))
#             .limit(1)
#         )
#         return self.session.exec(stmt).first()

#     def search_by_name_or_alias(
#         self,
#         term: str,
#         *,
#         limit: int = 10,
#         offset: int = 0,
#         order_desc: bool = True,
#     ) -> List[Company]:
#         """
#         使用 ILIKE 以 term 模糊搜尋 name/alias。
#         預設以 id DESC 排序（Company 模型無 created_at 欄位）。
#         """
#         ilike = f"%{term}%"
#         stmt = (
#             select(Company)
#             .where((Company.name.ilike(ilike)) | (Company.alias.ilike(ilike)))  # type: ignore
#         )
#         if order_desc:
#             stmt = stmt.order_by(Company.id.desc())  # type: ignore
#         else:
#             stmt = stmt.order_by(Company.id.asc())  # type: ignore

#         if offset:
#             stmt = stmt.offset(offset)
#         if limit:
#             stmt = stmt.limit(limit)

#         return list(self.session.exec(stmt))

#     def list_all(
#         self,
#         *,
#         limit: Optional[int] = None,
#         offset: int = 0,
#         order_desc: bool = True,
#     ) -> List[Company]:
#         """
#         列出全部（支援分頁/排序）。
#         """
#         stmt = select(Company)
#         if order_desc:
#             stmt = stmt.order_by(Company.id.desc())  # type: ignore
#         else:
#             stmt = stmt.order_by(Company.id.asc())  # type: ignore

#         if offset:
#             stmt = stmt.offset(offset)
#         if limit:
#             stmt = stmt.limit(limit)

#         return list(self.session.exec(stmt))

#     # --- Convenience wrappers (optional) ------------------------------------

#     def update_contact(
#         self,
#         company_id: int,
#         *,
#         address: Optional[str] = None,
#         phone: Optional[str] = None,
#     ) -> Optional[Company]:
#         """
#         便捷：只更新聯絡資訊。實作仍呼叫父類 update()（已自動做乾淨輸入）。
#         """
#         return self.update(company_id, address=address, phone=phone)
