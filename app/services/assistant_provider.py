"""Rule-based DemoProvider (no API key needed). The Groq provider lives in assistant_groq.py.

A provider returns: {"text", "sources": [..], "links": [{"label","href"}], "pending": {...} | None}.
A pending action is only ever applied after the user presses Confirm (see assistant_service)."""
import re

from app.data.safety_documents import DOCUMENTS
from app.repositories.site_repository import SiteRepository
from app.repositories.worker_repository import WorkerRepository
from app.services import action_service, dashboard_service, incident_service, inspection_service, workforce_service

STOP = set("the and for are what which that this with from have has was were does how who when where should must can you your about into".split())
EXAMPLES = ["What PPE is required for working at height?", "What is the emergency procedure?", "Summarize the latest incident.",
            "What safety issues were identified during the latest inspection?"]
COMMANDS = ["mark ACT-05 as completed", "close INC-02", "move Brian Mwangi to Eastgate", "add worker Jane Doe as Electrician to Ridgeline"]
HELP_TEXT = ("Here is what you can do.\n\nAsk a question\n- Site procedures and PPE, e.g. \"What is the emergency procedure?\"\n- Summaries of the latest incident or inspection\n"
             "- Status, e.g. \"What's overdue?\" or \"Which certifications are expiring?\"\n\nRun a command (I always ask you to confirm first)\n"
             "- Update an action: \"mark ACT-05 as completed\"\n- Update an incident: \"close INC-02\" or \"add a note to INC-01: toe boards installed\"\n"
             "- Move a worker: \"move Brian Mwangi to Eastgate\"\n- Add a worker: \"add worker Jane Doe to Ridgeline\"\n- Report an incident: \"report a near miss at Harbour: description\"")
HELP = ("I couldn't match that to the sample documents or to an action I can take. Try a question such as \"What is the emergency procedure?\", "
        "a summary request, or a command such as \"mark ACT-05 as completed\", \"close INC-02\", \"move Brian Mwangi to Eastgate\" or \"add worker Jane Doe to Ridgeline\".")


def _reply(text, sources=None, links=None, pending=None, label="Simulated demo response"):
    return {"text": text, "sources": sources or [], "links": links or [], "pending": pending, "label": label}


def _pending(kind, summary, **params):
    return {"type": kind, "summary": summary, "params": params}


def _tokens(text):
    words = (w[:-1] if len(w) > 4 and w.endswith("s") else w for w in re.findall(r"[a-z]+", text.lower()))
    return {w for w in words if len(w) > 2 and w not in STOP}


def _find_site(text):
    low = text.lower()
    for s in SiteRepository().all():
        first = re.findall(r"[a-z]+", s["name"].lower())[0]
        if s["name"].lower() in low or first in low or re.search(rf"\b{s['id'].lower()}\b", low):
            return s
    return None


def _find_worker(text):
    low, workers = text.lower(), WorkerRepository().all()
    full = [w for w in workers if w["name"].lower() in low]
    if full:
        return full[0]
    firsts = [w for w in workers if re.search(rf"\b{w['name'].split()[0].lower()}\b", low)]
    return firsts[0] if len(firsts) == 1 else None


class DemoProvider:
    def respond(self, message, history=None):
        low = message.lower()
        for handler in (self._action, self._incident_cmd, self._assign, self._add_worker, self._report, self._summary, self._stats):
            result = handler(message, low)
            if result:
                return result
        return self._documents(message)

    # ---- commands (return a pending action, never change data) ----
    def _action(self, message, low):
        m = re.search(r"\bact-?(\d+)\b", low)
        if not m and not re.search(r"\b(mark|set|complete|finish)\b.*\baction\b", low):
            return None
        if not m:
            open_ids = ", ".join(a["id"] for a in action_service.list_actions("open")[:6])
            return _reply(f"Which action? Open actions include {open_ids}. Try \"mark ACT-05 as completed\".", ["Live demo data: actions"])
        a = action_service.get_action(f"ACT-{int(m.group(1)):02d}")
        if not a:
            return _reply(f"I couldn't find action ACT-{int(m.group(1)):02d}.", ["Live demo data: actions"])
        status = ("in_progress" if re.search(r"in[- ]progress|start|begin", low) else "completed" if re.search(r"complet|done|finish|close|resolve", low)
                  else "open" if re.search(r"re-?open|\bopen\b", low) else None)
        links = [{"label": f"Open {a['id']}", "href": f"/actions/{a['id']}"}]
        if not status:
            return _reply(f"{a['id']}: {a['title']}\nStatus: {action_service.STATUSES[a['status']]} | Priority: {a['priority']} | Due {a['due']} | Assigned to {a['assignee']}", ["Live demo data: actions"], links)
        label = action_service.STATUSES[status].lower()
        return _reply(f"I can set {a['id']} (\"{a['title']}\") to {label}. Confirm to apply.", ["Live demo data: actions"], links,
                      _pending("action_status", f"Set {a['id']} to {label}", action_id=a["id"], status=status))

    def _incident_cmd(self, message, low):
        m = re.search(r"\binc-?(\d+)\b", low)
        if not m:
            return None
        inc = incident_service.get_incident(f"INC-{int(m.group(1)):02d}")
        if not inc:
            return _reply(f"I couldn't find incident INC-{int(m.group(1)):02d}.", ["Live demo data: incidents"])
        links = [{"label": f"Open {inc['id']}", "href": f"/incidents/{inc['id']}"}]
        if re.search(r"\bnote\b", low):
            parts = re.split(r"\bnote\b[:\s,-]*(?:that\s+)?", message, maxsplit=1, flags=re.I)
            text = parts[1].strip() if len(parts) > 1 else ""
            if not text:
                return _reply("What should the note say? Try \"add a note to INC-01: toe boards installed\".", ["Live demo data: incidents"], links)
            return _reply(f"I can add this note to {inc['id']}: \"{text}\". Confirm to apply.", ["Live demo data: incidents"], links,
                          _pending("incident_note", f"Add a note to {inc['id']}", incident_id=inc["id"], text=text))
        status = ("closed" if re.search(r"clos|resolve", low) else "investigating" if "investigat" in low else "open" if re.search(r"re-?open|\bopen\b", low) else None)
        if not status:
            return _reply(f"{inc['id']}: {inc['title']}\nSeverity: {inc['severity']} | Status: {incident_service.STATUSES[inc['status']]} | {inc['site_name']} | {inc['date']}", ["Live demo data: incidents"], links)
        label = incident_service.STATUSES[status].lower()
        return _reply(f"I can set {inc['id']} (\"{inc['title']}\") to {label}. Confirm to apply.", ["Live demo data: incidents"], links,
                      _pending("incident_status", f"Set {inc['id']} to {label}", incident_id=inc["id"], status=status))

    def _assign(self, message, low):
        if not re.search(r"\b(move|assign|transfer|reassign)\b", low):
            return None
        w, s = _find_worker(message), _find_site(message)
        if not (w and s):
            return _reply("Tell me the worker's name and the site, for example \"move Brian Mwangi to Eastgate\".", ["Live demo data: workforce"])
        return _reply(f"I can assign {w['name']} to {s['name']}. Their required inductions will change with the site. Confirm to apply.", ["Live demo data: workforce"],
                      [{"label": f"Open {w['name']}", "href": f"/workforce/{w['id']}"}],
                      _pending("assign_site", f"Assign {w['name']} to {s['name']}", worker_id=w["id"], site_id=s["id"]))

    def _add_worker(self, message, low):
        m = re.search(r"add (?:a |an |new )*worker\s+(?:named\s+)?(?P<name>[A-Za-z' -]+?)(?:\s+as (?:a |an )?(?P<title>[A-Za-z ]+?))?\s+(?:to|at|on)\s+(?P<site>.+)$", message, re.I)
        if not m:
            return _reply("Try \"add worker Jane Doe as Electrician to Ridgeline\".", ["Live demo data: workforce"]) if re.search(r"add (a |an |new )*worker", low) else None
        s = _find_site(m.group("site"))
        if not s:
            return _reply("I didn't recognise that site. The sites are " + ", ".join(x["name"] for x in SiteRepository().all()) + ".", ["Live demo data: sites"])
        title = (m.group("title") or "Site Worker").strip().title()
        return _reply(f"I can add {m.group('name').strip().title()} ({title}) to {s['name']}. Confirm to apply.", ["Live demo data: workforce"], None,
                      _pending("add_worker", f"Add {m.group('name').strip().title()} to {s['name']}", name=m.group("name").strip().title(), job_title=title, site_id=s["id"]))

    def _report(self, message, low):
        if not re.match(r"\s*(please\s+)?(report|log)\b", low):
            return None
        s = _find_site(message)
        desc = message.split(":", 1)[1].strip() if ":" in message else ""
        if not (s and desc):
            return _reply("To report an incident use: \"report a near miss at Harbour: description of what happened\".", ["Live demo data: incidents"])
        kind = ("Near miss" if "near miss" in low else "Injury" if re.search(r"injur|hurt|cut\b", low) else "Property damage" if "damage" in low
                else "Environmental" if re.search(r"spill|environment", low) else "Other")
        sev = "High" if re.search(r"high|serious|major", low.split(":")[0]) else "Low" if re.search(r"\blow\b|minor", low.split(":")[0]) else "Medium"
        title = desc[:70].rstrip(". ").capitalize()
        return _reply(f"I can report a {sev.lower()}-severity {kind.lower()} at {s['name']}: \"{title}\". Confirm to apply.", ["Live demo data: incidents"], None,
                      _pending("report_incident", f"Report {kind.lower()} at {s['name']}", title=title, type=kind, severity=sev, site_id=s["id"], description=desc))

    # ---- read-only answers from live demo data ----
    def _summary(self, message, low):
        if "incident" in low and re.search(r"summar|latest|last|recent|newest", low):
            rows = incident_service.list_incidents()
            i = incident_service.get_incident(rows[0]["id"]) if rows else None
            if not i:
                return _reply("There are no incidents recorded.", ["Live demo data: incidents"])
            acts = "; ".join(f"{a['id']} ({action_service.STATUSES[a['status']].lower()}{', overdue' if a['overdue'] else ''})" for a in i["actions"]) or "none"
            last = f"\nLatest note: {i['notes'][-1]['text']}" if i["notes"] else ""
            text = (f"Latest incident: {i['id']} - {i['title']}\n{i['type']}, {i['severity']} severity, status {incident_service.STATUSES[i['status']].lower()}.\n"
                    f"{i['site_name']}, {i['date']}, reported by {i['reporter']}.{last}\nLinked actions: {acts}.")
            return _reply(text, ["Live demo data: incidents"], [{"label": f"Open {i['id']}", "href": f"/incidents/{i['id']}"}])
        if "inspection" in low and re.search(r"summar|latest|last|recent|issue|finding|identif|fail", low):
            rows = inspection_service.list_inspections()
            i = inspection_service.get_inspection(rows[0]["id"]) if rows else None
            if not i:
                return _reply("There are no inspections recorded.", ["Live demo data: inspections"])
            head = f"Latest inspection: {i['id']} - {i['title']}\n{i['site_name']}, {i['date']}, inspector {i['inspector']}.\n"
            if not i["findings"]:
                body = "All checklist items passed. No findings."
            else:
                lines = [f"- {f['text']}" + (f" ({f['note']})" if f["note"] else "") + (f" -> {f['action']['id']}, {f['action']['status_label'].lower()}, due {f['action']['due']}" if f["action"] else "") for f in i["findings"]]
                body = f"{len(i['findings'])} finding(s):\n" + "\n".join(lines)
            return _reply(head + body, ["Live demo data: inspections"], [{"label": f"Open {i['id']}", "href": f"/inspections/{i['id']}"}])
        return None

    def _stats(self, message, low):
        if "overdue" in low:
            rows = action_service.list_actions("overdue")
            text = "Overdue actions:\n" + "\n".join(f"- {a['id']} {a['title']} (due {a['due']}, {a['assignee']})" for a in rows) if rows else "There are no overdue actions."
            return _reply(text, ["Live demo data: actions"], [{"label": "Open overdue actions", "href": "/actions?view=overdue"}])
        if re.search(r"expir", low):
            d = dashboard_service.build_dashboard()
            lines = [f"- {e['worker']}: {e['name']} ({'expired' if e['days'] < 0 else 'in ' + str(e['days']) + ' days'})" for e in d["expiries"]]
            return _reply(f"{d['stats']['expiring']} certification(s) expired or expiring within 30 days. Soonest:\n" + "\n".join(lines), ["Live demo data: workforce"])
        return None

    # ---- keyword retrieval over the sample documents ----
    def _documents(self, message):
        q, scored = _tokens(message), []
        for d in DOCUMENTS:
            title = _tokens(d["title"])
            scored += [(len(q & (_tokens(c) | title)) + len(q & _tokens(c)), d["title"], c) for c in d["chunks"]]
        scored = sorted((s for s in scored if s[0] >= 2), key=lambda s: -s[0])[:2]
        if not scored:
            return _reply(HELP)
        text = "\n\n".join(f"{c}\n(Source: {t})" for _, t, c in scored)
        return _reply(text, [f"Sample document: {t}" for _, t, _ in scored])
