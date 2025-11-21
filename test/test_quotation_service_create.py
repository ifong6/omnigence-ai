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
    InspectionJobSchemaForTest,
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
        self.inspection_model = InspectionJobSchemaForTest

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
    """
    測試版 QuotationService:
    - 用 SQLite 版 QuotationSchemaForTest / QuotationItemSchemaForTest
    - 用 DesignJobSchemaForTest / InspectionJobSchemaForTest
    """
    def __init__(self, session: Session):
        super().__init__(session)
        # override models with SQLite-friendly test schemas
        self.quotation_model = QuotationSchemaForTest          # type: ignore[assignment]
        self.quotation_item_model = QuotationItemSchemaForTest # type: ignore[assignment]

        # job models for DESIGN / INSPECTION
        self.design_job_model = DesignJobSchemaForTest         # type: ignore[assignment]
        self.inspection_job_model = InspectionJobSchemaForTest # type: ignore[assignment]

        # prefix → model 映射，配合 _resolve_job_model 使用
        self.job_model_by_prefix = {
            "Q-JCP-": self.design_job_model,
            "Q-JICP-": self.inspection_job_model,
        }


# ============================================================
#  DESIGN JOB TESTS
# ============================================================

class TestQuotationServiceCreateDesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)

        # 只建 test 需要的表
        CompanySchema.__table__.create(bind=cls.engine, checkfirst=True)              # type: ignore[attr-defined]
        DesignJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        InspectionJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]
        QuotationSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        QuotationItemSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]

    def setUp(self):
        self.session = Session(self.engine)
        self.job_service = JobServiceForTest(self.session)
        self.quotation_service = QuotationServiceForTest(self.session)

        # 1) company
        self.company = CompanySchema(
            name="ABC Construction",
            address="123 Test St",
            phone="12345678",
        )
        self.session.add(self.company)
        self.session.commit()

        # 2) 只建 DESIGN job
        self.design_job = self.job_service.create_job(
            company_id=self.company.id or 0,
            title="Test Design Job for Quotation",
            job_type="DESIGN",
            index=1,
            status="NEW",
            quotation_status="NOT_CREATED",
        )

        print("=" * 60)
        print("Printing company & DESIGN job tables")
        print_table_schema(self.session, "company")
        print_table_schema(self.session, "design_job")
        print("=" * 60)

    def tearDown(self):
        print("=" * 60)
        print("Printing quotation & quotation_item_test tables (DESIGN tests)")
        print_table_schema(self.session, "quotation")
        print_table_schema(self.session, "quotation_item_test")
        print("=" * 60)
        self.session.close()

    # 1) CREATE QUOTATION for DESIGN JOB（第一張：-01-R00）
    def test_create_quotation_for_design_job(self):
        result = self.quotation_service.create_quotation(
            job_no=self.design_job.job_no or "",
            company_id=self.company.id or 0,
            project_name="Unit test design project",
            items=[
                {
                    "item_desc": "Test structural design fee",
                    "quantity": 2,
                    "unit": "LS",
                    "unit_price": 4000.0,  # 2 * 4000 = 8000
                }
            ],
            date_issued=datetime.now().date(),
            revision_no="00",
            valid_until=datetime.now().date() + timedelta(days=30),
            notes="Test quotation for design job",
        )
        self.session.commit()

        self.assertIn("quotations", result)
        self.assertIn("quo_no", result)

        quotation = result["quotations"][0]
        quo_no = result["quo_no"]

        # 檢查 quo_no pattern
        job_no_from_quo, index, rev = parse_quo_no(quo_no)
        self.assertEqual(job_no_from_quo, self.design_job.job_no)
        self.assertEqual(index, 1)
        self.assertEqual(rev, 0)

        # 檢查 item 寫入
        items = list(
            self.session.exec(
                select(QuotationItemSchemaForTest).where(
                    QuotationItemSchemaForTest.quotation_id == quotation.id
                )
            )
        )
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, 4000.0)
        self.assertEqual(item.amount, 8000.0)

    # 2) 同一 DESIGN job 建多張 quotation：-01-R00 / -02-R00 / ...
    def test_create_multiple_quotations_for_same_design_job(self):
        # 第一張
        r1 = self.quotation_service.create_quotation(
            job_no=self.design_job.job_no or "",
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
            revision_no="00",
            valid_until=datetime.now().date() + timedelta(days=30),
            notes="First quotation",
        )
        self.session.commit()
        q1 = r1["quotations"][0]
        no1 = r1["quo_no"]

        # 第二張
        r2 = self.quotation_service.create_quotation(
            job_no=self.design_job.job_no or "",
            company_id=self.company.id or 1,
            project_name="Multi quotation project - second",
            items=[
                {
                    "item_desc": "Second design scope",
                    "quantity": 1,
                    "unit": "LS",
                    "unit_rate": 9000.0,
                }
            ],
            date_issued=datetime.now().date(),
            revision_no="00",
            valid_until=datetime.now().date() + timedelta(days=45),
            notes="Second quotation",
        )
        self.session.commit()
        q2 = r2["quotations"][0]
        no2 = r2["quo_no"]

        self.assertNotEqual(no1, no2)

        job_no1, idx1, rev1 = parse_quo_no(no1)
        job_no2, idx2, rev2 = parse_quo_no(no2)

        self.assertEqual(job_no1, self.design_job.job_no)
        self.assertEqual(job_no2, self.design_job.job_no)

        self.assertEqual(idx1, 1)
        self.assertEqual(rev1, 0)
        self.assertEqual(idx2, 2)
        self.assertEqual(rev2, 0)

        if getattr(q1, "id", None) is not None:
            db_q1 = self.session.get(QuotationSchemaForTest, q1.id)
            self.assertIsNotNone(db_q1)

        if getattr(q2, "id", None) is not None:
            db_q2 = self.session.get(QuotationSchemaForTest, q2.id)
            self.assertIsNotNone(db_q2)


# ============================================================
#  INSPECTION JOB TESTS
# ============================================================

class TestQuotationServiceCreateInspection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)

        CompanySchema.__table__.create(bind=cls.engine, checkfirst=True)              # type: ignore[attr-defined]
        DesignJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        InspectionJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]
        QuotationSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        QuotationItemSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]

    def setUp(self):
        self.session = Session(self.engine)
        self.job_service = JobServiceForTest(self.session)
        self.quotation_service = QuotationServiceForTest(self.session)

        # company
        self.company = CompanySchema(
            name="ABC Construction",
            address="123 Test St",
            phone="12345678",
        )
        self.session.add(self.company)
        self.session.commit()

        # 只建 INSPECTION job
        self.inspection_job = self.job_service.create_job(
            company_id=self.company.id or 0,
            title="Test Inspection Job for Quotation",
            job_type="INSPECTION",
            index=1,
            status="NEW",
            quotation_status="NOT_CREATED",
        )

        print("=" * 60)
        print("Printing company & INSPECTION job tables")
        print_table_schema(self.session, "company")
        print_table_schema(self.session, "inspection_job")
        print("=" * 60)

    def tearDown(self):
        print("=" * 60)
        print("Printing quotation & quotation_item_test tables (INSPECTION tests)")
        print_table_schema(self.session, "quotation")
        print_table_schema(self.session, "quotation_item_test")
        print("=" * 60)
        self.session.close()

    # 3) CREATE QUOTATION for INSPECTION JOB
    def test_create_quotation_for_inspection_job(self):
        result = self.quotation_service.create_quotation(
            job_no=self.inspection_job.job_no or "",
            company_id=self.company.id or 0,
            project_name="Unit test inspection project",
            items=[
                {
                    "item_desc": "Test structural inspection fee",
                    "quantity": 2,
                    "unit": "LS",
                    "unit_price": 3000.0,  # 2 * 3000 = 6000
                }
            ],
            date_issued=datetime.now().date(),
            revision_no="00",
            valid_until=datetime.now().date() + timedelta(days=30),
            notes="Test quotation for inspection job",
        )
        self.session.commit()

        quotation = result["quotations"][0]

        items = list(
            self.session.exec(
                select(QuotationItemSchemaForTest).where(
                    QuotationItemSchemaForTest.quotation_id == quotation.id
                )
            )
        )

        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, 3000.0)
        self.assertEqual(item.amount, 6000.0)

    # 4) 同一 INSPECTION job 建多張 quotation
    def test_create_multiple_quotations_for_same_inspection_job(self):
        # 第一張
        r1 = self.quotation_service.create_quotation(
            job_no=self.inspection_job.job_no or "",
            company_id=self.company.id or 1,
            project_name="Inspection multi quotation project",
            items=[
                {
                    "item_desc": "Initial inspection scope",
                    "quantity": 1,
                    "unit": "LS",
                    "unit_rate": 6000.0,
                }
            ],
            date_issued=datetime.now().date(),
            revision_no="00",
            valid_until=datetime.now().date() + timedelta(days=20),
            notes="First inspection quotation",
        )
        self.session.commit()
        q1 = r1["quotations"][0]
        no1 = r1["quo_no"]

        # 第二張
        r2 = self.quotation_service.create_quotation(
            job_no=self.inspection_job.job_no or "",
            company_id=self.company.id or 1,
            project_name="Inspection multi quotation project - second",
            items=[
                {
                    "item_desc": "Second inspection scope",
                    "quantity": 1,
                    "unit": "LS",
                    "unit_rate": 7000.0,
                }
            ],
            date_issued=datetime.now().date(),
            revision_no="00",
            valid_until=datetime.now().date() + timedelta(days=30),
            notes="Second inspection quotation",
        )
        self.session.commit()
        q2 = r2["quotations"][0]
        no2 = r2["quo_no"]

        self.assertNotEqual(no1, no2)

        job_no1, idx1, rev1 = parse_quo_no(no1)
        job_no2, idx2, rev2 = parse_quo_no(no2)

        self.assertEqual(job_no1, self.inspection_job.job_no)
        self.assertEqual(job_no2, self.inspection_job.job_no)

        self.assertEqual(idx1, 1)
        self.assertEqual(rev1, 0)
        self.assertEqual(idx2, 2)
        self.assertEqual(rev2, 0)

        if getattr(q1, "id", None) is not None:
            db_q1 = self.session.get(QuotationSchemaForTest, q1.id)
            self.assertIsNotNone(db_q1)

        if getattr(q2, "id", None) is not None:
            db_q2 = self.session.get(QuotationSchemaForTest, q2.id)
            self.assertIsNotNone(db_q2)


if __name__ == "__main__":
    unittest.main()
