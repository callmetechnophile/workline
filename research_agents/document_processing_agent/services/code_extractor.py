"""
Code block extraction service for DocumentProcessingAgent (Section 21).
Extracts source code snippets with language detection and page provenance without executing them.
"""

import re
from typing import List
from research_agents.document_processing_agent.schemas import (
    ExtractedBlock,
    ExtractedCodeBlock,
)


class CodeBlockExtractor:
    """Detects and extracts code snippets from document blocks."""

    LANG_HINTS = {
        "python": [r"import\s+\w+", r"from\s+\w+\s+import", r"def\s+\w+\(.*\):", r"class\s+\w+:"],
        "cpp": [r"#include\s*<.*>", r"int\s+main\(.*\)", r"std::", r"uint8_t\s+"],
        "c": [r"#include\s*<stdio\.h>", r"void\s+\w+\(.*\)", r"struct\s+\w+\s*\{"],
        "rust": [r"fn\s+main\(.*\)", r"let\s+mut\s+", r"impl\s+\w+"],
        "javascript": [r"function\s+\w+\(.*\)", r"const\s+\w+\s*=", r"console\.log\("],
        "json": [r"^\s*\{\s*\"[\w-]+\":", r"^\s*\[\s*\{"],
        "yaml": [r"^\s*[\w-]+:\s*.*$", r"^\s*-\s+[\w-]+:"],
        "bash": [r"^\s*\$\s+", r"^\s*sudo\s+", r"^\s*apt-get\s+", r"^\s*pip\s+install"],
    }

    def extract_code_blocks(self, blocks: List[ExtractedBlock]) -> List[ExtractedCodeBlock]:
        """
        Scans extracted blocks and identifies code snippets.
        """
        code_blocks: List[ExtractedCodeBlock] = []

        for b in blocks:
            text = b.text.strip()
            # 1. Explicit Markdown Code Fence
            if text.startswith("```"):
                fence_match = re.match(r"^```([a-zA-Z0-9_-]*)\n([\s\S]*?)```$", text)
                if fence_match:
                    lang = fence_match.group(1).strip() or self._detect_language(fence_match.group(2))
                    code_blocks.append(
                        ExtractedCodeBlock(
                            language=lang or None,
                            code=fence_match.group(2).strip(),
                            page=b.page_number,
                        )
                    )
                    continue

            # 2. Block marked as 'code' by HTML/PDF parser
            if b.block_type == "code":
                lang = self._detect_language(text)
                code_blocks.append(
                    ExtractedCodeBlock(
                        language=lang or None,
                        code=text,
                        page=b.page_number,
                    )
                )
                continue

            # 3. Code heuristics on short/indented block
            if self._is_likely_code(text):
                lang = self._detect_language(text)
                if lang:
                    code_blocks.append(
                        ExtractedCodeBlock(
                            language=lang,
                            code=text,
                            page=b.page_number,
                        )
                    )

        return code_blocks

    def _detect_language(self, text: str) -> str:
        for lang, patterns in self.LANG_HINTS.items():
            for pat in patterns:
                if re.search(pat, text, re.MULTILINE):
                    return lang
        return ""

    def _is_likely_code(self, text: str) -> bool:
        if "#include <" in text or "def " in text or "function " in text or "console.log" in text:
            return True
        return False
