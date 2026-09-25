# applying-to-job

A [Claude Code skill](https://code.claude.com/docs/en/skills) that turns a pasted job description into a complete job application, reviewed one step at a time: an honest fit check, a tailored one-page resume, a cover letter, recruiter phone-screen prep, and outreach drafts. The resume and cover letter come out as Word files filled from your own templates. Each posting gets its own git branch, and every application is logged in a tracker.

It won't invent experience. Every claim comes from your own profile files, and job keywords you can't back up are listed as gaps instead of being slipped into your resume.

> [!NOTE]
> This skill grew out of the author's own job search and is shared as-is. It expects a specific workspace layout and has the author's file paths written into `SKILL.md`. The [`job-hunting/`](job-hunting) folder is a copy of the author's workspace for you to start from, and the [install steps](#install) cover the rest.

## What it does

Paste a job posting and the skill works through 11 steps, stopping after each one for your review:

| Step | What happens | Saved as |
|---|---|---|
| 0 | Fit and referral check: apply, stretch-apply, or skip? Do you know anyone there? | |
| 1 | Creates a git branch and worktree for this posting | `jd.md`, `fit-and-referral.md` |
| 2 | Loads your master profile | |
| 3 | Pulls the must-haves, skills, and keywords out of the posting | `jd-analysis.md` |
| 4 | Tailors your resume and lists the keyword gaps | `tailored-resume.md`, `keyword-gaps.md` |
| 5 | Checks keyword coverage and that the resume will parse cleanly | `keyword-coverage.md` |
| 6 | Simulates a hiring manager's 10-second skim | `hiring-manager-scan.md` |
| 7 | Researches the company, then writes the cover letter | `company-research.md`, `cover-letter.md` |
| 8 | Prepares your answers for the recruiter phone screen | `phone-screen-narrative.md` |
| 9 | Drafts a referral request, a note to the recruiter, and a follow-up | `outreach.md` |
| 10 | Fills your Word templates and checks the resume is exactly one full page | `<Name>_Resume.docx`, `<Name>_Cover_Letter.docx` |

Once you approve the final files, it commits them to the posting's branch and logs the application in `tracker.md` and `application-tracker.xlsx`. Later, tell it "I submitted the Acme one" or "Acme rejected me" and it updates the tracker and lists any follow-ups that are due.

Outreach messages are drafts only. The skill never sends anything.

## Requirements

- **Claude Code**: the CLI, the desktop app, or an IDE extension. The skill works on your local files, runs git, and drives Microsoft Word, so it can't run end to end as an uploaded skill in claude.ai chats.
- **Git**, for the per-application branches and worktrees.
- **Anthropic's `docx` skill**, which Step 10 uses to fill your Word templates. If you don't have it, run these in Claude Code:

  ```text
  /plugin marketplace add anthropics/skills
  /plugin install document-skills@anthropic-agent-skills
  ```

- **Windows with Microsoft Word** for Step 10's page checks, which run Word through PowerShell. The skill was built on Windows 11; on macOS or Linux you'll need your own way to check the page count.
- **Python 3** for the helper scripts. The tracker script needs `openpyxl` (`pip install openpyxl`).

## Install

### 1. Clone the skill

Clone this repo into your personal skills folder and name the folder `applying-to-job`. Claude Code uses the folder name as the command name.

macOS / Linux:

```bash
git clone https://github.com/pateldhruvkumar/claude-skill-for-job-application.git ~/.claude/skills/applying-to-job
```

Windows (PowerShell):

```powershell
git clone https://github.com/pateldhruvkumar/claude-skill-for-job-application.git "$env:USERPROFILE\.claude\skills\applying-to-job"
```

To confirm it loaded, run `/skills` in Claude Code and look for `applying-to-job`. Claude Code picks up new skills without a restart, unless `~/.claude/skills` didn't exist when your session started. In that case, restart it once.

### 2. Create your workspace

The skill runs inside a git repo that holds your master profile, Word templates, and helper scripts. The [`job-hunting/`](job-hunting) folder in this repo is a copy of the author's setup. Copy it to wherever you want your workspace:

macOS / Linux:

```bash
cp -R ~/.claude/skills/applying-to-job/job-hunting ~/job-hunting
```

Windows (PowerShell):

```powershell
Copy-Item -Recurse "$env:USERPROFILE\.claude\skills\applying-to-job\job-hunting" "$env:USERPROFILE\job-hunting"
```

The copy also includes the author's own `tracker.md`. Delete it from your copy so your tracker starts empty:

macOS / Linux:

```bash
rm ~/job-hunting/tracker.md
```

Windows (PowerShell):

```powershell
Remove-Item "$env:USERPROFILE\job-hunting\tracker.md"
```

Once it's in use, your workspace looks like this:

```text
job-hunting/
├── database/
│   ├── master-personal-info.md      name, city, phone, email, LinkedIn, GitHub, portfolio
│   ├── master-experience.md         every job, with every true bullet you might use
│   ├── master-project.md            every project, with its stack, dates, and results
│   └── master-education.md          degrees, plus an "## Awards & Honors" section
├── resume-template/
│   └── resume-template.docx         one-page Word resume template
├── cover-letter-template/
│   └── cover-letter-template.docx   Word cover-letter template
├── scripts/                         helper scripts (see below)
│   ├── verify-resume-pattern.py
│   ├── verify-resume-fit.ps1
│   ├── update-application-tracker.py
│   └── test-*.ps1                   the author's tests for the scripts
├── docs/                            the author's design notes and plans
├── applications/                    finished applications, archived here as you go
├── tracker.md                       created by the skill
└── application-tracker.xlsx         created by the tracker script
```

1. **Replace the author's profile with yours.** The four `database/*.md` files hold the author's own history as an example of the format. Rewrite them with yours. They're the only thing the skill draws from, so include everything true you might want on a resume. It won't add anything that isn't there.
2. **Put your details in both Word templates.** Open them in Word and swap the author's name, contact line, and links for yours.
3. **Commit it all to `main`.** Every application branch is cut from `main`:

   ```bash
   cd ~/job-hunting
   git init -b main
   git add .
   git commit -m "Add master profile and templates"
   ```

Each application then gets its own worktree in a sibling folder named after your workspace, for example `job-hunting-worktrees/2026-07-06-stripe-full-stack-engineer/`.

#### Helper scripts

Step 10 and the tracker updates call three scripts in your workspace's `scripts/` folder:

| Script | What it does |
|---|---|
| `verify-resume-pattern.py` | Compares the generated resume with `resume-template.docx` and fails if the layout drifted: heading shapes, font sizes and weights, entries with fewer than two bullets, margins |
| `verify-resume-fit.ps1` | Opens the resume in Word and passes only if it's exactly one page with at least 92% of the usable height filled |
| `update-application-tracker.py` | Adds or updates rows in `application-tracker.xlsx`: one sheet per month, with a Status dropdown. Subcommands: `add` and `set-status` |

`verify-resume-fit.ps1` drives Microsoft Word through PowerShell, so it only runs on Windows. On a Mac, ask Claude to skip that check, then open the resume in Word and confirm it fills exactly one page.

The two `test-*.ps1` files are the author's own tests for these scripts. `test-verify-resume-fit.ps1` uses two of the author's past resumes, which aren't included, so it won't fully run in your copy.

#### Your resume template

Step 10's formatting rules match the included `resume-template.docx`: the section order (Experience, Projects, Technical Skills, Education, Awards), two-line headings with the company first, and exact font sizes and tab stops. Keep its layout when you add your details. If you switch to a different template, update Step 4's rules and Step 10's heading table in `SKILL.md` to match it.

### 3. Point the skill at your paths

`SKILL.md` has the author's paths written in, all in that one file. Replace them with your own:

| Find | Replace with |
|---|---|
| `D:/github/job-hunting` and `D:\github\job-hunting` | your workspace, e.g. `/Users/jane/job-hunting` or `C:/Users/jane/job-hunting` |
| `C:/Users/Dhruv/.claude/skills/applying-to-job` | `${CLAUDE_SKILL_DIR}` (Claude Code fills in the skill's own folder), or the full path where you cloned it |
| `Dhruvkumar_` | the prefix for your output files, e.g. `Jane_Doe_` |

The first row also moves the worktree folder (`D:/github/job-hunting-worktrees`), since its path starts with the workspace path.

Or have Claude Code make the edits. Paste this into a session, with your own values:

```text
In ~/.claude/skills/applying-to-job/SKILL.md, replace every "D:/github/job-hunting" and "D:\github\job-hunting" with "/Users/jane/job-hunting", every "C:/Users/Dhruv/.claude/skills/applying-to-job" with "${CLAUDE_SKILL_DIR}", and every "Dhruvkumar_" with "Jane_Doe_".
```

## Usage

Open Claude Code in your workspace folder, since that's where the skill expects to start:

```bash
cd ~/job-hunting
claude
```

Paste a job description and ask for an application, for example "Apply to this role" or "Tailor my resume for this posting". You can also type `/applying-to-job` and paste the posting after it.

The skill starts with the fit-and-referral check and waits for your go-ahead before creating anything. After that it stops after every step so you can review and edit. The finished files end up in `job-hunting-worktrees/<slug>/application/`, committed to that posting's branch.

To update an application's status, just say so:

- "I submitted the Acme application"
- "I got a phone screen with Acme"
- "Acme rejected me"
- "Which follow-ups are due?"

## Update or uninstall

To pull the latest version (your path edits are stashed and re-applied automatically):

```bash
cd ~/.claude/skills/applying-to-job
git pull --rebase --autostash
```

To uninstall, delete the `~/.claude/skills/applying-to-job` folder.

## What's in this repo

```text
SKILL.md                  the workflow, rules, and reviewer personas
guidelines/
  action-verbs.md         verb bank for resume bullets
  bullet-points.md        the XYZ bullet formula and credibility checks
references/
  llm-tells.md            AI-sounding words and punctuation to scrub
templates/                skeletons for the Markdown files the skill writes
job-hunting/              a copy of the author's workspace to start yours from
  database/               the author's profile files, as a format example
  resume-template/        Word resume template
  cover-letter-template/  Word cover-letter template
  scripts/                helper scripts the skill runs
  docs/                   the author's design notes and plans
  tracker.md              the author's tracker (delete it in your copy)
```
