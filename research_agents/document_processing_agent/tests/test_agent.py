"""
End-to-end unit and integration tests for DocumentProcessingAgent.
"""

import tempfile
import pytest
from pathlib import Path

from research_agents.document_processing_agent.agent import DocumentProcessingAgent
from research_agents.document_processing_agent.schemas import DocumentProcessingInput
from research_agents.document_processing_agent.tests.test_pdf_parser import create_sample_pdf_bytes


@pytest.mark.asyncio
async def test_agent_process_pdf_local_file():
    pdf_bytes = create_sample_pdf_bytes()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    agent = DocumentProcessingAgent()
    input_data = DocumentProcessingInput(
        document_id="paper_sar_001",
        local_path=tmp_path,
        document_type="pdf",
        title="Thermal Human Detection on Edge UAVs",
    )

    output = await agent.run(input_data)

    # Clean up temp file
    Path(tmp_path).unlink(missing_ok=True)

    assert output.status == "success"
    assert output.document_id == "paper_sar_001"
    assert output.metadata.page_count == 2
    assert "<!-- source_page: 1 -->" in output.markdown
    assert len(output.chunks) >= 2
    assert len(output.entities) >= 2
    assert len(output.facts) >= 1
    assert output.quality_score >= 0.70


@pytest.mark.asyncio
async def test_agent_process_text_file():
    text_content = (
        "# Synchronous Buck Converter Specifications\n\n"
        "## Electrical Characteristics\n"
        "The TPS54308 buck converter operates at 24 V input voltage and delivers 3.3 V output at 3 A current.\n\n"
        "## Thermal Dissipation\n"
        "Operating temperature range is -40 °C to 125 °C.\n"
    )
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(text_content)
        tmp_path = tmp.name

    agent = DocumentProcessingAgent()
    input_data = DocumentProcessingInput(
        document_id="spec_buck_002",
        local_path=tmp_path,
        document_type="text",
    )

    output = await agent.run(input_data)
    Path(tmp_path).unlink(missing_ok=True)

    assert output.status == "success"
    assert len(output.chunks) >= 2
    assert len(output.facts) >= 1


@pytest.mark.asyncio
async def test_agent_missing_file_error():
    agent = DocumentProcessingAgent()
    input_data = DocumentProcessingInput(
        document_id="non_existent",
        local_path="C:/non_existent_folder/missing_file.pdf",
    )

    output = await agent.run(input_data)
    assert output.status == "error"
    assert len(output.errors) > 0
    assert output.errors[0].code == "FILE_NOT_FOUND"


def test_agent_sync_execution():
    text_content = "# Quick Spec\n\nESP32 operates at 3.3 V."
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(text_content)
        tmp_path = tmp.name

    agent = DocumentProcessingAgent()
    input_data = DocumentProcessingInput(
        document_id="quick_sync_test",
        local_path=tmp_path,
    )

    output = agent.run_sync(input_data)
    Path(tmp_path).unlink(missing_ok=True)

    assert output.status == "success"
    assert len(output.chunks) >= 1
