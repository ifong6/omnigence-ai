from typing import Any, Dict
import json
from sqlmodel import Session
from app.db.engine import engine
from app.finance_agent.services.quotation_service import QuotationService
        
def quotation_service_tool(operation: str, params: Dict[str, Any]) -> str:
    """
    A high-level service wrapper for quotation operations.

    Args:
        operation: Operation name (create, generate_number, get_by_quo_no, get_by_job_no,
                                  search, update, get_total, list_all).
        params: Operation parameters as dict.

    Returns:
        JSON string with operation result or error.
    Operations:
        1. create: Create complete quotation with header and items.
           params: {job_no: str, company_id: int, project_name: str,
                   items: [{item_desc: str, quantity: int, unit_price: Decimal, unit?: str}, ...],
                   currency?: str, date_issued?: date, is_revision?: bool,
                   valid_until?: date, notes?: str}
           returns: {quotation: {...}, items: [{id, item_desc, quantity, unit_price, amount}, ...]}

        2. generate_number: Generate quotation number only.
           params: {job_no: str, is_revision?: bool}
           returns: "Q-JICP-25-02-q1-R00"

        3. get_by_quo_no: Get quotation header by quotation number.
           params: {quo_no: str}
           returns: {id, quo_no, client_id, project_name, status, ...}

        4. get_by_job_no: Get all quotations for a job.
           params: {job_no: str}
           returns: [{id, quo_no, project_name, status, ...}, ...]

        5. search: Search quotations by project name.
           params: {project_name_pattern: str, limit?: int}
           returns: [{id, quo_no, project_name, ...}, ...]

        6. update: Update quotation header.
           params: {quotation_ids: [int, ...], **update_fields}
           returns: [{id, quo_no, ...}, ...]

        7. get_total: Calculate total for a quotation.
           params: {quo_no: str}
           returns: {total: Decimal, item_count: int}

        8. list_all: List all quotations.
           params: {order_by?: str, descending?: bool, limit?: int}
           returns: [{id, quo_no, project_name, ...}, ...]

    Examples:
        >>> quotation_service_tool("generate_number", {
        ...     "job_no": "JICP-25-02-1"
        ... })
        '"Q-JICP-25-02-q1-R00"'

        >>> quotation_service_tool("create", {
        ...     "job_no": "JICP-25-02-1",
        ...     "company_id": 27,
        ...     "project_name": "結構安全檢測 - Building A",
        ...     "items": [
        ...         {"item_desc": "Foundation inspection", "quantity": 1, "unit_price": 20000},
        ...         {"item_desc": "Structural assessment", "quantity": 1, "unit_price": 25000}
        ...     ]
        ... })
        '{"quotation": {"id": 1, "quo_no": "Q-JICP-25-02-q1-R00", ...}, "items": [...]}'
    """
    print(f"[DEBUG][quotation_service_tool] operation={operation}")
    print(f"[DEBUG][quotation_service_tool] params={params}")

    try:
        with Session(engine) as session:
            service = QuotationService(session)

            if operation == "create":
                result = service.create_quotation(**params)
                session.commit()

                quotation = result["quotation"]
                items = result["items"]

                return json.dumps({
                    "quotation": {
                        "id": quotation.id,
                        "quo_no": quotation.quo_no,
                        "client_id": quotation.client_id,
                        "project_name": quotation.project_name,
                        "date_issued": quotation.date_issued.isoformat(),
                        "status": quotation.status,
                        "currency": quotation.currency,
                        "revision_no": quotation.revision_no,
                        "valid_until": quotation.valid_until.isoformat() if quotation.valid_until else None,
                        "notes": quotation.notes
                    },
                    "items": [
                        {
                            "id": item.id,
                            "quotation_id": item.quotation_id,
                            "item_desc": item.item_desc,
                            "unit": item.unit,
                            "quantity": item.quantity,
                            "unit_price": float(item.unit_price),
                            "amount": float(item.amount) if item.amount else None
                        }
                        for item in items
                    ]
                }, ensure_ascii=False)

            elif operation == "generate_number":
                quo_no = service.generate_quotation_number(
                    params["job_no"],
                    params.get("is_revision", False)
                )
                return json.dumps(quo_no)

            elif operation == "get_by_quo_no":
                # Get quotation header by quo_no (should be unique)
                quotation = service.get_quotation_by_quo_no(params["quo_no"])
                if not quotation:
                    return json.dumps({"error": f"Quotation not found: {params['quo_no']}"})

                return json.dumps({
                    "id": quotation.id,
                    "quo_no": quotation.quo_no,
                    "client_id": quotation.client_id,
                    "project_name": quotation.project_name,
                    "date_issued": quotation.date_issued.isoformat(),
                    "status": quotation.status,
                    "currency": quotation.currency,
                    "revision_no": quotation.revision_no,
                    "valid_until": quotation.valid_until.isoformat() if quotation.valid_until else None,
                    "notes": quotation.notes,
                    "created_at": quotation.created_at.isoformat() if quotation.created_at else None,
                    "updated_at": quotation.updated_at.isoformat() if quotation.updated_at else None
                }, ensure_ascii=False)

            elif operation == "get_by_job_no":
                quotations = service.get_by_job_no(params["job_no"])
                return json.dumps([
                    {
                        "id": q.id,
                        "quo_no": q.quo_no,
                        "date_issued": q.date_issued.isoformat(),
                        "project_name": q.project_name,
                        "status": q.status,
                        "currency": q.currency,
                        "revision_no": q.revision_no
                    }
                    for q in quotations
                ], ensure_ascii=False)

            elif operation == "search":
                quotations = service.search_by_project(
                    params["project_name_pattern"],
                    params.get("limit", 10)
                )
                return json.dumps([
                    {
                        "id": q.id,
                        "quo_no": q.quo_no,
                        "project_name": q.project_name,
                        "date_issued": q.date_issued.isoformat(),
                        "status": q.status,
                        "currency": q.currency
                    }
                    for q in quotations
                ], ensure_ascii=False)

            elif operation == "update":
                quotation_ids = params.pop("quotation_ids")
                quotations = service.update_quotation(quotation_ids, **params)
                session.commit()
                return json.dumps([
                    {
                        "id": q.id,
                        "quo_no": q.quo_no,
                        "project_name": q.project_name,
                        "status": q.status,
                        "date_issued": q.date_issued.isoformat(),
                        "currency": q.currency
                    }
                    for q in quotations
                ], ensure_ascii=False)

            elif operation == "get_total":
                # Get quotation with items and calculate total
                quotation = service.get_quotation_by_quo_no(params["quo_no"])
                if not quotation:
                    return json.dumps({"error": f"Quotation not found: {params['quo_no']}"})

                # Refresh to load items
                session.refresh(quotation)
                total = sum(item.amount or 0 for item in quotation.items)
                item_count = len(quotation.items)

                return json.dumps({
                    "total": float(total),
                    "item_count": item_count
                })

            elif operation == "list_all":
                quotations = service.list_all(
                    params.get("order_by", "date_issued"),
                    params.get("descending", True),
                    params.get("limit")
                )
                return json.dumps([
                    {
                        "id": q.id,
                        "quo_no": q.quo_no,
                        "project_name": q.project_name,
                        "date_issued": q.date_issued.isoformat(),
                        "status": q.status,
                        "currency": q.currency,
                        "revision_no": q.revision_no
                    }
                    for q in quotations
                ], ensure_ascii=False)

            else:
                return json.dumps({
                    "error": f"Unknown operation: {operation}"
                })

    except Exception as e:
        error_msg = f"Error in quotation_service_tool: {str(e)}"
        print(f"[ERROR][quotation_service_tool] {error_msg}")
        return json.dumps({"error": error_msg})
