"""Token encoding, decoding, hashing, and URL formatting for opaque invitation links."""

import base64
import hashlib
import json
import os
from typing import Optional

from backend.workline.collaboration.invitations.encryption import (
    InvalidTokenError,
    InvitationEncryptionEngine,
    invitation_crypto,
)
from backend.workline.collaboration.invitations.models import InvitationPayload

DEFAULT_BASE_URL = os.environ.get("WORKLINE_BASE_URL", "https://workline.app")


class TokenService:
    """
    Handles packaging of encrypted payloads into opaque URL-safe tokens,
    and server-side cryptographic hashing for database lookups.
    """

    def __init__(self, crypto: InvitationEncryptionEngine = invitation_crypto):
        self.crypto = crypto

    def encode_token(self, payload: InvitationPayload, key_version: str = "v1") -> str:
        """
        Serializes payload into JSON, performs AES-256-GCM encryption, and packs into an opaque URL-safe token.
        Binary packet format:
        [1 byte: key_version_len] + [key_version bytes] + [12 bytes: nonce] + [ciphertext_and_tag]
        """
        payload_dict = payload.model_dump()
        payload_bytes = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")

        nonce, ciphertext_and_tag, version = self.crypto.encrypt_payload(payload_bytes, key_version=key_version)

        ver_bytes = version.encode("ascii")
        if len(ver_bytes) > 255:
            raise ValueError("Key version identifier exceeds maximum allowed length.")

        packet = bytes([len(ver_bytes)]) + ver_bytes + nonce + ciphertext_and_tag
        return base64.urlsafe_b64encode(packet).decode("ascii").rstrip("=")

    def decode_token(self, opaque_token: str) -> InvitationPayload:
        """
        Unpacks and authenticates an opaque URL-safe token.
        Returns the decrypted InvitationPayload if authentication tag verifies.
        """
        if not opaque_token or not isinstance(opaque_token, str):
            raise InvalidTokenError("Empty or invalid token format.")

        # Re-add URL-safe base64 padding
        s = opaque_token.strip()
        padding_needed = (-len(s)) % 4
        padded = s + ("=" * padding_needed)

        try:
            packet = base64.urlsafe_b64decode(padded.encode("ascii"))
        except Exception as e:
            raise InvalidTokenError(f"Malformed base64 token string: {e}")

        # Unpack binary packet
        if len(packet) < 1 + 1 + 12 + 16:  # len_byte + min_ver + nonce(12) + tag(16)
            raise InvalidTokenError("Token packet is shorter than minimum required length.")

        ver_len = packet[0]
        if len(packet) < 1 + ver_len + 12 + 16:
            raise InvalidTokenError("Invalid token header structure.")

        ver_start = 1
        ver_end = ver_start + ver_len
        version = packet[ver_start:ver_end].decode("ascii", errors="ignore")

        nonce_start = ver_end
        nonce_end = nonce_start + 12
        nonce = packet[nonce_start:nonce_end]

        ciphertext_and_tag = packet[nonce_end:]

        plaintext_bytes = self.crypto.decrypt_payload(
            nonce=nonce,
            ciphertext_and_tag=ciphertext_and_tag,
            key_version=version,
        )

        try:
            data = json.loads(plaintext_bytes.decode("utf-8"))
            return InvitationPayload.model_validate(data)
        except Exception as e:
            raise InvalidTokenError(f"Decrypted payload format invalid: {e}")

    def hash_token(self, opaque_token: str) -> str:
        """
        Produces a secure SHA-256 fingerprint of the token for database lookup and revocation.
        Plaintext tokens are never stored in the database.
        """
        clean_token = opaque_token.strip()
        return hashlib.sha256(clean_token.encode("utf-8")).hexdigest()

    def build_join_url(self, opaque_token: str, base_url: Optional[str] = None) -> str:
        """Constructs safe recipient join URL with opaque token."""
        domain = (base_url or os.environ.get("WORKLINE_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        return f"{domain}/team/join/{opaque_token}"


# Module-level singleton
token_service = TokenService()
