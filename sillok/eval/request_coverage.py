"""Request coverage — did the final answer address every numbered item the human asked for?

The most frequent correction in the upstream harness's six-month audit was
*omission*: a request listed items 1..N and the answer quietly covered fewer.
This check is structural, not semantic — it only asks whether each number
(or an ``N/N`` tally) is *visible* in the final answer. A Stop hook can then
send the turn back **once** with the missing numbers; a second stop always
passes, so there is no loop.

Conservative by design (false alarms cost more than misses):

* only a gap-free 1..N list with 2 ≤ N ≤ 20 counts (``2. … 5. …`` is ignored);
* decimals and years (``0.18.2)``, ``2026.``) are not items;
* follow-ups that paste a previous decision list (``go``, ``ok``, ``continue``, …)
  and empty answers (interrupted turns) are skipped.

CLI (Claude Code Stop hook payload on stdin)::

    python -m sillok.eval.request_coverage            # prints {"decision": "block", ...} or nothing
    python -m sillok.eval.request_coverage --self-test

Off switch: ``SILLOK_REQUEST_COVERAGE=off``.
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

MAX_ITEMS = 20
ENV_OFF = "SILLOK_REQUEST_COVERAGE"
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮"
# "1. ", "2) ", "(3) ", "4） " — preceded by start/space/punctuation, followed by text.
ENUM_RE = re.compile(r"(?:^|[\s;:,(（\[])\(?(\d{1,2})[.)）．]\s*(?=\S)")
SKIP_PREFIX_RE = re.compile(
    r"^\s*(?:go\b|ok\b|okay\b|yes\b|continue\b|keep going|lgtm\b|진행\b|계속\b|네\b|예\b|ㄱ\b|\[pm\]|\[Request interrupted)",
    re.IGNORECASE,
)
INJECTED_PREFIXES = (
    "<local-command",
    "<command-name",
    "<bash-input",
    "<bash-stdout",
    "<bash-stderr",
    "Caveat:",
    "<task-notification",
    "<system-reminder",
    "<teammate-message",
    "<system-warning",
    "This session is being continued from a previous conversation",
)


def enumerated_count(prompt: str) -> int:
    """N when the prompt numbers its items 1..N without gaps (2 ≤ N ≤ 20), else 0."""
    nums = {int(m.group(1)) for m in ENUM_RE.finditer(prompt)}
    nums |= {CIRCLED.index(ch) + 1 for ch in prompt if ch in CIRCLED}
    if not nums:
        return 0
    n = max(nums)
    if n < 2 or n > MAX_ITEMS or set(range(1, n + 1)) - nums:
        return 0
    return n


def _mentioned(answer: str, k: int, n: int) -> bool:
    if re.search(rf"(?<![\d/]){n}\s*/\s*{n}(?![\d/])", answer):  # "3/3" tally
        return True
    if k <= len(CIRCLED) and CIRCLED[k - 1] in answer:
        return True
    patterns = (
        rf"(?m)^\s*(?:#+\s*|\*\*|[-*]\s+)?\(?{k}[.)）．]\s",  # line head "1. ", "**1.", "### 1.", "- 1."
        rf"\|\s*{k}\s*\|",  # first table cell
        rf"(?<![\d.]){k}번",  # Korean "2번"
        rf"(?i)\b(?:items?|steps?|points?)\s+(?:\d{{1,2}}\s*(?:,|and|&|/)\s*)*{k}\b",  # "item 2", "items 1 and 3"
        rf"(?i)(?:\bno\.?\s*|#){k}\b",  # "no. 2", "#2"
        rf"\({k}\)",  # "(2)"
        rf"(?<![\d.]){k}[.)]\s*(?=\S)",  # inline "2) ", "2. "
    )
    return any(re.search(p, answer) for p in patterns)


def missing_items(prompt: str, answer: str) -> list[int]:
    """Numbers 1..N from the prompt that the answer never mentions ([] when not applicable)."""
    n = enumerated_count(prompt)
    if not n or not answer.strip():
        return []
    return [k for k in range(1, n + 1) if not _mentioned(answer, k, n)]


def _text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return ""
        return "\n".join(
            b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def last_turn(transcript_path: str) -> tuple[str, str]:
    """(last human prompt, text of the last assistant message after it) from a Claude Code JSONL transcript."""
    prompt = ""
    answers: dict[str, list[str]] = {}
    last_id = ""
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(ev, dict):
                    continue
                kind = ev.get("type")
                if kind == "user":
                    if ev.get("isMeta") or ev.get("isSidechain"):
                        continue
                    text = _text_of((ev.get("message") or {}).get("content"))
                    if not text.strip() or text.lstrip().startswith(INJECTED_PREFIXES):
                        continue
                    prompt, answers, last_id = text, {}, ""
                elif kind == "assistant" and prompt and not ev.get("isSidechain"):
                    msg = ev.get("message") or {}
                    mid = msg.get("id") or ev.get("uuid") or ""
                    texts = [
                        b.get("text", "")
                        for b in (msg.get("content") or [])
                        if isinstance(b, dict) and b.get("type") == "text"
                    ]
                    if texts:
                        answers.setdefault(mid, []).extend(texts)
                        last_id = mid
    except OSError:
        return "", ""
    return prompt, "\n".join(answers.get(last_id, []))


def reason_text(missing: list[int], n: int) -> str:
    nums = ", ".join(str(k) for k in missing)
    return (
        f"[request-coverage] The request listed {n} numbered items (1–{n}) but the final answer does not show item(s) {nums}. "
        "Close with one line per number (done / not done / reason / where). If already covered, just add the numbers. "
        f"(structural check · sent back once · off: {ENV_OFF}=off)"
    )


def stop_hook(payload: dict[str, Any]) -> dict[str, str] | None:
    """Claude Code Stop hook decision, or None to let the turn end."""
    if os.environ.get(ENV_OFF, "").strip().lower() in {"off", "0", "false", "no"}:
        return None
    if not isinstance(payload, dict) or payload.get("stop_hook_active"):
        return None
    path = payload.get("transcript_path") or ""
    if not path or not os.path.isfile(path):
        return None
    prompt, answer = last_turn(path)
    if not prompt or SKIP_PREFIX_RE.match(prompt):
        return None
    missing = missing_items(prompt, answer)
    if not missing:
        return None
    return {"decision": "block", "reason": reason_text(missing, enumerated_count(prompt))}


SELF_TEST_CASES: tuple[tuple[str, str, list[int]], ...] = (
    ("1. fix the table 2. add the chart 3. deploy", "1. Table fixed.\n2. Chart added.", [3]),
    (
        "1. fix the table 2. add the chart 3. deploy",
        "**1.** table ✅ **2.** chart ✅ **3.** deploy held (permission)",
        [],
    ),
    ("① table ② chart ③ deploy", "Handled 3/3.", []),
    ("(1) table (2) chart", "| 1 | table | done |\n| 2 | chart | done |", []),
    ("after installing v0.18.2) check 2026. November", "done", []),
    ("2. only this 5. only that", "done", []),
    ("1. A 2. B", "", []),
    ("1. A 2. B 3. C 4. D", "Items 1 and 3 are done, item 2 is on hold, #4 has a reason noted", []),
)


def self_test() -> int:
    ok = True
    for prompt, answer, want in SELF_TEST_CASES:
        got = missing_items(prompt, answer)
        if got != want:
            ok = False
            print(f"FAIL {prompt[:30]!r} → {got} (want {want})")
    print("self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--self-test" in argv:
        return self_test()
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    decision = stop_hook(payload)
    if decision:
        print(json.dumps(decision, ensure_ascii=False))
    return 0  # never fail the session


if __name__ == "__main__":
    sys.exit(main())
