# Stitch UI Adoption Plan

## Package Location

The Stitch UI package was found locally at:

- `/Users/justindwinata/Documents/DataPulse/stitch_datapulse_saas_platform_design.zip`
- `/Users/justindwinata/Downloads/stitch_datapulse_saas_platform_design.zip`

The repository copy is treated as a local design reference only and is ignored by Git. The ZIP was extracted temporarily to:

- `/tmp/datapulse_stitch_inspection/stitch_datapulse_saas_platform_design`

## Files and Screens Found

The ZIP contains four rendered UI concepts plus one design-system document:

- `datapulse/DESIGN.md`
- `datapulse_home/code.html`
- `datapulse_home/screen.png`
- `workspace_analysis_rules/code.html`
- `workspace_analysis_rules/screen.png`
- `session_history/code.html`
- `session_history/screen.png`
- `workflow_templates/code.html`
- `workflow_templates/screen.png`

## Stitch Design Summary

The package presents DataPulse as a modern SaaS data-operations product with:

- A blue/slate enterprise color system
- Inter typography with JetBrains Mono for data values
- A left-side app shell for Workspace, History, Templates, and Reports
- A top workflow stepper for upload, detect, analyze, clean, and export
- Dense dashboard cards for quality score and issue severity
- Scroll-safe data tables with zebra striping and sticky headers
- A right-side rules engine panel
- History list surfaces with quality-score badges and action icons
- Template cards with rule tags and apply actions

## Suitable Concepts to Adopt

- DataPulse blue as the primary action and active-state color
- Slate text palette for a more technical SaaS look
- Compact card borders, subtle shadows, and 4-8px radii
- App shell with persistent navigation anchors
- Workflow stage strip/stepper for the cleaning sequence
- Quality score and issue summary as dashboard cards
- Scroll-contained data tables with mono-style data cells
- Rule cards grouped into recommended and available rules
- Local history as a table-first audit surface
- Workflow templates as reusable rule-set cards/details

## Concepts Rejected or Adjusted

- External CDN dependencies from Stitch HTML are not adopted; DataPulse stays with local React, TypeScript, Vite, and standard CSS.
- Material Symbols are not added as a dependency; current text labels and CSS-based UI affordances remain sufficient.
- Fake Stitch items such as Settings, Profile, Pricing, Admin, Governance, and cloud/team language are not adopted.
- Stitch's "Enterprise Data Ops" positioning is softened because DataPulse is a local portfolio/demo product, not a deployed enterprise service.
- The Stitch right-side rules panel is adapted into the current rule selection flow rather than replacing existing workflow state.
- Screenshot assets from the ZIP are not committed because they are generated references, not production app assets.

## Mapping to DataPulse

| Stitch screen | DataPulse implementation target |
| --- | --- |
| `datapulse_home` | Home/hero area, product value proposition, supported formats, workflow summary, trust/limitations |
| `workspace_analysis_rules` | Upload workspace, stage strip, quality cards, raw/cleaned preview tables, rule selection, export/report/save panels |
| `session_history` | Saved sessions list, detail summary, saved report replay, reuse rules, delete action |
| `workflow_templates` | Templates list, create/edit forms, apply template workflow, template badges |
| `DESIGN.md` | CSS tokens for color, typography, spacing, cards, buttons, tables, badges, and focus states |

## Implementation Plan

1. Extract Stitch design tokens into `frontend/src/styles.css`.
2. Keep the existing React architecture and API clients intact.
3. Improve app shell and navigation while retaining anchor-based access to Workflow, History, and Templates.
4. Redesign home content around deterministic cleaning, local privacy, CSV-first export, and honest Excel limitations.
5. Redesign workspace sections using Stitch-inspired cards, score panels, tables, and rule surfaces.
6. Polish History and Templates sections to feel like SaaS management surfaces.
7. Preserve all existing data flows: upload validation, structure detection, quality profiling, cleaning preview, CSV export, HTML reports, saved sessions, saved report replay, restored rules, and workflow templates.
8. Validate with unit tests, build checks, and manual workflow QA using `dataset/dirty_cafe_sales.csv`.

## Risks

- The current app is a single-page workflow with many states; aggressive layout changes could break tests or hide existing actions.
- The Stitch workspace assumes a split dashboard with fake data; DataPulse must render real API responses and empty/loading/error states.
- The ZIP includes generated HTML and screenshots that should not be copied wholesale into the app.
- A side navigation can reduce width for tables, so responsive table wrappers must remain scroll-safe.

## Limitations

- This adoption changes visual and UX presentation only.
- No AI/LLM cleaning, authentication, cloud sync, deployment, PDF export, XLSX export, or original uploaded file storage is added.
- The redesign should look deployment-ready in appearance, but it does not implement deployment.

## Asset Decision

No Stitch screenshots, generated HTML, external images, CDN scripts, or package artifacts will be committed. The design is used as a reference for local CSS and React layout improvements.
