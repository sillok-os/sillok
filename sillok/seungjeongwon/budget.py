"""Session-level de-duplication of injected guidance blocks."""

from __future__ import annotations

import contextlib
import hashlib
import re
import time
from pathlib import Path

from sillok.sacho.state import env_off, read_json, session_file, write_json_atomic

DEDUP_WINDOW_S = 1800
MAX_KEYS = 200
ENV_OFF = "SILLOK_CONTEXT_BUDGET"
_SECTION_HEAD = re.compile(r"^\[([A-Za-z0-9._-]+)\]\s*$")


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


class SessionSeen:
    """Block keys this session saw recently → ``[epoch, content_digest]``."""

    def __init__(self, state_dir: Path, session_id: str, now: float | None = None) -> None:
        self.path = session_file(state_dir, session_id, "budget")
        self.now = time.time() if now is None else now
        raw = read_json(self.path).get("seen")
        self.seen: dict[str, list[float | str]] = {}
        if isinstance(raw, dict):
            # Malformed entries count as "never seen" — corrupt state must not suppress output.
            self.seen = {
                str(k): [float(v[0]), v[1]]
                for k, v in raw.items()
                if isinstance(v, list)
                and len(v) == 2
                and isinstance(v[1], str)
                and isinstance(v[0], (int, float))
                and not isinstance(v[0], bool)
            }
        self.stats = {"deduped": 0, "chars_saved": 0}

    def fresh(self, key: str, text: str) -> bool:
        """False if identical content was shown within the window; otherwise record it and return True.

        A recorded time in the future (clock rewind, corruption) reads as
        never seen, so a bad timestamp cannot suppress a block indefinitely.
        """
        prev = self.seen.get(key)
        digest = _digest(text)
        if (
            isinstance(prev, list)
            and len(prev) == 2
            and prev[1] == digest
            and 0 <= self.now - float(prev[0]) <= DEDUP_WINDOW_S
        ):
            return False
        self.seen[key] = [self.now, digest]
        return True

    def mark(self, key: str, text: str) -> None:
        self.seen[key] = [self.now, _digest(text)]

    def save(self) -> None:
        try:
            if len(self.seen) > MAX_KEYS:
                keep = sorted(self.seen.items(), key=lambda kv: float(kv[1][0]), reverse=True)[
                    :MAX_KEYS
                ]
                self.seen = dict(keep)
            write_json_atomic(self.path, {"schema": 1, "seen": self.seen})
        except (OSError, TypeError, ValueError):
            pass  # not recording only means the block is shown again next turn


def dedup_sections(block: str, seen: SessionSeen, paths: dict[str, str] | None = None) -> str:
    """Collapse ``[section-id]`` sections (followed by ``- `` lines) already shown.

    Lines before the first section (header) and after the last section's
    bullets (tail) are kept as-is. Collapsed sections become one line naming
    each section and, when known, the path to re-read it.
    """
    if not block:
        return block
    head: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    tail: list[str] = []
    for line in block.splitlines():
        match = _SECTION_HEAD.match(line)
        if match and not tail:
            sections.append((match.group(1), [line]))
        elif sections and not tail and line.startswith("- "):
            sections[-1][1].append(line)
        elif not sections:
            head.append(line)
        else:
            tail.append(line)
    if not sections:
        return block
    out = list(head)
    repeated: list[str] = []
    for section_id, body in sections:
        text = "\n".join(body)
        if seen.fresh(f"section:{section_id}", text):
            out.extend(body)
        else:
            path = (paths or {}).get(section_id)
            repeated.append(f"{section_id} → {path}" if path else section_id)
            seen.stats["deduped"] += 1
            seen.stats["chars_saved"] += len(text)
    if repeated:
        out.append(
            f"[same as earlier this session] {' · '.join(repeated)} — Read the body again if needed"
        )
    out.extend(tail)
    return "\n".join(out)


def dedup_list_block(
    block: str, seen: SessionSeen, prefix: str, keys: list[str] | None = None
) -> str:
    """Collapse ``- `` lines already shown into one line of their keys.

    ``keys`` gives each ``- `` line's key in order (the producer knows them);
    without it the text after the last ``→`` (or a backticked span in it) is
    used. Non-bullet lines (headers) stay so the reader keeps the folder to
    re-read from. If collapsing would not make the block shorter, the
    original block is returned (and the lines re-marked as seen now).
    """
    if not block:
        return block
    out: list[str] = []
    repeated: list[tuple[str, str]] = []
    given = list(keys or [])
    for line in block.splitlines():
        if not line.startswith("- "):
            out.append(line)
            continue
        if given:
            key = given.pop(0)
        else:
            key_src = line.rsplit("→", 1)[-1]
            found = re.search(r"`([^`]+)`", key_src)
            key = (found.group(1) if found else key_src).strip()
        if seen.fresh(f"{prefix}:{key}", line):
            out.append(line)
        else:
            repeated.append((key, line))
    if not repeated:
        return "\n".join(out)
    collapsed = "\n".join(
        out
        + [
            f"[same items as earlier this session] {' · '.join(k for k, _ in repeated)} — Read if needed"
        ]
    )
    if len(collapsed.encode("utf-8")) >= len(block.encode("utf-8")):
        for key, line in repeated:
            seen.mark(f"{prefix}:{key}", line)
        return block
    seen.stats["deduped"] += len(repeated)
    seen.stats["chars_saved"] += len(block) - len(collapsed)
    return collapsed


class ContextBudget:
    """One turn's budget. Inactive (pass-through) without a session ID or when switched off.

    Use it only on runtimes that can tell you when context was lost
    (compaction/resume/clear) so you can call :func:`reset`; otherwise a
    collapsed line may point at something the model no longer has.
    """

    def __init__(self, state_dir: Path | None, session_id: str, now: float | None = None) -> None:
        self.seen: SessionSeen | None = None
        if state_dir is None or not (session_id or "").strip() or env_off(ENV_OFF):
            return
        self.seen = SessionSeen(state_dir, session_id, now)

    @property
    def active(self) -> bool:
        return self.seen is not None

    def sections(self, block: str, paths: dict[str, str] | None = None) -> str:
        if self.seen is None:
            return block
        try:
            return dedup_sections(block, self.seen, paths)
        except Exception:  # noqa: BLE001 — fail open
            return block

    def list_block(self, block: str, prefix: str, keys: list[str] | None = None) -> str:
        if self.seen is None:
            return block
        try:
            return dedup_list_block(block, self.seen, prefix, keys)
        except Exception:  # noqa: BLE001 — fail open
            return block

    def save(self) -> None:
        if self.seen is not None:
            self.seen.save()


def reset(state_dir: Path, session_id: str) -> None:
    """Forget what this session has seen (call on compaction, resume, clear)."""
    if not (session_id or "").strip():
        return
    with contextlib.suppress(OSError):
        session_file(state_dir, session_id, "budget").unlink(missing_ok=True)
