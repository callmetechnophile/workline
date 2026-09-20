import pytest
from backend.workline.artifacts.store import S3ArtifactStore, FilesystemArtifactStore


@pytest.mark.asyncio
async def test_s3_artifact_store_lifecycle():
    store = S3ArtifactStore(bucket_name="test-bucket")
    test_data = b"MOCK_CAD_STEP_DATA_FOR_WORKLINE_ENGINEERING"
    
    # Put artifact
    art = await store.put_artifact(
        filename="chassis_bracket.step",
        data=test_data,
        project_id="proj-101",
        category="cad"
    )

    assert art.filename == "chassis_bracket.step"
    assert art.project_id == "proj-101"
    assert art.category == "cad"
    assert art.size_bytes == len(test_data)
    assert len(art.sha256_hash) == 64

    # Get bytes
    retrieved = await store.get_artifact_bytes(art.artifact_id)
    assert retrieved == test_data

    # Generate presigned GET
    get_url = await store.generate_presigned_get_url(art.artifact_id)
    assert get_url is not None

    # Generate presigned PUT
    put_spec = await store.generate_presigned_put_url("thermal_contour.png", "proj-101", "thermal")
    assert "upload_url" in put_spec
