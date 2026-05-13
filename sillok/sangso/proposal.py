"""sillok.sangso.proposal — Proposal artifact dataclass and serialization."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from sillok.sangso.gates import GateResult


_PROPOSAL_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class Proposal:
    pack_id: str
    timestamp: datetime
    diff_source: Path
    gates: list[GateResult] = field(default_factory=list)

    @property
    def id(self) -> str:
        ts = self.timestamp.strftime("%Y%m%dT%H%M%SZ")
        return f"{ts}-{self.pack_id}"

    @property
    def upstream_passed(self) -> bool:
        return all(g.passed for g in self.gates)

    def to_markdown(self) -> str:
        """Render the proposal as a markdown artifact for human review."""
        lines: list[str] = []
        lines.append("---")
        lines.append(f'proposal_id: "{self.id}"')
        lines.append(f"pack_id: {self.pack_id}")
        lines.append(f"timestamp: {self.timestamp.isoformat()}")
        lines.append(f"diff_source: {self.diff_source}")
        lines.append(f"upstream_gates_passed: {str(self.upstream_passed).lower()}")
        lines.append(f"gate_count: {len(self.gates)}")
        lines.append("---")
        lines.append("")
        lines.append(f"# Proposal — `{self.pack_id}`")
        lines.append("")
        lines.append(f"> Generated {self.timestamp.isoformat()}")
        lines.append(f"> Diff source: `{self.diff_source}`")
        lines.append("")
        lines.append("## Gate Results")
        lines.append("")
        lines.append("| Gate | Passed | Summary |")
        lines.append("|---|:---:|---|")
        for g in self.gates:
            mark = "✅" if g.passed else "❌"
            summary = (g.summary or g.error or "").replace("|", "\\|")
            lines.append(f"| {g.gate} | {mark} | {summary} |")
        lines.append("")

        for g in self.gates:
            lines.append(f"### Gate — {g.gate}")
            lines.append("")
            lines.append(f"- **passed**: `{g.passed}`")
            lines.append(f"- **summary**: {g.summary}")
            if g.error:
                lines.append(f"- **error**: {g.error}")
            if g.details:
                lines.append("- **details**:")
                lines.append("")
                lines.append("```yaml")
                # Avoid dumping the unified_diff inline to keep the artifact compact;
                # extract it to a separate fenced block below.
                clean_details = {
                    k: v for k, v in g.details.items() if k != "unified_diff"
                }
                lines.append(yaml.safe_dump(clean_details, sort_keys=False, default_flow_style=False).rstrip())
                lines.append("```")
                lines.append("")

                if "unified_diff" in g.details:
                    lines.append("- **unified diff**:")
                    lines.append("")
                    lines.append("```diff")
                    lines.append(g.details["unified_diff"].rstrip())
                    lines.append("```")
                    lines.append("")
            lines.append("")

        lines.append("## How to apply")
        lines.append("")
        lines.append("`sillok.sangso accept` requires interactive `y/N` confirmation. There is no")
        lines.append("`--force` flag and no API endpoint for auto-merge. Run:")
        lines.append("")
        lines.append("```bash")
        lines.append(f"python -m sillok.sangso accept {self.id}")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def load(cls, path: Path) -> "ProposalSummary":
        """Load a proposal artifact (frontmatter only — gate results omitted)."""
        text = path.read_text(encoding="utf-8")
        m = _PROPOSAL_FRONTMATTER_RE.match(text)
        if not m:
            raise ValueError(f"no frontmatter in {path}")
        fm: dict[str, Any] = yaml.safe_load(m.group(1)) or {}
        ts_raw = fm.get("timestamp")
        if isinstance(ts_raw, datetime):
            timestamp = ts_raw
        elif isinstance(ts_raw, str):
            timestamp = datetime.fromisoformat(ts_raw)
        else:
            timestamp = None
        return ProposalSummary(
            artifact_path=path,
            id=fm.get("proposal_id", path.stem),
            pack_id=fm.get("pack_id", ""),
            timestamp=timestamp,
            diff_source=Path(fm["diff_source"]) if fm.get("diff_source") else None,
            upstream_passed=bool(fm.get("upstream_gates_passed", False)),
            gate_count=int(fm.get("gate_count", 0)),
        )


@dataclass
class ProposalSummary:
    artifact_path: Path
    id: str
    pack_id: str
    timestamp: datetime | None
    diff_source: Path | None
    upstream_passed: bool
    gate_count: int
