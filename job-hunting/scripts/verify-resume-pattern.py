#!/usr/bin/env python
"""Verify a generated resume .docx follows resume-template.docx's entry patterns.

Used by the applying-to-job skill at Step 10, alongside verify-resume-fit.ps1.
verify-resume-fit checks that the page is full; this checks that the shapes on
it are the template's shapes.

Template revision 2026-09-19 (morning): resume-template.docx was replaced
with a two-line entry layout. An Experience heading is now ONE paragraph
holding TWO lines:

    line 1:  <COMPANY NAME>   -> right tab ->  <City, Country>
    line 2:  <Job Title>      -> right tab ->  <Month Year - Month Year>

So the company leads line 1 and the job title leads line 2; they are separate
zones and the heading carries NO "Title | Company" pipe. (The previous
template used a single-line "Job Title | Company" heading with the location on
a second line; that shape is now wrong and is reported as such.)

Template revision 2026-09-19 (afternoon) added, on top of that:
  * the company name renders in ALL CAPS ("ASSOCIATED GROCERS"), still bold
    at sz=20 so it matches the location beside it;
  * the header contact line leads with the location -
    "Surrey, BC | phone | email | LinkedIn | GitHub | Portfolio" - where the
    location used to trail it;
  * around 2 to 4 bullets per entry (two remains the hard floor; more than
    four is reported as a warning, not a failure, because the 92%-fill rule
    occasionally needs a fifth);
  * three Technical Skills category lines, down from four.

Other shapes in the current template:
    Project    <Name> | <Technologies used>[ | GitHub] -> right tab -> <date>
               one line only, no location
    Education  <School> -> right tab -> <City, Country>
               <Degree, italic> -> right tab -> <dates>
    Achievement<Award name, bold> -> right tab -> <date>
    Bullet     pStyle=ListParagraph + numId=1

Known deviations when you run this against resume-template.docx itself
(the template is a hand-edited Word file, not a generated one - these are
expected and must NOT be "fixed" by changing the generated output):
  * company-run-style - the template's retyped "COMPANY NAME" run carries
    sz=19, picked up from the square brackets it replaced. The user chose
    ALL CAPS at sz=20 (2026-09-19) so the company matches the location beside
    it, so SZ_COMPANY stays 20 and the template trips its own check.
  * education/degree-style and education/degree-dates - the template pushes
    the degree dates across with a row of literal tab runs and leaves the
    degree text non-italic. Generated resumes use the right tab stop at
    pos=10973 with an italic degree, which is the shape enforced here.

Emits one line per check plus a machine-readable summary:
    RESULT checks=<int> failed=<int> warned=<int> verdict=<PASS|FAIL>

Exit codes: 0 = PASS, 1 = one or more FAIL, 2 = file not found.

Usage:
  python scripts/verify-resume-pattern.py <resume.docx>
         [--template resume-template/resume-template.docx]
         [--db database]
"""
import argparse
import os
import re
import sys
import zipfile

HEADING_COLOR = "2B579A"          # blue section-heading rule in the template
RIGHT_TAB = 'w:val="right" w:pos="10973"'
EXPECTED_ORDER = ["PROFESSIONAL EXPERIENCE", "PROJECTS", "TECHNICAL SKILLS",
                  "EDUCATION", "ACHIEVEMENTS"]

# Run sizes the template uses, in half-points. A run with no explicit <w:sz>
# inherits Normal (18 = 9pt); INHERIT stands for that case.
INHERIT = None
SZ_COMPANY = 20      # bold
SZ_CITY = 20         # bold
SZ_JOBTITLE = INHERIT
SZ_ENTRY_DATE = INHERIT
SZ_PROJECT = 20
SZ_EDU_SCHOOL = 20
SZ_AWARD = 20

MAX_BULLETS = 4          # "around 2 to 4 bullet points per role" (warn above)
MAX_SKILL_CATEGORIES = 3 # the template ships three Technical Skills lines

# Employers that appear on older resumes but are no longer in master-experience.md
# (the current role was renamed to Associated Grocers / Inventory Analyst). Without
# these, a heading naming a retired employer passes silently.
LEGACY_COMPANIES = [
    "Jim Pattison Food Group",
    "Save-On-Foods",
    "Save-On Foods",
]

failures, warnings, checks = [], [], []


def record(ok, name, detail="", warn_only=False):
    checks.append(name)
    if ok:
        print("  ok    " + name)
    elif warn_only:
        warnings.append((name, detail))
        print("  WARN  {0}: {1}".format(name, detail))
    else:
        failures.append((name, detail))
        print("  FAIL  {0}: {1}".format(name, detail))


def read_xml(path, member="word/document.xml"):
    with zipfile.ZipFile(path) as z:
        return z.read(member).decode("utf-8")


def paragraphs(xml):
    body = xml[xml.index("<w:body>"):]
    return re.findall(r"<w:p\b(?:[^>]*/>|(?:(?!</w:p>).)*?</w:p>)", body, re.S)


def unescape(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&apos;", "'"))


def text_of(p):
    return unescape("".join(re.findall(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", p, re.S)))


def runs(p):
    """[(rPr_xml, text, has_tab, has_line_break), ...] in document order.

    Runs nested inside <w:hyperlink> are included, so a linked "GitHub" in a
    project heading counts as part of the heading text.
    """
    out = []
    for r in re.findall(r"<w:r\b(?:(?!</w:r>).)*?</w:r>", p, re.S):
        m = re.search(r"<w:rPr>(.*?)</w:rPr>", r, re.S)
        text = unescape("".join(re.findall(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", r, re.S)))
        out.append((m.group(1) if m else "", text, "<w:tab/>" in r, "<w:br/>" in r))
    return out


def lines_and_zones(p):
    """Split a heading paragraph into lines, and each line into tab-separated zones.

    Returns [[zone, zone, ...], ...] where a zone is a list of (rPr, text) runs.
    A heading is routinely split across several runs (Word does this on its own
    while editing), so every zone is a list, never a single run.
    """
    lines, line, zone = [], [], []
    for rpr, text, has_tab, has_br in runs(p):
        if has_tab:                       # text in a tab run follows the tab
            line.append(zone)
            zone = []
        zone.append((rpr, text))
        if has_br:
            line.append(zone)
            lines.append(line)
            line, zone = [], []
    line.append(zone)
    lines.append(line)
    return lines


def zone(lines, li, zi):
    try:
        return lines[li][zi]
    except IndexError:
        return []


def joined(seg):
    return "".join(t for _, t in seg).strip()


def first_texty(seg):
    return next(((rpr, t) for rpr, t in seg if t.strip()), ("", ""))


def sz_of(rpr):
    m = re.search(r'<w:sz w:val="(\d+)"', rpr)
    return int(m.group(1)) if m else None


def is_bold(rpr):
    return re.search(r"<w:b/>|<w:b ", rpr) is not None


def is_italic(rpr):
    return re.search(r"<w:i/>|<w:i ", rpr) is not None


def is_bullet(p):
    return 'w:val="ListParagraph"' in p or "<w:numPr>" in p


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def companies_and_titles(db_dir):
    """Company + job-title strings from database/master-experience.md headings.

    Headings look like:  ## <Title> <dash> <Company>, <Location> | <dates>
    """
    path = os.path.join(db_dir, "master-experience.md")
    comps, titles = [], []
    if not os.path.isfile(path):
        return comps, titles
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("## "):
                continue
            head = line[3:].split("|")[0].strip()
            parts = re.split(r"\s[-–—]\s", head, maxsplit=1)
            if len(parts) != 2:
                continue
            titles.append(parts[0].strip())
            comps.append(parts[1].split(",")[0].strip())
    return comps + LEGACY_COMPANIES, titles


def home_location(db_dir):
    """The **Location:** value from database/master-personal-info.md, or ""."""
    path = os.path.join(db_dir, "master-personal-info.md")
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"\s*-\s*\*\*Location:\*\*\s*(.+?)\s*$", line)
            if m:
                return m.group(1)
    return ""


def matches_any(segment, candidates):
    """Loose containment match, tolerant of trailing location words and suffixes."""
    seg = norm(segment)
    if len(seg) < 4:
        return None
    for c in candidates:
        cn = norm(c)
        if len(cn) < 4:
            continue
        if seg == cn or seg in cn or cn in seg:
            return c
    return None


def sections(paras):
    """{HEADING: [paragraphs until the next heading]}"""
    out, current = {}, None
    for p in paras:
        t = text_of(p).strip().upper()
        if HEADING_COLOR in p and t:
            current = t
            out[current] = []
        elif current:
            out[current].append(p)
    return out


def entry_headers(body):
    """(index, paragraph) for non-bullet paragraphs carrying the right tab stop."""
    return [(i, p) for i, p in enumerate(body) if not is_bullet(p) and RIGHT_TAB in p]


def bullets_after(body, idx):
    n = 0
    for p in body[idx + 1:]:
        if is_bullet(p):
            n += 1
        else:
            break
    return n


def style_ok(rpr, want_bold, want_sz):
    return is_bold(rpr) == want_bold and sz_of(rpr) == want_sz


def check_experience(body, comps, titles):
    headers = entry_headers(body)
    record(bool(headers), "experience/entries-present", "no Experience entry headings found")
    for i, p in headers:
        lines = lines_and_zones(p)
        company = joined(zone(lines, 0, 0))
        city = joined(zone(lines, 0, 1))
        title = joined(zone(lines, 1, 0))
        date = joined(zone(lines, 1, 1))
        tag = "experience[{0}]".format(company[:34] or text_of(p)[:34])

        if len(lines) < 2:
            record(False, tag + "/two-line-heading",
                   'heading is "{0}" on one line - the template wants two lines in one '
                   'paragraph: "Company -> tab -> City, Country", then <w:br/>, then '
                   '"Job Title -> tab -> dates"'.format(text_of(p).strip()))
            continue

        record(True, tag + "/two-line-heading")

        # The old template used "Job Title | Company" on line 1. Catch it being reused.
        if " | " in company:
            record(False, tag + "/no-title-pipe",
                   'line 1 is "{0}" - the current template keeps the company alone on '
                   'line 1 and the job title alone on line 2, with no pipe'.format(company))
        else:
            record(True, tag + "/no-title-pipe")

        record(bool(company), tag + "/company-line-1", "line 1 has no company name")
        record(company == company.upper(), tag + "/company-uppercase",
               '"{0}" must render in ALL CAPS - the template shows the company as '
               '"COMPANY NAME"'.format(company))
        record(bool(city), tag + "/city-after-tab",
               "line 1 must carry the location after the right tab")
        record(bool(title), tag + "/title-line-2", "line 2 has no job title")
        record(bool(date), tag + "/date-after-tab", "line 2 must carry the dates after the right tab")

        # company/title should not be swapped
        if company and matches_any(company, titles) and not matches_any(company, comps):
            record(False, tag + "/company-first",
                   '"{0}" is a job title. The template order is company on line 1, '
                   'job title on line 2 - this entry has them swapped'.format(company))
        else:
            record(True, tag + "/company-first")

        if comps and company and not matches_any(company, comps):
            record(False, tag + "/company-known",
                   '"{0}" matches no company in master-experience.md'.format(company),
                   warn_only=True)
        if titles and title and not matches_any(title, titles):
            record(False, tag + "/title-known",
                   '"{0}" matches no job title in master-experience.md'.format(title),
                   warn_only=True)

        cr = first_texty(zone(lines, 0, 0))
        record(style_ok(cr[0], True, SZ_COMPANY), tag + "/company-run-style",
               "company run must be bold sz={0}, got bold={1} sz={2}".format(
                   SZ_COMPANY, is_bold(cr[0]), sz_of(cr[0])))
        yr = first_texty(zone(lines, 0, 1))
        record(style_ok(yr[0], True, SZ_CITY), tag + "/city-run-style",
               "location run must be bold sz={0}, got bold={1} sz={2}".format(
                   SZ_CITY, is_bold(yr[0]), sz_of(yr[0])))
        tr = first_texty(zone(lines, 1, 0))
        record(style_ok(tr[0], False, SZ_JOBTITLE), tag + "/title-run-style",
               "job-title run must be non-bold at the inherited body size, got bold={0} sz={1}".format(
                   is_bold(tr[0]), sz_of(tr[0])))
        dr = first_texty(zone(lines, 1, 1))
        record(style_ok(dr[0], False, SZ_ENTRY_DATE), tag + "/date-run-style",
               'date "{0}" must be non-bold at the inherited body size, got bold={1} sz={2}'.format(
                   date, is_bold(dr[0]), sz_of(dr[0])))

        n = bullets_after(body, i)
        record(n >= 2, tag + "/min-two-bullets",
               "{0} bullet(s); the template pattern needs >= 2".format(n))
        record(n <= MAX_BULLETS, tag + "/bullet-ceiling",
               "{0} bullets; the template asks for around 2 to 4 per role - keep it "
               "only if the page genuinely needs the height".format(n),
               warn_only=True)


def check_projects(body):
    headers = entry_headers(body)
    record(bool(headers), "projects/entries-present", "no Project entry headings found")
    for i, p in headers:
        lines = lines_and_zones(p)
        heading = joined(zone(lines, 0, 0))
        date = joined(zone(lines, 0, 1))
        tag = "project[{0}]".format(heading.split(" | ")[0][:34])

        record(len(lines) == 1, tag + "/single-line",
               "project headings are one line in the template, no location second line")
        record(" | " in heading, tag + "/name-pipe-tech",
               'heading is "{0}" - the template wants '
               '"PROJECT TITLE | Technologies Used" (GitHub link optional)'.format(heading))
        hr = first_texty(zone(lines, 0, 0))
        record(style_ok(hr[0], True, SZ_PROJECT), tag + "/heading-run-style",
               "project heading run must be bold sz={0}, got bold={1} sz={2}".format(
                   SZ_PROJECT, is_bold(hr[0]), sz_of(hr[0])))
        dr = first_texty(zone(lines, 0, 1))
        record(bool(date) and style_ok(dr[0], False, SZ_PROJECT), tag + "/date-run-style",
               "date must sit after the right tab, non-bold sz={0}, got {1!r} bold={2} sz={3}".format(
                   SZ_PROJECT, date, is_bold(dr[0]), sz_of(dr[0])))
        n = bullets_after(body, i)
        record(n >= 2, tag + "/min-two-bullets",
               "{0} bullet(s); the template pattern needs >= 2".format(n))
        record(n <= MAX_BULLETS, tag + "/bullet-ceiling",
               "{0} bullets; the template asks for around 2 to 4 per entry - keep it "
               "only if the page genuinely needs the height".format(n),
               warn_only=True)


def check_education(body):
    rows = [p for p in body if text_of(p).strip()]
    record(len(rows) >= 2 and len(rows) % 2 == 0, "education/school-degree-pairs",
           "expected school+degree paragraph pairs, got {0} paragraph(s)".format(len(rows)))
    for j in range(0, len(rows) - 1, 2):
        slines = lines_and_zones(rows[j])
        dlines = lines_and_zones(rows[j + 1])
        sr = first_texty(zone(slines, 0, 0))
        dr = first_texty(zone(dlines, 0, 0))
        tag = "education[{0}]".format(sr[1].strip()[:28])
        record(style_ok(sr[0], True, SZ_EDU_SCHOOL), tag + "/school-style",
               "school run must be bold sz={0}, got bold={1} sz={2}".format(
                   SZ_EDU_SCHOOL, is_bold(sr[0]), sz_of(sr[0])))
        record(bool(joined(zone(slines, 0, 1))), tag + "/school-location",
               "school line must carry the location after the right tab")
        record(is_italic(dr[0]) and sz_of(dr[0]) is INHERIT, tag + "/degree-style",
               "degree run must be italic at the inherited body size, got italic={0} sz={1}".format(
                   is_italic(dr[0]), sz_of(dr[0])))
        record(bool(joined(zone(dlines, 0, 1))), tag + "/degree-dates",
               "degree line must carry the dates after the right tab")


def check_achievements(body):
    """Achievements are warn-only: the template's shape is bold name -> tab -> date,
    but the exact run sizes here have never been the thing that goes wrong."""
    rows = [p for p in body if text_of(p).strip()]
    for p in rows:
        lines = lines_and_zones(p)
        name = joined(zone(lines, 0, 0))
        tag = "achievement[{0}]".format(name[:28])
        record(is_bold(first_texty(zone(lines, 0, 0))[0]), tag + "/name-bold",
               "achievement name should be bold, as in the template", warn_only=True)
        record(bool(joined(zone(lines, 0, 1))), tag + "/date-after-tab",
               "achievement date should sit after the right tab", warn_only=True)


LOCATION_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]*,\s*[A-Za-z][A-Za-z .]*$")


def check_header(paras, home):
    """The contact line leads with the location (template revision 2026-09-19 pm).

    Before that revision the location trailed the line, after Portfolio. Any
    resume still built from the old shape trips this.
    """
    contact = None
    for p in paras[:6]:
        if HEADING_COLOR in p:            # reached the first section rule
            break
        if " | " in text_of(p):
            contact = p
            break
    if contact is None:
        record(False, "header/contact-line", "no ' | '-separated contact line in the header")
        return

    segs = [x.strip() for x in text_of(contact).split("|")]
    segs = [x for x in segs if x]
    first, last = segs[0], segs[-1]

    if LOCATION_RE.match(first):
        record(True, "header/location-first")
    elif LOCATION_RE.match(last):
        record(False, "header/location-first",
               'the contact line ends with "{0}" - the template now leads with the '
               'location: "{0} | phone | email | LinkedIn | GitHub | Portfolio"'.format(last))
    else:
        record(False, "header/location-first",
               'the contact line starts with "{0}", which is not a "City, Prov" '
               "location - the template leads with the location".format(first))

    if home and segs:
        loc = first if LOCATION_RE.match(first) else (last if LOCATION_RE.match(last) else "")
        record(norm(loc) == norm(home), "header/location-matches-db",
               'header says "{0}", master-personal-info.md says "{1}"'.format(loc, home),
               warn_only=True)


def check_skills(body):
    """The template ships three "Category: skills" lines; more is a warning."""
    lines = []
    for p in body:
        for chunk in re.split(r"<w:br/>", p):
            t = unescape("".join(re.findall(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", chunk, re.S))).strip()
            if t and ":" in t:
                lines.append(t)
    record(bool(lines), "skills/categories-present", "no 'Category: skills' lines found")
    record(len(lines) <= MAX_SKILL_CATEGORIES, "skills/category-ceiling",
           "{0} category lines; the template ships {1}".format(len(lines), MAX_SKILL_CATEGORIES),
           warn_only=True)


def check_page_setup(out_xml, tmpl_xml):
    def sect(x):
        size = re.search(r"<w:pgSz[^>]*/>", x)
        mar = re.search(r"<w:pgMar[^>]*/>", x)
        return (size.group(0) if size else None, mar.group(0) if mar else None)

    o, t = sect(out_xml), sect(tmpl_xml)
    if None in o or None in t:
        record(False, "page-setup/present", "could not read pgSz/pgMar", warn_only=True)
        return
    record(o[0] == t[0], "page-setup/page-size",
           "page size changed\n        template: {0}\n        resume:   {1}".format(t[0], o[0]))
    record(o[1] == t[1], "page-setup/margins",
           "margins changed - widening margins to make content fit is not allowed"
           "\n        template: {0}\n        resume:   {1}".format(t[1], o[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resume")
    ap.add_argument("--template", default=None)
    ap.add_argument("--db", default=None)
    args = ap.parse_args()

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template = args.template or os.path.join(repo, "resume-template", "resume-template.docx")
    db_dir = args.db or os.path.join(repo, "database")

    for f in (args.resume, template):
        if not os.path.isfile(f):
            print("RESULT checks=0 failed=1 warned=0 verdict=FAIL")
            print("FAIL: file not found: " + f)
            return 2

    out_xml = read_xml(args.resume)
    tmpl_xml = read_xml(template)
    comps, titles = companies_and_titles(db_dir)

    out_paras = paragraphs(out_xml)
    secs = sections(out_paras)
    order = [h for h in secs if h in EXPECTED_ORDER]

    print("checking " + args.resume)
    print("against  " + template)
    print()

    record(order == EXPECTED_ORDER[:len(order)] and "PROFESSIONAL EXPERIENCE" in order,
           "sections/order",
           "expected {0} (Achievements optional), got {1}".format(
               " > ".join(EXPECTED_ORDER), " > ".join(order) or "none"))
    record(not any("SUMMARY" in h or "PROFILE" in h for h in secs), "sections/no-summary",
           "the template has no Summary/Profile section")

    check_header(out_paras, home_location(db_dir))

    if "PROFESSIONAL EXPERIENCE" in secs:
        check_experience(secs["PROFESSIONAL EXPERIENCE"], comps, titles)
    if "PROJECTS" in secs:
        check_projects(secs["PROJECTS"])
    if "TECHNICAL SKILLS" in secs:
        check_skills(secs["TECHNICAL SKILLS"])
    if "EDUCATION" in secs:
        check_education(secs["EDUCATION"])
    if "ACHIEVEMENTS" in secs:
        check_achievements(secs["ACHIEVEMENTS"])
    check_page_setup(out_xml, tmpl_xml)

    print()
    verdict = "FAIL" if failures else "PASS"
    print("RESULT checks={0} failed={1} warned={2} verdict={3}".format(
        len(checks), len(failures), len(warnings), verdict))
    if failures:
        print("FAIL: {0} pattern deviation(s) from resume-template.docx.".format(len(failures)))
        print("      Fix the .docx rendering (Step 10) - never change approved wording to satisfy it.")
        return 1
    print("PASS: every entry follows the resume-template.docx pattern.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
