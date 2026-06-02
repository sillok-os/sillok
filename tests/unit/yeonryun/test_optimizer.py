"""Unit tests for sillok.yeonryun.optimizer — pluggable optimization interface."""

from __future__ import annotations

from sillok.yeonryun import optimizer as opt


def test_mutation_optimizer_satisfies_protocol() -> None:
    assert isinstance(opt.MutationOptimizer(), opt.Optimizer)


def test_accepts_when_a_mutation_clears_threshold() -> None:
    # metric rewards any text containing "step by step".
    def metric(body: str) -> float:
        return 1.0 if "step by step" in body else 0.0

    proposal = opt.MutationOptimizer(accept_threshold=0.5).propose("seed", metric)
    assert proposal.accepted
    assert "step by step" in proposal.candidate
    assert proposal.uplift == 1.0


def test_rejects_when_no_mutation_improves() -> None:
    proposal = opt.MutationOptimizer().propose("seed", metric=lambda body: 0.5)
    assert not proposal.accepted
    assert proposal.candidate == "seed"
    assert proposal.uplift == 0.0
    assert "no mutation beat the seed" in proposal.rationale


def test_rejects_when_uplift_below_threshold() -> None:
    calls = {"n": 0}

    def metric(body: str) -> float:
        # seed scores 0.50; first mutation scores 0.52 (uplift 0.02 < 0.05).
        calls["n"] += 1
        return 0.50 if calls["n"] == 1 else 0.52

    proposal = opt.MutationOptimizer(accept_threshold=0.05).propose("seed", metric)
    assert not proposal.accepted
    assert proposal.candidate != "seed"
    assert "below threshold" in proposal.rationale


def test_custom_mutations() -> None:
    proposal = opt.MutationOptimizer(
        mutations=[lambda s: s + " EXTRA"],
        accept_threshold=0.0,
    ).propose("seed", metric=lambda body: float(len(body)))
    assert proposal.candidate == "seed EXTRA"
    assert proposal.accepted


def test_optimizer_is_dependency_free() -> None:
    # Guardrail: the optimizer module must not import an LLM/optimizer framework.
    import pathlib

    source = pathlib.Path(opt.__file__).read_text(encoding="utf-8")
    for banned in ("import dspy", "from dspy", "import openai", "import anthropic"):
        assert banned not in source
