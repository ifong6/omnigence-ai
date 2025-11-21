import os
os.environ["USE_DB_SCHEMA"] = "0"

import unittest
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine
from app.models.company_models import CompanySchema
from app.services.impl.JobServiceImpl import JobServiceImpl
from app.services.impl.QuotationServiceImpl import QuotationServiceImpl
from app.services.helpers.quotation_service_helper import parse_quo_no
from test.test_helpers import print_table_schema, DesignJobSchemaForTest, QuotationSchemaForTest

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
        self.job_model = DesignJobSchemaForTest  # type: ignore[assignment]


# ============================================================
#  Unit Tests for QuotationServiceImpl.create_quotation
# ============================================================

class TestQuotationServiceCreate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)

        # 只建 test 需要的表
        CompanySchema.__table__.create(bind=cls.engine, checkfirst=True)          # type: ignore[attr-defined]
        DesignJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]
        QuotationSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]

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
                    "unit": "LS",
                    "unit_rate": 10000.0,
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
                    "unit": "LS",
                    "unit_rate": 8000.0,
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
                    "unit": "LS",
                    "unit_rate": 9000.0,
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


if __name__ == "__main__":
    unittest.main()
