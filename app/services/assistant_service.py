"""Chat state, provider selection, and the confirm-then-apply step for assistant actions."""
from datetime import datetime

from app.core.config import settings
from app.data import storage
from app.repositories.base import Repository
from app.services import action_service, incident_service, workforce_service
from app.services.assistant_groq import GroqError, GroqProvider
import re

from app.services.assistant_provider import HELP_TEXT, DemoProvider, _reply


class ChatRepository(Repository):
    collection, prefix = "assistant_chat", "M"


def provider_name():
    return "groq" if settings.assistant_provider == "groq" and settings.groq_api_key else "demo"


def get_provider():
    return GroqProvider() if provider_name() == "groq" else DemoProvider()


def history(limit=40):
    return ChatRepository().all()[-limit:]


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _is_help(message):
    return bool(re.fullmatch(r"\s*(help|commands|\?|what can (you|i) do)\s*[.!?]*\s*", message, re.I))


def ask(message):
    message = message.strip()[:500]
    if not message:
        return []
    repo = ChatRepository()
    prior = [{"role": m["role"], "content": m["text"]} for m in history(6)]
    user_msg = repo.add({"role": "user", "text": message, "at": _now()})
    try:
        reply = _reply(HELP_TEXT, label="Help") if _is_help(message) else get_provider().respond(message, prior)
    except GroqError as exc:
        reply = DemoProvider().respond(message)
        reply["text"] = f"Groq was unavailable ({exc}), so this is a demo-mode answer.\n\n{reply['text']}"
    bot_msg = repo.add({"role": "assistant", "text": reply["text"], "label": reply.get("label"), "sources": reply["sources"], "links": reply["links"], "pending": reply["pending"],
              "pending_status": "pending" if reply["pending"] else None, "result": None, "at": _now()})
    return [user_msg, bot_msg]


def get_message(message_id):
    return ChatRepository().get(message_id)


def public(m):
    """The fields the chat bubble needs. Never includes pending parameters."""
    pending = m.get("pending") or {}
    return {"id": m["id"], "role": m["role"], "text": m["text"], "label": m.get("label"), "sources": m.get("sources", []), "links": m.get("links", []),
            "pending_summary": pending.get("summary") if m.get("pending_status") == "pending" else None, "pending_status": m.get("pending_status"),
            "result": m.get("result"), "result_href": m.get("result_href")}


def clear():
    storage.clear_collection("assistant_chat")


def _execute(p):
    t, a, user = p["type"], p["params"], settings.demo_user["name"]
    if t == "action_status":
        return action_service.set_status(a["action_id"], a["status"]), f"/actions/{a['action_id']}"
    if t == "incident_status":
        return incident_service.update_status(a["incident_id"], a["status"]), f"/incidents/{a['incident_id']}"
    if t == "incident_note":
        return incident_service.add_note(a["incident_id"], a["text"], f"{user} via AI Assistant"), f"/incidents/{a['incident_id']}"
    if t == "assign_site":
        return workforce_service.assign_site(a["worker_id"], a["site_id"]), f"/workforce/{a['worker_id']}"
    if t == "add_worker":
        w, err = workforce_service.add_worker(a["name"], a["job_title"], "General", a["site_id"])
        return err, f"/workforce/{w['id']}" if w else None
    if t == "report_incident":
        inc, err = incident_service.report_incident(a["title"], a["type"], a["severity"], a["site_id"], user, datetime.now().date().isoformat(), a["description"])
        return err, f"/incidents/{inc['id']}" if inc else None
    return "Unknown action.", None


def resolve(message_id, confirm):
    repo, m = ChatRepository(), ChatRepository().get(message_id)
    if not m or m.get("pending_status") != "pending":
        return "That request is no longer waiting for confirmation."
    if not confirm:
        repo.update(message_id, pending_status="cancelled", result="Cancelled. Nothing was changed.")
        return None
    error, href = _execute(m["pending"])
    if error:
        repo.update(message_id, pending_status="failed", result=f"Could not apply: {error}")
        return None
    storage.log_activity("assistant", f"Applied via AI Assistant: {m['pending']['summary']}")
    repo.update(message_id, pending_status="confirmed", result=f"Done: {m['pending']['summary']}.", result_href=href)
    return None
