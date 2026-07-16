# DataPulse UI/UX Redesign Audit

Date: 2026-07-16
Branch: codex/professional-ui-redesign
Phase: 1 - Discovery and Audit

## 1. Application Summary

DataPulse is a deterministic CSV and Excel cleaning studio for messy table-like files. It helps users validate uploads, detect table structure, inspect raw previews, profile data quality issues, choose rule-based cleaning transformations, preview cleaned output, export cleaned CSV files, generate standalone HTML cleaning reports, save local cleaning-session history, restore saved rule sets, and manage reusable workflow templates.

The product is intentionally not an AI cleaning tool. Its strongest product promise is transparency: users should see what was detected, choose deterministic rules, and understand what changed before exporting data.

## 2. Target Users

- Students preparing datasets for coursework, portfolio projects, and analysis practice.
- Junior analysts cleaning exported business reports.
- Developers validating CSV or spreadsheet input before import.
- Data learners who need visible, explainable data-preparation steps.

## 3. Technology Stack

- Frontend: React 18, TypeScript, Vite, Vitest, Testing Library, global CSS.
- Backend: Python 3.11+, FastAPI, Pydantic, Uvicorn, Pytest.
- File processing: Python CSV utilities, openpyxl for XLSX, xlrd for compatible XLS.
- Persistence: local SQLite for saved sessions and workflow templates.
- Build/test workflow: root Makefile, frontend npm scripts, backend pytest.
- Current deployment posture: local portfolio/demo application, no production hosting config yet.

## 4. Repository and Git State

- Active branch before audit: main tracking origin/main.
- Working branch created for this work: codex/professional-ui-redesign.
- Remote: https://github.com/Justindwinata/DataPulse.git.
- Last commit at audit start: 1dc1914 fix: improve cleaning report rule labels.
- Working tree at audit start: clean.
- Notable ignored local data: dataset/, backend/data/*.sqlite3, .env files, node_modules, virtualenvs, build outputs.

## 5. Current User Flow

1. User opens the Workflow section.
2. User selects a CSV, TSV, TXT, XLSX, or XLS file.
3. Frontend validates upload metadata through POST /files/validate-upload.
4. User detects structure through POST /files/detect-structure.
5. Excel users choose a sheet before preview/profiling.
6. User profiles data quality through POST /files/detect-quality.
7. User selects deterministic cleaning rules.
8. User generates cleaned preview through POST /files/apply-cleaning-preview.
9. User downloads CSV through POST /files/export-cleaned-csv.
10. User opens live HTML report through POST /files/cleaning-report.html.
11. User can save local session metadata, review history, replay saved HTML reports, restore rules, and create/apply templates.

## 6. Baseline Validation

Commands run during audit:

```bash
cd frontend && npm test -- --run
cd frontend && npm run build
cd backend && .venv/bin/python -m pytest
git diff --check
```

Results:

- Frontend tests: 9 files passed, 78 tests passed.
- Frontend production build: passed.
- Backend tests: 212 passed, 1 Starlette/httpx deprecation warning.
- Whitespace check: passed.

Local app audit:

- FastAPI started on http://127.0.0.1:8000.
- Vite started on http://127.0.0.1:5173.
- Browser console errors/warnings on initial page: none observed.
- Main API smoke checks against demo/messy_sales.csv passed for validation, structure detection, quality profiling, cleaning preview, CSV export, and HTML report generation.

## 7. Current UI/UX Condition

The application is functional and has useful states, but the visual system still feels like a broad portfolio demo page rather than a focused data-cleaning product. The strongest issue is not a single color choice; it is information architecture and interaction density.

Observed strengths:

- Product boundaries are honest and clear: deterministic rules, sample-based previews, no original upload storage.
- Main workflow includes validation, empty, loading, error, success, preview, export, report, save, history, and template states.
- Tables are horizontally scrollable and keyboard focusable.
- Form labels generally exist and controls use native buttons/inputs/selects.
- Backend contracts are strongly tested.

Observed UI/UX issues:

- The hero is oversized for an application workflow. It pushes the real task down and makes the product feel more like a landing page.
- Navigation uses anchor links only and has no clear active state. Workflow, History, and Templates feel like page sections rather than durable product areas.
- The status panel is partially clipped at the default browser width in the observed screenshot, which makes the hero grid feel unbalanced.
- The workflow stage cards add clarity, but they also create another row of cards before the user reaches the actual upload task.
- `App.tsx` is 2,332 lines, so UI states, data fetching, domain copy, and rendering are tightly coupled. This increases redesign risk.
- `styles.css` is 1,122 lines of global selectors. It lacks formal design tokens and makes component-level consistency hard to maintain.
- Many panels share the same card styling, so important actions, reports, history, templates, and generic explanatory sections compete visually.
- The interface relies heavily on text labels and long explanatory copy. It is accurate, but slower to scan than a production tool.
- No icon system is currently used. Important actions such as upload, detect, analyze, export, report, save, and delete are text-only.
- Typography hierarchy is too dramatic in the hero and h2 sections for a workflow-heavy tool.
- Dashboard-like summaries exist, but they need tighter numeric hierarchy, labels, and context.
- Some production-readiness copy still reads as milestone-oriented, for example DP-0012 in the hero, while docs indicate DP-0013 readiness.

## 8. Technical Findings

Important findings:

- `/cleaning/capabilities` appears stale. It reports DP-0001 and claims file upload, parsing, cleaning, export, reports, and saved history are not implemented, although those features now exist and are documented through DP-0013.
- Frontend API clients each define a localhost fallback for `VITE_API_BASE_URL`. This is acceptable for local demos, but deployment needs a documented `.env.example` and production base URL strategy.
- No `.env.example` exists at audit time.
- Backend CORS allows only local Vite origins. Production deployment will need environment-driven allowed origins.
- No lint script exists beyond `git diff --check`.
- No formatter command is configured.
- No accessibility test automation exists.
- No end-to-end or browser regression test exists for the main file-cleaning workflow.
- README is detailed, but deployment guidance is not yet production-ready.

Security/secret audit:

- No obvious API keys, passwords, private keys, tokens, or cloud credentials were found through text search.
- Local SQLite and local datasets are ignored by Git.
- Uploaded source files are not stored permanently by the backend workflow.

## 9. Design References

The redesign should learn from these references without copying their visual identity.

### OpenRefine

Reference: https://openrefine.org/docs/manual/facets

- Relevant pattern: data-cleaning workbench with visible transformations, facets, and explicit operations.
- What to learn: make issue discovery and transformation selection feel inspectable, reversible, and data-first.
- Fit for DataPulse: DataPulse has similar transparency goals, but should be simpler and more guided for students and junior analysts.

### Microsoft Power Query

Reference: https://learn.microsoft.com/en-us/power-query/power-query-what-is-power-query

- Relevant pattern: step-based data transformation workflow.
- What to learn: clear sequence, applied steps, preview-first workflow, and explicit transformation language.
- Fit for DataPulse: DataPulse can borrow the step clarity while staying lighter and local-demo friendly.

### Tableau Prep Builder

Reference: https://help.tableau.com/current/prep/en-us/prep_clean.htm

- Relevant pattern: profile, clean, shape, and review data in a structured preparation flow.
- What to learn: combine data preview, quality indicators, and transformation effects without overwhelming the user.
- Fit for DataPulse: DataPulse already has profile/preview/effects; redesign should make those areas visually connected.

### Carbon Design System Data Table

Reference: https://carbondesignsystem.com/components/data-table/usage/

- Relevant pattern: professional data tables with clear density, alignment, toolbar actions, and row actions.
- What to learn: table hierarchy, restrained borders, predictable actions, and accessible focus states.
- Fit for DataPulse: DataPulse relies heavily on raw preview, column profile, sessions, and templates tables.

### GOV.UK Design System Forms and Error Summary

Reference: https://design-system.service.gov.uk/components/error-summary/

- Relevant pattern: clear labels, direct errors, accessible validation, and visible recovery.
- What to learn: errors should be near the task, human-readable, and keyboard/screen-reader friendly.
- Fit for DataPulse: upload, template forms, report actions, and backend-down states need concise recovery guidance.

## 10. Design Direction

Target character:

- Professional, calm, technical, trustworthy, and efficient.
- More product workspace than marketing page.
- Data-cleaning studio with visible steps, not a generic SaaS dashboard.

Initial design system direction:

- Primary: deep teal for core actions and active states.
- Secondary: neutral graphite/slate for text and structure.
- Accent: restrained amber/copper only for warnings and attention, not as a dominant brand color.
- Background: cool off-white with neutral surfaces.
- Surface: white and near-white panels with light borders.
- Success: green/teal.
- Warning: amber/copper.
- Danger: red.
- Radius: 6-8px for panels/buttons; avoid pill-heavy UI except compact status labels.
- Shadow: minimal and functional; rely more on borders, spacing, and grouping.
- Typography: tighter app scale, no viewport-scaled oversized hero type for workflow screens.
- Spacing: consistent 4/8px scale with denser controls for repeated use.
- Icons: add one consistent icon library only if the existing stack can support it safely; Lucide is a good candidate for upload, table, file, report, save, history, and trash actions.
- Layout: top-level app shell with clearer sections; reduce hero dominance; prioritize the upload/workflow workspace in first viewport.
- Cards: use cards only for repeated items, panels, and bounded tools. Avoid card-on-card layouts.
- Tables: preserve horizontal scroll, improve density, headers, numeric alignment, empty state, and action grouping.
- Forms: visible labels, field-level helper/error text, loading/disabled states, and no loss of user input after recoverable errors.
- Feedback: consistent inline status components for success, error, warning, info, and loading.

## 11. Preserve

- Deterministic cleaning model and backend contracts.
- Local-only saved history and template boundaries.
- CSV-first export.
- Explicit limitations around Excel formatting and sample-based previews.
- Existing backend service layering.
- Existing test coverage and demo datasets.
- Existing API routes unless a stale metadata endpoint is deliberately fixed with tests.

## 12. Recommended Implementation Plan

Phase 2 - Design foundation:

- Introduce CSS design tokens in `:root`.
- Normalize typography, spacing, surfaces, buttons, inputs, status labels, and focus states.
- Add a compact app-shell rhythm that places the main task higher in the viewport.
- Keep behavior unchanged.

Phase 3 - Layout and navigation:

- Refactor navigation into a clearer app header with active/section states where practical.
- Reduce hero dominance and transform the first screen into a workflow-first product workspace.
- Improve mobile navigation and section spacing.

Phase 4 - Core workflow redesign:

- Improve upload panel, validation result, structure preview, quality profile, rule selection, cleaned preview, export/report/save panels.
- Add stronger loading, empty, success, and error presentation without changing API contracts.

Phase 5 - History and templates:

- Improve saved session and template tables, action grouping, detail panels, edit forms, and delete/reuse feedback.

Phase 6 - Responsive/accessibility:

- Validate narrow mobile, tablet, laptop, and desktop layouts.
- Audit heading order, labels, focus, table regions, keyboard navigation, contrast, and action semantics.

Phase 7 - Production readiness:

- Add `.env.example`.
- Document frontend/backend environment variables.
- Make backend CORS configurable for production.
- Fix stale `/cleaning/capabilities` metadata or document its scope.
- Add deployment guidance for suitable platforms.
- Consider a lightweight Dockerfile or platform-specific guide only if it matches the chosen deployment path.

Phase 8 - Final verification:

- Run backend tests, frontend tests, production build, local server smoke tests, browser console check, and manual acceptance checklist.

## 13. Likely Files To Change Later

- `frontend/src/App.tsx`
- `frontend/src/styles.css`
- `frontend/src/api/*.ts` if API base URL handling is centralized
- `frontend/package.json` if an icon library or lint script is added
- `backend/src/datapulse_api/main.py`
- `backend/src/datapulse_api/api/cleaning.py`
- `backend/tests/test_cors.py`
- `backend/tests/test_cleaning_capabilities.py`
- `.env.example`
- `README.md`
- `docs/QA_CHECKLIST.md`
- `docs/SYSTEM_ARCHITECTURE.md`
- `docs/DEPLOYMENT.md` if added

## 14. Phase 1 Risk Assessment

- Redesign risk is moderate because the frontend is concentrated in one large component and one global stylesheet.
- Backend risk is low if API contracts are preserved.
- Deployment risk is moderate because production CORS and environment variable strategy are not finished.
- UX risk is moderate because the current UI is copy-heavy and card-heavy; reducing clutter must not remove important safety explanations.
- Testing risk is low for backend logic but moderate for browser workflows because no end-to-end test currently covers the full upload-to-export path.

## 15. Acceptance Checklist For Later Phases

- Main page opens without console errors.
- Upload validation works for accepted and rejected files.
- Structure detection works for CSV-like files.
- Excel sheet selection remains usable.
- Quality profiling renders issue summary and column profile.
- Rule selection and cleaned preview work.
- CSV export downloads a cleaned file.
- HTML report opens.
- Save session, load history, view detail, delete, saved report replay, and reuse rules work.
- Template create, load, view/edit, apply, and delete work.
- Empty/loading/error/success states are visible and consistent.
- Desktop, tablet, and mobile layouts avoid incoherent overlap and horizontal page overflow.
- Tables remain readable and horizontally scrollable where needed.
- Keyboard focus is visible.
- Production build succeeds.
- No secrets are committed.
