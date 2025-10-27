from pydantic import BaseModel
from app.postgres.db_connection import execute_query
from app.llm.invoke_openai_llm import invoke_openai_llm
from datetime import datetime

class JobNumberOutput(BaseModel):
    job_no: list[str]

# ====================
# PROMPT COMPONENTS
# ====================

ROLE = """You are a job number generator. Generate job numbers based on job type."""

CRITICAL_PREFIX_RULE = """
**CRITICAL PREFIX RULE - READ THIS FIRST:**
• Inspection/checking/testing jobs → MUST use prefix "JICP"
• Design/construction/other jobs → MUST use prefix "JCP"
• Inspection-related keywords include: inspection, checking, survey, review, verification, testing, 檢測, 檢查, 巡查, 驗收, 測試
• DO NOT confuse these prefixes. Double-check each job's type before assigning a prefix.
"""

CURRENT_STATE = """
**Current State:**
- Latest job_no in database: "{current_latest_job_no}"
- Current year: 20{current_year}
- Jobs to generate numbers for: {jobs_list}
"""

FORMAT = """
**Job Number Format:** PREFIX-YY-NO-X
"""

INSPECTION_KEYWORDS = """
**Inspection Keywords (use JICP prefix):**
- English: "inspection", "checking", "survey", "review", "verification", "safety check", "testing", "assessment", "audit", "examination"
- Chinese: "檢測", "檢查", "巡查", "驗收", "測試", "審查", "評估", "視察"
"""

PREFIX_RULES = """
**PREFIX Rules (CASE INSENSITIVE):**
- If job_type or job_title contains ANY inspection keyword above → use prefix "JICP"
- Otherwise (design, construction, general projects) → use prefix "JCP"
- CHECK EACH JOB'S TYPE INDIVIDUALLY AND APPLY THE CORRECT PREFIX
"""

YY_RULES = """
**YY:** {current_year} (current year, 2 digits)
"""

NO_RULES = """
**NO (Sequential Number):**
1. If current_latest_job_no is "NONE": start at "01"
2. Otherwise, parse the NO from current_latest_job_no (example: "JCP-25-03-1" means NO is "03")
3. Start at parsed NO + 1, with 2-digit padding (example: "03" becomes "04", "09" becomes "10")
4. For multiple jobs, increment NO by 1 for each subsequent job
"""

X_RULES = """
**X (Sequential Number):**
If there are multiple jobs, use "-1" for first job, "-2" for second job, and so on.
"""

CLASSIFICATION_PROCESS = """
**CLASSIFICATION PROCESS (FOLLOW THESE STEPS):**

For EACH job, follow this two-step process:

Step 1 - Classify the job:
• Read the job_type and job_title carefully
• Ask: "Does this job involve checking, reviewing, testing, or verifying existing work?"
  → YES = This is an INSPECTION job
  → NO = This is a DESIGN/CONSTRUCTION/GENERAL job

Step 2 - Apply the correct prefix:
• INSPECTION jobs → JICP
• DESIGN/CONSTRUCTION/GENERAL jobs → JCP

**CRITICAL:** Each job MUST get the CORRECT PREFIX based on its classification!
"""

EXAMPLES = """
---------------

Example 1:
- Input: [{{"job_type": "inspection"}}, {{"job_type": "design"}}]
- Latest: "JCP-25-05-1"
- Output: {{"job_no": ["JICP-25-06-1", "JCP-25-07-2"]}}
        (inspection gets JICP, design gets JCP)

Example 2 (with Chinese titles):
- Input: [
    {{"job_type": "inspection", "job_title": "外牆檢測工程"}},
    {{"job_type": "design", "job_title": "樓宇設計"}},
    {{"job_type": "inspection", "job_title": "消防安全檢查"}}
  ]
- Latest: "JICP-25-10-1"
- Output: {{"job_no": ["JICP-25-11-1", "JCP-25-12-2", "JICP-25-13-3"]}}
        (檢測=inspection→JICP, 設計=design→JCP, 檢查=inspection→JICP)

Example 3:
- Input: [
    {{"job_type": "construction", "job_title": "Building Construction"}},
    {{"job_type": "inspection", "job_title": "Safety Verification"}}
  ]
- Latest: "NONE"
- Output: {{"job_no": ["JCP-25-01-1", "JICP-25-02-2"]}}
        (construction→JCP, verification=inspection→JICP)
"""

RETURN_FORMAT = """
**Return format (use JobNumberOutput schema):**
{{
    "job_no": ["generated_number_1", "generated_number_2", ...]
}}
"""

# ====================
# COMBINED PROMPT
# ====================

PROMPT_TEMPLATE = (
    ROLE + "\n\n" +
    CRITICAL_PREFIX_RULE + "\n" +
    CURRENT_STATE + "\n" +
    FORMAT + "\n" +
    INSPECTION_KEYWORDS + "\n" +
    PREFIX_RULES + "\n" +
    YY_RULES + "\n" +
    NO_RULES + "\n" +
    X_RULES + "\n" +
    CLASSIFICATION_PROCESS + "\n" +
    EXAMPLES + "\n" +
    RETURN_FORMAT
)

def create_job_number_tool(list_of_jobs: list[dict]):
    """
    Create new job number(s) for a specific new project(s).

    args:
        list_of_jobs: list[dict] - Each dict should have 'job_type' field (Inspection/Design)
        Example: [{"job_type": "Inspection", "job_title": "..."}, {"job_type": "Design", "job_title": "..."}]

    returns:
        list[str]: The generated job numbers in order
    """

    # Get the latest job number from database
    rows = execute_query(
        query="""SELECT job_no
            FROM "Finance".job
            ORDER BY id DESC
            LIMIT 1;
            """,
        fetch_results=True
    )

    # Fix: Check if rows is empty, not if rows[0] is truthy
    latest_job_no = rows[0]['job_no'] if rows else "NONE"

    # Get current year (2-digit format)
    current_year = datetime.now().strftime("%y")

    # Format the prompt with actual values
    formatted_prompt = PROMPT_TEMPLATE.format(
        current_latest_job_no=latest_job_no,
        jobs_list=list_of_jobs,
        current_year=current_year
    )

    # Generate job numbers using LLM
    job_number_output = invoke_openai_llm(formatted_prompt, JobNumberOutput)

    return job_number_output.job_no if job_number_output else []