"""Site overviews built from worker compliance."""
from app.repositories.induction_repository import InductionRepository
from app.repositories.site_repository import SiteRepository
from app.services.workforce_service import list_workers


def _level(pct):
    return ("Compliant", "green") if pct >= 80 else ("Attention", "amber") if pct >= 50 else ("At risk", "red")


def _summary(site, profiles, inductions):
    workers = [p for p in profiles if p["site_id"] == site["id"]]
    counts = {k: sum(w["status"] == k for w in workers) for k in ("compliant", "attention", "non_compliant")}
    pct = round(100 * counts["compliant"] / len(workers)) if workers else 100
    required = []
    for i in inductions:
        if site["id"] in i["required_sites"]:
            done = sum(1 for w in workers for r in w["required"] if r["id"] == i["id"] and r["record"])
            required.append({**i, "done": done, "total": len(workers)})
    label, tone = _level(pct)
    return {**site, "workers": workers, "worker_count": len(workers), "counts": counts, "pct": pct, "label": label, "tone": tone, "required": required}


def list_sites():
    profiles, inductions = list_workers(), InductionRepository().all()
    return [_summary(s, profiles, inductions) for s in SiteRepository().all()]


def get_site(site_id):
    return next((s for s in list_sites() if s["id"] == site_id), None)
