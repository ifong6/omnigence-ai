"""
Tool for finding invoice by job number.

This module provides functionality to query invoices by their associated job number.
"""

from typing import Any, Dict, List
from app.finance_agent.utils.constants import (
    DatabaseSchema,
    InvoiceFields,
    CompanyFields,
    ErrorMessages
)
from app.finance_agent.utils.db_helper import DatabaseError
from app.postgres.db_connection import execute_query


def find_invoice_by_job_no(job_no: str) -> Dict[str, Any]:
    """
    Find invoice by job number.

    This tool queries the database for all invoice items with the given
    job number and returns them with client information.

    Args:
        job_no: Job number to search for (e.g., "JCP-25-01-1")

    Returns:
        dict: Invoice information with structure:
            {
                "success": True,
                "job_no": "JCP-25-01-1",
                "items_found": 2,
                "invoice_data": {
                    "inv_no": "INV-JCP-25-01-1",
                    "date_issued": "2025-01-20",
                    "due_date": "2025-02-20",
                    "project_name": "A8項目模板計算",
                    "job_no": "JCP-25-01-1",
                    "quotation_no": "Q-JCP-25-01-q1",
                    "total_amount": 10000.0,
                    "currency": "MOP",
                    "status": "pending",
                    "notes": "...",
                    "client": {
                        "id": 1,
                        "name": "金輝工程有限公司",
                        "address": "...",
                        "phone": "..."
                    },
                    "items": [
                        {
                            "id": 1,
                            "invoice_item_description": "樑模板計算",
                            "sub_amount": 5000.0,
                            "amount": 1.0,
                            "unit": "Lot"
                        },
                        ...
                    ]
                }
            }

        On error or not found: {"error": "error message"}

    Examples:
        >>> find_invoice_by_job_no("JCP-25-01-1")
        {
            "success": True,
            "job_no": "JCP-25-01-1",
            "items_found": 2,
            "invoice_data": {...}
        }

        >>> find_invoice_by_job_no("JCP-NOTFOUND")
        {"error": "No invoice found with job_no='JCP-NOTFOUND'"}
    """
    try:
        if not job_no:
            raise ValueError("job_no is required")

        # Query invoice items with client information
        rows = execute_query(
            f"""
            SELECT
                i.{InvoiceFields.ID},
                i.{InvoiceFields.INV_NO},
                i.{InvoiceFields.DATE_ISSUED},
                i.{InvoiceFields.DUE_DATE},
                i.{InvoiceFields.PROJECT_NAME},
                i.{InvoiceFields.JOB_NO},
                i.{InvoiceFields.QUOTATION_NO},
                i.{InvoiceFields.INVOICE_ITEM_DESCRIPTION},
                i.{InvoiceFields.SUB_AMOUNT},
                i.{InvoiceFields.TOTAL_AMOUNT},
                i.{InvoiceFields.CURRENCY},
                i.{InvoiceFields.STATUS},
                i.{InvoiceFields.AMOUNT},
                i.{InvoiceFields.UNIT},
                i.{InvoiceFields.NOTES},
                c.{CompanyFields.ID} as client_id,
                c.{CompanyFields.NAME} as client_name,
                c.{CompanyFields.ADDRESS} as client_address,
                c.{CompanyFields.PHONE} as client_phone
            FROM {DatabaseSchema.INVOICE_TABLE} i
            LEFT JOIN {DatabaseSchema.COMPANY_TABLE} c
                ON i.{InvoiceFields.CLIENT_ID} = c.{CompanyFields.ID}
            WHERE i.{InvoiceFields.JOB_NO} = %s
            ORDER BY i.{InvoiceFields.ID}
            """,
            params=(job_no,),
            fetch_results=True
        )

        if not rows:
            return {
                "error": ErrorMessages.RECORD_NOT_FOUND.format(
                    tool="find_invoice_by_job_no",
                    entity="invoice",
                    field="job_no",
                    value=job_no
                )
            }

        # Build response
        first_row = rows[0]
        invoice_data = {
            "inv_no": first_row[InvoiceFields.INV_NO],
            "date_issued": first_row[InvoiceFields.DATE_ISSUED],
            "due_date": first_row[InvoiceFields.DUE_DATE],
            "project_name": first_row[InvoiceFields.PROJECT_NAME],
            "job_no": first_row[InvoiceFields.JOB_NO],
            "quotation_no": first_row[InvoiceFields.QUOTATION_NO],
            "total_amount": first_row[InvoiceFields.TOTAL_AMOUNT],
            "currency": first_row[InvoiceFields.CURRENCY],
            "status": first_row[InvoiceFields.STATUS],
            "notes": first_row[InvoiceFields.NOTES],
            "client": {
                "id": first_row['client_id'],
                "name": first_row['client_name'],
                "address": first_row['client_address'],
                "phone": first_row['client_phone']
            },
            "items": [
                {
                    "id": row[InvoiceFields.ID],
                    "invoice_item_description": row[InvoiceFields.INVOICE_ITEM_DESCRIPTION],
                    "sub_amount": row[InvoiceFields.SUB_AMOUNT],
                    "amount": row[InvoiceFields.AMOUNT],
                    "unit": row[InvoiceFields.UNIT]
                }
                for row in rows
            ]
        }

        return {
            "success": True,
            "job_no": job_no,
            "items_found": len(rows),
            "invoice_data": invoice_data
        }

    except ValueError as e:
        return {"error": str(e)}
    except DatabaseError as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        error_msg = f"Unexpected error finding invoice: {str(e)}"
        print(f"[ERROR][find_invoice_by_job_no] {error_msg}")
        return {"error": error_msg}
