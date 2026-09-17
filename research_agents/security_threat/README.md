# Agent #22: SecurityThreatModelingAgent

**SecurityThreatModelingAgent** is the central cybersecurity threat modeling, attack surface discovery, trust boundary analysis, security control mapping, and security test specification engine for **WorkflowGuide AI**.

---

## 1. Responsibilities & Boundaries

- **Owns:**
  - Threat Modeling (STRIDE + Agentic AI categories)
  - Attack Surface Discovery & Ingress Point Mapping
  - Trust Boundary Analysis & Sensitive Data Flow Tracing
  - Multi-Step Attack Path Construction
  - Security Control Mapping & Least-Privilege Audits
  - Security Test Case Generation (for Agent #18)
  - Change Security Impact Analysis & Security Regression Flagging
  - Security Gate Evaluation (`SECURITY_PASS`, `SECURITY_REVIEW_REQUIRED`, `SECURITY_BLOCKED`)
- **Does NOT Own:**
  - Engineering FMEA (Agent #21)
  - Regulatory Compliance Authority (Agent #17)
  - Runtime Authorization Enforcement (ArmorIQ)
  - Verification Authority (Agent #18)
  - Change Approval (Agent #16)
  - Lifecycle Orchestration (Agent #14)

---

## 2. CLI Usage

```bash
# Discover assets
python -m research_agents.security_threat assets --project PROJ-001

# Map attack surface
python -m research_agents.security_threat surface --project PROJ-001

# View threat register
python -m research_agents.security_threat threats --project PROJ-001

# Generate security tests
python -m research_agents.security_threat tests --project PROJ-001

# Export 22-section markdown report and JSON/CSV artifacts
python -m research_agents.security_threat report --project PROJ-001 --output output/security_threat
```
