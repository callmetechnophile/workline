from typing import List, Dict, Any, Optional

# Verified authentic manufacturer datasheet index
VERIFIED_MANUFACTURER_DATASHEETS = {
    "usb5734": {
        "link": "https://ww1.microchip.com/downloads/en/DeviceDoc/00002166B.pdf",
        "manufacturer": "Microchip Technology",
        "source": "Microchip Official",
        "mpn": "USB5734/MR",
    },
    "tps65987": {
        "link": "https://www.ti.com/lit/ds/symlink/tps65987d.pdf",
        "manufacturer": "Texas Instruments",
        "source": "Texas Instruments Official",
        "mpn": "TPS65987DDHR",
    },
    "tpd4e05u06": {
        "link": "https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf",
        "manufacturer": "Texas Instruments",
        "source": "Texas Instruments Official",
        "mpn": "TPD4E05U06DQAR",
    },
    "tps54331": {
        "link": "https://www.ti.com/lit/ds/symlink/tps54331.pdf",
        "manufacturer": "Texas Instruments",
        "source": "Texas Instruments Official",
        "mpn": "TPS54331DR",
    },
    "lm5116": {
        "link": "https://www.ti.com/lit/ds/symlink/lm5116.pdf",
        "manufacturer": "Texas Instruments",
        "source": "Texas Instruments Official",
        "mpn": "LM5116MH/NOPB",
    },
    "esp32": {
        "link": "https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf",
        "manufacturer": "Espressif Systems",
        "source": "Espressif Systems Official",
        "mpn": "ESP32-WROOM-32D",
    },
    "stm32f4": {
        "link": "https://www.st.com/resource/en/datasheet/stm32f407vg.pdf",
        "manufacturer": "STMicroelectronics",
        "source": "STMicroelectronics Official",
        "mpn": "STM32F407VET6",
    },
    "pca9685": {
        "link": "https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf",
        "manufacturer": "NXP Semiconductors",
        "source": "NXP Semiconductors Official",
        "mpn": "PCA9685PW",
    },
    "bme688": {
        "link": "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme688-ds000.pdf",
        "manufacturer": "Bosch Sensortec",
        "source": "Bosch Sensortec Official",
        "mpn": "BME688",
    },
    "neo-m8": {
        "link": "https://content.u-blox.com/sites/default/files/NEO-M8-FW3_DataSheet_UBX-15031086.pdf",
        "manufacturer": "u-blox",
        "source": "u-blox Official",
        "mpn": "NEO-M8N-0",
    },
}


def fetch_datasheet_links(component_name: str, mpn: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves verified manufacturer datasheet links.
    Never fabricates fake URLs. If unverified, returns DATASHEET UNAVAILABLE.
    """
    search_str = f"{component_name} {mpn or ''}".lower()
    
    for key, spec in VERIFIED_MANUFACTURER_DATASHEETS.items():
        if key in search_str:
            return {
                "component": component_name,
                "mpn": spec.get("mpn", mpn or component_name),
                "manufacturer": spec.get("manufacturer", "Semiconductor Manufacturer"),
                "datasheet_link": spec["link"],
                "source": spec["source"],
                "trust_status": "TRUSTED_MANUFACTURER",
                "status": "AVAILABLE",
            }
            
    # If no verified datasheet URL exists, mark DATASHEET UNAVAILABLE without inventing URLs
    return {
        "component": component_name,
        "mpn": mpn or "N/A",
        "manufacturer": "Unknown",
        "datasheet_link": None,
        "source": "N/A",
        "trust_status": "UNAVAILABLE",
        "status": "DATASHEET UNAVAILABLE",
    }
