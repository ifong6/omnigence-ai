-- Flow Table Schema
-- Stores logs from PreOrchestratorLogger for UI rendering

CREATE TABLE IF NOT EXISTS flow_table (
    uuid UUID PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_input TEXT NOT NULL,
    user_intent TEXT,
    identified_agents TEXT[],
    summary TEXT NOT NULL,
    classifier_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index on session_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_flow_table_session_id ON flow_table(session_id);

-- Index on created_at for chronological queries
CREATE INDEX IF NOT EXISTS idx_flow_table_created_at ON flow_table(created_at DESC);

-- Comments for documentation
COMMENT ON TABLE flow_table IS 'Stores flow logs from PreOrchestratorLogger before task orchestration';
COMMENT ON COLUMN flow_table.uuid IS 'Unique identifier for this flow execution';
COMMENT ON COLUMN flow_table.session_id IS 'User session identifier';
COMMENT ON COLUMN flow_table.user_input IS 'Original user request';
COMMENT ON COLUMN flow_table.user_intent IS 'Extracted user intent (1 sentence)';
COMMENT ON COLUMN flow_table.identified_agents IS 'Array of agent names to handle this request';
COMMENT ON COLUMN flow_table.summary IS 'LLM-generated summary of the flow state';
COMMENT ON COLUMN flow_table.classifier_message IS 'Message from the classifier agent';
