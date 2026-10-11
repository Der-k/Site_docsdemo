"""Inspections: templates, submission, and automatic findings + corrective actions."""
from datetime import date, timedelta

from app.data import storage
from app.repositories.action_repository import ActionRepository
from app.repositories.inspection_repository import InspectionRepository, InspectionTemplateRepository
from app.repositories.site_repository import SiteRepository
from app.services.action_service import STATUSES
from app.services.dashboard_service import days_until

DUE_DAYS = {"High": 3, "Medium": 7, "Low": 14}


def list_templates():
    return InspectionTemplateRepository().all()


def get_template(template_id):
    return InspectionTemplateRepository().get(template_id)


def list_inspections():
    sites = {s["id"]: s["name"] for s in SiteRepository().all()}
    rows = [{**i, "site_name": sites.get(i["site_id"], "Unknown"), "fail_count": len(i["findings"])} for i in InspectionRepository().all()]
    return sorted(rows, key=lambda i: (i["date"], i["id"]), reverse=True)


def get_inspection(inspection_id):
    insp = InspectionRepository().get(inspection_id)
    if not insp:
        return None
    tpl = get_template(insp["template_id"]) or {"items": []}
    items = {it["id"]: it for it in tpl["items"]}
    actions = {a["id"]: a for a in ActionRepository().all()}
    rows = [{**r, "text": items.get(r["item_id"], {}).get("text", r["item_id"]), "category": items.get(r["item_id"], {}).get("category", "")} for r in insp["responses"]]
    findings = []
    for f in insp["findings"]:
        a = actions.get(f["action_id"])
        findings.append({**f, "action": a and {**a, "overdue": a["status"] != "completed" and days_until(a["due"]) < 0, "status_label": STATUSES[a["status"]]}})
    site = SiteRepository().get(insp["site_id"]) or {}
    return {**insp, "rows": rows, "findings": findings, "site_name": site.get("name", "Unknown")}


def submit_inspection(template_id, site_id, inspector, answers, observations):
    """answers: {item_id: {"result": "pass"|"fail", "note": str}}. Returns (inspection, error)."""
    tpl, site = get_template(template_id), SiteRepository().get(site_id)
    if not tpl or not site:
        return None, "Choose a valid template and site."
    if any(answers.get(it["id"], {}).get("result") not in ("pass", "fail") for it in tpl["items"]):
        return None, "Mark every checklist item as pass or fail."
    responses = [{"item_id": it["id"], "result": answers[it["id"]]["result"], "note": answers[it["id"]]["note"].strip()} for it in tpl["items"]]
    insp = InspectionRepository().add({"title": tpl["title"], "template_id": tpl["id"], "site_id": site_id, "date": date.today().isoformat(),
                                       "inspector": inspector.strip() or "Demo inspector", "status": "submitted", "responses": responses,
                                       "observations": observations.strip(), "findings": []})
    findings = _create_findings(insp, tpl, site)
    InspectionRepository().update(insp["id"], findings=findings)
    storage.log_activity("inspection", f"{insp['title']} submitted for {site['name']}: {len(findings)} finding(s), {len(findings)} action(s) created")
    return {**insp, "findings": findings}, None


def _create_findings(insp, tpl, site):
    items = {it["id"]: it for it in tpl["items"]}
    findings = []
    for n, r in enumerate((r for r in insp["responses"] if r["result"] == "fail"), start=1):
        item = items[r["item_id"]]
        action = ActionRepository().add({
            "title": f"Rectify: {item['text']}", "source_type": "inspection", "source_id": insp["id"], "assignee": site["manager"],
            "priority": item["priority"], "due": (date.today() + timedelta(days=DUE_DAYS[item["priority"]])).isoformat(), "status": "open",
            "description": r["note"] or "Failed during inspection."})
        findings.append({"id": f"{insp['id']}-F{n}", "item_id": item["id"], "text": item["text"], "note": r["note"], "action_id": action["id"]})
    return findings
