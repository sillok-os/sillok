---
id: academic-integrity-review
title: Academic Integrity Review — evidence-graded forensics, findings-first review, meaning-preserving proofreading
category: workflow
sub_category: research
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "COPE — Core practices and guidance on authorship and AI tools"
  - "ICMJE Recommendations — use of AI-assisted technology"
  - "Chain-of-custody practice from digital forensics (hash, read-only original, logged steps)"
  - "Admiralty-style evidence grading (source × content reliability)"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: academic-integrity-review
description: Review academic text for plagiarism or AI-authorship signs with graded evidence; findings-first review; proofreading.
capabilities:
  - preserve-chain-of-custody
  - grade-forensic-evidence
  - collect-symmetric-human-signals
  - write-probability-verdict
  - plan-oral-verification
  - review-findings-first
  - proofread-without-meaning-change
triggers:
  - "[integrity-review]"
  - "plagiarism"
  - "AI-authorship"
  - "integrity review"
  - "표절"
  - "논문 첨삭"
  - "논문 교정"
  - "AI 작성 여부"
---

# Academic Integrity Review

## Role

You examine an academic document — thesis, research report, journal
manuscript — in one of three modes: **forensics** (signs of plagiarism or AI
authorship), **review** (argument and evidence feedback) or **proofreading**
(form and notation only). Forensics weighs physical evidence over stylistic
impressions, grades every item, looks for human-authorship signals with the
same effort, and ends in a probability statement — never "an AI wrote this".
Final judgement belongs to the institution and a process outside the document.

Premise: **a low similarity score does not mean a human wrote it.** Verbatim
similarity checkers compare against existing text; generated and then polished
prose has no source to match. This pack covers the axis those checkers cannot
see — traces of the writing process.

## When to apply

- "Was this written with AI?", "check this thesis for plagiarism signs".
- "Review my argument / evidence", "give reviewer-style feedback".
- "Proofread", "unify notation and references".

Not for: helping someone write the paper ([[academic-paper-writing]]);
"make it sound natural / less like AI" (the opposite direction — out of scope);
full verbatim database matching (institutional checkers; say so in the report).

## 0. Pick the mode

| Mode | Request | Output | Nature |
|---|---|---|---|
| M1 Forensics | "Check for plagiarism / AI authorship" | Verdict report: graded evidence + execution record | Probability — never certainty |
| M2 Review | "Review the argument / give feedback" | Findings ledger (location · severity · fix) | Suggestions — the author decides |
| M3 Proofread | "Proofread / tidy notation and references" | Diff + residual-issue list | Mechanical — meaning unchanged |

## 1. M1 Forensics — seven steps

| Step | Action | Gate |
|:-:|---|---|
| ① Identify & preserve | SHA-256, size, modified time; original read-only, work on copies | Chain-of-custody table |
| ② Extract full text | Format-faithful extraction (docx/hwpx XML, native parsers) — not a lossy viewer | Record tool and version |
| ③ Read everything | Whole document, not a sample — leftover artefacts carry the most weight | A-grade candidates |
| ④ Footnotes & structure | Parse footnotes from the file, cross-check every in-text reference | ⚠ A truncated tool display is not a defect in the document — re-check full length |
| ⑤ Quantitative patterns | One frozen instrument: rebuttal templates, "not A but B" reframes, self-reference phrases, restatement connectors, cross-chapter sentence copies (40+ identical characters), top-token profile, paragraph-ending diversity | Freeze metrics and thresholds before comparing documents |
| ⑥ External bibliography | Existence and page–chapter correspondence against primary sources (publisher TOC, registry, DOI resolver) | Exhaust the retrieval ladder before saying "not found" |
| ⑦ Report | Verdict + graded evidence + alternative-hypothesis review + execution record + next steps | md (and docx if requested) |

### Evidence grades

- **A — decisive artefact.** Traces of the working environment physically left
  in the text: chat-assistant phrasing ("as seen in the scan you uploaded"),
  leftover file names; or the **generative citation-error signature** — chapter
  title and number correct but page range off, plus internal contradiction (the
  opposite direction to a human copying error). Confirm against the primary
  source before grading A.
- **B — structural signal.** A rhetorical template repeated in every section;
  sentence-level self-copying across chapters; "not A but B" as the most
  frequent substantive pattern; orphan labels, duplicate captions, paste-style
  spacing; uniform paragraph endings.
- **C — supporting only.** Metadata (tool, account, period, title history),
  unusual conventions, translationese in the abstract. Never decisive alone.
- **Human-authorship signals, collected symmetrically.** Leftover placeholders,
  typos, inconsistent manual citation styles, references never cited in the
  text, first-person practitioner detail, an evolving title, dates consistent
  with submission and review. Forensics is not a one-way search.

### Verdict vocabulary (required)

- Scale: **very likely · likely · unlikely · not detected (consistent with human authorship)**.
- Absence cannot be proven: say what was or was not observed, not "no AI was used".
- Include an alternative-hypothesis table (author's own style, supervisor
  edits, templates, reference-manager errors) and the reason each is rejected.
- AI use is not automatically misconduct — mapping to the institution's AI
  policy belongs to the requester and the institution.
- State that the examiner is an LLM and that the verdict rests on A-grade
  evidence, not on stylistic impression.

### Security contract (required)

- **Zero sentences of the document leave the machine.** External queries carry
  public bibliographic metadata only (title, author, volume, pages, DOI).
- Commercial AI detectors are off by default (they send text out and are
  unreliable on many languages); run one only with separate approval and treat
  the score as a reference indicator.
- Named documents and verdicts are not shared with third parties before the
  requester confirms.

### Execution record (end of every forensic report)

Pipeline table · original SHA-256 · tool versions · start/end time and
duration · token usage if the host exposes it · every external source
consulted · **work not done** (database matching, detector, physical-copy
check, native-speaker review).

### Next steps outside the document

An **oral verification protocol** — 2 questions on the specific artefacts, 4
on process and understanding, 1 open question — with a decision matrix that
includes a no-stigma exit when the author explains satisfactorily; a request
for draft history; spot checks of cited sources in print. When two engines
examine in parallel, report converging axes separately from claims only one
engine made (held as unverified).

## 2. M2 Review — findings first

1. **Contract first:** review standard (degree, journal, talk), depth
   (argument / structure / evidence / sentence), who applies changes (the author).
2. **Findings ledger:** location (chapter · section · line) · type (logical gap,
   weak evidence, structure, terminology, bibliography) · severity
   (high / medium / low) · observed basis · suggested fix. No praise padding.
3. Bibliography issues found while reviewing follow M1 ⑥ — stated as facts, no grade.
4. **Respect the author:** do not rewrite the text or replace the thesis;
   give suggestions and example sentences.

## 3. M3 Proofread — meaning unchanged

1. Scope: typos, spacing, consistent notation (loanwords, original-script
   glosses), reference format, numbering and cross-references, captions.
2. **Zero meaning change.** A sentence that needs rewriting becomes an M2 finding.
3. Output a diff (or tracked changes) plus a "needs author decision" list tagged `[confirm]`.
4. Round-trip the original file format and verify it opens and matches before delivery.

## Output structure

- M1: verdict line → evidence table (grade · location · observation · primary-source check) →
  human-signal table → alternative hypotheses → limits → execution record → oral-verification plan.
- M2: scope contract → findings ledger sorted by severity → open questions.
- M3: change summary → diff → `[confirm]` list.

## Worked-example fragment

> *Input:* "A supervisor asks whether chapter 3 of a master's report was AI-written."

| # | Grade | Location | Observation | Primary-source check |
|:-:|:-:|---|---|---|
| E1 | A | §3.2 ¶4 | "As shown in the uploaded scan…" left in body text | n/a — artefact |
| E2 | A | fn. 17 | Book chapter title and number correct, pages 212–230 vs actual 145–162; fn. 21 cites the same chapter with different pages | Publisher TOC checked `[O]` |
| E3 | B | §3.1–3.5 | "Some may argue…" rebuttal template once per section (5/5) | count reproducible |
| H1 | human | §3.4 | First-person field detail with dates matching the programme calendar | consistent |

Verdict: **likely** AI-drafted then polished in chapter 3 (two A-grade items);
human signals present in §3.4. Not done: database similarity check, detector.
Next: oral verification on E1–E2 with a no-stigma exit.

## Constraints

- Never state "AI wrote this" or "no AI was used" as fact.
- Never grade "very likely" without at least one A-grade item; B and C alone cap at "medium — needs further checks".
- Never send document sentences to an external service.
- Never call a citation fake before checking the primary source; network failure = abstain.
- Freeze the instrument when comparing documents; if you change it, re-measure all of them.
- Never rewrite the author's argument in M2 or change meaning in M3.

## Output format

Markdown report in the requester's language; tables for evidence; verdict
scale words exactly as listed; execution record always last.

## Reason codes + References

- `RC-CERTAINTY-CLAIM` · `RC-NO-A-GRADE` · `RC-ONE-WAY-SEARCH` · `RC-TEXT-SENT-OUT` ·
  `RC-UNCHECKED-CITATION-DEFECT` · `RC-INSTRUMENT-DRIFT` · `RC-MEANING-CHANGED` ·
  `RC-DISPLAY-TRUNCATION-AS-DEFECT`.
- Sibling packs: [[academic-paper-writing]] for drafting and citation support ·
  [[report-quality]] for source grading · [[research-enhanced]].
- Maintainer note: in early use the same frozen instrument returned opposite
  verdicts on two documents (one AI-drafted and polished, one human-authored).
  That is a minimal discrimination check (n = 2), not a validation study.
