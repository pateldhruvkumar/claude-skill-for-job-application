# Flatten Worktrees to `application/` — Implementation Plan

> **For agentic workers:** This is git-migration + Markdown-editing work, not code. Steps use checkbox (`- [ ]`) syntax. Execute **inline** (subagent-driven is inappropriate for live git surgery on the user's repo). Verification steps replace unit tests.

**Goal:** Make every job worktree show its deliverables directly under a generic `application/` folder (no repeated slug), name the Word deliverables `Dhruvkumar_Resume.docx` / `Dhruvkumar_Cover_Letter.docx`, and update the `applying-to-job` skill so all future applications follow the new layout — without ever touching `main`'s `applications/<slug>/` archive.

**Architecture:** Each per-job branch renames its committed `applications/<slug>/` tree to `application/` (one cosmetic commit per branch), re-narrows sparse-checkout to `application`, and renames the two Word deliverables (no-clobber). The skill's worktree-context paths change to `application/`; `main`'s archive stays `applications/<slug>/`, bridged by a new path-remapping archive command. `main` itself is never modified by the migration.

**Tech Stack:** Git worktrees + cone-mode sparse-checkout, Git Bash, Markdown.

## Global Constraints

- Generic folder name is exactly `application/` (singular).
- Deliverable filenames are exactly `Dhruvkumar_Resume.docx` and `Dhruvkumar_Cover_Letter.docx`.
- **Never touch `main`:** the migration only commits on `job-hunting-worktrees/*` branches. `main`'s HEAD SHA and tracked tree must be identical before and after.
- **Never clobber a hand-made file:** rename a deliverable only if the target name does not already exist.
- **Never touch a dirty worktree:** skip any worktree with uncommitted changes and report it.
- Idempotent: re-running the migration makes no further changes.
- `main`'s `applications/<slug>/` archive layout and its historical filenames are out of scope — unchanged.

---

## Task 1: Migration script + dry-run

**Files:**
- Create: `<scratchpad>/flatten-worktrees.sh`
- Writes (on apply only): `<scratchpad>/flatten-pre-shas.log`

Where `<scratchpad>` = `C:/Users/Dhruv/AppData/Local/Temp/claude/D--github-job-hunting/2a13d06f-b321-49b3-b476-b01ca3817cd4/scratchpad`.

- [ ] **Step 1: Record `main`'s pre-migration state**

Run:
```bash
git -C "D:/github/job-hunting" rev-parse HEAD | tee /tmp/main-head-before.txt
git -C "D:/github/job-hunting" status --porcelain --untracked-files=no
```
Expected: a SHA saved; no *tracked* modifications (untracked spec/plan docs are fine).

- [ ] **Step 2: Write the migration script**

Create `<scratchpad>/flatten-worktrees.sh` with exactly:
```bash
#!/usr/bin/env bash
# flatten-worktrees.sh — flatten job worktrees to application/ + rename deliverables
# Usage: bash flatten-worktrees.sh            (dry-run, default)
#        bash flatten-worktrees.sh --apply     (perform changes)
set -uo pipefail

MAIN="D:/github/job-hunting"
SHALOG="C:/Users/Dhruv/AppData/Local/Temp/claude/D--github-job-hunting/2a13d06f-b321-49b3-b476-b01ca3817cd4/scratchpad/flatten-pre-shas.log"
APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

mig=0; sdirty=0; sdone=0; sanom=0

while IFS= read -r wt; do
  case "$wt" in *job-hunting-worktrees*) ;; *) continue ;; esac
  [ -d "$wt" ] || { echo "SKIP missing-dir: $wt"; continue; }
  slug="$(basename "$wt")"

  if [ -d "$wt/application" ] && [ ! -d "$wt/applications/$slug" ]; then
    echo "SKIP already-migrated: $slug"; sdone=$((sdone+1)); continue
  fi
  if [ ! -d "$wt/applications/$slug" ]; then
    echo "SKIP no-applications-folder: $slug"; sanom=$((sanom+1)); continue
  fi
  if [ -n "$(git -C "$wt" status --porcelain)" ]; then
    echo "SKIP dirty: $slug"; sdirty=$((sdirty+1)); continue
  fi

  src="$wt/applications/$slug"
  rmsg=""
  if [ -f "$src/resume.docx" ]; then
    if [ -e "$src/Dhruvkumar_Resume.docx" ]; then rmsg="$rmsg [resume COLLISION-leave-both]"; else rmsg="$rmsg resume->Dhruvkumar_Resume"; fi
  fi
  if [ -f "$src/cover-letter.docx" ]; then
    if [ -e "$src/Dhruvkumar_Cover_Letter.docx" ]; then rmsg="$rmsg [cover COLLISION-leave-both]"; else rmsg="$rmsg cover-letter->Dhruvkumar_Cover_Letter"; fi
  fi
  echo "MIGRATE: $slug   HEAD=$(git -C "$wt" rev-parse --short HEAD)  rename:${rmsg:- none}"

  if [ "$APPLY" = "1" ]; then
    echo "$slug $(git -C "$wt" rev-parse HEAD)" >> "$SHALOG"
    git -C "$wt" sparse-checkout set --cone database "applications/$slug" application || { echo "  ERR sparse-add"; continue; }
    git -C "$wt" mv "applications/$slug" application || { echo "  ERR mv"; continue; }
    if [ -f "$wt/application/resume.docx" ] && [ ! -e "$wt/application/Dhruvkumar_Resume.docx" ]; then
      git -C "$wt" mv application/resume.docx application/Dhruvkumar_Resume.docx
    fi
    if [ -f "$wt/application/cover-letter.docx" ] && [ ! -e "$wt/application/Dhruvkumar_Cover_Letter.docx" ]; then
      git -C "$wt" mv application/cover-letter.docx application/Dhruvkumar_Cover_Letter.docx
    fi
    git -C "$wt" sparse-checkout set --cone database application || { echo "  ERR sparse-set"; continue; }
    git -C "$wt" commit -q -m "restructure: flatten to application/ folder" && echo "  OK committed" || echo "  ERR commit"
    mig=$((mig+1))
  fi
done < <(git -C "$MAIN" worktree list --porcelain | awk '/^worktree /{print $2}')

echo "----"
echo "migrated=$mig  skip_done=$sdone  skip_dirty=$sdirty  skip_anom=$sanom  (apply=$APPLY)"
```

- [ ] **Step 3: Run the dry-run**

Run: `bash "<scratchpad>/flatten-worktrees.sh"`
Expected: ~83 `MIGRATE:` lines, `SKIP dirty:` for `2026-08-10-td-software-engineer-i` and `2026-08-10-vretta-data-analyst`, summary `migrated=0 skip_dirty=2` (nothing changed — apply=0).

- [ ] **Step 4: Review the report**

Read the output. Confirm: exactly the 2 known dirty worktrees are skipped; any `no-applications-folder` anomalies are noted; collision flags (e.g. `ea`) look right. No commits were made (apply=0). **Checkpoint — do not proceed until the report looks correct.**

---

## Task 2: Validate on one worktree

Prove the exact procedure on a single clean worktree before the batch. Uses `2026-08-10-kpmg-amds-software-developer-coop` (clean, has both `resume.docx` and `cover-letter.docx` → exercises folder move + both renames).

**Interfaces:**
- Produces: a migrated `kpmg` worktree that the batch run (Task 3) will then skip as `already-migrated`.

- [ ] **Step 1: Migrate the one worktree**

Run:
```bash
WT="D:/github/job-hunting-worktrees/2026-08-10-kpmg-amds-software-developer-coop"
git -C "$WT" rev-parse HEAD
git -C "$WT" sparse-checkout set --cone database "applications/2026-08-10-kpmg-amds-software-developer-coop" application
git -C "$WT" mv "applications/2026-08-10-kpmg-amds-software-developer-coop" application
git -C "$WT" mv application/resume.docx application/Dhruvkumar_Resume.docx
git -C "$WT" mv application/cover-letter.docx application/Dhruvkumar_Cover_Letter.docx
git -C "$WT" sparse-checkout set --cone database application
git -C "$WT" commit -q -m "restructure: flatten to application/ folder"
```

- [ ] **Step 2: Verify on-disk layout and cleanliness**

Run:
```bash
ls -1 "$WT"                    # expect: application/ database/ tracker.md application-tracker.xlsx (no applications/)
ls -1 "$WT/application" | grep -E 'Dhruvkumar_(Resume|Cover_Letter).docx'
[ -d "$WT/applications" ] && echo "FAIL: applications/ still present" || echo "OK: no applications/"
git -C "$WT" status --porcelain   # expect: empty (clean)
```
Expected: `application/` holds the files including both renamed `.docx`; no `applications/` on disk; working tree clean.

- [ ] **Step 3: Verify `main` still untouched**

Run: `diff <(git -C "D:/github/job-hunting" rev-parse HEAD) /tmp/main-head-before.txt && echo "OK main HEAD unchanged"`
Expected: `OK main HEAD unchanged`.

**Checkpoint — confirm the validation worktree looks right before batching.**

---

## Task 3: Batch-migrate the rest + verify

- [ ] **Step 1: Apply to all remaining clean worktrees**

Run: `bash "<scratchpad>/flatten-worktrees.sh" --apply`
Expected: `MIGRATE … OK committed` for each clean, not-yet-migrated worktree; `SKIP already-migrated: 2026-08-10-kpmg…`; `SKIP dirty:` for td and vretta; summary e.g. `migrated=82 skip_done=1 skip_dirty=2`.

- [ ] **Step 2: Verify a 3-era sample**

Run:
```bash
for s in 2026-08-04-rbc-ai-engineer 2026-07-20-ea-data-analyst 2026-07-07-fgf-ai-engineer; do
  W="D:/github/job-hunting-worktrees/$s"
  echo "== $s =="; ls -1 "$W" | tr '\n' ' '; echo
  [ -d "$W/applications" ] && echo "  FAIL applications/ present" || echo "  OK flat"
  git -C "$W" status --porcelain | head
done
```
Expected: each shows `application/` + `database/`, no `applications/`, clean status. (`ea` keeps its pre-existing `Dhruvkumar_Cover_Letter.docx`; `fgf` is a `.tex`-era folder moved intact with no rename.)

- [ ] **Step 3: Verify idempotency**

Run: `bash "<scratchpad>/flatten-worktrees.sh"`  (dry-run again)
Expected: every clean worktree now reports `SKIP already-migrated`; only td/vretta report `SKIP dirty`; `migrated=0`.

- [ ] **Step 4: Verify `main` untouched after the full batch**

Run:
```bash
diff <(git -C "D:/github/job-hunting" rev-parse HEAD) /tmp/main-head-before.txt && echo "OK main HEAD unchanged"
git -C "D:/github/job-hunting" status --porcelain --untracked-files=no
```
Expected: `OK main HEAD unchanged`; no tracked modifications.

- [ ] **Step 5: Report skipped worktrees to the user**

State which worktrees were skipped (td, vretta — dirty; any anomalies). Tell the user they can commit those and I'll re-run the (idempotent) script.

---

## Task 4: Update the `applying-to-job` skill

**Files:**
- Modify: `C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md`

Every `applications/<slug>` reference in SKILL.md is worktree-context (the archive step is undocumented), so it all becomes `application`. The plural glob `applications/*` (describing `main`'s full archive) must stay.

- [ ] **Step 1: Repoint worktree paths**

Edit (replace_all): `applications/<slug>` → `application`.
This turns `applications/<slug>/X` into `application/X`, sparse args `"applications/<slug>"` into `"application"`, and the tracker `--jd-file` path into `…/<slug>/application/jd.md`. It does **not** touch `applications/*`.

- [ ] **Step 2: Rename the deliverables in the skill**

Edit (replace_all): `resume.docx` → `Dhruvkumar_Resume.docx`
Edit (replace_all): `cover-letter.docx` → `Dhruvkumar_Cover_Letter.docx`
(Safe: `resume-template.docx` / `cover-letter-template.docx` do not contain those exact substrings.)

- [ ] **Step 3: Add the documented archive step**

In "After the Workflow", immediately before the **Cleanup** subsection, insert:
```markdown
**Archive into `main` (when filing the finished application into the permanent archive).**

The branch stores artifacts under `application/`, but `main`'s archive keeps every job at `applications/<slug>/`. So archiving is a path-remap, not a plain merge:

    git -C "D:/github/job-hunting" read-tree --prefix="applications/<slug>/" -u "<slug>:application"
    git -C "D:/github/job-hunting" commit -m "archive: <slug>"

Run this from a clean `main`. It grafts the branch's `application/` tree into `main` at `applications/<slug>/`. Because it is not a merge, `git branch --merged` will not flag archived branches — to check whether a job is already archived, test the folder: `git -C "D:/github/job-hunting" cat-file -e "main:applications/<slug>/jd.md"` (exit 0 = already archived).
```

- [ ] **Step 4: Verify no stragglers**

Run:
```bash
grep -nE 'applications/<slug>|[^-]resume\.docx|[^-]cover-letter\.docx' "C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md"
```
Expected: the only `applications/<slug>/` hits are inside the new archive step (Step 3); no bare `resume.docx`/`cover-letter.docx` remain. Also confirm `applications/*` (plural glob) is still present where it describes the full archive:
`grep -n 'applications/\*' "C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md"` → still there.

---

## Task 5: Update memory

**Files:**
- Modify: `C:/Users/Dhruv/.claude/projects/D--github-job-hunting/memory/concurrent-sessions-worktree.md`
- Modify (if the hook line needs it): `C:/Users/Dhruv/.claude/projects/D--github-job-hunting/memory/MEMORY.md`

- [ ] **Step 1: Update the worktree memory**

Change the sparse-checkout target from `applications/<slug>` to `application`, and note the flatten + deliverable filrenames (`Dhruvkumar_Resume.docx` / `Dhruvkumar_Cover_Letter.docx`) and the new read-tree archive step. Keep it one fact, updated in place (don't duplicate).

- [ ] **Step 2: Sync the index line**

If the MEMORY.md hook line for that memory mentions the old `applications/<slug>` sparse target, update it to match.

---

## Self-Review

- **Spec coverage:** folder rename (Tasks 1–3), deliverable rename no-clobber (script + Task 2/4), skill repath + filenames + archive step (Task 4), migrate all existing (Task 3), main untouched (Tasks 1/2/3 verifications), memory follow-up (Task 5). All spec sections covered.
- **Placeholders:** none — full script and exact edits included.
- **Consistency:** folder `application/`, files `Dhruvkumar_Resume.docx` / `Dhruvkumar_Cover_Letter.docx`, and the read-tree archive command are identical across spec and plan.
