import os
os.environ["USE_DB_SCHEMA"] = "0"

import unittest
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, select
from app.models.company_models import CompanySchema
from app.services.impl.JobServiceImpl import JobServiceImpl
from app.services.impl.QuotationServiceImpl import QuotationServiceImpl
from app.services.helpers.quotation_service_helper import parse_quo_no
from test.test_helpers import (
    print_table_schema,
    DesignJobSchemaForTest,
    QuotationSchemaForTest,
    QuotationItemSchemaForTest,
)

# ============================================================
#  Test Service Wrappers
# ============================================================

class JobServiceForTest(JobServiceImpl):
    def __init__(self, session: Session):
        super().__init__(session)
        self.design_model = DesignJobSchemaForTest
        # 如果之後要測 inspection，再加：
        # self.inspection_model = InspectionJobSchemaForTest

    def create_job(self, *args, **kwargs):
        job = super().create_job(*args, **kwargs)

        job_type = kwargs.get("job_type", "DESIGN")
        index = kwargs.get("index", 1)

        year_suffix = 25  # 固定測試年份
        batch = 1         # "01"
        prefix = "Q-JCP" if job_type == "DESIGN" else "Q-JICP"

        job.job_no = f"{prefix}-{year_suffix:02d}-{batch:02d}-{index}"

        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job


class QuotationServiceForTest(QuotationServiceImpl):
    def __init__(self, session: Session):
        super().__init__(session)
        # 確保同 QuotationServiceImpl 裡面用的屬性名一致
        self.quotation_model = QuotationSchemaForTest  # type: ignore[assignment]
        self.quotation_item_model = QuotationItemSchemaForTest  # type: ignore[assignment]
        self.design_job_model = DesignJobSchemaForTest  # type: ignore[assignment]


# ============================================================
#  Unit Tests for QuotationServiceImpl.create_quotation
# ============================================================

class TestQuotationServiceCreate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)

        # 只建 test 需要的表
        CompanySchema.__table__.create(bind=cls.engine, checkfirst=True)              # type: ignore[attr-defined]
        DesignJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        QuotationSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        QuotationItemSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]

    def setUp(self):
        self.session = Session(self.engine)

        self.job_service = JobServiceForTest(self.session)
        self.quotation_service = QuotationServiceForTest(self.session)

        # 1) 先造一個 company
        self.company = CompanySchema(
            name="ABC Construction",
            address="123 Test St",
            phone="12345678",
        )
        self.session.add(self.company)
        self.session.commit()

        # 2) 再造一個 DESIGN job（通過 JobServiceForTest，job_no 可預測）
        self.job = self.job_service.create_job(
            company_id=self.company.id or 0,
            title="Test Design Job for Quotation",
            job_type="DESIGN",
            index=1,
            status="NEW",
            quotation_status="NOT_CREATED",
        )

        # debug: print company & job tables
        print_table_schema(self.session, "company")
        print_table_schema(self.session, "design_job")

    def tearDown(self):
        # debug: print quotation table
        print_table_schema(self.session, "quotation")

        self.session.close()

    # --------------------------------------------------------
    # 1) CREATE QUOTATION for DESIGN JOB（第一張：-01-R00）
    # --------------------------------------------------------
    def test_create_quotation_for_design_job(self):
        result = self.quotation_service.create_quotation(
            job_no=self.job.job_no or "",
            company_id=self.company.id or 0,
            project_name="Unit test design project",
            items=[
                {
                    "item_desc": "Structural design fee",
                    "quantity": 1,
                    "unit": "Lot",
                    "unit_price": 10000.0,
                }
            ],
            date_issued=datetime.now().date(),
            revision_no="00",  # 對 create_quotation 來說會被固定成 R00
            valid_until=datetime.now().date() + timedelta(days=30),
            notes="Test quotation from unit test",
        )
        self.session.commit()


        # create_quotation 回傳 dict
        self.assertIn("quotations", result)
        self.assertIn("quo_no", result)

        quotations = result["quotations"]
        quo_no = result["quo_no"]

        self.assertEqual(len(quotations), 1)
        quotation = quotations[0]

        # ========= 檢查 quo_no pattern =========
        job_no_from_quo, index, rev = parse_quo_no(quo_no)
        self.assertEqual(job_no_from_quo, self.job.job_no)
        self.assertEqual(index, 1)   # 第一張 = 01
        self.assertEqual(rev, 0)     # R00

        # ========= 基本欄位 =========
        self.assertIsNotNone(quotation.id)
        # 注意：實際 Quotation model 有可能用 client_id 而唔係 company_id
        self.assertEqual(getattr(quotation, "client_id", None), self.company.id)

        # DB 持久化檢查
        db_quotation = self.session.get(QuotationSchemaForTest, quotation.id)
        self.assertIsNotNone(db_quotation)

        if db_quotation:
            self.assertEqual(db_quotation.quo_no, quo_no) # type: ignore[attr-defined]

        # ========= 檢查 quotation items 是否被創建 =========
        items = list(
            self.session.exec(
                select(QuotationItemSchemaForTest).where(
                    QuotationItemSchemaForTest.quotation_id == quotation.id
                )
            )
        )

        # 驗證 item 數量
        self.assertEqual(len(items), 1, "Should have exactly 1 item")

        # 驗證 item 字段
        item = items[0]
        self.assertEqual(item.item_desc, "Structural design fee")
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.unit, "Lot")
        self.assertEqual(item.unit_price, 10000.0)
        self.assertEqual(item.amount, 10000.0)  # quantity * unit_price = 1 * 10000

        # 驗證 quotation-item 關係
        self.assertEqual(item.quotation_id, quotation.id)

    # --------------------------------------------------------
    # 2) 同一 job 建多張 quotation：-01-R00 / -02-R00 / ...
    # --------------------------------------------------------
    def test_create_multiple_quotations_for_same_job(self):
        # 第 1 張：index = 1, rev = 0
        r1 = self.quotation_service.create_quotation(
            job_no=self.job.job_no or "",
            company_id=self.company.id or 1,
            project_name="Multi quotation project",
            items=[
                {
                    "item_desc": "Initial design scope",
                    "quantity": 1,
                    "unit": "Lot",
                    "unit_price": 8000.0,
                }
            ],
            date_issued=datetime.now().date(),
            revision_no="00",  # 新 quotation 一律 R00
            valid_until=datetime.now().date() + timedelta(days=30),
            notes="First quotation",
        )
        self.session.commit()   # 手動 commit 一次，然後先俾 tearDown rollback 其他嘢
        q1 = r1["quotations"][0]
        no1 = r1["quo_no"]

        # 第 2 張（同 job）：index 應該變 2，依然 R00
        r2 = self.quotation_service.create_quotation(
            job_no=self.job.job_no or "",
            company_id=self.company.id or 1,
            project_name="Multi quotation project - second",
            items=[
                {
                    "item_desc": "Second quotation scope",
                    "quantity": 1,
                    "unit": "Lot",
                    "unit_price": 9000.0,
                }
            ],
            date_issued=datetime.now().date(),
            revision_no="00",  # 依然 create path，唔係 revision
            valid_until=datetime.now().date() + timedelta(days=45),
            notes="Second quotation",
        )
        self.session.commit()   # 手動 commit 一次，然後先俾 tearDown rollback 其他嘢
        q2 = r2["quotations"][0]
        no2 = r2["quo_no"]

        # 基本：兩個 quo_no 一定唔相同
        self.assertNotEqual(no1, no2, "Two quotations for same job should not share the same quo_no")

        # 用 helper 解析
        job_no1, idx1, rev1 = parse_quo_no(no1)
        job_no2, idx2, rev2 = parse_quo_no(no2)

        self.assertEqual(job_no1, self.job.job_no)
        self.assertEqual(job_no2, self.job.job_no)

        # index 1 -> 2，revision 一直 0
        self.assertEqual(idx1, 1)
        self.assertEqual(rev1, 0)

        self.assertEqual(idx2, 2)
        self.assertEqual(rev2, 0)

        # DB check：都應該被持久化
        if getattr(q1, "id", None) is not None:
            db_q1 = self.session.get(QuotationSchemaForTest, q1.id)
            self.assertIsNotNone(db_q1)

        if getattr(q2, "id", None) is not None:
            db_q2 = self.session.get(QuotationSchemaForTest, q2.id)
            self.assertIsNotNone(db_q2)

        # ========= 檢查第一個 quotation 的 items =========
        items_q1 = list(
            self.session.exec(
                select(QuotationItemSchemaForTest).where(
                    QuotationItemSchemaForTest.quotation_id == q1.id
                )
            )
        )
        self.assertEqual(len(items_q1), 1, "First quotation should have 1 item")
        self.assertEqual(items_q1[0].item_desc, "Initial design scope")
        self.assertEqual(items_q1[0].quantity, 1)
        self.assertEqual(items_q1[0].unit, "Lot")
        self.assertEqual(items_q1[0].unit_price, 8000.0)
        self.assertEqual(items_q1[0].amount, 8000.0)  # 1 * 8000
        self.assertEqual(items_q1[0].quotation_id, q1.id)

        # ========= 檢查第二個 quotation 的 items =========
        items_q2 = list(
            self.session.exec(
                select(QuotationItemSchemaForTest).where(
                    QuotationItemSchemaForTest.quotation_id == q2.id
                )
            )
        )
        self.assertEqual(len(items_q2), 1, "Second quotation should have 1 item")
        self.assertEqual(items_q2[0].item_desc, "Second quotation scope")
        self.assertEqual(items_q2[0].quantity, 1)
        self.assertEqual(items_q2[0].unit, "Lot")
        self.assertEqual(items_q2[0].unit_price, 9000.0)
        self.assertEqual(items_q2[0].amount, 9000.0)  # 1 * 9000
        self.assertEqual(items_q2[0].quotation_id, q2.id)

        # ========= 驗證兩個 quotation 的 items 是獨立的 =========
        self.assertNotEqual(items_q1[0].id, items_q2[0].id,
                            "Items should have different IDs")
        self.assertNotEqual(items_q1[0].quotation_id, items_q2[0].quotation_id,
                            "Items should belong to different quotations")


# ============================================================
#  UPDATE QUOTATION TESTS (Revision Creation)
# ============================================================

class TestQuotationServiceUpdateRevision(unittest.TestCase):
    """測試 update_quotation 方法 - 創建 revision"""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)

        # 創建所需的表
        CompanySchema.__table__.create(bind=cls.engine, checkfirst=True)              # type: ignore[attr-defined]
        DesignJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        QuotationSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        QuotationItemSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]

    def setUp(self):
        self.session = Session(self.engine)
        self.job_service = JobServiceForTest(self.session)
        self.quotation_service = QuotationServiceForTest(self.session)

        # 創建 company
        self.company = CompanySchema(
            name="Test Company",
            address="456 Update St",
            phone="87654321",
        )
        self.session.add(self.company)
        self.session.commit()

        # 創建 job
        self.job = self.job_service.create_job(
            company_id=self.company.id or 0,
            title="Test Job for Update",
            job_type="DESIGN",
            index=1,
            status="NEW",
            quotation_status="NOT_CREATED",
        )

        # 創建基礎 quotation (R00)
        result = self.quotation_service.create_quotation(
            job_no=self.job.job_no or "",
            company_id=self.company.id or 0,
            project_name="Update test project",
            items=[
                {
                    "item_desc": "Original design fee",
                    "quantity": 1,
                    "unit": "Lot",
                    "unit_price": 10000.0,
                }
            ],
            date_issued=datetime.now().date(),
            valid_until=datetime.now().date() + timedelta(days=30),
            notes="Original quotation",
        )
        self.session.commit()
        self.base_quotation = result["quotations"][0]
        self.base_quo_no = result["quo_no"]

    def tearDown(self):
        print("=" * 60)
        print("Printing quotation & quotation_item_test tables (UPDATE tests)")
        print_table_schema(self.session, "quotation")
        print_table_schema(self.session, "quotation_item_test")
        print("=" * 60)
        self.session.close()

    # --------------------------------------------------------
    # 1) UPDATE creates new revision (R00 -> R01)
    # --------------------------------------------------------
    def test_update_creates_new_revision(self):
        """測試 update_quotation 創建新的 revision"""
        from app.models.quotation_models import QuotationUpdate

        # 更新 status
        update_payload = QuotationUpdate(
            status="SENT",
            notes="Updated to SENT status",
        )

        new_revision = self.quotation_service.update_quotation(
            base_quotation_id=self.base_quotation.id,  # type: ignore[attr-defined]
            update_payload=update_payload,
        )
        self.session.commit()

        # 檢查新 revision
        self.assertIsNotNone(new_revision.id)
        self.assertNotEqual(new_revision.id, self.base_quotation.id)

        # 檢查 quo_no 格式（應該是 R01）
        job_no, idx, rev = parse_quo_no(new_revision.quo_no)  # type: ignore[attr-defined]
        self.assertEqual(job_no, self.job.job_no)
        self.assertEqual(idx, 1)  # Same quotation index
        self.assertEqual(rev, 1)  # Revision incremented to R01

        # 檢查更新的字段
        self.assertEqual(new_revision.status, "SENT")  # type: ignore[attr-defined]
        self.assertEqual(new_revision.notes, "Updated to SENT status")  # type: ignore[attr-defined]

        # 檢查基礎 quotation 沒有被修改
        base_in_db = self.session.get(QuotationSchemaForTest, self.base_quotation.id)
        self.assertEqual(base_in_db.status, "DRAFTED")  # type: ignore[attr-defined]
        self.assertEqual(base_in_db.notes, "Original quotation")  # type: ignore[attr-defined]

    # --------------------------------------------------------
    # 2) Multiple revisions (R00 -> R01 -> R02)
    # --------------------------------------------------------
    def test_multiple_revisions(self):
        """測試多次 revision（R00 -> R01 -> R02）"""
        from app.models.quotation_models import QuotationUpdate

        # 第一次更新：R00 -> R01
        update1 = QuotationUpdate(status="SENT")
        rev1 = self.quotation_service.update_quotation(
            base_quotation_id=self.base_quotation.id,  # type: ignore[attr-defined]
            update_payload=update1,
        )
        self.session.commit()

        _, _, rev_no1 = parse_quo_no(rev1.quo_no)  # type: ignore[attr-defined]
        self.assertEqual(rev_no1, 1)

        # 第二次更新：使用 R00 再次更新 -> R02
        update2 = QuotationUpdate(
            status="ACCEPTED",
            notes="Client accepted",
        )
        rev2 = self.quotation_service.update_quotation(
            base_quotation_id=self.base_quotation.id,  # type: ignore[attr-defined]
            update_payload=update2,
        )
        self.session.commit()

        _, _, rev_no2 = parse_quo_no(rev2.quo_no)  # type: ignore[attr-defined]
        self.assertEqual(rev_no2, 2)

        # 驗證數據庫中有 3 個 quotation（R00, R01, R02）
        all_quotations = list(
            self.session.exec(
                select(QuotationSchemaForTest).where(
                    QuotationSchemaForTest.quo_no.like(f"{self.job.job_no}-01-R%")  # type: ignore[attr-defined]
                )
            )
        )
        self.assertEqual(len(all_quotations), 3)

        # 驗證各個 revision 的 status
        quotations_by_rev = {parse_quo_no(q.quo_no)[2]: q for q in all_quotations}  # type: ignore[attr-defined]
        self.assertEqual(quotations_by_rev[0].status, "DRAFTED")  # type: ignore[attr-defined]
        self.assertEqual(quotations_by_rev[1].status, "SENT")  # type: ignore[attr-defined]
        self.assertEqual(quotations_by_rev[2].status, "ACCEPTED")  # type: ignore[attr-defined]

    # --------------------------------------------------------
    # 3) Update multiple fields at once
    # --------------------------------------------------------
    def test_update_multiple_fields(self):
        """測試同時更新多個字段"""
        from app.models.quotation_models import QuotationUpdate

        new_valid_until = datetime.now().date() + timedelta(days=60)

        update_payload = QuotationUpdate(
            status="SENT",
            valid_until=new_valid_until,
            notes="Extended validity and sent to client",
            currency="HKD",
        )

        new_revision = self.quotation_service.update_quotation(
            base_quotation_id=self.base_quotation.id,  # type: ignore[attr-defined]
            update_payload=update_payload,
        )
        self.session.commit()

        # 驗證所有更新的字段
        self.assertEqual(new_revision.status, "SENT")  # type: ignore[attr-defined]
        self.assertEqual(new_revision.valid_until, new_valid_until)  # type: ignore[attr-defined]
        self.assertEqual(new_revision.notes, "Extended validity and sent to client")  # type: ignore[attr-defined]
        self.assertEqual(new_revision.currency, "HKD")  # type: ignore[attr-defined]

        # 驗證未更新的字段保持不變
        self.assertEqual(new_revision.client_id, self.base_quotation.client_id)  # type: ignore[attr-defined]
        self.assertEqual(new_revision.project_name, self.base_quotation.project_name)  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
