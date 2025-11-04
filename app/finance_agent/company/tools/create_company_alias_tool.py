"""
Tool for creating intelligent company aliases using LLM.

This tool takes a company name and uses an LLM to generate a smart alias
for quick search, including abbreviations, common names, and alternative spellings.
"""

from pydantic import BaseModel
from typing import Optional
import json
from app.llm.invoke_openai_llm import invoke_openai_llm
from database.supabase.db_connection import execute_query
from database.supabase.db_enum import DBTable_Enum


class CompanyAliasOutput(BaseModel):
    """Output structure for company alias generation."""
    alias: str


ALIAS_GENERATION_PROMPT = """
You are an intelligent assistant that generates concise, searchable aliases for company names.

Company Name: {company_name}

INSTRUCTIONS:
1. Generate a short, memorable alias for this company that would help users search for it quickly
2. Consider common abbreviations, acronyms, or shortened forms
3. For Chinese companies, consider:
   - Simplified version of the name
   - Common abbreviations (e.g., 澳門科技大學 -> 澳科大, 科大)
   - Mixed Chinese-English versions if applicable
4. For English companies, consider:
   - Acronyms (e.g., International Business Machines -> IBM)
   - Shortened forms (e.g., Microsoft Corporation -> Microsoft)
5. The alias should be 2-8 characters long when possible
6. If the company name is already short (<=8 chars), you may return a slightly different variation or the same name

Examples:
- 澳門科技大學 → 澳科大
- 金龍酒店 → 金龍
- International Business Machines Corporation → IBM
- Microsoft Corporation → Microsoft
- 中國建設銀行 → 建行

Generate ONE clear alias for the company. Output ONLY the alias, nothing else.
"""


def create_company_alias_tool(tool_input) -> dict:
    """
    Generate and assign an intelligent alias to a company using LLM.

    This tool helps create searchable aliases for companies to enable quick search.
    The LLM analyzes the company name and generates appropriate abbreviations,
    acronyms, or shortened forms.

    Args:
        tool_input: Either a company name (string) or company ID (int)

    Returns:
        dict: Updated company information with the new alias, or error dict

    Examples:
        >>> create_company_alias_tool("澳門科技大學")
        {"id": 1, "name": "澳門科技大學", "alias": "澳科大", "status": "alias_created"}

        >>> create_company_alias_tool({"company_id": 5})
        {"id": 5, "name": "金龍酒店", "alias": "金龍", "status": "alias_created"}
    """

    # Handle different input types from LangChain
    if isinstance(tool_input, str):
        # Try to parse as int first (company_id)
        try:
            company_id = int(tool_input)
            company_name = None
        except ValueError:
            # It's a company name
            company_id = None
            company_name = tool_input
    elif isinstance(tool_input, int):
        company_id = tool_input
        company_name = None
    elif isinstance(tool_input, dict):
        company_id = tool_input.get("company_id")
        company_name = tool_input.get("company_name")
    else:
        return {
            "error": "Invalid input type. Expected string, int, or dict",
            "status": "error"
        }

    if not company_id and not company_name:
        return {
            "error": "Either company_id or company_name must be provided",
            "status": "error"
        }

    try:
        # Step 1: Find the company in the database
        if company_id:
            query = f"""
                SELECT id, name, alias, address, phone
                FROM {DBTable_Enum.COMPANY_TABLE}
                WHERE id = %s
                LIMIT 1
            """
            params = (company_id,)
        else:
            query = f"""
                SELECT id, name, alias, address, phone
                FROM {DBTable_Enum.COMPANY_TABLE}
                WHERE name = %s
                LIMIT 1
            """
            params = (company_name.strip() if company_name else None,)

        rows = execute_query(query, params=params, fetch=True)

        if not rows:
            return {
                "error": f"Company not found",
                "status": "not_found"
            }

        company = dict(rows[0])
        company_id = company["id"]
        company_name = company["name"]
        current_alias = company.get("alias")

        # Step 2: Use LLM to generate intelligent alias
        print(f"[INFO][create_company_alias_tool] Generating alias for company: {company_name}")

        prompt = ALIAS_GENERATION_PROMPT.format(company_name=company_name)
        alias_output = invoke_openai_llm(prompt, config=CompanyAliasOutput)
        generated_alias = alias_output.alias.strip()

        print(f"[INFO][create_company_alias_tool] Generated alias: {generated_alias}")

        # Step 3: Update the company with the generated alias
        update_query = f"""
            UPDATE {DBTable_Enum.COMPANY_TABLE}
            SET alias = %s
            WHERE id = %s
            RETURNING id, name, alias, address, phone
        """

        updated_rows = execute_query(
            update_query,
            params=(generated_alias, company_id),
            fetch=True
        )

        if updated_rows:
            result = dict(updated_rows[0])
            result["status"] = "alias_created" if not current_alias else "alias_updated"
            result["message"] = f"Successfully generated alias '{generated_alias}' for company '{company_name}'"
            return result
        else:
            return {
                "error": "Failed to update company with generated alias",
                "status": "error"
            }

    except Exception as e:
        error_msg = f"Error generating company alias: {str(e)}"
        print(f"[ERROR][create_company_alias_tool] {error_msg}")
        return {
            "error": error_msg,
            "status": "error"
        }
