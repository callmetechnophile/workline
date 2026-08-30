"""
Unit tests for code block extraction without execution (Section 21).
"""

from research_agents.document_processing_agent.schemas import ExtractedBlock
from research_agents.document_processing_agent.services.code_extractor import CodeBlockExtractor


def test_code_block_extraction_cpp():
    extractor = CodeBlockExtractor()
    blocks = [
        ExtractedBlock(
            block_id="b1",
            page_number=4,
            text="```cpp\n#include <Arduino.h>\n#include <Wire.h>\nvoid setup() { Wire.begin(); }\n```",
            block_type="code",
        ),
        ExtractedBlock(
            block_id="b2",
            page_number=5,
            text="```python\nimport torch\nimport cv2\ndef detect(image):\n    return model(image)\n```",
            block_type="code",
        ),
    ]

    code_blocks = extractor.extract_code_blocks(blocks)
    assert len(code_blocks) == 2

    cpp_block = code_blocks[0]
    assert cpp_block.language == "cpp"
    assert "Wire.begin()" in cpp_block.code
    assert cpp_block.page == 4

    py_block = code_blocks[1]
    assert py_block.language == "python"
    assert "import torch" in py_block.code
    assert py_block.page == 5
