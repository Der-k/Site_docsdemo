"""Corrective actions: filtering, status changes, source lookups."""
from datetime import date

from app.data import storage
from app.repositories.action_repository import ActionRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.inspection_repository import InspectionRepository
from app.services.dashboard_service import days_until

STATUSES = {"open": "Open", "in_progress": "In progress", "completed": "Completed"}
VIEWS = ("all", "open", "overdue", "completed")


def _decorate(a):
    overdue = a["status"] != "completed" and days_until(a["due"]) < 0
    is_insp = a["source_type"] == "inspection"
    return {**a, "overdue": overdue, "days": days_until(a["due"]), "source_href": f"/inspections/{a['source_id']}" if is_insp else f"/incidents/{a['source_id']}"}


def _matches(a, view):
    return {"all": True, "open": a["status"] != "completed", "overdue": a["overdue"], "completed": a["status"] == "completed"}[view]


def list_actions(view="all"):
    rows = [_decorate(a) for a in ActionRepository().all()]
    rows = [a for a in rows if _matches(a, view if view in VIEWS else "all")]
    return sorted(rows, key=lambda a: (a["status"] == "completed", a["due"]))


def view_counts():
    rows = [_decorate(a) for a in ActionRepository().all()]
    return {v: sum(1 for a in rows if _matches(a, v)) for v in VIEWS}


def get_action(action_id):
    a = ActionRepository().get(action_id)
    if not a:
        return None
    a = _decorate(a)
    source = (InspectionRepository() if a["source_type"] == "inspection" else IncidentRepository()).get(a["source_id"])
    return {**a, "source_title": source["title"] if source else "Source record not found"}


def set_status(action_id, status):
    action = ActionRepository().get(action_id)
    if not action or status not in STATUSES:
        return "That action or status is not valid."
    ActionRepository().update(action_id, status=status, completed_on=date.today().isoformat() if status == "completed" else None)
    verb = "completed" if status == "completed" else f"set to {STATUSES[status].lower()}"
    storage.log_activity("action", f"Action {action_id} {verb}")
    return None
