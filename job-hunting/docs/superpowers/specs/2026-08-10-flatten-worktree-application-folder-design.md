# Flatten worktree layout to a generic `application/` folder — Design

**Date:** 2026-08-10
**Status:** Approved (pending spec review)
**Author:** Dhruv + Claude

## Problem

Inside every job worktree, the deliverables are three levels deep with the job
name repeated:

```
job-hunting-worktrees/
└── 2026-08-10-kpmg-amds-software-developer-coop/     ← worktree root (slug)
    └── applications/
        └── 2026-08-10-kpmg-amds-software-developer-coop/   ← slug AGAIN
            └── resume.docx, cover-letter.docx, …
```

Browsing to the files means clicking through the slug name twice. The inner
`applications/<slug>/` folder exists because that is the path the artifacts are
**committed** at on each per-job branch, and a git worktree always materializes
files at their committed path. `main` archives each job by `git merge`-ing the
branch, which only works because the branch path and `main`'s archive path are
identical (`applications/<slug>/`).

## Goal / End state

**A worktree (what the user browses):**

```
job-hunting-worktrees/
└── 2026-08-10-kpmg-amds-software-developer-coop/     ← the job folder
    ├── application/          ← deliverables directly here; name never repeats
    │   ├── Dhruvkumar_Resume.docx
    │   ├── Dhruvkumar_Cover_Letter.docx
    │   ├── company-research.md, jd.md, …
    ├── database/
    └── tracker.md, application-tracker.xlsx   (repo-root files, unchanged)
```

**`main`'s permanent archive (DELIBERATELY UNCHANGED):**

```
job-hunting/applications/
├── 2026-08-10-kpmg-amds-software-developer-coop/     ← still keyed by slug
├── 2026-08-06-startech-data-analyst/                 (flat list, no repetition)
└── …
```

The branch/worktree uses `application/`; `main`'s archive stays
`applications/<slug>/`; a path-remapping archive step bridges the two.

## Decisions (approved)

- **Generic folder name:** `application/` (singular). Matches the user's mental
  model ("open the application"). On disk a worktree only ever shows
  `application/` + `database/`, so there is no visible clash with `main`'s
  plural `applications/`.
- **Deliverable filenames:** the final Word files are named
  `Dhruvkumar_Resume.docx` and `Dhruvkumar_Cover_Letter.docx` (was
  `resume.docx` / `cover-letter.docx`). This matches the existing exported-PDF
  convention (`Dhruvkumar_Resume.pdf`). Working `.md` files
  (`tailored-resume.md`, `cover-letter.md`, etc.) keep their names — they are
  internal, not deliverables.
- **Scope:** all 85 existing worktrees **and** all future applications (the
  `applying-to-job` skill).
- **`main`'s archive is out of scope:** its layout stays `applications/<slug>/`
  and its already-archived files keep their historical names. Only the branch
  side and the going-forward convention change. New jobs archive with the new
  names naturally.

## Changes

### A. `applying-to-job` skill (all future applications)

File: `C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md`

Replace **worktree/branch-context** paths `applications/<slug>/` → `application/`,
while **keeping** `main`-archive-context paths as `applications/<slug>/`:

1. **Step 1 (worktree + sparse-checkout):**
   `sparse-checkout set --cone database "applications/<slug>"` →
   `sparse-checkout set --cone database application`.
   `mkdir applications/<slug>` → create `application/`. Save `jd.md` and
   `fit-and-referral.md` to `application/`.
2. **Steps 3–10 (all artifacts):** every output path
   `applications/<slug>/X` → `application/X`.
3. **Step 10 (Word output filenames):** outputs become
   `application/Dhruvkumar_Resume.docx` and
   `application/Dhruvkumar_Cover_Letter.docx`. Update the validate/one-page-verify
   commands and the Outputs line accordingly.
4. **After the Workflow:** artifact list under `application/`; commit step
   `git add application/`; tracker `--jd-file` path
   `…/<slug>/application/jd.md`; "reopen a past application" sparse-checkout uses
   `application`.
5. **New documented archive step** (see B) — currently undocumented.
6. **Key Rules / Common Mistakes:** update the sparse-checkout example and any
   `applications/<slug>/` references that are worktree-context.

### B. Archive step (branch → `main`)

Replace the current implicit `git merge <slug>` with a path-remapping archive
that deposits the branch's `application/` into `main` at `applications/<slug>/`:

```
git -C "D:/github/job-hunting" read-tree --prefix="applications/<slug>/" -u "<slug>:application"
git -C "D:/github/job-hunting" commit -m "archive: <slug>"
```

`<slug>:application` resolves to the `application` tree at the branch tip; the
prefix grafts it under `applications/<slug>/` in `main`. `main`'s archive layout
is therefore identical to today.

- Consequence: "archive: <slug>" becomes a normal (single-parent) commit, so
  `git branch --merged main` no longer detects archived branches. New
  archived-state check: does `main` contain the folder, i.e.
  `git -C <main> cat-file -e "main:applications/<slug>/jd.md"`. Document this in
  the skill.

### C. Migrate the 85 existing worktrees

An idempotent migration (script in scratchpad; not committed to the repo). For
each registered worktree under `job-hunting-worktrees/` with branch `<slug>`:

1. **Skip if dirty:** `git -C <wt> status --porcelain` non-empty → skip + report
   (never touch uncommitted work). Known dirty now: `2026-08-10-td-software-engineer-i`,
   `2026-08-10-vretta-data-analyst`.
2. **Skip if already migrated:** `application/` exists and `applications/<slug>/`
   does not → skip.
3. **Skip if anomalous:** no `applications/<slug>/` present → skip + report
   (e.g. a non-standard worktree).
4. **Flatten:** `git -C <wt> mv applications/<slug> application`.
5. **Rename deliverables, no-clobber:** inside `application/`, if
   `Dhruvkumar_Resume.docx` does **not** already exist and `resume.docx` does →
   `git mv resume.docx Dhruvkumar_Resume.docx`. Same for
   `cover-letter.docx` → `Dhruvkumar_Cover_Letter.docx`. If the target already
   exists (e.g. `ea` has a hand-made `Dhruvkumar_Cover_Letter.docx`), leave both
   untouched and report — never destroy a hand-made file.
6. **Re-narrow:** `git -C <wt> sparse-checkout set --cone database application`.
7. **Commit:** `git -C <wt> commit -m "restructure: flatten to application/ folder"`.
8. **Verify:** `application/` present on disk with files; `applications/` gone
   from disk; `git status` clean.

Order matters in steps 4→6: do **not** run `sparse-checkout reapply` between the
`git mv` and the new `sparse-checkout set`, or `application/` (not yet in the
cone) could be de-materialized. Set the new cone before committing.

Run **dry-run first** (report per-worktree action, capture each branch's
pre-migration commit SHA), then **validate the full procedure on one clean
worktree** and spot-check it, then execute the batch.

## Edge cases

- **Dirty worktrees** (`td`, `vretta`): skipped; reported so the user can commit,
  then re-run (idempotent).
- **Rename collision** (`ea` and any worktree with a pre-existing
  `Dhruvkumar_*.docx`): no-clobber rule leaves files intact; reported.
- **No `applications/<slug>/`**: skipped + reported.
- **Legacy `.tex`/PDF-era worktrees**: flatten still applies (moves whatever is
  in the folder); no `.docx` to rename → rename step is a no-op.
- **Inherited `applications/<other>/` in each branch tree**: branches were cut
  from `main`, so their trees carry every other job's folder (already hidden by
  sparse-checkout today). The move touches only `<slug>`; the others stay
  tracked-but-hidden. Harmless, unchanged from today.

## Safety

- **`main` is never modified** by the migration — only per-job branches get one
  cosmetic commit each. The permanent archive is untouched throughout.
- Pre-migration branch SHAs are captured; any single branch is trivially
  restorable (`git -C <wt> reset --hard <sha>`).
- Dry-run precedes any commit.

## Out of scope (deliberately unchanged)

`main`'s `applications/<slug>/` archive layout and historical filenames; the
database masters; `tracker.md` / `application-tracker.xlsx`.

## Verification

- Spot-check 3 migrated worktrees (one recent `.docx` era, one PDF era, one
  legacy `.tex` era): `application/` holds the files, deliverables renamed where
  applicable, `git status` clean.
- Confirm `main` HEAD and `applications/` are byte-for-byte unchanged after
  migration (`git -C <main> status` clean; HEAD SHA unchanged).
- Re-run the migration to confirm idempotency (all report "already migrated").

## Follow-up

- Update memory `concurrent-sessions-worktree.md` (sparse-checkout target is now
  `application`, not `applications/<slug>`).
