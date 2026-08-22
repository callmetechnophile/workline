# Workline Frontend Design Audit

**Audit Date**: 2026-08-23  
**Auditor**: UI/UX & Frontend Lead  
**Scope**: `frontend/src/**/*.{tsx,ts,css}`, `frontend/tailwind.config.*`, `DESIGN.md`

---

## 1. Executive Summary

This audit evaluates the Workline frontend against the **Workline Design System** specification and the Stripe visual reference principles. It classifies design inconsistencies across visual tokens, typography, spacing, component styling, engineering status indicators, and accessibility.

---

## 2. Findings Classification

### CRITICAL (Functional or Accessibility Impairments)

| Finding ID | Component / Area | Description | Resolution Status |
| :--- | :--- | :--- | :--- |
| **AUDIT-C01** | Status Representation | Engineering statuses (PASS, FAIL, UNKNOWN) previously relied primarily on color text spans without standardized icons or contrast tokens. | **RESOLVED** via `EngineeringStatusBadge` with dedicated semantic CSS tokens, WCAG AA contrast, and icons. |
| **AUDIT-C02** | Lockfile & Build Ambiguity | Extraneous `frontend/package-lock.json` caused multiple lockfile warnings during Next.js Turbopack inference. | **RESOLVED** by consolidating single canonical `package-lock.json` at repository root. |

### HIGH (Token Inconsistencies & Hardcoded Values)

| Finding ID | Component / Area | Description | Resolution Status |
| :--- | :--- | :--- | :--- |
| **AUDIT-H01** | Arbitrary Hex Colors | Direct usage of ad-hoc hex values (`#0d253d`, `#10b981`, `#06b6d4`) inside components rather than CSS variables. | **RESOLVED** by defining standard palette in `globals.css` and `DESIGN.md` using `--surface`, `--border`, `--primary`, `--status-*`. |
| **AUDIT-H02** | Tabular Figures in Tables | Numerical values in BOM, power analysis, and pin tables lacked explicit tabular figure font features. | **RESOLVED** by adding `.font-tabular` / `font-variant-numeric: tabular-nums` to engineering tables. |

### MEDIUM (Typography & Radius Drift)

| Finding ID | Component / Area | Description | Resolution Status |
| :--- | :--- | :--- | :--- |
| **AUDIT-M01** | Inconsistent Border Radii | Mix of `rounded-sm`, `rounded-lg`, `rounded-xl`, and `rounded-2xl` without clear token hierarchy. | **RESOLVED** by establishing standard radii scale (`xs`: 3px, `sm`: 4px, `md`: 6px, `lg`: 8px, `xl`: 12px, `pill`: 9999px). |
| **AUDIT-M02** | Deprecated Middleware File | `src/middleware.ts` logged deprecation warnings in Next.js 16. | **RESOLVED** by migrating to `src/proxy.ts` convention. |

### LOW (Cosmetic Polish & Micro-interactions)

| Finding ID | Component / Area | Description | Resolution Status |
| :--- | :--- | :--- | :--- |
| **AUDIT-L01** | Reduced Motion Support | Keyframe scanlines and glow animations did not explicitly check `prefers-reduced-motion`. | **RESOLVED** by adding `@media (prefers-reduced-motion: reduce)` rules in `globals.css`. |
| **AUDIT-L02** | Technical Metric Display | Engineering parameters and units lacked a uniform label-value-unit component structure. | **RESOLVED** by creating `MetricDisplay.tsx`. |

---

## 3. Remediation Checklist

- [x] Create centralized `DESIGN.md` specification with Workline Design Rules.
- [x] Standardize CSS variables in `globals.css` covering dark mode and light mode.
- [x] Create `EngineeringStatusBadge` for PASS, FAIL, WARNING, RUNNING, PENDING, BLOCKED, UNKNOWN, MOCKED, NOT_CONFIGURED.
- [x] Create `MetricDisplay` for technical data density.
- [x] Standardize engineering tables with tabular figures.
- [x] Eliminate deprecated Next.js 16 conventions.
- [x] Run full TypeScript typecheck, ESLint, and Next.js production build without regressions.
