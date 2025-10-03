from datetime import datetime

from langchain.schema import AIMessage
import os
from app.llm.invoke_llm import invoke_llm
from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.prompt.quotation_html_render_prompt_template import QUOTATION_HTML_RENDER_PROMPT_TEMPLATE


def quotation_html_renderer_node(state: FinanceAgentState):
    print("[Handler][quotation_html_renderer_node]")

    try:
        # Validate inputs
        if not state.quotation_info:
            error_msg = "quotation_info is empty"
            print(f"[HTML STATE ERROR] {error_msg}")
            return {
                "messages": [AIMessage(content=error_msg)]
            }

        if not state.quotation_file_names:
            error_msg = "quotation_file_names is missing or empty"
            print(f"[HTML STATE ERROR] {error_msg}")
            return {
                "messages": [AIMessage(content=error_msg)]
            }

        # Read HTML template
        html_template_path = "/Users/keven/Desktop/product_v01/html/quotation_html_template.html"
        with open(html_template_path, "r", encoding="utf-8") as f:
            html_template = f.read()

        # Setup output directory
        html_file_dir = "/Users/keven/Desktop/product_v01/app/finance_agent/quotation_html_file"
        os.makedirs(html_file_dir, exist_ok=True)

        # Process each quotation
        generated_html_files = []

        for idx, (quotation_data, file_name) in enumerate(zip(state.quotation_info, state.quotation_file_names), 1):
            print(f"\n📄 Processing HTML {idx}/{len(state.quotation_file_names)}: {file_name}")

            # Prepare the prompt for single quotation
            system_prompt = QUOTATION_HTML_RENDER_PROMPT_TEMPLATE.format(
                html_template=html_template,
                quotation_info=[quotation_data],  # Pass as single-item list
                quotation_file_name=file_name,
                current_date_str=datetime.now().strftime("%Y-%m-%d")
            )

            # Invoke LLM to generate HTML
            try:
                parsed_response = invoke_llm(system_prompt)
                html_content = parsed_response.get('html_content', "")

                
            except Exception as llm_error:
                error_msg = f"Error generating HTML for {file_name}: {llm_error}"
                print(f"[HTML LLM ERROR] {error_msg}")
                continue

            # Generate HTML file name (replace .csv with .html)
            html_file_name = file_name.replace('.csv', '.html')
            html_file_path = f"{html_file_dir}/{html_file_name}"

            # Check if file already exists
            if os.path.exists(html_file_path):
                print(f"[HTML FILE EXISTS] HTML file already exists: {html_file_path}")

            # Write HTML to file
            try:
                with open(html_file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"[HTML WRITE SUCCESS] HTML file written to {html_file_path}")
                generated_html_files.append(html_file_name)
                
            except Exception as write_error:
                error_msg = f"Error writing HTML file {html_file_name}: {write_error}"
                print(f"[HTML WRITE ERROR] {error_msg}")
                continue

        if not generated_html_files:
            error_msg = "No HTML files were successfully generated"
            print(f"[HTML PROCESS ERROR] {error_msg}")
            return {
                "messages": [AIMessage(content=error_msg)]
            }

        success_msg = f"Successfully generated {len(generated_html_files)} HTML file(s)"
        print(f"[HTML PROCESS SUCCESS] {success_msg}")

        return {
            "messages": [AIMessage(content=success_msg)]
        }

    except Exception as e:
        import traceback
        error_msg = f"[Error][quotation_html_renderer_node]: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return {
            "messages": [AIMessage(content=error_msg)]
        }
