import hashlib
import tempfile
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import settings


class StorageBackend(ABC):
    """Abstract interface for evidence object storage."""

    @abstractmethod
    def save_quarantine(self, key: str, data: bytes) -> str:
        """Saves unverified data to quarantine. Returns storage path."""

    @abstractmethod
    def read_quarantine(self, path: str) -> bytes:
        """Reads raw bytes from quarantine."""

    @abstractmethod
    def promote_to_accepted(self, quarantine_path: str, accepted_key: str) -> tuple[str, str, int]:
        """Atomically copies verified data from quarantine to accepted.

        Returns: (accepted_path, sha256_hash, byte_size)
        """

    @abstractmethod
    def read_accepted(self, path: str) -> bytes:
        """Reads accepted data."""

    @abstractmethod
    def delete_quarantine(self, path: str) -> None:
        """Deletes quarantine object."""

    @abstractmethod
    def delete_accepted(self, path: str) -> None:
        """Deletes accepted object."""


class LocalDiskStorageBackend(StorageBackend):
    """Local filesystem storage backend enforcing quarantine/accepted separation."""

    def __init__(self, base_dir: Path | None = None, legacy_base: Path | None = None):
        if base_dir is None:
            # Default to a dedicated evidence vault directory under backend data
            base = Path(__file__).resolve().parent.parent.parent / "data" / "evidence_vault"
        else:
            base = base_dir

        self.base_dir = base.resolve()
        self.legacy_base = legacy_base.resolve() if legacy_base else None
        self.quarantine_dir = self.base_dir / "quarantine"
        self.accepted_dir = self.base_dir / "accepted"

        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        self.accepted_dir.mkdir(parents=True, exist_ok=True)

    def _checked_path(self, path: str, area: str) -> Path:
        target = Path(path).resolve()
        roots = [self.base_dir / area]
        if self.legacy_base:
            roots.append(self.legacy_base / area)
        if not any(target.is_relative_to(root.resolve()) for root in roots):
            raise PermissionError('Evidence path is outside the configured vault.')
        return target

    def _sanitize_key(self, key: str) -> str:
        # Strip path traversal elements, purely alphanumeric and hyphens/underscores
        clean = Path(key).name
        if not clean or clean.startswith("."):
            clean = f"obj_{uuid.uuid4().hex}"
        return clean

    def save_quarantine(self, key: str, data: bytes) -> str:
        safe_name = self._sanitize_key(key)
        target = self.quarantine_dir / safe_name
        # Atomic write via tempfile
        with tempfile.NamedTemporaryFile(dir=self.quarantine_dir, delete=False) as tf:
            tf.write(data)
            temp_path = Path(tf.name)
        temp_path.replace(target)
        return str(target)

    def read_quarantine(self, path: str) -> bytes:
        p = self._checked_path(path, 'quarantine')
        if not p.is_file():
            raise FileNotFoundError(f"Quarantine object not found at {path}")
        return p.read_bytes()

    def promote_to_accepted(self, quarantine_path: str, accepted_key: str) -> tuple[str, str, int]:
        q_path = self._checked_path(quarantine_path, 'quarantine')
        if not q_path.is_file():
            raise FileNotFoundError(f"Quarantine source not found: {quarantine_path}")

        safe_name = self._sanitize_key(accepted_key)
        target = self.accepted_dir / safe_name

        hasher = hashlib.sha256()
        total_bytes = 0

        with (
            open(q_path, "rb") as src,
            tempfile.NamedTemporaryFile(dir=self.accepted_dir, delete=False) as dst,
        ):
            while chunk := src.read(65536):
                hasher.update(chunk)
                total_bytes += len(chunk)
                dst.write(chunk)
            temp_path = Path(dst.name)

        temp_path.replace(target)
        sha256_hash = hasher.hexdigest()

        # Delete from quarantine after successful promotion
        try:
            q_path.unlink()
        except OSError:
            pass

        return str(target), sha256_hash, total_bytes

    def read_accepted(self, path: str) -> bytes:
        p = self._checked_path(path, 'accepted')
        if not p.is_file():
            raise FileNotFoundError(f"Accepted object not found at {path}")
        return p.read_bytes()

    def delete_quarantine(self, path: str) -> None:
        target = self._checked_path(path, 'quarantine')
        try:
            target.unlink(missing_ok=True)
        except OSError:
            pass

    def delete_accepted(self, path: str) -> None:
        target = self._checked_path(path, 'accepted')
        try:
            target.unlink(missing_ok=True)
        except OSError:
            pass


# Global singleton storage backend
_legacy_vault = Path(__file__).resolve().parent.parent.parent / 'data' / 'evidence_vault'
_configured_vault = Path(settings.LOCAL_STORAGE_DIR).resolve() if 'LOCAL_STORAGE_DIR' in settings.model_fields_set else _legacy_vault
default_storage: StorageBackend = LocalDiskStorageBackend(_configured_vault, legacy_base=_legacy_vault)


def get_storage_backend() -> StorageBackend:
    if settings.STORAGE_BACKEND != 'local':
        raise RuntimeError('Ebarki has no configured adapter for this storage backend.')
    return default_storage
