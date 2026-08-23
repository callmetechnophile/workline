import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from backend.database import get_db_connection, execute_query
from backend.armoriq.receipts import generate_receipt, save_tool_receipt
from backend.armoriq.delegation import log_audit_trail

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

def create_team_invitation(team_id: int, email: str, role: str) -> dict:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(days=7)
    
    # Generate ArmorIQ receipt for invitation created
    receipt = generate_receipt(
        agent="CollaborationAgent", 
        scope=["invite_member"], 
        input_data={"token_hash": token_hash, "team_id": team_id, "email": email}
    )
    receipt_id = receipt.receipt_id
    
    log_audit_trail(
        agent="CollaborationAgent",
        action="INVITATION_CREATED",
        allowed_scope=["invite_member"],
        status="SUCCESS",
        details=f"Created team invite for {email} to team {team_id}",
        receipt_id=receipt_id
    )
    save_tool_receipt("CollaborationAgent", "Planner Agent", "invite_member", ["invite_member"], "SUCCESS", f"Created invite token for {email}")
    
    conn = get_db_connection()
    query = """
        INSERT INTO team_invitations (team_id, token_hash, email, role, status, created_at, expires_at, receipt_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(
        conn, 
        query, 
        (team_id, token_hash, email, role, "Pending", created_at.isoformat(), expires_at.isoformat(), receipt_id)
    )
    conn.commit()
    conn.close()
    
    # Fetch team information for email template
    team_info = get_team_by_id(team_id)
    team_name = team_info.get("name", f"Team {team_id}")
    team_uuid = team_info.get("uuid", f"uuid-{team_id}")
    
    invite_url = f"https://workflowguide.vercel.app/invite/{raw_token}"
    
    email_subject = f"You're invited to join {team_name} on WorkflowGuide AI"
    email_body = f"""Hi {email},

You have been invited to collaborate on WorkflowGuide AI.

Click the secure button below to join your team.

------------------------------------------------

[ Join Team ] ({invite_url})

URL
{invite_url}

------------------------------------------------

Team Information

Team Name:
{team_name}

Team ID:
{team_uuid}

Invitation expires in:
7 Days

If you were not expecting this invitation, you may safely ignore this email.

Best regards,
System Owner

WorkflowGuide AI"""

    # Dispatch via SMTP
    send_email_via_smtp(email, email_subject, email_body)

    return {
        "raw_token": raw_token,
        "token_hash": token_hash,
        "invite_url": invite_url,
        "email_subject": email_subject,
        "email_body": email_body,
        "expires_at": expires_at.isoformat()
    }

def get_team_invitation_by_token(raw_token: str) -> Optional[dict]:
    token_hash = hash_token(raw_token)
    conn = get_db_connection()
    
    query = """
        SELECT id, team_id, token_hash, email, role, status, created_at, expires_at, receipt_id
        FROM team_invitations
        WHERE token_hash = ?
    """
    cursor = execute_query(conn, query, (token_hash,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    inv_data = dict(row)
    
    # Check expiry
    expires_at = datetime.fromisoformat(inv_data["expires_at"])
    now = datetime.utcnow()
    
    days_left = (expires_at - now).days
    
    # Log viewed receipt
    receipt = generate_receipt(
        agent="CollaborationAgent",
        scope=["comment"],
        input_data={"token_hash": token_hash}
    )
    log_audit_trail(
        agent="CollaborationAgent",
        action="INVITATION_VIEWED",
        allowed_scope=["comment"],
        status="SUCCESS",
        details=f"Viewed team invitation for {inv_data['email']}",
        receipt_id=receipt.receipt_id
    )
    save_tool_receipt("CollaborationAgent", "Planner Agent", "comment", ["comment"], "SUCCESS", "Viewed invite")
    
    if now > expires_at:
        # Mark as expired
        if inv_data["status"] == "Pending":
            update_invitation_status(token_hash, "Expired")
            inv_data["status"] = "Expired"
            
            # Log expired receipt
            expire_receipt = generate_receipt(
                agent="CollaborationAgent",
                scope=["comment"],
                input_data={"token_hash": token_hash}
            )
            log_audit_trail(
                agent="CollaborationAgent",
                action="INVITATION_EXPIRED",
                allowed_scope=["comment"],
                status="SUCCESS",
                details=f"Team invitation expired for {inv_data['email']}",
                receipt_id=expire_receipt.receipt_id
            )
            
        inv_data["days_left"] = -1
    else:
        inv_data["days_left"] = max(0, days_left)
        
    return inv_data

def update_invitation_status(token_hash: str, status: str):
    conn = get_db_connection()
    query = "UPDATE team_invitations SET status = ? WHERE token_hash = ?"
    execute_query(conn, query, (status, token_hash))
    conn.commit()
    conn.close()

def accept_team_invitation(raw_token: str, user_id: str) -> dict:
    token_hash = hash_token(raw_token)
    inv = get_team_invitation_by_token(raw_token)
    
    if not inv:
        return {"status": "error", "reason": "Invalid invitation token."}
        
    if inv["status"] == "Expired":
        return {"status": "error", "reason": "Expired"}
        
    if inv["status"] == "Accepted":
        return {"status": "error", "reason": "Already Used"}
        
    if inv["status"] in ("Declined", "Revoked"):
        return {"status": "error", "reason": "Revoked"}
        
    # Check actual dates again just in case
    expires_at = datetime.fromisoformat(inv["expires_at"])
    if datetime.utcnow() > expires_at:
        update_invitation_status(token_hash, "Expired")
        return {"status": "error", "reason": "Expired"}
        
    # Add user to team members
    from backend.services.collaboration_service import invite_member
    invite_member(inv["team_id"], user_id, inv["email"], inv["role"])
    
    # Mark accepted
    update_invitation_status(token_hash, "Accepted")
    
    # Generate accepted receipt
    receipt = generate_receipt(
        agent="CollaborationAgent",
        scope=["invite_member"],
        input_data={"token_hash": token_hash, "user_id": user_id}
    )
    log_audit_trail(
        agent="CollaborationAgent",
        action="INVITATION_ACCEPTED",
        allowed_scope=["invite_member"],
        status="SUCCESS",
        details=f"User {user_id} accepted invite to join team {inv['team_id']}",
        receipt_id=receipt.receipt_id
    )
    save_tool_receipt("CollaborationAgent", "Planner Agent", "invite_member", ["invite_member"], "SUCCESS", f"User {user_id} joined team")
    
    team_info = get_team_by_id(inv["team_id"])
    return {
        "status": "success",
        "team_uuid": team_info.get("uuid", f"uuid-{inv['team_id']}")
    }

def decline_team_invitation(raw_token: str) -> dict:
    token_hash = hash_token(raw_token)
    inv = get_team_invitation_by_token(raw_token)
    
    if not inv:
        return {"status": "error", "reason": "Invalid invitation token."}
        
    # Mark Declined
    update_invitation_status(token_hash, "Declined")
    
    # Generate declined receipt
    receipt = generate_receipt(
        agent="CollaborationAgent",
        scope=["comment"],
        input_data={"token_hash": token_hash}
    )
    log_audit_trail(
        agent="CollaborationAgent",
        action="INVITATION_DECLINED",
        allowed_scope=["comment"],
        status="SUCCESS",
        details=f"Team invitation declined for token",
        receipt_id=receipt.receipt_id
    )
    save_tool_receipt("CollaborationAgent", "Planner Agent", "comment", ["comment"], "SUCCESS", "Declined invite")
    
    return {"status": "success"}

def get_team_by_id(team_id: int) -> dict:
    conn = get_db_connection()
    query = "SELECT id, uuid, name, created_at FROM teams WHERE id = ?"
    cursor = execute_query(conn, query, (team_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {}
    return dict(row)

def get_team_by_uuid(uuid_str: str) -> dict:
    conn = get_db_connection()
    query = "SELECT id, uuid, name, created_at FROM teams WHERE uuid = ?"
    cursor = execute_query(conn, query, (uuid_str,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {}
    return dict(row)

def create_and_invite_team(team_name: str, email: str, role: str) -> dict:
    import random
    import time
    from backend.graph.graph_service import GraphService

    conn = get_db_connection()
    is_postgres = hasattr(conn, "cursor_factory")
    
    # 1. Generate unique 6-digit numeric Team ID
    team_id_numeric = None
    for _ in range(50):
        candidate = str(random.randint(100000, 999999))
        if is_postgres:
            cursor = execute_query(conn, "SELECT id FROM teams WHERE uuid = %s", (candidate,))
        else:
            cursor = execute_query(conn, "SELECT id FROM teams WHERE uuid = ?", (candidate,))
        if not cursor.fetchone():
            team_id_numeric = candidate
            break
            
    if not team_id_numeric:
        team_id_numeric = str(random.randint(100000, 999999))
        
    # 2. Insert team into SQL transactional database
    timestamp = datetime.utcnow().isoformat()
    if is_postgres:
        query_t = "INSERT INTO teams (uuid, name, created_at) VALUES (%s, %s, %s)"
    else:
        query_t = "INSERT INTO teams (uuid, name, created_at) VALUES (?, ?, ?)"
    cursor = execute_query(conn, query_t, (team_id_numeric, team_name, timestamp))
    team_id = cursor.lastrowid
    if team_id is None:
        try:
            if is_postgres:
                cursor.execute("SELECT currval(pg_get_serial_sequence('teams', 'id'))")
                team_id = cursor.fetchone()[0]
            else:
                team_id = 1
        except Exception:
            team_id = 1
    conn.commit()
    conn.close()
    
    # Log team creation activity
    from backend.services.collaboration_service import log_activity
    log_activity(team_id, "system", "CREATE_TEAM", f"Team '{team_name}' with ID {team_id_numeric} was created.")
    
    # 3. Create secure invitation token
    invite = create_team_invitation(team_id, email, role)
    
    # Override email body to show the 6-digit numeric Team ID
    invite_url = invite["invite_url"]
    invite["email_body"] = f"""Hi {email},

You have been invited to collaborate on WorkflowGuide AI.

Click the secure button below to join your team.

------------------------------------------------

[ Join Team ] ({invite_url})

URL
{invite_url}

------------------------------------------------

Team Information

Team Name:
{team_name}

Team ID:
{team_id_numeric}

Invitation expires in:
7 Days

If you were not expecting this invitation, you may safely ignore this email.

Best regards,
System Owner

WorkflowGuide AI"""

    # 4. Store team name, numeric team id, and invite link in Knowledge Graph
    try:
        service = GraphService()
        with service.driver.session() as session:
            session.run(
                "MERGE (t:Team {id: $team_id}) "
                "SET t.name = $team_name, t.invite_url = $invite_url, t.created_at = $ts",
                team_id=str(team_id_numeric),
                team_name=team_name,
                invite_url=invite_url,
                ts=str(time.time())
            )
            session.run(
                "MERGE (u:User {email: 'engineer@armourline.io'}) "
                "WITH u "
                "MATCH (t:Team {id: $team_id}) "
                "MERGE (u)-[:MEMBER_OF]->(t) "
                "MERGE (u)-[:OWNER_OF]->(t) "
                "MERGE (u)-[:ENGINEER_IN]->(t)",
                team_id=str(team_id_numeric)
            )
    except Exception as e:
        import logging
        logging.getLogger("GraphLoader").warning(f"Could not store team details in Knowledge Graph: {e}")
        
    # Dispatch via SMTP
    send_email_via_smtp(email, invite["email_subject"], invite["email_body"])

    return {
        "team_id": team_id,
        "team_id_numeric": team_id_numeric,
        "team_name": team_name,
        "invite_url": invite_url,
        "email_subject": invite["email_subject"],
        "email_body": invite["email_body"]
    }

def send_email_via_smtp(recipient_email: str, subject: str, body: str) -> bool:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM_EMAIL") or smtp_user
    
    if not smtp_host or not smtp_user or "your_email" in smtp_user:
        print(f"[SMTP Notice] SMTP host/user not configured. Skipping email dispatch to {recipient_email}")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_from
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_from, recipient_email, msg.as_string())
        server.quit()
        print(f"[SMTP Success] Secure invitation email dispatched to {recipient_email}")
        return True
    except Exception as e:
        print(f"[SMTP Error] Failed to dispatch invitation email to {recipient_email}: {e}")
        return False
