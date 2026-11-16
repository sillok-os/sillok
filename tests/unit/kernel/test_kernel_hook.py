"""Kernel hook — the four managers wired as one Claude Code prompt hook."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from sillok.kernel import load_config, prompt_turn, session_start

PROFILES = [
    {
        "id": "report",
        "label": "Reporting",
        "action_signals": {"path_prefixes": ["docs/reports/"]},
        "guide_refs": ["docs/sop/report.md"],
    }
]
ITEMS = [
    {
        "id": "tables",
        "work_type": "report",
        "title": "Compare options in a table, with the recommended option first",
        "path": "lessons/tables.md",
    },
    {
        "id": "numbers",
        "work_type": "report",
        "title": "Answer every numbered request item and tally N/N at the end",
        "path": "lessons/numbers.md",
    },
]
NOTE = "---\nname: churn-report\ndescription: Quarterly churn report conventions for the board\n---\n# Board\nLead with the decision.\n"
Q = "draft the quarterly churn report for the board meeting"


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "SILLOK_PLAYBOOK_MODE",
        "SILLOK_WORK_CONTEXT",
        "SILLOK_MEMORY_RECALL",
        "SILLOK_CONTEXT_BUDGET",
        "SILLOK_KERNEL_CONFIG",
    ):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture()
def config(tmp_path: Path) -> Path:
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "churn-report.md").write_text(NOTE, encoding="utf-8")
    (tmp_path / "profiles.json").write_text(json.dumps(PROFILES), encoding="utf-8")
    (tmp_path / "items.json").write_text(json.dumps(ITEMS), encoding="utf-8")
    cfg = {
        "state_dir": "state",
        "profiles": "profiles.json",
        "playbook": {"mode": "auto", "items": "items.json"},
        "recall": {"memory_dir": "memory", "db": "recall.db", "exposure_log": "exposure.jsonl"},
    }
    path = tmp_path / "kernel.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def test_load_config_resolves_relative_paths(config: Path) -> None:
    cfg = load_config(config)
    assert cfg["state_dir"] == config.parent / "state"
    assert cfg["profiles"][0]["id"] == "report"
    assert cfg["recall"]["db"] == config.parent / "recall.db"
    assert load_config(config.parent / "missing.json") == {}


def test_turns_compose_then_collapse_then_reset_after_compaction(config: Path) -> None:
    cfg = load_config(config)
    first = prompt_turn({"session_id": "s1", "prompt": Q, "work_type": "report"}, cfg, now=100.0)
    assert "## Lessons for Reporting" in first and "## Recall" in first
    assert "[work context]" not in first  # explicitly named work needs no reminder line

    second = prompt_turn({"session_id": "s1", "prompt": Q}, cfg, now=200.0)
    assert second.startswith("[work context] Reporting (inherited) · guide: docs/sop/report.md")
    assert "Compare options in a table" not in second  # same lessons → collapsed to a pointer
    assert "tables.md" in second

    session_start({"hook_event_name": "SessionStart", "source": "compact", "session_id": "s1"}, cfg)
    third = prompt_turn({"session_id": "s1", "prompt": Q}, cfg, now=300.0)
    assert "Compare options in a table" in third


def test_empty_config_is_silent(tmp_path: Path) -> None:
    assert prompt_turn({"session_id": "s1", "prompt": Q}, {}, now=1.0) == ""


def test_cli_emits_additional_context_and_survives_garbage(config: Path) -> None:
    payload = {
        "hook_event_name": "UserPromptSubmit",
        "session_id": "s9",
        "prompt": Q,
        "work_type": "report",
    }
    run = [sys.executable, "-m", "sillok.kernel.hook", "--config", str(config)]
    proc = subprocess.run(
        run, input=json.dumps(payload), capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "UserPromptSubmit" and "## Recall" in out["additionalContext"]
    bad = subprocess.run(run, input="{not json", capture_output=True, text=True, check=False)
    assert bad.returncode == 0 and bad.stdout == ""


def test_profile_triggers_name_the_work_when_no_router_does(config: Path) -> None:
    cfg = load_config(config)
    cfg["profiles"] = [{**PROFILES[0], "triggers": ["churn report"]}]
    first = prompt_turn({"session_id": "s2", "prompt": Q}, cfg, now=100.0)
    assert "## Lessons for Reporting" in first and "[work context]" not in first
    follow = prompt_turn({"session_id": "s2", "prompt": "go"}, cfg, now=160.0)
    assert follow.startswith("[work context] Reporting (inherited)")
