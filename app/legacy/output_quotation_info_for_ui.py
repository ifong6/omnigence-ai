from app.prompt.quotation_prompt_template import ProjectItem

def output_quotation_info_for_ui(
    quotation_no: str,
    revision_str: str,
    client_name: str,
    client_address: str,
    client_phone: str,
    project_name: str,
    date: str,
    project_items: list[ProjectItem],
    total_amount: str,
    currency: str,
) -> dict:
    """
    Output all quotation information for the UI to render the quotation sheet.

    This is the FINAL step that consolidates all quotation data for rendering.

    Args:
        quotation_no: The quotation number (e.g., "Q-JCP-25-01-q1")
        revision_str: The revision string (e.g., "00", "01", "02")
        client_name: Client/company name
        client_address: Client address
        client_phone: Client phone number
        project_name: Name of the project
        date: Quotation date
        project_items: List of project items, each containing:
            - no: Item number
            - content: Item description
            - quantity: Quantity
            - unit: Unit of measurement
            - unit_price: Price per unit
            - subtotal: Subtotal for the item
        total_amount: Total amount for the quotation
        currency: Currency code (e.g., "MOP", "USD")
        
    Returns:
        dict: Complete quotation information structured for UI rendering
    """

    # Return all data as a flat dictionary
    return {
        "quotation_no": quotation_no,
        "revision": revision_str,
        "date": date,
        "project_name": project_name,
        "client_name": client_name,
        "client_address": client_address,
        "client_phone": client_phone,
        "project_items": project_items,
        "total_amount": total_amount,
        "currency": currency
    }