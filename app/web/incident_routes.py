from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.repositories.site_repository import SiteRepository
from app.services import incident_service as svc
from app.web.render import flash, not_found, render

router = APIRouter()
BACK = ("Back to incidents", "/incidents")


@router.get("/incidents")
def incidents(request: Request, status: str = "", site: str = ""):
    return render(request, "incidents.html", "Incidents", rows=svc.list_incidents(status, site), sites=SiteRepository().all(), f_status=status, f_site=site, statuses=svc.STATUSES)


@router.get("/incidents/new")
def new_incident(request: Request):
    crumbs = [("Incidents", "/incidents"), ("Report incident", None)]
    return render(request, "incident_new.html", "Report an incident", crumbs=crumbs, sites=SiteRepository().all(), types=svc.TYPES, severities=svc.SEVERITIES, today=date.today().isoformat())


@router.post("/incidents")
def create_incident(request: Request, title: str = Form(""), type: str = Form(""), severity: str = Form(""), site_id: str = Form(""),
                    reporter: str = Form(""), incident_date: str = Form(""), description: str = Form("")):
    inc, error = svc.report_incident(title, type, severity, site_id, reporter, incident_date, description)
    if error:
        flash(request, error, "error")
        return RedirectResponse("/incidents/new", status_code=303)
    flash(request, f"Incident {inc['id']} reported.")
    return RedirectResponse(f"/incidents/{inc['id']}", status_code=303)


@router.get("/incidents/{incident_id}")
def incident_detail(request: Request, incident_id: str):
    inc = svc.get_incident(incident_id)
    if not inc:
        return not_found(request, "That incident", *BACK)
    return render(request, "incident_detail.html", inc["title"], crumbs=[("Incidents", "/incidents"), (inc["id"], None)], i=inc, statuses=svc.STATUSES)


@router.post("/incidents/{incident_id}/status")
def change_status(request: Request, incident_id: str, status: str = Form("")):
    error = svc.update_status(incident_id, status)
    flash(request, error or f"Investigation status updated to {svc.STATUSES[status].lower()}.", "error" if error else "success")
    return RedirectResponse(f"/incidents/{incident_id}", status_code=303)


@router.post("/incidents/{incident_id}/notes")
def add_note(request: Request, incident_id: str, text: str = Form("")):
    error = svc.add_note(incident_id, text, settings.demo_user["name"])
    flash(request, error or "Investigation note added.", "error" if error else "success")
    return RedirectResponse(f"/incidents/{incident_id}", status_code=303)
