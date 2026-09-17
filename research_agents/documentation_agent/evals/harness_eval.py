"""
Harness evaluation for Agent #27 — Technical Documentation & Engineering Publication Agent.
5 benchmark points covering the Zero-Fabrication invariant, lifecycle transitions,
self-approval block, ArmorIQ guard, and conflict detection.
"""

import json
from research_agents.documentation_agent.agent import TechDocAgent


def run_eval() -> dict:
    agent  = TechDocAgent()
    results = {}

    # ── Point 1: Create document — authority not invented ─────────────────────
    res1 = agent.run({
        "project_id": "EVAL-PROJ",
        "operation":  "create_document",
        "user_id":    "eng.alice",
        "document_type": "FMEA_REPORT",
        "title":      "Thermal Subsystem FMEA",
        "authority_claim": "UNKNOWN",
    })
    results["point_1_authority_not_elevated"] = {
        "passed":    res1["status"] == "ok" and res1["document"]["authority"] == "UNKNOWN",
        "authority": res1.get("document", {}).get("authority"),
    }

    doc_id = res1.get("document", {}).get("doc_id", "")

    # ── Point 2: Self-approval blocked ───────────────────────────────────────
    # Submit for review first
    agent.run({"project_id": "EVAL-PROJ", "operation": "review_document",
                "user_id": "eng.alice", "doc_id": doc_id})
    res2 = agent.run({
        "project_id": "EVAL-PROJ",
        "operation":  "approve_document",
        "user_id":    "eng.alice",   # same as author → must be denied
        "doc_id":     doc_id,
    })
    results["point_2_self_approval_blocked"] = {
        "passed":  res2["status"] == "error" and "SELF_APPROVAL_DENIED" in " ".join(res2.get("errors", [])),
        "errors":  res2.get("errors", []),
    }

    # ── Point 3: Approve by different user ───────────────────────────────────
    res3 = agent.run({
        "project_id": "EVAL-PROJ",
        "operation":  "approve_document",
        "user_id":    "eng.bob",
        "doc_id":     doc_id,
    })
    results["point_3_approval_by_other_user"] = {
        "passed":  res3["status"] == "ok" and res3.get("document", {}).get("status") == "APPROVED",
        "status":  res3.get("document", {}).get("status"),
    }

    # ── Point 4: Controlled publication requires ArmorIQ ─────────────────────
    res4 = agent.run({
        "project_id": "EVAL-PROJ",
        "operation":  "publish_document",
        "user_id":    "eng.bob",
        "doc_id":     doc_id,
        "metadata":   {"channel": "CONTROLLED_VAULT", "armoriq_authorized": False},
    })
    results["point_4_armoriq_required"] = {
        "passed":  res4["status"] == "error" and "ARMORIQ" in " ".join(res4.get("errors", [])),
        "errors":  res4.get("errors", []),
    }

    # ── Point 5: Conflict detection (CONFLICT_DETECTED, never auto-resolved) ──
    res5a = agent.run({
        "project_id": "EVAL-PROJ",
        "operation":  "create_document",
        "user_id":    "eng.alice",
        "document_type": "FMEA_REPORT",
        "title":      "Thermal Subsystem FMEA",   # same type + title → duplicate conflict
    })
    doc_id_b = res5a.get("document", {}).get("doc_id", "")
    res5 = agent.run({
        "project_id": "EVAL-PROJ",
        "operation":  "detect_conflicts",
        "doc_id":     doc_id,
        "doc_id_b":   doc_id_b,
    })
    all_resolutions = [c.get("resolution") for c in res5.get("conflicts", [])]
    results["point_5_conflict_detected_not_resolved"] = {
        "passed":      res5["status"] in ("conflict_detected", "ok") and
                       all(r == "CONFLICT_DETECTED" for r in all_resolutions),
        "conflicts":   len(res5.get("conflicts", [])),
        "resolutions": all_resolutions,
    }

    all_passed = all(v["passed"] for v in results.values())
    return {
        "all_passed":        all_passed,
        "benchmark_results": results,
        "summary":           f"Passed {sum(v['passed'] for v in results.values())}/5 evaluation points.",
    }


if __name__ == "__main__":
    print(json.dumps(run_eval(), indent=2, default=str))
