# Applying-to-Job Skill Revision — "Beat the Silence" Package

**Date:** 2026-07-13
**Status:** Approved design, pending implementation
**Skill under revision:** `C:/Users/Dhruv/.claude/skills/applying-to-job/` (personal skill)
**Repo affected:** `D:/github/job-hunting` (tracker file, one database fix, this spec)

## Context

A review of the skill after ~19 application branches (2026-07-06 through 2026-07-13) found the
document pipeline solid — fit gate, worktree isolation, XYZ bullets, honest keyword handling,
hiring-manager scan all work as designed — but surfaced two kinds of problems:

1. **Internal inconsistencies**: support templates that contradict the SKILL.md rules they serve.
2. **Strategic gaps**: the skill ends at the `.docx`, with no outreach, no company research, and
   no tracking — and the user's reported failure mode is **silence after submitting**, which is
   exactly what those gaps predict.

**User's goal:** land an AI/ML engineering role (dream track); other tracks are volume/backup.

**Chosen scope:** consistency fixes + outreach artifacts + application tracker + company
research, built into the pipeline as default steps (Approach A). Rejected alternatives: a
separate companion skill (relies on remembering to invoke it — reintroduces the follow-through
failure) and artifacts-only with no steps (passive, will be skipped under volume).

## 1. Consistency fixes

1. **`templates/ats-score.md` → rename to `templates/keyword-coverage.template.md`** and
   rewrite to match Step 5's "coverage check, not a score" framing:
   - Remove: `Overall Score XX/100`, per-dimension numeric scores, and the
     "Score Threshold Interpretation" section (85+/70–84/<70 gates).
   - Replace with: a table over the same six dimensions (required skills, preferred skills,
     action verbs, domain vocabulary, hard requirements, format/parse compliance) where each
     item is marked **covered / partially covered / genuinely missing**.
   - Keep: bullet→JD requirement mapping, keyword landing report, the `.docx` parse-safety
     checklist, and the "paste into Notepad" real-parse check.
   - Update the Step 5 template reference in SKILL.md.
2. **`templates/tailored-resume.template.md`**:
   - Add a `## Summary` section at the top (required by Step 4 rule 7 but absent).
   - Reorder sections to match the Word template: Summary → Technical Skills → Projects →
     Experience → Education.
   - Fix the stray `| |` typo in the second Project heading line.
3. **`templates/keyword-gaps.template.md`**: replace the footer ("add it to `master\master.md`
   and re-run Stage 3") with: add the forgotten experience to the appropriate `database/*.md`
   file and re-run Step 4.
4. **`database/master-personal-info.md`** (repo change, committed to main): remove the
   "Jake's Resume template" note; describe the heading in terms of the Word resume template.

## 2. Company research (folded into the cover-letter step — no extra pause)

The cover-letter step gains a **research pre-action** using web search, producing
`applications/<slug>/company-research.md` in the same step (single pause) as `cover-letter.md`:

- What the company builds; recent news / funding / launches.
- Tech-stack hints relevant to the role track.
- A salary range for the role + region from public sources (levels.fyi, Glassdoor, posted
  ranges), feeding the phone-screen step's salary bracket (replacing "for the candidate to
  research").
- Publicly listed recruiter / hiring-manager / team-lead names, for outreach targeting only.
  Names come only from public pages (company site, the posting, public LinkedIn results).

**Hard rule:** if search returns nothing useful, say so in the artifact and write the JD-only
cover letter — **never invent company facts.** Every company-specific claim in the cover letter
must trace to `company-research.md` or the JD.

Step 0 additionally gets a one-line quick sanity check (company is real, roughly what it does)
to inform the go/no-go — not the full research pass.

## 3. Outreach kit (new step, after the phone-screen narrative)

New step producing `applications/<slug>/outreach.md` with three drafts. All are **drafts the
user sends manually** — the skill never sends anything on the user's behalf.

1. **Referral request** — short message to a contact (named from Step 0 if one exists,
   otherwise a reusable 2nd-degree version: "do you know anyone at X?").
2. **Cold note to recruiter / hiring manager** — two lengths:
   - LinkedIn connection note, ≤300 characters.
   - Longer InMail/email version: the specific role applied to, one proof point from the
     tailored resume, a soft ask (15 minutes / keep me in mind / point me to the right person).
3. **Follow-up nudge** — pre-drafted for 5–7 business days after submission, containing one
   *new* proof point (not just "checking in").

Rules: personalize from `company-research.md`; no fabrication; scrub LLM tells; spoken-natural.
**For ML/AI-track postings this step is mandatory** — never skip outreach on the dream track.

New template: `templates/outreach.template.md`. Also new:
`templates/company-research.template.md` (for §2).

Persona: an outreach coach who has read thousands of cold messages as a recruiter and knows
what gets replies (short, specific, one clear ask) versus what gets ignored.

## 4. Application tracker (`tracker.md` at the repo root, on `main`)

One markdown table, one row per application:

`Date | Company | Role | Track | Branch | Status | Submitted | Outreach sent | Follow-up due | Response | Notes`

Status flow: `prepared → submitted → followed-up → screen → interview → offer | rejected | no-response`.

- **Location & safety:** written in the **main folder** (`D:/github/job-hunting/tracker.md`),
  never in a worktree. Safe because the skill never switches the main folder's branch. Commit
  immediately after every edit to minimize collision between parallel sessions; on conflict,
  re-read, reapply the row change, recommit.
- **Pipeline hook:** at the existing commit-artifacts moment (after `.docx` approval), add the
  row with status `prepared` and the outreach follow-up date. No new pause.
- **Standalone trigger:** the skill's frontmatter description gains wording so that status
  reports in any future session ("I submitted the Diligent one", "Jerry.ai rejected me",
  "update my job tracker") update the row without running the pipeline.
- **Follow-up surfacing:** whenever the tracker is touched, report any follow-ups now due or
  overdue.

The tracker file is created on first use with a header comment explaining the columns and
status values; no separate template file needed.

## 5. Skill structure changes

- **Step renumbering (0–10):** 0 fit/referral gate (+ quick sanity check) · 1 worktree ·
  2 profile load · 3 JD extraction · 4 tailor resume · 5 keyword coverage · 6 hiring-manager
  scan · 7 company research + cover letter · 8 phone-screen narrative · 9 outreach kit ·
  10 fill `.docx` + one-page verify. Pause count goes from 10 to 11.
- **Frontmatter description:** add outreach/tracker triggers so the skill fires on status
  reports and tracker requests, not only on new JDs.
- **After the Workflow:** add tracker registration, the standalone update rule, and the
  follow-up reporting rule. Artifact list gains `company-research.md` and `outreach.md`.
- **Key Rules additions:** (a) outreach kit is produced for every application and is mandatory
  for the ML/AI track; (b) every company-specific claim traces to `company-research.md` or the
  JD — never invent company facts; (c) register every application in `tracker.md` and update
  it when outcomes arrive.
- **Common Mistakes additions:** skipping outreach because the cover letter felt sufficient;
  letting the tracker rot (defeats the feedback loop); personalizing outreach with invented
  company facts; writing `tracker.md` inside a worktree.

## Error handling

| Failure | Behavior |
|---|---|
| Web search unavailable / no useful results | Note it in `company-research.md`; write the JD-only cover letter; phone-screen salary stays a bracketed to-research range |
| No public recruiter/HM contact found | Outreach kit still produced, with a role-generic recruiter note |
| Tracker commit conflict (parallel sessions) | Re-read `tracker.md`, reapply the row change, recommit |
| Cover-letter or resume template missing | Unchanged from current skill: pause and ask |

## Out of scope (explicitly deferred)

Surfaced in review but excluded from this revision by user choice: screening-question/form
answers artifact, master-database feedback loop, two-tier fast/full mode, worktree cleanup
nudges, technical/behavioral interview prep.

## Verification

1. Re-read the revised SKILL.md end-to-end for internal contradictions (especially step-number
   references and the Step 5 coverage framing vs. the renamed template).
2. Dry-run the new/changed steps (7, 9, tracker registration) against one existing ML/AI
   application branch (e.g. `2026-07-07-fgf-ai-engineer` or
   `2026-07-07-hellofresh-machine-learning-engineer`) and confirm sensible
   `company-research.md`, `outreach.md`, and a correct `tracker.md` row.
3. Confirm the standalone tracker trigger: simulate "I submitted X" in a fresh context and
   check the row updates and due follow-ups are reported.
