"""Shared page rendering and flash messages for all route modules."""
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.services import dashboard_service
from app.services.assistant_teasers import teasers_for

templates = Jinja2Templates(directory=str(settings.base_dir / "app" / "templates"))

NAV = [
    ("Dashboard", "/"), ("Workforce", "/workforce"), ("Sites", "/sites"), ("Inductions & Training", "/inductions"),
    ("Inspections", "/inspections"), ("Incidents", "/incidents"), ("Corrective Actions", "/actions"),
    ("AI Assistant", "/assistant"), ("Settings", "/settings"),
]


def flash(request, message, tone="success"):
    request.session["flash"] = {"message": message, "tone": tone}


def render(request, template, title, crumbs=None, status_code=200, **context):
    base = {
        "title": title, "nav": NAV, "path": request.url.path, "user": settings.demo_user, "app_name": settings.app_name,
        "flash": request.session.pop("flash", None), "crumbs": crumbs or [(title, None)],
        "alerts": dashboard_service.alert_count(), "gate_on": bool(settings.demo_password), "teasers": teasers_for(request.url.path), "q": request.query_params.get("q", ""),
    }
    return templates.TemplateResponse(request, template, {**base, **context}, status_code=status_code)


def not_found(request, what, back_label, back_href):
    return render(request, "not_found.html", "Not found", status_code=404, what=what, back_label=back_label, back_href=back_href)
