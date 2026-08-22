-- Workline Comprehensive SurrealDB Schema Definition
-- Migration 001: Initial Structured Tables & Relation Graph

-- ============================================================================
-- 1. SCHEMAS & TABLES DEFINITION
-- ============================================================================

DEFINE TABLE users SCHEMAFULL;
DEFINE FIELD name ON users TYPE string;
DEFINE FIELD email ON users TYPE string;
DEFINE FIELD created_at ON users TYPE string;

DEFINE TABLE teams SCHEMAFULL;
DEFINE FIELD name ON teams TYPE string;
DEFINE FIELD uuid ON teams TYPE string;
DEFINE FIELD created_at ON teams TYPE string;

DEFINE TABLE team_members SCHEMAFULL;
DEFINE FIELD team_id ON team_members TYPE string;
DEFINE FIELD user_id ON team_members TYPE string;
DEFINE FIELD email ON team_members TYPE string;
DEFINE FIELD role ON team_members TYPE string;
DEFINE FIELD joined_at ON team_members TYPE string;

DEFINE TABLE invitations SCHEMAFULL;
DEFINE FIELD team_id ON invitations TYPE string;
DEFINE FIELD email ON invitations TYPE string;
DEFINE FIELD role ON invitations TYPE string;
DEFINE FIELD token_hash ON invitations TYPE string;
DEFINE FIELD status ON invitations TYPE string;
DEFINE FIELD created_at ON invitations TYPE string;

DEFINE TABLE projects SCHEMAFULL;
DEFINE FIELD name ON projects TYPE string;
DEFINE FIELD display_name ON projects TYPE string;
DEFINE FIELD description ON projects TYPE option<string>;
DEFINE FIELD domain ON projects TYPE option<string>;
DEFINE FIELD budget ON projects TYPE option<object>;
DEFINE FIELD timeline ON projects TYPE option<object>;
DEFINE FIELD complexity ON projects TYPE option<string>;
DEFINE FIELD target_platform ON projects TYPE option<object>;
DEFINE FIELD current_stage ON projects TYPE option<string>;
DEFINE FIELD status ON projects TYPE option<string>;
DEFINE FIELD created_at ON projects TYPE string;
DEFINE FIELD updated_at ON projects TYPE string;
DEFINE FIELD bom ON projects TYPE option<array>;
DEFINE FIELD power ON projects TYPE option<object>;
DEFINE FIELD dependencies ON projects TYPE option<object>;
DEFINE FIELD wiring ON projects TYPE option<array>;
DEFINE FIELD papers ON projects TYPE option<array>;
DEFINE FIELD gantt ON projects TYPE option<array>;
DEFINE FIELD code ON projects TYPE option<string>;
DEFINE FIELD exports ON projects TYPE option<array>;
DEFINE FIELD version ON projects TYPE option<int>;

DEFINE TABLE project_versions SCHEMAFULL;
DEFINE FIELD project_id ON project_versions TYPE string;
DEFINE FIELD version_num ON project_versions TYPE int;
DEFINE FIELD data ON project_versions TYPE object;
DEFINE FIELD modified_by ON project_versions TYPE string;
DEFINE FIELD change_summary ON project_versions TYPE string;
DEFINE FIELD created_at ON project_versions TYPE string;

DEFINE TABLE workspace_bundles SCHEMAFULL;
DEFINE FIELD user_id ON workspace_bundles TYPE string;
DEFINE FIELD name ON workspace_bundles TYPE string;
DEFINE FIELD description ON workspace_bundles TYPE option<string>;
DEFINE FIELD bundle_blob ON workspace_bundles TYPE string;
DEFINE FIELD checksum ON workspace_bundles TYPE string;
DEFINE FIELD bundle_size ON workspace_bundles TYPE int;
DEFINE FIELD field_count ON workspace_bundles TYPE int;
DEFINE FIELD version ON workspace_bundles TYPE int;
DEFINE FIELD saved_at ON workspace_bundles TYPE string;

DEFINE TABLE comments SCHEMAFULL;
DEFINE FIELD project_id ON comments TYPE string;
DEFINE FIELD section ON comments TYPE string;
DEFINE FIELD author ON comments TYPE string;
DEFINE FIELD content ON comments TYPE string;
DEFINE FIELD timestamp ON comments TYPE string;

DEFINE TABLE requirements SCHEMAFULL;
DEFINE FIELD project_id ON requirements TYPE string;
DEFINE FIELD title ON requirements TYPE string;
DEFINE FIELD description ON requirements TYPE option<string>;
DEFINE FIELD category ON requirements TYPE option<string>;
DEFINE FIELD priority ON requirements TYPE option<string>;
DEFINE FIELD status ON requirements TYPE option<string>;

DEFINE TABLE subsystems SCHEMAFULL;
DEFINE FIELD project_id ON subsystems TYPE string;
DEFINE FIELD name ON subsystems TYPE string;
DEFINE FIELD description ON subsystems TYPE option<string>;
DEFINE FIELD status ON subsystems TYPE option<string>;

DEFINE TABLE components SCHEMAFULL;
DEFINE FIELD project_id ON components TYPE string;
DEFINE FIELD name ON components TYPE string;
DEFINE FIELD mpn ON components TYPE option<string>;
DEFINE FIELD manufacturer ON components TYPE option<string>;
DEFINE FIELD description ON components TYPE option<string>;
DEFINE FIELD category ON components TYPE option<string>;
DEFINE FIELD price ON components TYPE option<float>;
DEFINE FIELD voltage ON components TYPE option<string>;
DEFINE FIELD current_ma ON components TYPE option<float>;
DEFINE FIELD datasheet_url ON components TYPE option<string>;

DEFINE TABLE datasheets SCHEMAFULL;
DEFINE FIELD component_id ON datasheets TYPE string;
DEFINE FIELD title ON datasheets TYPE string;
DEFINE FIELD url ON datasheets TYPE string;
DEFINE FIELD verified ON datasheets TYPE option<bool>;

DEFINE TABLE power_architectures SCHEMAFULL;
DEFINE FIELD project_id ON power_architectures TYPE string;
DEFINE FIELD total_power_mw ON power_architectures TYPE option<float>;
DEFINE FIELD battery_hours ON power_architectures TYPE option<float>;
DEFINE FIELD rails ON power_architectures TYPE option<array>;

DEFINE TABLE interfaces SCHEMAFULL;
DEFINE FIELD component_id ON interfaces TYPE string;
DEFINE FIELD type ON interfaces TYPE string;
DEFINE FIELD pin_count ON interfaces TYPE option<int>;

DEFINE TABLE connections SCHEMAFULL;
DEFINE FIELD project_id ON connections TYPE string;
DEFINE FIELD from_component ON connections TYPE string;
DEFINE FIELD from_pin ON connections TYPE string;
DEFINE FIELD to_component ON connections TYPE string;
DEFINE FIELD to_pin ON connections TYPE string;
DEFINE FIELD signal_type ON connections TYPE option<string>;

DEFINE TABLE schematics SCHEMAFULL;
DEFINE FIELD project_id ON schematics TYPE string;
DEFINE FIELD diagram_svg ON schematics TYPE option<string>;

DEFINE TABLE bom SCHEMAFULL;
DEFINE FIELD project_id ON bom TYPE string;
DEFINE FIELD total_cost ON bom TYPE option<float>;
DEFINE FIELD currency ON bom TYPE option<string>;

DEFINE TABLE bom_items SCHEMAFULL;
DEFINE FIELD bom_id ON bom_items TYPE string;
DEFINE FIELD component_id ON bom_items TYPE string;
DEFINE FIELD quantity ON bom_items TYPE int;
DEFINE FIELD unit_price ON bom_items TYPE float;
DEFINE FIELD total_price ON bom_items TYPE float;

DEFINE TABLE firmware SCHEMAFULL;
DEFINE FIELD project_id ON firmware TYPE string;
DEFINE FIELD target ON firmware TYPE string;
DEFINE FIELD code ON firmware TYPE string;

DEFINE TABLE tests SCHEMAFULL;
DEFINE FIELD project_id ON tests TYPE string;
DEFINE FIELD name ON tests TYPE string;
DEFINE FIELD status ON tests TYPE string;

DEFINE TABLE validation SCHEMAFULL;
DEFINE FIELD project_id ON validation TYPE string;
DEFINE FIELD category ON validation TYPE string;
DEFINE FIELD status ON validation TYPE string;
DEFINE FIELD details ON validation TYPE option<string>;

DEFINE TABLE documents SCHEMAFULL;
DEFINE FIELD project_id ON documents TYPE string;
DEFINE FIELD title ON documents TYPE string;
DEFINE FIELD content ON documents TYPE string;
DEFINE FIELD doc_type ON documents TYPE option<string>;
DEFINE FIELD embedding_id ON documents TYPE option<string>;

DEFINE TABLE research_items SCHEMAFULL;
DEFINE FIELD project_id ON research_items TYPE string;
DEFINE FIELD title ON research_items TYPE string;
DEFINE FIELD abstract ON research_items TYPE option<string>;
DEFINE FIELD authors ON research_items TYPE option<array>;
DEFINE FIELD url ON research_items TYPE option<string>;
DEFINE FIELD score ON research_items TYPE option<float>;

DEFINE TABLE workspace_state SCHEMAFULL;
DEFINE FIELD project_id ON workspace_state TYPE string;
DEFINE FIELD state_json ON workspace_state TYPE string;

DEFINE TABLE lifecycle_state SCHEMAFULL;
DEFINE FIELD project_id ON lifecycle_state TYPE string;
DEFINE FIELD current_stage ON lifecycle_state TYPE string;
DEFINE FIELD progress ON lifecycle_state TYPE float;
DEFINE FIELD stages ON lifecycle_state TYPE object;

DEFINE TABLE releases SCHEMAFULL;
DEFINE FIELD project_id ON releases TYPE string;
DEFINE FIELD version ON releases TYPE string;
DEFINE FIELD artifacts ON releases TYPE option<array>;
DEFINE FIELD created_at ON releases TYPE string;

-- ============================================================================
-- 2. GRAPH RELATIONS (EDGES)
-- ============================================================================

DEFINE TABLE CONTAINS TYPE RELATION;
DEFINE TABLE REQUIRES TYPE RELATION;
DEFINE TABLE USES TYPE RELATION;
DEFINE TABLE CONNECTS_TO TYPE RELATION;
DEFINE TABLE POWERED_BY TYPE RELATION;
DEFINE TABLE COMMUNICATES_VIA TYPE RELATION;
DEFINE TABLE HAS_DATASHEET TYPE RELATION;
DEFINE TABLE ALTERNATIVE_TO TYPE RELATION;
DEFINE TABLE SOLD_BY TYPE RELATION;
DEFINE TABLE SATISFIES TYPE RELATION;
DEFINE TABLE DEPENDS_ON TYPE RELATION;
DEFINE TABLE VALIDATED_BY TYPE RELATION;
DEFINE TABLE DERIVED_FROM TYPE RELATION;
DEFINE TABLE PRODUCES TYPE RELATION;
DEFINE TABLE BLOCKS TYPE RELATION;
DEFINE TABLE IMPLEMENTS TYPE RELATION;
