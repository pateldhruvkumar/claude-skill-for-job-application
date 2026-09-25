# Master Experience

> Canonical work-experience record. Use this file as the source of truth when tailoring resumes for specific job applications. Companion files for technical skills, education, and projects will live alongside it.

---
## Inventory Analyst - Associated Grocers, Surrey, BC | Mar 2025 – Present

> Role covers the full inventory-analyst scope: cycle counting, variance investigation, stock adjustments, receiving reconciliation, and KPI reporting. Details in [brackets] are to confirm before use on a tailored resume.

- Manage daily cycle counts and inventory audits across warehouse systems, reconciling stock levels for 200+ orders daily serving roughly 300 retail stores.
- Investigate count variances and trace discrepancies to root causes [receiving errors, mispicks, unrecorded damage], posting stock adjustments that keep on-hand records accurate for replenishment decisions.
- Validate incoming deliveries against bills of lading and packing slips, resolving quantity and item mismatches with receiving teams before putaway, keeping system orders closed and inventory records current.
- Track damaged, [short-dated], and slow-moving stock, logging write-offs with reasons and quantities so reorder and store-allocation decisions reflect true available inventory.
- Prepare daily KPI reports tracking inventory accuracy, fulfillment rate, and shipping performance, highlighting recurring discrepancy patterns for corrective action.
- Coordinate weekly interbranch shipment documentation and backorder communications, flagging stock shortfalls early so replenishment plans adjust before stores run out.

---

## Data & Operations Analyst — Northeastern University Vancouver, BC | Jan 2026 – August 2026

- Identified and corrected roughly $120K CAD of incorrectly applied tax on campus supply orders by auditing MySQL cost-calculation queries, finding that tax-exempt grocery items were being charged Vancouver's 12% tax, and fixing the pricing logic and affected records.
- Restructured item categorization in the operations MySQL database, adding distinct categories for grocery (dairy, non-dairy, food items), kitchen equipment, and furniture, which simplified report queries and enabled reliable category-level spend reporting.
- Cut Power BI report refresh time by 13% by refactoring DAX measures and calculated columns against the new category schema, replacing convoluted query logic with direct column references.
- Managed a student records database of 9,000+ active students, maintaining data accuracy and integrity to support operations reporting and daily workflows.
- Translated requirements from daily operations meetings into MySQL queries and report updates supporting day-to-day ordering and reporting decisions.

---

## Software Developer — Vault AI Vancouver,BC | Jun 2025 – Dec 2025

- Architected an AI-powered client intake portal for private credit firms, enabling natural-language analytics on financial data and automated extraction from unstructured PDFs, built on Supabase and serverless Edge Functions for real-time processing.
- Engineered an autonomous Due Diligence Agent that orchestrates multi-source web research to synthesize credit risk and legal compliance into production-ready PDF reports.
- Designed a Multi-Company Financial Comparison Agent to benchmark fiscal performance across entities, reducing manual comparison effort by 60%.
- Built secure RAG pipelines over 100+ confidential documents with vector retrieval, ensuring enterprise-grade data privacy and reliable grounding for complex inquiries.
- Fine-tuned Llama models with QLoRA on domain-specific terminology, improving answer accuracy by 15% on internal evaluations.
- Engineered a unified text-to-speech playback controller in React that streams and cancels audio across 4 providers (browser SpeechSynthesis, OpenAI, ElevenLabs, and local Piper/ONNX in-browser inference), using MediaSource Extensions and AbortController for chunked streaming and clean teardown.
- Designed an event-driven synchronization layer using browser CustomEvents (STOP_TTS_PLAYBACK, TTS_PLAYBACK_STARTED/ENDED) to coordinate playback state across independent chat components and guarantee cleanup on unmount, eliminating overlapping-audio bugs.
- Built a runtime theming system with CSS custom properties and a React context, letting users switch light/dark themes and custom logos instantly without a page reload, and removed the screen-flicker that occurred on theme change.
- Implemented a global modal-state mechanism that broadcasts open/close events so dropdown menus (agent-type selector, saved prompts, slash commands) close correctly and stop capturing input while a modal is open.
- Rebuilt core chat components (message bubbles and inline message editing) with an auto-resizing textarea and dynamic message alignment, improving the in-place editing experience and readability.
- Added per-response PDF export with jsPDF, enabling users to download any individual chat answer as a formatted document.
- Shipped per-workspace AI model selection with a specialist-model dropdown and tooltips, and fixed a race condition that left text generation running when a user switched models mid-stream.
- Extended Node/Express endpoints and system-settings models to persist appearance and TTS configuration consumed by the React client, working across the full stack.
- Improved workspace navigation by adding search-by-workspace, refining sidebar layout and scroll behavior, and reworking thread option menus for consistency.
- Implemented client-side password validation and refined the multi-user authentication and account-management modals.
- Optimized responsive layout and accessibility across chat, settings, and onboarding views (input alignment, scroll containers, dimension fixes) to support varied screen sizes.
- Collaborated on a 3-service monorepo (React/Vite frontend, Node/Express API, document collector) alongside a 7-developer team, contributing 79 commits through a Git feature-branch and pull-request workflow.
- Shipped production features using AI-assisted development tools (Claude Code) as a daily engineering practice — agentic coding sessions for feature implementation, refactoring, and test scaffolding — reviewing and validating all generated code before merge. [Confirm scope: also GitHub Copilot at Vault AI?]

---

## Software Developer — Dots N Key, Surat, India | Dec 2022 – Jul 2024

> Source: B.Tech Industrial Training report + presentation (UTU/CGPIT, May 2023). Percentages in [brackets] are estimates to confirm before use on a tailored resume; unbracketed counts are verifiable from the project documentation. Note: this is the same POS platform (SONAR POS) referenced in the Dots N Key entry — do not list both on the same resume without reconciling.

- Reduced manual data entry in a retail POS used across 150+ store locations by ~60% by replacing hardcoded forms with metadata-driven dynamic UIs — field definitions stored in MySQL, served via stored procedures through Node.js APIs, and rendered at runtime in React
- Eliminated inline SQL from the application layer (100% of item, supplier, and count-session queries) by implementing all CRUD operations as MySQL stored procedures exposed through Node.js REST APIs, improving query reusability and security
- Cut item-onboarding time for store admins by ~40% by building a 6-step item-creation wizard (info → details → pricing → inventory → images → locations) with per-variation pricing, promo scheduling, commission overrides, and a 5-slot cumulative tax engine computed server-side
- Enabled store-specific merchandising without code changes by building a dynamic custom-field engine for supplier records — admins configure field types (file/dropdown/text), validation, receipt visibility, and per-location scoping through the UI
- Accelerated physical stock audits by ~70% by building an inventory-count module with barcode-scan lookup, Excel bulk import/export, server-calculated count valuations, and resumable count sessions that reconcile live stock on close
- Reduced barcode label waste by ~30% by adding configurable label-sheet PDF generation with saved presets, zero-fill numbering, and a skip-used-labels option for partially consumed sticker sheets
- Improved inventory accuracy by ~25% by implementing per-location reorder/replenish thresholds, days-to-expiration tracking, and damaged-goods logging with reasons and quantity adjustments
- Boosted query performance by 60% on the SONAR POS platform by leading the full MySQL to AWS RDS migration, eliminating single-point-of-failure risk and unlocking production-grade scalability for high-traffic retail operations.

**Technologies:** React.js, Node.js, MySQL (stored procedures), REST APIs, JavaScript (ES6), HTML5, CSS3, Bootstrap, jQuery, AJAX, Visual Studio Code, Agile/Scrum

---

## Software Developer — Unistar Softech Private Ltd., Bardoli, India | May 2022 – Nov 2022

- Engineered full-stack dashboards, backend services, and role-based access control for multi-user enterprise operations.
- Delivered real-time operational visibility by building 14 interactive PHP/HTML/MySQL dashboards for 12+ stakeholders, replacing spreadsheet-based reporting and cutting report turnaround by 40%.
- Sped up backend processing by 30% by refactoring Node.js scripts and tuning database queries, cutting report generation time and clearing delays in business-critical data delivery.
- Hardened application security by implementing Role-Based Access Control (RBAC) with 21 role tiers and integrating 45+ third-party task-orchestration APIs, cutting cross-team handoff delays by 23% in multi-user environments.
