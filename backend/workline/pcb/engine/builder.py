"""PCB Builder constructing PCBProject from BOM and canonical components."""

import math
from typing import Dict, List, Optional
import uuid

from backend.workline.pcb.models.board import Board, Keepout, MountingHole
from backend.workline.pcb.models.component import PCBComponent
from backend.workline.pcb.models.constraints import PCBConstraint
from backend.workline.pcb.models.footprint import Footprint, Pad
from backend.workline.pcb.models.net import Net, NetClass, NetNode
from backend.workline.pcb.models.pin import ElectricalType, Pin
from backend.workline.pcb.models.placement import ComponentPlacement, Placement, PlacementZone, ZoneType
from backend.workline.pcb.models.power import PowerModel, PowerRail
from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.models.stackup import Stackup
from backend.workline.pcb.models.thermal import BoardThermalProperties, ThermalComponent, ThermalModel
from backend.workline.procurement.models import BOM, BOMItem


class PCBBuilder:
    """Builds a complete, strongly-typed PCBProject from a Bill of Materials."""

    @staticmethod
    def get_standard_footprints() -> Dict[str, Footprint]:
        """Provides normalized standard footprints for common component categories."""
        return {
            "FP_QFN32": Footprint(
                id="FP_QFN32",
                name="QFN-32 (5x5mm)",
                package="QFN-32",
                body_width=5.0,
                body_height=5.0,
                courtyard_width=6.0,
                courtyard_height=6.0,
                pads=[
                    Pad(number=i + 1, x=-2.4 + (i % 8) * 0.6, y=-2.4 if i < 16 else 2.4, width=0.3, height=0.8)
                    for i in range(32)
                ],
            ),
            "FP_SOT223": Footprint(
                id="FP_SOT223",
                name="SOT-223",
                package="SOT-223",
                body_width=6.5,
                body_height=3.5,
                courtyard_width=7.5,
                courtyard_height=7.0,
                pads=[
                    Pad(number=1, x=-2.3, y=-3.1, width=1.0, height=1.8),
                    Pad(number=2, x=0.0, y=-3.1, width=1.0, height=1.8),
                    Pad(number=3, x=2.3, y=-3.1, width=1.0, height=1.8),
                    Pad(number=4, x=0.0, y=3.1, width=3.3, height=1.8), # Thermal Tab
                ],
            ),
            "FP_SOIC8": Footprint(
                id="FP_SOIC8",
                name="SOIC-8",
                package="SOIC-8",
                body_width=4.9,
                body_height=3.9,
                courtyard_width=6.0,
                courtyard_height=5.0,
                pads=[
                    Pad(number=1, x=-2.6, y=-1.9, width=1.5, height=0.6),
                    Pad(number=2, x=-2.6, y=-0.63, width=1.5, height=0.6),
                    Pad(number=3, x=-2.6, y=0.63, width=1.5, height=0.6),
                    Pad(number=4, x=-2.6, y=1.9, width=1.5, height=0.6),
                    Pad(number=5, x=2.6, y=1.9, width=1.5, height=0.6),
                    Pad(number=6, x=2.6, y=0.63, width=1.5, height=0.6),
                    Pad(number=7, x=2.6, y=-0.63, width=1.5, height=0.6),
                    Pad(number=8, x=2.6, y=-1.9, width=1.5, height=0.6),
                ],
            ),
            "FP_0805": Footprint(
                id="FP_0805",
                name="0805 (2012 Metric)",
                package="0805",
                body_width=2.0,
                body_height=1.25,
                courtyard_width=2.8,
                courtyard_height=1.8,
                pads=[
                    Pad(number=1, x=-0.95, y=0.0, width=1.0, height=1.3),
                    Pad(number=2, x=0.95, y=0.0, width=1.0, height=1.3),
                ],
            ),
            "FP_MODULE_ESP32": Footprint(
                id="FP_MODULE_ESP32",
                name="ESP32-S3-WROOM-1 Module",
                package="Module",
                body_width=18.0,
                body_height=25.5,
                courtyard_width=19.5,
                courtyard_height=27.0,
                pads=[
                    Pad(number=i + 1, x=-9.0 if i < 20 else 9.0, y=-10.0 + (i % 20) * 1.0, width=1.5, height=0.8)
                    for i in range(40)
                ],
            ),
            "FP_HDR_1X4": Footprint(
                id="FP_HDR_1X4",
                name="Pin Header 1x4 (2.54mm)",
                package="Through-Hole Header",
                body_width=10.16,
                body_height=2.54,
                courtyard_width=11.5,
                courtyard_height=3.5,
                pads=[
                    Pad(number=i + 1, x=-3.81 + i * 2.54, y=0.0, width=1.7, height=1.7, shape="CIRCULAR", layer="THROUGH_HOLE")
                    for i in range(4)
                ],
            ),
        }

    @classmethod
    def build_from_bom(cls, project_id: str, bom: BOM, board_width: float = 80.0, board_height: float = 60.0) -> PCBProject:
        """Constructs a full PCBProject with assigned footprints, pins, nets, and initial placement."""
        fps = cls.get_standard_footprints()

        pcb_components: Dict[str, PCBComponent] = {}
        thermal_components: Dict[str, ThermalComponent] = {}
        placements: Dict[str, ComponentPlacement] = {}

        ref_counts: Dict[str, int] = {}

        # Default standard net list
        nets: Dict[str, Net] = {
            "net_gnd": Net(id="net_gnd", name="GND", net_class=NetClass.GROUND, priority=5, voltage=0.0, criticality="CRITICAL"),
            "net_3v3": Net(id="net_3v3", name="VCC_3V3", net_class=NetClass.POWER, priority=4, voltage=3.3, current=1.2, criticality="CRITICAL"),
            "net_5v": Net(id="net_5v", name="VCC_5V", net_class=NetClass.POWER, priority=4, voltage=5.0, current=0.5, criticality="HIGH"),
            "net_i2c_sda": Net(id="net_i2c_sda", name="I2C_SDA", net_class=NetClass.DIGITAL, priority=3, voltage=3.3, frequency=400000.0),
            "net_i2c_scl": Net(id="net_i2c_scl", name="I2C_SCL", net_class=NetClass.CLOCK, priority=3, voltage=3.3, frequency=400000.0),
            "net_uart_tx": Net(id="net_uart_tx", name="UART_TX", net_class=NetClass.DIGITAL, priority=2, voltage=3.3),
            "net_uart_rx": Net(id="net_uart_rx", name="UART_RX", net_class=NetClass.DIGITAL, priority=2, voltage=3.3),
        }

        # 3-column grid placement (col 0=large ICs, col 1=medium ICs/passives, col 2=connectors)
        col_y = [8.0, 8.0, 8.0]

        for item in bom.items:
            for q in range(item.quantity):
                cat = (getattr(item, "category", None) or getattr(item, "description", None) or "").lower()
                mpn = (getattr(item, "mpn", None) or "").upper()

                # Determine RefDes prefix and footprint
                if "microcontroller" in cat or "compute" in cat or "esp32" in mpn:
                    prefix = "U"
                    fp_id = "FP_MODULE_ESP32"
                    power_w = 0.45
                    pins = [
                        Pin(component_id="", pin_number=1, name="GND", electrical_type=ElectricalType.GROUND, net_id="net_gnd"),
                        Pin(component_id="", pin_number=2, name="3V3", electrical_type=ElectricalType.POWER, net_id="net_3v3"),
                        Pin(component_id="", pin_number=8, name="I2C_SDA", electrical_type=ElectricalType.BIDIRECTIONAL, net_id="net_i2c_sda"),
                        Pin(component_id="", pin_number=9, name="I2C_SCL", electrical_type=ElectricalType.OUTPUT, net_id="net_i2c_scl"),
                        Pin(component_id="", pin_number=17, name="TXD0", electrical_type=ElectricalType.OUTPUT, net_id="net_uart_tx"),
                        Pin(component_id="", pin_number=18, name="RXD0", electrical_type=ElectricalType.INPUT, net_id="net_uart_rx"),
                    ]
                elif "power" in cat or "regulator" in cat or "lm2596" in mpn or "tps" in mpn:
                    prefix = "U"
                    fp_id = "FP_SOT223"
                    power_w = 0.85 # Higher heat dissipation for regulator
                    pins = [
                        Pin(component_id="", pin_number=1, name="VIN", electrical_type=ElectricalType.POWER, net_id="net_5v"),
                        Pin(component_id="", pin_number=2, name="GND", electrical_type=ElectricalType.GROUND, net_id="net_gnd"),
                        Pin(component_id="", pin_number=3, name="VOUT", electrical_type=ElectricalType.POWER, net_id="net_3v3"),
                        Pin(component_id="", pin_number=4, name="TAB", electrical_type=ElectricalType.GROUND, net_id="net_gnd"),
                    ]
                elif "sensor" in cat or "bme" in mpn or "mpu" in mpn or "adc" in cat:
                    prefix = "U"
                    fp_id = "FP_SOIC8"
                    power_w = 0.05
                    pins = [
                        Pin(component_id="", pin_number=1, name="VDD", electrical_type=ElectricalType.POWER, net_id="net_3v3"),
                        Pin(component_id="", pin_number=2, name="GND", electrical_type=ElectricalType.GROUND, net_id="net_gnd"),
                        Pin(component_id="", pin_number=3, name="SDA", electrical_type=ElectricalType.BIDIRECTIONAL, net_id="net_i2c_sda"),
                        Pin(component_id="", pin_number=4, name="SCL", electrical_type=ElectricalType.INPUT, net_id="net_i2c_scl"),
                    ]
                elif "connector" in cat or "header" in cat:
                    prefix = "J"
                    fp_id = "FP_HDR_1X4"
                    power_w = 0.01
                    pins = [
                        Pin(component_id="", pin_number=1, name="VCC", electrical_type=ElectricalType.POWER, net_id="net_5v"),
                        Pin(component_id="", pin_number=2, name="GND", electrical_type=ElectricalType.GROUND, net_id="net_gnd"),
                        Pin(component_id="", pin_number=3, name="TX", electrical_type=ElectricalType.OUTPUT, net_id="net_uart_tx"),
                        Pin(component_id="", pin_number=4, name="RX", electrical_type=ElectricalType.INPUT, net_id="net_uart_rx"),
                    ]
                else:
                    prefix = "R" if "res" in cat else ("C" if "cap" in cat else "U")
                    fp_id = "FP_0805"
                    power_w = 0.02
                    pins = [
                        Pin(component_id="", pin_number=1, name="1", electrical_type=ElectricalType.PASSIVE, net_id="net_3v3"),
                        Pin(component_id="", pin_number=2, name="2", electrical_type=ElectricalType.PASSIVE, net_id="net_gnd"),
                    ]

                count = ref_counts.get(prefix, 0) + 1
                ref_counts[prefix] = count
                ref_des = f"{prefix}{count}"
                comp_instance_id = f"pcb_comp_{ref_des.lower()}"

                # Link pin IDs to component
                for p in pins:
                    p.component_id = comp_instance_id
                    if p.net_id and p.net_id in nets:
                        nets[p.net_id].nodes.append(NetNode(component_id=comp_instance_id, pin_number=p.pin_number, pin_name=p.name))

                fp = fps[fp_id]
                w = fp.courtyard_width or (fp.body_width + 1.0)
                h = fp.courtyard_height or (fp.body_height + 1.0)

                # 3-column assignment:
                #  col 0 (x≈15): large ICs (MODULE_ESP32 etc, w>10)
                #  col 1 (x≈36): medium ICs (SOT223, SOIC8, etc)
                #  col 2 (x≈47): connectors (always pinned far-right)
                if prefix == "J":
                    c_idx = 2
                elif w > 10.0:
                    c_idx = 0
                else:
                    c_idx = 1

                col_x_vals = [
                    max(w / 2.0 + 3.0, board_width * 0.22),
                    board_width * 0.55,
                    board_width - w / 2.0 - 3.0,
                ]
                pos_x = col_x_vals[c_idx]
                pos_y = col_y[c_idx]

                # clamp to board boundary
                pos_x = max(w / 2.0 + 2.0, min(pos_x, board_width - w / 2.0 - 2.0))
                pos_y = max(h / 2.0 + 2.0, min(pos_y, board_height - h / 2.0 - 2.0))

                # Advance column y
                col_y[c_idx] += h + 6.0
                if col_y[c_idx] > board_height - h / 2.0 - 4.0:
                    col_y[c_idx] = h / 2.0 + 4.0

                comp = PCBComponent(
                    id=comp_instance_id,
                    component_id=item.component_id,
                    reference_designator=ref_des,
                    value=item.mpn,
                    footprint_id=fp_id,
                    x=round(pos_x, 2),
                    y=round(pos_y, 2),
                    rotation=0.0,
                    layer="TOP",
                    mounting_type="THROUGH_HOLE" if "HDR" in fp_id else "SMD",
                    locked=(prefix == "J"), # Lock external connectors to edges
                    pins=pins,
                )

                pcb_components[comp.id] = comp
                placements[comp.id] = ComponentPlacement(
                    component_id=comp.id,
                    reference_designator=ref_des,
                    x=comp.x,
                    y=comp.y,
                    locked=comp.locked,
                )

                thermal_components[comp.id] = ThermalComponent(
                    component_id=comp.id,
                    power_dissipation=power_w,
                    thermal_resistance_jc=25.0 if prefix == "U" else 50.0,
                    max_junction_temperature=125.0,
                    ambient_temperature=25.0,
                )

        board = Board(
            width=board_width,
            height=board_height,
            mounting_holes=[
                MountingHole(id="MH1", x=4.0, y=4.0, diameter=3.2),
                MountingHole(id="MH2", x=board_width - 4.0, y=4.0, diameter=3.2),
                MountingHole(id="MH3", x=4.0, y=board_height - 4.0, diameter=3.2),
                MountingHole(id="MH4", x=board_width - 4.0, y=board_height - 4.0, diameter=3.2),
            ],
            keepouts=[
                Keepout(id="KO_EDGE", name="Board Edge Clearance", x=0.0, y=0.0, width=board_width, height=board_height),
            ],
        )

        power_model = PowerModel(
            rails={
                "3V3": PowerRail(name="3V3", voltage=3.3, max_current=1.5, estimated_current=0.65, consumers=[c.reference_designator for c in pcb_components.values()]),
                "5V": PowerRail(name="5V", voltage=5.0, max_current=1.0, estimated_current=0.30),
            },
            total_power_watts=sum(t.power_dissipation for t in thermal_components.values()),
        )

        thermal_model = ThermalModel(
            board_properties=BoardThermalProperties(ambient_temperature=25.0),
            components=thermal_components,
            ambient_temperature=25.0,
        )

        placement_model = Placement(
            placements=placements,
            zones=[
                PlacementZone(id="Z_POWER", name="Power Zone", zone_type=ZoneType.POWER_ZONE, x=5.0, y=5.0, width=30.0, height=25.0),
                PlacementZone(id="Z_DIGITAL", name="Digital Core", zone_type=ZoneType.DIGITAL_ZONE, x=35.0, y=5.0, width=40.0, height=50.0),
            ],
        )

        return PCBProject(
            project_id=project_id,
            name=f"{project_id.capitalize()} PCB Design",
            board=board,
            stackup=Stackup(),
            components=pcb_components,
            footprints=fps,
            nets=nets,
            constraints=PCBConstraint(project_id=project_id),
            placement=placement_model,
            power=power_model,
            thermal=thermal_model,
        )
