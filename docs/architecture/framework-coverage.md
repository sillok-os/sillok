# Framework coverage — global standards inventory

Sillok's roadmap covers **25 categories / 110+ global standards** across
five axes. The `0.1.0a3` alpha ships **10 starter packs** spanning 7–8 of
those categories; the remaining 17–18 categories are queued in the
milestones called out in the table.

This document is the OSS-distribution version of the upstream coverage
inventory (`aipm/project/Harness-Sillok/00-meta/06-framework-coverage-inventory.md`).
The two are intentionally kept in sync but are licensed and distributed
separately — see [`NOTICE`](../../NOTICE) before redistributing.

---

## 1. The 5 axes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Sillok roadmap   = 5 axes × 25 categories ≈ 110+ standards                 │
│                                                                              │
│  [Axis 1] Governance      [Axis 2] Delivery      [Axis 3] Industry          │
│  ├─ 1. ERM/EA             ├─ 5. PMBOK            ├─ 9.  Automotive          │
│  ├─ 2. Risk quant         ├─ 6. SAFe             ├─ 10. Medical Device      │
│  ├─ 3. ITIL/ITSM          ├─ 7. Change Mgmt      ├─ 11. Banking             │
│  └─ 4. Security/Compl     └─ 8. Org Design       ├─ 12. Insurance           │
│                                                  └─ 13. Embedded SW         │
│                                                                              │
│  [Axis 4] Business        [Axis 5] AI/Engineering   [Aux] Output            │
│  ├─ 14. Strategy/BM       ├─ 19. AI/LLM Eng         ├─ 21. External delivery │
│  ├─ 15. M&A / Finance     └─ 20. Prompt sequencing  ├─ 22. Content publish  │
│  ├─ 16. SaaS/Pricing/GTM                            ├─ 23. Enterprise B2B   │
│  ├─ 17. Growth/Data                                 ├─ 24. Design system    │
│  └─ 18. UX/Discovery                                └─ 25. Diagram/Image    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ship status per category

Legend: ✅ ships in 0.1.0a3 today · 🚧 queued for 0.2.0a1 · ⏳ queued for 1.0.0 GA

### Axis 1 — Governance / Risk / Security / Compliance

| # | Category | 0.1.0a3 | 0.2.0a1 | 1.0.0 GA | Standards |
|:-:|---|:-:|:-:|:-:|---|
| 1 | ERM · IT Governance · EA | ✅ `governance-standards` | | ✅ | COSO ERM 2017 · ISO 31000 · COBIT 2019 · TOGAF 10 ADM · Three Lines |
| 2 | Risk quantification | | 🚧 `risk-specialized-standards` | ✅ | NIST RMF · IEC 31010 · FAIR · AIAG-VDA FMEA |
| 3 | ITIL · ITSM | ✅ `itil-operations` | | ✅ | ITIL v4 · 5-Why + Ishikawa · Blameless PM · BIA · DR runbook |
| 4 | Security · Compliance | | 🚧 `regulatory-compliance-kr-eu` + `consulting-security-audit` | ✅ | K-ISMS-P · DORA · PIPL · PCI DSS v4.0 · GDPR/CCPA · STRIDE · OWASP Top 10 |

### Axis 2 — Project / Delivery / Org

| # | Category | 0.1.0a3 | 0.2.0a1 | 1.0.0 GA | Standards |
|:-:|---|:-:|:-:|:-:|---|
| 5 | Project · Portfolio | ✅ `pm-enhanced` + `portfolio-governance` + `risk-uncertainty` | | ✅ | PMBOK 8 · PMP/PgMP/PfMP · Stage-Gate · Power-Interest · Kraljic |
| 6 | SAFe Agile | ✅ `safe-agile-delivery` | | ✅ | SAFe 6.0 · PI Planning · WSJF · ROAM · Lean Portfolio · I&A |
| 7 | Change management | | 🚧 `change-management` | ✅ | ADKAR · Kotter 8-step · Team Topologies · McKinsey 7-S |
| 8 | Org design | | 🚧 `org-design-strategy` | ✅ | McKinsey 7-S · Galbraith Star · Ashridge POLISM · Hub-Spoke |

### Axis 3 — Industry-specific

| # | Category | 0.1.0a3 | 0.2.0a1 | 1.0.0 GA | Standards |
|:-:|---|:-:|:-:|:-:|---|
| 9 | Automotive | | | ⏳ `automotive-standards` | ISO 26262 · ISO/SAE 21434 · UN R155/R156 · ISO 21448 SOTIF · IATF 16949 · ASPICE |
| 10 | Medical device | | | ⏳ `medical-device-standards` | ISO 14971 · IEC 62304 · FDA 21 CFR 820 · EU MDR · IMDRF SaMD · 510(k)/De Novo/PMA |
| 11 | Banking | | | ⏳ `financial-services-standards` | Basel III/IV · CET1/LCR/NSFR · ICAAP/ILAAP · SREP · CCAR/DFAST · K-BCBS |
| 12 | Insurance | | | ⏳ `insurance-standards` | Solvency II · ORSA · IFRS 17 · IAIS ICS 2.0 · K-ICS · K-IFRS 17 |
| 13 | Embedded SW | | | ⏳ `embedded-systems-standards` | AUTOSAR Classic/Adaptive · MISRA C/C++:2023 · SEI CERT · ISO C11/17 / C++20 · Rust Embedded |

### Axis 4 — Business / Strategy / Execution

| # | Category | 0.1.0a3 | 0.2.0a1 | 1.0.0 GA | Standards |
|:-:|---|:-:|:-:|:-:|---|
| 14 | Strategy · Market · BM | ✅ `consulting-strategy-audit` | | ✅ + `platform-strategy` | Porter 5F · Ansoff · Blue Ocean ERRC · BMC · Value Chain · TAM/SAM/SOM · Pyramid · SCQA · Sequoia |
| 15 | M&A · Financial modeling | | | ⏳ `ma-diligence` + `unit-economics-modeling` | Deal Thesis · 6-Stream DD · Synergy EMV · Valuation triangulation · Day -30/+365 PMI · Rule of 40 |
| 16 | SaaS · Pricing · GTM | ✅ `consulting-saas-audit` (audit half) | | ✅ + `saas-pricing-packaging` + `gtm-launch-playbook` | Price Metric · GBB tier · Van Westendorp PSM · Conjoint · Launch Tier 1-4 · Crossing the Chasm |
| 17 | Growth · Data | | | ⏳ `consulting-growth-audit` | Event taxonomy · AARRR · NSM · Aha Moment · Retention Loop · ICE Score |
| 18 | UX · Discovery | | | ⏳ `consulting-uxui-audit` + `product-discovery` | Nielsen 10H · JTBD · ODI · Torres interview · Opportunity Solution Tree · Cagan 4 Risks · VPC |

### Axis 5 — AI / LLM / Prompt engineering

| # | Category | 0.1.0a3 | 0.2.0a1 | 1.0.0 GA | Standards |
|:-:|---|:-:|:-:|:-:|---|
| 19 | AI · LLM engineering | | 🚧 `consulting-ai-engineering-audit` (partial) | ✅ + `prompt-os-self-audit` + `claude-code-wat` | RAG + Claim Verification · Model mix · 4-axis Eval rubric · DSPy GEPA · MCP · OpenTelemetry · Langfuse · 17 RAG probes · 30 router goldens |
| 20 | Prompt sequencing | | | ⏳ `prompt-sequencing-meta` | Layer 1 P1~P5 · Layer 2 Stage 0~5 · Layer 3 D0~D3 · Subagent discipline · Self-healing 3-prompt |

### Auxiliary axis — Output / Delivery / Content

| # | Category | 0.1.0a3 | 0.2.0a1 | 1.0.0 GA | Standards |
|:-:|---|:-:|:-:|:-:|---|
| 21 | External delivery · Magazine | ✅ `exec-communication` | | ✅ + `consulting-audit-magazine-html` + `external-delivery-hardening` | Pyramid Principle · SCQA · 10-slide Board · 1-Pager · Sequoia · MD&A · Pandoc · WCAG AA · Sanitization 5-gate |
| 22 | Content publishing E2E | | | ⏳ `content-publishing-suite` | 8-phase pipeline · 6-Layer · Board-Ready 3-3-3 · Core Web Vitals + Pa11y |
| 23 | Report quality | ✅ `report-quality` | | ✅ | CRAAP · AIMQ · IQF · Bond Triangulation |
| 24 | Enterprise B2B sales | | | ⏳ `enterprise-b2b-sales` | MEDDPICC · Champion Kit · Buying Committee · Challenger CI · POV · MAP · RFP |
| 25 | Design system / Diagram / Image | | | ⏳ `design-system-storybook` + `diagram-design` + `image-prompt-playbook` | Storybook 5-axis · Tailwind v4 tokens · WCAG AA · 13 diagram types · Image 8-slot |

---

## 3. Persona pairing — who uses which category

Match yourself to one of the 25 categories below and you have the entry point that makes Sillok useful for your role today (✅) or worth tracking (🚧 / ⏳).

| # | Category | External consultant | Internal IC / Manager | Internal Leader |
|:-:|---|---|---|---|
| 1 | ERM · IT Governance · EA | Governance Consultant · Industry SME | Risk Manager · Compliance Officer · EA | CIO · CRO · CISO |
| 2 | Risk Quant (NIST/FAIR/FMEA) | Risk Consultant (FAIR Practitioner) | Risk Engineer · Quant Risk Analyst · QA | CRO · CISO |
| 3 | ITIL · ITSM | ITIL Consultant (ITIL Master) | SRE · ITSM Engineer · IT Ops Manager | CIO · VP IT Ops |
| 4 | Security · Compliance | Security Consultant · CISO Advisory | Security Engineer · Compliance Officer | CISO · DPO |
| 5 | Project · Portfolio (PMBOK 8) | PMO Consultant (PMP/PgMP) | PjM · PgM · PMO Lead | COO · Director of Delivery · PfM |
| 6 | SAFe 6.0 | SAFe Consultant (SPC) | Scrum Master · RTE · Delivery Manager | COO · VP Engineering |
| 7 | Change management | OD Consultant (Prosci) | Director of Transformation · Change Manager | CHRO · CEO |
| 8 | Org design | OD Consultant (Korn Ferry / Mercer) | HR Business Partner · Org Designer | CHRO · CEO |
| 9 | Automotive standards | Industry SME (Auto) | Functional Safety Lead · Cybersecurity Lead | CTO · BU Head (Auto) |
| 10 | Medical device standards | Industry SME (Med) | RA/QA · Clinical Lead · UDI Manager | CTO · CMO · BU Head (Med) |
| 11 | Banking standards | Banking Risk Consultant | Risk Manager · Capital Manager · ICAAP Lead | CRO · CFO · CISO |
| 12 | Insurance standards | Actuarial Consultant | Actuary · IFRS 17 Lead · ORSA Lead | CRO · CFO |
| 13 | Embedded SW | Industry SME (Embedded) | Principal Engineer · Embedded Lead | CTO · BU Head |
| 14 | Strategy · Market · BM | **Strategy Consultant** | **Product Manager** · Sr PM · Director of Product | **CPO** · CSO · CEO |
| 15 | M&A · Finance | M&A Consultant (DD) | Corp Dev Manager · M&A Director · BD Lead | CFO · CSO · CEO |
| 16 | SaaS · Pricing · GTM | GTM / Pricing Consultant | Product Manager · Growth PM · Marketing Manager | CPO · CMO · CRO |
| 17 | Growth · Data | Growth Consultant | Growth PM · Data PM · Analytics Lead | CPO · CMO · CDO |
| 18 | UX · Discovery | UX Consultant | Product Designer · UX Researcher · Sr PM | CPO · VP Design |
| 19 | AI · LLM engineering | AI Solution Architect | ML Engineer · TPM · AI PM | CTO · CDO · CPO |
| 20 | Prompt sequencing · Meta | AI Consultant | AI Operations Engineer · PromptOps Lead | CTO |
| 21 | External delivery · Magazine | Consulting deliverable producer | Editorial Lead · Marketing Manager · Tech Writer | CMO |
| 22 | Content publishing E2E | Content / Marketing Consultant | Content Manager · Editorial Lead · Tech Writer | CMO · CCO |
| 23 | Enterprise B2B sales | Sales Consultant (MEDDPICC) | Account Executive · Sales Engineer · Sales Director | CRO · CSO |
| 24 | Design system | Design System Consultant | Product Designer · Design System Lead · Frontend Lead | VP Design · CTO |
| 25 | Diagram · Image prompts | Editorial / Visual Consultant | Tech Writer · Content Manager · Designer | CMO |

### Pattern in the pairing

- **Categories 1–4 (Governance/Risk/Security)** → Senior external + Senior internal + CIO/CISO/CRO
- **Categories 5–8 (Project/Delivery/Org)** → Mid-level external + Mid-level internal + COO/CHRO
- **Categories 9–13 (Industry-specific)** → Industry SME + Domain Lead + CTO / BU Head
- **Categories 14–18 (Business)** → Strategy/GTM consultant + PM line + CPO/CSO/CMO
- **Categories 19–20 (AI engineering)** → AI Solution Architect + ML/PromptOps + CTO/CDO
- **Categories 21–25 (Aux output)** → Specialty consultant + Editorial/Design/Sales line + CMO/VP Design

---

## 4. Why this is Sillok's defensive moat

Other LLM harness systems (LangGraph / CrewAI / Claude Code Skills / BMAD / Devin) typically ship **prompt patterns and orchestration primitives** but not a structured catalog of **formal global standards**. Sillok's value proposition for the consulting / enterprise audience is:

1. **One registry, one audit trail, one proposal-only governance gate** — every framework above is exposed through the same `naru` router and `bongsu` retrieval, with the same `sangso` review pipeline (Phase 1+).
2. **Industry-specific compliance ready** — Banking (Basel III/IV), Insurance (Solvency II / IFRS 17), Automotive (ISO 26262 / 21434 / R155 / R156), Medical Device (ISO 14971 / IEC 62304 / FDA Part 820 / EU MDR), Embedded SW (AUTOSAR / MISRA / SEI CERT) all live under the same operating model.
3. **Cross-axis triangulation** — a banking RFP that needs ICAAP (cat 11) + ITIL Continuity (cat 3) + ERM Governance (cat 1) + SAFe delivery (cat 6) + Pyramid exec communication (cat 21) traverses one router, one pack pipeline, one proposal log.

This is the "moat" claim. It is not yet fully delivered — `0.1.0a3` ships the foundation (axes 1, 2, 14, 16 partial, 21, 23) — but the registry shape, governance contract, and persona mapping are stable enough that downstream packs land additively rather than rearchitecturally.

---

## 5. How to follow the milestone

| Milestone | Categories added | Standards added | Target |
|---|:-:|:-:|---|
| **0.1.0a3 (today)** | 7 | ~30 | shipped |
| 0.1.0a4 (planned) | docs | docs | this doc + README inventory |
| 0.2.0a1 | +6 (cat 2 · 4 · 7 · 8 · 19 partial · 21 partial) | +30 | Phase 1 close |
| 0.3.0 | +5 (cat 14 · 16 · 17 · 18 · 22) | +20 | Business axis complete |
| 1.0.0 GA | +12 (industry + AI + aux) | ~30 | All 25 / 110+ |

Open the [Roadmap](../../03-plan/) (in the upstream Harness-Sillok project) for activation gates and dependencies.

---

## See also

- README §"What works today" — the four `python -m sillok.<module>` CLIs that operate over whichever packs are shipped.
- `packs/registry.yaml` — the source of truth for what's currently registered.
- `obsidian-vault/90_Governance/Reports/20260424-rag-corpus-reevaluation.md` (upstream-only) — the K-6 ablation that motivated the vault-resident-only architecture.
