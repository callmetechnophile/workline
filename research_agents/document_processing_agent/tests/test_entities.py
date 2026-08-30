"""
Unit tests for engineering entity extraction.
"""

from research_agents.document_processing_agent.schemas import ExtractedBlock
from research_agents.document_processing_agent.services.entity_extractor import EngineeringEntityExtractor


def test_entity_extraction_microcontroller_sensor_interfaces():
    extractor = EngineeringEntityExtractor()
    blocks = [
        ExtractedBlock(
            block_id="b1",
            page_number=1,
            text="The prototype utilizes an ESP32-S3 microcontroller connected to an MPU6050 IMU sensor over I2C.",
        ),
        ExtractedBlock(
            block_id="b2",
            page_number=2,
            text="High-throughput vision processing runs on NVIDIA Jetson Orin Nano with ROS 2 Humble and TensorRT.",
        ),
    ]

    entities = extractor.extract_entities(blocks)
    names = {e.name.lower() for e in entities}

    assert any("esp32-s3" in n or "esp32" in n for n in names)
    assert any("mpu6050" in n or "mpu-6050" in n for n in names)
    assert any("i2c" in n for n in names)
    assert any("jetson" in n for n in names)
    assert any("ros" in n for n in names)
