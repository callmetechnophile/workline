import pytest
from backend.services.thermal_service import (
    calculate_project_thermal_analysis,
    extract_component_thermal_spec,
)

def test_thermal_extraction_verified_components():
    tps_spec = extract_component_thermal_spec({'name': 'TPS62130 Step-Down Converter', 'mpn': 'TPS62130RGTR'}, 'U1')
    assert tps_spec['data_status'] == 'AVAILABLE'
    assert tps_spec['min_temp_c'] == -40.0
    assert tps_spec['max_temp_c'] == 125.0
    assert tps_spec['range_width_c'] == 165.0
    assert 'Operating Junction' in tps_spec['temp_type']
    assert 'TI' in tps_spec['manufacturer'] or 'Texas' in tps_spec['manufacturer']

    cap_spec = extract_component_thermal_spec({'name': '10uF Ceramic Capacitor', 'category': 'Capacitor'}, 'C1')
    assert cap_spec['data_status'] == 'AVAILABLE'
    assert cap_spec['min_temp_c'] == -55.0
    assert cap_spec['max_temp_c'] == 125.0
    assert 'Murata' in cap_spec['manufacturer']

    unverified_spec = extract_component_thermal_spec({'name': 'Custom Proprietary Widget', 'mpn': 'CPW-001'}, 'U99')
    assert unverified_spec['data_status'] == 'UNAVAILABLE'
    assert unverified_spec['min_temp_c'] is None
    assert unverified_spec['max_temp_c'] is None
    assert unverified_spec['temp_type'] == 'THERMAL DATA UNAVAILABLE'

def test_cross_component_thermal_analysis():
    sample_components = [
        {'name': 'USB5734 Hub Controller', 'mpn': 'USB5734/MR', 'category': 'Controller'},
        {'name': 'TPS62130 Converter', 'mpn': 'TPS62130RGTR', 'category': 'Power'},
        {'name': '100nF Ceramic Cap', 'mpn': 'GRM188R71E104KA01D', 'category': 'Capacitor'},
        {'name': '10k Resistor', 'mpn': 'RC0603FR-0710KL', 'category': 'Resistor'},
        {'name': 'Unknown Subsystem IC', 'mpn': 'XYZ-9999', 'category': 'Custom'},
    ]

    analysis = calculate_project_thermal_analysis(components=sample_components, project_id='usb_hub_v1')

    assert analysis['project_id'] == 'usb_hub_v1'
    assert analysis['components_analyzed'] == 5
    assert analysis['thermal_data_available'] == 4
    assert analysis['thermal_data_missing'] == 1
    assert analysis['coverage_percent'] == 80.0
    assert analysis['simulation_status'] == 'THERMAL LIMIT COMPARISON ONLY'

    # Extreme lowest (-55 °C from Resistor/Capacitor)
    assert analysis['lowest_operating_temperature']['value_c'] == -55.0
    # Extreme highest (155 °C from Yageo resistor)
    assert analysis['highest_operating_temperature']['value_c'] == 155.0

    # Missing components list
    assert len(analysis['missing_components']) == 1
    assert analysis['missing_components'][0]['part_number'] == 'XYZ-9999'
