"""Cryptographic engine for authenticated AES-256-GCM encryption of team invitation payloads."""

import base64
import json
import logging
import os
import secrets
from typing import Dict, Optional, Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger("workline.invitations.encryption")

DEFAULT_AAD = b"WORKLINE_TEAM_INVITATION_V1"
DEFAULT_KEY_VERSION = "v1"


class CryptographicError(Exception):
    """Base exception for cryptographic operations."""
    pass


class InvalidTokenError(CryptographicError):
    """Raised when token authentication, decryption, or structure validation fails."""
    pass


class InvalidKeyVersionError(CryptographicError):
    """Raised when the specified key version is unknown or unsupported."""
    pass


class InvitationEncryptionEngine:
    """
    Manages AES-256-GCM authenticated encryption and key rotation for invitation tokens.
    Guarantees keys remain strictly on the backend and are never exposed.
    """

    def __init__(self):
        self._keys: Dict[str, bytes] = {}
        self._active_version: str = DEFAULT_KEY_VERSION
        self._load_keys()

    def _load_keys(self) -> None:
        """Loads encryption keys from environment variables with safe in-memory fallback."""
        # Key v1
        k1 = os.environ.get("WORKLINE_INVITATION_KEY_V1") or os.environ.get("WORKLINE_INVITATION_ENCRYPTION_KEY")
        if k1:
            self._keys["v1"] = self._parse_key_bytes(k1)
        else:
            # Generate deterministic in-memory session key for testing/dev if no env provided
            # (Ensures zero plaintext keys are ever hardcoded or committed)
            self._keys["v1"] = secrets.token_bytes(32)

        # Optional Key v2 for rotation
        k2 = os.environ.get("WORKLINE_INVITATION_KEY_V2")
        if k2:
            self._keys["v2"] = self._parse_key_bytes(k2)

    def _parse_key_bytes(self, raw_val: str) -> bytes:
        """Parses hex, base64, or raw string key into 32 bytes."""
        val = raw_val.strip()
        # Try hex
        if len(val) == 64:
            try:
                return bytes.fromhex(val)
            except ValueError:
                pass
        # Try base64
        try:
            decoded = base64.b64decode(val)
            if len(decoded) == 32:
                return decoded
        except Exception:
            pass
        # Raw bytes padded/hashed to 32 bytes
        import hashlib
        return hashlib.sha256(val.encode("utf-8")).digest()

    def register_key(self, version: str, key_bytes: bytes) -> None:
        """Registers a key version for rotation support."""
        if len(key_bytes) != 32:
            raise CryptographicError("AES-256-GCM requires exactly 32-byte key.")
        self._keys[version] = key_bytes

    def set_active_key_version(self, version: str) -> None:
        """Sets the active key version for new encryptions."""
        if version not in self._keys:
            raise InvalidKeyVersionError(f"Key version '{version}' is not registered.")
        self._active_version = version

    def encrypt_payload(
        self,
        payload_bytes: bytes,
        key_version: Optional[str] = None,
        aad: bytes = DEFAULT_AAD,
    ) -> Tuple[bytes, bytes, str]:
        """
        Encrypts payload using AES-256-GCM with a random 12-byte nonce.
        Returns: (nonce, ciphertext_with_tag, key_version)
        """
        version = key_version or self._active_version
        if version not in self._keys:
            raise InvalidKeyVersionError(f"Unknown key version: {version}")

        key = self._keys[version]
        nonce = secrets.token_bytes(12)  # 96-bit cryptographically secure random nonce
        aesgcm = AESGCM(key)

        # AESGCM encrypt produces ciphertext + 16-byte authentication tag appended
        ciphertext_and_tag = aesgcm.encrypt(nonce, payload_bytes, aad)
        return nonce, ciphertext_and_tag, version

    def decrypt_payload(
        self,
        nonce: bytes,
        ciphertext_and_tag: bytes,
        key_version: str,
        aad: bytes = DEFAULT_AAD,
    ) -> bytes:
        """
        Decrypts and authenticates AES-256-GCM payload.
        Fails immediately if ciphertext or authentication tag is tampered with.
        """
        if key_version not in self._keys:
            logger.warning(f"Decryption failed: Unknown key version '{key_version}'.")
            raise InvalidKeyVersionError(f"Unsupported key version: {key_version}")

        if len(nonce) != 12:
            logger.warning("Decryption failed: Invalid nonce length.")
            raise InvalidTokenError("Invalid nonce length.")

        key = self._keys[key_version]
        aesgcm = AESGCM(key)

        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext_and_tag, aad)
            return plaintext
        except Exception as e:
            logger.warning(f"Decryption failed: Cryptographic authentication tag verification failed ({e}).")
            raise InvalidTokenError("Authentication tag verification failed.") from e


# Module-level singleton
invitation_crypto = InvitationEncryptionEngine()
