"""Secret detection rules, Git safety policies, and repository name validation."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.workline.git.errors import InvalidRepoNameError, SecretDetectedError


# Regex patterns for credential and secret detection
SECRET_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub Token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,255}\b")),
    ("Generic Private Key", re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----")),
    ("Generic API Key / Bearer", re.compile(r"""(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|secret[_-]?key)\s*[:=]\s*['"][A-Za-z0-9\-_.]{16,}['"]""")),
    ("OpenAI / Anthropic Key", re.compile(r"\b(sk-[a-zA-Z0-9]{20,}|sk-ant-[a-zA-Z0-9_\-]{20,})\b")),
    ("Google API Key", re.compile(r"\bAIza[0-9A-Za-z-_]{35}\b")),
    ("Crypto Wallet Private Key", re.compile(r"\b0x[a-fA-F0-9]{64}\b")),
    ("Mnemonic Seed Phrase", re.compile(r"\b(abandon|ability|able|about|above|absent|absorb|abstract|absurd|abuse|access|accident|account|accuse|achieve|acid|acoustic|acquire|across|act|action|actor|actress|actual|adapt|add|addict|address|adjust|admit|adult|advance|advice|aerobic|affair|afford|afraid|again|age|agent|agree|ahead|aim|air|airport|aisle|alarm|album|alcohol|alert|alien|all|alley|allow|almost|alone|alpha|already|also|alter|always|amateur|amazing|among|amount|amused|analyst|anchor|ancient|anger|angle|angry|animal|ankle|announce|annual|another|answer|antenna|antique|anxiety|any|apart|apology|appear|apple|approve|april|arch|arctic|area|arena|argue|arm|armed|armor|army|around|arrange|arrest|arrive|arrow|art|artefact|artist|artwork|ask|aspect|assault|asset|assist|assume|asthma|athlete|atom|attack|attend|attitude|attract|auction|audit|august|aunt|author|auto|autumn|average|avocado|avoid|awake|aware|away|awesome|awful|awkward|axis|baby|bachelor|bacon|badge|bag|balance|balcony|ball|bamboo|banana|banner|bar|barely|bargain|barrel|base|basic|basket|battle|beach|bean|beauty|because|become|beef|before|begin|behave|behind|believe|below|belt|bench|benefit|best|betray|better|between|beyond|bicycle|bid|bike|bind|biology|bird|birth|bitter|black|blade|blame|blanket|blast|bleak|bless|blind|blood|blossom|blouse|blue|blur|blush|board|boat|body|boil|bomb|bone|bonus|book|boost|border|boring|borrow|boss|bottom|bounce|box|boy|bracket|brain|brand|brass|brave|bread|breeze|brick|bridge|brief|bright|bring|brisk|broccoli|broken|bronze|broom|brother|brown|brush|bubble|buddy|budget|buffalo|build|bulb|bulk|bullet|bundle|bunker|burden|burger|burst|bus|business|busy|butter|buyer|buzz)\s+(?:[a-z]+\s+){10,23}[a-z]+\b")),
    ("Nexar Secret", re.compile(r"""(?i)nexar[_-]?(?:secret|token|client_secret)\s*[:=]\s*['"][A-Za-z0-9\-_]{20,}['"]""")),
    ("x402 Payment Secret", re.compile(r"""(?i)x402[_-]?(?:secret|private_key|key)\s*[:=]\s*['"][A-Za-z0-9\-_]{20,}['"]""")),
    ("Database Password URL", re.compile(r"://[^:]+:([^@]+)@[a-zA-Z0-9.-]+:[0-9]+")),
]

# Sensitive file patterns that must never be staged
SENSITIVE_FILE_NAMES: List[str] = [
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "wallet.json",
    "secrets.yaml",
    "credentials.json",
]


class SecretFinding:
    def __init__(self, file_path: str, line_number: int, secret_type: str, matched_sample: str):
        self.file_path = file_path
        self.line_number = line_number
        self.secret_type = secret_type
        # Redact matched sample
        if len(matched_sample) > 8:
            self.matched_sample = matched_sample[:3] + "..." + matched_sample[-3:]
        else:
            self.matched_sample = "***"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file_path,
            "line": self.line_number,
            "type": self.secret_type,
            "sample": self.matched_sample,
        }

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_number} [{self.secret_type}]"


class SecretScanner:
    """Scans text content and file paths for accidentally exposed secrets and credentials."""

    @staticmethod
    def scan_content(content: str, file_path: str = "staged_file") -> List[SecretFinding]:
        findings = []
        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            for label, pattern in SECRET_PATTERNS:
                matches = pattern.finditer(line)
                for match in matches:
                    findings.append(
                        SecretFinding(
                            file_path=file_path,
                            line_number=idx,
                            secret_type=label,
                            matched_sample=match.group(0),
                        )
                    )
        return findings

    @staticmethod
    def is_sensitive_file(file_path: str) -> bool:
        p = Path(file_path)
        name = p.name.lower()
        if name in SENSITIVE_FILE_NAMES:
            return True
        if name.startswith(".env") and not name.endswith(".example"):
            return True
        if name.endswith(".pem") or name.endswith(".key") or name.endswith(".p12") or name.endswith(".pfx"):
            return True
        return False

    @classmethod
    def scan_staged_files(cls, files_with_content: Dict[str, str]) -> List[SecretFinding]:
        all_findings = []
        for fpath, content in files_with_content.items():
            if cls.is_sensitive_file(fpath):
                all_findings.append(
                    SecretFinding(
                        file_path=fpath,
                        line_number=1,
                        secret_type="Sensitive Environment / Key File",
                        matched_sample=fpath,
                    )
                )
            all_findings.extend(cls.scan_content(content, fpath))
        return all_findings


def validate_repository_name(name: str) -> str:
    """
    Validate GitHub repository naming rules:
    - 1-100 characters
    - only alphanumeric characters, periods (.), dashes (-), and underscores (_)
    - cannot begin or end with a hyphen or dot
    """
    cleaned = name.strip()
    if not cleaned:
        raise InvalidRepoNameError("Repository name cannot be empty.")
    if len(cleaned) > 100:
        raise InvalidRepoNameError(f"Repository name '{cleaned}' exceeds 100 character limit.")
    if cleaned.startswith("-") or cleaned.startswith("."):
        raise InvalidRepoNameError(f"Repository name '{cleaned}' cannot start with a hyphen or period.")
    if cleaned.endswith("-") or cleaned.endswith("."):
        raise InvalidRepoNameError(f"Repository name '{cleaned}' cannot end with a hyphen or period.")
    if not re.match(r"^[a-zA-Z0-9_.-]+$", cleaned):
        raise InvalidRepoNameError(f"Repository name '{cleaned}' contains invalid characters. Use alphanumeric, -, _, or .")
    return cleaned


def generate_default_gitignore() -> str:
    """Return the authoritative default .gitignore for Workline projects."""
    return """# Workline Authoritative Git Ignore Rules

# Environment and Secrets (CRITICAL)
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
wallet.json
secrets.yaml
credentials.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
.venv/
venv/
ENV/
env/

# Testing & Coverage
.pytest_cache/
.coverage
.coverage.*
htmlcov/
nosetests.xml
coverage.xml
*.cover

# JavaScript / Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Frontend Builds
.next/
out/

# Caches & Temp
.cache/
*.log
*.tmp
*.temp
.DS_Store
Thumbs.db

# Large Model Checkpoints & Datasets (Git LFS / External Storage)
*.h5
*.onnx
*.pt
*.pth
*.ckpt
*.safetensors
*.bin

# Local Database Files
*.sqlite3
*.db
surrealdb/
"""
