---
id: project-charter
title: Project Charter Pack — PMBOK 8 + SAFe 6.0 + BABOK v3 9-Section
category: output-style
sub_category: business
license: Apache-2.0
license_atoms: CC-BY-4.0
status: starter
version: 0.1.0a1
references:
  - "PMBOK Guide 8th Edition (PMI, 2025)"
  - "Scaled Agile Framework (SAFe) 6.0"
  - "IIBA — Business Analysis Body of Knowledge (BABOK v3)"
  - "ITIL 4 — Service Management"
  - "Prosci ADKAR — Change Management"
top10_features: ["#3 typed registry", "#9 cross-tool plan SSoT (charter via plan files)"]

# agentskills.io v0.9 capability discovery (additive — docs/architecture/frontmatter-compatibility.md)
name: project-charter
description: Project Charter — PMBOK + SAFe + BABOK 9-section with ROI 3-Scenario, 4-Gate, RACI, Steering Deck.
capabilities:
  - structure-9-section-charter
  - build-roi-3-scenario
  - plan-4-phase-4-gate
  - run-3-lens-self-review
triggers:
  - "[charter]"
  - "Charter"
  - "프로젝트 제안서"
  - "Project Proposal"
  - "Steering Committee"
  - "임원 결재용"
---

# Project Charter Pack

> 외부 클라이언트(C-Suite·Sponsor) 제출용 Project Charter / Proposal 표준 패턴
> 용도: 컨설팅 계약 진행 확정 後 경영진 결재용 1차 안 작성

## When to apply

다음 시그널 중 하나가 감지되면 본 pack의 9-section 구조를 자동 적용:

- "Charter", "프로젝트 제안서", "Project Proposal" 명시 요청
- "Steering Committee 자료", "임원 결재용 deck"
- 2개 이상 Track 동시 추진 + 12개월+ 기간
- PMBOK + SAFe 혼합 거버넌스 요구

## Trigger signals

| Signal | Example |
|---|---|
| Explicit | Charter / 프로젝트 제안서 / Project Proposal / 초기 기획서 |
| Forum | Steering Committee / Sponsor 결재 / 경영진 보고 |
| Structure | Multi-Track / Multi-Phase / 12개월+ |
| Methodology | PMBOK 8 / SAFe 6.0 / BABOK v3 / ITIL 4 / ADKAR |

## Mandatory 5-Section structure (Core)

### 1. Executive Summary

- **Why Now** — 위기·골든타임·트리거
- **What** — 1줄 요약 + Track별 단기/장기
- **Value proposition** — 즉시·점증·자산 가치
- **Investment scale** — 단기/장기 합계 + ROI 1줄

### 2. As-Is vs To-Be

- **Track별 정량 비교 표** (현재 vs 목표)
- **Track별 정성 비교 표** (시야·chain·휴먼 에러·승계 risk·AI 활용)
- **시점별 시각화 ≥4컷** (Phase별 mockup 또는 ASCII)

### 3. Project Objectives & Scope

- Track별 단기 목표 + Acceptance Criteria
- Track별 장기 목표 + Acceptance Criteria
- **Scope (IN) / Scope (OUT) 명시 必**
- 코칭 범위 (PM·Agile·Change·AI)

### 4. Key Deliverables

- Track별 ≥10개 산출물 (T1-D1~T1-D10 식)
- 거버넌스 산출물 ≥5개 (G-D1~G-D5)
- 각 산출물 책임자·시점 명시

### 5. High-Level Roadmap

- **4-Phase 시각화** (Q별 + 상태)
- 단기 12주 W0~W12 상세
- 장기 12개월 M3~M12 마일스톤
- **Gate Decision Matrix (G1~G4)**
- **RACI Matrix** (≥6 활동 × ≥6 역할)

## Mandatory supplementary 4-Section (PMBOK 8)

### 6. Risk + Mitigation (Top 5)

| # | Risk | Impact | Mitigation |

Standard 5: 변화 저항 / Vendor 협조 / 할루시네이션 / Scope 분리 / SPOF

### 7. Success Criteria (NSM + Guardrail)

- 단기: NSM 1 + Guardrail 4
- 장기: 핵심 5종
- 모든 지표에 baseline + target 명시

### 8. Governance 3-Tier

```
Tier 1: Steering Committee (분기 1회, 100분)
Tier 2: Project Working Group (주 1회, 60분)
Tier 3: Daily Operations (Daily, 15분)
```

+ Reporting cadence 표 (Daily / Weekly / Monthly / Quarterly / Phase Gate)

### 9. Approval request

- **Immediate approvals** ≥6 항목 (각 금액·결재선)
- **Phased approvals** (Gate 통과 後)
- **No-Go loss limit** 표

## Mandatory guardrails

### 1. ROI 3-Scenario (mandatory)

```
Conservative (확률 30%) → 12개월 회수 가치 + ROI %
Base (50%)              → 12개월 회수 가치 + ROI %
Optimistic (20%)        → 12개월 회수 가치 + ROI %
Expected Value          → 가중 평균
```

### 2. Break-even point explicit

Conservative scenario 기준 month-by-month 누적 비용 vs 가치 비교 표 필수.

### 3. Phase Gate Go/No-Go quantified

각 Gate에 ≥4개 정량 기준 + No-Go 옵션 A/B 必 (단순 "보류" ❌).

### 4. Cost of Inaction comparison

본 투자 ₩X vs 안 할 시 손실 ₩Y → Y > X 명확화 必.

### 5. Approval-line clarity

각 결재 항목에 **금액 + 결재선** 명시 (Sponsor / Steering / Working Group).

### 6. 3-Lens self-review (mandatory pre-publish)

Charter / Steering Deck draft 완성 후 **publish 전 3-Lens self-review 1회 의무**:

```
Lens 1 — C-Level (Sponsor / 사외이사):
   ✓ ROI 3-Scenario consistency? Break-even 1줄로 인지 가능?
   ✓ Approval-line gaps? Amount + Phase + Gate mapping clear?
   ✓ Risk Top 3 + Mitigation Top 3 pairing?
   ✓ Decision timing (e.g., 5/14 approval / 6/15 conditional D1b) explicit?

Lens 2 — Agility (Working Group / Lead):
   ✓ Day-0 baseline measurable? Measurement method explicit?
   ✓ Champion dependency (single person vs pair + Plan B)?
   ✓ 4-Phase Roadmap learning loops (M1/M3/M6 Pivot Point)?
   ✓ Cadence (Weekly review / Daily standup) operationally feasible?

Lens 3 — Framework (PMBOK/SAFe/BABOK/ITIL standards):
   ✓ PMBOK 8 PD8 Risk Register coverage? Threshold/Tolerance/Appetite separated?
   ✓ SAFe 6.0 LPM 3 Horizons mapping? Lean Budget explicit?
   ✓ BABOK v3 Stakeholder analysis 6×6 Power-Interest grid?
   ✓ ITIL 4 BIA RPO/RTO/RLO (operational scope)?
```

**Execution**:
- 3 sub-agents in parallel
- Integrate results with priority Pn (P1~P10+)
- Priority ≥P3 (high) items: mandatory pre-publish
- Priority ≤P5 (medium) items: deferrable to v1.x patch

## Companion output: Steering Deck Template (10-slide reveal.js)

Charter 작성 시 자동 동반 제안:

```
1. Cover (Sponsor·일시·발표자·문서번호)
2. Why Now (위기 + 골든타임)
3. Core Proposal (Track별 + 가치 KPI 3종)
4. 4-Phase Roadmap (Phase별 예산 표시)
5. AS-IS vs TO-BE (mockup 1컷 + 정성 비교)
6. KPI (NSM + Guardrail 4종)
7. Budget (Phase × category 매트릭스 + 운영비)
8. ROI (3-Scenario + Break-even ASCII)
9. Risk Top 5 + Cost of Inaction
10. Decision Request + Next Steps timeline
```

**Style**: Pretendard + Navy/Gold + reveal.js 5.0+ + Print CSS friendly.

## Standard output frontmatter

```yaml
---
title: <client> 프로젝트 제안서 — <Track 1> + <Track 2>
date: YYYY-MM-DD
type: project-proposal
client: <client>
document_no: <CLIENT>-YYYYMMDD-PROPOSAL-V1
status: v1.0 (초안 — 경영진 검토용)
classification: Confidential — C-Suite & Sponsor Only
prepared_for: <Sponsor> · <stakeholder>
prepared_by: <Consultant>
methodology: PMBOK 8 · SAFe 6.0 · BABOK v3 · ITIL 4 · ADKAR
relates_to: <related document numbers>
---
```

## File-naming convention

```
<project>/deliverables/YYYYMMDD-<client>-project-proposal-charter.md
<project>/deliverables/YYYYMMDD-<client>-comprehensive-roadmap-budget.md  # G-D2 동반
<project>/deliverables/YYYYMMDD-<client>-steering-committee-kickoff-deck.html
```

## Boundaries vs adjacent packs

| Pack | Difference |
|---|---|
| `pm-enhanced` | Internal `[pm]` lifecycle (start/done/release) — this pack: external client Charter |
| `safe-agile-delivery` | SAFe 6.0 ART/PI Planning — this pack: SAFe + PMBOK hybrid |
| `portfolio-governance` | ITIL Portfolio + 4-dim scoring — this pack: single project Charter |
| `report-quality` | Generic report quality — this pack: Charter-specific |

## Output contracts

- `charter-9-section.md` — full 9-section markdown
- `roi-3-scenario.md` — Conservative/Base/Optimistic + EV
- `4-phase-4-gate-matrix.md`
- `raci-6x6.md`
- `steering-deck-10-slide.html` (reveal.js)
- `3-lens-self-review-report.md`
- `cost-of-inaction-table.md`
