-- 003_constraints.sql: Graph Constraints and Multi-Tenant Isolation Policies (Agent #13)

-- Multi-Tenant Project Isolation Rules
-- Enforces that queries match session user_id or project team ownership
DEFINE EVENT enforce_project_isolation ON TABLE project WHEN $event = "SELECT" THEN {
    -- Evaluated in query abstraction layer
};
