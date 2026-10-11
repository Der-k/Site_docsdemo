"""Worker profiles and compliance, derived from certifications and induction records.

Non-compliant: an expired certificate, or the General Site Safety Induction not done.
Attention:     a certificate expiring within the window, or other required training outstanding.
"""
from app.core.config import settings
from app.data import storage
from app.repositories.induction_repository import InductionRecordRepository, InductionRepository
from app.repositories.site_repository import SiteRepository
from app.repositories.worker_repository import CertificationRepository, WorkerRepository
from app.services.dashboard_service import days_until

GENERAL_INDUCTION_ID = "I1"


def _context():
    return {"sites": {s["id"]: s for s in SiteRepository().all()}, "inductions": InductionRepository().all(),
            "certs": CertificationRepository().all(), "records": InductionRecordRepository().all()}


def _cert_state(days):
    return "expired" if days < 0 else "expiring" if days <= settings.expiry_window_days else "valid"


def _profile(worker, ctx):
    certs = [{**c, "days": days_until(c["expires"]), "state": _cert_state(days_until(c["expires"]))} for c in ctx["certs"] if c["worker_id"] == worker["id"]]
    done = {r["induction_id"]: r for r in ctx["records"] if r["worker_id"] == worker["id"]}
    required = [{**i, "record": done.get(i["id"])} for i in ctx["inductions"] if worker["site_id"] in i["required_sites"]]
    completed = sum(1 for i in required if i["record"])
    general_missing = any(i["id"] == GENERAL_INDUCTION_ID and not i["record"] for i in required)
    if general_missing or any(c["state"] == "expired" for c in certs):
        status = "non_compliant"
    elif completed < len(required) or any(c["state"] == "expiring" for c in certs):
        status = "attention"
    else:
        status = "compliant"
    return {**worker, "site_name": ctx["sites"].get(worker["site_id"], {}).get("name", "Unassigned"), "certs": certs, "required": required,
            "training_pct": round(100 * completed / len(required)) if required else 100, "status": status}


def list_workers(q="", site_id="", status=""):
    ctx = _context()
    rows = [_profile(w, ctx) for w in WorkerRepository().all()]
    q = q.strip().lower()
    if q:
        rows = [r for r in rows if q in " ".join([r["name"], r["job_title"], r["department"], r["site_name"]]).lower()]
    if site_id:
        rows = [r for r in rows if r["site_id"] == site_id]
    if status:
        rows = [r for r in rows if r["status"] == status]
    return rows


def get_profile(worker_id):
    worker = WorkerRepository().get(worker_id)
    return _profile(worker, _context()) if worker else None


def add_worker(name, job_title, department, site_id):
    name = name.strip()
    if not name:
        return None, "Enter the worker's name."
    if not SiteRepository().get(site_id):
        return None, "Choose a site for the new worker."
    worker = WorkerRepository().add({"name": name, "job_title": job_title.strip() or "Site Worker", "department": department.strip() or "General", "site_id": site_id})
    storage.log_activity("worker", f"{name} added to {SiteRepository().get(site_id)['name']}")
    return worker, None


def assign_site(worker_id, site_id):
    worker, site = WorkerRepository().get(worker_id), SiteRepository().get(site_id)
    if not worker or not site:
        return "That worker or site no longer exists."
    WorkerRepository().update(worker_id, site_id=site_id)
    storage.log_activity("worker", f"{worker['name']} assigned to {site['name']}")
    return None
