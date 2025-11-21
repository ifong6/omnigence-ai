test-all:
	python -m unittest discover

test-company-create:
	python -m unittest test.test_company_service_create

test-company-update:
	python -m unittest test.test_company_service_update

test-job-create:
	python -m unittest test.test_job_service_create

test-job-update:
	python -m unittest test.test_job_service_update

# Quotation tests (DESIGN)
test-quotation-create-design:
	python -m unittest test.test_quotation_service_create.TestQuotationServiceCreateDesign.test_create_quotation_for_design_job

test-quotation-create-design-multiple:
	python -m unittest test.test_quotation_service_create.TestQuotationServiceCreateDesign.test_create_multiple_quotations_for_same_design_job

# Quotation tests (INSPECTION)
test-quotation-create-inspection:
	python -m unittest test.test_quotation_service_create.TestQuotationServiceCreateInspection.test_create_quotation_for_inspection_job

test-quotation-create-inspection-multiple:
	python -m unittest test.test_quotation_service_create.TestQuotationServiceCreateInspection.test_create_multiple_quotations_for_same_inspection_job

test-orchestrator-non-financial:
	python -m unittest test.test_orchestrator_non_financial
