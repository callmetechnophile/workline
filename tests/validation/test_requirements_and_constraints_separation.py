"""
Unit and integration tests for Requirements & Constraints separation,
Project scoping, CRUD endpoints, and Validation overview.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.workline.validation.models import (
    ConstraintOperator,
    ConstraintSeverity,
    ConstraintStatus,
    EngineeringConstraint,
    EngineeringRequirement,
    RequirementCategory,
    RequirementPriority,
    RequirementStatus,
    ValidationStatus,
)
from backend.workline.validation.service import ValidationService, validation_service


def test_requirements_crud_and_project_scoping():
    """Test creating, listing, updating, and deleting structured requirements with project scoping."""
    svc = ValidationService()

    # 1. Create requirement for Project A
    req_a = svc.create_requirement(
        requirement_id="REQ-001",
        project_id="proj_alpha",
        title="Regulated Output Voltage",
        description="Must provide 12V regulated rail to main logic board.",
        category=RequirementCategory.ELECTRICAL,
        parameter="output_voltage",
        target_value="12",
        unit="V",
        priority=RequirementPriority.CRITICAL,
        status=RequirementStatus.ACTIVE,
        verification_method="Simulation",
        source="System Specs v1.0",
    )
    assert req_a.requirement_id == "REQ-001"
    assert req_a.project_id == "proj_alpha"
    assert req_a.category == RequirementCategory.ELECTRICAL
    assert req_a.priority == RequirementPriority.CRITICAL

    # 2. Create requirement for Project B
    req_b = svc.create_requirement(
        requirement_id="REQ-002",
        project_id="proj_beta",
        title="Thermal Limit",
        description="Board surface temp must remain below 70°C.",
        category=RequirementCategory.THERMAL,
        parameter="max_temperature",
        target_value="70",
        unit="°C",
        priority=RequirementPriority.HIGH,
    )
    assert req_b.project_id == "proj_beta"

    # 3. Project Scoping Verification (User/Project isolation)
    alpha_reqs = svc.list_requirements(project_id="proj_alpha")
    beta_reqs = svc.list_requirements(project_id="proj_beta")
    assert len(alpha_reqs) == 1
    assert alpha_reqs[0].requirement_id == "REQ-001"
    assert len(beta_reqs) == 1
    assert beta_reqs[0].requirement_id == "REQ-002"

    # 4. Update requirement
    updated = svc.update_requirement("REQ-001", {"status": RequirementStatus.VERIFIED, "target_value": "12.0"})
    assert updated is not None
    assert updated.status == RequirementStatus.VERIFIED
    assert updated.target_value == "12.0"

    # 5. Delete requirement
    deleted = svc.delete_requirement("REQ-001")
    assert deleted is True
    assert svc.get_requirement("REQ-001") is None
    assert len(svc.list_requirements(project_id="proj_alpha")) == 0


def test_constraints_crud_and_requirement_linking():
    """Test creating design constraints, operators, severities, and requirement linking."""
    svc = ValidationService()

    # Create justifying requirement
    req = svc.create_requirement(
        requirement_id="REQ-PWR-01",
        project_id="proj_pwr",
        title="Efficiency Target",
        description="Power stage efficiency must exceed 92%.",
        category=RequirementCategory.PERFORMANCE,
    )

    # Create linked constraint
    con = svc.create_constraint(
        constraint_id="CON-EFF-01",
        property_name="efficiency",
        operator=ConstraintOperator.GTE,
        required_value="92",
        required_unit="%",
        project_id="proj_pwr",
        requirement_id="REQ-PWR-01",
        severity=ConstraintSeverity.CRITICAL,
        verification_method="Simulation",
    )
    assert con.constraint_id == "CON-EFF-01"
    assert con.property == "efficiency"
    assert con.operator == ConstraintOperator.GTE
    assert con.requirement_id == "REQ-PWR-01"

    # Verify link is reflected in requirement's constraints
    fetched_req = svc.get_requirement("REQ-PWR-01")
    assert len(fetched_req.constraints) == 1
    assert fetched_req.constraints[0].constraint_id == "CON-EFF-01"

    # List constraints by project
    pwr_cons = svc.list_constraints(project_id="proj_pwr")
    assert len(pwr_cons) == 1

    # List constraints by requirement
    req_cons = svc.list_constraints(requirement_id="REQ-PWR-01")
    assert len(req_cons) == 1

    # Delete constraint
    ok = svc.delete_constraint("CON-EFF-01")
    assert ok is True
    assert len(svc.list_constraints(project_id="proj_pwr")) == 0
    assert len(svc.get_requirement("REQ-PWR-01").constraints) == 0


def test_project_validation_overview_calculations():
    """Test real-time calculation of requirements, constraints, validated count, violations, and overall status."""
    svc = ValidationService()

    # Empty project
    empty_overview = svc.get_project_validation_overview("proj_empty")
    assert empty_overview.total_requirements == 0
    assert empty_overview.total_constraints == 0
    assert empty_overview.overall_status == ValidationStatus.PENDING

    # Project with active requirements
    svc.create_requirement(
        requirement_id="REQ-1",
        project_id="proj_active",
        title="Input Voltage Range",
        description="Operate from 18V to 36V DC.",
        status=RequirementStatus.ACTIVE,
    )
    svc.create_requirement(
        requirement_id="REQ-2",
        project_id="proj_active",
        title="Ripple Voltage",
        description="Output ripple <= 50mV.",
        status=RequirementStatus.VERIFIED,
    )
    svc.create_constraint(
        constraint_id="CON-1",
        property_name="ripple_voltage",
        operator=ConstraintOperator.LTE,
        required_value="50",
        required_unit="mV",
        project_id="proj_active",
    )

    overview = svc.get_project_validation_overview("proj_active")
    assert overview.total_requirements == 2
    assert overview.total_constraints == 1
    assert overview.validated_count == 1
    assert overview.pending_count == 1
    assert overview.violations_count == 0
    assert overview.overall_status == ValidationStatus.WARNING

    # Add a failed requirement / violation
    svc.create_requirement(
        requirement_id="REQ-3",
        project_id="proj_active",
        title="Peak Current",
        description="Must support 25A peak.",
        status=RequirementStatus.FAILED,
    )
    fail_overview = svc.get_project_validation_overview("proj_active")
    assert fail_overview.violations_count >= 1
    assert fail_overview.overall_status == ValidationStatus.FAIL


def test_requirements_and_constraints_rest_api():
    """Test full REST API endpoints for requirements, constraints, and validation overview."""
    client = TestClient(app)

    # 1. Create requirement via API
    res_req = client.post(
        "/api/requirements",
        json={
            "requirement_id": "REQ-API-01",
            "project_id": "proj_api_test",
            "title": "Continuous Current",
            "description": "Continuous output current >= 15A.",
            "category": "PERFORMANCE",
            "parameter": "output_current",
            "target_value": "15",
            "unit": "A",
            "priority": "HIGH",
            "verification_method": "Simulation",
        },
    )
    assert res_req.status_code == 200
    req_data = res_req.json()
    assert req_data["requirement_id"] == "REQ-API-01"
    assert req_data["parameter"] == "output_current"

    # 2. List requirements for project
    res_list = client.get("/api/requirements?project_id=proj_api_test")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 3. Create constraint via API
    res_con = client.post(
        "/api/constraints",
        json={
            "constraint_id": "CON-API-01",
            "property": "output_current",
            "operator": ">=",
            "required_value": "15",
            "required_unit": "A",
            "project_id": "proj_api_test",
            "requirement_id": "REQ-API-01",
            "severity": "CRITICAL",
        },
    )
    assert res_con.status_code == 200
    con_data = res_con.json()
    assert con_data["constraint_id"] == "CON-API-01"
    assert con_data["operator"] == ">="

    # 4. Get validation overview
    res_ov = client.get("/api/projects/proj_api_test/validation/overview")
    assert res_ov.status_code == 200
    ov_data = res_ov.json()
    assert ov_data["total_requirements"] >= 1
    assert ov_data["total_constraints"] >= 1

    # 5. Delete requirement
    res_del = client.delete("/api/requirements/REQ-API-01")
    assert res_del.status_code == 200
    assert res_del.json()["deleted"] is True
