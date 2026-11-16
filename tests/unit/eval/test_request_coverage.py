"""Request coverage — numbered items in the request must be visible in the final answer."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from sillok.eval.request_coverage import SELF_TEST_CASES, enumerated_count, missing_items, stop_hook


@pytest.mark.parametrize(("prompt", "answer", "want"), SELF_TEST_CASES)
def test_cases(prompt: str, answer: str, want: list[int]) -> None:
    assert missing_items(prompt, answer) == want


def test_enumeration_bounds() -> None:
    assert enumerated_count("1. only one") == 0
    assert enumerated_count(" ".join(f"{i}. x" for i in range(1, 22))) == 0  # > 20
    assert enumerated_count("1) a 2) b 3) c") == 3


def _transcript(tmp_path: Path, prompt: str, answer: str, *, meta_after: bool = False) -> Path:
    rows = [
        {"type": "user", "message": {"content": "earlier question"}},
        {
            "type": "assistant",
            "message": {"id": "m0", "content": [{"type": "text", "text": "earlier answer"}]},
        },
        {"type": "user", "message": {"content": prompt}},
        {
            "type": "assistant",
            "message": {"id": "m1", "content": [{"type": "text", "text": "working…"}]},
        },
        {"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}},
        {
            "type": "assistant",
            "message": {"id": "m2", "content": [{"type": "text", "text": answer}]},
        },
    ]
    if meta_after:
        rows.append({"type": "user", "isMeta": True, "message": {"content": "1. a 2. b 3. c"}})
    path = tmp_path / "t.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    return path


def test_stop_hook_blocks_once_with_missing_numbers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SILLOK_REQUEST_COVERAGE", raising=False)
    path = _transcript(
        tmp_path,
        "1. fix the table 2. add the chart 3. deploy",
        "1. fixed\n2. added",
        meta_after=True,
    )
    decision = stop_hook({"transcript_path": str(path)})
    assert decision and decision["decision"] == "block" and "item(s) 3" in decision["reason"]
    assert stop_hook({"transcript_path": str(path), "stop_hook_active": True}) is None


def test_stop_hook_skips_follow_ups_and_off_switch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _transcript(tmp_path, "go : 1. commit 2. deploy", "committed")
    assert stop_hook({"transcript_path": str(path)}) is None
    path = _transcript(tmp_path, "1. a 2. b", "only a")
    monkeypatch.setenv("SILLOK_REQUEST_COVERAGE", "off")
    assert stop_hook({"transcript_path": str(path)}) is None


def test_cli_prints_decision_and_always_exits_zero(tmp_path: Path) -> None:
    path = _transcript(tmp_path, "1. a 2. b", "1. a done")
    proc = subprocess.run(
        [sys.executable, "-m", "sillok.eval.request_coverage"],
        input=json.dumps({"transcript_path": str(path)}),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0 and json.loads(proc.stdout)["decision"] == "block"
    bad = subprocess.run(
        [sys.executable, "-m", "sillok.eval.request_coverage"],
        input="not json",
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad.returncode == 0 and bad.stdout == ""
