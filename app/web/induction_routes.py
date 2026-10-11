from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.repositories.worker_repository import WorkerRepository
from app.services import induction_service
from app.web.render import flash, not_found, render

router = APIRouter()
BACK = ("Back to inductions", "/inductions")


@router.get("/inductions")
def inductions(request: Request):
    return render(request, "inductions.html", "Inductions & Training", inductions=induction_service.list_inductions(), recent=induction_service.recent_completions())


@router.get("/inductions/{induction_id}")
def induction_detail(request: Request, induction_id: str, worker: str = ""):
    ind = induction_service.get_induction(induction_id)
    if not ind:
        return not_found(request, "That induction", *BACK)
    crumbs = [("Inductions & Training", "/inductions"), (ind["title"], None)]
    return render(request, "induction_detail.html", ind["title"], crumbs=crumbs, ind=ind, workers=WorkerRepository().all(), selected=worker)


@router.get("/inductions/{induction_id}/take")
def take(request: Request, induction_id: str, worker: str = ""):
    ind, w = induction_service.get_induction(induction_id), WorkerRepository().get(worker)
    if not ind:
        return not_found(request, "That induction", *BACK)
    if not w:
        flash(request, "Choose who is taking the induction.", "error")
        return RedirectResponse(f"/inductions/{induction_id}", status_code=303)
    crumbs = [("Inductions & Training", "/inductions"), (ind["title"], f"/inductions/{induction_id}"), ("Take induction", None)]
    return render(request, "induction_take.html", ind["title"], crumbs=crumbs, ind=ind, w=w)


@router.post("/inductions/{induction_id}/submit")
async def submit(request: Request, induction_id: str, worker_id: str = Form("")):
    form = await request.form()
    answers = {int(k[1:]): int(v) for k, v in form.items() if k.startswith("q") and k[1:].isdigit() and str(v).isdigit()}
    result, error = induction_service.submit(induction_id, worker_id, answers)
    if error:
        flash(request, error, "error")
        return RedirectResponse(f"/inductions/{induction_id}/take?worker={worker_id}", status_code=303)
    if result["passed"]:
        flash(request, f"Induction passed with {result['pct']}% ({result['correct']} of {result['total']}). Completion record created.")
        return RedirectResponse(f"/inductions/{induction_id}/certificate/{worker_id}", status_code=303)
    flash(request, f"Score {result['pct']}% ({result['correct']} of {result['total']}) is below the pass mark. Review the sections and try again.", "error")
    return RedirectResponse(f"/inductions/{induction_id}/take?worker={worker_id}", status_code=303)


@router.get("/inductions/{induction_id}/certificate/{worker_id}")
def certificate(request: Request, induction_id: str, worker_id: str):
    data = induction_service.certificate(induction_id, worker_id)
    if not data:
        return not_found(request, "That completion record", *BACK)
    crumbs = [("Inductions & Training", "/inductions"), ("Completion record", None)]
    return render(request, "certificate.html", "Completion record", crumbs=crumbs, **data)
