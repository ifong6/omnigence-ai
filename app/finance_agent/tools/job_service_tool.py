from typing import Any, Dict
import json
from sqlmodel import Session
from app.db.engine import engine
from app.services.impl import JobServiceImpl 

def job_service_tool(operation: str, params: Dict[str, Any]) -> str:
    """
    A high-level service wrapper for job operations.

    IMPORTANT: The parameter name is 'title', NOT 'name' or 'project'. Use 'title' for job creation.

    Operations:
        1. create: Create new job with auto-generated job_no
           REQUIRED params: {
               company_id: int,        # Company ID (get from CompanyService first)
               title: str,             # Job title/project name (e.g., "消防系統設計")
               job_type: str           # Must be "DESIGN" or "INSPECTION"
           }
           OPTIONAL params: {
               index: int,             # Default: 1
               status: str,            # Default: "NEW" (auto-set, don't override)
               quotation_status: str   # Default: "NOT_CREATED" (auto-set, don't override)
           }
           returns: {id: int, job_no: str, company_id: int, title: str, status: str, ...}

        2. get_by_job_no: Get job by job number
           params: {job_no: str, job_type: "DESIGN"|"INSPECTION"}
           returns: {id: int, job_no: str, ...} or null

        3. get_by_company: Get all jobs for a company
           params: {company_id: int, job_type: "DESIGN"|"INSPECTION", limit?: int}
           returns: [{id, job_no, title, ...}, ...]

        4. update: Update existing job
           params: {job_id: int, job_type: "DESIGN"|"INSPECTION", title?: str,
                   status?: str, quotation_status?: str}
           returns: {id: int, job_no: str, ...} or null

        5. list_all: List all jobs of a type
           REQUIRED params: {job_type: "DESIGN"|"INSPECTION"}
           OPTIONAL params: {limit: int}
           returns: [{id, job_no, title, status, quotation_status, ...}, ...]

    Examples:
        CREATE JOB (correct):
        >>> job_service_tool("create", {
        ...     "company_id": 15,
        ...     "title": "消防系統設計",     # ← Use 'title', not 'name' or 'project'
        ...     "job_type": "DESIGN"
        ... })
        '{"id": 1, "job_no": "JCP-25-01-1", "status": "NEW", ...}'

        LIST ALL JOBS (correct):
        >>> job_service_tool("list_all", {"job_type": "INSPECTION"})
        '[{"id": 1, "job_no": "JICP-25-01-1", ...}]'
    """
    print(f"[DEBUG][job_service_tool] operation={operation}")
    print(f"[DEBUG][job_service_tool] params={params}")

    try:
        with Session(engine) as session:
            service = JobServiceImpl(session)

            if operation == "create":
                job = service.create_job(**params)
                session.commit()
                return json.dumps({
                    "id": job.id,
                    "job_no": job.job_no,
                    "company_id": job.company_id,
                    "title": job.title,
                    "status": job.status,
                    "quotation_status": job.quotation_status,
                    "date_created": job.date_created.isoformat() if job.date_created else None
                }, ensure_ascii=False)

            elif operation == "get_by_job_no":
                job = service.get_by_job_no(
                    params["job_no"],
                    params["job_type"]
                )
                if not job:
                    return json.dumps(None)
                return json.dumps({
                    "id": job.id,
                    "job_no": job.job_no,
                    "company_id": job.company_id,
                    "title": job.title,
                    "status": job.status,
                    "quotation_status": job.quotation_status
                }, ensure_ascii=False)

            elif operation == "get_by_company":
                jobs = service.get_by_company(
                    params["company_id"],
                    params["job_type"],
                    params.get("limit")
                )
                return json.dumps([
                    {
                        "id": j.id,
                        "job_no": j.job_no,
                        "company_id": j.company_id,
                        "title": j.title,
                        "status": j.status,
                        "quotation_status": j.quotation_status
                    }
                    for j in jobs
                ], ensure_ascii=False)

            elif operation == "update":
                job_id = params.pop("job_id")
                job_type = params.pop("job_type")
                job = service.update(job_id, job_type, **params)
                session.commit()
                if not job:
                    return json.dumps(None)
                return json.dumps({
                    "id": job.id,
                    "job_no": job.job_no,
                    "company_id": job.company_id,
                    "title": job.title,
                    "status": job.status,
                    "quotation_status": job.quotation_status
                }, ensure_ascii=False)

            elif operation == "list_all":
                jobs = service.list_all(
                    params["job_type"],
                    params.get("limit")
                )
                return json.dumps([
                    {
                        "id": j.id,
                        "job_no": j.job_no,
                        "company_id": j.company_id,
                        "title": j.title,
                        "status": j.status,
                        "quotation_status": j.quotation_status
                    }
                    for j in jobs
                ], ensure_ascii=False)

            else:
                return json.dumps({
                    "error": f"Unknown operation: {operation}"
                })

    except TypeError as e:
        # Catch parameter name errors and provide helpful message
        error_str = str(e)
        if "unexpected keyword argument" in error_str:
            if "'name'" in error_str:
                error_msg = "Error: Use 'title' parameter, not 'name'. Correct format: {\"company_id\": int, \"title\": str, \"job_type\": \"DESIGN\"|\"INSPECTION\"}"
            elif "'project'" in error_str:
                error_msg = "Error: Use 'title' parameter, not 'project'. Correct format: {\"company_id\": int, \"title\": str, \"job_type\": \"DESIGN\"|\"INSPECTION\"}"
            else:
                error_msg = f"Error: Invalid parameter. {error_str}. See tool documentation for correct parameters."
        else:
            error_msg = f"Type error in job_service_tool: {error_str}"
        print(f"[ERROR][job_service_tool] {error_msg}")
        return json.dumps({"error": error_msg})
    except KeyError as e:
        # Catch missing required parameters
        error_msg = f"Error: Missing required parameter {str(e)}. For 'create' operation, required: company_id, title, job_type. For 'list_all', required: job_type."
        print(f"[ERROR][job_service_tool] {error_msg}")
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error in job_service_tool: {str(e)}"
        print(f"[ERROR][job_service_tool] {error_msg}")
        return json.dumps({"error": error_msg})
