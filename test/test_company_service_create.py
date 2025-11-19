import os
os.environ["USE_DB_SCHEMA"] = "0"

import unittest
from sqlmodel import SQLModel, Session, create_engine, text
from app.models.company_models import CompanySchema
from app.services.impl.CompanyServiceImpl import CompanyServiceImpl
from test.test_helpers import print_table_schema

class TestCompanyServiceCreate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False) # In-memory SQLite database for testing
        CompanySchema.__table__.create(bind=cls.engine) # type: ignore[attr-defined]

    def setUp(self): # Set up the test environment
        # SQLModel（基于 SQLAlchemy）的 Session 类
        self.session = Session(self.engine) # Create a session for the test
        self.service = CompanyServiceImpl(self.session)

    def tearDown(self): # Tear down the test environment
        self.session.close() # Close the session after the test

    def test_create_company(self): # Test the create company functionality
        company = self.service.create( # Create a company
            name="ABC Construction",
            address="123 Test Street",
            phone="28887890",
        )

        self.assertIsNotNone(company.id)
        self.assertEqual(company.name, "ABC Construction")

        db_company = self.session.get(CompanySchema, company.id)
        self.assertIsNotNone(db_company, "Company should be persisted in DB")
        
        # ========== Print Before Close ==========
        print_table_schema(self.session, "company")
        
        assert db_company is not None
        self.assertEqual(db_company.name, "ABC Construction")
        self.assertEqual(db_company.address, "123 Test Street")
        self.assertEqual(db_company.phone, "28887890")
        
if __name__ == "__main__":
    unittest.main()