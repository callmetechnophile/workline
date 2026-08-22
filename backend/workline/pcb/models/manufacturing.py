"""Design For Manufacturing (DFM) capabilities and constraints."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ManufacturingConstraints(BaseModel):
    """Fabrication and assembly capability boundaries."""
    min_trace_width_mm: float = 0.127  # 5 mil
    min_spacing_mm: float = 0.127      # 5 mil
    min_drill_diameter_mm: float = 0.30 # 12 mil
    min_annular_ring_mm: float = 0.15  # 6 mil
    copper_to_board_edge_mm: float = 0.30
    solder_mask_expansion_mm: float = 0.05
    silkscreen_min_text_height_mm: float = 0.80
    silkscreen_min_line_width_mm: float = 0.15
    surface_finish: str = "ENIG"       # ENIG, HASL, OSP
    solder_mask_color: str = "GREEN"   # GREEN, BLUE, BLACK, RED, MATTE_BLACK
    silkscreen_color: str = "WHITE"
