# Resume Refinement Loop — Design

**Date:** 2026-07-23
**Status:** Approved by user (sections 1–3) pending spec review
**Scope:** Steps 4–6 of the `applying-to-job` skill (`C:\Users\Dhruv\.claude\skills\applying-to-job\SKILL.md`)

## Problem

The applying-to-job pipeline already contains two quality judges — the Step 5 keyword-coverage check and the Step 6 hiring-manager 10-second scan — but they run once, linearly, and only *report* findings. Nothing feeds their fixes back into the resume automatically. The user wants a "loop engineering" pattern: critique → revise → re-check until the resume converges, so every application reliably reaches the survives-a-skeptical-human bar with less manual back-and-forth.

**Honest framing (agreed with user):** the loop converges on explicit criteria, not "perfect." Past the point where the resume survives the 10-second scan with real keyword coverage, extra polish does not move callbacks — referrals and the Step 9 outreach kit do. The loop's value is reliably *reaching* that bar, not exceeding it.

## Goals

- Fold Steps 4–6 into a single bounded critique-revise loop on the markdown resume (`tailored-resume.md`).
- Make the Step 6 critique a genuinely cold read each round (fresh-eyes subagent).
- Replace the three per-step pauses (after Steps 4, 5, 6) with one pause at convergence, showing the full round history.
- Preserve every existing guardrail: no fabrication, one-page ceiling, Step 6 beats Step 5, keyword gaps stay gaps.

## Non-Goals

- No loop for the cover letter (Step 7 unchanged; may extend later if the resume loop proves out).
- No scripted/programmatic harness — the judges are LLM personas; the only computable check (page count) already lives in Step 10.
- No cross-application learning from callback outcomes (different feature).
- No changes to Steps 0–3 or 7–10, the repo scripts, or the Word templates.

## Design

### Loop mechanics (replaces the linear Steps 4 → 5 → 6)

1. **Step 4 — Tailor (unchanged content, no pause).** Produce `tailored-resume.md` v1 and `keyword-gaps.md` from the four `database/*.md` files + `jd-analysis.md`, under the existing rules (Google XYZ, no LLM tells, one-page budget, no unbacked keywords).
2. **Step 5 — Keyword coverage (inline, each round, no pause).** Run the existing coverage check in the main session against the current draft. Findings framed as covered / partially covered / genuinely missing, exactly as today.
3. **Step 6 — Hiring-manager scan (fresh critic, each round).** Dispatch a subagent whose prompt contains ONLY:
   - the role-track reviewer persona (dev / ML / analyst, from Preflight),
   - the hiring-manager-scan template,
   - the file paths to `jd-analysis.md` and the current `tailored-resume.md`.

   The critic has zero knowledge of the drafting process, the database files, or prior rounds — the same information a real reviewer has. It returns: verdict (READ DEEPER / REJECT), what it actually read in 10 seconds, red flags, and specific fixes — **each fix labeled `must-fix` (would push the verdict toward REJECT or wastes the 10-second read) or `nice-to-have` (polish)**. Convergence considers only `must-fix` items; `nice-to-have` items are applied when cheap but never trigger another round on their own.
4. **Triage + revise (main session).** For each suggested fix:
   - Backed by the `database/*.md` files → apply it to `tailored-resume.md` (replacing/tightening content, never appending past the one-page budget).
   - Requires a claim the database does not support → route to `keyword-gaps.md`; never applied. A loop cannot close a real gap.

   Then return to step 2 for the next round.
5. **Stop conditions (whichever hits first):**
   - **Converged:** critic verdict is READ DEEPER with no must-fix items remaining, AND coverage shows no genuinely-missing-but-real keywords.
   - **Round cap:** 3 rounds completed → stop and present the best version, with unresolved items flagged honestly at the pause.
   - **Oscillation:** the critic asks to undo a change a previous round requested → treat as converged (taste churn, not improvement); note it in the log.
6. **Single pause at convergence.** The user reviews: the final `tailored-resume.md`, the round-by-round `refinement-log.md`, and the final `keyword-coverage.md` + `hiring-manager-scan.md`. This replaces the current pauses after Steps 4, 5, and 6. All later pauses (Steps 7–10) are unchanged.

### Artifacts

- **New:** `applications/<slug>/refinement-log.md` — one short section per round: round number, critic verdict, key findings, fixes applied, items routed to `keyword-gaps.md`. Written incrementally as rounds complete.
- **New template:** `templates/refinement-log.template.md` in the skill folder (`C:\Users\Dhruv\.claude\skills\applying-to-job\templates\`).
- `hiring-manager-scan.md` and `keyword-coverage.md` hold the **final round's** versions (overwritten each round; history lives in the refinement log).
- `refinement-log.md` joins the artifact list committed to the application branch in After the Workflow.

### Files changed

- `C:\Users\Dhruv\.claude\skills\applying-to-job\SKILL.md`:
  - Steps 4–6 rewritten as the loop (personas and templates for Steps 4/5/6 kept verbatim).
  - Overview, Key Rules, and Common Mistakes updated to describe the loop, the single convergence pause, and the new artifact.
  - After the Workflow artifact list gains `refinement-log.md`.
- New file `templates/refinement-log.template.md` in the skill folder.
- Nothing in the job-hunting repo itself changes (this spec and its plan excepted).

### Guardrails

1. **Anti-fabrication is absolute and restated inside the loop text:** a critic's suggestion never overrides the no-unbacked-claims rule. Unsupported suggestions go to `keyword-gaps.md`.
2. **One-page budget respected during revision:** fixes replace or tighten; the final proof remains Step 10's Word page-count check.
3. **Step 6 beats Step 5** when they disagree, exactly as today.
4. **Critic failure fallback:** if the subagent errors or times out, run that round's critique inline in the main session, note the fallback in the log, and continue — the pipeline never stalls on infrastructure.
5. **Hard cap of 3 rounds** — diminishing returns past that are rewording churn.

### Error handling summary

| Failure | Handling |
|---|---|
| Critic subagent errors/times out | Inline critique for that round; noted in log |
| Critic suggests unbacked claim | Routed to `keyword-gaps.md`, never applied |
| Critic contradicts a previous round | Oscillation stop; converged; noted in log |
| Round cap hit without convergence | Present best version; unresolved items flagged at the pause |
| Revision threatens one-page budget | Replace/tighten instead of append; Step 10 remains the proof |

## Verification

Run the revised skill end-to-end on the next real JD and confirm:

1. The loop terminates within 3 rounds (converged, capped, or oscillation-stopped).
2. `refinement-log.md` exists with one section per round.
3. Every claim in the final `tailored-resume.md` traces to the `database/*.md` files (spot-check against the critic's applied fixes).
4. Exactly one review pause covers the resume stage (no pauses between rounds), and Steps 7–10 pause as before.
5. `refinement-log.md` is committed with the other artifacts on the application branch.

## Decisions log

- **Placement:** loop lives at Steps 4–6 on the markdown resume — judges already exist there, revision is cheap, downstream artifacts depend on a stable resume. (User approved.)
- **Scope:** resume only; cover letter excluded for now. (User chose.)
- **Critic:** fresh-eyes subagent per round (Approach B), over inline self-critique (A, soft self-review risk) and a scripted harness (C, can't run LLM-persona judges). (User chose B.)
- **Pauses:** single pause at convergence replaces the three per-step pauses. (User approved.)
