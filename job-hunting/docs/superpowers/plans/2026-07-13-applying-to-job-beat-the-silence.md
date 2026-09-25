# Applying-to-Job "Beat the Silence" Revision — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Revise the personal `applying-to-job` skill so every application ships with company research, an outreach kit, and a tracker row — plus fix four internal inconsistencies — per the approved spec at `docs/superpowers/specs/2026-07-13-applying-to-job-review-design.md`.

**Architecture:** All skill logic lives in markdown under `C:/Users/Dhruv/.claude/skills/applying-to-job/` (NOT a git repo — no commits there; verify each edit by re-reading). Repo-side changes (`tracker.md`, one database note, this plan) are additive commits directly to `main` in `D:/github/job-hunting`, matching repo convention. No worktree needed: most files live outside any git repo and the repo changes don't touch application branches.

**Tech Stack:** Markdown skill files, Git (job-hunting repo only), web search (dry-run task only).

**Editing discipline:** SKILL.md tasks change an existing skill — the executor should follow `superpowers:writing-skills` principles (keep the skill's voice, don't dilute existing hard rules, exact paths).

**Important paths:**
- Skill folder: `C:/Users/Dhruv/.claude/skills/applying-to-job/` (abbreviated below as `<skill>/`)
- Repo: `D:/github/job-hunting`

---

### Task 1: Rewrite `tailored-resume.template.md` (Summary section + Word-template order + typo)

**Files:**
- Rewrite: `<skill>/templates/tailored-resume.template.md`

- [ ] **Step 1: Replace the entire file with this content** (adds `## Summary`, reorders to Summary → Technical Skills → Projects → Experience → Education to match the Word template, fixes the `| |` typo, adds the portfolio URL to the heading line):

```markdown
# {{FULL NAME}}

{{phone}} | {{email}} | {{linkedin URL}} | {{github URL}} | {{portfolio URL}} | {{city, state}}

---

## Summary

{{2-3 lines max — or keep it minimal if the substance is thin (Step 4 rule 7). Shape: [Discipline/role] with [background]. Built [a specific, real thing] that [quantified result]. Strong in [2-3 real, JD-relevant skills]. Targeting [role type]. Banned openers: "A [X] professional with a passion for…", "Passionate about…", "Results-driven…", "Seeking opportunities to…".}}

---

## Technical Skills

**Languages:** {{Python, JavaScript, TypeScript, Go, SQL}}
**Frameworks:** {{React, Node.js, Express, Django, Flask}}
**Developer Tools:** {{Git, Docker, Kubernetes, AWS, GCP, Jenkins}}
**Libraries:** {{pandas, NumPy, scikit-learn, TensorFlow}}

---

## Projects

**{{Project Name}}** | {{Start Month YYYY}} – {{End Month YYYY (or Present)}}

- {{What you built + impact metric + technical approach}}
- {{Second bullet if needed}}

**{{Project Name}}** | {{Start Month YYYY}} – {{End Month YYYY (or Present)}}

- {{Bullet}}

---

## Experience

**{{Company Name}}** | {{City, State}}
*{{Job Title}}* | {{Start Month YYYY}} – {{End Month YYYY (or Present)}}

- {{Action verb + what you did + quantified result + how/method - Google XYZ formula}}
- {{Action verb + what you did + quantified result + how/method}}
- {{Action verb + what you did + quantified result + how/method}}

**{{Company Name}}** | {{City, State}}
*{{Job Title}}* | {{Start Month YYYY}} – {{End Month YYYY}}

- {{Bullet}}
- {{Bullet}}

---

## Education

**{{University Name}}** | {{City, State}}
*{{Degree, Major}}* | {{Start Month YYYY}} – {{End Month YYYY}}

**{{University Name (if second degree)}}** | {{City, State}}
*{{Degree, Major}}* | {{Start Month YYYY}} – {{End Month YYYY}}
```

- [ ] **Step 2: Verify** — Read the file back; confirm section order is Summary, Technical Skills, Projects, Experience, Education and no `| |` double-pipe remains: `grep -n "| |" <skill>/templates/tailored-resume.template.md` → no matches.

---

### Task 2: Fix stale footer in `keyword-gaps.template.md`

**Files:**
- Modify: `<skill>/templates/keyword-gaps.template.md` (final section, "Master Resume Updates Suggested")

- [ ] **Step 1: Edit** — replace:

```markdown
If any "Real Gap" keyword represents an experience you *do* have but forgot to include in the master, add it to `master\master.md` and re-run Stage 3.
```

with:

```markdown
If any "Real Gap" keyword represents an experience you *do* have but forgot to include in the master, add it to the appropriate `database/*.md` file (experience/project/education) and re-run Step 4 (Tailor Resume).
```

- [ ] **Step 2: Verify** — `grep -n "master.md\|Stage 3" <skill>/templates/keyword-gaps.template.md` → no matches.

---

### Task 3: Replace `ats-score.md` with `keyword-coverage.template.md`

**Files:**
- Create: `<skill>/templates/keyword-coverage.template.md`
- Delete: `<skill>/templates/ats-score.md`

- [ ] **Step 1: Create `<skill>/templates/keyword-coverage.template.md`** with this content (keeps the six dimensions, bullet→JD mapping, landing report, parse-safety checklist and Notepad check from the old template; removes the /100 score, per-dimension scores, and the 85+/70–84/<70 threshold table):

```markdown
# Keyword Coverage — {{COMPANY}} {{ROLE}}

> Checked by Claude acting as a recruiting-ops analyst. **This is a coverage check, not a score.**
> For most employers, Workday/Greenhouse/Lever parse and store the resume so a recruiter can
> search it — they do not compute a pass/fail number. A human still reads you. When this check
> and the hiring-manager scan (Step 6) disagree, the human read wins.
> Target resume format: .docx (single-column Word document).

## Coverage Summary

Every finding is **covered / partially covered / genuinely missing** — never a number.
Route every *genuinely missing* keyword to `keyword-gaps.md`; never invent coverage.

| Dimension | Coverage | Notes |
|---|---|---|
| Required-skill coverage | {{covered / partially covered / genuinely missing}} | {{e.g., "7 of 8 required skills present with the JD's phrasing; 'Terraform' genuinely missing → keyword-gaps.md"}} |
| Preferred-skill coverage | {{...}} | {{e.g., "4 of 6 preferred present; K8s and Go are real gaps"}} |
| Action-verb alignment | {{...}} | {{e.g., "JD's responsibility verbs (design, ship, own) mirrored where the claims are true"}} |
| Domain-vocabulary match | {{...}} | {{e.g., "6 of 8 domain terms appear naturally in bullets"}} |
| Hard-requirement satisfaction | {{...}} | {{e.g., "Degree ✓, authorization ✓, 2+ yrs ✓"}} |
| Format / parse compliance | {{Pass / issues found}} | {{"Single column, standard headings, ≤ one page, native .docx text"}} |

## Bullet → JD Requirement Mapping

- **Resume bullet:** "{{quote bullet 1}}"
  **Maps to JD:** "{{quote JD line}}"
  **Why it works:** {{specific reasoning — skill match, scale match, quantification}}

- **Resume bullet:** "{{quote bullet 2}}"
  **Maps to JD:** "{{quote JD line}}"
  **Why it works:** {{reasoning}}

- **Resume bullet:** "{{quote bullet 3}}"
  **Maps to JD:** "{{quote JD line}}"
  **Why it works:** {{reasoning}}

## Keyword Landing Report

- "**{{keyword 1}}**" appears in: Skills section AND Experience bullet 2 — named in Skills so it surfaces in a recruiter's keyword search, and proven in a bullet so it reads as real to the human
- "**{{keyword 2}}**" appears in: Experience bullet 1 with quantified context
- "**{{keyword 3}}**" appears in: Skills section, Technical Skills > Languages

## Format/Parsing Predictions (.docx)

- Single column, text flows top-to-bottom → parses cleanly across Workday/iCIMS/Taleo/Greenhouse. A well-built .docx is often parsed *more* reliably than a PDF, so this format is a safe choice.
- No tables used for layout/alignment → avoids the single most common Word parse failure. Parsers frequently read table cells out of order or flatten them, so any side-by-side alignment is done with tabs/indentation, not tables.
- No text boxes, no SmartArt, no WordArt → text inside these elements is often dropped entirely by parsers.
- No images with embedded text, and no resume-as-image → all content is live, selectable text.
- Contact info lives in the document body, not in the header/footer → header/footer content is unreliable and sometimes ignored.
- Standard fonts + standard section headings ("Experience", "Education", "Skills") → section detection and field mapping succeed.
- Saved as **.docx**, not legacy **.doc** → the modern XML format parses more reliably than the old binary format, which some ATS handle poorly.

> **Real parse check — do this, don't just eyeball the checklist:** open the actual .docx, Select All → Copy → paste into a plain-text editor (Notepad). If every line comes out in the right order with nothing missing or scrambled, the parser will read it the same way. If a table interleaves, a text box vanishes, or the dates scatter, that's a real problem the visual checklist above will not catch on its own.

## Suggestions

1. {{Specific actionable suggestion — e.g., "Bullet 4 in the Acme role is unquantified; a quantified alternative exists in master-experience.md"}}
2. {{Suggestion — e.g., "JD's 'reconciliation' has a true supporting bullet in master-project.md that isn't surfaced"}}
3. {{Suggestion}}
```

- [ ] **Step 2: Delete the old template** — remove `<skill>/templates/ats-score.md`.

- [ ] **Step 3: Verify** — `Get-ChildItem <skill>/templates/` shows `keyword-coverage.template.md` and NOT `ats-score.md`; `grep -rn "Overall Score\|/100\|85+" <skill>/templates/` → no matches.

*(SKILL.md's Step 5 reference to the old path is updated in Task 7.)*

---

### Task 4: Create `company-research.template.md`

**Files:**
- Create: `<skill>/templates/company-research.template.md`

- [ ] **Step 1: Create the file** with this content:

```markdown
# Company Research — {{COMPANY}} {{ROLE}}

> Researched by Claude acting as a company-research analyst, via web search on {{YYYY-MM-DD}}.
> **Every fact below must trace to a source in the Sources list.** If search returned nothing
> useful for a section, write "Nothing found — do not invent" and move on. Names only from
> public pages (company site, the posting itself, public LinkedIn results).

## What the company builds

- {{Product/service in 2-3 plain lines, and who the customer is}}

## Recent signals (news / funding / launches)

- {{e.g., "Series C, $85M, Mar 2026 — TechCrunch"}}
- {{Recent launch or announcement relevant to this role}}

## Tech-stack hints (for the {{role track}} track)

- {{From the JD, engineering blog, conference talks, job-board postings}}

## Salary range ({{role}}, {{region}})

- {{Source (posted range / levels.fyi / Glassdoor)}}: {{range}}
- **Bracket for the phone screen (Step 8):** {{e.g., "CAD 85–105k base, per Glassdoor for Vancouver"}} — the candidate confirms before quoting it. If nothing found, leave the Step 8 bracket as a to-research placeholder.

## People (public sources only — for Step 9 outreach targeting)

| Name | Role | Source URL | Outreach relevance |
|---|---|---|---|
| {{name or "none found"}} | {{Recruiter / hiring manager / team lead}} | {{public URL}} | {{e.g., "recruiter listed on the posting — target for the cold note"}} |

## Cover-letter angles

- {{1-3 specific, TRUE hooks connecting something researched to the candidate's real experience — each must trace to a source above AND to a database/*.md fact}}

## Sources

- {{URL — what it supported}}
- {{URL — what it supported}}
```

- [ ] **Step 2: Verify** — Read the file back; confirm the "never invent" rule and the Sources section are present.

---

### Task 5: Create `outreach.template.md`

**Files:**
- Create: `<skill>/templates/outreach.template.md`

- [ ] **Step 1: Create the file** with this content:

```markdown
# Outreach Kit — {{COMPANY}} {{ROLE}}

> **Drafts only — the user sends everything manually.** Every claim traces to the database
> files, `tailored-resume.md`, or `company-research.md`. No fabricated familiarity ("long-time
> fan of…" only if provably true), no LLM tells (see references/llm-tells.md), spoken-natural,
> ONE clear ask per message.

## 1. Referral request

**If a contact exists** (named in `fit-and-referral.md`) — to {{contact name}}:

{{2-4 sentences: I'm applying to [role] at [company] (link). One line on why it's a genuine
fit (real proof point). Direct ask: "Would you be open to referring me?" Offer to send the
resume + tailored blurb. End with an easy out ("totally fine if not").}}

**If no direct contact** (2nd-degree ask, reusable with any acquaintance):

{{2-3 sentences: I'm applying to [role] at [company] — do you know anyone there (or anyone
who'd know someone) I could talk to for 10 minutes before I apply cold?}}

## 2. Cold note to the recruiter / hiring manager

**Target:** {{name + role from company-research.md People table, else "the recruiter attached to the posting"}}

**LinkedIn connection note (≤300 characters — count them):**

{{Applied for [role]. One proof point with a number. Soft ask: would value 15 minutes, or
"keeping my application on your radar."}}

**Longer version (InMail / email):**

{{4-6 sentences: the specific role + req ID if any; the single most relevant proof point,
quantified; ONE company-specific line drawn from company-research.md; a soft ask (15 minutes,
or "point me to the right person"); sign-off with name + LinkedIn/portfolio link.}}

## 3. Follow-up nudge (send on {{submitted date + 5–7 business days}})

{{3-4 sentences: still interested in [role]; one NEW proof point that was NOT in the first
message; one line reiterating fit; soft close. Never just "checking in."}}

## Send checklist

- [ ] Connection note is ≤300 characters (count, don't estimate)
- [ ] Every claim defensible from the database files in one sentence
- [ ] No LLM tells; reads spoken-natural
- [ ] Exactly one ask per message
- [ ] Names and company facts trace to company-research.md public sources
- [ ] Follow-up date written into the tracker row (see After the Workflow)
```

- [ ] **Step 2: Verify** — Read the file back; confirm the three message sections and the "drafts only" rule are present.

---

### Task 6: SKILL.md — frontmatter description + Overview + workflow heading

**Files:**
- Modify: `<skill>/SKILL.md` (frontmatter lines 1-4; Overview paragraphs; the `## Workflow` heading)

- [ ] **Step 1: Replace the frontmatter `description:` value** with:

```
Use when you paste or provide a job description and want to prepare a complete tailored job application, when starting a new application from a posting in the job-hunting repo, or when asked to apply to a specific company/role. Runs a fit-and-referral gate first (is this worth applying to, and who can refer you?), then handles branch/worktree creation, resume tailoring, a keyword-coverage check, a hiring-manager scan, company research, a cover letter, a recruiter phone-screen narrative, an outreach kit (referral request, recruiter cold note, follow-up nudge), Word (.docx) output filled from the user's provided templates, and registration in the application tracker (tracker.md). ALSO use this skill when the user reports an application status — "I submitted X", "they rejected me", "I got a phone screen", "no response yet" — or asks to update or check the job tracker or follow-ups due.
```

- [ ] **Step 2: Update the Overview "sandwich" paragraph** — replace the sentence ending `…and it closes with a **recruiter phone-screen narrative** (Step 8 — the 30-second verbal answer you'll actually be judged on). The polished `.docx` is the middle of the sandwich, not the whole meal.` with:

```
…and it closes with a **recruiter phone-screen narrative** (Step 8) and an **outreach kit** (Step 9 — the referral request, recruiter cold note, and follow-up nudge that put the application in front of a human instead of leaving it in a database). The polished `.docx` is the middle of the sandwich, not the whole meal. Every application also gets a row in **`tracker.md`** (repo root, on `main`) so submissions, follow-ups, and outcomes stop disappearing into silence.
```

- [ ] **Step 3: Update the one-page-verify sentence in the Overview** — change `Verify that each fits on one page in Microsoft Word (Step 9).` to `Verify that each fits on one page in Microsoft Word (Step 10).`

- [ ] **Step 4: Update the self-contained-assets sentence** — change `the JD-extraction, resume, keyword-coverage, hiring-manager-scan, cover-letter, and phone-screen steps use this skill's own reference and template files` to `the JD-extraction, resume, keyword-coverage, hiring-manager-scan, company-research, cover-letter, phone-screen, and outreach steps use this skill's own reference and template files`.

- [ ] **Step 5: Update the workflow heading** — change `## Workflow — Step 0 through Step 9` to `## Workflow — Step 0 through Step 10`.

- [ ] **Step 6: Verify** — `grep -n "Step 9\|Step 10" <skill>/SKILL.md` and confirm the Overview now references Step 10 for the Word verify; frontmatter parses (opens/closes with `---`).

---

### Task 7: SKILL.md — Step 0 sanity check + Step 5 template path + Step 7 rewrite (research + cover letter)

**Files:**
- Modify: `<skill>/SKILL.md` (Step 0 Action list; Step 5 Action paragraph; entire Step 7 section)

- [ ] **Step 1: Step 0 — add a quick sanity check.** Change the Action lead-in from `**Action — two quick checks, presented to the user for a go / no-go before any workspace is built:**` to `**Action — three quick checks, presented to the user for a go / no-go before any workspace is built:**`, and insert this as new item 1 (renumber the existing Fit check to 2 and Referral scan to 3):

```markdown
1. **Quick company sanity check (one line, not the deep dive).** If the company is unfamiliar, web-search it: is it real, what does it roughly build, any red flags (scam signals, ghost-job reposting)? One line in the verdict. The deep research pass happens at Step 7 — do not spend time on it here.
```

- [ ] **Step 2: Step 5 — point at the new template.** Change `Using C:/Users/Dhruv/.claude/skills/applying-to-job/templates/ats-score.md, read its six dimensions` to `Using C:/Users/Dhruv/.claude/skills/applying-to-job/templates/keyword-coverage.template.md, read its six dimensions`.

- [ ] **Step 3: Replace the entire `### Step 7 — Cover Letter` section** with:

```markdown
### Step 7 — Company Research + Cover Letter

Two parts, one pause: research first, then the letter that uses it.

**Part A — Company research.**

**Role:** *Act as a company-research analyst who preps candidates for competitive applications. You find what the company actually builds, what changed recently (funding, launches, news), what the team's stack looks like, what the role pays in this region, and which humans are publicly attached to the role — and you never state a fact you cannot source.*

**Action:** Web-search the company and produce `applications/<slug>/company-research.md` via `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/company-research.template.md`: what they build, recent news/funding, tech-stack hints for the role track, a salary range for the role + region from public sources (posted range, levels.fyi, Glassdoor), publicly listed recruiter / hiring-manager / team-lead names (public pages only — these feed Step 9 outreach targeting), and 1-3 cover-letter angles. **If search returns nothing useful for a section, write "Nothing found — do not invent" and move on. Never fabricate company facts.**

**Part B — Cover letter.**

**Role:** *Act as an expert cover-letter writer who has drafted 2,000+ letters that landed interviews at top tech companies. You write concise, specific, non-generic letters that connect the candidate's real accomplishments to the role's actual needs. You never fabricate, never pad with fluff, and never sound like a template.*

**Inputs:** `jd-analysis.md` + `tailored-resume.md` + `company-research.md` + the four `database/*.md` files.

**Rules:**
1. One page, ~3-4 short paragraphs: hook + why this company/role, 1-2 proof paragraphs tying real accomplishments to the JD's top requirements, close with a call to action.
2. Every claim about the candidate traces to the database files. Never fabricate — a keyword gap stays a gap (see `keyword-gaps.md`).
3. **Every claim about the company traces to `company-research.md` (sourced) or the JD.** If the research came up empty, write the JD-only version — company claims stay generic-but-true, never invented.
4. Scrub LLM tells per `C:/Users/Dhruv/.claude/skills/applying-to-job/references/llm-tells.md` (no em dashes, no "leveraged/robust/seamless/passionate about", etc.).
5. Use the real contact block from `database/master-personal-info.md`. Address to the hiring team/manager; use the company name.

**Outputs:** `applications/<slug>/company-research.md` + `applications/<slug>/cover-letter.md` (via `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/cover-letter.template.md`).

**Pause once, covering both artifacts.**
```

- [ ] **Step 4: Verify** — `grep -n "ats-score" <skill>/SKILL.md` → no matches; `grep -n "company-research" <skill>/SKILL.md` → hits in Step 7; Step 0 has three checks.

---

### Task 8: SKILL.md — Step 8 salary line + new Step 9 (Outreach Kit) + renumber docx step to 10

**Files:**
- Modify: `<skill>/SKILL.md` (Step 8 inputs + item 3; insert new Step 9 section; retitle old Step 9)

- [ ] **Step 1: Step 8 inputs** — change `**Inputs:** jd-analysis.md + tailored-resume.md + the four database/*.md files + keyword-gaps.md.` to `**Inputs:** jd-analysis.md + tailored-resume.md + company-research.md + the four database/*.md files + keyword-gaps.md.`

- [ ] **Step 2: Step 8 salary answer** — change the item-3 parenthetical `and "salary expectations" (a bracketed range for the candidate to research/confirm — never a fabricated number)` to `and "salary expectations" (use the researched range from company-research.md as the bracket when it found one — the candidate confirms it before quoting; if research found nothing, keep a bracketed to-research placeholder — never a fabricated number)`.

- [ ] **Step 3: Insert the new Step 9 section** between Step 8 and the docx step:

```markdown
### Step 9 — Outreach Kit (mandatory for ML/AI-track postings)

**Why this exists:** a cold application with no outreach is how applications disappear into silence. A referral, or a two-line note to the right recruiter, moves the application out of the ATS database and into a human's field of view — for response rate, this is the highest-leverage artifact in the pipeline.

**Role:** *Act as an outreach coach who spent years as an in-house recruiter reading cold messages. You know what gets replies — short, specific, one clear ask, one real proof point — and what gets ignored: long messages, flattery, vague "any opportunities?" asks, and fake familiarity.*

**Inputs:** `fit-and-referral.md` (the contact, if Step 0 found one) + `company-research.md` (people + angles) + `tailored-resume.md` + `jd-analysis.md`.

**Action:** Produce `applications/<slug>/outreach.md` via `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/outreach.template.md` with three drafts:
1. **Referral request** — addressed to the named contact from Step 0 if one exists, otherwise the reusable 2nd-degree version ("do you know anyone at X?").
2. **Cold note to the recruiter / hiring manager** — targeted at a name from `company-research.md` when one is public, otherwise role-generic. Two lengths: a ≤300-character LinkedIn connection note AND a longer InMail/email version with one quantified proof point and a soft ask.
3. **Follow-up nudge** — pre-dated 5–7 business days after submission, containing one NEW proof point (never just "checking in").

**Rules:** drafts only — **never send anything; the user sends manually.** No fabrication, no fake familiarity, scrub LLM tells. **ML/AI-track postings: never skip this step** — that is the dream track, and cold-applying there without outreach is what produces silence. Other tracks: produce it anyway; the user chooses whether to send.

**Pause.**
```

- [ ] **Step 4: Renumber the docx step** — change the heading `### Step 9 — Fill the Word (.docx) templates + one-page verify` to `### Step 10 — Fill the Word (.docx) templates + one-page verify`. Then fix the two remaining in-body references: in Step 4 rule 1 change `at Step 9` to `at Step 10`; in Step 4 rule 6 change `verified in Word at Step 9` to `verified in Word at Step 10`.

- [ ] **Step 5: Verify** — `grep -n "Step 9" <skill>/SKILL.md` → every remaining hit refers to the Outreach Kit; `grep -n "Step 10" <skill>/SKILL.md` → docx references all updated (Overview, Step 4 ×2, heading).

---

### Task 9: SKILL.md — After the Workflow: artifact list + tracker registration + standalone updates

**Files:**
- Modify: `<skill>/SKILL.md` (the `## After the Workflow` section)

- [ ] **Step 1: Extend the artifact list** — in the first paragraph, change `…cover-letter.md, phone-screen-narrative.md, resume.docx, cover-letter.docx.` to `…company-research.md, cover-letter.md, phone-screen-narrative.md, outreach.md, resume.docx, cover-letter.docx.`

- [ ] **Step 2: Insert this block immediately after the existing commit-artifacts code block and its "One commit per posting…" paragraph:**

```markdown
**Register the application in `tracker.md` (right after committing the artifacts).**

`tracker.md` lives at the repo root in the **MAIN folder** (`D:/github/job-hunting/tracker.md`), on `main` — **never inside a worktree.** (The main folder never switches branches, so writing there is safe alongside parallel worktrees.) If the file doesn't exist, create it with the exact header below. Append one row for this application with Status `prepared`, then commit immediately — small immediate commits are what keep parallel sessions from colliding. If the commit conflicts with a parallel session, re-read the file, reapply your row, and commit again.

    git -C "D:/github/job-hunting" add tracker.md
    git -C "D:/github/job-hunting" commit -m "tracker: <slug> prepared"

Tracker file format (used verbatim to create the file if missing):

    # Application Tracker

    > One row per application. Status flow: prepared → submitted → followed-up → screen → interview → offer | rejected | no-response.
    > Follow-up due = Submitted + 5–7 business days (send the outreach.md nudge). Dates are YYYY-MM-DD.
    > Update rows in the MAIN folder only (never a worktree); commit after every change.

    | Date | Company | Role | Track | Branch | Status | Submitted | Outreach sent | Follow-up due | Response | Notes |
    |---|---|---|---|---|---|---|---|---|---|---|

**Standalone tracker updates (no pipeline run needed):** when the user reports a status in ANY session — "I submitted the Diligent one", "Jerry.ai rejected me", "I got a screen", "update the tracker" — update that application's row in the main folder: set Status and the relevant date columns, compute Follow-up due (Submitted + 5–7 business days) when they report submitting, note responses, and commit. **Every time you touch `tracker.md`, finish by listing any follow-ups now due or overdue** (today ≥ Follow-up due, Status is submitted/followed-up, and Response is empty) so the user knows exactly which nudges to send today.
```

- [ ] **Step 3: Verify** — Read the After the Workflow section; confirm tracker block sits before the Cleanup subsection and the artifact list has 13 items.

---

### Task 10: SKILL.md — Key Rules + Common Mistakes additions

**Files:**
- Modify: `<skill>/SKILL.md` (the `## Key Rules` numbered list and the `## Common Mistakes` table)

- [ ] **Step 1: Fix the docx-check reference in existing Key Rule 9** — change `checking the page count (Step 9)` to `checking the page count (Step 10)`.

- [ ] **Step 2: Append three Key Rules** after rule 14:

```markdown
15. **Produce the outreach kit (Step 9) for every application — mandatory on the ML/AI track.** A referral or a two-line recruiter note beats a perfect cold resume. Drafts only; the user sends them manually.
16. **Never invent company facts.** Every company-specific claim in the cover letter or outreach traces to `company-research.md` (with a source) or the JD. Empty research means a JD-only letter, not improvisation.
17. **Register every application in `tracker.md`** (main folder, on `main`, never in a worktree), commit after every change, update rows when the user reports outcomes, and list follow-ups due whenever the tracker is touched.
```

- [ ] **Step 3: Fix the docx-check reference in the existing Common Mistakes row** — change `confirm it is ≤ one page (Step 9) before handoff` to `confirm it is ≤ one page (Step 10) before handoff`.

- [ ] **Step 4: Append five Common Mistakes rows:**

```markdown
| Skipping outreach because the cover letter felt sufficient | The cover letter rides inside the ATS; the outreach kit (Step 9) is what puts the application in front of a human — produce it every time, mandatory for ML/AI roles |
| Personalizing outreach or the cover letter with invented company facts | Every company claim traces to `company-research.md` (sourced) or the JD; empty research → JD-only version |
| Sending outreach automatically | Never — everything in `outreach.md` is a draft the user sends manually |
| Letting `tracker.md` rot after submission | Update the row on every status report; list due follow-ups whenever the tracker is touched — silence with no follow-up is how applications die |
| Writing `tracker.md` inside a worktree | The tracker lives only in the main folder on `main`; worktrees are per-application workspaces |
```

- [ ] **Step 5: Verify** — Key Rules count is 17; `grep -c "^|" <skill>/SKILL.md` shows the Common Mistakes table grew by 5 rows; no remaining `(Step 9)` refers to the docx check.

---

### Task 11: Repo changes — database note fix + create `tracker.md` + commit

**Files:**
- Modify: `D:/github/job-hunting/database/master-personal-info.md` (Notes section)
- Create: `D:/github/job-hunting/tracker.md`

- [ ] **Step 1: Fix the stale Jake's note** — in `database/master-personal-info.md`, replace:

```markdown
- Resume heading format (Jake's Resume template): phone | email | LinkedIn | GitHub | portfolio | location, one centered line under the name.
```

with:

```markdown
- Resume heading: this contact block fills the heading of the Word resume template (`resume-template/resume-template.docx`) — phone | email | LinkedIn | GitHub | portfolio | location.
```

- [ ] **Step 2: Create `D:/github/job-hunting/tracker.md`** with exactly the format from Task 9 Step 2 (title, the three `>` note lines, and the empty table header — no rows yet).

- [ ] **Step 3: Commit both to main:**

```powershell
git -C "D:/github/job-hunting" add tracker.md database/master-personal-info.md
git -C "D:/github/job-hunting" commit -m @'
Add application tracker; fix stale resume-heading note

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@
```

Expected: 2 files changed, on branch `main`.

- [ ] **Step 4: Verify** — `git -C "D:/github/job-hunting" status` clean for these files; `grep -n "Jake" database/master-personal-info.md` → no matches.

---

### Task 12: Consistency sweep of the whole skill folder

**Files:**
- Read/spot-fix: everything under `<skill>/`

- [ ] **Step 1: Run the sweep greps** over `<skill>/` (SKILL.md + templates/ + guidelines/ + references/):
  - `Overall Score`, `/100`, `85+`, `ats-score` → expected: no matches
  - `Stage 3`, `master.md`, `master\master` → expected: no matches
  - `Jake` → expected: matches only in prohibition context ("NOT Jake's Resume", "no Jake's Resume format") — those stay
  - `Step 9` → every match refers to the Outreach Kit
  - `Step 10` → every match refers to the docx fill/verify step
- [ ] **Step 2: Fix any straggler inline** (edit the file, re-run that grep).
- [ ] **Step 3: Read the revised SKILL.md top to bottom once** — check the step sequence reads 0,1,2,3,4,5,6,7,8,9,10 with no gaps, every template path named in a step exists on disk (`Get-ChildItem <skill>/templates/`), and no section contradicts another (especially Step 5 coverage framing vs. the new template, and the tracker "main folder only" rule vs. the worktree isolation rules).

---

### Task 13: Dry-run the new steps against a real ML/AI application

**Files:**
- Create (in the existing worktree): `D:/github/job-hunting-worktrees/2026-07-07-hellofresh-machine-learning-engineer/applications/2026-07-07-hellofresh-machine-learning-engineer/company-research.md` and `outreach.md`
- Modify: `D:/github/job-hunting/tracker.md`

- [ ] **Step 1: Load context** — read `jd.md`, `jd-analysis.md`, `tailored-resume.md`, `fit-and-referral.md` from that worktree's `applications/2026-07-07-hellofresh-machine-learning-engineer/` folder.
- [ ] **Step 2: Execute Step 7 Part A for real** — web-search HelloFresh (ML/AI-engineer track): products, recent news, ML-stack hints, ML-engineer salary range for the posting's region, public recruiter/HM names. Fill `company-research.md` from the new template. Every fact sourced; empty sections say "Nothing found — do not invent".
- [ ] **Step 3: Execute Step 9 for real** — fill `outreach.md` from the new template using the research + the existing tailored resume. Run the template's send checklist, including actually counting the connection note's characters (≤300).
- [ ] **Step 4: Quality gate** — check both artifacts against the templates' own rules: no LLM tells, one ask per message, every claim traceable. Fix template wording if the dry-run exposed a confusing placeholder (that's the point of the dry-run).
- [ ] **Step 5: Commit the artifacts to that application's branch:**

```powershell
git -C "D:/github/job-hunting-worktrees/2026-07-07-hellofresh-machine-learning-engineer" add applications/
git -C "D:/github/job-hunting-worktrees/2026-07-07-hellofresh-machine-learning-engineer" commit -m @'
Add company research and outreach kit (dry-run of revised skill)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@
```

- [ ] **Step 6: Exercise the tracker registration** — append the HelloFresh row to `D:/github/job-hunting/tracker.md` (Date 2026-07-07, Track ml-ai, Branch `2026-07-07-hellofresh-machine-learning-engineer`, Status `prepared` — ask the user its real status first and use that if known), commit with message `tracker: 2026-07-07-hellofresh-machine-learning-engineer prepared`, and finish by listing follow-ups due (per the new rule).

---

### Task 14: Verify the standalone tracker trigger

- [ ] **Step 1: Grep the frontmatter** — `grep -n "I submitted\|rejected me\|tracker" <skill>/SKILL.md` → the description contains the status-report trigger phrases.
- [ ] **Step 2: User-assisted check (report it, don't skip it)** — tell the user: in a **fresh session**, say `I submitted the HelloFresh application today`. Expected behavior: the skill triggers, updates the HelloFresh row (Status `submitted`, Submitted = today, Follow-up due = today + 5–7 business days), commits, and lists follow-ups due. If the skill does not trigger, strengthen the description's trigger wording and repeat.
- [ ] **Step 3: Done report** — summarize to the user what changed (skill files + repo files), and remind them the old application branches (before today) are not backfilled into the tracker — offer that as a follow-up if wanted.

---

## Self-review notes (spec → task coverage)

- Spec §1.1 (score template) → Task 3 + Task 7 Step 2 · §1.2 (resume template) → Task 1 · §1.3 (gaps footer) → Task 2 · §1.4 (Jake note) → Task 11
- Spec §2 (research) → Tasks 4, 7; salary hook → Task 8 Steps 1-2; Step 0 sanity check → Task 7 Step 1
- Spec §3 (outreach) → Tasks 5, 8
- Spec §4 (tracker) → Tasks 9, 11, 13 Step 6, 14
- Spec §5 (structure) → Tasks 6-10, 12
- Spec error handling → embedded in Step 7/9/After-the-Workflow texts (Tasks 7-9)
- Spec verification → Tasks 12, 13, 14
