from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.repositories.site_repository import SiteRepository
from app.services import workforce_service
from app.web.render import flash, not_found, render

router = APIRouter()


@router.get("/workforce")
def workforce(request: Request, q: str = "", site: str = "", status: str = ""):
    rows = workforce_service.list_workers(q, site, status)
    return render(request, "workforce.html", "Workforce", rows=rows, sites=SiteRepository().all(), f_site=site, f_status=status)


@router.post("/workforce")
def add_worker(request: Request, name: str = Form(""), job_title: str = Form(""), department: str = Form(""), site_id: str = Form("")):
    worker, error = workforce_service.add_worker(name, job_title, department, site_id)
    if error:
        flash(request, error, "error")
        return RedirectResponse("/workforce", status_code=303)
    flash(request, f"{worker['name']} added to the workforce.")
    return RedirectResponse(f"/workforce/{worker['id']}", status_code=303)


@router.get("/workforce/{worker_id}")
def worker_detail(request: Request, worker_id: str):
    worker = workforce_service.get_profile(worker_id)
    if not worker:
        return not_found(request, "That worker", "Back to workforce", "/workforce")
    return render(request, "worker_detail.html", worker["name"], crumbs=[("Workforce", "/workforce"), (worker["name"], None)], w=worker, sites=SiteRepository().all())


@router.post("/workforce/{worker_id}/assign")
def assign_site(request: Request, worker_id: str, site_id: str = Form("")):
    error = workforce_service.assign_site(worker_id, site_id)
    flash(request, error or "Site assignment updated.", "error" if error else "success")
    return RedirectResponse(f"/workforce/{worker_id}", status_code=303)
