"""
Database table and schema constants.

This module defines database table names and schema constants
to ensure consistency across the application.
"""

class DBTable:
    """Database table names with schema qualification."""

    # Schema names
    FINANCE_SCHEMA = "Finance"

    # Table names with schema
    DESIGN_JOB_TABLE = '"Finance".design_job'
    INSPECTION_JOB_TABLE = '"Finance".inspection_job'
    QUOTATION_TABLE = '"Finance".quotation'
    COMPANY_TABLE = '"Finance".company'
    FLOW_TABLE = '"Finance".flow'
