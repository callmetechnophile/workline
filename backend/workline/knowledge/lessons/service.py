"""Engineering Lesson management service."""

from datetime import datetime, timezone
import logging
import threading
from typing import Dict, List, Optional

from backend.workline.knowledge.models import (
    Actor,
    EngineeringLesson,
    KnowledgeAuditEvent,
    KnowledgeAuditEventType,
)

logger = logging.getLogger("workline.knowledge.lessons")


class LessonService:
    """Manages engineering lessons learned, context, causes, impacts, and recommendations."""

    def __init__(self):
        self._lock = threading.RLock()
        self._lessons: Dict[str, EngineeringLesson] = {}  # lesson_id -> EngineeringLesson
        self._audit_logs: List[KnowledgeAuditEvent] = []

    def create_lesson(
        self,
        lesson: EngineeringLesson,
        actor: Optional[Actor] = None,
    ) -> EngineeringLesson:
        """Records an engineering lesson learned."""
        with self._lock:
            now_iso = datetime.now(timezone.utc).isoformat()
            lesson.created_at = now_iso
            if actor:
                lesson.created_by = actor

            self._lessons[lesson.lesson_id] = lesson

            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{lesson.lesson_id}_created",
                    event_type=KnowledgeAuditEventType.LESSON_CREATED,
                    project_id=lesson.project_id,
                    object_id=lesson.lesson_id,
                    actor=lesson.created_by,
                    details={"title": lesson.title},
                )
            )
            return lesson

    def get_lesson(self, lesson_id: str) -> Optional[EngineeringLesson]:
        """Retrieves single lesson."""
        with self._lock:
            return self._lessons.get(lesson_id)

    def list_lessons(self, project_id: str) -> List[EngineeringLesson]:
        """Lists all lessons learned for a project."""
        with self._lock:
            res = [l for l in self._lessons.values() if l.project_id == project_id]
            return sorted(res, key=lambda l: l.created_at)


lesson_service = LessonService()
