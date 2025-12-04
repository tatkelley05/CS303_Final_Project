# logger.py
import json
import time
import threading
from pathlib import Path

import config

_lock = threading.Lock()


def _ensure_log_dir():
    Path(config.LOG_DIR).mkdir(parents=True, exist_ok=True)


def log_event(event_type: str, **fields) -> None:
    """
    Append one JSON line to LOG_FILE.
    Always includes a timestamp (seconds since epoch) and event_type.
    """
    _ensure_log_dir()

    event = {
        "ts": time.time(),
        "event_type": event_type,
        **fields,
    }

    line = json.dumps(event, ensure_ascii=False)

    with _lock:
        with open(config.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

