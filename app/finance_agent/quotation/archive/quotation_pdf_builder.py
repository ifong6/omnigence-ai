import os
from dotenv import load_dotenv
from weasyprint import HTML, CSS
from app.s3_bucket.connection import setup_s3_bucket
from app.finance_agent.utils.inject_print_css import inject_print_css
from langchain.schema import AIMessage
from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState

load_dotenv()

def quotation_pdf_builder_node(state: FinanceAgentState):
    print("[Handler][quotation_pdf_builder_node]")
    try:
        # Check if quotation_file_names exists and is not empty
        if not state.quotation_file_names:
            error_msg = "quotation_file_names is missing or empty"
            print(f"[PDF STATE ERROR] {error_msg}")
            return {
                "messages": [AIMessage(content=error_msg)]
            }

        # 1) Get file_names from state
        file_names = state.quotation_file_names

        # Setup directories
        pdf_output_dir = os.getenv('QUOTATION_PDF_OUTPUT_DIR')
        html_file_dir = os.getenv('QUOTATION_HTML_FILE_DIR')
        os.makedirs(pdf_output_dir, exist_ok=True)

        # Setup S3
        quotation_pdf_bucket = setup_s3_bucket()
        if quotation_pdf_bucket is None:
            error_msg = "Failed to setup S3 bucket"
            print(f"[PDF S3 SETUP ERROR] {error_msg}")
            return {
                "messages": [AIMessage(content=error_msg)]
            }

        s3_folder = os.getenv('S3_QUOTATION_PDF_FOLDER')
        s3_base_url = os.getenv('S3_BASE_URL')

        # Process each file
        pdf_s3_urls = []

        for idx, file_name in enumerate(file_names, 1):
            print(f"\n📄 Processing PDF {idx}/{len(file_names)}: {file_name}")

            # Normalize base name
            base = os.path.basename(file_name)
            if base.endswith(".csv") or base.endswith(".pdf"):
                base = base.rsplit(".", 1)[0]

            html_file_name = f"{base}.html"
            html_file_path = os.path.join(html_file_dir, html_file_name)

            if not os.path.exists(html_file_path):
                error_msg = f"HTML file not found: {html_file_path}"
                print(f"[PDF HTML FILE NOT FOUND] {error_msg}")
                continue

            pdf_file_name = f"{base}.pdf"
            pdf_output_path = os.path.join(pdf_output_dir, pdf_file_name)

            # ---- WeasyPrint render with injected print CSS ----
            try:
                with open(html_file_path, "r", encoding="utf-8") as f:
                    html_text = f.read()

                html_with_css = inject_print_css(html_text)

                # base_url is critical so images/fonts referenced relatively can be resolved
                HTML(string=html_with_css, base_url=html_file_dir).write_pdf(
                    pdf_output_path,
                    stylesheets=[CSS(string="")],  # keep list; extra stylesheets can be appended if needed
                    presentational_hints=True
                )
                print(f"[PDF BUILD SUCCESS] PDF {pdf_file_name} generated locally: {pdf_output_path}")
            except Exception as pdf_error:
                error_msg = f"Error generating PDF for {base}: {pdf_error}"
                print(f"[PDF BUILD ERROR] {error_msg}")
                continue

            # ---- Upload to S3 ----
            try:
                s3_key = f"{s3_folder}/{pdf_file_name}" if s3_folder else pdf_file_name
                quotation_pdf_bucket.upload_file(pdf_output_path, s3_key)
                s3_url = f"{s3_base_url}/{s3_key}" if s3_base_url else s3_key
                print(f"[PDF S3 UPLOAD SUCCESS] Uploaded PDF file to {s3_url}")
                pdf_s3_urls.append(s3_url)
            except Exception as upload_error:
                error_msg = f"Error uploading PDF file {pdf_file_name}: {upload_error}"
                print(f"[PDF S3 UPLOAD ERROR] {error_msg}")
                continue

        if not pdf_s3_urls:
            error_msg = "No PDFs were successfully generated and uploaded"
            print(f"[PDF PROCESS ERROR] {error_msg}")
            return {"messages": [AIMessage(content=error_msg)]}

        success_msg = f"Successfully generated and uploaded {len(pdf_s3_urls)} PDF(s) to S3"
        print(f"[PDF PROCESS SUCCESS] {success_msg}")
        return {"messages": [AIMessage(content=success_msg)], "pdf_s3_urls": pdf_s3_urls}

    except Exception as e:
        error_msg = f"[Error][quotation_pdf_builder_node]: {str(e)}"
        print(error_msg)
        return {"messages": [AIMessage(content=error_msg)]}