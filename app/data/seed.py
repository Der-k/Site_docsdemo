"""Initial demo dataset. All people and projects are fictional.
Dates are relative to today so expiries stay realistic after every reset."""
from datetime import date, datetime, timedelta

from app.data.induction_content import CONTENT
from app.data.inspection_content import SEED_FAILS, TEMPLATES


def _d(n):
    return (date.today() + timedelta(days=n)).isoformat()


def _t(**kw):
    return (datetime.now() - timedelta(**kw)).isoformat(timespec="seconds")


SITES = [
    {"id": "S1", "name": "Ridgeline Wind Farm", "location": "Northern Plateau", "manager": "Amina Wekesa", "status": "active"},
    {"id": "S2", "name": "Harbour Substation Upgrade", "location": "Port District", "manager": "Daniel Otieno", "status": "active"},
    {"id": "S3", "name": "Eastgate Fabrication Yard", "location": "Industrial Estate", "manager": "Grace Mutua", "status": "active"},
]

WORKERS = [
    ("Samuel Njoroge", "Site Supervisor", "Operations", "S1"), ("Lydia Achieng", "Electrician", "Electrical", "S1"),
    ("Peter Kamau", "Rigger", "Lifting", "S1"), ("Faith Wanjiru", "Safety Officer", "HSE", "S1"),
    ("Brian Mwangi", "Crane Operator", "Lifting", "S1"), ("Naomi Chebet", "Electrical Engineer", "Electrical", "S2"),
    ("Joseph Ouma", "Cable Jointer", "Electrical", "S2"), ("Esther Mbugua", "Site Engineer", "Engineering", "S2"),
    ("Kevin Mutiso", "Technician", "Electrical", "S2"), ("Ruth Akinyi", "Safety Officer", "HSE", "S2"),
    ("Hassan Abdi", "Welder", "Fabrication", "S3"), ("Mercy Wambui", "Fabricator", "Fabrication", "S3"),
    ("Collins Rotich", "Scaffolder", "Access", "S3"), ("Janet Nyambura", "Quality Inspector", "Quality", "S3"),
    ("Isaac Kiprono", "Yard Foreman", "Operations", "S3"),
]

CERTS = ["Working at Height", "First Aid", "Confined Space Entry", "Electrical Safety"]
CLEAN = {0, 1, 2, 3, 5, 6, 10}  # workers with valid certificates and all required inductions
OFFSETS = [-20, 12, 25, 90, 120, 200, 300, 400, 150, 250, 330, 180, 220, 275, 365, 450]

INDUCTIONS = [
    {"id": "I1", "title": "General Site Safety Induction", "summary": "Core rules every person on site must know.", "duration_min": 20, "required_sites": ["S1", "S2", "S3"]},
    {"id": "I2", "title": "Working at Height Awareness", "summary": "Fall protection, harness checks and rescue basics.", "duration_min": 25, "required_sites": ["S1", "S2"]},
    {"id": "I3", "title": "Electrical Hazards Awareness", "summary": "Isolation, lock-out/tag-out and safe distances.", "duration_min": 25, "required_sites": ["S2"]},
    {"id": "I4", "title": "Hot Work and Fire Safety", "summary": "Permits, fire watch and extinguisher use.", "duration_min": 20, "required_sites": ["S3"]},
    {"id": "I5", "title": "Emergency Response Procedures", "summary": "Muster points, alarms and first response.", "duration_min": 15, "required_sites": ["S1", "S2", "S3"]},
]

INCIDENTS = [
    ("Dropped tool from platform level", "Near miss", "Medium", "S1", "Peter Kamau", -9, "investigating"),
    ("Minor hand laceration during cable stripping", "Injury", "Low", "S2", "Joseph Ouma", -27, "open"),
    ("Forklift contact with scaffold base", "Property damage", "Medium", "S3", "Isaac Kiprono", -48, "closed"),
    ("Exclusion zone breached during lift", "Near miss", "High", "S1", "Faith Wanjiru", -95, "closed"),
]

ACTIONS = [
    ("Install toe boards on level 2 platform", "incident", "INC-01", "Amina Wekesa", "High", -4, "in_progress"),
    ("Replace damaged cable stripping tools", "incident", "INC-02", "Daniel Otieno", "Medium", 6, "open"),
    ("Repaint scaffold base guard markings", "incident", "INC-03", "Grace Mutua", "Low", -30, "completed"),
    ("Refresh lifting exclusion zone briefing", "incident", "INC-04", "Samuel Njoroge", "High", -60, "completed"),
    ("Renew expired First Aid certificates", "inspection", "INS-02", "Ruth Akinyi", "High", -2, "open"),
    ("Fix missing fire extinguisher signage", "inspection", "INS-03", "Isaac Kiprono", "Medium", 10, "open"),
    ("Repair damaged guardrail section", "inspection", "INS-01", "Amina Wekesa", "High", 3, "in_progress"),
    ("Update site emergency contact board", "inspection", "INS-04", "Daniel Otieno", "Low", 14, "open"),
]

INSPECTIONS = [
    ("Weekly Site Safety Inspection", "S1", -6, "Faith Wanjiru"), ("PPE and Certification Check", "S2", -12, "Ruth Akinyi"),
    ("Fire and Housekeeping Inspection", "S3", -15, "Janet Nyambura"), ("Weekly Site Safety Inspection", "S2", -20, "Ruth Akinyi"),
    ("Weekly Site Safety Inspection", "S3", -27, "Janet Nyambura"),
]


def build_seed():
    workers, certs, records = [], [], []
    for i, (name, title, dept, site) in enumerate(WORKERS):
        wid = f"W{i + 1:02d}"
        workers.append({"id": wid, "name": name, "job_title": title, "department": dept, "site_id": site})
        for j, cert in enumerate(CERTS[: 2 + i % 3]):
            certs.append({"id": f"C{len(certs) + 1:03d}", "worker_id": wid, "name": cert, "expires": _d(150 + 40 * j if i in CLEAN else OFFSETS[(i * 3 + j) % 16])})
        for ind in INDUCTIONS:
            if site not in ind["required_sites"]:
                continue
            done = i in CLEAN or ((i % 5 != 4) if ind["id"] == "I1" else (i % 2 == 0) if ind["id"] == "I5" else (i % 3 != 0))
            if done:
                records.append({"id": f"R{len(records) + 1:03d}", "worker_id": wid, "induction_id": ind["id"], "completed_on": _d(-10 - i), "score": 80 + i % 4 * 5})
    incidents = [
        {"id": f"INC-{k + 1:02d}", "title": t, "type": ty, "severity": sv, "site_id": s, "reporter": r, "date": _d(o), "status": st,
         "description": f"{t}. Reported on site by {r}.", "notes": []}
        for k, (t, ty, sv, s, r, o, st) in enumerate(INCIDENTS)
    ]
    notes = {"INC-01": [("Faith Wanjiru", -8, "Tool was unsecured. Platform edge lacks toe boards."), ("Amina Wekesa", -5, "Toe board install scheduled. Briefing given to the crew.")],
             "INC-03": [("Grace Mutua", -45, "Driver retrained. Scaffold base now guarded."), ("Grace Mutua", -40, "Investigation complete. Closed.")],
             "INC-04": [("Amina Wekesa", -90, "Zone re-marked and lift plan updated. Closed.")]}
    for inc in incidents:
        inc["notes"] = [{"at": _d(o), "author": a, "text": t} for a, o, t in notes.get(inc["id"], [])]
    actions = [
        {"id": f"ACT-{k + 1:02d}", "title": t, "source_type": st, "source_id": sid, "assignee": a, "priority": p, "due": _d(o), "status": s}
        for k, (t, st, sid, a, p, o, s) in enumerate(ACTIONS)
    ]
    by_title = {t["title"]: t for t in TEMPLATES}
    inspections = []
    for k, (title, site, off, inspector) in enumerate(INSPECTIONS):
        iid, tpl = f"INS-{k + 1:02d}", by_title[title]
        fail = SEED_FAILS.get(iid)
        responses = [{"item_id": it["id"], "result": "fail" if fail and it["id"] == fail[0] else "pass", "note": fail[1] if fail and it["id"] == fail[0] else ""} for it in tpl["items"]]
        findings = []
        if fail:
            text = next(it["text"] for it in tpl["items"] if it["id"] == fail[0])
            findings = [{"id": f"{iid}-F1", "item_id": fail[0], "text": text, "note": fail[1], "action_id": fail[2]}]
        inspections.append({"id": iid, "title": title, "template_id": tpl["id"], "site_id": site, "date": _d(off), "inspector": inspector,
                            "status": "submitted", "responses": responses, "observations": "", "findings": findings})
    activity = [
        {"at": _t(hours=3), "kind": "incident", "text": "Incident INC-01 moved to investigating"},
        {"at": _t(hours=20), "kind": "training", "text": "Lydia Achieng completed General Site Safety Induction"},
        {"at": _t(days=2), "kind": "inspection", "text": "Weekly Site Safety Inspection submitted for Ridgeline Wind Farm"},
        {"at": _t(days=3), "kind": "action", "text": "Action ACT-07 assigned to Amina Wekesa"},
        {"at": _t(days=5), "kind": "worker", "text": "Isaac Kiprono assigned to Eastgate Fabrication Yard"},
    ]
    return {"sites": SITES, "workers": workers, "certifications": certs, "inductions": [{**i, **CONTENT[i["id"]]} for i in INDUCTIONS], "induction_records": records,
            "incidents": incidents, "actions": actions, "inspections": inspections, "inspection_templates": TEMPLATES, "activity": activity, "assistant_chat": []}
