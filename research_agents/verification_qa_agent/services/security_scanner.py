"""
Security scanning and prompt injection detection service for VerificationQAAgent (Sections 27, 28, 56).
Scans implementation files for hardcoded secrets (with masking), command injection, and prompt injection risks.
"""

import os
from pathlib import Path
import re
from typing import List, Optional
import uuid
from research_agents.verification_qa_agent.schemas import SecurityFinding


class SecurityScanner:
    """Detects security vulnerabilities, hardcoded secrets, and unsafe execution patterns."""

    SECRET_PATTERNS = [
        (r"(?i)api[_-]?key\s*[:=]\s*['\"]([^'\"]{8,})['\"]", "secret", "Hardcoded API Key"),
        (r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*['\"]([^'\"]{16,})['\"]", "secret", "Hardcoded AWS Secret Key"),
        (r"(?i)password\s*[:=]\s*['\"]([^'\"]{6,})['\"]", "secret", "Hardcoded Password"),
        (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "secret", "Hardcoded Private Key"),
        (r"(?i)system\(\s*f?['\"].*?(rm -rf|curl |wget ).*?['\"]\s*\)", "command_injection", "Unsafe Shell Command Execution"),
        (r"(?i)ignore previous instructions and", "prompt_injection", "Prompt Injection Token"),
    ]

    def __init__(self, project_root_dir: Optional[str] = None):
        self.project_root_dir = Path(project_root_dir or ".").resolve()

    def mask_secret(self, val: str) -> str:
        """Masks sensitive token preserving prefix and suffix."""
        if len(val) <= 6:
            return "******"
        return val[:3] + "*" * (len(val) - 6) + val[-3:]

    def scan_files(self, file_paths: List[str]) -> List[SecurityFinding]:
        """
        Scans specified file paths for security vulnerabilities.
        """
        findings: List[SecurityFinding] = []

        for rel_path in file_paths:
            full_path = self.project_root_dir / rel_path
            if not full_path.exists() or not full_path.is_file():
                continue

            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
                lines = content.splitlines()

                for line_idx, line in enumerate(lines, start=1):
                    for pat, cat, title in self.SECRET_PATTERNS:
                        match = re.search(pat, line)
                        if match:
                            raw_val = match.group(1) if match.groups() else match.group(0)
                            masked = self.mask_secret(raw_val)
                            clean_line = line.replace(raw_val, masked)

                            findings.append(
                                SecurityFinding(
                                    finding_id=f"SEC-{uuid.uuid4().hex[:6].upper()}",
                                    category=cat,
                                    severity="CRITICAL" if cat == "secret" else "HIGH",
                                    file=rel_path,
                                    line=line_idx,
                                    masked_snippet=clean_line.strip(),
                                    description=f"{title} detected on line {line_idx}.",
                                )
                            )
            except Exception:
                pass

        return findings
