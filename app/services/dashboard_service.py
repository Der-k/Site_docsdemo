"""Dashboard figures, always computed from the stored records."""
from datetime import date, datetime

from app.core.config import settings
from app.data import storage
from app.repositories.action_repository import ActionRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.induction_repository import InductionRecordRepository, InductionRepository
from app.repositories.site_repository import SiteRepository
from app.repositories.worker_repository import CertificationRepository, WorkerRepository


def days_until(iso):
    return (date.fromisoformat(iso) - date.today()).days


def _ago(iso):
    delta = datetime.now() - datetime.fromisoformat(iso)
    if delta.days >= 1:
        return f"{delta.days}d ago"
    hours = delta.seconds // 3600
    return f"{hours}h ago" if hours else "just now"


def training_rate(workers, inductions, records):
    done = {(r["worker_id"], r["induction_id"]) for r in records}
    needed = [(w["id"], i["id"]) for w in workers for i in inductions if w["site_id"] in i["required_sites"]]
    return round(100 * sum(p in done for p in needed) / len(needed)) if needed else 100


def incident_trend(incidents, months=6):
    today = date.today()
    keys = []
    for k in range(months - 1, -1, -1):
        y, m = today.year, today.month - k
        while m <= 0:
            m, y = m + 12, y - 1
        keys.append((y, m))
    counts = {k: 0 for k in keys}
    for inc in incidents:
        d = date.fromisoformat(inc["date"])
        if (d.year, d.month) in counts:
            counts[(d.year, d.month)] += 1
    peak = max(max(counts.values()), 1)
    return [{"label": date(y, m, 1).strftime("%b"), "count": counts[(y, m)], "pct": round(100 * counts[(y, m)] / peak)} for y, m in keys]


def is_overdue(action):
    return action["status"] != "completed" and days_until(action["due"]) < 0


def alert_count():
    expired = sum(days_until(c["expires"]) < 0 for c in CertificationRepository().all())
    return expired + sum(is_overdue(a) for a in ActionRepository().all())


def build_dashboard():
    workers, sites = WorkerRepository().all(), SiteRepository().all()
    certs, actions = CertificationRepository().all(), ActionRepository().all()
    incidents = IncidentRepository().all()
    names = {w["id"]: w["name"] for w in workers}
    due = sorted((c for c in certs if days_until(c["expires"]) <= settings.expiry_window_days), key=lambda c: c["expires"])
    open_inc = [i for i in incidents if i["status"] != "closed"]
    outstanding = [a for a in actions if a["status"] != "completed"]
    return {
        "stats": {
            "workers": len(workers),
            "sites": sum(s["status"] == "active" for s in sites),
            "training": training_rate(workers, InductionRepository().all(), InductionRecordRepository().all()),
            "expiring": len(due), "expired": sum(days_until(c["expires"]) < 0 for c in due),
            "open_incidents": len(open_inc),
            "outstanding": len(outstanding), "overdue": sum(is_overdue(a) for a in outstanding),
        },
        "expiries": [{**c, "worker": names.get(c["worker_id"], "Unknown"), "days": days_until(c["expires"])} for c in due[:6]],
        "incidents": sorted(incidents, key=lambda i: i["date"], reverse=True)[:4],
        "trend": incident_trend(incidents),
        "activity": [{**a, "ago": _ago(a["at"])} for a in storage.list_records("activity")[:6]],
        "site_names": {s["id"]: s["name"] for s in sites},
    }
