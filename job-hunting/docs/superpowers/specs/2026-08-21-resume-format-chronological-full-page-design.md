# Resume Format: Drop Summary, Chronological Order, Full Page, Awards

**Date:** 2026-08-21
**Status:** Approved
**Affects:** `C:/Users/Dhruv/.claude/skills/applying-to-job/` (SKILL.md + templates), `resume-template/resume-template.docx`, `database/master-education.md`, new `scripts/verify-resume-fit.ps1`

## Problem

Four changes to how the `applying-to-job` skill builds a resume:

1. Remove the Summary section.
2. Follow the chronological (reverse-chronological) format.
3. Fill the full page, with at least two bullet points on every Experience and Project entry.
4. Use this section order: **Experience, Projects, Technical Skills, Education, Awards.**

Requirement 3 directly reverses a rule the skill currently states emphatically in five places
("no fill target", "a three-quarter page beats a padded full one"). Leaving any of those in place
would make the skill contradict itself mid-run, so the reversal must propagate everywhere.

Requirement 4 introduces an **Awards** section that does not exist in the template, and moves
**Technical Skills** from the top of the document to below Projects.

Requirement 2 also exposes an existing factual bug: SKILL.md documents the template's section
order as `Summary, Technical Skills, Projects, Experience, Education`, but the actual
`resume-template.docx` is ordered `SUMMARY, TECHNICAL SKILLS, EXPERIENCE, PROJECTS, EDUCATION`.
Neither matches the target order, and the skill's own description of the template is wrong today.

## Evidence

**Page fill.** Measured with Word COM (`Range.Information(6)` = wdVerticalPositionRelativeToPage on
the last character, as a percentage of usable page height) across existing generated resumes:

| Application | Pages | Fill |
|---|---|---|
| 2026-07-13-larus-data-scientist | 1 | 97.0% |
| 2026-08-21-trudell-medical-data-analyst | 1 | 96.6% |
| 2026-08-21-scotiabank-data-analyst-business-enablement | 1 | 96.4% |
| 2026-08-21-carrington-ai-data-analyst | 1 | 95.7% |
| 2026-07-27-workstream-full-stack-engineer | 1 | 94.4% |
| 2026-08-21-stripe-data-analyst | 1 | 85.1% |

Good resumes cluster at 94-97%. A **92% pass line** accepts every resume that already reads as
full and flags only the genuinely short one.

**Source material.** `database/master-experience.md` holds 5 entries and `database/master-project.md`
holds 9, so a full page with >=2 bullets per entry is reachable without fabrication.

**Awards material is thin.** The database contains exactly two award-grade facts, both currently
embedded inside other sections:

- "Graduated with Distinction" — inside the B.Tech line, `master-education.md:9`
- "placed 2nd of 15+ teams at Northeastern's Agentic AI 2.0 Hackathon" — inside a Kahoot Bot
  project bullet, `master-project.md:103`

There are no certifications, GPA, scholarships, or other placements on record.

## Design

### A. Target section order

```
Name / contact heading
EXPERIENCE
PROJECTS
TECHNICAL SKILLS
EDUCATION
AWARDS          (conditional - see section E)
```

**Noted consequence:** moving Technical Skills below Projects means the top third of the page —
what the Step 6 hiring-manager 10-second scan reads — is now Experience only. The stack has to
surface through Experience and Project bullet text rather than through a skills block near the top.
Step 6's persona instructions are updated to account for this rather than flagging it as a defect.

### B. Template surgery

Edit `resume-template/resume-template.docx` (`word/document.xml`) and commit it. The template is the
format's source of truth; leaving stale or mis-ordered slots invites drift. All changes are
paragraph-level moves and clones — no style, font, or numbering definitions are altered:

1. **Delete** the `SUMMARY` heading and its body paragraph (paragraphs 2-3).
2. **Move** the `TECHNICAL SKILLS` block (heading + 4 category rows, paragraphs 4-7) to sit after
   the `PROJECTS` block.
3. **Append** an `AWARDS` section after `EDUCATION`: clone the `EDUCATION` heading paragraph and
   swap its text (preserving the `2B579A` blue bottom border and the bold blue 9.5pt run styling),
   then add two award-line paragraphs cloned from the education-entry pattern (right tab stop at
   10973 twips for the right-aligned date).

Bullet numbering (`numId 1`) appears only inside Experience and Projects, which move as intact
blocks, so list numbering is unaffected.

### C. Chronological format

- Correct both misstatements of the template order in SKILL.md (Step 4 rule 1, Step 10 item 1) to
  the target order in section A.
- Add an explicit rule to Step 4: the resume uses the **reverse-chronological** format. Experience
  always precedes Projects. Within each section, entries run newest first. Every entry carries a
  date range. Projects never lead the document, even when they are the stronger material — that
  strength is expressed through bullet quality and ordering, not by displacing Experience.
- Reorder `templates/tailored-resume.template.md` to match, drop its `## Summary` block, and add an
  `## Awards` block.

### D. Fill rule reversal

Replace the anti-fill language everywhere it appears:

| Location | Current | Becomes |
|---|---|---|
| Overview "Length rule" paragraph | "ceiling, not a fill target ... no requirement to fill the page" | "fills the page, and never spills onto a second" |
| Step 4 rule 6 | "One page maximum - never pad to fill it ... no minimum fill" | "Exactly one full page": fill with real JD-relevant content, hard 1-page ceiling |
| Step 10 item 4 | "no vertical-fill target - do NOT regenerate just because the bottom has whitespace" | run the fit check; fail on under-fill as well as overflow |
| Key Rule 9 | "One page maximum, never padded to fill" | "One full page - fill it with real content, never cross onto a second" |
| Common Mistakes: "Padding the resume with weak or old bullets" | "Fill is not a goal" | inverted: under-filled page is the mistake; fix by adding real material |

**The anti-fabrication guard survives unchanged.** The page is filled by drawing more real material
from the database files (another true bullet, another relevant entry), never by inventing claims,
inflating line spacing, enlarging fonts, or widening margins. If the strongest honest material
genuinely cannot reach 92%, the skill reports the shortfall to the user for a call rather than
padding silently.

### E. Awards section

**Canonical source.** Add an `## Awards & Honors` block to `database/master-education.md` listing
both known items with dates. This keeps the profile at four master files rather than introducing a
fifth (the skill asserts "the four `database/*.md` files are the master" in many places, and a
fifth file would mean churn across all of them). Honors and academic placements are
education-adjacent, so the fit is natural.

**One canonical home per fact on the rendered resume.** A fact rendered in Awards is not repeated
elsewhere on the same resume:

- The B.Tech education entry drops "Graduated with Distinction" when Awards carries it.
- The Kahoot Bot project bullet drops the "placed 2nd of 15+ teams" clause when Awards carries it.
  That bullet keeps its 90%-accuracy and 60%-cost-reduction evidence, which is the stronger signal
  anyway.

The database keeps the full, rich record in both places; the de-duplication is a **rendering rule**
applied when building the resume, not a deletion from the master files.

**Conditional inclusion.** Awards appears only when the database yields **2 or more** genuine
items. Below that it is omitted entirely rather than shipped as a one-line stub — consistent with
the >=2-bullets rule for Experience and Projects. With the two items on record it renders today,
but the rule keeps a future thin-material case from producing a stub.

**Thin-material flag.** Because Awards currently holds only two items, Step 4 notes the shortfall
to the user in its summary, in the same spirit as `keyword-gaps.md`: real certifications, placements
or scholarships would strengthen the section, and only the user can supply them. The skill never
invents an award.

### F. Minimum two bullets per entry

New Step 4 rule: every Experience entry and every Project entry carries **at least two** bullet
points. An entry that can only justify one real bullet is either merged into a stronger entry or
dropped, never shipped as a one-line stub.

This interacts with trimming: when the resume overflows, cut whole low-value entries rather than
reducing a surviving entry below two bullets.

Mirrored in `templates/tailored-resume.template.md` (which currently shows a one-bullet project as
acceptable) and in Step 10's mapping instructions. Education entries and Awards lines have no
bullets and are unaffected.

### G. Verification script

New `scripts/verify-resume-fit.ps1`, invoked by Step 10:

```
powershell -File scripts/verify-resume-fit.ps1 -Path <resume.docx> [-MinFill 92]
```

Behavior:
- Opens the `.docx` read-only through Word COM.
- Reads `ComputeStatistics(2)` for page count and `Range.Information(6)` on the last character for
  the last line's vertical position.
- Computes `fill% = (vertPos - topMargin) / (pageHeight - topMargin - bottomMargin) * 100`.
- **PASS** when `pages == 1` and `fill >= MinFill`.
- **FAIL (overflow)** when `pages > 1` -> trim per Step 4 rule 6.
- **FAIL (underfill)** when `fill < MinFill` -> add real content per Step 4 rule 6.
- Prints a single machine-readable line plus a human verdict, and exits non-zero on failure.
- Always closes the document and quits Word, even on error, so no stray `WINWORD` processes leak.

The script lives in the repo (not inline in SKILL.md) so it is reusable across runs and keeps the
skill document readable. Step 10 keeps the existing guidance to kill stray `WINWORD` processes and
retry if a Word call hangs.

The cover letter keeps its existing check: `pages <= 1`, with **no** fill requirement. The
full-page rule applies to the resume only.

## Out of scope

- The 5 in-flight `2026-08-21-*` worktree applications keep their already-approved resumes. This
  design governs future runs.
- No change to the cover-letter template or its 12pt body override.
- No change to keyword-coverage, hiring-manager-scan, company-research, phone-screen, or outreach
  stages beyond removing stale Summary references and the Step 6 top-third note in section A.

## Verification

1. `resume-template.docx` opens cleanly in Word with no SUMMARY section, an AWARDS section, and
   sections in the order: Experience, Projects, Technical Skills, Education, Awards.
2. `scripts/verify-resume-fit.ps1` reproduces the measured table above: 92%+ resumes PASS, the
   85.1% Stripe resume FAILs with an underfill verdict.
3. `grep -ri summary` over the skill returns no instruction to produce a resume Summary.
4. No sentence anywhere in SKILL.md still tells the reader not to fill the page.
5. Every stated section order in SKILL.md and `tailored-resume.template.md` matches section A.
