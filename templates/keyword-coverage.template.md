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
| Format / parse compliance | {{Pass / issues found}} | {{"Single column, standard headings, exactly one full page (≥92% fill, 1 page), native .docx text"}} |

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
