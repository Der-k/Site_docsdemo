from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.services import action_service
from app.web.render import flash, not_found, render

router = APIRouter()


@router.get("/actions")
def actions(request: Request, view: str = "all"):
    view = view if view in action_service.VIEWS else "all"
    return render(request, "actions.html", "Corrective Actions", actions=action_service.list_actions(view), counts=action_service.view_counts(), view=view)


@router.get("/actions/{action_id}")
def action_detail(request: Request, action_id: str):
    a = action_service.get_action(action_id)
    if not a:
        return not_found(request, "That action", "Back to actions", "/actions")
    return render(request, "action_detail.html", a["id"], crumbs=[("Corrective Actions", "/actions"), (a["id"], None)], a=a)


@router.post("/actions/{action_id}/status")
def update_status(request: Request, action_id: str, status: str = Form("")):
    error = action_service.set_status(action_id, status)
    flash(request, error or f"Action {action_id} updated.", "error" if error else "success")
    return RedirectResponse(f"/actions/{action_id}", status_code=303)
