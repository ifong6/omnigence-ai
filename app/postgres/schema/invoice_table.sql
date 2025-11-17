-- Invoice Table Schema
-- Stores invoice records for billing clients
-- Note: Similar to quotation table, stores ONE ROW PER INVOICE ITEM

CREATE TABLE IF NOT EXISTS "Finance".invoice (
    id SERIAL PRIMARY KEY,
    inv_no VARCHAR(100) NOT NULL,
    date_issued DATE,
    due_date DATE,
    client_id INTEGER REFERENCES "Finance".company(id),
    project_name VARCHAR(500),
    job_no VARCHAR(100),
    quotation_no VARCHAR(100),
    invoice_item_description TEXT NOT NULL,
    sub_amount NUMERIC(12, 2),
    total_amount NUMERIC(12, 2),
    currency VARCHAR(10) DEFAULT 'MOP',
    status VARCHAR(20) DEFAULT 'pending',
    amount NUMERIC(12, 2),
    unit VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_invoice_inv_no ON "Finance".invoice(inv_no);
CREATE INDEX IF NOT EXISTS idx_invoice_job_no ON "Finance".invoice(job_no);
CREATE INDEX IF NOT EXISTS idx_invoice_quotation_no ON "Finance".invoice(quotation_no);
CREATE INDEX IF NOT EXISTS idx_invoice_client_id ON "Finance".invoice(client_id);
CREATE INDEX IF NOT EXISTS idx_invoice_status ON "Finance".invoice(status);
CREATE INDEX IF NOT EXISTS idx_invoice_date_issued ON "Finance".invoice(date_issued DESC);

-- Comments for documentation
COMMENT ON TABLE "Finance".invoice IS 'Stores invoice records - one row per invoice item (similar to quotation table structure)';
COMMENT ON COLUMN "Finance".invoice.id IS 'Primary key - unique identifier for each invoice item row';
COMMENT ON COLUMN "Finance".invoice.inv_no IS 'Invoice number (e.g., INV-JCP-25-01-1)';
COMMENT ON COLUMN "Finance".invoice.date_issued IS 'Invoice issue date';
COMMENT ON COLUMN "Finance".invoice.due_date IS 'Payment due date';
COMMENT ON COLUMN "Finance".invoice.client_id IS 'Foreign key to company table (client/customer)';
COMMENT ON COLUMN "Finance".invoice.project_name IS 'Name of the project being invoiced';
COMMENT ON COLUMN "Finance".invoice.job_no IS 'Reference to the original job number';
COMMENT ON COLUMN "Finance".invoice.quotation_no IS 'Reference to the original quotation number (if applicable)';
COMMENT ON COLUMN "Finance".invoice.invoice_item_description IS 'Description of the billable item/service';
COMMENT ON COLUMN "Finance".invoice.sub_amount IS 'Subtotal for this individual line item';
COMMENT ON COLUMN "Finance".invoice.total_amount IS 'Total amount for the entire invoice (same across all items)';
COMMENT ON COLUMN "Finance".invoice.currency IS 'Currency code (MOP, HKD, USD, etc.)';
COMMENT ON COLUMN "Finance".invoice.status IS 'Payment status: pending, paid, overdue, cancelled';
COMMENT ON COLUMN "Finance".invoice.amount IS 'Quantity of this item';
COMMENT ON COLUMN "Finance".invoice.unit IS 'Unit of measurement (Lot, 件, 套, m, m², hr, etc.)';
COMMENT ON COLUMN "Finance".invoice.notes IS 'Additional notes or payment terms';
COMMENT ON COLUMN "Finance".invoice.created_at IS 'Timestamp when this record was created';
COMMENT ON COLUMN "Finance".invoice.updated_at IS 'Timestamp when this record was last updated';
