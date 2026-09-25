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
