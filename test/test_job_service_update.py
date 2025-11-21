import os
os.environ["USE_DB_SCHEMA"] = "0"

import unittest
from sqlmodel import Session, create_engine
from app.models.company_models import CompanySchema
from app.services.impl.JobServiceImpl import JobServiceImpl
from test.test_helpers import (
    DesignJobSchemaForTest,
    InspectionJobSchemaForTest,
    print_table_schema,
)


# ============================================================
#  Inject test models into JobServiceImpl
# ============================================================
class JobServiceForTest(JobServiceImpl):
    def __init__(self, session: Session):
        super().__init__(session)
        # Use SQLite-friendly test schemas
        self.design_model = DesignJobSchemaForTest
        self.inspection_model = InspectionJobSchemaForTest


# ============================================================
#  Unit Tests for update()
# ============================================================
class TestUpdateJob(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)

        # Only create the tables needed for tests
        CompanySchema.__table__.create(bind=cls.engine, checkfirst=True)              # type: ignore[attr-defined]
        DesignJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True)     # type: ignore[attr-defined]
        InspectionJobSchemaForTest.__table__.create(bind=cls.engine, checkfirst=True) # type: ignore[attr-defined]

    def setUp(self):
        self.session = Session(self.engine)
        self.job_service = JobServiceForTest(self.session)

        # Seed one company
        self.company = CompanySchema(
            name="ABC Construction",
            address="123 Test St",
            phone="12345678",
        )
        self.session.add(self.company)
        self.session.commit()

        # Seed one DESIGN job
        self.design_job = self.job_service.create_job(
            company_id=self.company.id or 0,
            title="Original Design Job",
            job_type="DESIGN",
            index=1,
            status="NEW",
            quotation_status="NOT_CREATED",
        )

        # Seed one INSPECTION job
        self.inspection_job = self.job_service.create_job(
            company_id=self.company.id or 0,
            title="Original Inspection Job",
            job_type="INSPECTION",
            index=1,
            status="NEW",
            quotation_status="NOT_CREATED",
        )

    def tearDown(self):
        self.session.close()

    # --------------------------------------------------------
    # UPDATE DESIGN job
    # --------------------------------------------------------
    def test_update_design_job(self):
        # Print BEFORE update
        print_table_schema(self.session, "design_job")

        updated = self.job_service.update(
            job_id=self.design_job.id or 1,
            job_type="DESIGN",
            title="Updated Design Job",
            status="IN_PROGRESS",
            quotation_status="CREATED",
        )

        self.assertIsNotNone(updated)
        assert updated is not None

        self.assertEqual(updated.title, "Updated Design Job")
        self.assertEqual(updated.status, "IN_PROGRESS")
        self.assertEqual(updated.quotation_status, "CREATED")

        db_job = self.session.get(DesignJobSchemaForTest, self.design_job.id)
        self.assertIsNotNone(db_job)
        if db_job:
            self.assertEqual(db_job.title, "Updated Design Job")
            self.assertEqual(db_job.status, "IN_PROGRESS")
            self.assertEqual(db_job.quotation_status, "CREATED")

        # Print AFTER update
        print_table_schema(self.session, "design_job")

    # --------------------------------------------------------
    # UPDATE INSPECTION job
    # --------------------------------------------------------
    def test_update_inspection_job(self):
        # Print BEFORE update
        print_table_schema(self.session, "inspection_job")

        updated = self.job_service.update(
            job_id=self.inspection_job.id or 1, 
            job_type="INSPECTION",
            title="Updated Inspection Job",
            status="COMPLETED",
            quotation_status="CREATED",
        )

        self.assertIsNotNone(updated)
        assert updated is not None

        self.assertEqual(updated.title, "Updated Inspection Job")
        self.assertEqual(updated.status, "COMPLETED")
        self.assertEqual(updated.quotation_status, "CREATED")

        db_job = self.session.get(InspectionJobSchemaForTest, self.inspection_job.id)
        self.assertIsNotNone(db_job)
        if db_job:
            self.assertEqual(db_job.title, "Updated Inspection Job")
            self.assertEqual(db_job.status, "COMPLETED")
            self.assertEqual(db_job.quotation_status, "CREATED")

        # Print AFTER update
        print_table_schema(self.session, "inspection_job")

    # --------------------------------------------------------
    # UPDATE non-existent job
    # --------------------------------------------------------
    def test_update_nonexistent_job(self):
        result = self.job_service.update(
            job_id=99999,
            job_type="DESIGN",
            title="Should Not Exist",
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
