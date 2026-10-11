from fastapi import APIRouter, Request

from app.core.config import settings
from app.services.assistant_service import provider_name
from app.web.render import render

router = APIRouter()


@router.get("/settings")
def settings_page(request: Request):
    return render(request, "settings.html", "Settings", data_file=str(settings.data_file), provider=provider_name(), model=settings.groq_model, key_set=bool(settings.groq_api_key), gate_on=bool(settings.demo_password))
