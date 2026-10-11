"""Optional shared-password gate for public deployments. Active only when DEMO_PASSWORD is set."""
import secrets
import time
from urllib.parse import quote

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.web.render import templates

router = APIRouter()
OPEN_PATHS = ("/login", "/static/", "/healthz")


class AuthGate(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if settings.demo_password and not request.session.get("authed") and not request.url.path.startswith(OPEN_PATHS):
            target = "/login" if request.method != "GET" else f"/login?next={quote(request.url.path)}"
            return RedirectResponse(target, status_code=303)
        return await call_next(request)


def _safe_next(value):
    return value if value.startswith("/") and not value.startswith("//") and "\\" not in value else "/"


@router.get("/healthz")
def healthz():
    return JSONResponse({"status": "ok"})


@router.get("/login")
def login_page(request: Request, next: str = "/"):
    if not settings.demo_password or request.session.get("authed"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"app_name": settings.app_name, "next": _safe_next(next), "error": None})


@router.post("/login")
def login(request: Request, password: str = Form(""), next: str = Form("/")):
    if settings.demo_password and secrets.compare_digest(password.encode(), settings.demo_password.encode()):
        request.session["authed"] = True
        return RedirectResponse(_safe_next(next), status_code=303)
    time.sleep(0.7)  # slows down password guessing
    return templates.TemplateResponse(request, "login.html", {"app_name": settings.app_name, "next": _safe_next(next), "error": "Incorrect password."}, status_code=401)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
