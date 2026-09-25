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
    # Each cleanup step is independently guarded: a failure in one (e.g. Close()
    # throwing) must never prevent the next (e.g. Quit()) from running, or a
    # WINWORD.exe process leaks.
    if ($null -ne $doc)  { try { $doc.Close($false)  | Out-Null } catch { } }
    if ($null -ne $word) { try { $word.Quit()        | Out-Null } catch { } }
    if ($null -ne $doc)  { try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc)  | Out-Null } catch { } }
    if ($null -ne $word) { try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null } catch { } }
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
