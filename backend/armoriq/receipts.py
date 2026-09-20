import os
import json
import hmac
import hashlib
import time
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

SECRET_KEY = b"armoriq-cryptographic-secure-salt-2026"

class CryptographicReceipt(BaseModel):
    receipt_id: str
    timestamp: float
    agent: str
    scope: List[str]
    parent_receipt_id: Optional[str] = None
    input_hash: Optional[str] = None
    signature: str

def calculate_signature(receipt_id: str, timestamp: float, agent: str, scope: List[str], parent_receipt_id: Optional[str] = None, input_hash: Optional[str] = None) -> str:
    # Deterministic string representation of fields
    scope_str = ",".join(sorted(scope))
    parent_id_str = parent_receipt_id or ""
    hash_str = input_hash or ""
    
    payload = f"{receipt_id}|{timestamp}|{agent}|{scope_str}|{parent_id_str}|{hash_str}"
    
    mac = hmac.new(SECRET_KEY, payload.encode('utf-8'), hashlib.sha256)
    return mac.hexdigest()

def generate_receipt(agent: str, scope: List[str], parent_receipt_id: Optional[str] = None, input_data: Optional[Any] = None) -> CryptographicReceipt:
    receipt_id = str(uuid.uuid4())
    timestamp = time.time()
    
    # Calculate input hash if input_data is provided
    input_hash = None
    if input_data is not None:
        input_hash = hashlib.sha256(str(input_data).encode('utf-8')).hexdigest()
        
    sig = calculate_signature(receipt_id, timestamp, agent, scope, parent_receipt_id, input_hash)
    
    return CryptographicReceipt(
        receipt_id=receipt_id,
        timestamp=timestamp,
        agent=agent,
        scope=scope,
        parent_receipt_id=parent_receipt_id,
        input_hash=input_hash,
        signature=sig
    )

def verify_receipt(receipt: Dict[str, Any]) -> bool:
    try:
        receipt_id = receipt.get("receipt_id")
        timestamp = receipt.get("timestamp")
        agent = receipt.get("agent")
        scope = receipt.get("scope", [])
        parent_receipt_id = receipt.get("parent_receipt_id")
        input_hash = receipt.get("input_hash")
        signature = receipt.get("signature")
        
        if not receipt_id or not timestamp or not agent or signature is None:
            return False
            
        expected_sig = calculate_signature(receipt_id, timestamp, agent, scope, parent_receipt_id, input_hash)
        return hmac.compare_digest(expected_sig, signature)
    except Exception:
        return False

# Receipt Explorer Storage Config
import tempfile

if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("LAMBDA_TASK_ROOT"):
    RECEIPTS_DIR = os.path.join(tempfile.gettempdir(), "receipts")
else:
    RECEIPTS_DIR = os.path.join(os.path.dirname(__file__), "receipts")

try:
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
except Exception:
    RECEIPTS_DIR = os.path.join(tempfile.gettempdir(), "receipts")
    try:
        os.makedirs(RECEIPTS_DIR, exist_ok=True)
    except Exception:
        pass

def save_tool_receipt(agent: str, parent: str, tool: str, scope: List[str], status: str, execution_result: Any) -> Dict[str, Any]:
    """
    Saves a tool invocation receipt as a JSON file in backend/armoriq/receipts/.
    Generates a cryptographic hash and traces the authority chain.
    """
    timestamp = str(time.time())
    
    # Calculate execution result hash
    res_str = str(execution_result)
    result_hash = hashlib.sha256(res_str.encode('utf-8')).hexdigest()
    
    # Build unique hash for the receipt
    payload = f"{agent}|{parent}|{tool}|{','.join(scope)}|{timestamp}|{status}|{result_hash}"
    receipt_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    # Trace simple authority chain
    authority_chain = ["Planner Agent"]
    if agent != "Planner Agent":
        authority_chain.append(agent)
        
    receipt_data = {
        "agent": agent,
        "parent": parent if parent else "None (Root Plan)",
        "tool": tool,
        "scope": scope,
        "timestamp": timestamp,
        "hash": receipt_hash,
        "status": "success" if status == "SUCCESS" else ("blocked" if status == "BLOCKED" else "failed"),
        "execution_result": res_str[:300] + "..." if len(res_str) > 300 else res_str,
        "authority_chain": " -> ".join(authority_chain)
    }
    
    try:
        filepath = os.path.join(RECEIPTS_DIR, f"{receipt_hash}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(receipt_data, f, indent=2)
    except Exception:
        pass
        
    return receipt_data


