from langchain.schema import AIMessage
import datetime
import os
from app.llm.invoke_llm import invoke_llm
from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.prompt.quotation_prompt_template import EXTRACT_QUOTATION_PROMPT_TEMPLATE, QuotationInfoExtractOutput
from app.prompt.quotation_info_transform_prompt_template import QUOTATION_INFO_CSV_TRANSFORM_PROMPT_TEMPLATE
from app.s3_bucket.upload_file_to_s3 import upload_file_to_s3
import re

def quotation_info_ETL_node(state: FinanceAgentState):
    print("[Handler][quotation_info_ETL_node]")

    try:
        # 1) Get extracted info and messages
        system_prompt_extract = EXTRACT_QUOTATION_PROMPT_TEMPLATE.format(user_input=state.user_input)
        parsed_response_extract = invoke_llm(system_prompt_extract, QuotationInfoExtractOutput)

        # Handle dict response
        extracted_quotation_info = parsed_response_extract.get('quotation_info', [])
        llm_result_msg = parsed_response_extract.get('messages', ["No message"])
        print(f"llm_result_msg: {llm_result_msg}")
        print(f"📊 Total quotations to process: {len(extracted_quotation_info)}")

        # Validate we have quotations to process
        if not extracted_quotation_info:
            raise ValueError("No quotation info extracted")

        # Setup for file generation
        current_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        current_year = datetime.datetime.now().strftime("%y")
        version_str = "1"
        csv_dir = "/Users/keven/Desktop/product_v01/app/finance_agent/quotation_csv_file"
        os.makedirs(csv_dir, exist_ok=True)

        # Get latest job number from existing CSV files
        max_job_no = 0
        for filename in os.listdir(csv_dir):
            if filename.endswith('.csv'):
                # Match pattern: quotation_Q-JCP-YY-NO-VER.csv
                match = re.search(r'Q-JCP-\d{2}-(\d+)-\d+\.csv', filename)
                if match:
                    job_no = int(match.group(1))
                    max_job_no = max(max_job_no, job_no)

        # Process each quotation
        generated_file_names = []
        current_job_no = max_job_no

        for idx, single_quotation in enumerate(extracted_quotation_info, 1):
            print(f"\n📄 Processing quotation {idx}/{len(extracted_quotation_info)}")

            # Increment job number for each quotation
            current_job_no += 1
            job_no_str = f"{current_job_no:02d}"
            quotation_no = f"Q-JCP-{current_year}-{job_no_str}-{version_str}"

            # 2) Transform single quotation to CSV
            system_prompt_transform = QUOTATION_INFO_CSV_TRANSFORM_PROMPT_TEMPLATE.format(
                quotation_info=[single_quotation],  # Pass as single-item list
                current_date_str=current_date_str,
                current_year=current_year,
                job_no_str=job_no_str,
                version_str=version_str
            )
            parsed_response_transform = invoke_llm(system_prompt_transform)
            csv_data = parsed_response_transform.get('csv_data', "")

            # 3a) Write csv_data to .csv file
            file_name = f"quotation_{quotation_no}.csv"
            file_path = f"{csv_dir}/{file_name}"

            # Check if file already exists
            if os.path.exists(file_path):
                print(f"⚠️ File already exists: {file_path}")

            with open(file_path, "w") as f:
                f.write(csv_data)
            print(f"✅ csv_data written to {file_path}")

            # 3b) Upload to S3
            upload_file_to_s3(file_path, file_name)

            generated_file_names.append(file_name)

        print(f"\n✅ Successfully processed {len(generated_file_names)} quotation(s)")

        return {
            "quotation_info": extracted_quotation_info,
            "quotation_file_names": generated_file_names,
            "messages": [AIMessage(content=f"{llm_result_msg}. Generated {len(generated_file_names)} quotation csv file(s).")]
        }
        
    except Exception as e:
        error_msg = f"[Error][quotation_info_ETL_node]: {str(e)}"
        print(error_msg)
        return {
            "messages": [AIMessage(content=error_msg)]
        }

