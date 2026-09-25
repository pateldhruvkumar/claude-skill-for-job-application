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
    param([string]$Target, [double]$MinFill = 92, [switch]$OmitMinFill)
    # No 2>&1 — in PowerShell 5.1 redirecting a native command's stderr wraps each
    # line in a NativeCommandError ErrorRecord and corrupts $?. The verifier writes
    # everything to stdout anyway.
    if ($OmitMinFill) {
        # Deliberately omit -MinFill so the verifier's own default (must be 92) is exercised.
        $out = & powershell -NoProfile -File $verifier -Path $Target
    } else {
        $out = & powershell -NoProfile -File $verifier -Path $Target -MinFill $MinFill
    }
    $code = $LASTEXITCODE
    $line = ($out | Where-Object { $_ -match '^RESULT ' } | Select-Object -First 1)
    return [pscustomobject]@{ Exit = $code; Result = [string]$line; Raw = ($out -join "`n") }
}

function Assert-Case {
    param([string]$Name, [string]$Target, [string]$ExpectReason, [int]$ExpectExit, [switch]$OmitMinFill)
    $script:ran++
    $r = Invoke-Verifier -Target $Target -OmitMinFill:$OmitMinFill
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

    Assert-Case -Name 'default MinFill is 92 when -MinFill is omitted (bare template must still underfill)' `
        -Target (Join-Path $repo 'resume-template\resume-template.docx') `
        -ExpectReason 'underfill' -ExpectExit 1 -OmitMinFill
}
finally {
    Remove-Item -LiteralPath $overflow -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $pyFile   -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "$($ran - $failures)/$ran cases passed"
if ($failures -gt 0) { exit 1 }
exit 0
