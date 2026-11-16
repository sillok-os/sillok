"""Work context — which kind of work this session is doing, held across turns.

Kernel manager *Sacho* (史草, the draft record written while events happen)
· experimental since 0.4.0.

Why: a message-level router only sees the current message. In the upstream
harness only 31.4 % of 1,986 human turns over 30 days were attributed to a
work type, and 66.4 % of the unattributed turns came after a turn in the same
session that *had* been attributed — most follow-ups are short ("go",
"continue", a screenshot) and carry no keywords. Replaying the same 30 days
with this precedence lifted attribution to 65.9 % (64.8 % without the action
signal).

Precedence, highest first:

1. **explicit** — the router matched a work-type profile on this message;
2. **action** — the session's recent file writes concentrate (≥ 2 writes,
   ≥ 70 % share, last 30 min, after the last explicit turn) in one profile's
   path prefixes;
3. **inherited** — the previous turn was ≤ 2 h ago *and* the last explicit or
   action evidence is ≤ 4 h old (limits drift into a mis-attribution).

A profile is a plain dict::

    {"id": "code-review", "label": "Code review",
     "action_signals": {"path_prefixes": ["src/", "tests/"],
                        "engagement_types": ["review"]},
     "guide_refs": ["docs/sop/review.md"],
     "triggers": ["code review", "PR"]}      # optional: see match_explicit()

Off switch: ``SILLOK_WORK_CONTEXT=off``. No session ID → no state, no output.
"""

from __future__ import annotations

import time
from collections import Counter
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from .state import env_off, prune, read_json, session_file, session_lock, write_json_atomic

GAP_S = 2 * 3600
ANCHOR_S = 4 * 3600
ACTION_LOOKBACK_S = 1800
ACTION_MIN_WRITES = 2
ACTION_MIN_SHARE = 0.7
SCHEMA = 1
ENV_OFF = "SILLOK_WORK_CONTEXT"

Profile = dict[str, Any]
Write = tuple[float, str]
Engagement = tuple[str, list[str]]


def enabled() -> bool:
    return not env_off(ENV_OFF)


def decide(
    prev: dict[str, Any] | None,
    explicit_id: str | None,
    action_id: str | None,
    now: float,
    gap_s: float = GAP_S,
    anchor_s: float = ANCHOR_S,
) -> dict[str, Any]:
    """Pure state transition. ``source`` is explicit | action | inherited | None."""
    prev = prev if isinstance(prev, dict) else {}
    base = {"last_seen": now, "explicit_at": prev.get("explicit_at")}
    if explicit_id:
        return {
            **base,
            "id": explicit_id,
            "source": "explicit",
            "anchor_at": now,
            "anchor_source": "explicit",
            "explicit_at": now,
            "since": prev.get("since") if prev.get("id") == explicit_id else now,
        }
    if action_id:
        return {
            **base,
            "id": action_id,
            "source": "action",
            "anchor_at": now,
            "anchor_source": "action",
            "since": prev.get("since") if prev.get("id") == action_id else now,
        }
    last_seen = float(prev.get("last_seen") or 0)
    anchor_at = float(prev.get("anchor_at") or 0)
    keep = {"anchor_at": anchor_at, "anchor_source": prev.get("anchor_source")}
    if prev.get("id") and now - last_seen <= gap_s and now - anchor_at <= anchor_s:
        return {
            **base,
            **keep,
            "id": prev["id"],
            "source": "inherited",
            "since": prev.get("since") or anchor_at,
        }
    return {**base, **keep, "id": None, "source": None, "since": None}


def match_explicit(message: str, profiles: list[Profile]) -> str | None:
    """Profile whose ``triggers`` hit the message most — the explicit signal when no router names one.

    Uses the router's token rule (upper-case abbreviations such as ``PR``
    match whole tokens only). Ties go to the higher ``priority``; no hit → None.
    """
    from sillok.naru.router_2tier import keyword_hit

    best: tuple[int, int, str] | None = None
    for profile in profiles:
        hits = sum(1 for t in profile.get("triggers") or [] if keyword_hit(str(t), message))
        if hits:
            key = (hits, int(profile.get("priority") or 0), str(profile.get("id")))
            if best is None or key[:2] > best[:2]:
                best = key
    return best[2] if best else None


def path_profile(
    rel_path: str, profiles: list[Profile], engagements: Iterable[Engagement] = ()
) -> str | None:
    """Map one file path to a profile ID — longest path prefix wins, then engagement types."""
    path = rel_path.replace("\\", "/")
    path = (path[2:] if path.startswith("./") else path).lstrip("/")
    best: tuple[int, str] | None = None
    for profile in profiles:
        for prefix in (profile.get("action_signals") or {}).get("path_prefixes") or []:
            prefix = str(prefix)
            if prefix and path.startswith(prefix) and (best is None or len(prefix) > best[0]):
                best = (len(prefix), str(profile.get("id")))
    if best:
        return best[1]
    for eng_path, types in engagements:
        if path == eng_path or path.startswith(eng_path.rstrip("/") + "/"):
            ranked = sorted(
                (
                    p
                    for p in profiles
                    if set(types)
                    & {
                        str(t)
                        for t in (p.get("action_signals") or {}).get("engagement_types") or []
                    }
                ),
                key=lambda p: int(p.get("priority", 0)),
                reverse=True,
            )
            return str(ranked[0].get("id")) if ranked else None
    return None


def vote(
    writes: Iterable[Write],
    since: float,
    now: float,
    profiles: list[Profile],
    engagements: Iterable[Engagement] = (),
) -> str | None:
    """Profile with ≥ 2 mapped writes and ≥ 70 % of *all* writes in ``(since, now]``."""
    engagements = list(engagements)
    votes: Counter[str] = Counter()
    total = 0
    for ts, rel in writes:
        if ts <= since or ts > now:
            continue
        total += 1
        pid = path_profile(rel, profiles, engagements)
        if pid:
            votes[pid] += 1
    if not votes:
        return None
    top, count = votes.most_common(1)[0]
    if count < ACTION_MIN_WRITES or count / total < ACTION_MIN_SHARE:
        return None
    return top


def _explicit_floor(prev: dict[str, Any] | None) -> float:
    """Writes before the last explicit turn never count as action evidence."""
    if not isinstance(prev, dict):
        return 0.0
    return float(prev.get("explicit_at") or 0)


def _first_guide(profile: Profile, guide_ok: Callable[[str], bool]) -> str | None:
    return next((str(r) for r in profile.get("guide_refs") or [] if r and guide_ok(str(r))), None)


def resolve(
    state_dir: Path,
    session_id: str,
    profiles: list[Profile],
    *,
    explicit_id: str | None = None,
    writes: Iterable[Write] = (),
    engagements: Iterable[Engagement] = (),
    now: float | None = None,
    guide_ok: Callable[[str], bool] | None = None,
) -> dict[str, Any] | None:
    """Decide this turn's work context and persist it. ``None`` when there is none.

    ``writes`` are ``(epoch_seconds, repo_relative_path)`` pairs this session
    wrote recently (your hook records them). ``guide_ok`` filters which
    guide reference may be surfaced (e.g. reject reference-only paths).

    State is saved under a per-session lock; if the lock is not acquired in
    0.5 s the decision is still returned but not saved, and a state written
    by a later turn is never overwritten by an earlier one.
    """
    if not (session_id or "").strip() or not enabled():
        return None
    now = time.time() if now is None else now
    guide_ok = guide_ok or (lambda ref: ".." not in Path(ref).parts)
    profiles = [p for p in profiles or [] if isinstance(p, dict) and p.get("id")]
    path = session_file(state_dir, session_id)
    with session_lock(state_dir, session_id) as lock:
        prev = read_json(path)
        if prev.get("schema") != SCHEMA:
            prev = {}
        action_id = None
        if not explicit_id:
            since = max(now - ACTION_LOOKBACK_S, _explicit_floor(prev))
            action_id = vote(writes, since, now, profiles, engagements)
        state = decide(prev, explicit_id, action_id, now)
        newer_saved = float(prev.get("last_seen") or 0) > now
        if lock.held and not newer_saved:
            try:
                write_json_atomic(path, {**state, "schema": SCHEMA})
                prune(state_dir, now)
            except OSError:
                pass
    if not state.get("id"):
        return None
    profile = next((p for p in profiles if str(p.get("id")) == state["id"]), {})
    return {
        "id": state["id"],
        "label": profile.get("label"),
        "source": state["source"],
        "guide": _first_guide(profile, guide_ok),
        "anchor_age_s": int(now - float(state.get("anchor_at") or now)),
    }


def render_line(context: dict[str, Any] | None) -> str:
    """One line a hook can inject on non-explicit turns (explicit turns already carry the full block)."""
    if not context or context.get("source") not in {"action", "inherited"}:
        return ""
    label = context.get("label") or context["id"]
    guide = f" · guide: {context['guide']}" if context.get("guide") else ""
    return f"[work context] {label} ({context['source']}){guide}"


def replay(
    turns: Iterable[dict[str, Any]],
    profiles: list[Profile],
    *,
    gap_s: float = GAP_S,
    anchor_s: float = ANCHOR_S,
) -> dict[str, Any]:
    """Offline attribution replay over logged turns (no state written).

    Each turn: ``{"session": str, "ts": float, "explicit_id": str|None,
    "writes": [(ts, path), ...]}`` in time order. Returns the share of turns
    attributed with and without the kernel, so a deployment can measure its
    own lift before switching the hook on.
    """
    profiles = [p for p in profiles if isinstance(p, dict) and p.get("id")]
    states: dict[str, dict[str, Any]] = {}
    total = explicit = attributed = 0
    by_source: Counter[str] = Counter()
    for turn in turns:
        total += 1
        sid = str(turn.get("session") or "")
        now = float(turn["ts"])
        prev = states.get(sid, {})
        eid = turn.get("explicit_id") or None
        explicit += 1 if eid else 0
        action_id = None
        if not eid:
            since = max(now - ACTION_LOOKBACK_S, _explicit_floor(prev))
            action_id = vote(turn.get("writes") or (), since, now, profiles)
        state = decide(prev, eid, action_id, now, gap_s, anchor_s)
        states[sid] = state
        if state.get("id"):
            attributed += 1
            by_source[str(state["source"])] += 1
    return {
        "turns": total,
        "explicit_share": round(explicit / total, 4) if total else 0.0,
        "attributed_share": round(attributed / total, 4) if total else 0.0,
        "by_source": dict(by_source),
    }
