# Master Projects

> Canonical project record. Use this file as the source of truth when tailoring resumes for specific job applications. Companion to `master-experience.md`.
>
> **Special rule for the flagship project below:** the Seaweed Market Intelligence Dashboard has three role-specific variants (Data Analyst, Software Developer, AI Engineer). Any given resume must use **exactly one** variant — pick the one matching the target role.

---

### Seaweed Market Intelligence Dashboard (PSIA) | May 2026 - Jul 2026
GitHub: https://github.com/pateldhruvkumar/seaweed-industry | Live: https://seaweed-industry.vercel.app

> Flagship project. Three role-specific variants below - use exactly ONE per resume, matching the target role. All numbers verified against the repo as of Jul 2026 (13 tabs, 11 datasets / 33K+ rows, 35 JSON outputs, 34 Vitest + 22 pytest tests, 12 PRs).

#### Variant 1: Data Analyst | Python, SQL (DuckDB), React, Recharts, Plotly

- Shipped a live 13-tab market-intelligence dashboard visualizing 33,000+ records across 11 FAO and Statistics Canada datasets, giving stakeholders self-serve access to production, trade, pricing, and licensing KPIs by transforming raw UN FAO and StatCan tables into 35 curated chart datasets rendered with Recharts.
- Created a 7-section exploratory data analysis module that surfaces data-quality issues before they reach stakeholders, combining per-dataset summary statistics, a missing-data matrix, log-scale distributions, top-N rankings, a top-20-country correlation heatmap, and IQR outlier boxplots.
- Engineered a Python preprocessing pipeline converting 11 raw CSVs (33K+ rows) into 35 chart-ready JSON datasets by aggregating, joining, and validating production, value, and trade tables with pytest coverage, moving all heavy computation out of the browser.
- Expanded coverage to the Canadian market by integrating 7 Statistics Canada, DFO, and Nova Scotia licensing datasets into dedicated Economics and Licensing & Sites KPI tabs, with per-chart citation footnotes distinguishing seaweed-specific figures from all-aquaculture proxies to keep every claim defensible.
- Enabled non-technical users to query 4 production tables in plain English by building a Text-to-SQL assistant on FastAPI and DuckDB that pairs embedding-based entity resolution with 20 few-shot examples and LLM SQL generation.
- Cut stakeholder reporting to one click by shipping client-side export of any tab to branded PDF, PowerPoint, and Excel files, and automated .pptx briefing decks via Playwright screenshot capture piped into python-pptx.

#### Variant 2: Software Developer | React 18, Vite, Tailwind, FastAPI, DuckDB, Vitest, pytest

- Shipped a live 13-tab analytics dashboard (React 18, Vite, Tailwind, Recharts) visualizing 33,000+ records across 11 datasets, using lazy-loaded routes and 35 preprocessed JSON payloads to keep the initial bundle lean, deployed on Vercel.
- Architected a FastAPI + DuckDB backend that turns natural-language questions into guarded SQL over 4 tables through a 6-step pipeline: embedding-based entity resolution, few-shot retrieval, LLM SQL generation, validated execution, and result summarization.
- Designed the chat experience across 12 purpose-built React components with streaming reveal, abort and regenerate, edit-and-resend conversation branching, and localStorage-persisted saved threads, hardening it against stale-state and superseded-request race conditions.
- Delivered fully client-side export of any dashboard tab to branded PDF, PowerPoint, and Excel by combining html-to-image DOM capture with jsPDF, PptxGenJS, and SheetJS, auto-collecting source citations from tagged components at zero backend cost.
- Migrated the chart layer from Plotly.js to Recharts across the dashboard (keeping Plotly only for heatmaps and boxplots), cutting the heavyweight Plotly dependency out of most tabs and unifying chart styling.
- Safeguarded every release with 55+ Vitest and pytest unit tests covering data transforms, chat race conditions, export deduplication, and the SQL pipeline, shipped through 12 reviewed pull requests on a development-branch flow.

#### Variant 3: AI Engineer | FastAPI, DuckDB, Sentence Transformers, Groq/OpenRouter LLM, React

- Built a production Text-to-SQL analytics assistant answering plain-English questions over 4 DuckDB tables by designing a 6-step FastAPI pipeline combining embedding-based entity resolution, few-shot retrieval, LLM SQL generation, guarded execution, and result summarization.
- Grounded the LLM with retrieval by indexing table entities and 20 seed question-to-SQL examples with bge-small-en-v1.5 sentence embeddings, so each query resolves against real table values and is steered by the closest worked examples instead of raw schema alone.
- Migrated the generation model from Groq Llama-3.3-70B to OpenRouter Qwen and hardened the SQL pipeline against malformed generations, surfacing backend error text and a pending indicator in the UI so failures stay transparent to users.
- Designed the assistant's chat UX across 12 React components with streaming reveal, abort and regenerate, edit-and-resend conversation branching, and saved threads persisted to localStorage, hardened against superseded-request race conditions.
- Shipped the host product: a live 13-tab dashboard (React 18, FastAPI, DuckDB) visualizing 33,000+ FAO and Statistics Canada records on Vercel, with the AI panel open by default as the flagship interaction.
- Verified the pipeline with 22 pytest unit tests spanning the DuckDB loader, embedding indexes, and end-to-end /chat behavior, plus 34 Vitest tests on the chat frontend.

### Credit Risk Analytics Pipeline - Lending Club Loan Book | Databricks, Delta Lake, Unity Catalog, Spark SQL, PySpark, Auto Loader, Python | Sep 2026 - Present

> Bronze and silver layers complete and validated; gold analytical marts and the Databricks AI/BI dashboard being finalized as of Sep 2026. Strongest interview talking points: the default-rate target correction and the CSV column-misalignment root-cause diagnosis (both more compelling than any chart). No public repo yet - publish once the dashboard is done.
>
> **Canonical counts - do not mix with older drafts.** Raw CSV: 2,260,701 rows x 151 source columns, 1.5 GB, in a Unity Catalog volume. Retained for analysis: 52 columns. Fully-null records dropped: 33 (leaving 2,260,668). Batch re-run duplicates removed: 603 (2,261,270 rows loaded against 2,260,667 distinct ids). An earlier version of this entry cited 152 source fields and ~40 retained columns - superseded, do not reuse those figures.

- Built an end-to-end medallion pipeline (bronze, silver, gold) on Databricks and Delta Lake that ingested and validated 2,260,701 Lending Club loan records across 151 source columns from a 1.5 GB CSV in a Unity Catalog volume, choosing Databricks managed volumes over an evaluated AWS S3 and external-volume data lake on cost grounds without losing pipeline functionality.
- Enforced read-time column types without hand-writing a 151-field schema, capturing Spark's inferred StructType, overriding only id to IntegerType and annual_inc to DoubleType through a list comprehension, and re-reading the CSV against that explicit schema, so inference still covered the other 149 fields while the record key and the borrower-income column were no longer left to it.
- Implemented and compared two bronze ingestion strategies on cost, idempotency, and incremental behavior: an Auto Loader (cloudFiles) streaming source using checkpointing, a rescued-data column for schema drift, and an availableNow trigger so re-runs pick up only new files, versus a year-partitioned PySpark batch load, proving the checkpointed stream was idempotent where the manual batch was not.
- Cut a bronze reload from 12 full-file scans to 1 by diagnosing that the batch loop filtered directly against read_files and re-scanned the full 1.5 GB on every vintage iteration, then specifying the fix (read once into a DataFrame, filter in memory) and the production pattern (batch on file arrival, not column value).
- Reduced 151 raw columns to 52 retained fields, each cut backed by a documented reason, by profiling null and NaN counts across every column in a single agg call (guarding the NaN check to numeric types so string columns could not error) and classifying sparsity by cause (no-information, structural, informative-missingness, vintage-driven) rather than by a blanket null threshold.
- Traced three unrelated-looking defects to one root cause, a 'Feb-2004' date landing in the numeric fico_range_low column, a ' reactors' token in emp_length, and an 'Oct-2015' value in loan_status, all produced by free-text description fields whose embedded commas and newlines shifted every downstream column one position because the CSV reader lacked multiLine parsing, then re-ingested with multiLine, quote, and escape options, replaced casts with try_cast/try_to_date, and quarantined unrecoverable rows in a silver_loans_rejected table.
- Normalized the text columns the analysis needed as numerics, stripping ' months' out of term with regexp_replace and casting to int, reformatting issue_d, earliest_cr_line, and last_credit_pull_d from MMM-yyyy with try_to_date rather than to_date so an unparseable date returns null instead of failing the job, and collapsing employment-length text ('10+ years', '< 1 year', and the corrupt ' reactors') to integers with a when chain and regexp_extract.
- Removed two classes of row-level defect in silver while leaving bronze intact as the faithful ingestion record: 603 duplicate loans traced to a re-run of the first INSERT in the batch loop (2,261,270 rows loaded against 2,260,667 distinct ids), deduplicated with QUALIFY row_number() OVER (PARTITION BY id ORDER BY issue_date DESC), and 33 records that were null across every column, dropped on a loan_status is-not-null filter.
- Corrected a materially understated default rate by redefining the target: because loan_status mixes live loans (Current, Late, In Grace Period) with resolved ones, set is_default to NULL for unresolved loans behind an is_resolved flag so avg(is_default) excludes in-flight loans instead of counting them as repaid, the single largest accuracy gain in the project.
- Engineered the silver feature set for credit modeling by deriving FICO midpoint, credit-history months, and vintage year from the parsed date and score fields, coalescing 95%-null joint-applicant income and DTI into fully populated columns, and separating application-time inputs from post-origination fields so a downstream model cannot train on information unavailable when a loan is actually scored.
- Developed the gold analytical layer in Spark SQL to test whether grade-based pricing covers realized losses, combining CTEs, window functions (lag, rank, ROW_NUMBER, running sum), QUALIFY, CASE risk segmentation, correlated subqueries, and conditional aggregation into risk ordering by grade, a FICO-by-DTI default matrix, vintage cohort curves, loss-given-default by grade, state-level origination concentration, borrowers benchmarked against their own state's average DTI, and an interest-premium-versus-default-rate adequacy view, with small-group comparisons gated behind HAVING COUNT(*) >= 50 so thin samples could not drive a conclusion.

### Multi-City Weather Data Warehouse - Dimensional ELT Pipeline | Python, pandas, SQLAlchemy, PostgreSQL 16, Docker Compose | Sep 2026 - Present
GitHub: https://github.com/pateldhruvkumar/weather-data-engineer

- Built an end-to-end ELT pipeline that ingests 105,408 hourly weather observations spanning 12 cities across 6 continents in under 90 seconds per run, converting the Open-Meteo Archive API's parallel-array JSON into a one-row-per-city-per-hour relational table with Python, requests, and pandas.
- Eliminated 632,448 duplicated field values by normalizing six repeating city attributes out of the fact table into a dedicated dimension table, enforcing the split with a foreign key and a composite (city_id, observed_at) primary key in PostgreSQL 16 DDL so a city cannot hold two readings for the same hour.
- Made repeat runs idempotent, writing 0 duplicate rows on re-execution, by staging each DataFrame into a scratch table and merging it with a single INSERT ... SELECT ... ON CONFLICT statement inside one atomic transaction per table, applying DO UPDATE to mutable city attributes and DO NOTHING to immutable historical readings.
- Cut the load stage from 105,408 network round trips to roughly 21 by batching multi-row inserts at 5,000 rows per statement, sized deliberately to stay under PostgreSQL's 65,535 bind-parameter ceiling.
- Kept the pipeline running through partial API outages by isolating every city's fetch behind its own error boundary, so a single failed request is logged and counted in the run summary while the remaining 11 cities still load successfully.
- Made the city roster config-driven so analysts onboard a new city by adding one CSV row instead of changing code, filtering extraction on an is_active flag while retaining retired cities in the dimension table to keep historical foreign keys valid.
- Provisioned reproducible infrastructure as code with Docker Compose running PostgreSQL 16 behind a pg_isready healthcheck and auto-applying the schema DDL on first boot, resolving credentials from a gitignored .env through SQLAlchemy's URL builder so passwords are escaped rather than string-interpolated.

### Olist E-Commerce Logistics & Margin Optimization Pipeline | Python, PostgreSQL (Supabase), SQL, Excel (Power Query, Power Pivot), Power BI (DAX) | Apr 2026 - Jul 2026
GitHub: https://github.com/pateldhruvkumar/end-to-end-e-commerce
Excel Power Query data model: Dhruvkumar_Patel_Olist_Logistics_Data_Model.xlsx (~30 MB; shareable work sample)

- Built an end-to-end analytics pipeline that moved 100K+ Olist Brazilian e-commerce records from 9 raw Kaggle CSVs into a live cloud Supabase PostgreSQL database using a Python and SQLAlchemy loader with chunked, multi-row bulk inserts, replacing flat-file analysis with a queryable relational source.
- Engineered a lightweight ETL pipeline in Excel Power Query to ingest, clean, and transform four raw datasets (orders, order_items, customers, payments) straight into the workbook data model, running cross-table merges and mapping Portuguese product categories to English for standardized reporting, then modeling a star schema in Power Pivot with primary/foreign-key relationships linking the Orders and Order Items fact tables to Customers and Products dimensions.
- Engineered a SQL master view joining orders, order_items, customers, and products that derives delivery_delay_days from the gap between actual and estimated delivery dates, handles nulls, and filters to delivered orders, so every downstream tool consumed clean, pre-calculated data instead of raw tables.
- Developed a dynamic Excel unit-economics "What-If" model on PivotTables covering all 27 Brazilian states, driving projected freight and per-order margin loss from a single carrier-rate parameter cell with absolute references, giving the operations team a sandbox to test carrier pricing scenarios.
- Quantified freight-cost sensitivity with the model, showing a 20% carrier rate hike adds $8.01 of freight cost per order in remote Acre versus just $3.02 in São Paulo, translating an abstract rate change into concrete per-state margin impact.
- Modeled the Power BI dataset as a star schema, building a dynamic DAX date dimension with CALENDARAUTO and linking it one-to-many to the logistics fact table to unlock time-intelligence analysis across 2016 to 2018 via a year slicer.
- Centralized business logic in a dedicated DAX measures table, including an SLA Breach Rate measure that divides late orders (delivery_delay_days > 0) by total orders, exposing a 7% nationwide breach rate against 60K total orders and an 11-day average early-delivery buffer.
- Implemented a custom Brazil Shape Map hardcoded to national geometry to bypass Bing Maps misreading Brazilian state codes as US states (e.g., AL as Alabama, not Alagoas), with red/green conditional formatting on SLA breach rate for instant, pre-attentive reading of failure hotspots.
- Surfaced actionable logistics insights: freight-to-price ratios above 50% in remote northern states (Rondônia 59.6%, Roraima 56.8%, Maranhão 55.0%) versus 26.5% in São Paulo, and heavy/bulky categories such as furniture as the main drivers of nationwide delivery delays, pointing to a need for a specialized oversized-freight partner.

### Shakespeare Text Generator — Transformer Inference Microservice | PyTorch, FastAPI, Docker, Google Cloud Run | Jan 2026 - Mar 2026
GitHub: https://github.com/pateldhruvkumar/transformer-microservice-gcp

- Shipped a custom PyTorch transformer language model as a live public REST microservice on Google Cloud Run, serving text generation within a 1 GiB memory ceiling (~500 MB runtime footprint) and 5–10 second cold starts, by containerizing a CPU-only inference stack on python:3.11-slim with dependency layers cached separately from application code.
- Implemented an encoder-only transformer from scratch in PyTorch — 4,865,326 parameters across 2 layers and 2 attention heads, 200-dim embeddings, sinusoidal positional encoding, and a 10,926-word vocabulary — and trained it on the Tiny Shakespeare corpus in ~2.5 minutes on a laptop CPU, proving the full stack runs GPU-free end to end.
- Made the entire model lifecycle reproducible in one command while keeping ~22 MB of binary artifacts out of git, by codifying corpus download, 90/5/5 train/validation/test splits, vocabulary construction, and SGD training with StepLR decay into a single artifact-export script that emits weights, vocab, and hyperparameters.
- Blocked malformed requests before they reached the model by enforcing typed Pydantic contracts on the /generate endpoint — max_tokens bounded to 1–200, temperature to 0.1–2.0, top-k to 0–50 — so invalid input fails fast with structured validation errors instead of surfacing as inference crashes.
- Gave users direct control over the coherence–creativity trade-off by implementing temperature-scaled top-k sampling over a 256-token sliding context window, exposed as three decoding presets (greedy, balanced, creative) through both the JSON API and a built-in browser UI.
- Cut model-load cost out of the request path entirely by loading weights and vocabulary once at startup via FastAPI's lifespan hook into a shared singleton, structuring the service into single-purpose modules (routes, schemas, model, state) with a /health endpoint for platform monitoring.

### Vancouver International Airport (YVR) — Capstone | Jan 2026 – Apr 2026

- Designed a 7-tab Streamlit dashboard on 183,909 cleaned charging sessions spanning 56 PosiCharge DVS 400 chargers, giving YVR operations real-time visibility into charger health for a 260-vehicle electric ground-support fleet.
- Engineered a Weighted Ensemble forecasting model (Random Forest + XGBoost + LightGBM) on 33 derived time, lag, flight, and weather features, hitting 84.7% binary accuracy and a 28% MAE reduction (15.26 → 10.94) over a 2-month baseline.

### AWS Big Data Pipeline – Serverless ETL Architecture | AWS S3, Lambda, Glue, DynamoDB | Jan 2026 - Mar 2026
GitHub: https://github.com/pateldhruvkumar/bigdata-final-project

- Automated ingestion of 5.6M user records into DynamoDB with zero manual steps by building an event-driven serverless ETL pipeline in Python where S3 upload events trigger a Lambda that launches an AWS Glue 4.0 job to validate, transform, and load data end-to-end.
- Scaled the load stage to complete 5.6M writes in a single Glue run without throttling by repartitioning the dataset across 150 Spark partitions and tuning 20 parallel DynamoDB writers with 25-item batched requests and a 10-retry policy on on-demand capacity.
- Enforced 100% key uniqueness across 5.6M records by generating deterministic MD5-based IDs for keyless rows, deduplicating and null-filtering in Spark, and stamping every item with ingestion timestamp and source-file lineage for auditability.
- Reduced environment setup and teardown to a single command each by codifying the full stack — S3, Lambda, Glue, DynamoDB, and two least-privilege IAM roles — as boto3 provisioning/cleanup scripts, making the pipeline reproducible and cost-safe between runs.

### eHealth – Electronic Health Records (EHR) Platform | Next.js 16, React 19, TypeScript, Supabase (Postgres RLS, Auth, Storage), TanStack Query | Jan 2026 – Jul 2026 
GitHub: https://github.com/pateldhruvkumar/ehealth

- Built a full-stack Electronic Health Records platform for 3 role-based user types (patient, doctor, admin) on Next.js 16 (App Router) and React 19, backed entirely by Supabase — Postgres, Auth, and Storage — with no separate API server, making the database itself the security boundary.
- Re-architected the original Node.js/Fastify + Prisma + JWT + AWS S3 backend onto Supabase, collapsing a standalone REST service into database-enforced Row Level Security and SECURITY DEFINER Postgres functions while keeping the frontend's service/hook layer stable.
- Enforced least-privilege access with Row Level Security across all 8 tables: patients reach only their own rows (user_id = auth.uid()), while doctors read a patient's data solely through an active, unexpired share (has_active_share), and soft-deleted documents are never visible to doctors.
- Routed every privileged multi-step operation through 6 SECURITY DEFINER RPCs (grant_access, revoke_access, verify_access_code, log_access, get_patient_dashboard, get_doctor_dashboard), blocking all direct client writes to the shared_access and access_logs tables.
- Implemented patient-controlled record sharing via QR-code access codes with time-based expiry and revocation, plus a tamper-resistant audit trail that logs the real client IP and user agent on every access through a dedicated API route.
- Secured documents in a private Supabase Storage bucket ({patient_id}/{document_id}/{file}) with Storage RLS mirroring the table policies; uploads stream browser-to-storage and downloads use short-lived signed URLs, keeping file bytes off any app server.
- Validated sessions in Next.js middleware by verifying the ES256 Supabase JWT against the project JWKS (getClaims), guarding /patient, /doctor, and /onboarding routes without a database round trip.
- Proved the security model with an automated 25-assertion Row Level Security verification matrix run against the live project, codifying cross-role access rules as executable tests.

### Steve's and Associates — Billing & Revenue Analysis Suite (Capstone) | Python, R, scikit-learn, NLTK, pandas, ggplot2, OpenRouter LLM API | Sep 2025 – Dec 2025
GitHub: https://github.com/pateldhruvkumar/xn-project

- Transformed 7 fiscal years (FY19–FY25) of raw Excel billing exports across 50+ enterprise clients into a single canonical, analysis-ready dataset by building a Python cleaning pipeline (pandas, openpyxl) that standardized inconsistent timesheet exports, accelerating executive report generation by 40%.
- Gave partners a consistent view of engagement profitability by defining and computing the firm's core billing KPIs — efficiency ratio, realized rate, extended-vs-revenue variance, and per-client discount percentage — as reusable aggregation logic instead of one-off spreadsheet formulas.
- Replaced ad-hoc spreadsheet charting with 15+ consistently themed, executive-ready visualizations (fiscal-year comparisons, top-client revenue, correlation matrices, discount analysis by client and year) built in matplotlib/seaborn with a uniform brand palette across every output.
- Cut manual categorization effort by ~70% by surfacing 7 recurring business themes from unstructured project summary notes, using a text-mining pipeline that combined TF-IDF, K-Means (validated with Elbow and Silhouette analysis), and LDA topic modeling in scikit-learn and NLTK, with GloVe embeddings (50–300d) for semantic comparison.
- Removed a manual writing step from every billing cycle by automating first-draft invoice descriptions, integrating the OpenRouter LLM API to convert raw project summaries into client-ready invoice language.
- De-risked the findings by implementing the full statistical and topic-modeling workflow twice — in Python (pandas, scikit-learn) and in R (dplyr, ggplot2, tidytext, topicmodels) — confirming that themes and billing metrics reproduced across independent toolchains.


### Kahoot Bot – Agentic AI Automation | Python, n8n, REST APIs | Aug 2025

- Shipped an automated AI quiz system in Python with n8n orchestrating 3 open-source APIs, hitting 90% accuracy while cutting inference costs by 60% via optimized call sequencing; placed 2nd of 15+ teams at Northeastern's Agentic AI 2.0 Hackathon.
