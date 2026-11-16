"""sillok.gyeongyeon — per-work-type playbook with outcome counters (kernel learning loop) · experimental since 0.4.0.

*Gyeongyeon* (經筵) was the king's standing study session. This module keeps
lessons per work type, shows the top few when that work comes back, and
re-ranks them from the human's *next* input — the ACE pattern
(arXiv 2510.04618): grow context item by item with helpful/harmful counters
instead of rewriting it wholesale.

Loop per human turn::

    previous exposure  +  this input  →  correction? harmful+1 : accept? helpful+1
    this turn's work type  →  top-k by Beta mean (h+1)/(h+x+2)  →  block (≤ 900 B)

* counted once per session × item × outcome (a run of "go" cannot inflate it);
* ``shadow`` mode shows nothing and writes control counters ``sh``/``sx``;
  ``auto`` shows the block and writes treatment counters ``h``/``x`` — run
  shadow first, compare, then switch (``SILLOK_PLAYBOOK_MODE=off|shadow|auto``);
* :meth:`Playbook.promote_candidates` lists items helpful in ≥ 3 distinct
  sessions with no harm — promotion into a rule or test stays a human decision.

Items are yours to supply (``{"id", "work_type", "title", "path"}``); no
prompt text or raw session ID is stored.
"""

from __future__ import annotations

from .playbook import ACCEPT, CORRECTION, Playbook, classify

__all__ = ["ACCEPT", "CORRECTION", "Playbook", "classify"]
