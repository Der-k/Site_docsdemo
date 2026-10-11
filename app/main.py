from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.web import (action_routes, assistant_routes, auth, incident_routes, induction_routes, inspection_routes,
                     routes, settings_routes, site_routes, workforce_routes)

app = FastAPI(title=settings.app_name)
# Middleware added last runs first: sessions must be loaded before the auth gate reads them.
app.add_middleware(auth.AuthGate)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, https_only=settings.https_only, same_site="lax", max_age=12 * 3600)
app.mount("/static", StaticFiles(directory=str(settings.base_dir / "app" / "static")), name="static")
for module in (auth, routes, workforce_routes, site_routes, induction_routes, inspection_routes,
               action_routes, incident_routes, assistant_routes, settings_routes):
    app.include_router(module.router)
