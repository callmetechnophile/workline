"""Comprehensive Datasheet Discovery, Verification, and Indexing Service."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.workline.database.models import GraphEdge, GraphNode
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.procurement.cache import datasheet_cache
from backend.workline.procurement.datasheets.extractor import DatasheetExtractor
from backend.workline.procurement.datasheets.verifier import DatasheetVerifier
from backend.workline.procurement.models import DatasheetInfo, DatasheetMetadata, DatasheetStatus
from backend.workline.retrieval.qdrant import COLLECTION_RESEARCH, QdrantManager, qdrant_manager


class DatasheetService:
    """
    Orchestrates datasheet discovery from Nexar and fallback web sources,
    verifies document authenticity, persists SurrealDB metadata, and indexes text into Qdrant.
    """

    def __init__(
        self,
        verifier: Optional[DatasheetVerifier] = None,
        extractor: Optional[DatasheetExtractor] = None,
        graph_repo: Optional[GraphRepository] = None,
        qdrant: Optional[QdrantManager] = None,
    ):
        self.verifier = verifier or DatasheetVerifier()
        self.extractor = extractor or DatasheetExtractor()
        self.graph_repo = graph_repo or GraphRepository()
        self.qdrant = qdrant or qdrant_manager

    async def verify_and_index(
        self,
        datasheet: DatasheetMetadata,
        project_id: Optional[str] = None,
        component_id: Optional[str] = None,
    ) -> DatasheetMetadata:
        """Verify datasheet, save to SurrealDB knowledge graph, and index in Qdrant."""
        status, reason = self.verifier.verify(datasheet, datasheet.manufacturer, datasheet.mpn)
        datasheet.verification_status = status

        # 1. Persist SurrealDB Graph Node & Edge
        if component_id:
            ds_node_id = f"datasheet:{datasheet.datasheet_id.replace(':', '_')}"
            await self.graph_repo.save_node(
                GraphNode(
                    id=ds_node_id,
                    type="Datasheet",
                    label=datasheet.title or f"{datasheet.mpn} Datasheet",
                    data={
                        "project_id": project_id,
                        "component_id": component_id,
                        "url": datasheet.url,
                        "status": datasheet.verification_status.value,
                        "document_type": datasheet.document_type,
                    },
                )
            )
            await self.graph_repo.save_edge(
                GraphEdge(
                    id=f"has_ds:{component_id.replace(':', '_')}_{ds_node_id.replace(':', '_')}",
                    source_id=component_id,
                    target_id=ds_node_id,
                    relationship="HAS_DATASHEET",
                    data={"project_id": project_id},
                )
            )

        # 2. Index in Qdrant vector database if verified
        if status == DatasheetStatus.VERIFIED:
            summary = f"Technical Datasheet for {datasheet.manufacturer} {datasheet.mpn}. Type: {datasheet.document_type}. URL: {datasheet.url}."
            self.qdrant.index_document(
                collection=COLLECTION_RESEARCH,
                doc_id=datasheet.datasheet_id,
                text=summary,
                payload={
                    "component_id": component_id,
                    "project_id": project_id,
                    "manufacturer": datasheet.manufacturer,
                    "mpn": datasheet.mpn,
                    "document_type": datasheet.document_type,
                    "url": datasheet.url,
                    "verified": True,
                },
            )

        return datasheet


# Singleton Datasheet Service
datasheet_service = DatasheetService()
