from typing import Any, Dict
import json
from sqlmodel import Session
from app.db.engine import engine
from app.services.impl import CompanyServiceImpl

def company_service_tool(operation: str, params: Dict[str, Any]) -> str:
    """
    A high-level service wrapper for company operations.

    Args:
        operation: Operation name (get_or_create, search, get_by_id, update, list_all)
        params: Operation parameters as dict

    Returns:
        JSON string with operation result or error

    Operations:
        1. get_or_create: Get existing or create new company
           params: {name: str, address?: str, phone?: str, alias?: str}
           returns: {id: int, name: str, address?: str, phone?: str, alias?: str}

        2. search: Search companies by name/alias
           params: {search_term: str, limit?: int}
           returns: [{id, name, address, phone, alias}, ...]

        3. get_by_id: Get company by ID
           params: {company_id: int}
           returns: {id: int, name: str, ...} or null

        4. update: Update company
           params: {company_id: int, name?: str, address?: str, phone?: str, alias?: str}
           returns: {id: int, name: str, ...} or null

        5. list_all: List all companies
           params: {limit?: int}
           returns: [{id, name, address, phone, alias}, ...]

    Examples:
        >>> company_service_tool("get_or_create", {"name": "澳門科技大學"})
        '{"id": 15, "name": "澳門科技大學", "address": null, ...}'

        >>> company_service_tool("search", {"search_term": "科技"})
        '[{"id": 15, "name": "澳門科技大學", ...}]'
    """
    print(f"[DEBUG][company_service_tool] operation={operation}")
    print(f"[DEBUG][company_service_tool] params={params}")

    try:
        with Session(engine) as session:
            service = CompanyServiceImpl(session)

            if operation == "get_or_create":
                company = service.get_or_create(**params)
                session.commit()
                return json.dumps({
                    "id": company.id,
                    "name": company.name,
                    "address": company.address,
                    "phone": company.phone,
                    "alias": company.alias
                }, ensure_ascii=False)

            elif operation == "search":
                companies = service.search_by_name(
                    params.get("search_term", ""),
                    params.get("limit", 10)
                )
                return json.dumps([
                    {
                        "id": c.id,
                        "name": c.name,
                        "address": c.address,
                        "phone": c.phone,
                        "alias": c.alias
                    }
                    for c in companies
                ], ensure_ascii=False)

            elif operation == "get_by_id":
                company = service.get_by_id(params["company_id"])
                if not company:
                    return json.dumps(None)
                return json.dumps({
                    "id": company.id,
                    "name": company.name,
                    "address": company.address,
                    "phone": company.phone,
                    "alias": company.alias
                }, ensure_ascii=False)

            elif operation == "update":
                company_id = params.pop("company_id")
                company = service.update(company_id, **params)
                session.commit()
                if not company:
                    return json.dumps(None)
                return json.dumps({
                    "id": company.id,
                    "name": company.name,
                    "address": company.address,
                    "phone": company.phone,
                    "alias": company.alias
                }, ensure_ascii=False)

            elif operation == "list_all":
                companies = service.list_all(params.get("limit"))
                return json.dumps([
                    {
                        "id": c.id,
                        "name": c.name,
                        "address": c.address,
                        "phone": c.phone,
                        "alias": c.alias
                    }
                    for c in companies
                ], ensure_ascii=False)

            else:
                return json.dumps({
                    "error": f"Unknown operation: {operation}"
                })

    except Exception as e:
        error_msg = f"Error in company_service_tool: {str(e)}"
        print(f"[ERROR][company_service_tool] {error_msg}")
        return json.dumps({"error": error_msg})
