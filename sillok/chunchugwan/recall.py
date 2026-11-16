"""Prompt-time recall over memory notes and past episodes (SQLite FTS5, stdlib only)."""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import sqlite3
import stat
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "3"
MAX_NOTE_BYTES = 512_000
HOOK_REFRESH_BUDGET_S = 0.25
HOOK_MIN_PROMPT_CHARS = 24
HOOK_MAX_LINES = 5
HOOK_MAX_BYTES = 900
ENV_OFF = "SILLOK_MEMORY_RECALL"
OPT_OUT_TAGS = ("[no-recall]", "[raw]", "[no-rag]")
NON_USER_MARKERS = (
    "[SYSTEM NOTIFICATION - NOT USER INPUT]",
    "<task-notification>",
    "<system-notification>",
    "This is an automated background-task event",
    "<agent-message",
    "[Subagent hand-back]",
)
AUTOMATION_PREFIXES = (
    "you are a ",
    "you are an ",
    "return strict json",
    "<command-",
    "caveat:",
    "<local-command",
)

KO_SUFFIXES = tuple(
    sorted(
        (
            "으로부터", "에서부터", "이라는", "에서는", "으로는", "에게서", "까지는", "부터는",
            "에서", "으로", "에게", "께서", "까지", "부터", "처럼", "보다", "이나", "하고", "이랑", "라는",
            "해줘", "해서", "하여", "하는", "하기", "하면", "했던", "되는", "된", "한", "할",
            "을", "를", "이", "가", "은", "는", "의", "에", "로", "와", "과", "도", "만", "랑", "나",
        ),
        key=len,
        reverse=True,
    )
)  # fmt: skip
STOPWORDS = frozenset(  # noqa: SIM905 — a word list reads better as text
    [
        "해줘",
        "해주세요",
        "하세요",
        "그리고",
        "그런데",
        "그래서",
        "이거",
        "이것",
        "저것",
        "그것",
        "우리",
        "지금",
        "다시",
        "정리",
        "확인",
        "작업",
        "관련",
        "대한",
        "위한",
        "통해",
        "하기",
        "하고",
        "있는",
        "없는",
        "같은",
        "경우",
        "내용",
        "부분",
        "사용",
        "진행",
        "해당",
        "기준",
        "중심",
        "방법",
        "이번",
        "오늘",
        "어제",
        "내일",
        "모두",
        "전체",
        "각각",
        "가장",
        "있다",
        "없다",
        "한다",
        "했다",
        "된다",
        "및",
        "등",
        "것",
        "수",
        "좀",
        "잘",
        "더",
        "또",
        "왜",
        "뭐",
        "어떻게",
        "무엇",
        "아래",
        "위의",
        "다음",
        "최근",
        "제대로",
        "적용",
        "고도화",
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "into",
        "your",
        "you",
        "are",
        "was",
        "were",
        "have",
        "has",
        "had",
        "not",
        "but",
        "can",
        "will",
        "what",
        "how",
        "why",
        "when",
        "please",
        "make",
        "sure",
        "using",
        "use",
        "about",
        "onto",
        "then",
        "than",
        "also",
        "just",
        "like",
        "more",
        "most",
        "only",
        "other",
        "some",
        "such",
    ]
)

_DDL = (
    "CREATE TABLE files(path TEXT PRIMARY KEY, mtime REAL, size INTEGER)",
    "CREATE VIRTUAL TABLE chunks USING fts5("
    " title, heading, body,"
    " cid UNINDEXED, source UNINDEXED, path UNINDEXED,"
    " line_start UNINDEXED, line_end UNINDEXED,"
    " ts UNINDEXED, session UNINDEXED, extra UNINDEXED, hash UNINDEXED,"
    " tokenize='unicode61 remove_diacritics 2')",
)

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE = re.compile(
    r"(?<!\d)(?:\+\d{1,3}[-. ]?)?0?\d{1,2}[-. ]\d{3,4}[-. ]\d{4}(?!\d)|(?<!\d)01\d\d{7,8}(?!\d)"
)
_LONG_TOKEN = re.compile(r"\b[A-Za-z0-9_+/=-]{32,}\b")
_SECRET = re.compile(
    r"(?i)(bearer\s+\S+|(?:api[-_]?key|token|password|secret|authorization)\s*[:=]\s*\S+|"
    r"\b(?:sk-ant-|sk-|ghp_|github_pat_|xox[bp]-)[A-Za-z0-9_-]+)"
)


# ── index ─────────────────────────────────────────────────────────────
def _schema(conn: sqlite3.Connection) -> str | None:
    try:
        row = conn.execute("SELECT v FROM meta WHERE k='schema'").fetchone()
    except sqlite3.OperationalError:
        return None
    return row[0] if row else None


def _ensure_schema(conn: sqlite3.Connection, observed: str | None) -> None:
    """Rebuild on a schema change — re-checked under the write lock so a
    concurrent session's fresh index is not dropped on a stale read."""
    if observed == SCHEMA_VERSION:
        return
    conn.execute("BEGIN IMMEDIATE")
    try:
        if _schema(conn) != SCHEMA_VERSION:
            for table in ("chunks", "files", "meta"):
                conn.execute(f"DROP TABLE IF EXISTS {table}")
            conn.execute("CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT)")
            for ddl in _DDL:
                conn.execute(ddl)
            conn.execute("INSERT INTO meta(k, v) VALUES('schema', ?)", (SCHEMA_VERSION,))
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def connect(path: Path, timeout: float = 5.0) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=timeout)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        _ensure_schema(conn, _schema(conn))
    except BaseException:
        conn.close()
        raise
    return conn


def _frontmatter(text: str) -> tuple[dict[str, str], int]:
    """Shallow front-matter parser → (fields, 1-based body start line); nested keys flattened."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, 1
    fm: dict[str, str] = {}
    for i, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return fm, i + 1
        m = re.match(r"^\s*([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m and m.group(1) not in fm:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return {}, 1


def chunk_note(path: Path) -> list[dict[str, Any]]:
    """One memory note → one chunk per heading path. Index files and superseded notes → []."""
    name = path.name
    if name in {"MEMORY.md", "README.md"} or name.startswith("_") or path.suffix != ".md":
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body_start = _frontmatter(text)
    if fm.get("status", "").lower() == "superseded":
        return []
    slug = fm.get("name") or path.stem
    title = f"{fm.get('description', '')} {slug.replace('_', ' ').replace('-', ' ')}".strip()
    lines = text.splitlines()
    chunks: list[dict[str, Any]] = []
    stack: list[tuple[int, str]] = []
    cur: dict[str, Any] = {"heading": "", "start": body_start, "buf": []}

    def flush(end_line: int) -> None:
        body = "\n".join(cur["buf"]).strip()
        if body or not chunks:
            chunks.append(
                {
                    "heading": cur["heading"],
                    "line_start": cur["start"],
                    "line_end": max(cur["start"], end_line),
                    "body": body[:1500],
                }
            )

    for no, line in enumerate(lines[body_start - 1 :], start=body_start):
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            flush(no - 1)
            level = len(m.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, m.group(2).strip()))
            cur = {"heading": " › ".join(t for _, t in stack), "start": no, "buf": []}
        else:
            cur["buf"].append(line)
    flush(len(lines))
    out = []
    for c in chunks:
        digest = hashlib.sha256(f"{title}\n{c['heading']}\n{c['body']}".encode()).hexdigest()[:16]
        out.append(
            {
                "cid": f"m:{name}:{c['line_start']}",
                "source": "memory",
                "path": name,
                "title": title,
                "heading": c["heading"],
                "body": c["body"],
                "line_start": c["line_start"],
                "line_end": c["line_end"],
                "ts": fm.get("updated") or fm.get("created") or "",
                "session": fm.get("originSessionId", ""),
                "extra": json.dumps({"type": fm.get("type", "")}, ensure_ascii=False),
                "hash": digest,
            }
        )
    return out


def _insert(conn: sqlite3.Connection, c: dict[str, Any]) -> None:
    conn.execute(
        "INSERT INTO chunks(title, heading, body, cid, source, path, line_start, line_end, ts, session, extra, hash) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            c["title"],
            c["heading"],
            c["body"],
            c["cid"],
            c["source"],
            c["path"],
            c["line_start"],
            c["line_end"],
            c["ts"],
            c["session"],
            c["extra"],
            c["hash"],
        ),
    )


def refresh_memory(
    conn: sqlite3.Connection, memory_dir: Path, budget_s: float | None = None
) -> dict[str, int]:
    """Re-chunk only notes whose (mtime, size) changed; regular files ≤ 512 KB only.

    With ``budget_s`` the remaining files are deferred to the next call —
    this bounds latency when called from a prompt hook.
    """
    t0 = time.monotonic()
    current: dict[str, tuple[float, int]] = {}
    if memory_dir.is_dir():
        for p in memory_dir.glob("*.md"):
            try:
                st = p.stat()
            except OSError:
                continue
            if stat.S_ISREG(st.st_mode) and st.st_size <= MAX_NOTE_BYTES:
                current[p.name] = (st.st_mtime, st.st_size)
    known = {
        r["path"]: (r["mtime"], r["size"])
        for r in conn.execute("SELECT path, mtime, size FROM files")
    }
    changed = [n for n, sig in current.items() if known.get(n) != sig]
    removed = [n for n in known if n not in current]
    if not changed and not removed:
        return {"changed": 0, "deferred": 0, "removed": 0, "files": len(current)}
    done = 0
    with conn:
        for n in removed:
            conn.execute("DELETE FROM chunks WHERE source='memory' AND path=?", (n,))
            conn.execute("DELETE FROM files WHERE path=?", (n,))
        for n in changed:
            if budget_s is not None and time.monotonic() - t0 > budget_s:
                break
            try:
                chunks = chunk_note(memory_dir / n)
            except (OSError, UnicodeError):
                continue
            conn.execute("DELETE FROM chunks WHERE source='memory' AND path=?", (n,))
            for c in chunks:
                _insert(conn, c)
            conn.execute(
                "INSERT OR REPLACE INTO files(path, mtime, size) VALUES(?,?,?)", (n, *current[n])
            )
            done += 1
    return {
        "changed": done,
        "deferred": len(changed) - done,
        "removed": len(removed),
        "files": len(current),
    }


def _clean_prompt(prompt: str) -> str:
    text = re.sub(r"<system-reminder>.*?</system-reminder>", " ", prompt, flags=re.S)
    text = re.sub(r"<[^>]{1,80}>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def eligible_episode(ep: dict[str, Any]) -> bool:
    """Human turns with ≥ 3 content terms; agent traffic and automation prompts excluded."""
    if ep.get("traffic") == "agent":
        return False
    head = (ep.get("prompt") or "").lstrip()[:400]
    if any(m in head for m in NON_USER_MARKERS) or head.lower().startswith(AUTOMATION_PREFIXES):
        return False
    return len(query_terms(_clean_prompt(ep.get("prompt") or "")[:600])) >= 3


def episode_chunk(ep: dict[str, Any]) -> dict[str, Any]:
    prompt = _clean_prompt(ep.get("prompt") or "")
    eid = (
        ep.get("episode_id")
        or hashlib.sha256(f"{ep.get('session')}|{ep.get('ts')}".encode()).hexdigest()[:16]
    )
    artifacts = [str(a) for a in (ep.get("artifacts") or [])[:3]]
    extra: dict[str, Any] = {
        "artifacts": artifacts,
        "corrected": bool(ep.get("corrected")),
        "runtime": ep.get("runtime") or "",
        "domain": ep.get("domain") or "",
    }
    body = prompt[:1200]
    if ep.get("correction_text"):
        body += " ‖ correction: " + _clean_prompt(str(ep["correction_text"]))[:300]
    body += " " + " ".join(artifacts)
    chunk = {
        "cid": f"e:{eid}",
        "source": "episode",
        "path": (artifacts or [""])[0],
        "title": prompt[:160],
        "heading": extra["domain"],
        "body": body,
        "line_start": 0,
        "line_end": 0,
        "ts": str(ep.get("ts") or ""),
        "session": str(ep.get("session") or ""),
        "extra": json.dumps(extra, ensure_ascii=False),
    }
    chunk["hash"] = hashlib.sha256(
        json.dumps(chunk, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()[:16]
    return chunk


def refresh_episodes(conn: sqlite3.Connection, episodes: Path) -> dict[str, Any]:
    """Sync the episode JSONL by episode ID (the file may be regenerated wholesale)."""
    if not episodes.is_file():
        return {"changed": 0, "removed": 0, "episodes": 0, "skipped": "missing"}
    st = episodes.stat()
    sig = f"{st.st_mtime}:{st.st_size}"
    row = conn.execute("SELECT v FROM meta WHERE k='episodes_sig'").fetchone()
    if row and row["v"] == sig:
        return {"changed": 0, "removed": 0, "episodes": None, "skipped": "unchanged"}
    wanted: dict[str, dict[str, Any]] = {}
    with episodes.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                ep = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(ep, dict) and eligible_episode(ep):
                c = episode_chunk(ep)
                wanted[c["cid"]] = c
    known = {
        r["cid"]: r["hash"]
        for r in conn.execute("SELECT cid, hash FROM chunks WHERE source='episode'")
    }
    changed = [cid for cid, c in wanted.items() if known.get(cid) != c["hash"]]
    removed = [cid for cid in known if cid not in wanted]
    with conn:
        for cid in removed + changed:
            conn.execute("DELETE FROM chunks WHERE source='episode' AND cid=?", (cid,))
        for cid in changed:
            _insert(conn, wanted[cid])
        conn.execute("INSERT OR REPLACE INTO meta(k, v) VALUES('episodes_sig', ?)", (sig,))
    return {
        "changed": len(changed),
        "removed": len(removed),
        "episodes": len(wanted),
        "skipped": "",
    }


# ── query ─────────────────────────────────────────────────────────────
def _strip_suffix(word: str) -> str:
    if not re.match(r"^[가-힣]", word):
        return word
    for suf in KO_SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 2:
            return word[: -len(suf)]
    return word


def query_terms(text: str, cap: int = 16) -> list[str]:
    """Content terms: Korean particles stripped, stopwords/short tokens/numbers dropped."""
    out: list[str] = []
    for raw in re.findall(r"[0-9A-Za-z가-힣][0-9A-Za-z가-힣_]*", text.lower()):
        for part in raw.split("_"):
            w = _strip_suffix(part)
            if w in STOPWORDS or w.isdigit():
                continue
            if re.match(r"^[가-힣]", w) and len(w) < 2:
                continue
            if re.match(r"^[0-9a-z]", w) and len(w) < 3:
                continue
            if w not in out:
                out.append(w)
            if len(out) >= cap:
                return out
    return out


def search(
    conn: sqlite3.Connection,
    text: str,
    k_mem: int = 3,
    k_epi: int = 2,
    exclude_session: str = "",
    min_terms: int = 2,
    require_head: bool = True,
    min_cover: float = 0.25,
    weights: tuple[float, float, float] = (4.0, 2.0, 1.0),
) -> dict[str, Any]:
    """Rank each source separately (episodes would otherwise crowd out notes).

    A hit must match ≥ ``min_terms`` terms (and ≥ ``min_cover`` of them) and,
    with ``require_head``, at least one in the title/heading — a body-only
    coincidence is not injected. The current session is excluded before the
    LIMIT so its own turns cannot fill the window.
    """
    terms = query_terms(text)
    result: dict[str, Any] = {"terms": terms, "memory": [], "episodes": []}
    if len(terms) < min_terms:
        return result
    fts = " OR ".join(f'"{t}"*' for t in terms)
    rows: list[sqlite3.Row] = []
    for source, k in (("memory", k_mem), ("episode", k_epi)):
        if k <= 0:
            continue
        rows += conn.execute(
            "SELECT cid, source, path, heading, title, body, line_start, line_end, ts, session, extra, "
            f"bm25(chunks, {float(weights[0])}, {float(weights[1])}, {float(weights[2])}) AS score "
            "FROM chunks WHERE chunks MATCH ? AND source = ? AND (? = '' OR session != ?) "
            "ORDER BY score LIMIT 150",
            (fts, source, exclude_session, exclude_session),
        ).fetchall()
    seen_paths: set[str] = set()
    seen_prompts: set[str] = set()
    pool: list[dict[str, Any]] = []
    for r in rows:
        head = f"{r['title']} {r['heading']}".lower()
        hay = f"{head} {r['body']}".lower()
        matched = [t for t in terms if t in hay]
        if len(matched) < max(min_terms, min_cover * len(terms)) or (
            require_head and not any(t in head for t in matched)
        ):
            continue
        if r["source"] == "memory":
            if len(result["memory"]) >= k_mem or r["path"] in seen_paths:
                continue
            seen_paths.add(r["path"])
            result["memory"].append(
                {
                    "path": r["path"],
                    "heading": r["heading"],
                    "title": r["title"],
                    "lines": [r["line_start"], r["line_end"]],
                    "matched": matched,
                    "score": round(r["score"], 3),
                }
            )
        else:
            if len(pool) >= 4 * k_epi:
                continue
            key = re.sub(r"\W+", "", r["title"])[:60]
            if key in seen_prompts:
                continue
            seen_prompts.add(key)
            extra = json.loads(r["extra"] or "{}")
            pool.append(
                {
                    "cid": r["cid"],
                    "ts": r["ts"][:10],
                    "prompt": r["title"],
                    "session": r["session"],
                    "artifacts": extra.get("artifacts", []),
                    "corrected": extra.get("corrected", False),
                    "runtime": extra.get("runtime", ""),
                    "matched": matched,
                    "score": round(r["score"], 3),
                }
            )
        if len(result["memory"]) >= k_mem and len(pool) >= 4 * k_epi:
            break
    # Episodes with an artifact path first: "→ path" is what a reader can reuse.
    result["episodes"] = sorted(pool, key=lambda e: not e["artifacts"])[: max(k_epi, 0)]
    return result


# ── render ────────────────────────────────────────────────────────────
def _short(text: str, n: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def redact(text: str) -> str:
    """Best-effort masking of secrets and contact details (not a guarantee).

    Recall lines enter another session's model context; previously pasted
    keys or contact details must not ride along.
    """
    text = _SECRET.sub("<secret>", text)
    text = _EMAIL.sub("<email>", text)
    text = _PHONE.sub("<phone>", text)
    return _LONG_TOKEN.sub("<redacted>", text)


def render_block(result: dict[str, Any], memory_dir: Path | None = None) -> str:
    """Paths plus one redacted line each — never note bodies or full prompts. ≤ 5 lines, ≤ 900 B."""
    lines: list[str] = []
    for m in result.get("memory", []):
        where = f" › {_short(redact(m['heading']), 24)}" if m.get("heading") else ""
        lines.append(f"- memory: {m['path']}{where} — {_short(redact(m['title']), 70)}")
    for e in result.get("episodes", []):
        art = e["artifacts"][0] if e.get("artifacts") else "no artifact"
        flag = " · was corrected" if e.get("corrected") else ""
        rt = f" · {e['runtime']}" if e.get("runtime") else ""
        lines.append(
            f'- past work {e["ts"]}{rt}: "{_short(redact(e["prompt"]), 44)}" → {art}{flag}'
        )
    if not lines:
        return ""
    folder = ""
    if memory_dir is not None:
        folder = " · notes in " + str(memory_dir).replace(str(Path.home()), "~", 1) + "/"
    head = f"## Recall (reference · read only if relevant{folder})"
    out: list[str] = []
    size = len(head.encode())
    for line in lines[:HOOK_MAX_LINES]:
        b = len(line.encode()) + 1
        if size + b > HOOK_MAX_BYTES:
            break
        out.append(line)
        size += b
    return head + "\n" + "\n".join(out) if out else ""


def log_exposure(path: Path, session_id: str, result: dict[str, Any]) -> None:
    """Append what was shown (note paths, episode IDs only) so 'shown then opened' can be measured."""
    row = {
        "ts": datetime.now(UTC).isoformat(timespec="seconds"),
        "session": hashlib.sha256(session_id.encode()).hexdigest()[:16] if session_id else "",
        "memory": [m["path"] for m in result.get("memory", [])],
        "episodes": [e.get("cid", "") for e in result.get("episodes", [])],
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def hook_block(
    prompt: str,
    *,
    db: Path,
    memory_dir: Path,
    session_id: str = "",
    exposure_log: Path | None = None,
) -> str:
    """Prompt-hook entry: returns a recall block or ''. Never raises.

    Skips short prompts (< 24 chars), slash commands, opt-out tags
    (``[no-recall]``, ``[raw]``, ``[no-rag]``) and non-user notifications.
    Off switch: ``SILLOK_MEMORY_RECALL=off``.
    """
    from sillok.sacho.state import env_off

    if env_off(ENV_OFF):
        return ""
    stripped = (prompt or "").strip()
    if len(stripped) < HOOK_MIN_PROMPT_CHARS or stripped.startswith("/"):
        return ""
    if any(tag in stripped.lower() for tag in OPT_OUT_TAGS) or any(
        m in stripped[:400] for m in NON_USER_MARKERS
    ):
        return ""
    try:
        conn = connect(db, timeout=0.3)
    except (sqlite3.Error, OSError):
        # OSError: the DB folder cannot be created (read-only/sandboxed FS,
        # a file in the way). Upstream caught only sqlite3.Error and the
        # hook raised.
        return ""
    try:
        with contextlib.suppress(sqlite3.Error):  # locked: recall from the previous index
            refresh_memory(conn, memory_dir, budget_s=HOOK_REFRESH_BUDGET_S)
        result = search(conn, stripped[:1500], exclude_session=session_id)
        block = render_block(result, memory_dir)
        if block and exposure_log is not None:
            log_exposure(exposure_log, session_id, result)
        return block
    except sqlite3.Error:
        return ""
    finally:
        conn.close()
