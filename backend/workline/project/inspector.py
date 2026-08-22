"""Read-only package inspection, verification, and diff engine for .wlipjt packages."""

import hashlib
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import zipfile

from backend.workline.git.toon import ToonSerializer
from backend.workline.project.errors import (
    ChecksumMismatchError,
    CorruptedPackageError,
    UnsupportedFormatVersionError,
)
from backend.workline.project.migrations.migrator import PackageMigrator
from backend.workline.project.models import (
    ChecksumManifest,
    FileChecksumEntry,
    PackageDiff,
    PackageInspection,
    PackageManifest,
    PackageSizeBreakdown,
    PackageValidationStatus,
)


class PackageInspector:
    """
    Read-only inspection and verification engine.
    Ensures zero side-effects on the local workspace while validating container integrity.
    """

    LARGE_PACKAGE_THRESHOLD_BYTES: int = 500 * 1024 * 1024  # 500 MB

    @classmethod
    def _hash_bytes(cls, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def read_manifest(cls, package_path: Path) -> PackageManifest:
        """Reads and deserializes manifest.toon from a package file."""
        p = Path(package_path).resolve()
        if not p.exists():
            raise CorruptedPackageError(f"Package file '{p}' not found.")

        try:
            with zipfile.ZipFile(p, "r") as zf:
                if "manifest.toon" not in zf.namelist():
                    raise CorruptedPackageError("Missing root 'manifest.toon' in package container.")
                raw_manifest = zf.read("manifest.toon").decode("utf-8")
                manifest_dict = ToonSerializer.dict_from_toon(raw_manifest)
                
                # Check version migration
                migrated_dict, _ = PackageMigrator.migrate_package_manifest(manifest_dict)
                return PackageManifest.model_validate(migrated_dict)
        except Exception as e:
            if isinstance(e, (CorruptedPackageError, UnsupportedFormatVersionError)):
                raise e
            raise CorruptedPackageError(f"Failed to read package manifest: {str(e)}")

    @classmethod
    def verify(cls, package_path: Path) -> Tuple[bool, List[str]]:
        """
        Validates internal file checksums against checksums.toon without modifying any local state.
        Returns (is_valid, list_of_errors_or_warnings).
        """
        p = Path(package_path).resolve()
        if not p.exists():
            return False, [f"Package file '{p}' does not exist."]

        errors: List[str] = []
        try:
            with zipfile.ZipFile(p, "r") as zf:
                names = set(zf.namelist())
                if "manifest.toon" not in names:
                    errors.append("Package is missing 'manifest.toon'.")
                if "checksums.toon" not in names:
                    errors.append("Package is missing 'checksums.toon'.")

                if errors:
                    return False, errors

                # Parse checksums
                chk_content = zf.read("checksums.toon").decode("utf-8")
                chk_dict = ToonSerializer.dict_from_toon(chk_content)
                entries_data = chk_dict if isinstance(chk_dict, list) else chk_dict.get("items", []) if isinstance(chk_dict, dict) else []
                
                for entry in entries_data:
                    file_path = entry.get("path")
                    expected_sha = entry.get("sha256")
                    if not file_path or not expected_sha:
                        continue

                    if file_path not in names:
                        errors.append(f"Package corrupt: Declared file '{file_path}' missing from archive.")
                        continue

                    actual_data = zf.read(file_path)
                    actual_sha = cls._hash_bytes(actual_data)
                    if actual_sha != expected_sha:
                        errors.append(f"Checksum mismatch for '{file_path}' (expected {expected_sha[:8]}, got {actual_sha[:8]}).")

        except zipfile.BadZipFile:
            return False, ["Invalid or corrupted ZIP container format."]
        except Exception as e:
            return False, [f"Verification failed: {str(e)}"]

        return len(errors) == 0, errors

    @classmethod
    def inspect(cls, package_path: Path) -> PackageInspection:
        """
        Performs comprehensive read-only inspection of a .wlipjt package.
        Calculates size breakdown, validates integrity, and generates warnings.
        """
        p = Path(package_path).resolve()
        manifest = cls.read_manifest(p)
        is_valid, errors = cls.verify(p)

        total_size = p.stat().st_size if p.exists() else 0
        art_size = 0
        state_size = 0
        doc_size = 0
        git_size = 0

        warnings: List[str] = []

        try:
            with zipfile.ZipFile(p, "r") as zf:
                for zinfo in zf.infolist():
                    name = zinfo.filename
                    size = zinfo.file_size
                    if name.startswith("artifacts/"):
                        art_size += size
                    elif name.startswith("git/"):
                        git_size += size
                    elif name.startswith("project/requirements") or name.startswith("research/"):
                        doc_size += size
                    else:
                        state_size += size
        except Exception:
            pass

        if total_size > cls.LARGE_PACKAGE_THRESHOLD_BYTES:
            warnings.append("Large artifact payload detected. Consider metadata-only export for faster transfer.")

        if manifest.validation_status == PackageValidationStatus.FORCED_EXPORT:
            warnings.append("Package was exported with --force flag (FORCED_EXPORT).")

        breakdown = PackageSizeBreakdown(
            total_package_size_bytes=total_size,
            artifacts_size_bytes=art_size,
            project_state_size_bytes=state_size,
            documentation_size_bytes=doc_size,
            git_size_bytes=git_size,
        )

        return PackageInspection(
            valid=is_valid and len(errors) == 0,
            manifest=manifest,
            integrity_status="VALID" if is_valid else "CORRUPTED",
            size_breakdown=breakdown,
            warnings=warnings,
            errors=errors,
        )

    @classmethod
    def diff(cls, package_a: Path, package_b: Path) -> PackageDiff:
        """Compares two .wlipjt packages and reports structured engineering differences."""
        pa = Path(package_a).resolve()
        pb = Path(package_b).resolve()

        meta_a = cls.read_manifest(pa)
        meta_b = cls.read_manifest(pb)

        def read_package_toon(pkg_path: Path, entry_name: str) -> Dict[str, Any]:
            try:
                with zipfile.ZipFile(pkg_path, "r") as zf:
                    if entry_name in zf.namelist():
                        raw = zf.read(entry_name).decode("utf-8")
                        return ToonSerializer.dict_from_toon(raw)
            except Exception:
                pass
            return {}

        eng_a_data = read_package_toon(pa, "engineering/components.toon")
        eng_a = eng_a_data if isinstance(eng_a_data, list) else eng_a_data.get("items", []) if isinstance(eng_a_data, dict) else []
        eng_b_data = read_package_toon(pb, "engineering/components.toon")
        eng_b = eng_b_data if isinstance(eng_b_data, list) else eng_b_data.get("items", []) if isinstance(eng_b_data, dict) else []
        
        comps_a = {c.get("id", c.get("mpn", str(i))): c for i, c in enumerate(eng_a)}
        comps_b = {c.get("id", c.get("mpn", str(i))): c for i, c in enumerate(eng_b)}

        added_comps = len(set(comps_b.keys()) - set(comps_a.keys()))
        removed_comps = len(set(comps_a.keys()) - set(comps_b.keys()))
        common_comps = set(comps_a.keys()) & set(comps_b.keys())
        modified_comps = sum(1 for k in common_comps if comps_a[k] != comps_b[k])

        nets_a_data = read_package_toon(pa, "engineering/nets.toon")
        nets_a_list = nets_a_data if isinstance(nets_a_data, list) else nets_a_data.get("items", []) if isinstance(nets_a_data, dict) else []
        nets_a = set(n.get("name", "") for n in nets_a_list)

        nets_b_data = read_package_toon(pb, "engineering/nets.toon")
        nets_b_list = nets_b_data if isinstance(nets_b_data, list) else nets_b_data.get("items", []) if isinstance(nets_b_data, dict) else []
        nets_b = set(n.get("name", "") for n in nets_b_list)

        added_nets = len(nets_b - nets_a)
        removed_nets = len(nets_a - nets_b)

        bom_a = read_package_toon(pa, "engineering/bom.toon")
        bom_b = read_package_toon(pb, "engineering/bom.toon")
        bom_changed = bom_a != bom_b

        pcb_a = read_package_toon(pa, "engineering/pcb.toon")
        pcb_b = read_package_toon(pb, "engineering/pcb.toon")
        pcb_changed = pcb_a != pcb_b

        con_a = read_package_toon(pa, "project/constraints.toon")
        con_b = read_package_toon(pb, "project/constraints.toon")
        constraints_changed = con_a != con_b

        version_diff = f"{meta_a.project_version} → {meta_b.project_version}"
        schema_diff = f"{meta_a.schema_version} → {meta_b.schema_version}"

        return PackageDiff(
            source_package=pa.name,
            target_package=pb.name,
            version_diff=version_diff,
            schema_diff=schema_diff,
            components_added=added_comps,
            components_removed=removed_comps,
            components_modified=modified_comps,
            nets_added=added_nets,
            nets_removed=removed_nets,
            bom_changed=bom_changed,
            pcb_changed=pcb_changed,
            constraints_changed=constraints_changed,
            details={
                "source_project_id": meta_a.project_id,
                "target_project_id": meta_b.project_id,
            },
        )
