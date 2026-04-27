# 실록 (Sillok)

> 2단계 라우팅을 갖춘 제안 전용 LLM 운영체제(Proposal-only LLM Operating System).
> 유네스코 세계기록유산(Memory of the World) 3관왕 — 실록(1997) · 직지(2001) · 장경(2007) — 에서 영감을 받았습니다.

**언어:** [English](README.md) · 한국어

[![PyPI](https://img.shields.io/pypi/v/sillok.svg)](https://pypi.org/project/sillok/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Tests](https://github.com/sillok-os/sillok/actions/workflows/eval.yml/badge.svg)](https://github.com/sillok-os/sillok/actions)

> **알림**: 본 README는 [영문 README](README.md)의 동격(同格) 한국어판입니다. 코드·로그·CLI 출력 자체는 영어로 통일되어 있으나, 핵심 어휘에 한해 우리 전통 용어 — *실록·나루·봉수·직지·상소·장경·연륜·사관·법전·편찬·과거·마당·두레·통사·역참* — 을 그대로 살려 표기합니다.

---

## 60초 퀵스타트

> **상태(2026-04-26)**: PyPI `sillok` 0.0.1 은 **이름 선점용 placeholder**(기능 없음)입니다. 실제 구현은 Phase 0 cherry-pick 이후 `0.1.0a1` 로 출시됩니다(roadmap §1). placeholder 를 명시적으로 고정하려면 `pip install "sillok==0.0.1"`. 아래 퀵스타트는 GA(`>=0.1.0a1`) 경험을 기준으로 합니다.

```bash
pip install sillok               # 0.1.0a1+ (실제 알파) — 상단 "상태" 참고
sillok init
sillok route "Acme사 Q3 전략 보고서 작성"

# 예상 출력:
# applied prompt packs: consulting-strategy-audit, exec-communication
# retrieval plan:       wiki_first
# confidence:           high (0.91)
# reason codes:         R1 R3
```

라우팅이 동작합니다. 그게 전부입니다.

---

## 무엇을 받게 되나요

- **10+ 개의 starter 프롬프트 팩** 기본 탑재(전략·PMO·ITIL·보안·그로스·UX 등)
- **2단계 라우터** — 적합한 팩(들)을 먼저 고르고, 적합한 retrieval plan 을 다음으로 선택
- **5종 retrieval plan** — `wiki_first`, with-fallback, recovery-first, dual-compare, no-corpus
- **Reason-coded 출력** — 라우팅 결정마다 R1~R7 태깅(감사 가능)
- **Proposal-only governance** — 4단계 게이트 검토, 무단 덮어쓰기 차단
- 라우팅 자체는 **API 키 불필요**. `--execute` 와 키를 추가하면 LLM 호출
- **외부 코퍼스 의존성 없음** — starter 코퍼스와 모든 통합이 `sillok` 안에 포함. 별도 wiki/지식 베이스 도구 설치 불필요

---

## 요구사항

- **Python 3.11+** (3.12 권장)
- **pip** 또는 **uv**
- macOS 13+ / Ubuntu 22.04+ / Windows 11 + WSL2

선택 사항:
- `ANTHROPIC_API_KEY` 또는 `OPENAI_API_KEY` — 실제 모델 호출 시
- MCP 호환 IDE(Claude Code, Cursor, Continue) — 에디터 내 사용 시
- Docker — 코퍼스를 self-host 하는 경우에만

---

## 설치 단계

3개 stage. 각 stage 는 이전 단계를 전제. 필요한 만큼만 진행하세요.

### 1. 기본 설치 — 1인 사용자 (≈ 5분)

```bash
# 설치
pip install sillok

# 작업 폴더 생성 후 초기화
mkdir my-work && cd my-work
sillok init

# 예상 출력:
# ✓ Created .sillok/config.toml
# ✓ Created .sillok/overlay.yaml  (empty — your customizations go here)
# ✓ Created .sillok/state/
# Run `sillok route "<your message>"` to test.

# 첫 라우팅 테스트(LLM 호출 없음)
sillok route "프로덕트팀 분기 OKR 초안"

# 예상 출력:
# applied prompt packs: pm-enhanced, exec-communication
# retrieval plan:       wiki_first
# confidence:           high (0.88)
# reason codes:         R1 R3 R4

# 실제 모델 호출(API 키 필요)
export ANTHROPIC_API_KEY=sk-ant-...
sillok route "프로덕트팀 분기 OKR 초안" --execute

# 예상: 라우팅된 시스템 프롬프트로 생성된 모델의 실제 답변
```

기본 워크플로우는 여기까지입니다. starter 팩이 컨설팅·PM·IT 운영의 일상 업무 대부분을 커버합니다.

---

### 2. MCP 통합 — IDE (Claude Code / Cursor / Continue, +5분)

**MCP 서버(통사;Tongsa)** 를 통해 IDE 채팅에서 직접 Sillok 라우팅을 사용합니다.

```bash
pip install sillok-mcp
```

**Claude Code** — `~/.claude/settings.json` 또는 프로젝트 `.mcp.json` 에 추가:

```json
{
  "mcpServers": {
    "sillok": {
      "command": "sillok-mcp",
      "args": ["serve", "--stdio"]
    }
  }
}
```

**Cursor** — 같은 형식으로 `~/.cursor/mcp.json` 에 저장.

**Continue** — `docs/integrations/continue.md` 참조.

IDE 재시작 후 채팅에서:

```
> @sillok route "SAP S/4HANA 마이그레이션을 위한 PMO 셋업"
```

```text
# IDE 채팅 예상 출력:
# applied prompt packs: pm-enhanced, safe-agile-delivery, change-management
# retrieval plan:       wiki_first
# confidence:           high
# reason codes:         R1 R3
```

저 줄이 보이면 MCP 연결이 완료된 것입니다. 이제 에디터 안의 모든 `@sillok` 요청을 Sillok 이 라우팅합니다.

---

### 3. 고급 — RAG 코퍼스(장경;Janggyeong) (+10분)

큐레이션된 지식 코퍼스를 부착해 retrieval 정확도를 끌어올립니다. 옵션을 선택하세요:

**A. 공식 starter 코퍼스 사용** (대부분 사용자 권장)

```bash
sillok corpus install --starter

# 예상 출력:
# Downloading 234 atoms (12 MOC entries)...
# ✓ Installed to ~/.sillok/corpus/
# ✓ FTS5 index built (47 ms)
```

**B. 기존 폴더 연결** (frontmatter v5.4 를 따르는 Markdown 노트 — Obsidian vault, docs 사이트, 개인 위키 등)

```bash
sillok corpus link --path /path/to/your/notes

# 예상 출력:
# Validating frontmatter v5.4 ...
# ✓ 412 atoms registered (98% schema-compliant)
# ⚠ 8 atoms skipped (frontmatter incomplete — see corpus.log)
```

> 참고: Sillok 의 코퍼스 포맷은 plain Markdown + YAML frontmatter 스키마입니다. 별도 도구 설치 없이, 스키마를 따르는 어떤 Markdown 폴더라도 동작합니다.

**C. 비어있는 상태로 시작, 누적 축적**

```bash
sillok corpus init --empty
# 큐레이션 파이프라인(편찬;Pyeonchan) 을 통해 작업하면서 atom 이 누적됩니다.
```

동작 확인:

```bash
sillok corpus stats

# 예상 출력:
# Total atoms: 234   (pattern: 78  case: 56  prompt: 41  decision: 28  template: 19  checklist: 12)
# MOC entries: 12
# Last indexed: 2026-04-26 14:30:11

sillok route "B2B SaaS tier-pricing case studies" --show-corpus

# 예상 출력:
# applied packs: saas-pricing-packaging, consulting-strategy-audit
# corpus retrieved (5 atoms):
#   - case/2024-stripe-tier-revamp.md
#   - pattern/value-based-pricing.md
#   - decision/2025-pricing-experiment.md
#   - case/2023-figma-pricing-pivot.md
#   - prompt/saas-pricing-discovery.md
```

---

## 자주 쓰는 워크플로

### 시니어 컨설턴트
```bash
pip install sillok sillok-mcp
sillok init
sillok corpus install --starter
sillok overlay create --client acme    # 클라이언트 단위 커스터마이징
# 이후 Claude Code / Cursor 안에서 @sillok 사용
```

### 팀 리드 / 인하우스 PM
```bash
pip install sillok
sillok init --registry https://internal.example.com/sillok-registry.yaml
# init 시점에 사내 표준 pack registry 를 가져옵니다.
```

### AI 에이전트 빌더
```bash
pip install sillok sillok-mcp
python - <<'EOF'
from sillok import route_message
result = route_message("Phase-2 ERP 롤아웃을 위한 risk register 생성")
print(result.applied_packs)        # ['pm-enhanced', 'risk-uncertainty']
print(result.retrieval_plan)       # 'wiki_first'
print(result.confidence)           # 'high'
EOF
```

---

## 자주 쓰는 명령어

```bash
sillok route "<메시지>"                  # 팩 + retrieval plan 선택(LLM 호출 없음)
sillok route "<메시지>" --execute        # 위와 같음 + LLM 호출 후 답변 출력
sillok route "<메시지>" --show-corpus    # 위 + retrieved atom 출력

sillok packs list                        # 사용 가능한 모든 팩
sillok packs info pm-enhanced            # 단일 팩 상세

sillok overlay create --client <name>   # 새 클라이언트/팀 overlay
sillok overlay use <name>                # 현재 셸에서 활성화
sillok overlay list                      # 모든 overlay 표시

sillok corpus stats                      # 코퍼스 헬스
sillok corpus reindex                    # FTS5 인덱스 재구축

sillok eval run --suite router-goldens   # 회귀: router 30 goldens
sillok eval run --suite rag-probes       # 회귀: 17 RAG probes

sillok sync                              # config + registry 드리프트 체크
sillok doctor                            # 일괄 진단 스냅샷
```

모든 명령어는 영문 alias 와 한국어 모듈명을 동시에 받습니다:
```bash
sillok telemetry tail   ≡   sillok sagwan tail
sillok eval run         ≡   sillok gwageo run
```

---

## 트러블슈팅

```text
sillok: command not found
  → pip install --user sillok 후 ~/.local/bin 을 PATH 에 추가

Corpus not found
  → sillok corpus install --starter

MCP server timeout in IDE
  → pip install sillok-mcp 후 IDE 재시작

Overlay validation failed
  → sillok overlay validate <name>      # 정확한 필드 오류 확인

Drift detected in registry.yaml
  → sillok sync --registry              # 재가져오기 + 조정

Routing slow (>10s)
  → sillok corpus reindex
  → sillok config set discovery_tier 2  # 큰 registry 용 2-tier router

LLM execution fails
  → ANTHROPIC_API_KEY / OPENAI_API_KEY 확인
  → sillok doctor                       # 환경 전체 덤프
```

---

## 다인원 / 전사 배포

위 안내는 **1인 + 1대 노트북** 기준입니다. 50명 이상이 공용 팩, 공용 코퍼스, RBAC, 감사 등급 governance 가 필요하다면 **모든 노트북에 동일 설치하지 말 것** — 코퍼스가 분기되고 감사 흔적이 사라집니다.

[`docs/enterprise-deployment.md`](docs/enterprise-deployment.md) 를 참고하세요:
- Git 백엔드 공용 코퍼스(복제 없음)
- Multi-tenant overlay scoping
- 중앙 telemetry export(OpenTelemetry → Langfuse / Datadog)
- RBAC + leaver-revocation
- self-approval 방지

엄지 규칙: 사내 10명 이상이 Sillok 을 쓸 예정이라면 위 가이드를 먼저 읽으세요.

---

## Top 10 Features

아래 10가지는 단순 RAG 노트북, Obsidian vault, 1회성 prompt-router 스크립트와 Sillok 을 구분 짓는 능력입니다. Feature 1 이 토대가 되는 루프이고, 나머지는 그 위에 governance·eval·multi-tool 도달 범위를 얹는 계층입니다.

| # | Feature | 무엇을 하나 | 모듈 |
|---|---|---|---|
| 1 | **Multi-format Auto-Ingest RAG** | `md` / `pdf` / `docx` / `xlsx` / `pptx` / `txt` / `hwpx`(한글) 에서 개인 RAG 코퍼스를 자동 구축. 파일 변경(`watch`), 스케줄(`cron`), 또는 on-demand 로 incremental 학습. 첫 부트스트랩 + delta 재인덱싱 — 전체 재스캔 없음. | `pyeonchan` + `janggyeong` |
| 2 | **Two-Stage Routing** | Tier 1 키워드/regex 매칭 → Tier 2 LLM 인텐트 분류. 각 쿼리가 필요한 팩과 코퍼스 슬라이스만 로드. 항상 켜진 풀 컨텍스트 대비 ~97% 토큰 절감. | `naru` |
| 3 | **Typed Pack Registry + 5 Retrieval Plans** | 모든 팩이 `corpus_affinity.retrieval_plan` 을 선언: `vault_first`, `vault_then_llmwiki_fallback`, `llmwiki_recovery_first`, `dual_compare`, `no_corpus`. 라우팅이 휴리스틱이 아닌 데이터 주도. | `jikji` + `bongsu` |
| 4 | **Proposal-Only 4-Gate Governance** | 자동 성장과 eval 피드백이 시스템 프롬프트나 팩 본문을 **절대로 직접** 덮어쓰지 않음. 모든 변경은 `prompts/system/proposals/` 에 안착하고 4단계 게이트(lint → diff → eval delta → 사람 승인) 를 통과해야 함. 프롬프트 드리프트 + 코퍼스 오염 hard guard. | `sangso` |
| 5 | **Multi-Tenant Overlay (스코프 코퍼스)** | 개인 vault + 팀 vault + 클라이언트별 vault 가 권한 스코프 계층으로 결합. 같은 라우터가 1인 사용자와 1,000명 조직을 재설계 없이 서비스. | `beopjeon` (스코프) + `janggyeong` |
| 6 | **MCP Bridge** | 같은 코퍼스와 팩을 Model Context Protocol 로 노출 — Claude Code, Cursor, Codex CLI, Continue, ChatGPT Desktop 에서 사용. 도구 lock-in 없음. | `tongsa` |
| 7 | **Plugin System** | 서드파티 능력(WAF-aware 웹 fetch, symbolic 코드 검색, 브라우저 자동화, doc-fetch) 이 팩처럼 등록되고 라우터가 선택. Sillok 확장에 fork 불필요. | `dure` |
| 8 | **Eval Golden Probes + KPI Guard** | 6개 쿼리 family 에 걸친 17-probe 회귀 스위트 내장. CI 게이트: citation coverage 100%, retrieval p50 ≤ 10초, baseline 대비 토큰 ≥ 30% 절감, blind-spot 승격 ≤ 7일. | `gwageo` |
| 9 | **Cross-Tool Plan SSoT** | `docs/plans/<ID>-plan.md` 가 Claude Code, Codex, Cursor 간에 공유 — 한 도구에서 plan 을 시작하고 다른 도구에서 완료. 라우터와 실행기가 같은 plan 을 읽음. | `madang` + `tongsa` |
| 10 | **Failure Taxonomy + Replay Pointer** | 모든 closeout(`pm-done`) 이 5종 failure 태그(`hallucination` / `routing-miss` / `corpus-gap` / `pack-drift` / `governance-bypass`)와 replay 좌표(commit + state snapshot) 를 기록. 이력이 일화가 아닌 학습 가능 데이터로 누적. | `sagwan` + `gwageo` |

> Feature 1 은 나머지 9개를 복리(複利) 로 만드는 **핵심 루프** 입니다. 지속적 multi-format ingest 가 없으면 코퍼스가 쇠퇴(stale)하고, 모든 하류 보장(라우팅 정밀도·eval probe·governance proposal)이 함께 부식합니다. PR-K(`03-plan/01-roadmap-and-activation-gates.md`)가 `pyeonchan` 을 full multi-format + watch/cron/on-demand 동등성까지 끌어올리는 미해결 작업을 추적합니다.

---

## 모듈 레퍼런스 (로그에서 마주칠 때만 참고)

`sillok` 은 단일 패키지입니다. 내부적으로 한국 전통 어휘로 명명된 모듈로 조직됩니다. 도구를 사용하기 위해 외울 필요는 없으나, 매핑은 다음과 같습니다:

```text
나루(naru)          - 2단계 라우팅 (강을 건너는 첫 길목)
봉수(bongsu)        - 5종 retrieval plan (烽燧, 봉화로 정보를 잇던 신호망)
직지(jikji)         - 팩 레지스트리 (直指, 1377년 세계 최고(最古) 금속활자본 = 인쇄형 표준)
상소(sangso)        - 제안 엔진 / 거버넌스 게이트 (上疏, 임금에게 올린 청원·제안 절차)
장경(janggyeong)    - RAG 코퍼스 (藏經, 팔만대장경 — 큐레이션된 atom 모음)
연륜(yeonryun)      - 자동 메모리 / telemetry 기반 성장 (年輪, 나이테처럼 누적되는 지식)
사관(sagwan)        - 텔레메트리 / 옵저버빌리티 (史官, 실록을 기록하던 사관)
법전(beopjeon)      - 스키마 (法典, Pydantic — 데이터의 법전)
과거(gwageo)        - eval (科擧, 회귀시험 = 과거시험)
마당(madang)        - CLI 진입점 (마당, 사람이 모이는 공간)
두레(dure)          - 플러그인 프레임워크 (두레, 협업 공동체)
통사(tongsa)        - MCP 서버 / IDE 통합 (通辭, 통역사 — 도구 간 언어 변환)
편찬(pyeonchan)     - 코퍼스 큐레이션 파이프라인 (編纂, 사료를 묶어 책으로 엮음)
역참(yeokcham)      - 외부 브릿지 (驛站, 역참 — 외부 vault·코퍼스로 가는 중계소)
```

모든 모듈 명령어는 영문 alias 도 가집니다(`sillok telemetry tail` ≡ `sillok sagwan tail`).

---

## 라이선스 & 기여

- **소스 코드**: Apache License 2.0 — [`LICENSE`](LICENSE) 참고
- **Starter atoms**(`04-prototypes/janggyeong-starter-atoms/`): Creative Commons Attribution 4.0 (CC BY 4.0) — 별도 라이선스인 교육 콘텐츠
- **상표 / 출처 표기 / 문화적 참조**: [`NOTICE`](NOTICE) — 재배포 전 필독. Sillok 은 PMBOK®, SAFe®, BABOK®, ITIL®, COBIT®, ISO/IEC 표준 등을 nominative fair use 로 참조하며, 어떤 단체와도 제휴 / 보증 관계가 없습니다.
- **기여**: [`CONTRIBUTING.md`](CONTRIBUTING.md) 참고(DCO sign-off 필수)
- **거버넌스**: [`GOVERNANCE.md`](GOVERNANCE.md) 참고
- **행동 강령**: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) 참고(Contributor Covenant 2.1)
- **이슈**: https://github.com/sillok-os/sillok/issues
- **토론**: https://github.com/sillok-os/sillok/discussions

---

## 선행 연구 & 영감

Sillok 의 지식 계층은 Andrej Karpathy 가 제안한 **"LLM Wiki" 패턴**([gist, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)) — 사용자와 raw source 사이에 위치하는 LLM 유지 / 영속 / 상호참조 markdown wiki — 의 제품화 구현입니다.

| Karpathy LLM Wiki | Sillok 모듈 |
|---|---|
| Raw sources (불변) | 사용자의 vault / 노트(코퍼스 외부 보관) |
| The wiki (LLM 생성 markdown) | RAG 코퍼스(장경;Janggyeong) |
| Schema (CLAUDE.md / AGENTS.md) | `CLAUDE.md` + frontmatter v5.4 |
| Ingest | 큐레이션 파이프라인(편찬;Pyeonchan) |
| Query | Retrieval(봉수;Bongsu) |
| Lint | 자동 성장(연륜;Yeonryun) + Eval(과거;Gwageo) |
| `index.md` | 코퍼스 내부의 MOC(Map of Content) |
| `log.md` | Telemetry 로그(사관;Sagwan) |

Sillok 은 패턴 위에 다음을 더합니다: 타입 있는 **pack registry**(직지;Jikji), **2단계 라우팅**(나루;Naru), **proposal-only 4-게이트 governance**(상소;Sangso), **multi-tenant overlay**(법전;Beopjeon scope), 그리고 **유네스코 세계기록유산 3관왕** 브랜드 정체성.

Karpathy 패턴에 이미 익숙하다면, Sillok 은 그 위에 governance · multi-tenant 스코프 · 한국 문화 앵커를 얹은 결과물입니다.

기타 영향: Vannevar Bush 의 **Memex**(1945) — 연상 trail 을 갖춘 개인 큐레이션 지식 — Karpathy 자신도 인용한 출발점.

### 왜 vault-resident 전용인가 (30시간 ablation)

vault-resident 코퍼스 저장만을 지원하는 결정(Install Manual §4.1)은 스타일 선택이 아니라 — 10년 묵은 Obsidian vault(45,640 노트)와 fresh Karpathy-style llm-wiki 사이의 30시간 head-to-head ablation 결과입니다(6 query pattern × 5 axis 루브릭 = 96점):

- **Q5(Case Bank Mode)**: vault 가 **0건** 반환한 사이 llm-wiki 는 OneDrive 스캐닝으로 5분 만에 케이스를 찾음 — "구조적 20% blind-spot" 가설을 입증한 16점 격차.
- **Coverage gap**: 45,640 노트 중 13,772(30%) 만이 `vault-search` 인덱싱; 나머지 **31,868 노트(70%) 가 사실상 retrieval 에 invisible** — extraction 전까지.
- **최종 아키텍처**: *vault 를 단일 진실원으로 + Karpathy 패턴이 surface 했을 모든 포맷을 흡수하는 extraction 파이프라인*. 정확히 Sillok 의 `pyeonchan`(Multi-format Auto-Ingest, Top 10 Feature #1)이 구현하는 것이며, Install Manual 이 system-global / 격리 `.sillok/` 코퍼스 위치를 거부하는 이유.

> 참고: K-6 _"30시간 RAG 실측 회고 — Karpathy 의 llm-wiki 는 내 10년 obsidian-vault 를 이길 수 있었나"_ (projectresearch.co.kr, 2026-04-18, post id 9998).

### 직접 명세 추적(D-시리즈)

Karpathy 패턴 외에도 Sillok 의 모듈 선택은 agentic engineering 6부작 PM-coach 분석(AX whitepaper 의 **D-시리즈**)과 1:1 대응합니다. 각 D-post 가 미해결 문제를 식별했고, 각 Sillok 모듈이 운영적 답안:

| D-post (projectresearch.co.kr) | 미해결 문제 | Sillok 모듈 / feature |
|---|---|---|
| D-1 _MCP & A2A 프로토콜_ (2026-04, post 10009) | agent-protocol lock-in 방지 | `tongsa` MCP Bridge (Feature #6) |
| D-2 _Agentic PM (PMBOK 8th)_ (post 10010) | AI as Assistance / Augmentation / Automation 3-pattern 통합 | `pm-enhanced` + `safe-agile-delivery` 팩 |
| D-3 _Vibe Coding & Agentic Engineering_ (post 10011) | OWASP Agentic Top 10 (ASI01~ASI10) 게이트 | `claude-code-wat` 팩 + `sangso` 4-게이트 |
| D-4 _Multi-agent topology 선택_ (post 10012) | 코디네이션 비용 소유권 | `tongsa` (MCP Bridge) + `dure` (플러그인 시스템) |
| D-5 _AI-SDLC governance 게이트_ (post 10013) | 품질 약속 → 게이트 배치 | `sangso` proposal-only 4-게이트 (Feature #4) |
| D-6 _RAG 지식 관리_ (post 10014) | 10년 lesson-learned / RAID / 플레이북 재활성화 | `janggyeong` + `pyeonchan` + multi-tenant overlay (Features #1 + #5) |

D-시리즈는 본 코드베이스보다 선행하며, Sillok 의 14개 모듈은 정확히 이 6개 문제를 해소하기 위해 선택되었습니다. D-시리즈를 먼저, Sillok 의 `02-design/06-architecture-overview-and-impact.md` Part 0.5 를 그 다음으로 읽으면 정합도가 직접적으로 드러납니다.

---

## 인용

연구에 Sillok 을 사용하시는 경우, 프리프린트 인용을 부탁드립니다:

```bibtex
@misc{sillok2026,
  title  = {Sillok: A Proposal-Only LLM Operating System with Two-Stage Routing},
  author = {Kim, Peter and contributors},
  year   = {2026},
  url    = {https://arxiv.org/abs/XXXX.XXXXX}
}

@misc{karpathy2026llmwiki,
  title  = {LLM Wiki},
  author = {Karpathy, Andrej},
  year   = {2026},
  howpublished = {GitHub Gist},
  url    = {https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f}
}
```

---

*실록(Sillok) = 조선왕조실록(朝鮮王朝實錄). 유네스코 세계기록유산, 1997.*
