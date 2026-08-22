---
version: 1.0.0
name: Workline Design System
description: A precision-engineered design system for Workline — an AI-powered hardware and systems engineering execution platform. Using Stripe's visual rhythm, typographic hierarchy, and token discipline as a base visual reference, Workline adapts these principles for data-dense, technical, and mission-critical engineering workflows (Requirements, BOM, PCB, Simulation, PINN, Validation, and Release).
tokens:
  colors:
    background: "#030712"
    background-secondary: "#090d16"
    surface: "#0f172a"
    surface-secondary: "#1e293b"
    surface-tertiary: "#334155"
    border: "#1e293b"
    border-subtle: "#172033"
    border-highlight: "#38bdf8"
    foreground: "#f8fafc"
    foreground-secondary: "#cbd5e1"
    muted: "#64748b"
    muted-foreground: "#94a3b8"
    
    # Primary & Accents
    primary: "#6366f1"
    primary-hover: "#4f46e5"
    primary-deep: "#4338ca"
    primary-foreground: "#ffffff"
    accent-cyan: "#06b6d4"
    accent-cyan-hover: "#0891b2"
    accent-blue: "#3b82f6"
    accent-purple: "#8b5cf6"
    accent-amber: "#f59e0b"
    accent-emerald: "#10b981"
    accent-rose: "#f43f5e"

    # Engineering Status System
    status-pass: "#10b981"
    status-pass-bg: "rgba(16, 185, 129, 0.12)"
    status-pass-border: "rgba(16, 185, 129, 0.3)"
    
    status-fail: "#ef4444"
    status-fail-bg: "rgba(239, 68, 68, 0.12)"
    status-fail-border: "rgba(239, 68, 68, 0.3)"
    
    status-warning: "#f59e0b"
    status-warning-bg: "rgba(245, 158, 11, 0.12)"
    status-warning-border: "rgba(245, 158, 11, 0.3)"
    
    status-running: "#06b6d4"
    status-running-bg: "rgba(6, 182, 212, 0.12)"
    status-running-border: "rgba(6, 182, 212, 0.3)"
    
    status-pending: "#6366f1"
    status-pending-bg: "rgba(99, 102, 241, 0.12)"
    status-pending-border: "rgba(99, 102, 241, 0.3)"
    
    status-blocked: "#a855f7"
    status-blocked-bg: "rgba(168, 85, 247, 0.12)"
    status-blocked-border: "rgba(168, 85, 247, 0.3)"
    
    status-unknown: "#64748b"
    status-unknown-bg: "rgba(100, 116, 139, 0.12)"
    status-unknown-border: "rgba(100, 116, 139, 0.3)"
    
    status-mocked: "#d97706"
    status-mocked-bg: "rgba(217, 119, 6, 0.12)"
    status-mocked-border: "rgba(217, 119, 6, 0.3)"
    
    status-not-configured: "#475569"
    status-not-configured-bg: "rgba(71, 85, 105, 0.12)"
    status-not-configured-border: "rgba(71, 85, 105, 0.3)"

  typography:
    font-sans: "var(--font-geist-sans), 'Inter', system-ui, -apple-system, sans-serif"
    font-mono: "var(--font-geist-mono), 'JetBrains Mono', 'Fira Code', monospace"
    display-xl:
      fontSize: "40px"
      fontWeight: "300"
      lineHeight: "1.15"
      letterSpacing: "-0.96px"
    display-lg:
      fontSize: "32px"
      fontWeight: "300"
      lineHeight: "1.2"
      letterSpacing: "-0.64px"
    heading-lg:
      fontSize: "24px"
      fontWeight: "500"
      lineHeight: "1.25"
      letterSpacing: "-0.32px"
    heading-md:
      fontSize: "18px"
      fontWeight: "500"
      lineHeight: "1.35"
      letterSpacing: "-0.18px"
    heading-sm:
      fontSize: "15px"
      fontWeight: "600"
      lineHeight: "1.4"
      letterSpacing: "0px"
    body-lg:
      fontSize: "15px"
      fontWeight: "400"
      lineHeight: "1.5"
    body-md:
      fontSize: "13.5px"
      fontWeight: "400"
      lineHeight: "1.45"
    body-mono:
      fontFamily: "var(--font-geist-mono), monospace"
      fontSize: "12.5px"
      fontWeight: "400"
      lineHeight: "1.4"
      fontFeature: "tnum"
    caption:
      fontSize: "11.5px"
      fontWeight: "400"
      lineHeight: "1.35"
    micro:
      fontSize: "10px"
      fontWeight: "600"
      letterSpacing: "0.08em"
      textTransform: "uppercase"

  spacing:
    xxs: "2px"
    xs: "4px"
    sm: "8px"
    md: "12px"
    lg: "16px"
    xl: "24px"
    2xl: "32px"
    3xl: "48px"

  radii:
    xs: "3px"
    sm: "4px"
    md: "6px"
    lg: "8px"
    xl: "12px"
    pill: "9999px"

  shadows:
    sm: "0 1px 2px 0 rgba(0, 0, 0, 0.4)"
    md: "0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3)"
    lg: "0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -4px rgba(0, 0, 0, 0.4)"
    glow-cyan: "0 0 20px rgba(6, 182, 212, 0.2)"
    glow-indigo: "0 0 20px rgba(99, 102, 241, 0.2)"
---

# Workline Design System Specification

## 1. Executive Summary & Purpose

The **Workline Design System** defines the unified visual, interaction, and technical architecture for the Workline platform.

Workline is an **AI-powered hardware and systems engineering execution platform**. It orchestrates the end-to-end lifecycle of technical product development:
- **Research**: Datasheet extraction, literature parsing, contradictory constraint detection.
- **Planning & Requirements**: Structured requirements management, dimensional tolerance validation.
- **Components & Procurement**: Intelligent BOM generation, multi-supplier price optimization, part obsolescence risk assessment.
- **PCB & Physics Simulation**: DRC geometric checking, thermal conduction modeling, PINN neural surrogate solvers.
- **Verification & Release**: Deterministic verification gates, tamper-evident `.wlipjt` project packaging.

The design system merges **Stripe's visual clarity, geometric precision, and typographic restraint** with an **engineering-grade, data-dense control center aesthetic**.

---

# Workline Design Rules

1. **Workline is NOT a Stripe clone**: We do not copy Stripe branding, logos, or marketing narratives.
2. **Stripe design principles are used as visual reference**: Tight typographic hierarchy, subtle hairline borders, and disciplined spacing serve as our baseline benchmark for visual polish.
3. **Workline engineering semantics take precedence**: Precision, mathematical clarity, unit notation, and high information density override decorative whitespace.
4. **Components must use design tokens**: Hardcoded hex colors, arbitrary padding, and ad-hoc border radii are strictly forbidden.
5. **No arbitrary colors**: All UI surfaces, text tiers, borders, and indicators must reference semantic CSS variables (`--background`, `--surface`, `--border`, `--primary`, `--status-*`).
6. **No arbitrary spacing**: Layouts must adhere to the 4px / 8px / 12px / 16px / 24px / 32px spacing scale.
7. **Status cannot rely only on color**: Every engineering status (PASS, FAIL, WARNING, RUNNING, PENDING, BLOCKED, UNKNOWN, MOCKED, NOT_CONFIGURED) MUST include an icon, a text label, and an accessible contrast token.
8. **Engineering data takes priority over decoration**: Monospace numbers (`font-mono`, `tnum`), clear technical units (`3.3 V`, `2.0 A`, `10 kΩ`), and table scanability take precedence over oversized illustrations.
9. **Accessibility is mandatory**: WCAG AA color contrast, full keyboard navigability, clear focus indicators (`--ring`), and semantic HTML elements are non-negotiable.
10. **Motion must communicate state**: Animations are permitted exclusively for state transitions, pipeline progression, and loading indicators. Constant ambient motion is prohibited, and `prefers-reduced-motion` must be respected.

---

## 2. Visual Architecture & Theme Polarity

### Dark Mode (Default)
Workline is engineered primarily as a dark-mode workstation interface. Deep zinc/slate canvases (`#030712`, `#0f172a`) minimize eye strain during extensive CAD, BOM, and simulation analysis sessions.

### Light Mode (Supported)
Light mode maps high-contrast slate surfaces (`#f8fafc`, `#ffffff`) with crisp borders (`#cbd5e1`, `#94a3b8`) for clean daylight visibility without losing component boundaries.

---

## 3. Engineering Status Taxonomy

| Status | Color Token | Icon | Semantic Meaning |
| :--- | :--- | :--- | :--- |
| **PASS** | `--status-pass` (`#10b981`) | `CheckCircle2` | Requirement fully satisfied with verified numerical evidence |
| **FAIL** | `--status-fail` (`#ef4444`) | `XCircle` | Constraint violation or DRC geometry conflict |
| **WARNING** | `--status-warning` (`#f59e0b`) | `AlertTriangle` | Derating threshold reached or potential thermal/current bottleneck |
| **RUNNING** | `--status-running` (`#06b6d4`) | `Loader2` (spin) | Solver active, agent executing, or live query in progress |
| **PENDING** | `--status-pending` (`#6366f1`) | `Clock` | Queued in pipeline or waiting for prerequisite task |
| **BLOCKED** | `--status-blocked` (`#a855f7`) | `Ban` | Dependency unmet or human approval gate required |
| **UNKNOWN** | `--status-unknown` (`#64748b`) | `HelpCircle` | Insufficient datasheet evidence to confirm compliance |
| **MOCKED** | `--status-mocked` (`#d97706`) | `ShieldAlert` | Synthetic or fallback data utilized for staging validation |
| **NOT_CONFIGURED** | `--status-not-configured` (`#475569`) | `AlertOctagon` | Parameter uninitialized in current project scope |

---

## 4. Typography Scale & Technical Data Density

Workline uses **Geist / Inter** for primary UI text and **Geist Mono / JetBrains Mono** for all technical metrics, code, part numbers, and units.

- **Display Headline**: 32px – 40px, weight 300, tracking -0.64px to -0.96px.
- **Section Heading**: 18px – 24px, weight 500, tracking -0.2px.
- **Subheading**: 15px, weight 600.
- **Body UI**: 13.5px, weight 400, line-height 1.45.
- **Technical/Monospace**: 12.5px, weight 400, tabular numbers (`font-variant-numeric: tabular-nums`).
- **Micro Eyebrows & Badges**: 10px – 11px, weight 600, uppercase, tracking +0.08em.

---

## 5. Workline Component Standards

1. **`Button`**: Pill (`rounded-full`) or subtle radius (`rounded-md`), consistent padding (`px-3 py-1.5` or `px-4 py-2`), distinct hover/active states with accessible focus rings.
2. **`Card / GlassPanel`**: Subtle backdrop blur, 1px hairline border (`border-zinc-800`), dark canvas fill (`bg-slate-900/60` or `bg-zinc-950/80`).
3. **`BOMTable & ProcurementTable`**: Compact rows (36px–40px), right-aligned numerical quantities and currencies, monospace part numbers, instant filter/search inputs.
4. **`DatasheetPanel & DocumentViewer`**: Side-by-side PDF / Markdown viewer with bounding box highlights and page provenance badges.
5. **`PowerAnalysis & ThermalMap`**: Real-time power tree diagrams, thermal risk gauges, and PINN residual loss curves.
6. **`GraphExplorer`**: Interactive canvas for component and requirement knowledge graphs with node inspection drawers.

---

## 6. Accessibility & Responsive Principles

- **Keyboard Traversal**: All interactive controls (buttons, inputs, tabs, modal dialogs) are navigable via `Tab`, `Enter`, `Space`, and arrow keys.
- **Focus Rings**: Universal `focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950`.
- **Responsive Layout**: Desktop-first data density (1200px–1600px grid) with seamless column collapsing on tablet (768px–1024px) and single-column stacked drawers on mobile (<768px).
- **Reduced Motion**: Motion transitions strictly bounded by `@media (prefers-reduced-motion: reduce)`.
