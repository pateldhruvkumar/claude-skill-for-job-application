# Loan Portfolio Analytics — Portfolio Project Design

**Date:** 2026-07-14
**Status:** Approved by user (brainstorming session)
**Lives in:** a new standalone public GitHub repo (`loan-portfolio-analytics`); this spec lives in job-hunting because the project's purpose is resume material for the data-analyst track.

## Purpose

Build a resume-ready, end-to-end banking analytics project that demonstrates Excel, Power BI, and Python working together on one dataset — the way a real bank portfolio-analytics team operates. It exists to patch the BI-depth gap flagged on data-analyst-track applications (e.g. Nature's Path BI & Analytics Specialist was a STRETCH-APPLY due to thin Power BI/Excel portfolio evidence) and to extend the Vault AI private-credit narrative into a personal project the user can demo.

**Success criteria:**

1. A public GitHub repo a recruiter can skim in 2 minutes (README leads with findings + screenshots).
2. Working `.pbix`, `.xlsx`, and Python pipeline that reproduce each other's numbers.
3. A new entry in `database/master-project.md` (data-analyst-track bullet set) usable by `applying-to-job` immediately.
4. Completed in ~1 focused week alongside ongoing applications.

## Domain and dataset

- **Domain:** banking — credit risk / loan portfolio health (user's choice; pairs with Vault AI private-credit experience).
- **Dataset:** LendingClub accepted loans 2007–2018Q4 from Kaggle (`wordsforthewise/lending-club`), ~2.26M rows × 151 columns, ~1.6 GB raw. Real, messy, and large enough that Python is justified rather than decorative.
- Raw data is **gitignored**; README documents the manual Kaggle fetch (free account required).

## Architecture — three layers, one data flow

```
Kaggle raw CSV (2.26M × 151)
        │  Python (pandas + pyarrow)
        ▼
star schema: fact_loans + dim_date/grade/purpose/geography  (Parquet/CSV)
        │                          │
        ▼                          ▼
Excel analyst workbook      Power BI flagship dashboard
(Power Query on extracts)   (model + DAX + 4 report pages)
```

### Layer 1 — Python pipeline (`scripts/`)

One cleaning script (plus optional exploration notebook):

- Load raw CSV efficiently (pyarrow / chunked); select ~30 analysis-relevant columns.
- Clean: type coercion, date parsing, missing-value handling (`emp_length`, `revol_util`).
- Engineer: `default_flag` (Charged Off/Default), loan-status buckets (Fully Paid / Current / Late / Default+Charged Off), issue vintage (year, quarter), FICO bands, DTI bands, income bands.
- Output: `fact_loans` + `dim_date`, `dim_grade`, `dim_purpose`, `dim_geography` (Parquet/CSV) + three pre-aggregated CSV extracts for Excel: grade × vintage KPIs, monthly portfolio KPIs, and state-level KPIs (each well under Excel's row limits).
- Emit `data_quality_report.txt`: rows in/out, null audit, key KPI totals — the reconciliation baseline for the other two layers.

### Layer 2 — Excel analyst workbook (`excel/loan_portfolio_analysis.xlsx`)

- **Power Query** connection to the aggregated extracts (not pasted data).
- Pivot tables: default rate by grade × vintage; delinquency aging with conditional formatting.
- Executive summary sheet: XLOOKUP/SUMIFS KPI cells + sparklines.
- What-if sheet: portfolio-yield sensitivity to loss-rate assumptions (Data Table).
- About sheet: sources, methodology, caveats (same discipline as the seaweed dashboard).

### Layer 3 — Power BI dashboard (`powerbi/loan_portfolio.pbix`)

- Star-schema model over the Python outputs.
- ~15 DAX measures: default rate, charge-off rate, weighted-avg FICO, avg interest rate, portfolio yield, expected-loss proxy, recovery rate, rolling-12-month default rate, YoY funded growth (time intelligence).
- Four pages:
  1. **Portfolio Overview** — KPI cards, funded-volume and default-rate trends, status breakdown.
  2. **Risk Segmentation** — grade/subgrade, FICO band, DTI band, purpose; decomposition tree.
  3. **Vintage Analysis** — cohort default curves by issue year (matrix + line). Flagship page.
  4. **Geography** — state map: volume vs default rate.
- Interactions: slicers (year, grade, term, state), drill-through to segment detail, bookmarks for an exec view.
- **Labeled caveat on immature vintages:** recent cohorts understate lifetime default rates because loans haven't aged; the dashboard marks these rather than hiding the bias. (Deliberate interview talking point.)

## Deliverables and repo layout

```
loan-portfolio-analytics/
├── data/            # raw + processed, gitignored; README explains fetch
├── scripts/         # Python pipeline + data_quality_report output
├── excel/           # loan_portfolio_analysis.xlsx
├── powerbi/         # loan_portfolio.pbix
├── docs/screenshots/
└── README.md
```

- README leads with **3–5 concrete findings** (e.g. default-rate step-up by grade, underperforming vintages) before any tech detail, plus an architecture diagram, KPI definitions, and caveats.
- Power BI ships as `.pbix` + screenshots. Publishing to Power BI Service is optional polish, not in scope.

## Verification

Every KPI on the Power BI overview page is **reconciled three ways**: Power BI measure vs Excel pivot vs Python `data_quality_report.txt`. Numbers must match before the project is called done. This is both the quality gate and a rehearsed interview line about testing BI outputs.

## Schedule (~1 week)

| Day | Work |
|---|---|
| 1 | Kaggle account/download, raw-data exploration |
| 2 | Python cleaning pipeline + star-schema outputs + quality report |
| 3 | Excel workbook (Power Query, pivots, what-if, exec summary) |
| 4–5 | Power BI model, DAX measures, 4 report pages, interactions |
| 6 | README, screenshots, three-way reconciliation pass |
| 7 | Findings write-up + resume bullets into `database/master-project.md` |

## Resume integration (back in job-hunting repo)

Final step adds a data-analyst-track project entry to `database/master-project.md`:

- one bullet on the Python pipeline (2.26M-row scale, star-schema outputs, data-quality report),
- one on the Excel deliverable (Power Query, pivots, what-if analysis),
- one on the Power BI model (star schema, DAX measures, drill-through, vintage analysis),
- one findings/impact bullet (written from actual results — numbers TBD until analysis runs; placeholder is intentional and resolved on Day 7).

## Risks and constraints

- Kaggle download is a manual step (free account) — Day 1.
- 1.6 GB raw file: pipeline must use pyarrow/chunked loading; raw data never committed.
- Vintage-maturity bias: handled as a labeled caveat, not hidden.
- Power BI Desktop required (free; user is on Windows 11 — fine). Excel with Power Query required (Microsoft 365 or 2016+).
- Scope discipline: no ML scoring model (explicitly rejected as Approach C), no Power BI Service publishing, no additional datasets. One week means the four pages and the workbook, done well.

## Decisions log

- Domain: banking (user), problem: credit risk / loan portfolio (user picked recommended option).
- Approach A (single end-to-end pipeline) chosen over three mini-projects (B) and A+ML scoring (C).
- Time budget: ~1 focused week (user picked recommended option).
- New standalone repo rather than a folder in job-hunting: portfolio material must be public and self-contained.
