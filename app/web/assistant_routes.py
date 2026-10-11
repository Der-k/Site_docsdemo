from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.config import settings
from app.services import assistant_service as svc
from app.services.assistant_provider import COMMANDS, EXAMPLES
from app.web.render import flash, render

router = APIRouter()
HOME = "/assistant#end"


# ---- full page (server-rendered) ----
@router.get("/assistant")
def assistant(request: Request):
    return render(request, "ai_assistant.html", "AI Assistant", messages=svc.history(), examples=EXAMPLES, commands=COMMANDS, ai_mode=svc.provider_name(), model=settings.groq_model)


@router.post("/assistant/ask")
def ask(request: Request, message: str = Form("")):
    if message.strip():
        svc.ask(message)
    else:
        flash(request, "Type a question or command first.", "error")
    return RedirectResponse(HOME, status_code=303)


@router.post("/assistant/{message_id}/confirm")
def confirm(request: Request, message_id: str):
    error = svc.resolve(message_id, True)
    if error:
        flash(request, error, "error")
    return RedirectResponse(HOME, status_code=303)


@router.post("/assistant/{message_id}/cancel")
def cancel(request: Request, message_id: str):
    error = svc.resolve(message_id, False)
    if error:
        flash(request, error, "error")
    return RedirectResponse(HOME, status_code=303)


@router.post("/assistant-clear")
def clear(request: Request):
    svc.clear()
    flash(request, "Conversation cleared.")
    return RedirectResponse("/assistant", status_code=303)


# ---- JSON API used by the chat bubble ----
def _json_only(request):
    """Browsers can't send application/json from a cross-site form, so requiring it blocks cross-site posts."""
    return request.headers.get("content-type", "").split(";")[0].strip() == "application/json"


def _bad(status, message):
    return JSONResponse({"error": message}, status_code=status)


@router.get("/assistant/api/history")
def api_history():
    return {"messages": [svc.public(m) for m in svc.history(20)], "ai_mode": svc.provider_name(), "model": settings.groq_model, "examples": EXAMPLES, "commands": COMMANDS}


@router.post("/assistant/api/ask")
async def api_ask(request: Request):
    if not _json_only(request):
        return _bad(415, "Send JSON.")
    try:
        body = await request.json()
    except ValueError:
        return _bad(400, "That request could not be read.")
    message = str(body.get("message", "")).strip() if isinstance(body, dict) else ""
    if not message:
        return _bad(400, "Type a question or command first.")
    return {"messages": [svc.public(m) for m in svc.ask(message)]}


@router.post("/assistant/api/clear")
async def api_clear(request: Request):
    if not _json_only(request):
        return _bad(415, "Send JSON.")
    svc.clear()
    return {"ok": True}


@router.post("/assistant/api/{message_id}/{decision}")
async def api_resolve(request: Request, message_id: str, decision: str):
    if decision not in ("confirm", "cancel"):
        return _bad(404, "Unknown action.")
    if not _json_only(request):
        return _bad(415, "Send JSON.")
    error = svc.resolve(message_id, decision == "confirm")
    message = svc.get_message(message_id)
    return {"error": error, "message": svc.public(message) if message else None}
