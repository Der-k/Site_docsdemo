from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.data import storage
from app.services import dashboard_service
from app.web.render import NAV, flash, render

router = APIRouter()
BUILT_ELSEWHERE = {"/workforce", "/sites", "/inductions", "/inspections", "/actions", "/incidents", "/assistant", "/settings"}  # modules with their own route files


@router.get("/")
def dashboard(request: Request):
    return render(request, "dashboard.html", "Dashboard", **dashboard_service.build_dashboard())


@router.post("/demo/reset")
def reset_demo(request: Request):
    storage.reset_data()
    flash(request, "Demo data reset to the original sample dataset.")
    return RedirectResponse("/", status_code=303)


def _placeholder(label):
    def page(request: Request):
        return render(request, "placeholder.html", label)
    return page


for label, href in NAV[1:]:
    if href not in BUILT_ELSEWHERE:
        router.add_api_route(href, _placeholder(label), methods=["GET"], name=label)
