"""
Invoice HTML renderer for generating invoice HTML from invoice data.

This module provides functionality to populate the invoice HTML template
with actual invoice data.
"""

from typing import Dict, Any
from datetime import datetime


def render_invoice_html(invoice_data: Dict[str, Any]) -> str:
    """
    Render invoice data into HTML format.

    This function takes invoice data and populates the invoice HTML template
    with the actual values.

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
        str: Populated HTML string ready for PDF conversion

    Examples:
        >>> invoice_data = {
        ...     "inv_no": "INV-JCP-25-01-1",
        ...     "date_issued": "2025-01-20",
        ...     "client": {"name": "Ñå", "address": "...", "phone": "..."},
        ...     "items": [...],
        ...     "total_amount": 10000.0
        ... }
        >>> html = render_invoice_html(invoice_data)
    """
    # Read the invoice HTML template
    with open('html/invoice_html_template.html', 'r', encoding='utf-8') as f:
        html_template = f.read()

    # Extract data
    inv_no = invoice_data.get('inv_no', '[INV]-JCP-YY-NO')
    date_issued = invoice_data.get('date_issued', datetime.now().strftime('%Y-%m-%d'))
    due_date = invoice_data.get('due_date', '')
    project_name = invoice_data.get('project_name', '')
    client = invoice_data.get('client', {})
    client_name = client.get('name', '')
    client_address = client.get('address', '')
    client_phone = client.get('phone', '')
    items = invoice_data.get('items', [])
    total_amount = invoice_data.get('total_amount', 0.0)
    currency = invoice_data.get('currency', 'MOP')
    notes = invoice_data.get('notes', '')

    # Populate template placeholders
    html = html_template.replace('{{current_date_str}}', date_issued)
    html = html.replace('{client_name}', client_name)
    html = html.replace('{client_phone}', client_phone)
    html = html.replace('{client_address}', client_address)

    # Set invoice number and project name
    html = html.replace('[INV]-JCP-YY-NO-VER', inv_no)
    html = html.replace('(example: A3#¥KDS±(!/¶—)', project_name)

    # Build table rows for items
    table_rows = ""
    for idx, item in enumerate(items, 1):
        description = item.get('invoice_item_description', '')
        quantity = item.get('amount', 1)
        unit = item.get('unit', 'Lot')
        # Calculate unit price from subtotal and quantity
        subtotal = float(item.get('sub_amount', 0))
        unit_price = subtotal / float(quantity) if float(quantity) > 0 else 0

        table_rows += f"""
              <tr>
                <td class="num">{idx}</td>
                <td>{description}</td>
                <td class="num">{quantity}</td>
                <td class="num">{unit}</td>
                <td class="right">MOP ${unit_price:,.2f}</td>
                <td class="right">MOP ${subtotal:,.2f}</td>
                <td></td>
              </tr>
        """

    # Replace the seed item in template with actual items
    # Find and replace the tbody content
    tbody_start = html.find('<tbody id="tbody">')
    tbody_end = html.find('</tbody>')
    if tbody_start != -1 and tbody_end != -1:
        html = html[:tbody_start + len('<tbody id="tbody">')] + table_rows + html[tbody_end:]

    # Update total amount
    html = html.replace(
        '<span id="grandtotal"><strong>MOP $0.00</strong></span>',
        f'<span id="grandtotal"><strong>{currency} ${float(total_amount):,.2f}</strong></span>'
    )

    # Add notes if provided
    if notes:
        html = html.replace(
            ',|hìûU‡öK8ÊÐ¤å\;',
            f'{notes}<br />,|hìûU‡öK8ÊÐ¤å\;'
        )

    # Hide the edit buttons for PDF export
    html = html.replace(
        '<div class="btns">',
        '<div class="btns" style="display:none;">'
    )

    return html
