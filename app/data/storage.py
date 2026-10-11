"""JSON-file storage: read, add, update, reset. Atomic writes, thread-safe."""
import json
import os
import tempfile
import threading
from datetime import datetime

from app.core.config import settings
from app.data.seed import build_seed

_lock = threading.RLock()


def _write(data):
    path = settings.data_file
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def _load():
    if not settings.data_file.exists():
        _write(build_seed())
    with open(settings.data_file, encoding="utf-8") as f:
        return json.load(f)


def list_records(collection):
    with _lock:
        return _load().get(collection, [])


def get_record(collection, record_id):
    return next((r for r in list_records(collection) if r.get("id") == record_id), None)


def _next_id(records, prefix):
    nums = [int(r["id"][len(prefix):]) for r in records if r.get("id", "").startswith(prefix) and r["id"][len(prefix):].isdigit()]
    return f"{prefix}{max(nums, default=0) + 1:02d}"


def add_record(collection, record, prefix):
    with _lock:
        data = _load()
        data.setdefault(collection, [])
        record = {**record, "id": _next_id(data[collection], prefix)}
        data[collection].append(record)
        _write(data)
        return record


def update_record(collection, record_id, changes):
    with _lock:
        data = _load()
        for rec in data[collection]:
            if rec.get("id") == record_id:
                rec.update(changes)
                _write(data)
                return rec
    return None


def clear_collection(collection):
    with _lock:
        data = _load()
        data[collection] = []
        _write(data)


def log_activity(kind, text):
    with _lock:
        data = _load()
        data["activity"].insert(0, {"at": datetime.now().isoformat(timespec="seconds"), "kind": kind, "text": text})
        _write(data)


def reset_data():
    with _lock:
        _write(build_seed())
