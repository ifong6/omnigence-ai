QUOTATION_INFO_CSV_TRANSFORM_PROMPT_TEMPLATE = """
    You are a Data Transformation Assistant. Your task is to convert nested JSON quotation data into a flat CSV format.
    
    STEP 1: Read the **Conversion Rules** below:
        1. Create one CSV row for each line_item in the JSON
        
        2. Repeat the parent quotation fields (client_name, project_name,total_amount, ..., currency) for each line_item row 
        
        3. quotation_no **MUST** use this format:

            Q-JCP-{current_year}-{job_no_str}-{version_str}

            Where:
            - current_year: 2-digit year (e.g., "25" for 2025)
            - job_no_str: 2-digit job number (e.g., "01", "02")
            - version_str: version number (e.g., "1")
            
        4. Use the exact CSV headers: \
            date, quotation_no, client_name, client_address, project_name,total_amount,no,content,quantity,unit,unit_price,subtotal,currency

    STEP 2: Output **MUST** follow below instructions: \
        - 1: Always include the CSV header row first \
        - 2: Each line_item becomes one CSV data row \
        - 3: Preserve all original values exactly as they appear \
        - 4: Handle multiple quotations by processing each quotation's line_items separately \
        - 5: No quotes around CSV values unless they contain commas \
       
    ----------------------
    
    **Input Example:**
    ```json
    {{
        "client_name": "長聯建築工程有限公司",
        "client_address": "澳門市區",
        "project_name": "A3連接橋D匝道箱樑木模板支撐架計算",
        "project_items": [
          {{
            "no": "1",
            "content": "A3連接橋D匝道箱樑木模板支撐架計算",
            "quantity": "1",
            "unit": "Lot",
            "unit_price": "7000",
            "subtotal": "7000"
          }}
          ],
        "total_amount": "7000",
        "currency": "MOP"
     }}
    ```

    Expected CSV Output:
    ```json
    {{
        "csv_data": 
        {{
            date, quotation_no,client_name,client_address,project_name,total_amount,no,content,quantity,unit,unit_price,subtotal,currency
            2025-01-01,Q-JCP-25-01-1,金輝,澳門市區,金輝A8項目模板計算,10000,1,樑模板計算,1,Lot,5000,5000,MOP
            2025-01-01,Q-JCP-25-01-1,金輝,澳門市區,金輝A8項目模板計算,10000,2,牆體模板計算,1,Lot,5000,5000,MOP
        }},
    }}

    ```

    Now, convert the following JSON quotation data to CSV format:
    - quotation_info:
        {quotation_info}

    - date:
        {current_date_str}

    - current_year:
        {current_year}

    - job_no_str:
        {job_no_str}

    - version_str:
        {version_str}
"""