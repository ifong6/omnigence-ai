import datetime
import re
import os

def save_quotation_html(filled_html: str, quotation_json: dict, output_dir: str):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    company_name = quotation_json.get("customer", "unknown")
    company_name = re.sub(r'[^a-zA-Z0-9_-]', '_', company_name)
    output_path = os.path.join(output_dir, f"official_quotation_{company_name}_{date_str}.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(filled_html)

    print(f"✅ Filled quotation saved at: {output_path}")
    return output_path
