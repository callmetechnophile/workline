"""Storage provider abstraction for Workline project packages."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class ProjectStorageProvider(ABC):
    """Abstract interface for storing and retrieving .wlipjt packages."""

    @abstractmethod
    def read_bytes(self, location: str) -> bytes:
        """Read binary contents of a package file."""
        pass

    @abstractmethod
    def write_bytes(self, location: str, data: bytes) -> str:
        """Write binary data to target package file and return canonical URI/path."""
        pass

    @abstractmethod
    def exists(self, location: str) -> bool:
        """Check if package exists at location."""
        pass

    @abstractmethod
    def list_packages(self, base_directory: Optional[str] = None) -> List[str]:
        """List available .wlipjt package URIs or paths."""
        pass

    @abstractmethod
    def delete(self, location: str) -> bool:
        """Delete package at location."""
        pass


class LocalStorageProvider(ProjectStorageProvider):
    """Default local filesystem storage provider for Workline packages."""

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = Path(root_dir).resolve() if root_dir else Path.cwd()

    def read_bytes(self, location: str) -> bytes:
        p = Path(location)
        if not p.is_absolute():
            p = self.root_dir / p
        if not p.exists():
            raise FileNotFoundError(f"Package not found at '{p}'.")
        return p.read_bytes()

    def write_bytes(self, location: str, data: bytes) -> str:
        p = Path(location)
        if not p.is_absolute():
            p = self.root_dir / p
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return str(p.resolve())

    def exists(self, location: str) -> bool:
        p = Path(location)
        if not p.is_absolute():
            p = self.root_dir / p
        return p.exists() and p.is_file()

    def list_packages(self, base_directory: Optional[str] = None) -> List[str]:
        target = Path(base_directory).resolve() if base_directory else self.root_dir
        if not target.exists():
            return []
        return [str(p.resolve()) for p in target.glob("**/*.wlipjt") if p.is_file()]

    def delete(self, location: str) -> bool:
        p = Path(location)
        if not p.is_absolute():
            p = self.root_dir / p
        if p.exists() and p.is_file():
            p.unlink()
            return True
        return False
