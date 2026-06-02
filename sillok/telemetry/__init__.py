"""sillok.telemetry — telemetry write path.

Ships the schema-enforced write-gate (:mod:`sillok.telemetry.gate`), which
validates every row against ``sillok.schemas.telemetry`` before append so the
eval / self-improvement corpus never ingests a malformed row.
"""

from __future__ import annotations

from .gate import validate_legacy, validate_v2, write_legacy, write_v2

__all__: list[str] = [
    "validate_v2",
    "validate_legacy",
    "write_v2",
    "write_legacy",
]
