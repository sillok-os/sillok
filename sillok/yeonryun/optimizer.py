# SPDX-License-Identifier: Apache-2.0
"""sillok.yeonryun.optimizer — prompt/pack optimization interface.

The auto-growth loop can, in principle, *improve* a pack body — not just promote
or gap-detect it. That improvement step is intentionally pluggable: the heavy
machinery (e.g. a DSPy / GEPA reflective optimizer) lives behind a small,
dependency-free :class:`Optimizer` protocol so the core package stays
provider-neutral (no LLM/optimizer-framework hard dependency).

This module ships:

- :class:`Optimizer` — the protocol an optimizer implements: given a ``seed``
  string and a ``metric`` callable, return an :class:`OptimizationProposal`.
- :class:`OptimizationProposal` — a candidate plus its measured uplift and an
  ``accepted`` flag. **Proposal-only**: producing a proposal never applies it —
  the caller (or ``sillok.sangso``) decides, mirroring the governance gates.
- :class:`MutationOptimizer` — a dependency-free reference implementation that
  tries a pool of generic textual mutations and keeps the best by ``metric``.

A DSPy/GEPA-backed optimizer would implement the same protocol and slot in
without any change to callers.

Example::

    from sillok.yeonryun.optimizer import MutationOptimizer

    opt = MutationOptimizer(accept_threshold=0.05)
    proposal = opt.propose(seed_prompt, metric=lambda body: golden_pass_rate(body))
    if proposal.accepted:
        ...  # route to a sangso proposal — never auto-apply
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

#: Generic, provider-neutral prompt mutations (seed -> variant). These are
#: deliberately broad prompt-hygiene edits, not domain-specific rewrites.
DEFAULT_MUTATIONS: tuple[Callable[[str], str], ...] = (
    lambda seed: f"{seed}\n\nBe concise and specific.",
    lambda seed: f"{seed}\n\nThink step by step before answering.",
    lambda seed: f"{seed}\n\nCite your sources where relevant.",
    lambda seed: f"You are an expert assistant.\n\n{seed}",
)


@dataclass(frozen=True)
class OptimizationProposal:
    """A candidate revision of ``seed`` with its measured uplift."""

    seed: str
    candidate: str
    seed_score: float
    candidate_score: float
    accepted: bool
    rationale: str = ""

    @property
    def uplift(self) -> float:
        return self.candidate_score - self.seed_score


@runtime_checkable
class Optimizer(Protocol):
    """Protocol for a pluggable prompt/pack optimizer (DSPy/GEPA, etc.)."""

    def propose(self, seed: str, metric: Callable[[str], float]) -> OptimizationProposal: ...


class MutationOptimizer:
    """Dependency-free reference :class:`Optimizer`.

    Evaluates the seed and each mutation with ``metric`` and proposes the best.
    The proposal is ``accepted`` only when its uplift clears ``accept_threshold``
    (and it actually differs from the seed).
    """

    def __init__(
        self,
        mutations: Sequence[Callable[[str], str]] | None = None,
        *,
        accept_threshold: float = 0.05,
    ) -> None:
        self.mutations: tuple[Callable[[str], str], ...] = (
            tuple(mutations) if mutations is not None else DEFAULT_MUTATIONS
        )
        self.accept_threshold = accept_threshold

    def propose(self, seed: str, metric: Callable[[str], float]) -> OptimizationProposal:
        seed_score = metric(seed)
        best_candidate, best_score = seed, seed_score
        for mutate in self.mutations:
            candidate = mutate(seed)
            score = metric(candidate)
            if score > best_score:
                best_candidate, best_score = candidate, score

        uplift = best_score - seed_score
        accepted = best_candidate != seed and uplift >= self.accept_threshold
        if accepted:
            rationale = (
                f"best mutation cleared threshold (uplift {uplift:+.4f} >= {self.accept_threshold})"
            )
        elif best_candidate == seed:
            rationale = "no mutation beat the seed"
        else:
            rationale = f"best uplift {uplift:+.4f} below threshold {self.accept_threshold}"
        return OptimizationProposal(
            seed=seed,
            candidate=best_candidate,
            seed_score=seed_score,
            candidate_score=best_score,
            accepted=accepted,
            rationale=rationale,
        )
