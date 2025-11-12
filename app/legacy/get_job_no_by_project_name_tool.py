from typing import Optional
from sqlmodel import Session, select, desc

from app.db.engine import engine
from app.models.job_models import DesignJob, InspectionJob


def get_job_no_by_project_name_tool(project_name: str) -> Optional[str]:
    """
    Fetch job_no by project title from design_job or inspection_job tables.

    Searches both tables (design first, then inspection) and returns most recent job_no.
    Returns None if project not found.

    Args:
        project_name: Project title (exact match, case-sensitive)

    Returns:
        job_no (e.g., "JCP-25-01-1") or None
    """
    try:
        with Session(engine) as session:
            # Try design_job first
            design_job = session.exec(
                select(DesignJob)
                .where(DesignJob.title == project_name)
                .order_by(desc(DesignJob.id))
                .limit(1)
            ).first()

            if design_job:
                return design_job.job_no

            # Try inspection_job
            inspection_job = session.exec(
                select(InspectionJob)
                .where(InspectionJob.title == project_name)
                .order_by(desc(InspectionJob.id))
                .limit(1)
            ).first()

            return inspection_job.job_no if inspection_job else None

    except Exception as e:
        print(f"[ERROR][get_job_no_by_project_name_tool] Failed to fetch job_no: {e}")
        import traceback
        traceback.print_exc()
        return None
