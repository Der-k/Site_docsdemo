"""Inductions: listing, quiz grading, completion records."""
from datetime import date

from app.data import storage
from app.repositories.induction_repository import InductionRecordRepository, InductionRepository
from app.repositories.site_repository import SiteRepository
from app.repositories.worker_repository import WorkerRepository
from app.services.workforce_service import list_workers


def _roster(induction, profiles):
    rows = []
    for p in profiles:
        entry = next((r for r in p["required"] if r["id"] == induction["id"]), None)
        if entry:
            rows.append({"worker": p, "record": entry["record"]})
    return rows


def _decorate(induction, profiles, sites):
    roster = _roster(induction, profiles)
    names = [sites[s]["name"] for s in induction["required_sites"] if s in sites]
    return {**induction, "roster": roster, "total": len(roster), "done": sum(1 for r in roster if r["record"]), "site_names": names}


def list_inductions():
    profiles, sites = list_workers(), {s["id"]: s for s in SiteRepository().all()}
    return [_decorate(i, profiles, sites) for i in InductionRepository().all()]


def get_induction(induction_id):
    return next((i for i in list_inductions() if i["id"] == induction_id), None)


def recent_completions(limit=8):
    workers = {w["id"]: w["name"] for w in WorkerRepository().all()}
    titles = {i["id"]: i["title"] for i in InductionRepository().all()}
    records = sorted(InductionRecordRepository().all(), key=lambda r: (r["completed_on"], r["id"]), reverse=True)[:limit]
    return [{**r, "worker": workers.get(r["worker_id"], "Unknown"), "title": titles.get(r["induction_id"], "Unknown")} for r in records]


def grade(induction, answers):
    total = len(induction["quiz"])
    correct = sum(1 for i, q in enumerate(induction["quiz"]) if answers.get(i) == q["answer"])
    pct = round(100 * correct / total) if total else 0
    return {"correct": correct, "total": total, "pct": pct, "passed": pct >= induction["pass_mark"]}


def submit(induction_id, worker_id, answers):
    induction, worker = InductionRepository().get(induction_id), WorkerRepository().get(worker_id)
    if not induction or not worker:
        return None, "That induction or worker no longer exists."
    if len(answers) < len(induction["quiz"]):
        return None, "Answer every question before submitting."
    result = grade(induction, answers)
    if result["passed"]:
        repo = InductionRecordRepository()
        existing = next((r for r in repo.all() if r["worker_id"] == worker_id and r["induction_id"] == induction_id), None)
        fields = {"completed_on": date.today().isoformat(), "score": result["pct"]}
        if existing:
            repo.update(existing["id"], **fields)
        else:
            repo.add({"worker_id": worker_id, "induction_id": induction_id, **fields})
        storage.log_activity("training", f"{worker['name']} completed {induction['title']} ({result['pct']}%)")
    return result, None


def certificate(induction_id, worker_id):
    induction, worker = InductionRepository().get(induction_id), WorkerRepository().get(worker_id)
    record = next((r for r in InductionRecordRepository().all() if r["worker_id"] == worker_id and r["induction_id"] == induction_id), None)
    if not (induction and worker and record):
        return None
    site = SiteRepository().get(worker["site_id"]) or {}
    return {"induction": induction, "worker": worker, "record": record, "site_name": site.get("name", "Unassigned")}
