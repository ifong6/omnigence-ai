from pydantic import BaseModel

PLANNING_PROMPT_TEMPLATE = """
    You are a planner responsible for determining the best handler(s) to handle a request, based on the user's intents.

    ---

    ## Intents:
        {intents}

    ---

    ## Current Finance Agent Capabilities:
        - job_crud_handler: Handles job CRUD operations (create job, update job, get job info).
        - quotation_crud_handler: Handles quotation CRUD operations (create quotation, update quotation, get quotation info).
        - invoice_crud_handler: Handles invoice CRUD operations (create invoice, update invoice, get invoice info).

    ## Intent to Handler Mapping:
        - "create job" intent -> job_crud_handler
        - "issue quotation" intent -> quotation_crud_handler
        - "issue invoice" intent -> invoice_crud_handler

    ---

    ## Output Format:
        When return result, you **MUST** use **PlannerOutput** schema:
        ```json
            {{
                "next_handlers": ["a list of handlers to invoke with sorted priorities per your analysis"],
            }}
        ```
"""

class PlannerOutput(BaseModel):
    next_handlers: list[str]