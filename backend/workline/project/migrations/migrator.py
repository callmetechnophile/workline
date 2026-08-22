"""Package format version migrator for evolving .wlipjt versions."""

from typing import Any, Dict, Tuple
from backend.workline.project.errors import UnsupportedFormatVersionError
from backend.workline.project.models import PackageManifest


class PackageMigrator:
    """
    Manages forwards and backwards compatibility across .wlipjt package format versions.
    Currently format_version 1 is authoritative.
    """

    CURRENT_FORMAT_VERSION: int = 1

    @classmethod
    def can_migrate(cls, source_version: int) -> bool:
        """Check if source format version can be migrated to current format."""
        return 1 <= source_version <= cls.CURRENT_FORMAT_VERSION

    @classmethod
    def migrate_package_manifest(cls, manifest_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """
        Migrates a package manifest dictionary from older format versions to current version.
        Returns migrated dictionary and boolean indicating if migration occurred.
        """
        version = int(manifest_dict.get("format_version", 1))
        if version > cls.CURRENT_FORMAT_VERSION:
            raise UnsupportedFormatVersionError(version, max_supported=cls.CURRENT_FORMAT_VERSION)

        migrated = False
        data = dict(manifest_dict)

        # Example future v0 -> v1 or v1 -> v2 migration hooks
        if version < 1:
            data["format_version"] = 1
            migrated = True

        return data, migrated
