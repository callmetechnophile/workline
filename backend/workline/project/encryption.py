"""Cryptographic abstraction for optional encrypted project package export/import."""

from abc import ABC, abstractmethod
import base64
import hashlib
import os
from typing import Optional


class ProjectEncryptionProvider(ABC):
    """Abstract interface for optional package payload encryption."""

    @abstractmethod
    def encrypt_payload(self, data: bytes, passphrase: str) -> bytes:
        """Encrypt byte payload with derived key from passphrase."""
        pass

    @abstractmethod
    def decrypt_payload(self, encrypted_data: bytes, passphrase: str) -> bytes:
        """Decrypt byte payload with derived key from passphrase."""
        pass


class StandardEncryptionProvider(ProjectEncryptionProvider):
    """
    Standard PBKDF2 HMAC-SHA256 based payload encryption provider.
    Supports optional --encrypt flag for future multi-agent or cloud backups.
    """

    def encrypt_payload(self, data: bytes, passphrase: str) -> bytes:
        if not passphrase:
            raise ValueError("Passphrase cannot be empty for encrypted package.")

        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, 100_000, dklen=32)

        # XOR stream with sha256 keystream block chaining (self-contained fallback if cryptography package is absent)
        try:
            from cryptography.fernet import Fernet
            fernet_key = base64.urlsafe_b64encode(key)
            f = Fernet(fernet_key)
            encrypted = f.encrypt(data)
            return b"WLIPJT_ENC_V1:" + salt + b":" + encrypted
        except ImportError:
            # Fallback simple deterministic stream obfuscation header
            stream_key = hashlib.sha256(key + salt).digest()
            obfuscated = bytearray(len(data))
            for i in range(len(data)):
                obfuscated[i] = data[i] ^ stream_key[i % len(stream_key)]
            return b"WLIPJT_RAW_V1:" + salt + b":" + bytes(obfuscated)

    def decrypt_payload(self, encrypted_data: bytes, passphrase: str) -> bytes:
        if not passphrase:
            raise ValueError("Passphrase required to decrypt package.")

        parts = encrypted_data.split(b":", 2)
        if len(parts) != 3:
            raise ValueError("Invalid encrypted package container format.")

        header, salt, payload = parts[0], parts[1], parts[2]
        key = hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, 100_000, dklen=32)

        if header == b"WLIPJT_ENC_V1":
            from cryptography.fernet import Fernet
            fernet_key = base64.urlsafe_b64encode(key)
            f = Fernet(fernet_key)
            return f.decrypt(payload)
        elif header == b"WLIPJT_RAW_V1":
            stream_key = hashlib.sha256(key + salt).digest()
            decrypted = bytearray(len(payload))
            for i in range(len(payload)):
                decrypted[i] = payload[i] ^ stream_key[i % len(stream_key)]
            return bytes(decrypted)
        else:
            raise ValueError(f"Unsupported encryption header: {header}")
