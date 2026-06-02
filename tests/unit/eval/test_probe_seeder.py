"""Unit tests for sillok.eval.probe_seeder — seed candidate probes from logs.

All conversation data here is synthetic; no real export is read.
"""

from __future__ import annotations

from sillok.eval import probe_seeder as ps


def _conversation(conv_id: str, first_user: str, n_messages: int) -> dict:
    messages = [{"role": "user", "text": first_user}]
    # pad with alternating roles to reach n_messages
    for i in range(n_messages - 1):
        role = "assistant" if i % 2 == 0 else "user"
        messages.append({"role": role, "text": f"msg {i}"})
    return {"id": conv_id, "messages": messages}


def test_deep_conversation_yields_unlabelled_stub() -> None:
    convs = [_conversation("c1", "how do I configure routing?", 12)]
    stubs = ps.seed_probes(convs, min_messages=10)
    assert len(stubs) == 1
    assert stubs[0].query == "how do I configure routing?"
    assert stubs[0].expected_pack is None  # human assigns the label
    assert stubs[0].source_id == "c1"


def test_shallow_conversation_is_skipped() -> None:
    convs = [_conversation("c1", "hi", 3)]
    assert ps.seed_probes(convs, min_messages=10) == []


def test_conversation_without_user_message_is_skipped() -> None:
    convs = [{"id": "c1", "messages": [{"role": "assistant", "text": "x"}] * 12}]
    assert ps.seed_probes(convs, min_messages=10) == []


def test_default_redactions_scrub_generic_pii() -> None:
    text = "email me at jane.doe@example.com or call 010-1234-5678 see https://x.io/p"
    out = ps.redact(text)
    assert "@example.com" not in out
    assert "010-1234-5678" not in out
    assert "https://x.io" not in out
    assert "⟨EMAIL⟩" in out and "⟨NUMBER⟩" in out and "⟨URL⟩" in out


def test_query_is_redacted_in_stub() -> None:
    convs = [_conversation("c1", "ping me at a@b.com about the plan", 11)]
    stubs = ps.seed_probes(convs, min_messages=10)
    assert "a@b.com" not in stubs[0].query
    assert "⟨EMAIL⟩" in stubs[0].query


def test_content_list_shape_is_supported() -> None:
    convs = [
        {
            "id": "c1",
            "messages": [
                {"role": "user", "content": [{"text": "part one"}, {"text": "part two"}]},
                *([{"role": "assistant", "text": "ok"}] * 10),
            ],
        }
    ]
    stubs = ps.seed_probes(convs, min_messages=10)
    assert stubs[0].query == "part one part two"


def test_query_truncation() -> None:
    long_q = "word " * 200
    convs = [_conversation("c1", long_q, 11)]
    stubs = ps.seed_probes(convs, min_messages=10, max_query_chars=50)
    assert len(stubs[0].query) <= 50


def test_no_personal_or_clinical_patterns_in_defaults() -> None:
    # Guardrail: defaults must carry only generic PII rules, never the
    # internal ancestor's clinical/domain patterns.
    blob = " ".join(r.pattern.pattern for r in ps.DEFAULT_REDACTIONS)
    for banned in ("op_", "mri_", "dx_", "rvef", "holter"):
        assert banned not in blob
