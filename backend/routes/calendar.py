from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from backend.auth import get_current_user
from backend.services.calendar_service import (
    generate_calendar_events,
    export_google_calendar,
    export_outlook_calendar,
    generate_ics_file,
    update_existing_calendar
)
from backend.database import get_db_connection, execute_query

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])

class CalendarExportSchema(BaseModel):
    project_id: int
    calendar_type: str
    reminders: List[str]
    timezone: str
    update_existing: Optional[bool] = False

@router.post("/export")
async def export_timeline(payload: CalendarExportSchema, user_id: str = Depends(get_current_user)):
    try:
        events = generate_calendar_events(payload.project_id, payload.reminders, payload.timezone)
        
        if payload.update_existing:
            return update_existing_calendar(payload.project_id, payload.calendar_type)

        if payload.calendar_type == "Google":
            return export_google_calendar(payload.project_id, events)
        elif payload.calendar_type == "Outlook":
            return export_outlook_calendar(payload.project_id, events)
        elif payload.calendar_type == "Apple":
            # Apple Calendar supports one-click .ics download/subscription integration
            return {
                "status": "success",
                "message": "Successfully prepared Apple Calendar (.ics) export payload.",
                "download_url": f"/api/calendar/download-ics/{payload.project_id}"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported calendar type: {payload.calendar_type}")
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-ics/{project_id}")
async def download_ics(project_id: int):
    try:
        # Load project name
        conn = get_db_connection()
        cursor = execute_query(conn, "SELECT name FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        
        project_name = row["name"] if row else f"project_{project_id}"
        
        # Default reminders
        reminders = ["1 Day Before", "1 Hour Before", "15 Minutes Before"]
        events = generate_calendar_events(project_id, reminders, "UTC")
        ics_content = generate_ics_file(project_id, events)
        
        safe_filename = project_name.replace(" ", "_").replace("/", "_")
        
        return Response(
            content=ics_content,
            media_type="text/calendar",
            headers={
                "Content-Disposition": f"attachment; filename={safe_filename}.ics"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateLinksSchema(BaseModel):
    project_id: Optional[Any] = "default"
    project_name: Optional[str] = "Engineering Project"
    task_ids: Optional[List[str]] = None
    tasks: Optional[List[Dict[str, Any]]] = None
    timezone: Optional[str] = "UTC"

@router.post("/generate-links")
async def generate_links(payload: GenerateLinksSchema):
    try:
        from backend.services.google_calendar_export import generate_multiple_event_links
        return generate_multiple_event_links(
            project_id=payload.project_id,
            task_ids=payload.task_ids or [],
            timezone=payload.timezone or "UTC",
            tasks=payload.tasks,
            project_name=payload.project_name
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
