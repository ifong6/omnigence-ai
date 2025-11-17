"""
Invoice PDF builder for generating PDF documents from invoice data.

This module provides functionality to generate PDF invoices using WeasyPrint.
"""

from typing import Dict, Any
from weasyprint import HTML
from io import BytesIO
from app.finance_agent.invoice_html_renderer import render_invoice_html


def build_invoice_pdf(invoice_data: Dict[str, Any]) -> bytes:
    """
    Build a PDF document from invoice data.

    This function takes invoice data, renders it as HTML, and converts it to PDF
    using WeasyPrint.

    Args:
        invoice_data: Dictionary containing invoice information with structure:
            {
                "inv_no": str,
                "date_issued": str,
                "due_date": str,
                "project_name": str,
                "client": {
                    "name": str,
                    "address": str,
                    "phone": str
                },
                "items": [
                    {
                        "invoice_item_description": str,
                        "amount": float,
                        "unit": str,
                        "sub_amount": float
                    },
                    ...
                ],
                "total_amount": float,
                "currency": str,
                "notes": str
            }

    Returns:
        bytes: PDF document as bytes

    Examples:
        >>> invoice_data = {
        ...     "inv_no": "INV-JCP-25-01-1",
        ...     "date_issued": "2025-01-20",
        ...     "client": {"name": "Ñå", "address": "...", "phone": "..."},
        ...     "items": [...],
        ...     "total_amount": 10000.0
        ... }
        >>> pdf_bytes = build_invoice_pdf(invoice_data)
        >>> with open('invoice.pdf', 'wb') as f:
        ...     f.write(pdf_bytes)
    """
    try:
        # Render invoice data to HTML
        html_content = render_invoice_html(invoice_data)

        # Convert HTML to PDF using WeasyPrint
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)

        return pdf_file.read()

    except Exception as e:
        error_msg = f"Error building invoice PDF: {str(e)}"
        print(f"[ERROR][build_invoice_pdf] {error_msg}")
        raise


def save_invoice_pdf(invoice_data: Dict[str, Any], output_path: str) -> str:
    """
    Build and save an invoice PDF to a file.

    This is a convenience function that builds the PDF and saves it to disk.

    Args:
        invoice_data: Dictionary containing invoice information
        output_path: Path where the PDF should be saved

    Returns:
        str: Path to the saved PDF file

    Examples:
        >>> invoice_data = {...}
        >>> path = save_invoice_pdf(invoice_data, '/tmp/invoice.pdf')
        >>> print(f"Invoice saved to: {path}")
    """
    try:
        pdf_bytes = build_invoice_pdf(invoice_data)

        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)

        print(f"[SUCCESS] Invoice PDF saved to: {output_path}")
        return output_path

    except Exception as e:
        error_msg = f"Error saving invoice PDF: {str(e)}"
        print(f"[ERROR][save_invoice_pdf] {error_msg}")
        raise
