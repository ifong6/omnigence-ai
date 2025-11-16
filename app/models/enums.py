from enum import Enum

class UnitType(str, Enum):
    """Unit types for quotation items - matches Finance.unit_type enum"""
    Lot = "Lot"
    m2 = "m²"
    m3 = "m³"
    piece = "piece"
    set = "set"
    hour = "hour"
    day = "day"


class QuotationStatus(str, Enum):
    """Quotation status values"""
    DRAFTED = "DRAFTED"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    
class DBTable(str, Enum):
    FINANCE_SCHEMA = "Finance"
    COMPANY_TABLE = '"Finance".company'
    DESIGN_JOB_TABLE = '"Finance".design_job'
    INSPECTION_JOB_TABLE = '"Finance".inspection_job'
    QUOTATION_TABLE = '"Finance".quotation'
    QUOTATION_ITEM_TABLE = '"Finance".quotation_item'
    INVOICE_TABLE = '"Finance".invoice'
    INVOICE_ITEM_TABLE = '"Finance".invoice_item'
    PAYMENT_RECORD_TABLE = '"Finance".payment_record'
    FLOW_TABLE = '"Finance".flow'

    @property
    def schema(self) -> str:
        """Extract schema name from fully qualified table name.

        Example: '"Finance".flow' -> 'Finance'
        """
        return self.value.split(".")[0].strip('"')

    @property
    def table(self) -> str:
        """Extract table name from fully qualified table name.

        Example: '"Finance".flow' -> 'flow'
        """
        return self.value.split(".")[1]