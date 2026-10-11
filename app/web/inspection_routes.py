from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.repositories.site_repository import SiteRepository
from app.services import inspection_service
from app.web.render import flash, not_found, render

router = APIRouter()
BACK = ("Back to inspections", "/inspections")


@router.get("/inspections")
def inspections(request: Request):
    return render(request, "inspections.html", "Inspections", templates=inspection_service.list_templates(), inspections=inspection_service.list_inspections())


@router.get("/inspections/new")
def new_inspection(request: Request, template: str = "", site: str = ""):
    t = inspection_service.get_template(template)
    if not t:
        return not_found(request, "That inspection template", *BACK)
    return render(request, "inspection_new.html", t["title"], crumbs=[("Inspections", "/inspections"), ("New inspection", None)], t=t, sites=SiteRepository().all(), site=site)


@router.post("/inspections")
async def submit_inspection(request: Request):
    form = await request.form()
    template_id = str(form.get("template_id", ""))
    answers = {k[2:]: {"result": str(v), "note": str(form.get("n_" + k[2:], ""))} for k, v in form.items() if k.startswith("r_")}
    insp, error = inspection_service.submit_inspection(template_id, str(form.get("site_id", "")), str(form.get("inspector", "")), answers, str(form.get("observations", "")))
    if error:
        flash(request, error, "error")
        return RedirectResponse(f"/inspections/new?template={template_id}", status_code=303)
    n = len(insp["findings"])
    flash(request, f"Inspection {insp['id']} submitted. {n} finding(s) and {n} corrective action(s) created." if n else f"Inspection {insp['id']} submitted. No findings.")
    return RedirectResponse(f"/inspections/{insp['id']}", status_code=303)


@router.get("/inspections/{inspection_id}")
def inspection_detail(request: Request, inspection_id: str):
    i = inspection_service.get_inspection(inspection_id)
    if not i:
        return not_found(request, "That inspection", *BACK)
    return render(request, "inspection_detail.html", i["title"], crumbs=[("Inspections", "/inspections"), (i["id"], None)], i=i)
