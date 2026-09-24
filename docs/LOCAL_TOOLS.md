# WORKLINE Local Tools (MCP & A2A)

## Overview

WORKLINE provides extensible tool interfaces through the **Model Context Protocol (MCP)** and **Agent-to-Agent (A2A / Bindu)** protocols.
These tools allow local agents, IDE assistants, and automated engineering pipelines to inspect, validate, and query `.wl` projects safely.

---

## Local MCP Server (`cli/workline/mcp/server.py`)

The local MCP server exposes project context directly to MCP-compatible clients (e.g. Claude Desktop, VS Code, Antigravity).

### Launching the Server
```bash
python -m cli.workline.mcp.server
```

### Provided Tools

1. **`workline_search`**
   - **Description**: Hybrid semantic and keyword search across `.wl` project files.
   - **Parameters**: `query: str`, `top_k: int = 10`, `resource_types: Optional[List[str]] = None`
   - **Returns**: Formatted list of `EngineeringRecord` instances.

2. **`workline_context`**
   - **Description**: Assembles a unified multi-domain context bundle (BOM, requirements, pinout, power) for a query.
   - **Parameters**: `query: str`
   - **Returns**: Structured dictionary of engineering context.

3. **`workline_component_lookup`**
   - **Description**: Retrieves technical dossiers and parametric data for a component by MPN.
   - **Parameters**: `mpn: str`
   - **Returns**: Component dossier or `null` if not found.

---

## Agent-to-Agent (A2A / Bindu Protocol)

The Bindu protocol (`backend/workline/interoperability/bindu/`) facilitates peer-to-peer delegation between specialized engineering agents:
- **`component_lookup`**: Asynchronous MPN cross-referencing and substitute discovery.
- **`drc_rules_check`**: Automated design-rule validation checks across subsystem boundaries.
- **Cryptographic Provenance**: Every inter-agent message carries an ArmorIQ HMAC-SHA256 signature ensuring traceable delegation chains.
