---
id: tool-adoption-consulting
title: Tool Adoption Consulting Pack — Top 5 Insights × 4-Phase × Lead User
category: domain
sub_category: consulting
license: Apache-2.0
license_atoms: CC-BY-4.0
status: starter
version: 0.1.0a1
references:
  - "Prosci ADKAR — Individual change model"
  - "Lead User Method — von Hippel (1986)"
  - "Phased migration patterns — manual dump → API sync staircase"
  - "Cost of Inaction analysis — Bain et al."
top10_features: ["#3 typed registry", "#5 multi-tenant overlay"]

# agentskills.io v0.9 capability discovery (additive — docs/architecture/frontmatter-compatibility.md)
name: tool-adoption-consulting
description: Tool adoption consulting — Top 5 insights, Risk vs Issue, 4-Phase × 4-Gate, Lead User negotiation.
capabilities:
  - run-top-5-insights
  - build-4-phase-roadmap
  - score-4-gate-decision
  - plan-data-migration-staged
triggers:
  - "[tool-adoption]"
  - "Jira vs"
  - "도구 도입"
  - "변화관리"
  - "Lead User"
  - "tool comparison"
---

# Tool Adoption Consulting Pack

> 도구 도입 컨설팅 (PLSnote/Jira/Salesforce/Notion 류) + 변화관리 + Vendor 협상 통합 패턴
> 용도: 그룹 IP 자산 보유 중견기업 + Lead User 관계 + AI/RAG/MCP 진입 case

## When to apply

다음 중 하나의 시그널이 감지되면 본 pack의 5 Insights와 4-Phase 패턴을 자동 적용:

- 도구 비교 ("Jira vs PLSnote", "Salesforce 검토")
- 변화 관리 ("사용자 저항", "사용률 낮음", "휴먼 에러")
- 데이터 마이그레이션 ("JSON dump", "DB export", "MCP")
- AI 학습 도입 ("RAG 학습", "Copilot 검토", "할루시네이션")
- Lead User 자산 ("그룹 IP", "내부 자산 활용")

## Trigger signals

| Category | Keywords |
|---|---|
| Tool comparison | Jira / Confluence / Salesforce / Notion / Asana / monday / ClickUp |
| Change management | 사용자 저항 / 사용률 / 휴먼 에러 / 거짓 진척 / 변화관리 |
| Data | JSON dump / CSV export / DB mirror / API |
| AI / RAG | RAG / MCP / Model Context Protocol / Copilot / 할루시네이션 |
| Lead user | Lead User / 그룹 IP / 내부 자산 / vendor 협상 |

## Top 5 Insights (mandatory)

### Insight 1 — Avoid tool-fixation

> "Jira냐 PLSnote냐가 아니라, 무엇을 어느 수준으로 관리할지부터 정하자."

- 차종 비유: 자동차 판매 vs 운전기술 (도구 vs 방법론)
- 적용: 모든 도구 도입 권고 前에 **"무엇을 관리할 것인가" 정의** 必
- 가드레일: 도구 비교표는 매니지먼트 포인트 정의 後에만 출력

### Insight 2 — Risk vs Issue separation

| 구분 | 정의 | 1차 도구 |
|---|---|---|
| **Issue** | 이미 발생한 사건, 즉시 처리 | Kanban Workflow + Issue Board |
| **Risk** | 잠재 사건, 사전 예방 | RBS + Heatmap |

**1차 범위 좁히기 룰**: 영업 도메인은 거의 Issue (Risk는 R&D·운영 단계). **1차 범위에서 Risk 본격 도입 ❌** — 단계적 확장.

### Insight 3 — Single deadline rule

```
❌ 다중 등록: A업체 5/10, B업체 5/15, C업체 5/22 (한 카드에 3개)
✅ 단일 등록: 바로 앞 1건만 (A업체 5/10) → 완료 後 다음 1건 등록
```

근거: MS Project / Plan 폐기 사례 — 다중 등록 시 관리 가능성 ↓.

### Insight 4 — Capability-based user selection

| 잘못된 선정 | 올바른 선정 |
|---|---|
| 직급 기준 (전 부장 자동 사용) | 능력 기반 (Lead User 발굴) |
| 강제 의무 | 자율 + 사회적 압력 |
| "다 써야 해" | "안 쓰면 빼버린다" |

**ADKAR Awareness/Desire 사회적 압력 활용**: 본부장이 보고를 도구 사용자에게만 받는 룰 → 자연 강제력.

### Insight 5 — Swan's feet (AI expectation calibration)

> "결과는 간단해 보이지만, 그것까지 가는 과정이 박사과정 수준의 데이터 정제·튜닝."

- AI/RAG는 "쓰는 건 쉽지만 구축은 어려움"
- 0~10단계 알고리즘 + 정규분포 정제 + 할루시네이션 방어 로직
- 적용: AI 도입 권고 前에 **기대치 보정 단락 必** (단계적 진입 안내)

## 5 mandatory deliverables

### 1. 4-Phase roadmap

```
Phase 1 (PoC, 12주)        →  Phase 2 (자산화, 3개월)
─────────────────────         ─────────────────────────
Issue 통제 + 신호등           Tool AI + 자체 RAG
3-team 우선                   자연어 검색 PoC

Phase 3 (안정화, 4개월)    →  Phase 4 (Recovery, 3개월)
─────────────────────────     ─────────────────────────
Enterprise 통합              Vendor MCP 정식 + Paper OCR
1·2-team + 협력사            과거 자산 부활
```

### 2. 4-Gate Decision Matrix

각 Phase 종료에 G1~G4. 의무 컬럼:

| Gate | Go (모두 충족) | No-Go A | No-Go B | 결정자 |
|---|---|---|---|---|
| G1~G4 | 정량 4종 + 정성 2종 | 4주 보강 운영 | 도구 변경 / Phase 종료 | Steering |

### 3. Phased data migration (4 stages)

| Stage | Method | Dev cost | When |
|---|---|---|---|
| 1 | Manual one-time dump | None | Immediate |
| 2 | Scheduled auto-dump | Medium | After 1st verification |
| 3 | Read-only mirror | High | Long-term |
| 4 | Bidirectional sync | Very high | **Not adopted** (risk) |

### 4. Traffic-light R/Y/G rule

| Color | Auto-rule (1st pass) | Qualitative (2nd pass) |
|---|---|---|
| 🔴 Red | Past due-date OR D-2 within | Revenue impact ≥ critical threshold |
| 🟡 Yellow | D-3~7 | Revenue impact medium |
| 🟢 Green | D-8 or beyond | Normal |

### 5. Cost of Inaction comparison

| Item | 12-month loss if not adopted |
|---|---|
| Issue leakage | N issues/quarter × avg impact × recovery rate |
| AI gap solidified | 12-18 month catch-up burden |
| Asset volatilization | IP value ↓ |

→ When **investment < Cost of Inaction**, decision is clear.

## Lead User negotiation (4 stages)

| Stage | Content | When |
|---|---|---|
| 1st | Free-of-charge cooperation request (manual dump) | Immediate |
| 2nd | "Productize" pitch ("usable for your other clients") | 1-2 months later |
| 3rd | Lead User pricing negotiation (formal dev discount) | After 1st verification |
| 4th | Joint R&D partnership evolution | Long-term |

## Vendor pricing fetch-first rule

**Problem**: assumed-vs-actual pricing mismatches cause cascading deliverable rewrites. Mandatory fetch-first:

```
Step 1: Detect tool/service names

Step 2: Pricing fetch priority:
   1) Official vendor pricing page (vendor.com/pricing)
   2) Web search "<vendor> <product> pricing 2026"
   3) User-provided price (if user provides)

Step 3: Estimated prices forbidden:
   ❌ "Jira는 무료일 듯" / "Free tier로 시작"
   ✅ "Jira Premium $X/user/month annual (Atlassian official 2026-MM-DD)" + source link

Step 4: Price-change guardrails:
   - Quarterly re-verification (1st of each quarter month)
   - Single deliverable with ≥3 vendors → footer fetch date
   - FX conversion → fetch-date FX rate

Step 5: User correction → immediate batch update across deliverables
```

**Vendor Pricing table standard format**:

| Vendor | Product/Tier | Price | Unit | Fetch Date | Source |
|---|---|---|---|---|---|
| Atlassian | Jira Premium | $X | user/month (annual) | YYYY-MM-DD | atlassian.com/.../pricing |
| Microsoft | M365 Copilot | $X | user/month | YYYY-MM-DD | microsoft.com/.../pricing |

## Change-management guardrails (ADKAR mapping)

| Stage | Pattern |
|---|---|
| **A**wareness | Director demo + live setup during meeting |
| **D**esire | "안 쓰면 빼버린다" social pressure + Daily reminder |
| **K**nowledge | 4-hour training session + 90-min workbook |
| **A**bility | Live simulation + input form template |
| **R**einforcement | Daily / Weekly review cadence + traffic-light alerts |

## 7 commonly-missed traps (checklist)

```
[ ] "이거 다 입력해야 돼?" → "이슈만, 일상은 그대로"
[ ] "due-date 모르겠어" → 추정값 입력 後 수정
[ ] "이건 Risk 아닌가?" → 이미 발생 = Issue, 잠재 = Risk (1차는 Issue만)
[ ] "한 이슈에 여러 일정" → 바로 앞 1건만
[ ] "고객사 정보 노출" → 내부 권한 only, 외부 share off 디폴트
[ ] "팀장 입력만" → 전 사용자가 본인 카드 직접
[ ] "전부 빨간불" → 빨간불 = 즉시 처리. 즉시 못 하면 노란불부터
```

## Boundaries vs adjacent packs

| Pack | Difference |
|---|---|
| `consulting-saas-audit` | SaaS product self-audit — this pack is adoption consulting |
| `change-management` | ADKAR/Kotter generic — this pack is tool-adoption specific |
| `risk-uncertainty` | Risk governance — this pack is Risk vs Issue separation + change management |

## Output contracts

- `top-5-insights-table.md`
- `4-phase-roadmap.md`
- `4-gate-decision-matrix.md`
- `data-migration-stages.md`
- `traffic-light-rules.md`
- `cost-of-inaction.md`
- `lead-user-negotiation-4-stage.md`
- `vendor-pricing-table.md` (with fetch dates)
- `adkar-application-mapping.md`
