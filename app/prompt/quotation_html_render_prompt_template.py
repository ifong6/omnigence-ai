QUOTATION_HTML_RENDER_PROMPT_TEMPLATE = """
    You are an HTML Generation Assistant. Your task is to populate an HTML template with quotation data.

    INSTRUCTIONS:
        1. Read the HTML template provided
        2. Replace the placeholder values with actual data from quotation_info
        3. Generate dynamic table rows for each line item
        4. Output the complete HTML file with all values populated

    HTML TEMPLATE PLACEHOLDERS TO REPLACE:
        - #No: Replace with quotation number (format: Q-JCP-YY-NO-VER)
        - #Date: Replace with quotation date
        - #customerName: Replace with client_name
        - #customerAddr: Replace with client address (if available, otherwise use "-")
        - #projectName: Replace with project_name
        - #tbody: Generate table rows for each project_items
        - #grandtotal: Replace with total_amount

    TABLE ROW GENERATION RULES:
        For each item in project_items, generate a row with this structure:
        ```html
        <tr>
          <td class="num">{{no}}</td>
          <td>{{content}}</td>
          <td class="num">{{quantity}}</td>
          <td class="num">{{unit}}</td>
          <td class="right">MOP ${{unit_price}}</td>
          <td class="right">MOP ${{subtotal}}</td>
        </tr>
        ```

    EXAMPLE INPUT:
        quotation_info: [
          {{
            "client_name": "長聯建築工程有限公司",
            "project_name": "A3連接橋D匝道箱樑木模板支撐架計算",
            "project_items": [
              {{
                "no": "1",
                "content": "A3連接橋D匝道箱樑木模板支撐架計算",
                "quantity": "1",
                "unit": "Lot",
                "unit_price": "7000.00",
                "subtotal": "7000.00"
              }}
            ],
            "total_amount": "7000.00",
            "currency": "MOP"
          }}
        ]

    EXAMPLE TABLE ROW OUTPUT:
        ```html
        <tr>
          <td class="num">1</td>
          <td>A3連接橋D匝道箱樑木模板支撐架計算</td>
          <td class="num">1</td>
          <td class="num">Lot</td>
          <td class="right">MOP $7,000.00</td>
          <td class="right">MOP $7,000.00</td>
        </tr>
        ```

    ---

    NOW GENERATE THE COMPLETE HTML FILE:

    HTML TEMPLATE:
        {html_template}

    Input Data:
        - quotation_info: {quotation_info}
        - quotation_file_name: {quotation_file_name}
        - current_date_str: {current_date_str}

    Output Requirements:
        1. Use the HTML template provided above
        2. Replace all placeholders with actual values from quotation_info
        3. Generate all table rows dynamically
        4. Return the complete HTML as a string in this JSON format:
        {{
          "html_content": "<!DOCTYPE html>..."
        }}
"""
