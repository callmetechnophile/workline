"""
Workline AI — RSA Asymmetric Cryptography Subsystem.

Provides:
1. RSA-OAEP + SHA-256 for asymmetric confidential payload encryption.
2. RSA-PSS + SHA-256 for tamper-proof digital signatures.
3. Server-side private key isolation (never exposed to frontend or logged).
4. Auto-generation of secure RSA-3072 keypairs for local/test environments if not supplied in env.
"""

import base64
import json
import os
from typing import Any, Dict, Optional, Tuple
from loguru import logger

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


class RsaCryptoEngine:
    """
    Production RSA asymmetric encryption and signature engine.
    Uses RSA-3072 by default with SHA-256 digest algorithms.
    """

    def __init__(
        self,
        private_key_pem: Optional[str] = None,
        public_key_pem: Optional[str] = None,
    ):
        self._private_key: Optional[RSAPrivateKey] = None
        self._public_key: Optional[RSAPublicKey] = None
        self._load_or_generate_keys(private_key_pem, public_key_pem)

    def _load_or_generate_keys(
        self,
        private_key_pem: Optional[str],
        public_key_pem: Optional[str],
    ) -> None:
        """Loads keys from parameters or env variables; generates dynamic RSA-3072 keypair if absent."""
        priv_pem = private_key_pem or os.getenv("TEAM_RSA_PRIVATE_KEY")
        pub_pem = public_key_pem or os.getenv("TEAM_RSA_PUBLIC_KEY")

        if priv_pem:
            try:
                self._private_key = serialization.load_pem_private_key(
                    priv_pem.encode("utf-8") if isinstance(priv_pem, str) else priv_pem,
                    password=None,
                )
                self._public_key = self._private_key.public_key()
                return
            except Exception as e:
                logger.warning(f"[RSA] Could not parse TEAM_RSA_PRIVATE_KEY: {e}. Generating new keypair.")

        if pub_pem and not self._private_key:
            try:
                self._public_key = serialization.load_pem_public_key(
                    pub_pem.encode("utf-8") if isinstance(pub_pem, str) else pub_pem
                )
            except Exception as e:
                logger.warning(f"[RSA] Could not parse TEAM_RSA_PUBLIC_KEY: {e}.")

        if not self._private_key:
            # Generate in-memory RSA-3072 keypair
            self._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=3072,
            )
            self._public_key = self._private_key.public_key()

    def get_public_key_pem(self) -> str:
        """Returns the public key serialized as standard PEM format."""
        if not self._public_key:
            raise ValueError("Public key is not initialized.")
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    def encrypt_payload(self, data: Dict[str, Any], public_key_pem: Optional[str] = None) -> str:
        """
        Encrypts JSON data using RSA-OAEP with SHA-256.
        Returns: base64-encoded ciphertext.
        """
        target_pub_key = self._public_key
        if public_key_pem:
            target_pub_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))

        if not target_pub_key:
            raise ValueError("No public key available for encryption.")

        raw_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
        ciphertext = target_pub_key.encrypt(
            raw_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return base64.b64encode(ciphertext).decode("utf-8")

    def decrypt_payload(self, b64_ciphertext: str) -> Dict[str, Any]:
        """
        Decrypts base64-encoded ciphertext using RSA-OAEP with SHA-256.
        Returns: decrypted dictionary.
        """
        if not self._private_key:
            raise ValueError("Private key is required to decrypt payloads.")

        raw_ciphertext = base64.b64decode(b64_ciphertext)
        decrypted_bytes = self._private_key.decrypt(
            raw_ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return json.loads(decrypted_bytes.decode("utf-8"))

    def sign_payload(self, data: Dict[str, Any]) -> str:
        """
        Generates a cryptographic signature of the canonical JSON data using RSA-PSS with SHA-256.
        Returns: base64-encoded signature.
        """
        if not self._private_key:
            raise ValueError("Private key is required to sign payloads.")

        canonical_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
        signature = self._private_key.sign(
            canonical_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def verify_signature(
        self,
        data: Dict[str, Any],
        b64_signature: str,
        public_key_pem: Optional[str] = None,
    ) -> bool:
        """
        Verifies RSA-PSS with SHA-256 signature for canonical JSON data.
        Returns: True if signature is valid, False otherwise.
        """
        target_pub_key = self._public_key
        if public_key_pem:
            try:
                target_pub_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
            except Exception:
                return False

        if not target_pub_key:
            return False

        try:
            canonical_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
            raw_signature = base64.b64decode(b64_signature)
            target_pub_key.verify(
                raw_signature,
                canonical_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False


# Global singleton engine
rsa_engine = RsaCryptoEngine()
