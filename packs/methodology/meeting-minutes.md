---
id: meeting-minutes
title: Meeting Minutes Pack — Transcript → 8-Section Structured Minutes
category: domain
sub_category: methodology
license: Apache-2.0
license_atoms: CC-BY-4.0
status: starter
version: 0.1.0a1
references:
  - "Robert's Rules of Order — Standard meeting minute conventions"
  - "ISO 9001:2015 §7.5.3 — Documented information control (records)"
  - "Decision / Action / Open-question (D/A/O) register pattern"
top10_features: ["#3 typed registry", "#10 failure taxonomy + replay"]

# agentskills.io v0.9 capability discovery (additive — docs/architecture/frontmatter-compatibility.md)
name: meeting-minutes
description: Raw transcript → 8-section minutes with D/A/O register, verbatim quotes, dual-pass attribution.
capabilities:
  - structure-8-section-minutes
  - verify-attribution-dual-pass
  - build-d-a-o-register
  - split-part1-part2
triggers:
  - "[meeting]"
  - "[minutes]"
  - "회의록"
  - "transcript"
  - "meeting minutes"
  - "녹취록"
---

# Meeting Minutes Pack

> Raw transcript (회의록·녹취록) → 구조화된 정리본 변환 패턴
> 용도: 1,000줄+ raw transcript의 결정·액션·미해결 이슈를 추적 가능한 형식으로 변환

## When to apply

다음 중 하나가 감지되면 본 pack의 8-section 구조를 자동 적용:

- "회의록 정리" / "transcript 정리" / "minutes 작성"
- raw transcript 파일 (≥500줄) + "정리해줘" 류 요청
- 화자 식별 가능한 multi-speaker 대화 텍스트

## Trigger signals

| Signal | Example |
|---|---|
| Raw transcript file | `*회의록*.txt`, `*meeting*.txt`, `transcript*.md` |
| Explicit | "회의록 정리", "transcript 정리", "minutes 작성", "회의 결과 정리" |
| Multi-speaker | 이사·상무·부장·팀장·대표 등 호칭 다수 등장 |
| Length | ≥500 lines (≥1,000 lines triggers Part split review) |

## Required output — 8 sections

```
1. 회의 개요
   - 일시·장소·참석자(요약)·목적·산출물 표
   - duration (시간 명시)

2. 참석자 표
   - 역할 / 이름 / 회의 中 핵심 입장
   - 발화 핵심을 한 줄로 요약

3. 의제 (Agenda)
   - 번호 list (1, 2, 3, ...)
   - 시간 배분이 있으면 명시

4. 핵심 논의
   - 발화 순서 ❌ / 주제별 재구성 ✅
   - 각 논의에 §X.Y 번호 부여
   - 직접 인용 verbatim 보존 (quote block)

5. 결정사항 Register (D-register)
   | # | 결정 내용 | 결정자 |
   |---|---|---|
   | D1 | ... | ... |
   - 결정자 명시 必 (이름 또는 합의)

6. 액션 아이템 Register (A-register)
   | # | 액션 | 담당 | 마감 |
   |---|---|---|---|
   | A1 | ... | ... | ... |
   - 담당자 + 마감일 명시 必

7. 미해결 이슈 Register (O-register)
   | # | 이슈 | 다음 결정 시점 |
   |---|---|---|
   | O1 | ... | ... |

8. Verbatim Quotes
   - 직접 인용 (3~5건)
   - 인용 출처 명시 (누가 발화)
```

## Mandatory guardrails

### 1. Verbatim preservation rule

직접 인용 quote는 사람 이름 보정과 무관하게 **원문 verbatim 보존**:

```
✅ 보존: "사장이 하라고 하면 하는 겁니다" (일반 격언)
✅ 보존: "안 쓰면 빼버린다" (정책 메시지)
❌ 비보존: "대표님:" 같은 attribution prefix → 사용자 보정 시 변경 가능
```

### 2. Name-correction protocol (when user corrects names)

```
Step 1: 보정 내용을 식별 (예: 대표님 → <full name + 직급>)
Step 2: replace_all로 본문 일괄 치환
Step 3: grep으로 잔존 검증
   - 구버전 호칭 0건 확인
   - 신버전 호칭 일관성 확인
Step 4: 부분 일관성 보정 (필요 시)
Step 5: 보정 결과 표로 사용자 confirm
```

### 2b. Decision Attribution Dual-Pass Verification

회의록 정확성 = consulting credibility 직결. 모든 Decision (D1, D2, ...) 항목에 화자 attribution을 명시할 때, **2-Pass verification 의무**:

```
Pass 1 — 1차 attribution 작성 시:
   - Decision 항목당 결정자 명시
   - 결정자 식별 근거 1줄 명시 (예: "directly attributed at L342")

Pass 2 — Verbatim quote cross-reference:
   - Decision의 결정자 = 해당 quote 본문의 화자와 일치 확인
   - 다음 명시 패턴 detect:
     • "X 이사: ..." (직접 attribution)
     • "X 이사가 ~를 말씀하셨다" (3인칭 reference)
   - 모든 Decision 결정자 vs verbatim 화자 1:1 매칭 표 생성

Pass 3 — Sub-agent independent verification (≥17 Decisions or ≥1,000 transcript lines):
   - 별도 sub-agent에 transcript + 1차 회의록 input
   - "Decision 결정자 attribution 정확성 검증" task
   - 불일치 발견 시 사용자 confirm 후 수정
```

**Verification gate**:
- 회의록 publish 前 Decision 결정자 100% Pass 2 cross-reference 완료 의무
- ≥17 Decision 또는 ≥1,000 transcript lines 시 Pass 3 sub-agent 검증 추천

### 3. Part 1 / Part 2 split rule

| Condition | Split |
|---|---|
| Transcript ≥1,000 lines | Recommended |
| Explicit lunch break | Required |
| 4+ hour meeting | Recommended |
| Distinct decision domains | Required (e.g., AM=Jira / PM=AI training) |

When split:
- Separate document numbers (Part 1 / Part 2)
- Mutual cross-link (`relates_to:` frontmatter)
- D-register / A-register numbers **continue** (Part 1 D1~D10 / Part 2 D11~D17)

### 4. Cross-link obligation

Appendix lists related artifacts:
- Same-project Charter / Roadmap / Plan
- Previous / next meeting minutes (chronological)
- Artifacts spawned by this meeting

### 5. Image evidence handling

When user attaches images:
- §0 or §X with `Image evidence:` one-liner + short description
- Live setup results in separate § (e.g., "§7 Live setup result during meeting")

## Standard frontmatter (output)

```yaml
---
title: YYYY-MM-DD <organization> Meeting Minutes — <core topic>
date: YYYY-MM-DD
type: meeting-minutes
client: <client>
document_no: <CLIENT>-YYYYMMDD-MEETING-<TYPE>
status: v1.0 (final)
classification: Confidential — <scope>
location: <venue>
duration: <hours>
relates_to: <related document numbers if Part split>
---
```

## 8 commonly-missed patterns (checklist)

```
[ ] Strip small talk / audio noise (coffee, lunch menu, etc.)
[ ] Decision-maker named (D-register: who decided)
[ ] Vague deadlines ("next week", "soon") resolved to absolute dates
[ ] 3-5 verbatim quotes extracted (policy/culture messages)
[ ] Live setup / demo results in separate §
[ ] Decision deltas (e.g., AM decision → PM revision) in Appendix matrix
[ ] Disposition (none / local-reusable / cross-repo-reusable)
[ ] Next-step timeline (ASCII visualization recommended)
```

## File-naming convention

```
<project>/YYYYMMDD-meeting-minutes-<slug>.md           # single meeting
<project>/YYYYMMDD-meeting-minutes-part1-<slug>.md    # split
<project>/YYYYMMDD-meeting-minutes-part2-<slug>.md
```

## Boundaries vs adjacent packs

| Pack | Difference |
|---|---|
| `worklog` | Period accumulation (daily/weekly/monthly) — minutes are single meeting |
| `pm-enhanced` | Internal `[pm]` lifecycle — minutes are external meeting record |
| `report-quality` | Report quality guardrails — minutes are transcript post-processing |

## Output contracts

- `meeting-minutes-8-section.md` — full 8-section markdown
- `attribution-verification-table.md` — Pass 1/2/3 results table
- `d-a-o-register.md` — combined Decision / Action / Open-question register
- `verbatim-quotes-3to5.md` — 3-5 highlighted quotes with attribution

## Telemetry

- Number of Decisions per session, attribution mismatch rate (Pass 1 vs Pass 2)
- Transcript length distribution (drives Part-split rules)
- Live-setup-result occurrence rate
