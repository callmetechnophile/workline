"""Deep security sanitizer for project packages to prevent exporting credentials or secrets."""

import re
from typing import Any, Dict, List, Set, Tuple
from backend.workline.git.policies import SecretScanner


class SecuritySanitizer:
    """
    Recursively scans and strips sensitive authentication tokens, API keys,
    private cryptographic keys, payment secrets, database passwords, and invitation secrets
    from project state before export into a .wlipjt package.
    """

    SENSITIVE_FIELD_NAMES: Set[str] = {
        "api_key",
        "apikey",
        "secret",
        "secret_key",
        "client_secret",
        "private_key",
        "privkey",
        "password",
        "passwd",
        "auth_token",
        "access_token",
        "refresh_token",
        "token",
        "x402_private_key",
        "wallet_secret",
        "seed_phrase",
        "mnemonic",
        "nexar_client_secret",
        "invitation_secret",
        "invitation_token",
        "invitation_key",
        "encryption_key",
        "raw_token",
        "session_token",
        "jwt",
    }

    @classmethod
    def sanitize_data(cls, data: Any, current_key: str = "") -> Tuple[Any, List[str]]:
        """
        Recursively sanitizes a data structure (dict, list, primitive) and returns
        the sanitized copy along with a list of redaction warnings.
        """
        warnings: List[str] = []

        if isinstance(data, dict):
            sanitized_dict = {}
            for k, v in sorted(data.items(), key=lambda x: str(x[0])):
                k_lower = str(k).lower().strip()
                if any(sens == k_lower or sens in k_lower for sens in cls.SENSITIVE_FIELD_NAMES):
                    if v is not None and str(v).strip() and str(v) != "None":
                        warnings.append(f"Sensitive credential omitted from package: field '{k}'")
                        sanitized_dict[k] = "[REDACTED_CREDENTIAL]"
                    else:
                        sanitized_dict[k] = None
                else:
                    sub_val, sub_warn = cls.sanitize_data(v, current_key=str(k))
                    sanitized_dict[k] = sub_val
                    warnings.extend(sub_warn)
            return sanitized_dict, warnings

        elif isinstance(data, list):
            sanitized_list = []
            for item in data:
                sub_item, sub_warn = cls.sanitize_data(item, current_key=current_key)
                sanitized_list.append(sub_item)
                warnings.extend(sub_warn)
            return sanitized_list, warnings

        elif isinstance(data, str):
            # Check string value with SecretScanner patterns
            findings = SecretScanner.scan_content(data, file_path=current_key or "record")
            if findings:
                warnings.append(f"Sensitive credential omitted from package in '{current_key}': {findings[0].secret_type}")
                return "[REDACTED_CREDENTIAL]", warnings
            return data, warnings

        return data, warnings

    @classmethod
    def sanitize_toon_text(cls, text: str, label: str = "") -> Tuple[str, List[str]]:
        """Scans TOON structured text line by line and replaces matched secrets."""
        warnings: List[str] = []
        findings = SecretScanner.scan_content(text, file_path=label or "toon_content")
        if not findings:
            return text, warnings

        lines = text.splitlines()
        for f in findings:
            line_idx = f.line_number - 1
            if 0 <= line_idx < len(lines):
                warnings.append(f"Sensitive credential omitted from package in '{label}': {f.secret_type}")
                lines[line_idx] = re.sub(r'[:=]\s*["\']?[^"\']+["\']?', ': "[REDACTED_CREDENTIAL]"', lines[line_idx])

        return "\n".join(lines) + "\n", warnings
