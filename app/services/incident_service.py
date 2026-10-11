"""Incidents: listing, reporting, investigation status and notes."""
from datetime import date

from app.data import storage
from app.repositories.action_repository import ActionRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.site_repository import SiteRepository
from app.services.dashboard_service import days_until

TYPES = ["Near miss", "Injury", "Property damage", "Environmental", "Other"]
SEVERITIES = ["Low", "Medium", "High"]
STATUSES = {"open": "Open", "investigating": "Investigating", "closed": "Closed"}


def list_incidents(status="", site_id=""):
    sites = {s["id"]: s["name"] for s in SiteRepository().all()}
    rows = [{**i, "site_name": sites.get(i["site_id"], "Unknown")} for i in IncidentRepository().all()]
    rows = [i for i in rows if (not status or i["status"] == status) and (not site_id or i["site_id"] == site_id)]
    return sorted(rows, key=lambda i: (i["date"], i["id"]), reverse=True)


def get_incident(incident_id):
    inc = IncidentRepository().get(incident_id)
    if not inc:
        return None
    site = SiteRepository().get(inc["site_id"]) or {}
    related = [{**a, "overdue": a["status"] != "completed" and days_until(a["due"]) < 0}
               for a in ActionRepository().all() if a["source_type"] == "incident" and a["source_id"] == incident_id]
    return {**inc, "site_name": site.get("name", "Unknown"), "actions": related}


def report_incident(title, inc_type, severity, site_id, reporter, incident_date, description):
    title = title.strip()
    if not title or not description.strip():
        return None, "Enter a title and a description."
    if inc_type not in TYPES or severity not in SEVERITIES or not SiteRepository().get(site_id):
        return None, "Choose a valid type, severity and site."
    try:
        when = date.fromisoformat(incident_date)
    except ValueError:
        return None, "Enter a valid incident date."
    if when > date.today():
        return None, "The incident date cannot be in the future."
    inc = IncidentRepository().add({"title": title, "type": inc_type, "severity": severity, "site_id": site_id, "reporter": reporter.strip() or "Demo user",
                                    "date": when.isoformat(), "status": "open", "description": description.strip(), "notes": []})
    storage.log_activity("incident", f"Incident {inc['id']} reported: {title}")
    return inc, None


def update_status(incident_id, status):
    if not IncidentRepository().get(incident_id) or status not in STATUSES:
        return "That incident or status is not valid."
    IncidentRepository().update(incident_id, status=status)
    storage.log_activity("incident", f"Incident {incident_id} moved to {status}")
    return None


def add_note(incident_id, text, author):
    inc = IncidentRepository().get(incident_id)
    if not inc:
        return "That incident no longer exists."
    if not text.strip():
        return "Enter an investigation note."
    note = {"at": date.today().isoformat(), "author": author, "text": text.strip()}
    IncidentRepository().update(incident_id, notes=[*inc["notes"], note])
    storage.log_activity("incident", f"Investigation note added to {incident_id}")
    return None
