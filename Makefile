test-all:
	python -m unittest discover

test-company-create:
	python -m unittest test.test_company_service_create

test-company-update:
	python -m unittest test.test_company_service_update

test-orchestrator:
	python -m unittest test.test_orchestrator_non_financial
