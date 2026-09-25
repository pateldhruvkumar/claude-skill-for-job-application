# {{FULL NAME}}

{{phone}} | {{email}} | {{linkedin URL}} | {{github URL}} | {{portfolio URL}} | {{city, state}}

---

## Experience

{{Reverse-chronological — newest entry first. Every entry carries a date range and TWO TO FOUR bullets (two is the hard floor; a fifth only when the page needs the height). An entry that can only justify one real bullet is merged into a stronger one or dropped. Bullet formula, from the template itself: action verb + task or project + metric or result.}}

{{HEADING ORDER IS COMPANY FIRST, ON TWO LINES — the shape `resume-template.docx` has used since 2026-09-19. Line 1: the company in ALL CAPS, then the location. Line 2: the job title, then the dates. There is NO `Title | Company` pipe — company and title never share a line. The heading shape written here is what gets rendered into the Word template at Step 10, and `verify-resume-pattern.py` fails the build on a title-first heading or a mixed-case company.}}

**{{COMPANY NAME}}** | {{City, Prov}}
{{Job Title}} | {{Start Month YYYY}} – {{End Month YYYY (or Present)}}

- {{Action verb + what you did + quantified result + how/method — Google XYZ formula}}
- {{Action verb + what you did + quantified result + how/method}}
- {{Third and fourth bullets when the entry earns them}}

**{{COMPANY NAME}}** | {{City, Prov}}
{{Job Title}} | {{Start Month YYYY}} – {{End Month YYYY}}

- {{Bullet}}
- {{Bullet}}

---

## Projects

{{Reverse-chronological — newest first. Same two-to-four bullet range as Experience. Projects never lead the document; Experience always precedes this section.}}

{{The project heading carries its TECH STACK after the pipe — `resume-template.docx` reads "[Project Heading] | [Technologies used]". Keep the stack short (3-5 JD-relevant tools) and true to what the project used; it is prime keyword real estate. Projects carry no location line.}}

**{{Project Name}} | {{Technologies used}}** — {{Start Month YYYY}} – {{End Month YYYY (or Present)}}

- {{What you built + impact metric + technical approach}}
- {{Second bullet — required, not optional}}

**{{Project Name}} | {{Technologies used}}** — {{Start Month YYYY}} – {{End Month YYYY}}

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
