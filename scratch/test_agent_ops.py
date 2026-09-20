import urllib.request
import json
import time

def test():
    base = "http://127.0.0.1:8000/api/agents"
    
    # 1. Test GET /api/agents
    print("--- 1. Testing GET /api/agents ---")
    req = urllib.request.Request(f"{base}")
    with urllib.request.urlopen(req) as resp:
        agents = json.loads(resp.read().decode())
        print(f"Total registered agents: {len(agents)}")
        clusters = {}
        for a in agents:
            tier = a.get("cluster_tier", "UNKNOWN")
            clusters[tier] = clusters.get(tier, 0) + 1
        print("Agents by Cluster:", clusters)

    # 2. Test Task Submission (BMS Validation)
    print("\n--- 2. Testing POST /api/agents/tasks (EngineeringValidationAgent) ---")
    payload = {
        "project_id": "Smart Battery Management System (BMS) for 4S",
        "team_id": "default_team",
        "requesting_agent": "WorklineUser",
        "target_agent": "EngineeringValidationAgent",
        "capability": "bms_validation",
        "payload": {
            "pack_configuration": "4S",
            "cell_chemistry": "LiFePO4",
            "nominal_voltage": 12.8,
            "max_charge_voltage": 14.6,
            "min_discharge_voltage": 10.0,
            "overcurrent_threshold_a": 30.0
        },
        "actor_id": "lead_engineer",
        "human_approved": True
    }
    req2 = urllib.request.Request(f"{base}/tasks", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req2) as resp:
        task_res = json.loads(resp.read().decode())
        print(f"Task ID: {task_res.get('task_id')}")
        print(f"Task Status: {task_res.get('status')}")
        print(f"Provenance Hash: {task_res.get('provenance', {}).get('output_hash') if task_res.get('provenance') else None}")
        print(f"ArmorIQ Receipt: {task_res.get('armoriq_receipt')}")

    # 3. Test Task Submission (Thermal Check)
    print("\n--- 3. Testing POST /api/agents/tasks (ThermalSolver) ---")
    thermal_payload = {
        "project_id": "Smart Battery Management System (BMS) for 4S",
        "team_id": "default_team",
        "requesting_agent": "WorklineUser",
        "target_agent": "ThermalSolver",
        "capability": "thermal_simulation",
        "payload": {
            "board_width": 120,
            "board_height": 80,
            "components": [
                {"ref": "Q1_MOSFET", "power_w": 3.5},
                {"ref": "U1_AFE", "power_w": 0.4}
            ]
        },
        "actor_id": "lead_engineer",
        "human_approved": True
    }
    req3 = urllib.request.Request(f"{base}/tasks", data=json.dumps(thermal_payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req3) as resp:
        thermal_res = json.loads(resp.read().decode())
        print(f"Thermal Task ID: {thermal_res.get('task_id')}")
        print(f"Thermal Task Status: {thermal_res.get('status')}")
        print(f"Thermal ArmorIQ Receipt: {thermal_res.get('armoriq_receipt')}")

    # 4. Test GET /api/agents/tasks
    print("\n--- 4. Testing GET /api/agents/tasks ---")
    req4 = urllib.request.Request(f"{base}/tasks?project_id=Smart%20Battery%20Management%20System%20(BMS)%20for%204S")
    with urllib.request.urlopen(req4) as resp:
        tasks = json.loads(resp.read().decode())
        print(f"Total tasks for project: {len(tasks)}")
        for t in tasks[:3]:
            print(f"  - [{t.get('status')}] {t.get('task_id')} -> {t.get('target_agent')} ({t.get('capability')})")

    # 5. Test GET /api/agents/executions
    print("\n--- 5. Testing GET /api/agents/executions ---")
    req5 = urllib.request.Request(f"{base}/executions?project_id=Smart%20Battery%20Management%20System%20(BMS)%20for%204S")
    with urllib.request.urlopen(req5) as resp:
        executions = json.loads(resp.read().decode())
        print(f"Total execution records: {len(executions)}")
        for ex in executions[:3]:
            print(f"  - [{ex.get('status')}] {ex.get('execution_id')}: {ex.get('action')} | Receipt: {ex.get('armoriq_receipt')}")

if __name__ == "__main__":
    time.sleep(1)
    test()
