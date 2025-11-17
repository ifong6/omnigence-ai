"""
Tool for formatting invoice data for UI display.

This module provides functionality to format invoice data from the database
into a structure suitable for frontend rendering.
"""

from typing import Any, Dict
from app.finance_agent.invoice.tools.query_tools.find_invoice_by_no import find_invoice_by_no


def output_invoice_info_for_ui(invoice_no: str) -> Dict[str, Any]:
    """
    Format invoice data for UI rendering.

    This tool retrieves invoice data from the database and formats it
    for display in the frontend application.

    Args:
        invoice_no: Invoice number (e.g., "INV-JCP-25-01-1")

    Returns:
        dict: Formatted invoice data ready for UI with structure:
            {
                "success": True,
                "invoice": {
                    "no": "INV-JCP-25-01-1",
                    "date": "2025-01-20",
                    "due_date": "2025-02-20",
                    "project_name": "A8項目模板計算",
                    "job_no": "JCP-25-01-1",
                    "quotation_no": "Q-JCP-25-01-q1",
                    "client_name": "金輝工程有限公司",
                    "client_address": "...",
                    "client_phone": "...",
                    "status": "pending",
                    "notes": "...",
                    "invoiceItems": [
                        {
                            "no": "1",
                            "content": "樑模板計算",
                            "quantity": "1",
                            "unit": "Lot",
                            "unit_price": "5000",
                            "subtotal": "5000"
                        },
                        ...
                    ],
                    "total_amount": "10000",
                    "currency": "MOP"
                }
            }

        On error: {"error": "error message"}

    Examples:
        >>> output_invoice_info_for_ui("INV-JCP-25-01-1")
        {
            "success": True,
            "invoice": {...}
        }
    """
    try:
        # Fetch invoice data from database
        result = find_invoice_by_no(invoice_no)

        if "error" in result:
            return result

        # Extract invoice data
        invoice_data = result.get("invoice_data", {})
        client = invoice_data.get("client", {})
        items = invoice_data.get("items", [])

        # Format for UI
        formatted_items = []
        for idx, item in enumerate(items, 1):
            quantity = float(item.get("amount", 1))
            subtotal = float(item.get("sub_amount", 0))
            unit_price = subtotal / quantity if quantity > 0 else 0

            formatted_items.append({
                "no": str(idx),
                "content": item.get("invoice_item_description", ""),
                "quantity": str(int(quantity)),
                "unit": item.get("unit", "Lot"),
                "unit_price": str(int(unit_price)),
                "subtotal": str(int(subtotal))
            })

        # Build final output structure
        invoice_output = {
            "no": invoice_data.get("inv_no", ""),
            "date": str(invoice_data.get("date_issued", "")),
            "due_date": str(invoice_data.get("due_date", "")) if invoice_data.get("due_date") else "",
            "project_name": invoice_data.get("project_name", ""),
            "job_no": invoice_data.get("job_no", ""),
            "quotation_no": invoice_data.get("quotation_no", ""),
            "client_name": client.get("name", ""),
            "client_address": client.get("address", ""),
            "client_phone": client.get("phone", ""),
            "status": invoice_data.get("status", "pending"),
            "notes": invoice_data.get("notes", ""),
            "invoiceItems": formatted_items,
            "total_amount": str(int(float(invoice_data.get("total_amount", 0)))),
            "currency": invoice_data.get("currency", "MOP")
        }

        return {
            "success": True,
            "invoice": invoice_output
        }

    except Exception as e:
        error_msg = f"Error formatting invoice for UI: {str(e)}"
        print(f"[ERROR][output_invoice_info_for_ui] {error_msg}")
        return {"error": error_msg}
