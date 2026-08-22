"""Cryptographic verification tests for AES-256-GCM team invitation encryption."""

import base64
import json
import secrets
import pytest

from backend.workline.collaboration.invitations.encryption import (
    CryptographicError,
    InvalidKeyVersionError,
    InvalidTokenError,
    InvitationEncryptionEngine,
)
from backend.workline.collaboration.invitations.models import InvitationPayload
from backend.workline.collaboration.invitations.token import TokenService


def test_encryption_and_decryption_roundtrip():
    """Test standard AES-256-GCM encryption and decryption roundtrip."""
    crypto = InvitationEncryptionEngine()
    test_payload = b'{"invitation_id": "inv_12345", "team_id": "team_pcb", "key_version": "v1"}'

    nonce, ciphertext_and_tag, version = crypto.encrypt_payload(test_payload, key_version="v1")
    assert len(nonce) == 12
    assert len(ciphertext_and_tag) > len(test_payload)
    assert version == "v1"

    decrypted = crypto.decrypt_payload(nonce, ciphertext_and_tag, key_version="v1")
    assert decrypted == test_payload


def test_tampered_ciphertext_detection():
    """Test that modifying even one bit in the ciphertext fails authentication tag verification."""
    crypto = InvitationEncryptionEngine()
    test_payload = b'{"team_id": "secret_team"}'

    nonce, ciphertext_and_tag, version = crypto.encrypt_payload(test_payload, key_version="v1")

    # Flip one byte
    tampered_bytes = bytearray(ciphertext_and_tag)
    tampered_bytes[0] ^= 0xFF
    tampered_ciphertext = bytes(tampered_bytes)

    with pytest.raises(InvalidTokenError):
        crypto.decrypt_payload(nonce, tampered_ciphertext, key_version=version)


def test_invalid_authentication_tag():
    """Test that tampering with the tag part at the end of ciphertext fails immediately."""
    crypto = InvitationEncryptionEngine()
    test_payload = b'{"invitation_id": "inv_abc"}'

    nonce, ciphertext_and_tag, version = crypto.encrypt_payload(test_payload, key_version="v1")

    # Tamper with the 16-byte tag at the end
    tampered = ciphertext_and_tag[:-1] + bytes([ciphertext_and_tag[-1] ^ 0x01])

    with pytest.raises(InvalidTokenError):
        crypto.decrypt_payload(nonce, tampered, key_version=version)


def test_wrong_key_and_key_rotation():
    """Test key rotation: tokens encrypted with v1 or v2 decrypt with their respective keys."""
    crypto = InvitationEncryptionEngine()
    key_v1 = secrets.token_bytes(32)
    key_v2 = secrets.token_bytes(32)

    crypto.register_key("v1", key_v1)
    crypto.register_key("v2", key_v2)

    payload_v1 = b'{"token": "version1_token"}'
    payload_v2 = b'{"token": "version2_token"}'

    nonce1, ct1, ver1 = crypto.encrypt_payload(payload_v1, key_version="v1")
    nonce2, ct2, ver2 = crypto.encrypt_payload(payload_v2, key_version="v2")

    # Decrypt with matching versions
    assert crypto.decrypt_payload(nonce1, ct1, key_version=ver1) == payload_v1
    assert crypto.decrypt_payload(nonce2, ct2, key_version=ver2) == payload_v2

    # Attempting to decrypt v1 ciphertext with v2 key must fail
    with pytest.raises(InvalidTokenError):
        crypto.decrypt_payload(nonce1, ct1, key_version="v2")

    # Unknown key version
    with pytest.raises(InvalidKeyVersionError):
        crypto.decrypt_payload(nonce1, ct1, key_version="v99")


def test_nonce_handling_and_entropy():
    """Test that identical payloads produce distinct nonces and distinct ciphertexts."""
    crypto = InvitationEncryptionEngine()
    payload = b'{"team_id": "team_alpha"}'

    nonce1, ct1, _ = crypto.encrypt_payload(payload)
    nonce2, ct2, _ = crypto.encrypt_payload(payload)

    assert nonce1 != nonce2
    assert ct1 != ct2


def test_url_safe_token_encoding_and_opaque_structure():
    """Test that TokenService produces URL-safe strings without leaking plaintext."""
    token_svc = TokenService()
    payload = InvitationPayload(
        invitation_id="inv_987654321",
        team_id="secret_research_team_123",
        expires_at="2026-09-01T00:00:00Z",
        key_version="v1",
    )

    opaque_token = token_svc.encode_token(payload)

    # 1. URL safe check: only url-safe base64 characters
    assert all(c.isalnum() or c in "-_" for c in opaque_token)

    # 2. Opaque check: team ID and invitation ID are NOT in the string
    assert "secret_research_team_123" not in opaque_token
    assert "inv_987654321" not in opaque_token
    assert "2026-09-01" not in opaque_token

    # 3. Decode check
    decoded_payload = token_svc.decode_token(opaque_token)
    assert decoded_payload.invitation_id == "inv_987654321"
    assert decoded_payload.team_id == "secret_research_team_123"
    assert decoded_payload.key_version == "v1"
