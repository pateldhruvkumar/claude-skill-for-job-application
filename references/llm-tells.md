# LLM Tells to Scrub

> Phrases and punctuation that signal "this was written by ChatGPT/Claude."
> Recruiters and AI-detection tools flag these. This skill scrubs them wherever it writes prose — the resume (Step 4), the cover letter (Step 7), and the phone-screen narrative (Step 8).

## Punctuation

| Tell | Replace with |
|---|---|
| `—` (em dash, U+2014) | `-` (hyphen), `,` (comma), `:` (colon), or `(...)` |
| `–` (en dash, U+2013) — mid-sentence | `-` or `,` |
| `–` in date ranges (e.g., `2021–2024`) | OK — leave as-is |
| `""` `''` (curly quotes) | `""` `''` (straight) |
| ` ` (non-breaking space, U+00A0) | regular space |
| `…` (single-char ellipsis) | `...` (three dots) |
| Zero-width characters (U+200B, U+200C, U+FEFF) | Delete |

## Phrases to Scrub Completely

These add nothing and signal AI authorship:

- "Leveraged" → use "used"
- "Utilized" → use "used"
- "Robust" → cut or replace with specific quality
- "Seamless" → cut or specify what was seamless
- "Cutting-edge" → cut
- "State-of-the-art" → cut unless literally measurable
- "Synergies" → cut
- "Spearheaded" → "led" (in most contexts)
- "Orchestrated" → "led" or "coordinated" (vary)
- "Pioneered" → "built first" or "established"
- "Revolutionized" → almost never warranted; cut
- "Best-in-class" → cut
- "World-class" → cut
- "Successfully" (as an adverb) → cut (if it shipped, it was successful)
- "Actively" (as in "actively contributed") → cut

## Sentence Patterns to Rewrite

| Pattern | Why bad | Fix |
|---|---|---|
| "Not only X, but also Y" | Overused, formal-sounding | "X. Y." or "X, and Y" |
| "In today's fast-paced world..." | Filler intro | Delete entire phrase |
| "It's worth noting that..." | Padding | Delete |
| "At the end of the day..." | Cliché | Delete |
| "Significant improvement" without numbers | Vague impact claim | Quantify or cut |
| Three-item parallel lists in every bullet | LLM rhythm pattern | Vary structure across bullets |

## Resume-Specific Tells

- **"Designed, developed, and deployed"** — three-verb parallel construction. LLM default. Pick one strong verb.
- **"Demonstrated strong communication skills"** — vague claim. Show, don't tell. Cut or replace with a concrete cross-functional bullet.
- **"Results-driven professional"** in summary — pure AI filler. Rewrite as concrete current role + specialty.
- **"Passionate about X"** — performative. Cut unless backed by evidence (open source, talks, etc.).

## Detection Workflow

Whenever you write prose (Step 4 resume, Step 7 cover letter, Step 8 phone-screen narrative), scan it for:

1. All entries in the Punctuation table above — auto-replace where unambiguous
2. All entries in the "Phrases to Scrub" list — flag each occurrence, prompt user to confirm replacement
3. Three-item parallel constructions in consecutive bullets — flag for variation
4. Bullets without numbers AND without specific qualifiers (e.g., "across 4 teams") — flag for quantification

## Meta-Rule

> If a sentence sounds smooth, polished, and could appear on 1000 other résumés — rewrite it with specificity only you could provide.
