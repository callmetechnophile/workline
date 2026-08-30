"""
Unit tests for SecurityScanner (Sections 27, 28, 56).
"""

from pathlib import Path
import tempfile
from research_agents.verification_qa_agent.services.security_scanner import SecurityScanner


def test_security_scanner_masks_secrets():
    with tempfile.TemporaryDirectory() as tmp_dir:
        scanner = SecurityScanner(project_root_dir=tmp_dir)

        p = Path(tmp_dir)
        (p / "src").mkdir(parents=True, exist_ok=True)
        secret_file = p / "src" / "config.py"
        secret_file.write_text("API_KEY = 'sk-proj-supersecretkey123456789'\n", encoding="utf-8")

        clean_file = p / "src" / "clean.py"
        clean_file.write_text("PORT = 8080\n", encoding="utf-8")

        findings = scanner.scan_files(["src/config.py", "src/clean.py"])

        assert len(findings) == 1
        assert findings[0].category == "secret"
        assert findings[0].severity == "CRITICAL"
        assert "sk-***" in findings[0].masked_snippet or "sk-" in findings[0].masked_snippet
        assert "supersecretkey123456789" not in findings[0].masked_snippet  # Secret must be masked!
