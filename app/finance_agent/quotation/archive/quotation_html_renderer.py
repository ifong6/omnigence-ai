from datetime import datetime

from langchain.schema import AIMessage
from app.llm.invoke_gemini_llm_streaming import invoke_gemini_llm_streaming
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
                parsed_response = invoke_gemini_llm_streaming(system_prompt)
                html_content = parsed_response.get('html_content', "")

                # Generate HTML file name (replace .csv with .html)
                html_file_name = file_name.replace('.csv', '.html')
                generated_html_files.append(html_file_name)
                print(f"[HTML GENERATION SUCCESS] HTML generated for {file_name}")

            except Exception as llm_error:
                error_msg = f"Error generating HTML for {file_name}: {llm_error}"
                print(f"[HTML LLM ERROR] {error_msg}")
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
