"""Playbook store, selection, rendering and outcome learning."""

from __future__ import annotations

import contextlib
import os
import re
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, cast

from sillok.sacho.state import FileLock, read_json, session_file, write_json_atomic

SCHEMA = 1
TOP_K = 3
BLOCK_MAX_BYTES = 900
OUTCOME_GAP_S = 2 * 3600
PROMOTE_MIN_HELPFUL = 3
MODES = ("off", "shadow", "auto")
ENV_MODE = "SILLOK_PLAYBOOK_MODE"

#: A short stand-alone approval of the previous turn.
ACCEPT = re.compile(
    r"^\s*(go|ok|okay|yes|lgtm|looks good|perfect|great|keep going|continue|"
    r"진행|계속|좋아요?|좋습니다|완벽(해요|합니다)?|오케이)\s*[.!~]*\s*$",
    re.IGNORECASE,
)
#: A closing command counts as acceptance of the work just shown.
CLOSE = re.compile(r"^\s*\[pm\]\s*(done|close)\b", re.IGNORECASE)
#: The human says the previous answer was wrong or incomplete.
CORRECTION = re.compile(
    r"(?i)\b(wrong|incorrect|not what i (asked|meant)|you (missed|forgot)|missing|left out|"
    r"didn'?t (apply|work)|still (broken|wrong|missing)|undo|revert|that'?s not)\b|"
    r"틀렸|틀려|잘못|누락|빠졌|빠져|반영 안|안 됐|안됐|아니(요|야)\b|다시 (해|하)"
)
#: Machine-injected input (command wrappers, reminders) is never learned from.
_MACHINE = re.compile(r"^\s*(<[a-z-]+[ >]|\[automation\]|Caveat:)", re.IGNORECASE)
_TIER = {"origin": 2, "summary": 1, "body": 0}


def classify(text: str | None) -> str | None:
    """Next human input → ``helpful`` | ``harmful`` | None.

    A correction wins even inside a closing command; a bare approval or a
    closing command is helpful; anything else teaches nothing.
    """
    text = (text or "").strip()
    if not text or _MACHINE.match(text):
        return None
    if CORRECTION.search(text) and not ACCEPT.match(text):
        return "harmful"
    if CLOSE.match(text) or ACCEPT.match(text):
        return "helpful"
    return None


def current_mode(default: str = "shadow") -> str:
    env = os.environ.get(ENV_MODE, "").strip().lower()
    if env in MODES:
        return env
    return default if default in MODES else "shadow"


class Playbook:
    """Global playbook (``_playbook.json``) plus per-session exposure files.

    All read-modify-write of the global file happens under one lock; if the
    lock is not acquired, the turn neither learns nor shows anything (another
    call may be judging this session's exposure).
    """

    def __init__(
        self,
        state_dir: Path,
        *,
        mode: str | None = None,
        classifier: Callable[[str | None], str | None] = classify,
    ) -> None:
        self.state_dir = Path(state_dir)
        self.mode = current_mode(mode or "shadow")
        self.classifier = classifier

    # ── storage ────────────────────────────────────────────────────────
    @property
    def path(self) -> Path:
        return self.state_dir / "_playbook.json"

    def load(self) -> dict[str, Any]:
        data = read_json(self.path)
        if data.get("schema") != SCHEMA:
            data = {}
        data.setdefault("schema", SCHEMA)
        data.setdefault("items", {})
        data.setdefault("counters", {})
        return data

    def _lock(self) -> FileLock:
        return FileLock(self.state_dir / "_playbook.lock")

    def add_items(self, items: Iterable[dict[str, Any]]) -> int:
        """Upsert items; counters are never reset. Returns the number written."""
        with self._lock() as lock:
            if not lock.held:
                return 0
            data = self.load()
            n = 0
            for item in items:
                if not isinstance(item, dict) or not item.get("id") or not item.get("work_type"):
                    continue
                data["items"][str(item["id"])] = {
                    "work_type": str(item["work_type"]),
                    "title": str(item.get("title") or item["id"]),
                    "path": str(item.get("path") or ""),
                    "how": str(item.get("how") or "body"),
                    "created": str(item.get("created") or ""),
                }
                n += 1
            write_json_atomic(self.path, data)
            return n

    # ── selection & rendering ─────────────────────────────────────────
    @staticmethod
    def select(data: dict[str, Any], work_type: str, k: int = TOP_K) -> list[str]:
        """Beta mean (h+1)/(h+x+2) desc → attribution tier → newest. Shadow counters never rank."""
        counters = (data.get("counters") or {}).get(work_type) or {}
        rows = []
        for item_id, item in (data.get("items") or {}).items():
            if item.get("work_type") != work_type:
                continue
            c = counters.get(item_id) or {}
            h, x = int(c.get("h", 0)), int(c.get("x", 0))
            rows.append(
                (
                    (h + 1) / (h + x + 2),
                    _TIER.get(str(item.get("how")), 0),
                    str(item.get("created", "")),
                    item_id,
                )
            )
        rows.sort(reverse=True)
        return [row[-1] for row in rows[:k]]

    @staticmethod
    def render(
        data: dict[str, Any], chosen: list[str], label: str, max_bytes: int = BLOCK_MAX_BYTES
    ) -> tuple[str, list[str]]:
        """(block, item IDs actually in it). Items cut by the byte cap are not an exposure."""
        items = data.get("items") or {}
        picked = [(i, items[i]) for i in chosen if i in items]
        if not picked:
            return "", []
        head = f"## Lessons for {label} (reference · read only if relevant)"
        size = len(head.encode("utf-8"))
        lines: list[str] = []
        shown: list[str] = []
        for item_id, item in picked:
            target = f" → {item['path']}" if item.get("path") else ""
            line = f"- {item['title']}{target}"
            if size + len(line.encode("utf-8")) + 1 > max_bytes:
                break
            lines.append(line)
            shown.append(item_id)
            size += len(line.encode("utf-8")) + 1
        return (head + "\n" + "\n".join(lines), shown) if lines else ("", [])

    # ── learning ──────────────────────────────────────────────────────
    @staticmethod
    def _apply(
        data: dict[str, Any], pending: dict[str, Any], outcome: str, counted: set[str]
    ) -> bool:
        work_type = str(pending.get("work_type") or "")
        if not work_type or outcome not in {"helpful", "harmful"}:
            return False
        live = pending.get("mode") == "auto"
        key = (
            ("h" if outcome == "helpful" else "x")
            if live
            else ("sh" if outcome == "helpful" else "sx")
        )
        bucket = data.setdefault("counters", {}).setdefault(work_type, {})
        changed = False
        for item_id in pending.get("items") or []:
            mark = f"{work_type}|{item_id}|{key}"
            if mark in counted:
                continue
            c = bucket.setdefault(str(item_id), {"h": 0, "x": 0, "sh": 0, "sx": 0})
            c[key] = int(c.get(key, 0)) + 1
            counted.add(mark)
            changed = True
        return changed

    def turn(
        self,
        session_id: str,
        human_input: str,
        work_type: str | None,
        label: str | None = None,
        *,
        now: float | None = None,
    ) -> str:
        """Judge the previous exposure with this input, then expose this turn's top items.

        Returns the block to inject (empty in ``shadow``/``off`` mode, without
        a session, for machine input, or when nothing applies). Never raises.
        """
        try:
            if self.mode == "off" or not (session_id or "").strip():
                return ""
            if not (human_input or "").strip() or _MACHINE.match(human_input):
                return ""  # machine input neither consumes nor judges the pending exposure
            now = time.time() if now is None else now
            pending_path = session_file(self.state_dir, session_id, "playbook")
            with self._lock() as lock:
                if not lock.held:
                    return ""
                data = self.load()
                pending = read_json(pending_path)
                raw_counted = pending.get("counted")
                counted = (
                    {k for k in raw_counted if isinstance(k, str)}
                    if isinstance(raw_counted, list)
                    else set()
                )
                ts = float(pending.get("ts") or 0)
                judged = bool(pending.get("items")) and ts < now and now - ts <= OUTCOME_GAP_S
                outcome = self.classifier(human_input) if judged else None
                learned = bool(outcome) and self._apply(data, pending, str(outcome), counted)
                block, exposed = "", cast(list[str], [])
                if work_type:
                    chosen = self.select(data, work_type)
                    if chosen:
                        block, exposed = self.render(data, chosen, label or work_type)
                if exposed or pending.get("items"):
                    write_json_atomic(
                        pending_path,
                        {
                            "items": exposed,
                            "work_type": work_type or "",
                            "mode": self.mode,
                            "ts": now,
                            "counted": sorted(counted),
                        },
                    )
                if learned:
                    # under-count rather than suppress this turn's output
                    with contextlib.suppress(OSError):
                        write_json_atomic(self.path, data)
            return block if self.mode == "auto" else ""
        except Exception:  # noqa: BLE001 — a hook must never crash the turn
            return ""

    def promote_candidates(self, min_helpful: int = PROMOTE_MIN_HELPFUL) -> list[dict[str, Any]]:
        """Items helpful in ≥ ``min_helpful`` distinct sessions and never harmful (treatment counters)."""
        data = self.load()
        out = []
        for work_type, bucket in (data.get("counters") or {}).items():
            for item_id, c in bucket.items():
                if int(c.get("h", 0)) >= min_helpful and int(c.get("x", 0)) == 0:
                    item = (data.get("items") or {}).get(item_id, {})
                    out.append(
                        {
                            "work_type": work_type,
                            "item": item_id,
                            "title": item.get("title", ""),
                            "path": item.get("path", ""),
                            "helpful_sessions": int(c.get("h", 0)),
                        }
                    )
        return sorted(out, key=lambda r: (-r["helpful_sessions"], r["item"]))
