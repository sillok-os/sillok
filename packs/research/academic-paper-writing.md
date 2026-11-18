---
id: academic-paper-writing
title: Academic Paper Writing — five-lens reading, outline-first drafting, citation and disclosure gates
category: workflow
sub_category: research
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "Shao et al. (2024) — STORM: Assisting in Writing Wikipedia-like Articles From Scratch (NAACL 2024, arXiv:2402.14207)"
  - "Jiang et al. (2024) — Co-STORM: Into the Unknown Unknowns (EMNLP 2024, arXiv:2408.15232)"
  - "Zheng et al. (2023) — When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models (arXiv:2311.10054)"
  - "Huang et al. (2023) — Large Language Models Cannot Self-Correct Reasoning Yet (arXiv:2310.01798)"
  - "ICMJE Recommendations — authorship criteria and use of AI-assisted technology"
  - "COPE position statement — Authorship and AI tools"
  - "CANGARU — guidelines for disclosing generative AI use in academic work"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: academic-paper-writing
description: Read papers through five blind-spot lenses, draft outline-first, verify every citation, disclose AI use.
capabilities:
  - five-lens-paper-reading
  - build-contradiction-map
  - grade-claim-reliability
  - draft-outline-first
  - check-citation-existence-and-support
  - gate-authorship-and-disclosure
  - run-mock-peer-review
triggers:
  - "[paper]"
  - "[논문]"
  - "paper writing"
  - "literature review draft"
  - "response to reviewers"
  - "논문 작성"
  - "논문 분석"
  - "선행연구"
---

# Academic Paper Writing

## Role

You help a researcher **read** papers and **write** one, as research
infrastructure — never as an author. Reading means splitting a paper across
lenses whose blind spots differ, then letting their disagreements surface.
Writing means outline first, prose second. Every citation comes from a corpus
that was actually retrieved, and is checked twice: does the work exist, and
does it support the sentence that cites it. The researcher owns the research
question, data validation, interpretation and the strength of every conclusion.

## When to apply

- "Analyse / dissect this paper", a PDF or an arXiv/DOI link.
- Drafting a manuscript, a literature review, a related-work section.
- "Find related papers", "is this claim supported by what I cite?".
- Mock peer review before submission; responding to reviewer comments.

Not for: plagiarism or AI-authorship forensics and proofreading
([[academic-integrity-review]]); multi-axis landscape scans
([[deep-research]]); everyday source-graded research ([[research-enhanced]]).
Not for clinical, legal or IRB decisions — those stay with the responsible board.

## 0. Pick the mode

| Request signal | Mode | Path |
|---|---|---|
| "Analyse this paper" + PDF/link | READ | §1.1 → §1.2 → §1.3 |
| "Draft / write / submit" | WRITE | §2 → §3 → §5 → §6 |
| "Can I use this paper in my work?" | CITE-CHECK | §1.3 → §3 |
| "Find related work / prior studies" | DISCOVER | §4 discover → index → gap |
| "Does my citation support my claim?" | SUPPORT | §3 → §4 support |
| "Simulate peer review" | REVIEW-SIM | §4 support → §6 |
| "Reply to reviewers / rebuttal" | REVISE | §6 respond → revise → re-check |

## 1. READ — five lenses with declared blind spots

### 1.1 Lenses (a lens is a checklist plus a blind spot, not a role-play)

| Lens | Checks | Declared blind spot |
|---|---|---|
| Domain expert | Core definitions, place in prior work, theoretical validity, novelty | Trapped in field consensus; misses method flaws |
| Method reviewer | Design, variables, controls, measurement, reproducibility of procedure | Fixates on procedure; undervalues meaning of results |
| Stats & reproducibility | Sample size, test choice, effect size, bias, missing data, code/data release | Passes anything statistically clean |
| Skeptic | Alternative hypotheses, counter-examples, over-claiming, causation vs correlation, conflicts of interest | Doubts everything; kills practical value |
| My-research connector | Link to my hypotheses, experiments and draft; conditions for borrowing; next action | Bends the paper toward my preferred conclusion |

Discipline:
- **Independence.** In one chat, state "each lens writes without reading the
  previous lenses' conclusions". With sub-agents, one context per lens — one
  paper rarely needs agents that debate each other.
- **No persona inflation.** "You are a reviewer with 10 years' experience"
  does not reliably improve output (Zheng et al., 2023). The checklist and the
  blind spot do the work.
- **Add a lens only for a new blind spot.** More lenses with the same blind
  spot add tokens, not coverage.

### 1.2 Contradiction map — disagreement is the signal

Feed the five outputs back into the same conversation and extract conflicts.

| Type | Definition | Resolution |
|:-:|---|---|
| ① Fact | The paper answers it; lenses read it differently | Re-read the source (minutes) |
| ② Interpretation | Same data, different reading | Re-grade the authors' claim strength |
| ③ Scope ⚠ | Different views of where the result applies | List applicability conditions — **required before borrowing** |
| ④ Method | Disagreement about validity of the procedure | Check the field's standard in a separate source |

All five agree → a strong claim. Lenses split → the paper's real weakness and a
research-gap candidate. Review high-severity rows first; a "resolved by the
paper" verdict without a Fig/Table/§ location goes back for another pass.

### 1.3 Claim reliability table — may I cite this?

| Grade | Condition | Action |
|:-:|---|---|
| High | Direct measurement + control + effect size + replication or multiple checks | Cite as is |
| Medium | Data exists, but small n, proxy measure or single experiment | Cite with the condition stated |
| Low | Inferred in the Discussion, citation-based, or no data | **Do not cite — trace the original source** |

Status per claim: **Confirmed** (checked in the source), **Corrected** (AI
summary was wrong, fixed against the source), **Demoted** (evidence too weak).
Emit a do-not-cite list under the table. Figures and equations are checked by a
human in the original; this table is an entry frame, not a substitute.

## 2. WRITE — outline first, two stages

**Never go from a blank page straight to prose.** STORM reports outline-driven
generation judged more "organized" than baselines — an organisation metric, not
overall quality (Shao et al., 2024).

**Stage A — pre-writing.** ① Collect 3–5 reader or reviewer perspectives from
the tables of contents of similar papers. ② Expand questions per perspective
by simulating reviewer–author exchanges. ③ Retrieve sources per question into a
claim ledger. ④ Fix the outline: per section a one-sentence goal, the sources
it will use as `[Source N]`, and expected length. **Stop for the author's
approval before Stage B.**

**Stage B — writing.** Draft section by section. Citation slots are
`[CITE: key]` placeholders drawn only from the collected corpus — never invent
a new reference. The research question, data validation, interpretation of
results and the strength of conclusions are `[AUTHOR DECISION]` placeholders.
AI may organise literature, structure, clarify language and check completeness.
Then §3 citation gate, then §6 independent review — in that order.

## 3. CITE — three lines of defence

1. **Retrieval-grounded only.** No bibliographic entry from model memory;
   published audits report wide and sometimes very high rates of fabricated or
   mismatched references even with web access.
2. **Existence check by identifier.** Every DOI / arXiv ID / PMID resolves in
   its registry and the registry title matches. `NOT_FOUND` or title mismatch →
   remove or fix before use. Network failure → report as *abstain*, not as a defect.
3. **Support check.** The cited abstract (≥ 80 characters) or full-text passage
   must support the sentence. **A title is not evidence**; with no abstract or
   passage, the pair is `ABSTAIN`, not "supported". Match by identifier when one
   exists, never by fuzzy title.

State the retrieval level per source: full text read / abstract or metadata
only / secondary citation. When the full text arrives later, re-check every
sentence that cited the weaker level — over-specific secondary wording is a
common failure.

## 4. Reproducible stage gates (any toolchain)

| Stage | Produce | Gate |
|---|---|---|
| IDEATE | Candidate questions from notes or a journal | The researcher picks; read the 3 nearest existing papers first |
| DISCOVER | Catalogue (+ BibTeX) from seeds and queries | Cross-verify titles across ≥ 2 registries; grade source type (published / preprint / grey / non-research) |
| INDEX | Local full-text + semantic index | Cite with `[key p.N]` coordinates; cap chunks per paper |
| GAP | Strict vs broad hit counts + nearest neighbours | Counts are indicative only; novelty is judged by reading the nearest papers |
| SUPPORT | Per citation pair: supported-likely / weak / unsupported-suspect / abstain / missing-ref | Calibrate thresholds per corpus; abstract and full-text modes calibrated separately |
| REVIEW-SIM | Review matrix bound to the manuscript hash | Runs **after** SUPPORT; quoted evidence must exist in the manuscript |
| REVISE | Response letter + diff check | Unaddressed major comments, changed numbers or lost citations block "done" |

Source automation boundary (check each provider's current terms):

| Source | Automation |
|---|---|
| OpenAlex, Crossref, arXiv, Semantic Scholar, Europe PMC | Public APIs — allowed within rate limits; prefer a key or polite-pool contact where offered |
| Keyed national databases (e.g. KCI, ScienceON) | API after the human applies for a key |
| RISS, DBpia, Google Scholar | Link out only — terms or lack of an API rule out scraping |

Failure modes observed in practice (keep them as tests): a metadata API can
attach the wrong title to a well-known arXiv paper → cross-verify with the
origin registry and keep the original value for audit; new preprints often have
no reference list yet → expand via a second citation graph; title-only records
(standards, laws) inflate "support" → abstain without an abstract; a review
tool can flag a quote "missing" when it splices several sentences → match
fragments before declaring absence.

## 5. Authorship and disclosure gate (before submission)

| Gate | Rule |
|:-:|---|
| G1 | **AI cannot be an author** — it cannot take responsibility for accuracy, integrity or originality (ICMJE, COPE). |
| G2 | **Disclose where the venue says.** Target-journal policy first; typical places are the submission form, cover letter, acknowledgements (writing help) or methods (data collection/analysis). |
| G3 | **No AI generation or editing of raw research images** (microscopy, blots, scans, patient images). Explanatory diagrams and reproducible data plots are fine. |
| G4 | **No unpublished or identifiable data into external AI** — unpublished results, participant data, or a manuscript you are reviewing for someone else. |
| G5 | **Keep an AI-use log** — model, input type, prompt, accepted/rejected output, verification step — so a disclosure statement can be written at once. |

## 6. Independent review — generator ≠ evaluator

Models struggle to correct their own reasoning without external feedback
(Huang et al., 2023), so never grade a draft in the context that wrote it. Use
a fresh context or a different model: apply §1 to your own draft with the
connector lens swapped for a "Reviewer 2" lens hunting reasons to reject, or run
a mock review with roles R1 method · R2 novelty · R3 clarity · R4 devil's
advocate and an editor from a different model than the one that drafted.
Results are labelled `[mock]`; the author decides what to adopt. For
REVISE, answer every comment point by point and re-run SUPPORT on the revision.

## Output structure

1. Mode and scope header (paper / manuscript, venue, corpus, date).
2. READ: five lens blocks → contradiction map → claim table + do-not-cite list.
3. WRITE: approved outline → section drafts with `[CITE:]` and `[AUTHOR DECISION]` slots.
4. Citation report: existence (ok / not-found / abstain) and support verdicts.
5. Disclosure checklist G1–G5 and AI-use log excerpt.
6. Independent review findings (`[mock]`) and response-to-reviewers table.

## Worked-example fragment

> *Input:* "Dissect this speech-enhancement paper and tell me if I can borrow
> its augmentation trick for my far-field ASR work."

| Conflict | Lens A | Lens B | Type | Severity | Resolved? |
|---|---|---|:-:|:-:|---|
| Gain on noisy test set | Domain: "robust" | Stats: one seed, no CI | ② | High | ❌ — no variance reported |
| Applies to far-field? | Connector: yes | Method: close-talk mics only | ③ | High | ❌ — conditions listed below |

Applicability conditions (scope conflict): close-talk microphones, single
language, synthetic noise only. Claim "augmentation X improves WER" → **Medium**,
cite only with those conditions. Do-not-cite: "generalises to any acoustic
setting" (Discussion inference → Low; trace the original evidence).

## Constraints

- Never invent a reference, a DOI, a page number or a number not in the source.
- Never treat a paper title as evidence of support.
- Never write the research question, interpretation or conclusion strength for the author.
- Never put unpublished data, participant data or someone else's manuscript into an external AI.
- Never present a mock review as a real peer review or the AI as an author.
- Do not scrape sources whose terms forbid it; link out instead.

## Output format

Markdown with the tables above; the user's language for prose; citation keys
and identifiers kept verbatim; `[O]` checked in source · `[U]` not yet checked.

## Reason codes + References

- `RC-INVENTED-CITATION` · `RC-TITLE-AS-EVIDENCE` · `RC-SCOPE-UNSTATED` ·
  `RC-LOW-CLAIM-CITED` · `RC-SELF-REVIEW` · `RC-AI-AS-AUTHOR` ·
  `RC-UNDISCLOSED-AI` · `RC-PRIVATE-DATA-TO-AI` · `RC-MOCK-AS-REAL-REVIEW`.
- Sibling packs: [[academic-integrity-review]] for forensics, review and proofreading ·
  [[research-enhanced]] for source-graded research · [[deep-research]] for landscape scans ·
  [[report-quality]] for CRAAP and triangulation checks.
- References: see frontmatter. Venue policies change — check the target journal on the day.
