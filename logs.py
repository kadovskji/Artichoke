"""Log file setup and a helper to read the recent entries (used by /admin → Log)."""
import logging
import os
import re
import time
from logging.handlers import RotatingFileHandler

LOG_FILE = os.environ.get("LOG_FILE", "artichoke.log")
_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"
_TS = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ")


class _Relevant(logging.Filter):
    """Keep the bot's own events and every warning/error; drop library chatter."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("artichoke") or record.levelno >= logging.WARNING


def setup() -> None:
    fmt = logging.Formatter(_FORMAT, _DATEFMT)
    file_h = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3,
                                 encoding="utf-8")
    console = logging.StreamHandler()
    for h in (file_h, console):
        h.setFormatter(fmt)
        h.addFilter(_Relevant())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers[:] = [file_h, console]
    for noisy in ("httpx", "httpcore", "telegram.ext", "apscheduler"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def recent(minutes: int = 60, limit: int = 50) -> list[str]:
    """The last `limit` log lines written in the past `minutes` minutes."""
    cutoff = time.time() - minutes * 60
    lines: list[str] = []
    for path in (f"{LOG_FILE}.1", LOG_FILE):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines += f.read().splitlines()
        except OSError:
            continue
    out: list[str] = []
    keep = False
    for line in lines:
        if _TS.match(line):
            try:
                keep = time.mktime(time.strptime(line[:19], _DATEFMT)) >= cutoff
            except ValueError:
                keep = False
        if keep:
            out.append(line)
    return out[-limit:]
