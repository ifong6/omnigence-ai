import os
os.environ["USE_DB_SCHEMA"] = "0"

import unittest
from sqlmodel import SQLModel, Session, create_engine, text
from app.models.company_models import CompanySchema
from app.services.impl.CompanyServiceImpl import CompanyServiceImpl
from test.test_helpers import print_table_schema

class TestCompanyServiceUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False) # In-memory SQLite database for testing
        CompanySchema.__table__.create(bind=cls.engine) # type: ignore[attr-defined]

    def setUp(self):
        self.session = Session(self.engine)
        self.service = CompanyServiceImpl(self.session)
        
        # Create a default company for testing updates
        self.default_company = self.service.create(
            name="Default Company",
            address="Default Address",
            phone="00000000",
        )
        self.session.commit()
        print_table_schema(self.session, "company")

    def tearDown(self): # Tear down the test environment
        self.session.close() # Close the session after the test

    def test_update_company(self):
        company_id = self.default_company.id
        assert company_id is not None  
        
        updated_company = self.service.update(
            company_id=company_id, 
            name="ABC Construction Updated",
            address="123 Test Street Updated",
            phone="28887890 Updated",
        )
        
        db_company = self.session.get(CompanySchema, self.default_company.id)
        self.assertIsNotNone(db_company, "Company should be persisted in DB")
        
        print_table_schema(self.session, "company")
        
        assert db_company is not None
        self.assertEqual(db_company.name, "ABC Construction Updated")
        self.assertEqual(db_company.address, "123 Test Street Updated")
        self.assertEqual(db_company.phone, "28887890 Updated")
            

if __name__ == "__main__":
    unittest.main()