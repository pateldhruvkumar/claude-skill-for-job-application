---
name: applying-to-job
description: Use when you paste or provide a job description and want to prepare a complete tailored job application, when starting a new application from a posting in the job-hunting repo, or when asked to apply to a specific company/role. Runs a fit-and-referral gate first (is this worth applying to, and who can refer you?), then handles branch/worktree creation, resume tailoring, a keyword-coverage check, a hiring-manager scan, company research, a cover letter, a recruiter phone-screen narrative, an outreach kit (referral request, recruiter cold note, follow-up nudge), Word (.docx) output filled from the user's provided templates, and registration in the application tracker (tracker.md + application-tracker.xlsx). ALSO use this skill when the user reports an application status — "I submitted X", "they rejected me", "I got a phone screen", "no response yet" — or asks to update or check the job tracker or follow-ups due.
---

# Applying to a Job

## Overview

Turn a pasted job description into a complete, reviewable application on its own git branch, worked on in an **isolated git worktree** so multiple applications can run in parallel without ever clobbering each other. The candidate profile is the four `database/*.md` files in the job-hunting repo (NOT a PDF). Every stage adopts an expert persona, produces one or more artifacts under `application/`, and **pauses for user review** before the next stage.

**A tailored resume and cover letter are necessary but not sufficient.** In real hiring, a referred candidate with a good-enough resume usually beats a cold applicant with a flawless one, and the recruiter phone screen decides more outcomes than the document does. So this flow does not open with the document machinery: it opens with a **fit-and-referral gate** (Step 0 — is this role worth applying to, and who can get it in front of a human?), and it closes with a **recruiter phone-screen narrative** (Step 8) and an **outreach kit** (Step 9 — the referral request, recruiter cold note, and follow-up nudge that put the application in front of a human instead of leaving it in a database). The polished `.docx` is the middle of the sandwich, not the whole meal. Every application also gets a row in **`tracker.md`** (repo root, on `main`) so submissions, follow-ups, and outcomes stop disappearing into silence — and a matching row in **`application-tracker.xlsx`** (also repo root, on `main`: one sheet tab per month, Status dropdown Applied/Interview/Rejected), maintained only via `scripts/update-application-tracker.py`.

**Length rule — exactly one full page:** the tailored resume **fills one page** and never spills onto a second. A page that stops three-quarters of the way down reads as thin, so fill it — but fill it with **real, JD-relevant material drawn from the `database/*.md` files** (another true bullet, another relevant entry), never with invented claims, stretched line spacing, enlarged fonts, or widened margins. Step 10 enforces both edges with `scripts/verify-resume-fit.ps1`: at least **92%** of the usable page filled, and never a second page. The cover letter is at most one page, with no fill requirement.

**Final deliverables are Word `.docx`:** the last stage fills the user's provided Word templates — `D:/github/job-hunting/resume-template/resume-template.docx` and `D:/github/job-hunting/cover-letter-template/cover-letter-template.docx` — with the approved content, producing `application/Dhruvkumar_Resume.docx` and `Dhruvkumar_Cover_Letter.docx`. **This skill does NOT use LaTeX or Jake's Resume format anywhere.** Fill the templates with the `docx` skill (unzip → edit `word/document.xml` → rezip; docx-js cannot open an existing file). Verify that each fits on one page in Microsoft Word (Step 10). The user opens the `.docx` and exports the final PDF from Word.

**Repo:** `D:\github\job-hunting`. **Master profile (source of truth):** `database/master-personal-info.md`, `database/master-experience.md`, `database/master-project.md`, `database/master-education.md`.

**Role track (set once, in Preflight):** decide up front whether this posting is a **software-developer**, **ML/AI-engineer**, or **data/operations-analyst** role, because each is screened by a different kind of reviewer looking for different signals. Carry that track into the JD extraction, the hiring-manager scan, and the phone-screen narrative — do not apply an engineering-manager lens to an analyst role or vice versa.

**Read-only assets live outside the worktree; everything you write goes inside it.** The Word templates (under `D:/github/job-hunting/`) and this skill's own reference and template files (under `C:/Users/Dhruv/.claude/skills/applying-to-job/`) are read-only and are read from their stable locations. The worktree is where every *artifact* is written. So "everything happens inside the worktree" means everything you **create** — reading a read-only template from the skill folder or the main folder does not break isolation, because you never write there.

**Self-contained assets:** the JD-extraction, resume, keyword-coverage, hiring-manager-scan, company-research, cover-letter, phone-screen, and outreach steps use this skill's own reference and template files, kept under `C:/Users/Dhruv/.claude/skills/applying-to-job/` (in `templates/`, `guidelines/`, and `references/`). This skill is fully self-contained — it does not borrow assets from any other skill. (Absolute paths are used deliberately: when this skill runs, the working directory is the job-hunting repo, not the skill folder, so a relative `../` path would resolve wrongly.)

## When to Use

- User pastes a job description and wants an application prepared
- Starting a new application from a posting
- "Apply to <company>", "tailor my resume for this JD", "make a cover letter for this role"
- The user reports an application status with NO new JD — "I submitted X", "they rejected me", "I got a screen", "no response yet" — or asks to update or check the tracker: **skip the pipeline entirely** and jump straight to "Standalone tracker updates" under **After the Workflow**. No worktree, no Preflight.

**When NOT to use:**
- No JD yet and it's not a status/tracker update (get the posting first)
- Editing the master `database/*.md` files themselves (edit those directly)
- The role is a clear non-fit — the Step 0 gate will confirm this; don't burn a week's effort on a no-go

## Preflight (before Step 0)

1. **Location:** working directory must be the job-hunting repo root — verify `database/master-personal-info.md` exists. If not, `cd D:\github\job-hunting`.
2. **Extract company + role** from the JD. If either is unclear, ASK the user — do not guess.
3. **Role track:** classify the posting as **software-developer**, **ML/AI-engineer**, or **data/operations-analyst**. This decides which reviewer persona the JD extraction, hiring-manager scan, and phone-screen narrative adopt — an analyst resume is judged differently from an engineering one. If genuinely mixed, pick the dominant track and note it.
4. **Date:** use today's date as `YYYY-MM-DD`.
5. **Slug:** `YYYY-MM-DD-<company>-<role>`, all lowercase, spaces and punctuation → single hyphens, keep the role concise (e.g. `2026-07-06-stripe-full-stack-engineer`).

## Workflow — Step 0 through Step 10

Pause after every step for user review. Never silently proceed.

### Step 0 — Fit & Referral Gate (do this BEFORE creating a worktree)

**Role:** *Act as a pragmatic job-search strategist and recruiter who has placed hundreds of candidates and knows the uncomfortable truth: most cold applications go nowhere, a referral is worth more than a perfect resume, and applying to roles you don't fit wastes the week. You are honest about fit, allergic to spray-and-pray, and you always ask "who do we know here?" before "how do we word this?"*

**Action — three quick checks, presented to the user for a go / no-go before any workspace is built:**

1. **Quick company sanity check (one line, not the deep dive).** If the company is unfamiliar, web-search it: is it real, what does it roughly build, any red flags (scam signals, ghost-job reposting)? One line in the verdict. The deep research pass happens at Step 7 — do not spend time on it here.
2. **Fit check.** Read the JD against the four `database/*.md` files (read them from the main folder — read-only). Give an honest verdict:
   - Do you clear the **hard must-haves** (years of experience, must-have skills, work authorization, location)? Missing a genuine non-negotiable = likely no-go; say so plainly.
   - Is this a **realistic target, a reasonable stretch, or a long shot**? State which, with one line of reasoning.
   - **Recommendation: APPLY / STRETCH-APPLY / SKIP** in one sentence. If SKIP, stop here — do not build a worktree for a role that isn't worth the effort.
3. **Referral / warm-intro scan.** Before treating this as a cold application, ask the user: *do you know anyone at this company, or anyone who knows someone there?* (Prompt them by name if the profile hints at relevant contacts.) If yes, the plan is to route the application through that person — a referral changes everything downstream, so flag it. If no, note that this is a cold application and continue.

**Output (only once the user says go):** these notes are saved as `application/fit-and-referral.md` in Step 1, right after the worktree exists. If the user says SKIP, nothing is created.

**Pause for the go / no-go.**

### Step 1 — Worktree + Workspace

**Never switch the branch of the main folder** (`D:/github/job-hunting`). Switching HEAD there is what let two parallel runs delete each other's files. Each JD gets its own **isolated worktree** instead, cut from the `main` ref — creating a worktree does NOT touch any other folder's checkout, so concurrent applications are structurally incapable of colliding.

1. The new branch is cut from the `main` **ref**, so make sure `main` has your latest master files committed. If there are uncommitted `database/` changes in the main folder, confirm with the user and commit them to `main` first.
2. Create the worktree on a fresh branch, without touching the main folder:
   `git worktree add "D:/github/job-hunting-worktrees/<slug>" -b <slug> main`
   (If that path already exists, this slug's workspace is already set up — reuse it, do not recreate.)
3. **Immediately narrow the worktree to this application only (sparse-checkout).** `main` is the permanent archive of every past application, so a plain worktree materializes all 80+ `applications/*` folders and every unrelated repo directory. That makes each workspace look like the whole repo and is confusing to browse. Run this right after creating the worktree:
   `git -C "D:/github/job-hunting-worktrees/<slug>" sparse-checkout set --cone database "application"`
   The worktree then contains only `database/` and `application/`. **This is a working-directory setting only — it changes nothing about the branch or any commit, and it is fully reversible** (`sparse-checkout disable` restores everything).
   - **Use `--cone`. Do NOT use `--no-cone`:** gitignore-style directory patterns like `/database/` silently fail to match there and will de-materialize your tracked artifacts.
   - Cone mode always keeps repo-root files, so `tracker.md` and `application-tracker.xlsx` still appear at the worktree root. **They are still off-limits inside a worktree** — edit them only in the main folder (see After the Workflow).
   - If a later step needs a directory that was excluded, add it rather than disabling sparse-checkout: `git -C "<worktree>" sparse-checkout add <dir>`.
4. From here on **everything you write happens inside the worktree**: read the four `database/*.md` files from `D:/github/job-hunting-worktrees/<slug>/database/` (they exist there because it was cut from `main`), write every artifact under `D:/github/job-hunting-worktrees/<slug>/application/` using absolute paths, and run every git command with `git -C "D:/github/job-hunting-worktrees/<slug>"`. (Read-only templates and reference files are still read from their stable locations — see Overview.) The sole write exceptions are `tracker.md` and `application-tracker.xlsx`, which live in the MAIN folder only and are committed with `git -C "D:/github/job-hunting"` — see After the Workflow.
5. Create `application/` inside the worktree and save (a) the raw JD verbatim to `application/jd.md`, and (b) the Step 0 notes to `application/fit-and-referral.md`.

**Pause.**

### Step 2 — Profile Load

**Role:** *Act as a senior career coach who has parsed 10,000+ resumes across tech, finance, and consulting roles. You catch every meaningful detail — every accomplishment, technology, metric, and implicit skill — without missing a single line. You are methodical, thorough, and never skip content.*

**Action:** Read all four `database/*.md` files. Treat them together as the complete candidate profile that every downstream stage draws from. There is no `resume.pdf` and no `master.md` — the database files ARE the master. Summarize what was loaded (roles, projects, skills, education) so the user can confirm nothing is missing.

**Pause.**

### Step 3 — JD Extraction

**Role:** *Act as a senior technical recruiter at a top tech company who has read 5,000+ job descriptions. You instantly separate must-haves from nice-to-haves, identify the unstated assumptions hiring managers make, and never miss a hidden requirement buried in boilerplate language.* Weight the extraction toward the real signals of the Preflight **role track** (e.g. an analyst posting cares about SQL/BI and business impact; an ML posting cares about production model work).

**Action:** Using `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/jd-analysis.template.md`, produce `application/jd-analysis.md` with all 7 sections: Hard Requirements, Required Skills, Preferred Skills, Action Verbs from JD, Domain Vocabulary, Cultural Signals, Top 10 Keywords.

**Pause.**

### Step 4 — Tailor Resume

**Role:** *Act as an expert technical resume writer who has crafted 3,000+ tailored resumes and placed candidates at FAANG and high-growth startups. You write to the user's provided Word resume template using the Google XYZ formula. You never fabricate — every claim must trace to the candidate's actual experience in the database files.*

**Inputs:** the four `database/*.md` files + `jd-analysis.md`.

**Rules:**
1. The output format is the user's Word template `D:/github/job-hunting/resume-template/resume-template.docx` (NOT Jake's Resume, NOT LaTeX). `tailored-resume.md` holds the approved content; it gets mapped into the template's sections, in the template's order (**Experience, Projects, Technical Skills, Education, Awards**), at Step 10. Produce every section the template expects. **There is no Summary section — never write one.**
2. Every bullet follows Google XYZ per `C:/Users/Dhruv/.claude/skills/applying-to-job/guidelines/bullet-points.md`.
3. Action verbs from `C:/Users/Dhruv/.claude/skills/applying-to-job/guidelines/action-verbs.md`; vary across bullets; mirror JD verbs when the claim is true.
4. Scrub LLM tells per `C:/Users/Dhruv/.claude/skills/applying-to-job/references/llm-tells.md`.
5. **Keyword handling — "surface what's real, flag what's missing":** backed by database → surface with the JD's exact phrasing; loosely related → show the supporting bullet before keeping it; not in database → DO NOT silently insert, list it in `keyword-gaps.md` with three options.
6. **Exactly one full page — fill it with real content.** The resume must fill one page and must never spill onto a second. Step 10 fails the build at **both** edges: content stopping short of **92% of the usable page height**, or crossing onto page 2.
   - **Under-filled?** Add real, JD-relevant material from the `database/*.md` files — another true bullet on the strongest entry, or another relevant Experience/Project entry. **Never invent a claim, never inflate line spacing, never enlarge fonts or widen margins to reach the line.**
   - **Overflowing?** Cut the least-relevant content first (older/less-relevant bullets, then whole low-value entries). **Never drop a surviving entry below the two-bullet minimum (rule 8) — cut the whole entry instead.**
   - If the strongest honest material genuinely cannot reach 92%, say so in your summary and let the user decide. **Do not pad silently.**

   State in your summary what you added or cut to land on one full page.
7. **Reverse-chronological format.** Experience always precedes Projects. Within Experience and within Projects, entries run **newest first**, and every entry carries a date range. Projects never lead the document, even when they are the stronger material — that strength shows through bullet quality and ordering, not by displacing Experience. Full section order: **Experience, Projects, Technical Skills, Education, Awards.**
8. **Two to four bullets per entry.** Every Experience entry and every Project entry carries **two or more** bullet points, and the template asks for **around 2 to 4 per entry** — a fifth is allowed only when the page genuinely needs the height (rule 6), and Step 10's pattern check warns on it. Each bullet follows the template's own formula: **action verb + task or project + metric or result**. An entry that can only justify one real bullet is merged into a stronger entry or dropped — never shipped as a one-line stub. (Education entries and Awards lines carry no bullets and are exempt.)
9. **Entry headings follow the Word template's shape — company first, on two lines.** An Experience heading is **one paragraph holding two lines**: line 1 is the **company in ALL CAPS** → right tab → **City, Prov**; line 2 is the **job title** → right tab → **dates**. There is no `Title | Company` pipe — the company and the title sit on separate lines. In `tailored-resume.md` write the heading company-first with the title after it (e.g. **`ASSOCIATED GROCERS | Surrey, BC`** then **`Inventory Analyst | Mar 2025 – Present`**), because Step 10 renders what this file says. Project headings are a different shape: a **single line**, `Project Name | Technologies used` (3-5 JD-relevant tools, true to the project), no location. Step 10's pattern check fails the build on a title-first heading, on a `Title | Company` pipe, and on a mixed-case company name.
10. **Awards — conditional, de-duplicated, never invented.** Source award lines from the `## Awards & Honors` block in `database/master-education.md`. Include the section only when **two or more** genuine items are available; below that, omit it entirely rather than ship a one-line stub. **A fact rendered in Awards is not repeated elsewhere on the same resume:** when Awards carries "Graduated with Distinction," the B.Tech education entry drops it; when Awards carries the hackathon placement, the Kahoot Bot project bullet drops that clause (it keeps its 90%-accuracy and 60%-cost-reduction evidence, which is the stronger signal anyway). If the awards material is thin, flag it in your summary the way `keyword-gaps.md` flags a gap — the user supplies real awards; you never invent one.

**Outputs:** `application/tailored-resume.md` (via `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/tailored-resume.template.md`) and `application/keyword-gaps.md` (via `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/keyword-gaps.template.md`).

**Pause.**

### Step 5 — Keyword Coverage Check

**Reality first:** for most employers, systems like Workday, Greenhouse, and Lever are **databases that parse and store your resume so a recruiter can search it** — not robots that compute a score and auto-reject you below a threshold. A human still reads you. So this stage is a **keyword-coverage check, not a pass/fail "ATS score."** Its job is to confirm the resume parses cleanly and that the JD's real language is present where it's genuinely true — nothing more. **It never overrides the hiring-manager scan (Step 6); when the two disagree, the human read wins.**

**Role:** *Act as a meticulous recruiting-ops analyst who checks two things only: (1) will this resume parse cleanly into an applicant-tracking database, and (2) does it surface the JD's real keywords and phrasing where the candidate genuinely has that experience. You do not gatekeep and you do not pretend a number decides the hire — you flag parsing risks and honest coverage gaps.*

**Inputs:** `tailored-resume.md` + `jd-analysis.md`.

**Action:** Using `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/keyword-coverage.template.md`, read its six dimensions as **coverage signals, not a verdict**: required-skill coverage, preferred-skill coverage, action-verb alignment, domain-vocabulary match, hard-requirement satisfaction, and format/parse compliance (which includes exactly one full page). Produce `application/keyword-coverage.md` with: a coverage summary per dimension, bullet-to-JD keyword mappings, a parse-safety check (standard headings, no tables/columns that break parsing, standard section names), and concrete suggestions. **Frame every finding as "covered / partially covered / genuinely missing," and route any genuinely missing keyword to `keyword-gaps.md` — never invent coverage to raise a number.**

**Pause.**

### Step 6 — Hiring-Manager 10-Second Scan (the human read — this is the one that decides)

**This is the judgment that matters most.** A real reviewer skims the top third and makes a read-deeper-or-reject call in seconds. **When this scan and the Step 5 coverage check disagree, this one wins** — optimize the resume to survive a skeptical human, not to raise a keyword number.

**Role (match the Preflight role track):**
- **Software-developer role →** *a senior engineering manager who reviews 50+ resumes a week, looking for seniority signals, relevant tech, and concrete shipped impact.*
- **ML/AI-engineer role →** *an ML lead scanning for real model and data work, production ML, and measurable outcomes — not just coursework.*
- **Data/operations-analyst role →** *an analytics or operations lead scanning for SQL/BI fluency, business impact, and clear quantified results — engineering "seniority" signals matter less than demonstrated analytical impact.*

In all cases: skeptical, time-pressured, unforgiving of fluff.

**Layout note:** the resume is reverse-chronological with Technical Skills below Projects, so the top third is Experience (and possibly the first project) — not a skills block. Judge whether the stack and the impact surface through those bullets. **Do not flag the absence of a skills list up top as a defect, and do not recommend moving Technical Skills back to the top** — that ordering is deliberate.

**Inputs:** `tailored-resume.md` + `jd-analysis.md`.

**Action:** Using `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/hiring-manager-scan.template.md`, simulate a 10-second skim of the top third. Produce `application/hiring-manager-scan.md` with what they'd actually read, the read-deeper-or-reject verdict with reasoning, red flags, and specific fixes.

**Pause.**

### Step 7 — Company Research + Cover Letter

Two parts, one pause: research first, then the letter that uses it.

**Part A — Company research.**

**Role:** *Act as a company-research analyst who preps candidates for competitive applications. You find what the company actually builds, what changed recently (funding, launches, news), what the team's stack looks like, what the role pays in this region, and which humans are publicly attached to the role — and you never state a fact you cannot source.*

**Action:** Web-search the company and produce `application/company-research.md` via `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/company-research.template.md`: what they build, recent news/funding, tech-stack hints for the role track, a salary range for the role + region from public sources (posted range, levels.fyi, Glassdoor), publicly listed recruiter / hiring-manager / team-lead names (public pages only — these feed Step 9 outreach targeting), and 1-3 cover-letter angles. **If search returns nothing useful for a section, write "Nothing found — do not invent" and move on. Never fabricate company facts.**

**Part B — Cover letter.**

**Role:** *Act as an expert cover-letter writer who has drafted 2,000+ letters that landed interviews at top tech companies. You write concise, specific, non-generic letters that connect the candidate's real accomplishments to the role's actual needs. You never fabricate, never pad with fluff, and never sound like a template.*

**Inputs:** `jd-analysis.md` + `tailored-resume.md` + `company-research.md` + the four `database/*.md` files.

**Rules:**
1. One page, ~3-4 short paragraphs: hook + why this company/role, 1-2 proof paragraphs tying real accomplishments to the JD's top requirements, close with a call to action.
2. Every claim about the candidate traces to the database files. Never fabricate — a keyword gap stays a gap (see `keyword-gaps.md`).
3. **Every claim about the company traces to `company-research.md` (sourced) or the JD.** If the research came up empty, write the JD-only version — company claims stay generic-but-true, never invented.
4. Scrub LLM tells per `C:/Users/Dhruv/.claude/skills/applying-to-job/references/llm-tells.md` (no em dashes, no "leveraged/robust/seamless/passionate about", etc.).
5. Use the real contact block from `database/master-personal-info.md`. Address to the hiring team/manager; use the company name.

**Outputs:** `application/company-research.md` + `application/cover-letter.md` (via `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/cover-letter.template.md`).

**Pause once, covering both artifacts.**

### Step 8 — Recruiter Phone-Screen Narrative

**Why this exists:** more applications are won or lost on the 20-minute recruiter call than on the resume. Prepare the verbal story now, while the material is fresh, so it's ready when the call comes.

**Role:** *Act as a coach who preps candidates for recruiter screens. You turn a resume into a tight spoken narrative — a 30-second "why me for this role," crisp answers to the predictable screen questions, and honest handling of gaps. No rambling, no memorized-sounding scripts.*

**Inputs:** `jd-analysis.md` + `tailored-resume.md` + `company-research.md` + the four `database/*.md` files + `keyword-gaps.md`.

**Action:** Produce `application/phone-screen-narrative.md` with:
1. **The 30-second pitch** — who you are, the 1-2 most relevant things you've done, and why this role/company, in ~4 spoken sentences.
2. **"Why this company / why this role"** — two real, specific reasons that tie to the JD and to something true about the candidate.
3. **Answers to the predictable questions** — "walk me through your background," "why are you looking," "what are you looking for," and "salary expectations" (use the researched range from `company-research.md` as the bracket when it found one — the candidate confirms it before quoting; if research found nothing, keep a bracketed to-research placeholder — never a fabricated number).
4. **Gap handling** — for each item in `keyword-gaps.md`, one honest, non-defensive line acknowledging it and pointing to the closest real experience.

Keep everything spoken-natural and short; scrub LLM tells per the `llm-tells.md` reference.

**Pause.**

### Step 9 — Outreach Kit (mandatory for ML/AI-track postings)

**Why this exists:** a cold application with no outreach is how applications disappear into silence. A referral, or a two-line note to the right recruiter, moves the application out of the ATS database and into a human's field of view — for response rate, this is the highest-leverage artifact in the pipeline.

**Role:** *Act as an outreach coach who spent years as an in-house recruiter reading cold messages. You know what gets replies — short, specific, one clear ask, one real proof point — and what gets ignored: long messages, flattery, vague "any opportunities?" asks, and fake familiarity.*

**Inputs:** `fit-and-referral.md` (the contact, if Step 0 found one) + `company-research.md` (people + angles) + `tailored-resume.md` + `jd-analysis.md`.

**Action:** Produce `application/outreach.md` via `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/outreach.template.md` with three drafts:
1. **Referral request** — addressed to the named contact from Step 0 if one exists, otherwise the reusable 2nd-degree version ("do you know anyone at X?").
2. **Cold note to the recruiter / hiring manager** — targeted at a name from `company-research.md` when one is public, otherwise role-generic. Two lengths: a ≤300-character LinkedIn connection note AND a longer InMail/email version with one quantified proof point and a soft ask.
3. **Follow-up nudge** — pre-dated 5–7 business days after submission, containing one NEW proof point (never just "checking in").

**Rules:** drafts only — **never send anything; the user sends manually.** No fabrication, no fake familiarity, scrub LLM tells. **ML/AI-track postings: never skip this step** — that is the dream track, and cold-applying there without outreach is what produces silence. Other tracks: produce it anyway; the user chooses whether to send.

**Pause.**

### Step 10 — Fill the Word (.docx) templates + one-page verify

**Role:** *Act as a Word/OOXML typesetter who has produced 1,000+ parse-safe, one-page-max resumes. You render approved content faithfully into the user's provided `.docx` template — you never change wording, never add claims, and preserve the template's styles exactly (the only exception is the cover-letter 12pt body-size override named in Action item 2).*

**Trigger:** only after the user has approved `tailored-resume.md` and `cover-letter.md`.

**Dependency — use the `docx` skill (`anthropic-skills:docx`).** To fill a `.docx` template: `unzip` it → edit `word/document.xml` (replace the placeholder paragraphs with the approved content, keeping every paragraph/run style pattern) → rezip. **docx-js cannot open an existing file, so always edit the provided template's XML — never rebuild the format from scratch.** On this machine there is no LibreOffice; use Python's `zipfile` to rezip (the `zip` CLI is absent) and set `PYTHONIOENCODING=utf-8` before running the skill's Python scripts.

**Action:**
1. **Resume → `application/Dhruvkumar_Resume.docx`.** Start from the provided template `D:/github/job-hunting/resume-template/resume-template.docx`. Fill the heading from `database/master-personal-info.md` — contact line **location first**: `Surrey, BC | phone | email | LinkedIn | GitHub | Portfolio`, then the template's empty paragraph before the first section rule — and the body from the approved `tailored-resume.md` ONLY, mapping content into the template's sections in the template's order (**Experience, Projects, Technical Skills, Education, Awards**). **The template has no Summary section — never add one.** Every Experience and Project entry keeps **two to four bullets** (Step 4 rule 8) and every Experience heading renders the company in **ALL CAPS**. Omit the Awards section entirely when fewer than two genuine items exist (Step 4 rule 10). Preserve the template's fonts, sizes, blue section-heading rule, bullet numbering, right-aligned dates, and **the entry-heading pattern spelled out below**. Make LinkedIn / GitHub / Portfolio / email real hyperlinks. Escape XML specials in all prose: `&`→`&amp;`, `<`→`&lt;`, `>`→`&gt;`. If the resume template is missing, PAUSE and ask the user for it — same rule as the cover-letter template: never fall back to LaTeX or invent a format.

   **The entry-heading pattern — copy these shapes, do not improvise them.** The template ships four placeholder Experience entries and two Projects; the fastest correct fill is to keep one placeholder paragraph per entry and swap only the text runs, adding or deleting whole paragraphs to match the entry count. The shapes:

   | Row | Pattern | Run styling |
   |---|---|---|
   | **Header contact line** | **location first**: `Surrey, BC \| phone \| email \| LinkedIn \| GitHub \| Portfolio`, centred, followed by one empty paragraph before the first section rule | every run `sz=16`; email / LinkedIn / GitHub / Portfolio are real hyperlinks |
   | **Experience heading** | **one paragraph, two lines.** Line 1: `COMPANY NAME` → tab → `City, Prov`, then `<w:br/>`. Line 2: `Job Title` → tab → date | company **ALL CAPS** bold `sz=20`; location bold `sz=20`; job title non-bold with **no explicit `sz`** (inherits 9pt); date non-bold, no explicit `sz` |
   | **Project heading** | `Project Name \| Technologies used` → tab → date. **Single line — no location, no `<w:br/>`** | name\|tech bold `sz=20`; date non-bold `sz=20` |
   | **Bullet** | `pStyle=ListParagraph` + `numId=1`, `spacing after=40 line=245` | `sz=18` |
   | **Technical Skills** | `Category: skills` lines — **three of them**, separated by `<w:br/>` inside the paragraph | category label bold, skill list non-bold, no explicit `sz` |
   | **Education** | two paragraphs: school → tab → location, then degree → tab → date | school bold `sz=20`; degree *italic* with no explicit `sz`; date no explicit `sz` |
   | **Award** | `Award name` → tab → date | name bold `sz=20`, date non-bold `sz=20` |

   Every heading row carries `<w:tabs><w:tab w:val="right" w:pos="10973"/></w:tabs>` and `spacing before=60 after=0 line=245`. **The company leads line 1 and the job title sits on line 2** — there is no `Title | Company` pipe anywhere in an Experience heading. A one-line `Job Title | Company` heading is drift from the pre-2026-09-19 template and fails the pattern check, as does a mixed-case company name or a header contact line that ends with the location instead of leading with it.

   > **Why `sz=20` when the template file says `sz=19`.** The live `resume-template.docx` carries `sz=19` on its `COMPANY NAME` run — a Word artifact from the square brackets that run replaced. The user's decision (2026-09-19) is **ALL CAPS at `sz=20`**, so the company matches the bold location beside it. Render `sz=20`; `verify-resume-pattern.py` enforces 20 and records why in its docstring.

   Reference skeleton for one Experience entry:

   ```xml
   <w:p><w:pPr><w:tabs><w:tab w:val="right" w:pos="10973"/></w:tabs><w:spacing w:before="60" w:after="0" w:line="245" w:lineRule="auto"/></w:pPr>
     <w:r><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:t xml:space="preserve">ASSOCIATED GROCERS</w:t></w:r>
     <w:r><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="19"/></w:rPr><w:tab/></w:r>
     <w:r><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:t xml:space="preserve">Surrey, BC</w:t></w:r>
     <w:r><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="19"/></w:rPr><w:br/></w:r>
     <w:r><w:rPr><w:bCs/><w:color w:val="000000"/><w:szCs w:val="18"/></w:rPr><w:t xml:space="preserve">Inventory Analyst</w:t></w:r>
     <w:r><w:rPr><w:bCs/><w:color w:val="000000"/><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr><w:tab/></w:r>
     <w:r><w:rPr><w:color w:val="000000"/><w:szCs w:val="18"/></w:rPr><w:t xml:space="preserve">Mar 2025 – Present</w:t></w:r></w:p>
   ```

2. **Cover letter → `application/Dhruvkumar_Cover_Letter.docx`**, filled from the approved `cover-letter.md` using the user's cover-letter template at `D:/github/job-hunting/cover-letter-template/cover-letter-template.docx` (name + contact header, date, recipient block + greeting, body paragraphs, signature). **Body font size: 12pt — this is the one deliberate style override.** The template's Normal style is 9pt; in the generated file's `word/styles.xml`, change the Normal style's `<w:sz w:val="18"/>` to `<w:sz w:val="24"/>` (and `w:szCs` to `24`). The date, recipient block, greeting, body paragraphs, and signature all inherit Normal, so this makes them 12pt; the name header and contact line keep their explicit run-level sizes — do not touch those. **If that template is missing, PAUSE and ask the user for it — do NOT fall back to LaTeX or invent a format.**
3. **Validate** each generated `.docx` with the docx skill's validator against its source template: `python <docx-skill>/scripts/office/validate.py <out>.docx --original <template>.docx`.
4. **Verify the resume matches the template's pattern.** Run the pattern check *before* the fit check — a resume with the wrong heading shape is wrong at any page count:

   ```
   python "D:/github/job-hunting/scripts/verify-resume-pattern.py" "D:/github/job-hunting-worktrees/<slug>/application/Dhruvkumar_Resume.docx"
   ```

   It diffs the generated file against `resume-template.docx` and fails on: a one-line or title-first Experience heading, a `Title | Company` pipe, a mixed-case company name, a missing location or date after the right tab, a contact line that trails the location instead of leading with it, a project heading with no tech stack, wrong run weights/sizes, an entry under two bullets, and changed page size or margins. It **warns** (does not fail) on an entry above four bullets, more than three Technical Skills categories, and a header location that disagrees with `master-personal-info.md`. Each failure names the entry and the exact correction. **Fix the rendering, never the approved wording** — if a heading genuinely needs different text, that change belongs in `tailored-resume.md` and goes back through Step 4 for the user's approval. `WARN` lines (a title or company that matches nothing in `master-experience.md`) do not fail the build, but read them: they usually mean a typo or an entry the database never got updated with.
5. **Verify the resume is exactly one full page.** Run the fit check:

   ```
   powershell -NoProfile -File "D:/github/job-hunting/scripts/verify-resume-fit.ps1" -Path "D:/github/job-hunting-worktrees/<slug>/application/Dhruvkumar_Resume.docx"
   ```

   It passes only when the document is exactly 1 page **and** at least 92% of the usable page height is filled.
   - `FAIL (overflow)` — trim per Step 4 rule 6 and regenerate.
   - `FAIL (underfill)` — **go back to Step 4**: add real content to `tailored-resume.md` per Step 4 rule 6, re-confirm the additions with the user, then re-render and re-check. **Whitespace at the bottom of the page is a defect now, not an acceptable outcome.** **Never inject content straight into the `.docx`** — anything added must pass through `tailored-resume.md` so it is covered by the Step 5 and Step 6 checks and by the user's approval.

   For `Dhruvkumar_Cover_Letter.docx`, check the page count only (`≤ 1`, no fill requirement) with `$doc.ComputeStatistics(2)` via Word COM. Word COM is the reliable renderer here (no LibreOffice); if a Word call hangs, kill stray `WINWORD` processes and retry.
6. **Never** produce a `.tex` file or run LaTeX/`pdflatex`. The user opens the `.docx` and exports the final PDF from Word.

**Outputs:** `application/Dhruvkumar_Resume.docx` (pattern-verified against `resume-template.docx` and Word-verified to exactly one full page) + `application/Dhruvkumar_Cover_Letter.docx` (Word-verified to at most one page). **Pause.** Once the user approves the `.docx`, commit all artifacts to the branch (see **After the Workflow**) — the committed branch is the durable safe copy of the application.

## After the Workflow

All artifacts sit under `application/` **inside the worktree** `D:/github/job-hunting-worktrees/<slug>` on branch `<slug>`: `jd.md`, `fit-and-referral.md`, `jd-analysis.md`, `tailored-resume.md`, `keyword-gaps.md`, `keyword-coverage.md`, `hiring-manager-scan.md`, `company-research.md`, `cover-letter.md`, `phone-screen-narrative.md`, `outreach.md`, `Dhruvkumar_Resume.docx`, `Dhruvkumar_Cover_Letter.docx`.

**Commit the artifacts to the branch (do this after the user approves the `.docx`)** — this is what makes each application permanently safe:

```
git -C "D:/github/job-hunting-worktrees/<slug>" add application/
git -C "D:/github/job-hunting-worktrees/<slug>" commit -m "Add <slug> application artifacts"
```

One commit per posting, matching the repo convention. **The committed branch is the durable safe copy; the worktree folder is only a temporary workspace.** This skill delivers Word `.docx` files (filled from the provided templates and Word-verified to at most one page); it does **not** produce a `.tex` file or a PDF. The user opens the `.docx` and exports the final PDF from Word.

**Register the application in `tracker.md` AND `application-tracker.xlsx` (right after committing the artifacts).**

`tracker.md` lives at the repo root in the **MAIN folder** (`D:/github/job-hunting/tracker.md`), on `main` — **never inside a worktree.** (The main folder never switches branches, so writing there is safe alongside parallel worktrees.) If the file doesn't exist, create it with the exact header below. Append one row for this application with Status `prepared`.

Then add the same application to **`application-tracker.xlsx`** (repo root, MAIN folder, on `main` — one sheet tab per month, columns Date | Company Name | Job Role | Status | Salary | Job Description, Status dropdown Applied/Interview/Rejected; the JD is auto-converted to plain text by the script). **Never edit the xlsx by hand or rebuild it** — run the registration script (it creates the workbook and month tab if missing, and re-running with the same company + role in the same month updates the row instead of duplicating):

    python "D:/github/job-hunting/scripts/update-application-tracker.py" add --date <YYYY-MM-DD> --company "<Company>" --role "<Role>" --status Applied --salary "<salary>" --jd-file "D:/github/job-hunting-worktrees/<slug>/application/jd.md"

`--salary` value — a plain range and NOTHING else, in exactly this shape: `80K to 95K` (hourly roles: `55 to 58 per hour`; non-CAD currency: append it, e.g. `128K to 184K USD`). The number comes from the JD's posted range when it names one, otherwise from the researched range in `company-research.md`; if neither exists, `Not posted`. **No annotations ever** — no `(posted)`, no `(est., Glassdoor)`, no `+ bonus`, no `$` signs; sources and bonus details belong in `company-research.md`/`tracker.md` Notes, not this column (user rule, 2026-07-22).

Commit both tracker files together immediately — small immediate commits are what keep parallel sessions from colliding. If the commit conflicts with a parallel session, re-read/re-run, reapply your row, and commit again.

    git -C "D:/github/job-hunting" add tracker.md application-tracker.xlsx
    git -C "D:/github/job-hunting" commit -m "tracker: <slug> prepared"

Tracker file format (used verbatim to create the file if missing):

    # Application Tracker

    > One row per application. Status flow: prepared → submitted → followed-up → screen → interview → offer | rejected | no-response.
    > Follow-up due = Submitted + 5–7 business days (send the outreach.md nudge). Dates are YYYY-MM-DD.
    > Update rows in the MAIN folder only (never a worktree); commit after every change.

    | Date | Company | Role | Track | Branch | Status | Submitted | Outreach sent | Follow-up due | Response | Notes |
    |---|---|---|---|---|---|---|---|---|---|---|

**Standalone tracker updates (no pipeline run needed):** when the user reports a status in ANY session — "I submitted the Diligent one", "Jerry.ai rejected me", "I got a screen", "update the tracker" — update that application's row in the main folder: set Status and the relevant date columns, compute Follow-up due (Submitted + 5–7 business days) when they report submitting, note responses, and commit. **Mirror every status change into `application-tracker.xlsx` in the same update** using the script (dropdown mapping: screen/interview/offer → `Interview`; rejected/withdrawn → `Rejected`; submitted/followed-up/no-response → `Applied`):

    python "D:/github/job-hunting/scripts/update-application-tracker.py" set-status --company "<Company>" --role "<Role>" --status <Applied|Interview|Rejected>

(`--role` is optional; the script errors with a list if the company alone is ambiguous. Commit `tracker.md` and `application-tracker.xlsx` together.) **Every time you touch `tracker.md`, finish by listing any follow-ups now due or overdue** (today ≥ Follow-up due, Status is submitted/followed-up, and Response is empty) so the user knows exactly which nudges to send today.

**Archive into `main` (when filing the finished application into the permanent archive).**

The branch stores artifacts under `application/`, but `main`'s archive keeps every job at `applications/<slug>/`. So archiving is a path-remap, **not** a plain merge:

    git -C "D:/github/job-hunting" read-tree --prefix="applications/<slug>/" -u "<slug>:application"
    git -C "D:/github/job-hunting" commit -m "archive: <slug>"

Run this from a clean `main`. It grafts the branch's `application/` tree into `main` at `applications/<slug>/`, so `main`'s archive layout is unchanged. Because it is not a merge, `git branch --merged` will not flag archived branches — to check whether a job is already archived, test the folder instead: `git -C "D:/github/job-hunting" cat-file -e "main:applications/<slug>/jd.md"` (exit 0 = already archived).

**Cleanup (optional — only when the user says they are done with this JD):**
1. Verify the worktree tree is clean: `git -C "D:/github/job-hunting-worktrees/<slug>" status`. If anything is uncommitted (e.g. a locally exported PDF or an edit), **STOP and warn** — never remove a worktree that has uncommitted work.
2. Once clean: `git worktree remove "D:/github/job-hunting-worktrees/<slug>"`.

The branch (with the committed resume and cover letter) remains forever, so nothing is lost. To reopen a past application later: `git worktree add "D:/github/job-hunting-worktrees/<slug>" <slug>` followed by `git -C "D:/github/job-hunting-worktrees/<slug>" sparse-checkout set --cone database "application"` so the reopened workspace stays scoped to that one application.

## Key Rules

1. **Run the fit-and-referral gate first (Step 0).** Don't apply to a clear non-fit; when a referral exists, route the application through it — that beats a perfect cold resume.
2. **Pause after every step** for user review. Never silently proceed.
3. **Quote each persona verbatim** before starting that step's work.
4. **The four `database/*.md` files are the master** — no PDF, no `master.md`.
5. **Never silently insert a keyword** not backed by the database → put it in `keyword-gaps.md`.
6. **Bullets follow Google XYZ**, start with a strong varied action verb.
7. **Use the user's Word `.docx` templates** for output (resume: `resume-template/resume-template.docx`; cover letter: `cover-letter-template/cover-letter-template.docx`, both under `D:/github/job-hunting/`) — no LaTeX, no Jake's Resume format, ever.
8. **No LLM tells** anywhere (resume, cover letter, and phone-screen narrative) — no "passion for / passionate about", no "leveraged / robust / seamless".
9. **One full page, never two** — the resume fills at least 92% of the usable page and never crosses onto a second. Fill only with real, JD-relevant material; never with invented claims or stretched spacing. Prove it by running `scripts/verify-resume-fit.ps1` (Step 10), not by eyeballing. The cover letter stays ≤ one page with no fill requirement.
10. **Keyword coverage is a check, not a gate** — the hiring-manager 10-second scan (the human read) wins whenever the two disagree.
11. **Match the reviewer to the role track** — engineering manager for a dev role, ML lead for an ML role, analytics/ops lead for an analyst role.
12. **Prepare the phone-screen narrative (Step 8)** — the recruiter call decides more outcomes than the document.
13. **Isolated, sparse worktree per JD** — never switch the main folder's branch; `git worktree add "D:/github/job-hunting-worktrees/<slug>" -b <slug> main`, then `sparse-checkout set --cone database "application"` so the workspace holds only this application, and do all writing there. Parallel applications never collide and no worktree shows another job's folders.
14. **Commit artifacts to the branch** after approval (the branch is the durable safe copy); only remove the worktree once the user is done and `git status` in it is clean.
15. **Produce the outreach kit (Step 9) for every application — mandatory on the ML/AI track.** A referral or a two-line recruiter note beats a perfect cold resume. Drafts only; the user sends them manually.
16. **Never invent company facts.** Every company-specific claim in the cover letter or outreach traces to `company-research.md` (with a source) or the JD. Empty research means a JD-only letter, not improvisation.
17. **Register every application in `tracker.md` AND `application-tracker.xlsx`** (both repo root, main folder, on `main`, never in a worktree), commit both after every change, update rows when the user reports outcomes, and list follow-ups due whenever the tracker is touched. The xlsx is only ever written through `scripts/update-application-tracker.py` — never by hand.
18. **Reverse-chronological, in this exact order: Experience, Projects, Technical Skills, Education, Awards.** No Summary section, ever. Every Experience and Project entry carries at least two bullets. Awards appears only with two or more genuine items from `master-education.md`, and nothing in Awards is repeated elsewhere on the page.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Applying to a role you don't fit, or applying cold when a referral exists | Run the Step 0 fit-and-referral gate first; skip clear no-gos, and route through a referral whenever you have one |
| Treating a keyword / "ATS score" as a pass-fail gate | It's a coverage check (`keyword-coverage.md`), not a gate; the hiring-manager 10-second scan wins when they disagree |
| Leaving the resume three-quarters full, with whitespace at the bottom | An under-filled page reads as thin. Add real, JD-relevant material until `verify-resume-fit.ps1` reports ≥92% fill — never invented claims, never stretched spacing |
| Filling the page by inflating line spacing, font size, or margins | That is padding, not content. Fill only with real material from `database/*.md`; if the honest material cannot reach 92%, tell the user instead of stretching the layout |
| Resume spills to two pages | Trim least-relevant content (older bullets, then whole low-value entries) to fit one page; never cut a surviving entry below two bullets — drop the whole entry instead |
| Writing a Summary or profile blurb at the top | There is no Summary section — the order is Experience, Projects, Technical Skills, Education, Awards. Lead with Experience |
| Putting Projects or Technical Skills above Experience | The format is reverse-chronological: Experience first, then Projects, then Technical Skills, Education, Awards |
| Shipping an Experience or Project entry with a single bullet | Every entry carries at least two bullets — merge it into a stronger entry, or drop the entry. The template's range is around 2 to 4; a fifth needs a page-fill reason |
| Writing a one-line Experience heading, or any `Title \| Company` pipe | Since 2026-09-19 the heading is **two lines in one paragraph**: `COMPANY NAME` → tab → `City, Prov`, `<w:br/>`, then `Job Title` → tab → dates. The old title-first pipe is the most common drift here because `master-experience.md` still records entries title-first; `scripts/verify-resume-pattern.py` catches it |
| Rendering the company in mixed case | The company renders **ALL CAPS** at `sz=20` (`ASSOCIATED GROCERS`), matching the bold location beside it |
| Putting the location at the end of the header contact line | Since 2026-09-19 the contact line **leads** with the location: `Surrey, BC \| phone \| email \| LinkedIn \| GitHub \| Portfolio` |
| Dropping the location, or putting it on the job-title line | The location sits on **line 1, after the right tab**, beside the company — bold `sz=20`. Line 2 carries the job title and the dates |
| A project heading with no tech stack | The template reads `[Project Heading] \| [Technologies used]` — the stack is part of the heading and is prime keyword real estate |
| Repeating an award in both Awards and Education / a project bullet | One canonical home per fact: when Awards carries it, the other section drops it |
| Inventing an award or certification to fill the Awards section | Awards come only from the `## Awards & Honors` block in `master-education.md`; below two genuine items, omit the section and flag the gap |
| Applying an engineering-manager lens to an analyst (or ML) role | Match the reviewer persona to the Preflight role track (dev / ML / analyst) |
| Skipping the recruiter phone-screen prep | Produce `phone-screen-narrative.md`; the call decides more than the resume |
| Parsing a PDF or looking for `master.md` | Read the four `database/*.md` files instead |
| Switching the main folder's branch (clobbers parallel runs) | Never `git checkout` a JD branch in the main folder; create a worktree with `git worktree add "D:/github/job-hunting-worktrees/<slug>" -b <slug> main` and work there |
| Worktree shows all 80+ past `applications/*` folders (looks like the whole repo) | `main` is the archive, so a plain worktree checks out everything. Right after `worktree add`, run `sparse-checkout set --cone database "application"`. Use `--cone` only — `--no-cone` patterns silently de-materialize tracked files |
| Leaving artifacts untracked (a concurrent `git clean` can wipe them) | Commit `application/` to the branch after approval; the branch is the durable safe copy |
| Removing a worktree with uncommitted work | Check `git -C "<worktree>" status` is clean first; if anything is uncommitted (e.g. a compiled PDF), stop and warn |
| Guessing the company or role | Ask the user when the JD is ambiguous |
| Skipping a persona | Quote it verbatim before working |
| Inserting an unbacked JD keyword | Move it to `keyword-gaps.md` |
| Generic, templated cover letter | Tie every paragraph to real accomplishments and the JD's top requirements |
| Rebuilding the resume format from scratch | Fill the provided `resume-template.docx` by editing its `word/document.xml` (docx-js cannot open existing files); keep every template style and never change approved wording |
| Rewording or adding claims while filling the `.docx` | Render the approved markdown faithfully into the template; escape XML specials (`& < >`) but never change content. If Step 10's fit check reports underfill, the fix is to go back to Step 4 and add real content to `tailored-resume.md` for re-approval — never to add it directly to the `.docx` |
| Handing off the resume without running both Step 10 checks | Run `scripts/verify-resume-pattern.py` (template shape) **and** `scripts/verify-resume-fit.ps1` (exactly 1 page, ≥92% fill) on `Dhruvkumar_Resume.docx` before handoff; eyeballing it in Word, or assuming it fits, is the mistake |
| Using LaTeX / Jake's format or producing a `.tex` or PDF | Out of scope: this skill outputs `.docx` only, filled from the user's templates; the user exports the PDF from Word |
| Cover-letter `.docx` template missing | It lives at `cover-letter-template/cover-letter-template.docx`; if absent, pause and ask the user — never fall back to LaTeX or invent a format |
| Skipping outreach because the cover letter felt sufficient | The cover letter rides inside the ATS; the outreach kit (Step 9) is what puts the application in front of a human — produce it every time, mandatory for ML/AI roles |
| Personalizing outreach or the cover letter with invented company facts | Every company claim traces to `company-research.md` (sourced) or the JD; empty research → JD-only version |
| Sending outreach automatically | Never — everything in `outreach.md` is a draft the user sends manually |
| Letting `tracker.md` rot after submission | Update the row on every status report; list due follow-ups whenever the tracker is touched — silence with no follow-up is how applications die |
| Updating `tracker.md` but forgetting `application-tracker.xlsx` (or vice versa) | They are registered in the same step and committed together; the xlsx row is added/updated via `scripts/update-application-tracker.py` |
| Editing `application-tracker.xlsx` by hand or rebuilding it with a new script | Always go through `scripts/update-application-tracker.py` — it creates month tabs with the Status dropdown, dedupes on company+role, and keeps formatting consistent |
| Writing `tracker.md` or `application-tracker.xlsx` inside a worktree | Both trackers live only in the main folder on `main`; worktrees are per-application workspaces |