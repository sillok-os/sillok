"""sillok.kernel — wiring for the four kernel managers · experimental since 0.4.0.

=================  ===========================  ==========================
manager            question it answers          module
=================  ===========================  ==========================
work context       what work is this turn?      :mod:`sillok.sacho`
context budget     was this already shown?      :mod:`sillok.seungjeongwon`
memory recall      what did we learn before?    :mod:`sillok.chunchugwan`
playbook           which lessons fit this work? :mod:`sillok.gyeongyeon`
=================  ===========================  ==========================

Engine boundary test used to pick these four: *if you switch it off, does the
next turn's answer change?* Measurement of their effect is still open; every
manager has its own off switch and the playbook starts in shadow mode.

Run as a Claude Code hook: ``python -m sillok.kernel.hook --config kernel.json``.
"""

from __future__ import annotations

from typing import Any

__all__ = ["load_config", "prompt_turn", "session_start"]


def __getattr__(name: str) -> Any:
    # Lazy so that ``python -m sillok.kernel.hook`` does not import the module
    # twice (runpy warns when the package already imported it).
    if name in __all__:
        from . import hook

        return getattr(hook, name)
    raise AttributeError(name)
