from fastapi import APIRouter, Request

from app.services import site_service
from app.web.render import not_found, render

router = APIRouter()


@router.get("/sites")
def sites(request: Request):
    return render(request, "sites.html", "Sites", sites=site_service.list_sites())


@router.get("/sites/{site_id}")
def site_detail(request: Request, site_id: str):
    site = site_service.get_site(site_id)
    if not site:
        return not_found(request, "That site", "Back to sites", "/sites")
    return render(request, "site_detail.html", site["name"], crumbs=[("Sites", "/sites"), (site["name"], None)], s=site)
