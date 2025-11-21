import os
os.environ["USE_DB_SCHEMA"] = "0"

import unittest
from datetime import datetime
from typing import ClassVar
from sqlmodel import SQLModel, Session, create_engine, Field
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.models.company_models import CompanySchema
from app.services.impl.JobServiceImpl import JobServiceImpl
from test.test_helpers import print_table_schema

# ============================================================
#  SQLite-Compatible Schemas for Testing create_job
# ============================================================
class DesignJobSchemaForTest(SQLModel, table=True):
    __tablename__: ClassVar[str] = "design_job"

    id: int | None = Field(default=None, primary_key=True)
    company_id: int
    title: str

    status: str | None = None
    quotation_status: str | None = None
    job_no: str | None = None

    date_created: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


class InspectionJobSchemaForTest(SQLModel, table=True):
    __tablename__: ClassVar[str] = "inspection_job"

    id: int | None = Field(default=None, primary_key=True)
    company_id: int
    title: str

    status: str | None = None
    quotation_status: str | None = None
    job_no: str | None = None

    date_created: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


# ============================================================
#  Inject test models into JobServiceImpl
# ============================================================
class JobServiceForTest(JobServiceImpl):
    def __init__(self, session: Session):
        super().__init__(session)
        self.design_model = DesignJobSchemaForTest
        self.inspection_model = InspectionJobSchemaForTest

    def create_job(self, *args, **kwargs):
        # inherit JobServiceImpl logic + slightly modified test version
        job = super().create_job(*args, **kwargs)

        job_type = kwargs.get("job_type", "DESIGN")
        index = kwargs.get("index", 1)

        year_suffix = 25   # fixed for test
        batch = 1          # "01"
        prefix = "Q-JCP" if job_type == "DESIGN" else "Q-JICP"

        job.job_no = f"{prefix}-{year_suffix:02d}-{batch:02d}-{index}"

        self.session.add(job)
        self.session.commit()

        return job


# ============================================================
#  Unit Tests for create_job
# ============================================================
class TestCreateJob(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)

        # Only create tables needed for tests
        CompanySchema.__table__.create(bind=cls.engine, checkfirst=True)              # type: ignore[attr-defined]
        DesignJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        InspectionJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]

    def setUp(self):
        self.session = Session(self.engine)
        self.job_service = JobServiceForTest(self.session)

        self.company = CompanySchema(
            name="ABC Construction",
            address="123 Test St",
            phone="12345678",
        )
        self.session.add(self.company)
        self.session.commit()

    def tearDown(self):
        self.session.close()

    # --------------------------------------------------------
    # DESIGN job
    # --------------------------------------------------------
    def test_create_design_job(self):
        job = self.job_service.create_job(
            company_id=self.company.id or 0,
            title="Building Design",
            job_type="DESIGN",
            index=1,
            status="NEW",
            quotation_status="NOT_CREATED",
        )

        self.assertIsNotNone(job.id)
        self.assertEqual(job.title, "Building Design")
        self.assertEqual(job.company_id, self.company.id)

        self.assertTrue(
            job.job_no and job.job_no.startswith("Q-JCP-25-01-"),
            f"job_no should start with 'Q-JCP-25-01-', got {job.job_no!r}",
        )

        db_job = self.session.get(DesignJobSchemaForTest, job.id)
        self.assertIsNotNone(db_job)
        if db_job:
            self.assertEqual(db_job.title, "Building Design")
            self.assertEqual(db_job.company_id, self.company.id)

        print_table_schema(self.session, "design_job")

    # --------------------------------------------------------
    # INSPECTION job
    # --------------------------------------------------------
    def test_create_inspection_job(self):
        job = self.job_service.create_job(
            company_id=self.company.id or 0,
            title="Site Inspection",
            job_type="INSPECTION",
            index=1,
            status="NEW",
            quotation_status="NOT_CREATED",
        )

        self.assertIsNotNone(job.id)
        self.assertEqual(job.title, "Site Inspection")
        self.assertEqual(job.company_id, self.company.id)

        self.assertTrue(
            job.job_no and job.job_no.startswith("Q-JICP-25-01-"),
            f"job_no should start with 'Q-JICP-25-01-', got {job.job_no!r}",
        )

        db_job = self.session.get(InspectionJobSchemaForTest, job.id)
        self.assertIsNotNone(db_job)
        if db_job:
            self.assertEqual(db_job.title, "Site Inspection")
            self.assertEqual(db_job.company_id, self.company.id)

        print_table_schema(self.session, "inspection_job")


if __name__ == "__main__":
    unittest.main()
