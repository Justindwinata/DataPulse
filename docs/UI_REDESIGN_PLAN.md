# DataPulse UI Redesign Plan

Date: 2026-07-16
Branch: codex/professional-ui-redesign

## Product Positioning

DataPulse is a deterministic CSV and Excel cleaning studio for students, junior analysts, data learners, and developers who need transparent table cleanup before analysis. The redesign should feel like a focused local data-preparation workspace, not a broad marketing page or generic dashboard.

Core promise:

- Validate local tabular files.
- Inspect structure and data quality issues.
- Choose deterministic cleaning rules.
- Preview changes before export.
- Download cleaned CSV output.
- Generate HTML reports.
- Save local metadata-only sessions and reusable rule templates.

The UI must preserve the product boundary: no AI cleaning, no original file storage, no cloud sync, no authentication, no XLSX export, and no deployment claim.

## References Studied

1. OpenRefine documentation
   - Reference: https://openrefine.org/docs/manual/facets
   - Useful idea: data cleaning is easiest to trust when users can inspect patterns, counts, filters, and transformations directly.
   - Adaptation: keep issue cards, column profiles, and rule effects visible next to the workflow instead of hiding them behind a wizard.

2. Microsoft Power Query
   - Reference: https://learn.microsoft.com/en-us/power-query/power-query-what-is-power-query
   - Useful idea: users preview data and select transformations from clear UI controls.
   - Adaptation: make the stage sequence feel like an applied workflow while still letting users choose rules manually.

3. Tableau Prep Builder
   - Reference: https://help.tableau.com/current/prep/en-us/prep_clean.htm
   - Useful idea: profile, clean, and result views should stay close enough that users understand the effect of each operation.
   - Adaptation: strengthen the relationship between issue summary, selected rules, rule effects, and cleaned preview.

4. Carbon Design System data table guidance
   - Reference: https://carbondesignsystem.com/components/data-table/usage/
   - Useful idea: data tables need explicit titles, descriptions, consistent row/header density, and enough width to avoid cramped analysis.
   - Adaptation: improve table containers, headers, overflow behavior, and table context copy for raw previews, profiles, saved sessions, and templates.

5. GOV.UK Design System error summary guidance
   - Reference: https://design-system.service.gov.uk/components/error-summary/
   - Useful idea: errors should be clear, task-local, recoverable, and accessible.
   - Adaptation: use consistent status panels for errors, backend-unavailable states, upload validation, and form validation without relying on color alone.

6. Metabase product pages
   - Reference: https://www.metabase.com/product/business-intelligence
   - Useful idea: trustworthy analytics tools use calm copy, direct actions, and visible governance or limitation language.
   - Adaptation: keep DataPulse copy honest and demo-friendly while reducing milestone-heavy text in the first viewport.

7. Retool admin panel pages
   - Reference: https://retool.com/use-case/admin-panels
   - Useful idea: internal data tools rely on durable shell structure, tables, forms, and compact action groups more than decorative hero sections.
   - Adaptation: make Workflow, History, and Templates feel like core product areas with clear action hierarchy.

## Current Weak Areas

- Hero takes too much vertical space before the real workflow.
- Navigation lacks a strong app-shell feel and active affordance.
- Several panels share the same visual weight, so upload, report, history, and template actions compete.
- Tables are functional but need more professional density, headers, scroll behavior, and action grouping.
- Rule cards are useful but need clearer selected, recommended, restored, and template states.
- Error/success/loading states exist but need one consistent presentation language.
- The first viewport still references DP milestones instead of product value.
- `/cleaning/capabilities` is stale and should reflect implemented workflow status.
- Deploy readiness needs `.env.example`, CORS documentation, and README run/build/test clarity.

## Design Direction

- App character: calm, technical, trustworthy, compact, and demo-ready.
- Layout: workflow-first app shell with concise product intro and visible primary action.
- Palette: neutral graphite text, off-white background, white surfaces, deep teal primary actions, amber warnings, red errors, green success.
- Radius: 6-8px for controls and panels.
- Typography: compact SaaS scale with strong numeric hierarchy but no oversized viewport-scaled type.
- Cards: use for bounded tools, repeated items, and detail panels only.
- Tables: scroll inside bordered containers, keep headers readable, make row actions compact.
- Forms: visible labels, helper text, clear disabled/loading states.
- Accessibility: semantic headings, focus-visible states, labels, `aria-live` where status changes matter, and no color-only status communication.

## Implementation Plan

1. Add design tokens and global UI foundations in CSS.
2. Polish app shell, hero, navigation, stage strip, and first-viewport workflow entry.
3. Redesign core workflow panels: upload, validation, structure, quality, rules, cleaning preview, export, report, and save session.
4. Polish secondary areas: history, saved-session detail, templates, and forms.
5. Improve responsive behavior for 1280px, 1024px, 768px, 390px, and 320px widths.
6. Fix stale capabilities metadata and add focused backend test coverage.
7. Add `.env.example` and README documentation for local run, build, test, environment variables, and limitations.
8. Run frontend tests, frontend build, backend tests, and `git diff --check`.

## Non-Goals

- No backend rewrite.
- No new product claims.
- No authentication, cloud database, payment, AI, or external integrations.
- No copyrighted brand assets or copied UI.
- No actual deployment unless explicitly requested later.
