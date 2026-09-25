# Resume Format (Chronological, Full-Page, Awards) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Change the `applying-to-job` skill so every generated resume has no Summary, runs in reverse-chronological order (Experience, Projects, Technical Skills, Education, Awards), fills a full page with at least two bullets per Experience/Project entry, and is machine-verified in Word.

**Architecture:** Four artifacts change together. `resume-template/resume-template.docx` is the format's source of truth and gets paragraph-level surgery (delete Summary, relocate Technical Skills, append Awards). `database/master-education.md` gains a canonical `## Awards & Honors` block. The skill's `SKILL.md` and `templates/tailored-resume.template.md` are rewritten to match and to reverse the existing anti-fill rules. A new `scripts/verify-resume-fit.ps1` turns "fills the page" from a judgement call into a pass/fail gate driven by Word COM.

**Tech Stack:** PowerShell 5.1 + Word COM automation (page count and vertical position), Python 3.14 `zipfile`/`re` for OOXML editing, Markdown for the skill documents. No new dependencies.

## Global Constraints

- **Target section order, everywhere it is stated:** `Experience, Projects, Technical Skills, Education, Awards`. No Summary section anywhere.
- **Fill threshold:** `92` percent of usable page height. Exactly `1` page. Both edges enforced.
- **Cover letter is unchanged:** `pages <= 1`, no fill requirement. The full-page rule applies to the resume only.
- **Anti-fabrication is absolute.** Fill the page by adding real material from `database/*.md` only. Never invent claims, never inflate line spacing, never enlarge fonts, never widen margins.
- **Skill files live outside the repo** at `C:/Users/Dhruv/.claude/skills/applying-to-job/`. They are NOT covered by repo commits. Repo files (`resume-template/`, `database/`, `scripts/`, `docs/`) are committed to `main` in `D:/github/job-hunting`.
- **Never use `New-Item -Force` on an existing file** (it truncates). Use `Write`/`Edit` tools or Python for file content.
- **PowerShell 5.1:** no `&&`, no `||`, no ternary. Chain with `;` and `if ($?) { }`.
- **Set `PYTHONIOENCODING=utf-8`** before Python scripts that print non-ASCII.
- **Out of scope:** the five in-flight `2026-08-21-*` worktree applications keep their already-approved resumes.

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `scripts/verify-resume-fit.ps1` | Create | Single-purpose gate: is this `.docx` exactly one page and at least `MinFill`% full? Exits non-zero on failure. |
| `scripts/test-verify-resume-fit.ps1` | Create | Test harness for the above. Asserts all four verdicts against real fixtures. |
| `resume-template/resume-template.docx` | Modify | The format's source of truth. Paragraph surgery only — no style/font/numbering changes. |
| `database/master-education.md` | Modify | Add canonical `## Awards & Honors` block. |
| `C:/.../applying-to-job/templates/tailored-resume.template.md` | Modify | Section order, no Summary, Awards block, two-bullet minimum. |
| `C:/.../applying-to-job/SKILL.md` | Modify | Rules: order, no Summary, Awards, two-bullet minimum, full-page fill, verifier wiring. |

**Task order rationale:** Task 1 (verifier) ships first because Task 2 uses it as a measurement instrument. Tasks 5 and 6 split `SKILL.md` by theme so each intermediate commit leaves the document internally consistent — a half-reversed fill rule would make the skill contradict itself mid-run, which is the exact failure this plan exists to prevent.

---

### Task 1: Resume fit verifier + tests

**Files:**
- Create: `D:/github/job-hunting/scripts/verify-resume-fit.ps1`
- Test: `D:/github/job-hunting/scripts/test-verify-resume-fit.ps1`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `scripts/verify-resume-fit.ps1 -Path <docx> [-MinFill <double>]`. Emits one machine-readable line `RESULT pages=<int> fill=<double> min=<double> verdict=<PASS|FAIL> reason=<ok|overflow|underfill|missing-file>` followed by a human verdict line. Exit code `0` = PASS, `1` = overflow/underfill, `2` = missing file. Task 6 wires this into SKILL.md Step 10.

**Fixture facts (measured 2026-08-21, do not re-derive):**

| Fixture | Pages | Fill | Expected verdict |
|---|---|---|---|
| `resume-template/resume-template.docx` | 1 | 76.1% | FAIL / underfill |
| `applications/2026-07-13-larus-data-scientist/Dhruvkumar-Resume.docx` | 1 | 97.0% | PASS |
| `applications/2026-07-27-workstream-full-stack-engineer/Dhruvkumar_Resume.docx` | 1 | 94.4% | PASS |
| generated triple-body doc | 3 | n/a | FAIL / overflow |

The template stays a valid underfill fixture after Task 2 edits it (removing Summary lowers fill further), so the test asserts the **verdict**, never the exact percentage.

**Deliberate deviation from the spec:** the spec's Verification section named the 85.1% Stripe resume as the underfill case. That file lives in `job-hunting-worktrees/`, which is disposable — the worktree can be removed at any time and the test would break. `resume-template.docx` is tracked in git, always present, and always well under the line, so it is the durable substitute. The behaviour being verified is identical.

- [ ] **Step 1: Write the failing test**

Create `D:/github/job-hunting/scripts/test-verify-resume-fit.ps1`:

```powershell
<#
.SYNOPSIS
  Tests scripts/verify-resume-fit.ps1 against real fixtures covering every verdict.
.DESCRIPTION
  Run:  powershell -NoProfile -File scripts\test-verify-resume-fit.ps1
  Exits 0 when all cases pass, 1 otherwise.
#>
$ErrorActionPreference = 'Stop'

$repo     = Split-Path -Parent $PSScriptRoot
$verifier = Join-Path $PSScriptRoot 'verify-resume-fit.ps1'
$failures = 0
$ran      = 0

function Invoke-Verifier {
    param([string]$Target, [double]$MinFill = 92)
    # No 2>&1 — in PowerShell 5.1 redirecting a native command's stderr wraps each
    # line in a NativeCommandError ErrorRecord and corrupts $?. The verifier writes
    # everything to stdout anyway.
    $out  = & powershell -NoProfile -File $verifier -Path $Target -MinFill $MinFill
    $code = $LASTEXITCODE
    $line = ($out | Where-Object { $_ -match '^RESULT ' } | Select-Object -First 1)
    return [pscustomobject]@{ Exit = $code; Result = [string]$line; Raw = ($out -join "`n") }
}

function Assert-Case {
    param([string]$Name, [string]$Target, [string]$ExpectReason, [int]$ExpectExit)
    $script:ran++
    $r = Invoke-Verifier -Target $Target
    if ($r.Result -match "reason=$ExpectReason\b" -and $r.Exit -eq $ExpectExit) {
        Write-Host "PASS  $Name" -ForegroundColor Green
    } else {
        Write-Host "FAIL  $Name" -ForegroundColor Red
        Write-Host "      expected reason=$ExpectReason exit=$ExpectExit"
        Write-Host "      got      $($r.Result) exit=$($r.Exit)"
        $script:failures++
    }
}

# --- Fixture: a guaranteed multi-page document, built by tripling the template body ---
$overflow = Join-Path ([System.IO.Path]::GetTempPath()) 'verify-fit-overflow.docx'
$tmpl     = Join-Path $repo 'resume-template\resume-template.docx'
$py = @"
import re, zipfile
src = r'''$tmpl'''
dst = r'''$overflow'''
zin = zipfile.ZipFile(src)
doc = zin.read('word/document.xml').decode('utf-8')
m = re.search(r'(<w:body>)(.*?)(<w:sectPr\b)', doc, re.S)
new = doc[:m.end(1)] + m.group(2) * 3 + doc[m.end(2):]
zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    data = zin.read(it.filename)
    if it.filename == 'word/document.xml':
        data = new.encode('utf-8')
    zout.writestr(it, data)
zout.close()
"@
$pyFile = Join-Path ([System.IO.Path]::GetTempPath()) 'verify-fit-make-overflow.py'
Set-Content -LiteralPath $pyFile -Value $py -Encoding utf8
$env:PYTHONIOENCODING = 'utf-8'
python $pyFile
if (-not (Test-Path -LiteralPath $overflow)) { throw "could not build overflow fixture at $overflow" }

try {
    Assert-Case -Name 'underfill: bare template (76% full)' `
        -Target (Join-Path $repo 'resume-template\resume-template.docx') `
        -ExpectReason 'underfill' -ExpectExit 1

    Assert-Case -Name 'pass: larus resume (97% full)' `
        -Target (Join-Path $repo 'applications\2026-07-13-larus-data-scientist\Dhruvkumar-Resume.docx') `
        -ExpectReason 'ok' -ExpectExit 0

    Assert-Case -Name 'pass: workstream resume (94% full)' `
        -Target (Join-Path $repo 'applications\2026-07-27-workstream-full-stack-engineer\Dhruvkumar_Resume.docx') `
        -ExpectReason 'ok' -ExpectExit 0

    Assert-Case -Name 'overflow: tripled-body document (3 pages)' `
        -Target $overflow -ExpectReason 'overflow' -ExpectExit 1

    Assert-Case -Name 'missing file' `
        -Target (Join-Path $repo 'resume-template\does-not-exist.docx') `
        -ExpectReason 'missing-file' -ExpectExit 2
}
finally {
    Remove-Item -LiteralPath $overflow -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $pyFile   -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "$($ran - $failures)/$ran cases passed"
if ($failures -gt 0) { exit 1 }
exit 0
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
powershell -NoProfile -File scripts/test-verify-resume-fit.ps1
```

Expected: fails immediately — `verify-resume-fit.ps1` does not exist yet, so every `Assert-Case` reports a mismatch (or the `&` call errors). Non-zero exit.

- [ ] **Step 3: Write the verifier**

Create `D:/github/job-hunting/scripts/verify-resume-fit.ps1`:

```powershell
<#
.SYNOPSIS
  Verifies a generated resume .docx is exactly one page AND fills at least -MinFill percent of it.
.DESCRIPTION
  Used by the applying-to-job skill at Step 10. Both edges are failures:
  spilling onto a second page, and stopping short of the fill line.

  Emits one machine-readable line:
    RESULT pages=<int> fill=<double> min=<double> verdict=<PASS|FAIL> reason=<ok|overflow|underfill|missing-file>

  Exit codes: 0 = PASS, 1 = overflow or underfill, 2 = file not found.
.EXAMPLE
  powershell -NoProfile -File scripts\verify-resume-fit.ps1 -Path application\Dhruvkumar_Resume.docx
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [double]$MinFill = 92
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Path)) {
    Write-Output "RESULT pages=0 fill=0 min=$MinFill verdict=FAIL reason=missing-file"
    Write-Output "FAIL: file not found: $Path"
    exit 2
}
$full = (Resolve-Path -LiteralPath $Path).Path

$word = $null
$doc  = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    # Open read-only, no add-to-recent-files, so the source is never modified.
    $doc = $word.Documents.Open($full, $false, $true)

    $pages = [int]$doc.ComputeStatistics(2)          # wdStatisticPages
    $ps     = $doc.PageSetup
    $usable = $ps.PageHeight - $ps.TopMargin - $ps.BottomMargin

    # Vertical position of the last character, in points from the top of its page.
    $end  = $doc.Content.End
    $rng  = $doc.Range($end - 1, $end)
    $vpos = $rng.Information(6)                      # wdVerticalPositionRelativeToPage
    $fill = [math]::Round(100 * ($vpos - $ps.TopMargin) / $usable, 1)
}
finally {
    if ($null -ne $doc)  { $doc.Close($false)  | Out-Null }
    if ($null -ne $word) { $word.Quit()        | Out-Null }
    if ($null -ne $doc)  { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc)  | Out-Null }
    if ($null -ne $word) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null }
}

if ($pages -gt 1) {
    Write-Output "RESULT pages=$pages fill=$fill min=$MinFill verdict=FAIL reason=overflow"
    Write-Output "FAIL (overflow): $pages pages. Trim the least-relevant content per Step 4 rule 6 and regenerate."
    Write-Output "                 Never cut a surviving entry below two bullets - drop the whole entry instead."
    exit 1
}

if ($fill -lt $MinFill) {
    Write-Output "RESULT pages=$pages fill=$fill min=$MinFill verdict=FAIL reason=underfill"
    Write-Output "FAIL (underfill): content stops at $fill% of the usable page, below the $MinFill% line."
    Write-Output "                  Add real, JD-relevant material from database/*.md per Step 4 rule 6."
    Write-Output "                  Never inflate spacing, enlarge fonts, or widen margins to reach the line."
    exit 1
}

Write-Output "RESULT pages=$pages fill=$fill min=$MinFill verdict=PASS reason=ok"
Write-Output "PASS: exactly 1 page, $fill% filled (>= $MinFill%)."
exit 0
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
powershell -NoProfile -File scripts/test-verify-resume-fit.ps1
```

Expected: `5/5 cases passed`, exit 0. If Word hangs, run `Get-Process WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force` and retry.

- [ ] **Step 5: Commit**

```bash
git add scripts/verify-resume-fit.ps1 scripts/test-verify-resume-fit.ps1
git commit -m "scripts: add resume one-page + fill verifier with tests"
```

---

### Task 2: Template surgery

**Files:**
- Modify: `D:/github/job-hunting/resume-template/resume-template.docx` (`word/document.xml`)
- Test: `D:/github/job-hunting/scripts/test-resume-template-order.ps1` (create)

**Interfaces:**
- Consumes: `scripts/verify-resume-fit.ps1` from Task 1 (used to confirm the edited template still opens and still underfills).
- Produces: a template whose section headings, in document order, are exactly `EXPERIENCE, PROJECTS, TECHNICAL SKILLS, EDUCATION, AWARDS`. Tasks 4-6 document this order.

**Current paragraph layout (measured 2026-08-21, 40 paragraphs total):**

| Index | Content |
|---|---|
| 0-1 | `[Name]`, contact line |
| 2-3 | `SUMMARY` heading, `[Summary section]` body |
| 4-7 | `TECHNICAL SKILLS` heading, 3 category rows |
| 8-24 | `EXPERIENCE` heading, 4 entries x (header + 3 bullets) |
| 25-33 | `PROJECTS` heading, 2 entries x (header + 3 bullets) |
| 34-38 | `EDUCATION` heading, 2 entries x (header + degree line) |
| 39 | trailing empty paragraph, **self-closing** (`<w:p .../>`) |

Section headings are self-contained paragraphs carrying a `2B579A` blue bottom border and bold blue `w:sz 19` runs. Bullets use `numId 1` and appear only inside Experience and Projects, which move as intact blocks — list numbering is therefore untouched.

**Critical regex detail (verified 2026-08-21):** the last paragraph is *self-closing*, so the obvious pattern `<w:p[ >].*?</w:p>` finds only **39** paragraphs and silently drops it. Use this pattern, which finds all **40** and round-trips the body byte-identically:

```python
PARA = r'<w:p\b(?:[^>]*/>|.*?</w:p>)'
```

The alternation order matters: `[^>]*/>` cannot cross the first `>`, so a normal `<w:p attrs>` falls through to the `.*?</w:p>` branch.

- [ ] **Step 1: Write the failing test**

Create `D:/github/job-hunting/scripts/test-resume-template-order.ps1`:

```powershell
<#
.SYNOPSIS
  Asserts resume-template.docx has the required section order and no Summary.
.DESCRIPTION
  Run:  powershell -NoProfile -File scripts\test-resume-template-order.ps1
#>
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$tmpl = Join-Path $repo 'resume-template\resume-template.docx'
$env:PYTHONIOENCODING = 'utf-8'

$py = @"
import re, sys, zipfile
z = zipfile.ZipFile(r'''$tmpl''')
x = z.read('word/document.xml').decode('utf-8')
paras = re.findall(r'<w:p\b(?:[^>]*/>|.*?</w:p>)', x, re.S)
heads = []
for p in paras:
    if '2B579A' not in p:
        continue
    txt = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))
    txt = txt.strip()
    if txt:
        heads.append(txt)
print('|'.join(heads))
"@
$pyFile = Join-Path ([System.IO.Path]::GetTempPath()) 'check-template-order.py'
Set-Content -LiteralPath $pyFile -Value $py -Encoding utf8
$actual = (python $pyFile).Trim()
Remove-Item -LiteralPath $pyFile -ErrorAction SilentlyContinue

$expected = 'EXPERIENCE|PROJECTS|TECHNICAL SKILLS|EDUCATION|AWARDS'
if ($actual -eq $expected) {
    Write-Host "PASS  section order: $actual" -ForegroundColor Green
    exit 0
}
Write-Host "FAIL  section order" -ForegroundColor Red
Write-Host "      expected: $expected"
Write-Host "      actual:   $actual"
exit 1
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
powershell -NoProfile -File scripts/test-resume-template-order.ps1
```

Expected: FAIL, actual `SUMMARY|TECHNICAL SKILLS|EXPERIENCE|PROJECTS|EDUCATION`.

- [ ] **Step 3: Perform the surgery**

Run this Python from `D:/github/job-hunting` (it edits `word/document.xml` in place, preserving every other part of the archive):

```python
import re, shutil, zipfile

SRC = 'resume-template/resume-template.docx'
shutil.copyfile(SRC, SRC + '.bak')

zin = zipfile.ZipFile(SRC)
doc = zin.read('word/document.xml').decode('utf-8')
parts = {i.filename: zin.read(i.filename) for i in zin.infolist()}
infos = zin.infolist()
zin.close()

PARA = r'<w:p\b(?:[^>]*/>|.*?</w:p>)'   # matches self-closing paragraphs too - see note above

m = re.search(r'(<w:body>)(.*?)(<w:sectPr\b)', doc, re.S)
head, body, tail_start = doc[:m.end(1)], m.group(2), m.end(2)
paras = re.findall(PARA, body, re.S)
assert len(paras) == 40, f'expected 40 paragraphs, found {len(paras)}'
assert ''.join(paras) == body, 'paragraph split is lossy - do not proceed'

def text(p):
    return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)).strip()

assert text(paras[2]) == 'SUMMARY', text(paras[2])
assert text(paras[4]) == 'TECHNICAL SKILLS', text(paras[4])
assert text(paras[8]) == 'EXPERIENCE', text(paras[8])
assert text(paras[25]) == 'PROJECTS', text(paras[25])
assert text(paras[34]) == 'EDUCATION', text(paras[34])

heading    = paras[0:2]     # name + contact
skills     = paras[4:8]     # TECHNICAL SKILLS + 3 category rows
experience = paras[8:25]    # EXPERIENCE + 4 entries
projects   = paras[25:34]   # PROJECTS + 2 entries
education  = paras[34:39]   # EDUCATION + 2 entries
trailing   = paras[39:40]   # the self-closing empty paragraph - keep it last

# AWARDS heading: clone the EDUCATION heading, swap its runs for a single AWARDS run.
edu_head = paras[34]
pPr = re.search(r'<w:pPr>.*?</w:pPr>', edu_head, re.S).group(0)
awards_head = (
    '<w:p>' + pPr +
    '<w:r><w:rPr><w:b/><w:color w:val="2B579A"/><w:sz w:val="19"/></w:rPr>'
    '<w:t>AWARDS</w:t></w:r></w:p>'
)

# Award lines: clone the education-entry paragraph shape (right tab stop at 10973)
# so the award name sits left and its date sits right.
entry_pPr = re.search(r'<w:pPr>.*?</w:pPr>', paras[35], re.S).group(0)
def award_line(name, date):
    return (
        '<w:p>' + entry_pPr +
        '<w:r><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="19"/></w:rPr>'
        f'<w:t xml:space="preserve">{name}</w:t></w:r>'
        '<w:r><w:rPr><w:color w:val="000000"/><w:sz w:val="19"/></w:rPr>'
        f'<w:tab/><w:t xml:space="preserve">{date}</w:t></w:r></w:p>'
    )

awards = [awards_head, award_line('[Award 1]', '[Date]'), award_line('[Award 2]', '[Date]')]

new_body = ''.join(heading + experience + projects + skills + education + awards + trailing)
new_doc = head + new_body + doc[tail_start:]

with zipfile.ZipFile(SRC, 'w', zipfile.ZIP_DEFLATED) as zout:
    for it in infos:
        data = new_doc.encode('utf-8') if it.filename == 'word/document.xml' else parts[it.filename]
        zout.writestr(it, data)

print('template rewritten')
```

Save it as a scratchpad file and run it with `PYTHONIOENCODING=utf-8 python <file>`. The `.bak` copy is the rollback if Word rejects the result.

- [ ] **Step 4: Run the test to verify it passes**

```bash
powershell -NoProfile -File scripts/test-resume-template-order.ps1
```

Expected: `PASS  section order: EXPERIENCE|PROJECTS|TECHNICAL SKILLS|EDUCATION|AWARDS`.

- [ ] **Step 5: Confirm Word still opens it cleanly**

```bash
powershell -NoProfile -File scripts/verify-resume-fit.ps1 -Path resume-template/resume-template.docx
```

Expected: `FAIL (underfill)` with a fill percentage in the 70s and `pages=1`. Underfill is the correct result for a placeholder template — the point of this step is that Word opens the edited file without a repair prompt and reports exactly 1 page. If Word raises a repair dialog, restore `resume-template.docx.bak` and re-check the XML.

- [ ] **Step 6: Delete the backup and commit**

```bash
rm resume-template/resume-template.docx.bak
git add resume-template/resume-template.docx scripts/test-resume-template-order.ps1
git commit -m "resume-template: drop Summary, reorder to Experience/Projects/Skills/Education, add Awards"
```

---

### Task 3: Canonical Awards block in the database

**Files:**
- Modify: `D:/github/job-hunting/database/master-education.md`

**Interfaces:**
- Consumes: nothing.
- Produces: a `## Awards & Honors` section in `master-education.md` holding exactly two items. Tasks 4-5 point the Awards rules at this block.

**Why `master-education.md` and not a new file:** SKILL.md asserts "the four `database/*.md` files are the master" in many places. A fifth master file would mean churn across all of them. Honors and academic placements are education-adjacent.

**The two facts on record**, verbatim sources:
- `database/master-education.md:9` — `Graduated with Distinction`, B.Tech IT, Uka Tarsadia University, ends Feb 2024.
- `database/master-project.md:103` — `placed 2nd of 15+ teams at Northeastern's Agentic AI 2.0 Hackathon`, Kahoot Bot project, Aug 2025.

Both stay where they are in the database. The database keeps the full record; de-duplication is a **rendering rule** applied when building a resume (Task 5), not a deletion here.

- [ ] **Step 1: Append the Awards block**

Add to the end of `D:/github/job-hunting/database/master-education.md`:

```markdown

---

## Awards & Honors

> Canonical award list — the source for the resume's Awards section. The resume includes that section only when two or more genuine items exist here, and never repeats an item that already appears in Education or in a project bullet on the same page.

- **Graduated with Distinction** — Bachelor of Technology, Information Technology, Uka Tarsadia University | Feb 2024
- **2nd Place (of 15+ teams), Agentic AI 2.0 Hackathon** — Northeastern University | Aug 2025

> Thin section: only two items on record. Certifications, scholarships, GPA honours, or other placements would strengthen it. Never invent an award to fill space.
```

- [ ] **Step 2: Verify the block parses as expected**

```bash
grep -c "^- \*\*" database/master-education.md
```

Expected: `2`.

```bash
grep -n "Awards & Honors" database/master-education.md
```

Expected: one match.

- [ ] **Step 3: Commit**

```bash
git add database/master-education.md
git commit -m "database: add canonical Awards & Honors block"
```

---

### Task 4: Rewrite the resume content template

**Files:**
- Modify: `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/tailored-resume.template.md`

**Interfaces:**
- Consumes: the section order established in Task 2; the Awards source from Task 3.
- Produces: the markdown scaffold Step 4 of the skill fills. Task 5 references its section names.

**Not a repo file** — it lives under `C:/Users/Dhruv/.claude/skills/`, so it is not part of any `git add` in this plan.

- [ ] **Step 1: Replace the file's entire contents**

Write `C:/Users/Dhruv/.claude/skills/applying-to-job/templates/tailored-resume.template.md`:

```markdown
# {{FULL NAME}}

{{phone}} | {{email}} | {{linkedin URL}} | {{github URL}} | {{portfolio URL}} | {{city, state}}

---

## Experience

{{Reverse-chronological — newest entry first. Every entry carries a date range and AT LEAST TWO bullets. An entry that can only justify one real bullet is merged into a stronger one or dropped.}}

**{{Company Name}}** | {{City, State}}
*{{Job Title}}* | {{Start Month YYYY}} – {{End Month YYYY (or Present)}}

- {{Action verb + what you did + quantified result + how/method — Google XYZ formula}}
- {{Action verb + what you did + quantified result + how/method}}
- {{Third bullet when the entry earns it}}

**{{Company Name}}** | {{City, State}}
*{{Job Title}}* | {{Start Month YYYY}} – {{End Month YYYY}}

- {{Bullet}}
- {{Bullet}}

---

## Projects

{{Reverse-chronological — newest first. Same two-bullet minimum as Experience. Projects never lead the document; Experience always precedes this section.}}

**{{Project Name}}** | {{Start Month YYYY}} – {{End Month YYYY (or Present)}}

- {{What you built + impact metric + technical approach}}
- {{Second bullet — required, not optional}}

**{{Project Name}}** | {{Start Month YYYY}} – {{End Month YYYY}}

- {{Bullet}}
- {{Bullet}}

---

## Technical Skills

{{Adapt category labels to the role track — SWE: Languages / Frameworks / Developer Tools / Libraries · ML/AI: Languages / ML Frameworks / MLOps & Data Tools / Libraries · analyst: Languages / BI & Visualization / Data Tools / Platforms. 3-4 rows max, only real skills, JD-relevant first.}}

**{{Category 1}}:** {{e.g., Python, SQL, TypeScript}}
**{{Category 2}}:** {{e.g., React, Node.js — or Power BI, DAX for analyst track}}
**{{Category 3}}:** {{e.g., Git, Docker, AWS — or DuckDB, pandas}}
**{{Category 4}}:** {{e.g., pandas, scikit-learn, TensorFlow}}

---

## Education

**{{University Name}}** | {{City, State}}
*{{Degree, Major}}* | {{Start Month YYYY}} – {{End Month YYYY}}

**{{University Name (if second degree)}}** | {{City, State}}
*{{Degree, Major}}* | {{Start Month YYYY}} – {{End Month YYYY}}

---

## Awards

{{CONDITIONAL — include this section only when the `## Awards & Honors` block in `database/master-education.md` yields TWO OR MORE genuine items. Below two, delete this whole section rather than shipping a one-line stub. Never invent an award. A fact listed here is NOT repeated elsewhere on the page: when Awards carries "Graduated with Distinction," the Education entry drops it; when Awards carries the hackathon placement, the project bullet drops that clause.}}

**{{Award name}}** | {{Month YYYY}}
**{{Award name}}** | {{Month YYYY}}
```

- [ ] **Step 2: Verify the section order and the absence of a Summary**

```bash
grep -n "^## " "C:/Users/Dhruv/.claude/skills/applying-to-job/templates/tailored-resume.template.md"
```

Expected, in this order: `## Experience`, `## Projects`, `## Technical Skills`, `## Education`, `## Awards`. No `## Summary`.

- [ ] **Step 3: No commit**

This file is outside the repo. Nothing to commit — state that explicitly in the task report rather than running `git add` on a path outside the working tree.

---

### Task 5: SKILL.md — order, Summary removal, Awards, two-bullet minimum

**Files:**
- Modify: `C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md`

**Interfaces:**
- Consumes: section order from Task 2, Awards source from Task 3, template scaffold from Task 4.
- Produces: Step 4 rules 1 and 7-9, a revised Step 6 layout note, and a revised Step 10 item 1. Task 6 edits **different** lines of the same file (fill rules and Step 10 item 4) and must not touch these.

**Rule-numbering discipline:** the existing Summary rule is number 7, and the existing one-page rule is number 6. Delete rule 7 and **append** new rules as 7, 8, 9. Do NOT renumber rules 1-6 — `Step 4 rule 6` is referenced from Step 10 and must keep pointing at the page-fit rule.

- [ ] **Step 1: Replace Step 4 rule 1 (line 109)**

Find the line beginning `1. The output format is the user's Word template` and replace it with:

```markdown
1. The output format is the user's Word template `D:/github/job-hunting/resume-template/resume-template.docx` (NOT Jake's Resume, NOT LaTeX). `tailored-resume.md` holds the approved content; it gets mapped into the template's sections, in the template's order (**Experience, Projects, Technical Skills, Education, Awards**), at Step 10. Produce every section the template expects. **There is no Summary section — never write one.**
```

- [ ] **Step 2: Delete the Summary rule (lines 115-118) and append rules 7-9**

Delete the entire rule 7 block — it starts `7. **Summary section (top of resume) — keep it concrete, or keep it short.**` and ends with the line `Keep it to ~2-3 lines, scrub LLM tells, and place it at the top of `tailored-resume.md` under a `## Summary` heading.` (four lines including the indented blockquote shape).

In its place, append these three rules after rule 6:

```markdown
7. **Reverse-chronological format.** Experience always precedes Projects. Within Experience and within Projects, entries run **newest first**, and every entry carries a date range. Projects never lead the document, even when they are the stronger material — that strength shows through bullet quality and ordering, not by displacing Experience. Full section order: **Experience, Projects, Technical Skills, Education, Awards.**
8. **At least two bullets per entry.** Every Experience entry and every Project entry carries **two or more** bullet points. An entry that can only justify one real bullet is merged into a stronger entry or dropped — never shipped as a one-line stub. (Education entries and Awards lines carry no bullets and are exempt.)
9. **Awards — conditional, de-duplicated, never invented.** Source award lines from the `## Awards & Honors` block in `database/master-education.md`. Include the section only when **two or more** genuine items are available; below that, omit it entirely rather than ship a one-line stub. **A fact rendered in Awards is not repeated elsewhere on the same resume:** when Awards carries "Graduated with Distinction," the B.Tech education entry drops it; when Awards carries the hackathon placement, the Kahoot Bot project bullet drops that clause (it keeps its 90%-accuracy and 60%-cost-reduction evidence, which is the stronger signal anyway). If the awards material is thin, flag it in your summary the way `keyword-gaps.md` flags a gap — the user supplies real awards; you never invent one.
```

- [ ] **Step 3: Add the Step 6 layout note**

In Step 6, find the line `In all cases: skeptical, time-pressured, unforgiving of fluff.` and add this paragraph immediately after it:

```markdown
**Layout note:** the resume is reverse-chronological with Technical Skills below Projects, so the top third is Experience (and possibly the first project) — not a skills block. Judge whether the stack and the impact surface through those bullets. **Do not flag the absence of a skills list up top as a defect, and do not recommend moving Technical Skills back to the top** — that ordering is deliberate.
```

- [ ] **Step 4: Replace Step 10 item 1 (line 224)**

Find the line beginning `1. **Resume → `application/Dhruvkumar_Resume.docx`.**` and replace the whole item with:

```markdown
1. **Resume → `application/Dhruvkumar_Resume.docx`.** Start from the provided template `D:/github/job-hunting/resume-template/resume-template.docx`. Fill the heading from `database/master-personal-info.md` and the body from the approved `tailored-resume.md` ONLY, mapping content into the template's sections in the template's order (**Experience, Projects, Technical Skills, Education, Awards**). **The template has no Summary section — never add one.** Every Experience and Project entry keeps **at least two bullets** (Step 4 rule 8). Omit the Awards section entirely when fewer than two genuine items exist (Step 4 rule 9). Preserve the template's fonts, sizes, blue section-heading rule, bullet numbering, and right-aligned dates. Make LinkedIn / GitHub / Portfolio / email real hyperlinks. Escape XML specials in all prose: `&`→`&amp;`, `<`→`&lt;`, `>`→`&gt;`. If the resume template is missing, PAUSE and ask the user for it — same rule as the cover-letter template: never fall back to LaTeX or invent a format.
```

- [ ] **Step 5: Update Key Rule 8 and add Key Rule 18**

Replace Key Rule 8 (it currently ends `— including no "passion for / passionate about" in the Summary.`) with:

```markdown
8. **No LLM tells** anywhere (resume, cover letter, and phone-screen narrative) — no "passion for / passionate about", no "leveraged / robust / seamless".
```

Append after Key Rule 17:

```markdown
18. **Reverse-chronological, in this exact order: Experience, Projects, Technical Skills, Education, Awards.** No Summary section, ever. Every Experience and Project entry carries at least two bullets. Awards appears only with two or more genuine items from `master-education.md`, and nothing in Awards is repeated elsewhere on the page.
```

- [ ] **Step 6: Rewrite the Summary row and add four Common Mistakes rows**

Replace the row that currently reads `| Summary opens with "a professional with a passion for…" / "passionate about" | ... |` with:

```markdown
| Writing a Summary or profile blurb at the top | There is no Summary section — the order is Experience, Projects, Technical Skills, Education, Awards. Lead with Experience |
| Putting Projects or Technical Skills above Experience | The format is reverse-chronological: Experience first, then Projects, then Technical Skills, Education, Awards |
| Shipping an Experience or Project entry with a single bullet | Every entry carries at least two bullets — merge it into a stronger entry, or drop the entry |
| Repeating an award in both Awards and Education / a project bullet | One canonical home per fact: when Awards carries it, the other section drops it |
| Inventing an award or certification to fill the Awards section | Awards come only from the `## Awards & Honors` block in `master-education.md`; below two genuine items, omit the section and flag the gap |
```

- [ ] **Step 7: Verify**

```bash
grep -n -i "summary" "C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md"
```

Expected: only two survivors, both unrelated to a resume Summary section — the Step 5 line about a "coverage summary per dimension", and Step 2's "Summarize what was loaded". No instruction to write a resume Summary.

```bash
grep -c "Experience, Projects, Technical Skills, Education, Awards" "C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md"
```

Expected: `4` or more (Step 4 rule 1, Step 4 rule 7, Step 10 item 1, Key Rule 18, plus Common Mistakes rows).

```bash
grep -n "Projects, Experience" "C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md"
```

Expected: no output — the old wrong order is gone.

- [ ] **Step 8: No commit**

`SKILL.md` is outside the repo. Report the change; do not `git add` it.

---

### Task 6: SKILL.md — full-page fill reversal and verifier wiring

**Files:**
- Modify: `C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md`

**Interfaces:**
- Consumes: `scripts/verify-resume-fit.ps1` and its exact CLI from Task 1; Step 4 rule 8 (two-bullet floor) from Task 5.
- Produces: nothing later tasks depend on. Task 7 verifies it.

**Do not touch** the lines Task 5 edited. This task changes only the fill language: the Overview length rule, Step 4 rule 6, the Step 5 parse-compliance clause, Step 10 item 4, Key Rule 9, and two Common Mistakes rows.

- [ ] **Step 1: Replace the Overview length rule (line 14)**

Replace the paragraph beginning `**Length rule — ceiling, not a fill target:**` with:

```markdown
**Length rule — exactly one full page:** the tailored resume **fills one page** and never spills onto a second. A page that stops three-quarters of the way down reads as thin, so fill it — but fill it with **real, JD-relevant material drawn from the `database/*.md` files** (another true bullet, another relevant entry), never with invented claims, stretched line spacing, enlarged fonts, or widened margins. Step 10 enforces both edges with `scripts/verify-resume-fit.ps1`: at least **92%** of the usable page filled, and never a second page. The cover letter is at most one page, with no fill requirement.
```

- [ ] **Step 2: Replace Step 4 rule 6 (line 114)**

Replace the rule beginning `6. **One page maximum — never pad to fill it.**` with:

```markdown
6. **Exactly one full page — fill it with real content.** The resume must fill one page and must never spill onto a second. Step 10 fails the build at **both** edges: content stopping short of **92% of the usable page height**, or crossing onto page 2.
   - **Under-filled?** Add real, JD-relevant material from the `database/*.md` files — another true bullet on the strongest entry, or another relevant Experience/Project entry. **Never invent a claim, never inflate line spacing, never enlarge fonts or widen margins to reach the line.**
   - **Overflowing?** Cut the least-relevant content first (older/less-relevant bullets, then whole low-value entries). **Never drop a surviving entry below the two-bullet minimum (rule 8) — cut the whole entry instead.**
   - If the strongest honest material genuinely cannot reach 92%, say so in your summary and let the user decide. **Do not pad silently.**

   State in your summary what you added or cut to land on one full page.
```

- [ ] **Step 3: Update the Step 5 parse-compliance clause (line 132)**

In Step 5's Action paragraph, replace `format/parse compliance (which includes ≤ one page)` with:

```markdown
format/parse compliance (which includes exactly one full page)
```

- [ ] **Step 4: Replace Step 10 item 4 (line 227)**

Replace the item beginning `4. **Verify it fits on one page (page-count check only).**` with:

````markdown
4. **Verify the resume is exactly one full page.** Run the fit check:

   ```
   powershell -NoProfile -File "D:/github/job-hunting/scripts/verify-resume-fit.ps1" -Path "D:/github/job-hunting-worktrees/<slug>/application/Dhruvkumar_Resume.docx"
   ```

   It passes only when the document is exactly 1 page **and** at least 92% of the usable page height is filled.
   - `FAIL (overflow)` — trim per Step 4 rule 6 and regenerate.
   - `FAIL (underfill)` — add real content per Step 4 rule 6 and regenerate. **Whitespace at the bottom of the page is a defect now, not an acceptable outcome.**

   For `Dhruvkumar_Cover_Letter.docx`, check the page count only (`≤ 1`, no fill requirement) with `$doc.ComputeStatistics(2)` via Word COM. Word COM is the reliable renderer here (no LibreOffice); if a Word call hangs, kill stray `WINWORD` processes and retry.
````

- [ ] **Step 5: Replace Key Rule 9**

Replace Key Rule 9 (it begins `9. **One page maximum, never padded to fill**`) with:

```markdown
9. **One full page, never two** — the resume fills at least 92% of the usable page and never crosses onto a second. Fill only with real, JD-relevant material; never with invented claims or stretched spacing. Prove it by running `scripts/verify-resume-fit.ps1` (Step 10), not by eyeballing. The cover letter stays ≤ one page with no fill requirement.
```

- [ ] **Step 6: Invert the two Common Mistakes fill rows**

Replace the row `| Padding the resume with weak or old bullets to fill the page | Fill is not a goal — keep only your strongest, most relevant material; a three-quarter page beats a padded full one |` with:

```markdown
| Leaving the resume three-quarters full, with whitespace at the bottom | An under-filled page reads as thin. Add real, JD-relevant material until `verify-resume-fit.ps1` reports ≥92% fill — never invented claims, never stretched spacing |
| Filling the page by inflating line spacing, font size, or margins | That is padding, not content. Fill only with real material from `database/*.md`; if the honest material cannot reach 92%, tell the user instead of stretching the layout |
```

Replace the row `| Resume spills to two pages | Trim least-relevant content (older bullets, then whole low-value entries) to fit one page |` with:

```markdown
| Resume spills to two pages | Trim least-relevant content (older bullets, then whole low-value entries) to fit one page; never cut a surviving entry below two bullets — drop the whole entry instead |
```

- [ ] **Step 7: Verify no anti-fill language survives**

```bash
grep -n -i "no fill target\|three-quarter\|never pad\|no minimum fill\|no vertical-fill\|page-count check only\|Fill is not a goal" "C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md"
```

Expected: no output. Every one of these phrases belonged to the old rule.

```bash
grep -c "92%" "C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md"
```

Expected: `5` or more.

```bash
grep -n "verify-resume-fit.ps1" "C:/Users/Dhruv/.claude/skills/applying-to-job/SKILL.md"
```

Expected: at least three matches (Overview, Step 10 item 4, Key Rule 9).

- [ ] **Step 8: No commit**

`SKILL.md` is outside the repo. Report the change; do not `git add` it.

---

### Task 7: End-to-end consistency sweep

**Files:**
- Test only. No files modified.

**Interfaces:**
- Consumes: everything from Tasks 1-6.
- Produces: the pass/fail evidence for the spec's Verification section.

- [ ] **Step 1: Run both test suites**

```bash
powershell -NoProfile -File scripts/test-verify-resume-fit.ps1
```

Expected: `5/5 cases passed`, exit 0.

```bash
powershell -NoProfile -File scripts/test-resume-template-order.ps1
```

Expected: `PASS  section order: EXPERIENCE|PROJECTS|TECHNICAL SKILLS|EDUCATION|AWARDS`, exit 0.

- [ ] **Step 2: Confirm no resume-Summary instruction survives anywhere in the skill**

```bash
grep -rn -i "summary" "C:/Users/Dhruv/.claude/skills/applying-to-job/"
```

Expected survivors only: `keyword-coverage.template.md` (`## Coverage Summary`), `jd-analysis.template.md` (`tone for summary`), `company-research.template.md` (`summary is not itself a public page`), `llm-tells.md` (`"Results-driven professional" in summary`), and SKILL.md's coverage-summary / "Summarize what was loaded" lines. **No `## Summary` in `tailored-resume.template.md`, and no instruction to write one in SKILL.md.**

- [ ] **Step 3: Confirm every stated section order matches**

```bash
grep -rn "Technical Skills, Projects\|Projects, Experience\|Summary, Technical Skills" "C:/Users/Dhruv/.claude/skills/applying-to-job/"
```

Expected: no output. Those are the three shapes of the old, wrong order.

- [ ] **Step 4: Confirm the two-bullet rule is stated in all three places**

```bash
grep -rn -i "two bullets\|two or more.*bullet\|TWO BULLETS" "C:/Users/Dhruv/.claude/skills/applying-to-job/"
```

Expected: matches in `SKILL.md` (Step 4 rule 8, Step 10 item 1, Key Rule 18, Common Mistakes) and in `templates/tailored-resume.template.md`.

- [ ] **Step 5: Confirm the repo tree is clean and the history reads correctly**

```bash
git status --short
```

Expected: clean except the pre-existing untracked `outreach/` directory.

```bash
git log --oneline -5
```

Expected: the three commits from Tasks 1-3 plus the two spec commits.

- [ ] **Step 6: Report**

Summarise for the user: what changed in the repo (3 commits), what changed outside the repo (`SKILL.md` + `tailored-resume.template.md`, uncommitted by design), the measured verifier results, and the standing note that Awards holds only two items until they supply more.
