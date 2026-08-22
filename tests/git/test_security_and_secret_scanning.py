"""Tests for Git safety policies, secret scanning, .env exclusion, and credential protection."""

from pathlib import Path
import pytest

from backend.workline.git.errors import SecretDetectedError
from backend.workline.git.policies import SecretScanner, generate_default_gitignore
from backend.workline.git.service import GitService


def test_secret_scanner_detects_api_keys_and_tokens():
    """Test detection of standard API keys, GitHub tokens, and private keys."""
    # OpenAI style key
    content1 = 'OPENAI_API_KEY = "sk-123456789012345678901234567890"'
    findings1 = SecretScanner.scan_content(content1)
    assert len(findings1) > 0
    assert any("OpenAI" in f.secret_type or "API Key" in f.secret_type for f in findings1)
    # Ensure sample is redacted
    assert "..." in findings1[0].matched_sample or "***" in findings1[0].matched_sample

    # GitHub PAT
    content2 = 'token: "ghp_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789"'
    findings2 = SecretScanner.scan_content(content2)
    assert len(findings2) > 0
    assert any("GitHub Token" in f.secret_type for f in findings2)

    # Generic Private Key
    content3 = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----"
    findings3 = SecretScanner.scan_content(content3)
    assert len(findings3) > 0
    assert any("Private Key" in f.secret_type for f in findings3)


def test_secret_scanner_detects_nexar_and_x402_secrets():
    """Test detection of Nexar client secrets and x402 payment secrets."""
    content_nexar = 'NEXAR_CLIENT_SECRET = "nexar_secret_abcdef1234567890_key"'
    findings_nexar = SecretScanner.scan_content(content_nexar)
    assert len(findings_nexar) > 0
    assert any("Nexar" in f.secret_type or "API Key" in f.secret_type for f in findings_nexar)

    content_x402 = 'x402_private_key = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"'
    findings_x402 = SecretScanner.scan_content(content_x402)
    assert len(findings_x402) > 0
    assert any("Wallet" in f.secret_type or "x402" in f.secret_type for f in findings_x402)


def test_sensitive_file_detection():
    """Test sensitive file identification."""
    assert SecretScanner.is_sensitive_file(".env") is True
    assert SecretScanner.is_sensitive_file(".env.local") is True
    assert SecretScanner.is_sensitive_file(".env.production") is True
    assert SecretScanner.is_sensitive_file("id_rsa") is True
    assert SecretScanner.is_sensitive_file("wallet.json") is True
    assert SecretScanner.is_sensitive_file(".env.example") is False
    assert SecretScanner.is_sensitive_file("main.py") is False


def test_commit_blocked_when_secret_staged(tmp_path: Path):
    """Test that GitService blocks commit and raises SecretDetectedError when a secret is staged."""
    svc = GitService()
    svc.initialize_repository(tmp_path, "main")

    # Write a file containing a private key
    leaky_file = tmp_path / "config.py"
    leaky_file.write_text('GITHUB_TOKEN = "ghp_1234567890abcdef1234567890abcdef123456"', encoding="utf-8")

    svc.stage_files(tmp_path)

    with pytest.raises(SecretDetectedError) as exc_info:
        svc.create_commit(tmp_path, "Add config", scan_secrets=True)

    assert "Potential secret or credential detected" in str(exc_info.value)
    assert len(exc_info.value.findings) > 0


def test_default_gitignore_covers_secrets():
    """Verify that default .gitignore covers .env, secrets, caches, and checkpoints."""
    gitignore_text = generate_default_gitignore()
    assert ".env" in gitignore_text
    assert ".env.*" in gitignore_text
    assert "!.env.example" in gitignore_text
    assert "*.pem" in gitignore_text
    assert "*.key" in gitignore_text
    assert "wallet.json" in gitignore_text
    assert "__pycache__/" in gitignore_text
    assert ".venv/" in gitignore_text
    assert "*.onnx" in gitignore_text
    assert "*.pt" in gitignore_text
