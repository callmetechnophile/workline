"""
Project integrity and schema validator for WORKLINE .wl projects.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cli.workline.project.filesystem import (
    README_FILENAME,
    WL_METADATA_DIR,
    MANIFEST_FILENAME,
    STANDARD_MODULES,
    calculate_file_hash,
    discover_project_files,
    is_secret_file,
)
from cli.workline.project.readme import parse_readme_wl
from cli.workline.project.manifest import parse_manifest_wl


@dataclass
class ValidationCheck:
    name: str
    passed: bool
    message: str = ""


@dataclass
class ProjectValidationResult:
    is_valid: bool
    checks: List[ValidationCheck] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def validate_project(
    project_root: Path,
    verify_checksums: bool = True,
) -> ProjectValidationResult:
    """
    Validate a WORKLINE project filesystem against the specification.
    Checks directory structure, manifest, README.wl, zero-secrets invariant,
    and file checksums.
    """
    project_root = project_root.resolve()
    checks: List[ValidationCheck] = []
    errors: List[str] = []
    warnings: List[str] = []
    
    # 1. README.wl Check
    readme_path = project_root / README_FILENAME
    if readme_path.exists():
        try:
            readme = parse_readme_wl(readme_path)
            checks.append(ValidationCheck("README.wl", True, f"Valid ({readme.name})"))
        except Exception as e:
            checks.append(ValidationCheck("README.wl", False, f"Failed parsing: {e}"))
            errors.append(f"README.wl parsing error: {e}")
    else:
        checks.append(ValidationCheck("README.wl", False, "Missing README.wl"))
        errors.append("README.wl does not exist in project root")

    # 2. Manifest Check
    manifest_path = project_root / WL_METADATA_DIR / MANIFEST_FILENAME
    manifest_data = None
    if manifest_path.exists():
        try:
            manifest_data = parse_manifest_wl(manifest_path)
            checks.append(ValidationCheck("manifest", True, f"Valid schema {manifest_data.schema_version}"))
        except Exception as e:
            checks.append(ValidationCheck("manifest", False, f"Failed parsing: {e}"))
            errors.append(f"manifest.wl parsing error: {e}")
    else:
        checks.append(ValidationCheck("manifest", False, "Missing .wl/manifest.wl"))
        errors.append(".wl/manifest.wl does not exist")

    # 3. Standard Directories Check
    for mod in STANDARD_MODULES:
        mod_dir = project_root / mod
        if mod_dir.exists() and mod_dir.is_dir():
            checks.append(ValidationCheck(f"{mod}", True, "Directory present"))
        else:
            checks.append(ValidationCheck(f"{mod}", True, "Directory present (empty/created)"))
            mod_dir.mkdir(parents=True, exist_ok=True)

    # 4. Zero-Secrets Invariant Check
    secret_patterns = {
        ".env", ".env.*", "*.env", "credentials*", "*.pem", "*.key",
        "*.token", "*.secret", "id_rsa*", "id_ed25519*", "private*",
    }
    found_secrets = []
    for item in project_root.rglob("*"):
        if item.is_file():
            rel_posix = item.relative_to(project_root).as_posix()
            if is_secret_file(rel_posix, secret_patterns):
                found_secrets.append(rel_posix)
                
    if found_secrets:
        checks.append(ValidationCheck("zero_secrets", False, f"Found sensitive files: {found_secrets}"))
        errors.append(f"Zero-secrets violation: {found_secrets}")
    else:
        checks.append(ValidationCheck("zero_secrets", True, "No secrets or private keys found"))

    # 5. Checksums Check (if manifest exists and has file_hashes)
    if verify_checksums and manifest_data and manifest_data.file_hashes:
        mismatches = []
        for rel_posix, expected_hash in manifest_data.file_hashes.items():
            file_path = project_root / rel_posix
            if not file_path.exists():
                mismatches.append(f"Missing file: {rel_posix}")
            else:
                actual_hash = calculate_file_hash(file_path)
                if actual_hash != expected_hash:
                    mismatches.append(f"Checksum mismatch: {rel_posix}")
        if mismatches:
            checks.append(ValidationCheck("checksums", False, f"{len(mismatches)} mismatches"))
            warnings.extend(mismatches)
        else:
            checks.append(ValidationCheck("checksums", True, "All file checksums match manifest"))

    # 6. Moss Metadata Check
    moss_file = project_root / WL_METADATA_DIR / "moss.wl"
    if moss_file.exists():
        checks.append(ValidationCheck("moss_configuration", True, "Configured (.wl/moss.wl present)"))
    else:
        checks.append(ValidationCheck("moss_configuration", True, "Uninitialized (.wl/moss.wl created upon indexing)"))

    is_valid = len(errors) == 0
    return ProjectValidationResult(
        is_valid=is_valid,
        checks=checks,
        errors=errors,
        warnings=warnings,
    )
