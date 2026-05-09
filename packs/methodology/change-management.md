---
id: change-management
title: Change Management Pack — ADKAR · Kotter · Team Topologies · MVT
category: domain
sub_category: methodology
license: Apache-2.0
license_atoms: CC-BY-4.0
status: starter
version: 0.1.0a1
references:
  - "Prosci ADKAR Model — Awareness/Desire/Knowledge/Ability/Reinforcement"
  - "Kotter — Leading Change (1996, 8-step)"
  - "Skelton & Pais — Team Topologies (2019)"
  - "McKinsey 7-S Framework — Hard 3 + Soft 4"
top10_features: ["#3 typed registry", "#5 multi-tenant overlay"]

# agentskills.io v0.9 capability discovery (additive — docs/architecture/frontmatter-compatibility.md)
name: change-management
description: Change management — ADKAR weakest-link, Kotter 8-step, Team Topologies 4 types, MVT for early-stage.
capabilities:
  - run-adkar-diagnosis
  - plan-kotter-8-step
  - design-team-topologies
  - build-mvt-canvas
triggers:
  - "[change]"
  - "[cm]"
  - "[adkar]"
  - "ADKAR"
  - "Kotter"
  - "Team Topologies"
  - "변화 관리"
  - "조직 전환"
  - "AX 전환"
---

# Change Management Pack

> 조직 변화·팀 재설계·AI 전환 같은 "사람의 변화가 결과를 결정하는" 과업에 적용.
> 근거: Prosci ADKAR · Kotter 8-step · Team Topologies 4 Types · McKinsey 7-S.

## Boundaries

| Concern | Pack |
|-------|-------|
| **People-change management** (ADKAR/Kotter/Team Topologies) | **This pack** |
| PM lifecycle issues/releases | `pm-enhanced` |
| Organization maturity / competency | (separate competency pack) |
| Audit-style 5-Lens diagnostics | `consulting-*-audit` |

## Trigger signals

- **Explicit**: `[change]`, `[cm]`, `[adkar]`, `[mvt]`
- **Contains**: `change management`, `변화 관리`, `ADKAR`, `Kotter`, `Team Topologies`, `조직 전환`, `AX 전환`, `DX 전환`, `재편`, `resistance`, `readiness`, `stream-aligned team`, `enabling team`, `platform team`, `complicated-subsystem team`, `minimum viable team`, `최소 팀`, `핵심 최소 인원`, `원격근무 팀`, `remote-first team`, `분산 팀 OKR`

## M1 — Prosci ADKAR (individual-level change model)

변화는 조직 단위가 아니라 **개인 단위**로 일어난다. 5단계를 개인 × 단계 매트릭스로 관리.

| Stage | Question | Intervention |
|-----|------|---------|
| **A** Awareness | "Why must we change?" | Burning platform memo · town hall · 1-line rationale |
| **D** Desire | "Why must **I** change?" (accepted) | WIIFM · stakeholder benefit table · resistance scripts |
| **K** Knowledge | "What must I do?" | Capability matrix · formal training · reference docs |
| **A** Ability | "Can I actually do it?" | Practice · coaching · psychological safety · sandbox |
| **R** Reinforcement | "Can it last?" | KPIs · incentives · repeat measurement · regression checklist |

### Diagnostic checklist

```markdown
## ADKAR diagnostic — {change name} / {date}

| Group | A | D | K | A | R | Weakest link | Next intervention |
|---------|:-:|:-:|:-:|:-:|:-:|---------|---------|
| {Group 1} | 4 | 3 | 2 | 1 | 0 | Ability | Coaching program |
| {Group 2} | ... |
```

Score 0-5. **Solve only the weakest link**. Reinforcing later stages while bottlenecked at earlier stages has no effect.

## M2 — Kotter 8-Step (organization-level change process)

| # | Step | Core deliverable |
|:-:|------|---------|
| 1 | Create Urgency | Burning platform story + data |
| 2 | Build Guiding Coalition | Change-driving team of 7-10 (authority · trust · diversity) |
| 3 | Form Strategic Vision | 1-sentence vision + 3-5 initiatives |
| 4 | Enlist Volunteer Army | Broad communication + participation |
| 5 | Enable Action by Removing Barriers | Process / structure / system constraints removed |
| 6 | Generate Short-Term Wins | 3 visible wins within 6 months |
| 7 | Sustain Acceleration | Don't rest on victories — chain to next change |
| 8 | Institute Change | Anchor in culture (hiring · evaluation · storytelling) |

### ADKAR ↔ Kotter mapping

| Kotter | ADKAR |
|--------|-------|
| 1, 2, 3 | Awareness |
| 4 | Desire |
| 5 (partial) | Knowledge, Ability |
| 6, 7 | Reinforcement (early) |
| 8 | Reinforcement (anchored) |

## M3 — Team Topologies (4 team types)

소프트웨어/AI 조직 재설계 시 팀 유형을 먼저 정하고 그 위에 변화 관리 얹기.

| Type | Purpose | Example |
|-----|------|------|
| **Stream-aligned** | Aligned to value flow (user/product stream) | Product team |
| **Enabling** | Drives capability transformation in other teams | DevEx · AI adoption team |
| **Complicated-Subsystem** | Isolates highly specialized domains | ML platform · cryptography |
| **Platform** | Self-service infrastructure for other teams | Cloud infra · internal dev portal |

### Interaction modes (3)

| Mode | When | Duration |
|-----|------|-----|
| **Collaboration** | Discovery · high uncertainty | Short-term (1-3 months) |
| **X-as-a-Service** | Formalized dependency | Long-term |
| **Facilitating** | One team teaches another | Short-term → transitions to X-as-a-Service |

### AI transformation default mapping

- **AI Enabling Team**: facilitates Claude Code · prompt engineering · RAG adoption in each Stream-aligned team
- **AI Platform Team**: provides MCP server · model gateway · eval framework as X-as-a-Service
- **AI Complicated-Subsystem Team**: handles fine-tuning · agent orchestration high-difficulty domains

## M4 — McKinsey 7-S (current-state diagnosis, optional)

Hard 3 (Strategy · Structure · Systems) + Soft 4 (Style · Staff · Skills · Shared Values) — used in AS-IS / TO-BE comparisons.

```
| Element | AS-IS | TO-BE | Gap | Intervention |
|------|-------|-------|-----|-----|
| Strategy    | ...
| Structure   | ...
| Systems     | ...
| Style       | ...
| Staff       | ...
| Skills      | ...
| Shared Values | ...
```

## M5 — Minimum Viable Team + OKR for Remote-first Early-stage

> **Boundary**: this module applies to **early-stage startup · new product team · remote-first** only.
> SAFe ART scale (50+ people) → use `safe-agile-delivery`.
> Existing-org reorg → use M3 Team Topologies above.

### 5.1 MVT Canvas

**Principles**:
- **4-6 role ceiling**: more than that, coordination cost > marginal capability
- **1 role = 1 OKR owner**: shared KR ownership prohibited (responsibility dilution)
- **FTE / contractor mix allowed** + explicit boundary (legal counsel recommended)
- **Time-zone rotation rule** explicit (≥4 hours overlap or asynchronous transition)

**Standard canvas**:

| Role | Primary responsibility | OKR KR count | Employment | Hours/week | Time zone |
|---|---|---|---|---|---|
| **Product Owner** | Vision · roadmap · priority | 1-2 | FTE | 40h | Main TZ |
| **Build Lead** | Product/service implementation | 1-2 | FTE or full-time contractor | 40h | Main TZ |
| **Content / Curation Lead** | Domain content quality | 1 | FTE or part-time | 20-40h | Flexible |
| **Community / Ops Lead** | User · customer · ops | 1 | FTE or part-time | 20-40h | User TZ |
| **Data / Growth Lead** (optional) | Measurement · experiments · insights | 1 | Contractor or part-time | 10-20h | Asynchronous |
| **Admin / Finance** (optional) | Legal · accounting · contracts | 0 (supporting) | Contractor | 5-10h | Asynchronous |

**Role-merge patterns** (when staffing is short):
- Product + Community (most common in earliest stage)
- Build + Data (technical-heavy services)
- Content + Community (content-heavy services)

### 5.2 Remote-first ceremony stack

**Principle**: synchronous meetings ≤ 1/week, otherwise async. Quarterly offsite restores relational capital.

| Ceremony | Cadence | Format | Max time | Tool |
|---|---|---|---|---|
| Async daily standup | Daily | Text (3 lines: yesterday · today · blocker) | 10 min compose | Slack · Notion |
| Weekly sync | 1/week | Sync video | 45 min | Zoom · Meet |
| OKR review | Bi-weekly | Async doc + 30 min sync | 30 min | Notion · Linear |
| Quarterly planning | Quarterly | Offsite 2 days (or online 2 days) | 2 days | Free |
| Quarterly retro | Quarterly | Offsite-linked (0.5 day) | 4h | Miro · Notion |
| 1:1 | Bi-weekly | Sync video | 30 min | Zoom · Meet |

**Time-zone rotation example**:
- All-overlap window: Tue/Thu 10:00-14:00 KST
- Mon/Wed/Fri: async only (no meetings except blockers)

### 5.3 OKR mapping to MVT

**Principle**: ≤ 2 KRs per role (avoid OKR bloat). Quarter OKR = 1-2 Objectives + 1-2 KRs/role = 4-8 total KRs.

```
## Q{N} OKR

### Objective 1: {service core outcome}
- KR1.1 (owner: Product Owner) — {measurable target}
- KR1.2 (owner: Build Lead) — {measurable target}

### Objective 2: {customer/community core outcome}
- KR2.1 (owner: Content Lead) — {measurable target}
- KR2.2 (owner: Community Lead) — {measurable target}
- KR2.3 (owner: Data Lead) — {measurable target}
```

**KR quality bar**:
- Number-bearing (target value · baseline · deadline)
- Measurable within one quarter
- No serial dependency between KRs (parallel-executable)

### 5.4 Exit criteria (MVT → formal organization transition)

**3 of 5 met → consider team expansion**:

| Criterion | Threshold |
|---|---|
| Monthly recurring revenue (MRR) | ≥ $20k or annual equivalent $240k |
| Monthly active users (MAU) | Target segment ≥ 1,000 or community ≥ 500 |
| Burnout indicator | Last 4 weeks: 2+ roles with overtime > 10h/week |
| Cumulative OKR achievement | 3 quarters in a row ≥ 70% |
| Product/service feedback loop | NPS ≥ 40 or 30-day retention ≥ 40% |

**Expansion priority**:
1. Burnout met → first secure coverage (contractor → FTE or new contractor)
2. MRR/MAU met → add Growth/Marketing role
3. Feedback loop met → consider Platform/Infra role

## Reusable commands

| Command | Use |
|------|------|
| `[change] adkar diagnose <group list>` | M1 diagnostic matrix draft |
| `[change] kotter plan <vision sentence>` | M2 8-step calendar draft |
| `[change] topologies design <team list>` | M3 team-type classification + interaction mode |
| `[change] 7s audit <organization>` | M4 AS-IS/TO-BE gap table |
| `[change] mvt design <product description>` | M5 Minimum Viable Team 4-6 role canvas |
| `[change] mvt okr <quarter> <objectives>` | M5 role-keyed KR mapping |
| `[change] mvt exit-check <current metrics>` | M5 5-criterion expansion evaluation |

## Output contracts

- `adkar-matrix`: groups × 5 stages × scores (0-5) + weakest-link callout
- `kotter-timeline`: 8-step with owner · deadline · deliverable per step
- `team-topology-map`: teams × type × interaction mode table
- `7s-gap-table`: AS-IS / TO-BE / intervention columns mandatory
- `mvt-canvas`: 4-6 roles × responsibility · KR · employment · time zone
- `remote-ceremony-stack`: ceremonies × cadence · format · max time
- `mvt-okr-plan`: 1-2 Objectives + 4-8 KRs (owner assigned)
- `mvt-exit-report`: 5 expansion criteria × current value × met/unmet

## Quality guards

- Reject "strengthen all stages" proposals without weakest-link callout (ADKAR)
- Reject step-5 / step-6 launch without Kotter steps 1-3 (Urgency / Coalition / Vision)
- Reject "org reorg" conclusion without explicit Team Topology coverage of ≥ 3 of 4 types (Enabling · Platform are commonly omitted)
- Reject Reinforcement closeout without measurement KPI

## Telemetry

- ADKAR diagnostic count, weakest-link distribution
- Kotter step revisit count
- Team Topology type-declaration distribution
