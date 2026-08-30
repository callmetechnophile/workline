-- 002_indexes.sql: Performance and Uniqueness Indexes for SurrealDB Knowledge Graph (Agent #13)

DEFINE INDEX idx_project_owner ON TABLE project COLUMNS owner_id;
DEFINE INDEX idx_requirement_proj ON TABLE requirement COLUMNS project_id;
DEFINE INDEX idx_component_part ON TABLE component COLUMNS manufacturer, part_number UNIQUE;
DEFINE INDEX idx_bom_proj ON TABLE bom COLUMNS project_id;
DEFINE INDEX idx_task_proj ON TABLE implementation_task COLUMNS project_id;
DEFINE INDEX idx_execution_proj ON TABLE execution COLUMNS project_id;
DEFINE INDEX idx_receipt_exec ON TABLE execution_receipt COLUMNS execution_id UNIQUE;
DEFINE INDEX idx_state_proj ON TABLE project_state COLUMNS project_id UNIQUE;
DEFINE INDEX idx_audit_proj ON TABLE audit_event COLUMNS project_id, timestamp;
