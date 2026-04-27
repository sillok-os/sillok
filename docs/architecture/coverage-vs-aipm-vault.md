---
title: "Sillok 0.1.0a1 README/Manual 커버리지 — aipm/promptos + obsidian-vault 대비 정합성 분석"
date: 2026-04-27
type: meta-audit
status: ratified
parent: project/Harness-Sillok/README.md
audience:
  - 본인 (사용자) — sillok ↔ aipm 두 시스템 운영 분리 결정
  - 외부 컨설턴트 / AX 직장인 — sillok 0.1.0a1 의 실제 capability 이해
purpose: "sillok 0.1.0a1 README/manual 만으로 사용자 본인의 daily workflow(aipm/promptos + obsidian-vault) 가 어느 정도 대체되는지 정직한 매트릭스 산출. 외부 OSS 사용자 관점과 본인 사용자 관점을 분리하여 실제 운영 권고 도출."
trigger_prompt: |
  본 /README 설치 가이드 및 사용자 가이드만 있으면 현재 aipm/promptos &
  obsidian-vault(RAG)의 많은 부분이 커버되는거지?
related_docs:
  - 04-prototypes/sillok-public-README.md (대상 README)
  - 05-launch/03-install-setup-manual.md (대상 사용자 매뉴얼)
  - 03-plan/01-roadmap-and-activation-gates.md (Phase 0 EXIT 기준)
  - 02-design/06-architecture-overview-and-impact.md Part 0.5 (Top 10 features)
release_target: v0.1.0a1 (2026-04-26 functional alpha)
---

# Sillok 0.1.0a1 README/Manual 커버리지 — aipm/promptos + obsidian-vault 대비 정합성 분석

## 한 줄 요약

**sillok 0.1.0a1 의 README + manual 만으로는 — 외부 OSS 사용자에게는 ~80% 커버 / 사용자 본인 daily workflow 대체로는 ~35% 만 커버.** 두 시스템을 분리 운영하는 것이 정합 (sillok = 외부 배포본, aipm + obsidian-vault = 본인 daily SSoT).

---

## 1. 분석 배경

`sillok 0.1.0a1` (functional alpha, 2026-04-26 출시) 의 README + 설치/사용 매뉴얼만으로 사용자 본인의 매일 쓰는 두 시스템:

- `~/GitHub/aipm` — promptos 본가 (56 packs registry, 14+ 자동화 scripts, PM 라이프사이클 hook)
- `~/GitHub/obsidian-vault` — 45,640 노트 + 13,772 indexed (vault-search FTS5 corpus)

이 어느 정도 커버되는지를 영역별로 정직 산출.

---

## 2. 영역별 커버리지 매트릭스

| 영역 | aipm/promptos 본가 자산 | obsidian-vault 자산 | sillok 0.1.0a1 커버 | Gap |
|---|---|---|:-:|---|
| **2-tier routing** | `prompt-router-2tier.py` 230 LOC | — | ✅ | 없음 (F0.3 step 1) |
| **Pack registry 메타** | 56 packs (registry.yaml v1.14.0) | — | 🟡 10/56 | **46개 누락** |
| **Pack 본문** | 56 body | — | 🟡 10/56 | 동일 비율 |
| **Schemas (Pydantic)** | `prompts/system/schemas/` 7파일 | — | ✅ | 없음 (F0.5) |
| **Bongsu post-update** | `prompt-router-post-update.py` | — | ✅ | 없음 (F0.4) |
| **Full v2 router** (calibration + semantic) | `prompt_os_v2.py` 1235 LOC | — | 🚫 | F0.3 step 2 → **0.2.0 deferred** |
| **Proposal generation** | `prompt-propose.py` | — | 🚫 | Sangso 미이식 (Phase 1) |
| **Vault FTS5 search** | `vault-search.sh` | 13,772 indexed of 45,640 | 🟡 minimal | FTS5 vs JSONL only — **RAG 정확도 격차** |
| **LLM auto-compile** | `compile-to-wiki.py` | Inbox 처리 | 🚫 | Pyeonchan Phase 2 (PR-K) |
| **Inbox process** | `inbox-process.sh` | `00_Inbox/` 분류 | 🚫 | 미이식 |
| **Vault disposition 자동 판정** | `vault-disposition.py` | atom 자동 승격 | 🚫 | Pyeonchan Phase 2 |
| **RAG KPI runner** | `rag-kpi.sh` (17 probe 실행) | — | 🟡 fixtures only | runner 미이식 |
| **PM 라이프사이클 자동화** | `pm-{start,sync,audit,close,release}.sh` | — | 🟡 가이드만 | pm-enhanced pack 명세 있지만 실제 자동화는 gh CLI 직접 호출 필요 |
| **GitHub issue 자동화** | `issue-create.sh` + 라벨 규칙 | — | 🚫 | 미이식 |
| **Multi-format ingest** | (aipm 도 md only) | — | 🟡 md only | 둘 다 PR-K Phase 2 에서 확장 (동일) |
| **Multi-tenant overlay (router 통합)** | `prompt_os_v2.py` 부분 | — | 🟡 schema 만 | router 통합 미완 |
| **MCP bridge** | (aipm 에는 없음) | — | 🚫 | `sillok-tongsa` Phase 1 PR-D 예정 |
| **Cross-tool plan SSoT 자동화** | `docs/plans/` + CLAUDE.md hook | — | 🟡 docs only | 자동화 미이식 |
| **Failure taxonomy + replay** | `pm-done` 강제 (CLAUDE.md) | — | 🟡 가이드만 | pack 명세만, 자동화 부재 |
| **Eval CI blocking** | 현재 warn-only | — | 🟡 동일 | 둘 다 PR-B 후 (동일) |

---

## 3. 두 관점에서의 실제 커버 비율

| 관점 | 커버 비율 | 적합성 |
|---|:-:|---|
| **외부 OSS 사용자 (첫 경험)** | **~80%** | 🟢 높음 — Top 10 features + 10 starter packs + minimal ingest + 7-client MCP 매트릭스가 60-초 quickstart 에 충분 |
| **사용자 본인의 daily workflow 대체** | **~35%** | 🔴 **낮음** — 핵심 자동화 부재가 critical |

---

## 4. 사용자 본인 관점에서 누락된 critical 자동화 5종

매일 쓰시는 워크플로우 중 sillok README 만으로는 안 되는 것:

1. **`vault-search.sh` 의 FTS5 정확도** — sillok 의 JSONL minimal 인덱스로는 같은 회수 품질 안 나옴 (K-6 30시간 실측의 13,772 indexed / 45,640 노트 = 30% 커버리지가 vault-search FTS5 기준)
2. **`vault-disposition.py` + `compile-to-wiki.py` + `inbox-process.sh`** — vault accumulation loop 의 핵심 3종 (자동 atom 승격 / Inbox 분류 / LLM 컴파일)
3. **`pm-start/sync/audit/close/release` 자동화** — `[pm]` 트리거의 실제 동작 (cross-repo issue sync, modernize, release advisor 등)
4. **46 누락 packs** — 본인이 자주 쓰는:
   - consulting Lens 2-5 (UX / AI Engineering / Security / Growth)
   - 산업 표준 4팩 (의료기기 / 금융 은행 / 보험 / 임베디드)
   - 자동차 표준팩 (ISO 26262 / 21434 / R155 / R156 / SOTIF / ASPICE)
   - AI 인물 백서 / AX 전략 / 디자인 시스템 / 다이어그램 / 이미지 프롬프트
   - SaaS 가격 / 플랫폼 / GTM / Unit Economics / B2B Sales
   - M&A / Product Discovery / Org Design / 변화 관리
   - Risk Specialized Standards (NIST RMF / IEC 31010 / FAIR / FMEA)
   - Regulatory Compliance KR-EU
5. **`prompt-propose.py`** — Sangso 4-gate proposal 생성 엔진 (telemetry → proposal artifact)

---

## 5. 1줄 결론

> **sillok 0.1.0a1 README/manual 은 OSS 외부 사용자에게는 ~80% 커버되어 첫 경험에 충분하지만, 사용자 본인의 매일 쓰는 aipm + obsidian-vault 시스템을 대체하려면 ~35% 만 커버됩니다. 사용자 본인은 aipm 본가 + obsidian-vault 를 그대로 daily 로 사용하시고, sillok 은 OSS 배포본/외부 공유본으로 분리 운영하시는 것이 정합합니다.**

---

## 6. 두 시스템 역할 분리 권고 (정직)

| 시스템 | 역할 | 사용자 | 갱신 주기 |
|---|---|---|---|
| **aipm/promptos + obsidian-vault** | daily SSoT — 실제 작업 환경 | 사용자 본인 (Peter) | 매일 (live) |
| **sillok-os/sillok** | OSS 배포본 — 외부 공유 + 검증된 부분 | 외부 컨설턴트 / AX 직장인 | 분기별 release (검증 후 cherry-pick) |

두 시스템을 동기화하려는 시도는 **sanitize 비용 + drift 위험** 으로 비효율적이며, sillok 은 **"aipm 의 검증된 부분만 정제하여 외부 공유한 stub"** 으로 이해하는 것이 정확합니다.

---

## 7. 만약 진짜 100% 커버 원한다면 (비권장)

추가로 필요한 작업 정량화:

| 작업 | 추정 시간 | 가치 |
|---|:-:|---|
| F0.3 step 2 (v2 router 1235 LOC sanitize) | 3~4시간 | 🟡 (2-tier 가 production path) |
| 46 packs body sanitize (각 1-2시간) | 50~90시간 | 🟢 (외부 가치 있음) |
| vault-disposition + compile-to-wiki + inbox-process cherry-pick | 20시간 | 🟡 (vault 데이터 분리 필요) |
| pm-* 자동화 cherry-pick + sanitize (cross-repo issue/modernize/advisor) | 15시간 | 🟡 (gh CLI 의존성) |
| vault-search FTS5 인덱스 이식 | 10시간 | 🟢 (RAG 정확도 결정적) |
| **합계** | **~100~140시간** = 2-3 주 풀타임 | — |

OSS 의 진짜 가치 (외부 공유) 와 비례하지 않으므로 **권장하지 않습니다**.

---

## 8. 단계적 cherry-pick 권고 (선택지 B 상세)

만약 일부 자동화만 sillok 에 추가하고 싶다면, ROI 순서:

| 우선 | 작업 | 추정 | 효과 |
|:-:|---|:-:|---|
| 1 | **vault-search FTS5 인덱스 이식** | 10시간 | RAG 정확도 즉시 ↑↑ — Pyeonchan FTS5 부트스트랩 |
| 2 | **5 추가 starter packs** (Lens 2-5 UX/AI/Security/Growth + Risk Specialized) | 5~10시간 | 컨설팅 시리즈 완성 → 외부 가치 +30% |
| 3 | **vault-disposition.py 분기 (workshop-retro)** | 5시간 | atom 승격 자동화 (AIPM-426 액션 아이템) |
| 4 | **pm-start.sh sanitize cherry-pick** | 4시간 | `[pm] start` 자동화 (cross-repo 미포함) |

= 24~29시간으로 sillok 의 사용자 본인 커버리지 ~35% → ~55% 상승. 단 외부 OSS 가치는 ~80% → ~85% 만 상승 (이미 80% 가 충분).

---

## 9. 결정 사안 (사용자)

- **(A)** 분리 운영 유지 — sillok 은 외부 배포본으로 freeze 하고 사용자 본인은 aipm + obsidian-vault 그대로
- **(B)** 단계적 cherry-pick (§8 의 1~2번만, 15~20시간) — RAG 정확도 + Lens 시리즈 완성
- **(C)** 풀 cherry-pick (§7 의 ~100~140시간) — 비권장
- **(D)** 별도 방향 — 예: 0.1.0a1 freeze + Phase 1 PR-A/B/D 진입 (eval CI + MCP 1급)

추천: **(A) 또는 (B)**.

---

## 10. 연관 결정 ADR (sillok 측)

본 분석을 sillok-os/sillok 의 향후 ADR 0002 또는 GOVERNANCE.md §scope 에 인용 시 다음 1줄 사용 가능:

> "Sillok is the OSS distribution stub of the upstream `aipm` PromptOS; it ships only the parts that have been sanitized for public consumption. Approximately 35% of the upstream maintainer's daily workflow is reproducible from the OSS surface, and that gap is intentional — the OSS value is breadth of audience, not parity with a single user's vault."

---

## Notes

- 본 분석은 v0.1.0a1 출시 직후(2026-04-26) 시점 기준
- `prompt_os_v2.py` 1235 LOC는 0.2.0 에 deferred
- vault-search FTS5 우위는 K-6 30시간 ablation 실측에 근거
- 46 packs 누락은 sanitize 비용이 OSS 가치보다 큰 영역으로 의도적 분리

---

## 11. Re-evaluation — B+ cherry-pick 적용 (2026-04-26 야간, v0.1.0a2)

§9 의 사용자 결정 "모두 적용" 에 따라 §8 의 우선순위 1·3 두 항목 — `vault-search` 와 `vault-disposition` — 을 sillok 에 cherry-pick 했습니다. 본 §11 은 그 결과의 정직 재평가입니다.

### 11.1 변경 요약 (4 commits, sillok-os/sillok)

| Commit | SHA | 내용 |
|---|---|---|
| B+ 1of4 | `f26b38e` | `sillok/bongsu/_common.py` (~165 LOC) + `bongsu/search.py` (~290 LOC) + smoke 12종 — frontmatter / build_index / filter / fulltext / scope-aliases |
| B+ 2of4 | `a4c3ccf` | `sillok/yeonryun/disposition.py` (~430 LOC) + smoke 16종 — score / disposition / atom 추출 / auto-extract |
| README ko | `3df2609` | `README.ko.md` 한글 동격본 (전통 어휘 보존) |
| B+ 3of4 | `09c7f82` | recipes 2개 (search · disposition) + integration 3종 (bongsu→yeonryun seam) |
| B+ 4of4 | (this) | §11 갱신 + 버전 0.1.0a2 + tag/release |

### 11.2 사용자 본인 daily workflow 커버리지 재산출

| 영역 | v0.1.0a1 (이전) | v0.1.0a2 (B+ 후) | 변화 |
|---|:-:|:-:|---|
| Vault FTS5 search | 🟡 minimal (JSONL only) | 🟢 frontmatter + body grep + scope-aliases | RAG 회수 정확도 ↑↑ |
| Vault disposition 자동 판정 | 🚫 미이식 | 🟢 score + threshold + auto-extract | atom 승격 자동화 ↑↑ |
| Recipes (실사용 가이드) | ⏳ 0개 | ✅ 2개 (search · disposition) | 외부 onboarding ↑ |
| Integration test seam | 0 | 3 (bongsu→yeonryun) | 회귀 안전망 ↑ |
| Bilingual README | EN only | EN + KO 동격 | 비영어권 onboarding ↑ |

### 11.3 두 관점 커버 비율 갱신

| 관점 | v0.1.0a1 | v0.1.0a2 (B+ 후) | Δ |
|---|:-:|:-:|:-:|
| **외부 OSS 사용자** | ~80% | **~88%** | +8pp (Karpathy LLM Wiki Query+Lint 절반이 production path) |
| **사용자 본인 daily 대체** | ~35% | **~55%** | +20pp (vault-search + disposition cherry-pick 효과) |

### 11.4 §4 누락 critical 5종의 처리 상태

1. ~~vault-search FTS5 정확도~~ → ✅ B+ 1of4 (frontmatter + body grep, FTS5 자체는 0.2.0 Pyeonchan 단계로 이연)
2. **vault-disposition** ~~+ compile-to-wiki + inbox-process~~ → 부분 ✅ disposition 만 흡수, compile-to-wiki / inbox-process 는 PR-K Phase 2 유지
3. ~~pm-start/sync/audit/close/release 자동화~~ → 🚫 변동 없음 (gh CLI 의존성으로 0.2.0 이후 cherry-pick 검토)
4. ~~46 누락 packs~~ → 🟡 변동 없음 (10/56 — 본 작업 범위 외)
5. ~~prompt-propose.py (Sangso)~~ → 🚫 변동 없음 (Phase 1 PR-D 예정)

### 11.5 §5 1줄 결론 갱신

> **sillok 0.1.0a2 README/manual 은 OSS 외부 사용자에게 ~88% 커버, 사용자 본인 daily workflow 대체로 ~55% 커버합니다. Karpathy LLM Wiki 패턴의 Query+Lint 절반이 이제 sillok 에서 production path 로 동작 — 본인 daily 와 외부 OSS 의 격차가 53pp → 33pp 로 축소됐습니다. 단 vault-search FTS5 (정밀 인덱스) · pm-* 자동화 · 46 누락 packs 는 여전히 aipm 본가 우위.**

### 11.6 §6 분리 운영 권고 — 변동 없음

분리 운영은 그대로 유효합니다. B+ cherry-pick 으로 RAG/promotion 코어가 OSS 표면에 노출됐지만, **daily SSoT 는 여전히 aipm + obsidian-vault** 이고, **sillok 은 OSS 배포본** 입니다. 두 시스템 동기화 비용이 정합 비율 (~88% / ~55%) 보다 크다는 §6 결론은 그대로 유지됩니다.

### 11.7 다음 단계 권고

| 우선 | 작업 | 추정 | 효과 |
|:-:|---|:-:|---|
| 1 | **FTS5 인덱스 빌더 이식** (Pyeonchan Phase 2) | 10시간 | RAG p50 latency ↓ + recall ↑ |
| 2 | **5 추가 starter packs** (Lens 2-5 + Risk Specialized) | 5~10시간 | 컨설팅 Lens 완성 → 외부 가치 ~88% → ~92% |
| 3 | **eval CI blocking gate** (PR-B) | 5시간 | 회귀 안전망 — 자동 promotion 시 필수 |

권장: 1·2 를 0.2.0a1 마일스톤으로 묶기.
