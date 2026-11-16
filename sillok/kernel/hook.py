"""One prompt hook that runs the four kernel managers in order · experimental since 0.4.0.

Per human turn (Claude Code ``UserPromptSubmit``)::

    sacho          work context: explicit > action > inherited   → one line
    gyeongyeon     playbook for that work type (shadow by default) → ≤ 900 B
    chunchugwan    memory / episode recall                        → ≤ 900 B
    seungjeongwon  collapse blocks already shown this session     → pointers

``SessionStart`` with ``source=compact`` resets the budget so the next turn
shows everything again (the model just lost its earlier context).

Configuration is a JSON file (``--config`` or ``SILLOK_KERNEL_CONFIG``)::

    {
      "state_dir":   "~/.sillok/state",
      "profiles":    "work-types.json",        # list of profiles (see sillok.sacho)
      "playbook":    {"mode": "shadow", "items": "playbook-items.json"},
      "recall":      {"memory_dir": "~/notes/memory", "db": "~/.sillok/recall.db",
                      "exposure_log": "~/.sillok/recall-exposure.jsonl"}
    }

Every section is optional; a missing section disables that manager. Each
manager has its own off switch (``SILLOK_WORK_CONTEXT``, ``SILLOK_PLAYBOOK_MODE``,
``SILLOK_MEMORY_RECALL``, ``SILLOK_CONTEXT_BUDGET``) and the hook as a whole
never fails the turn: any error yields no output and exit code 0.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ENV_CONFIG = "SILLOK_KERNEL_CONFIG"


def _path(value: Any, base: Path) -> Path | None:
    if not value:
        return None
    p = Path(os.path.expanduser(str(value)))
    return p if p.is_absolute() else base / p


def _load_json(path: Path | None) -> Any:
    if path is None:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_config(path: Path | None) -> dict[str, Any]:
    """Read the config and resolve every path relative to the config file."""
    if path is None:
        env = os.environ.get(ENV_CONFIG, "").strip()
        path = Path(os.path.expanduser(env)) if env else None
    raw = _load_json(path)
    if not isinstance(raw, dict) or path is None:
        return {}
    base = path.parent
    cfg: dict[str, Any] = {"state_dir": _path(raw.get("state_dir"), base)}
    profiles = _load_json(_path(raw.get("profiles"), base))
    cfg["profiles"] = profiles if isinstance(profiles, list) else []
    pb = raw.get("playbook") if isinstance(raw.get("playbook"), dict) else None
    if pb:
        items = _load_json(_path(pb.get("items"), base))
        cfg["playbook"] = {
            "mode": str(pb.get("mode") or "shadow"),
            "items": items if isinstance(items, list) else [],
        }
    rc = raw.get("recall") if isinstance(raw.get("recall"), dict) else None
    if rc and rc.get("memory_dir") and rc.get("db"):
        cfg["recall"] = {
            "memory_dir": _path(rc["memory_dir"], base),
            "db": _path(rc["db"], base),
            "exposure_log": _path(rc.get("exposure_log"), base),
        }
    return cfg


def prompt_turn(payload: dict[str, Any], cfg: dict[str, Any], *, now: float | None = None) -> str:
    """Context to add for this human prompt ('' when nothing applies)."""
    from sillok.chunchugwan import hook_block
    from sillok.gyeongyeon import Playbook
    from sillok.sacho import match_explicit, render_line, resolve
    from sillok.seungjeongwon import ContextBudget

    now = time.time() if now is None else now
    session = str(payload.get("session_id") or "")
    prompt = str(payload.get("prompt") or "")
    state_dir: Path | None = cfg.get("state_dir")
    profiles: list[dict[str, Any]] = cfg.get("profiles") or []
    parts: list[str] = []

    ctx = None
    if state_dir is not None and profiles:
        # An upstream router may name the work type; otherwise profile triggers
        # on this message; otherwise the session's action evidence or inheritance.
        named = payload.get("work_type")
        explicit = named if isinstance(named, str) else match_explicit(prompt, profiles)
        ctx = resolve(state_dir, session, profiles, explicit_id=explicit, now=now)
        line = render_line(ctx)
        if line:
            parts.append(line)

    budget = ContextBudget(state_dir, session, now=now)
    pb_cfg = cfg.get("playbook")
    if state_dir is not None and pb_cfg:
        playbook = Playbook(state_dir, mode=pb_cfg["mode"])
        if pb_cfg["items"] and not playbook.load()["items"]:
            playbook.add_items(pb_cfg["items"])
        block = playbook.turn(
            session, prompt, (ctx or {}).get("id"), (ctx or {}).get("label"), now=now
        )
        if block:
            parts.append(budget.list_block(block, "playbook"))

    rc = cfg.get("recall")
    if rc:
        block = hook_block(
            prompt,
            db=rc["db"],
            memory_dir=rc["memory_dir"],
            session_id=session,
            exposure_log=rc["exposure_log"],
        )
        if block:
            parts.append(budget.list_block(block, "recall"))
    budget.save()
    return "\n\n".join(p for p in parts if p)


def session_start(payload: dict[str, Any], cfg: dict[str, Any]) -> None:
    """After compaction the model lost earlier context — show everything again."""
    from sillok.seungjeongwon import reset

    if payload.get("source") == "compact" and cfg.get("state_dir") is not None:
        reset(cfg["state_dir"], str(payload.get("session_id") or ""))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    config = None
    if "--config" in argv:
        i = argv.index("--config")
        config = Path(os.path.expanduser(argv[i + 1])) if i + 1 < len(argv) else None
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            return 0
        cfg = load_config(config)
        event = payload.get("hook_event_name") or "UserPromptSubmit"
        if event == "SessionStart":
            session_start(payload, cfg)
            return 0
        text = prompt_turn(payload, cfg)
        if text:
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "UserPromptSubmit",
                            "additionalContext": text,
                        }
                    },
                    ensure_ascii=False,
                )
            )
    except Exception:  # noqa: BLE001 — a hook must never fail the turn
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
