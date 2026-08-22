# Workline Design System

## 1. Design Philosophy

**Workline** is an **AI-powered hardware and systems engineering execution platform**. It powers the transition from natural language or written requirements to fully validated, physics-verified, and procurement-ready engineering packages (`.wlipjt`).

The Workline Design System is built upon three foundational tenets:

1. **Stripe-Level Visual Restraint & Polish**:
   - Thin-weight display typography, crisp 1px hairline borders, subtle gradients, and rhythmic vertical spacing.
2. **Technical & Engineering-Centric Density**:
   - Monospace tabular figures for metrics, standard physical units (`V`, `A`, `W`, `Ω`, `°C`, `Hz`), high information density, and data-rich tables.
3. **Deterministic Semantic Statuses**:
   - Multi-modal state communication (icon + color + text label) ensuring unambiguous status assessment for mission-critical validation gates.

---

## 2. Design Tokens

### Color Palette

| Semantic Token | Dark Mode Value | Light Mode Value | Purpose |
| :--- | :--- | :--- | :--- |
| `--background` | `#030712` | `#f8fafc` | Deep viewport background |
| `--background-secondary` | `#090d16` | `#ffffff` | Navigation and sidebar background |
| `--surface` | `#0f172a` | `#ffffff` | Primary card and panel surface |
| `--surface-secondary` | `#1e293b` | `#f1f5f9` | Inset tables, search bars, nested cards |
| `--surface-tertiary` | `#334155` | `#e2e8f0` | Hover states, active selections |
| `--border` | `#1e293b` | `#cbd5e1` | Standard container hairline borders |
| `--border-subtle` | `#172033` | `#e2e8f0` | Table row dividers |
| `--border-highlight` | `rgba(56, 189, 248, 0.4)` | `rgba(99, 102, 241, 0.4)` | Focus rings and active card borders |
| `--foreground` | `#f8fafc` | `#0f172a` | Primary text |
| `--foreground-secondary` | `#cbd5e1` | `#334155` | Secondary text |
| `--muted-foreground` | `#94a3b8` | `#475569` | Helper labels, captions, metadata |
| `--primary` | `#6366f1` | `#6366f1` | Primary action buttons and CTA accents |
| `--primary-hover` | `#4f46e5` | `#4f46e5` | Button hover state |
| `--accent-cyan` | `#06b6d4` | `#0891b2` | Active solvers, graph nodes, telemetry |

---

## 3. Engineering Status System

Every status indicator must provide **color, icon, and text label** with WCAG AA compliant contrast ratios:

| Status | Text / Border Token | Background Token | Icon | Description |
| :--- | :--- | :--- | :--- | :--- |
| **PASS** | `#10b981` | `rgba(16, 185, 129, 0.12)` | `CheckCircle2` | Parameter satisfies requirement |
| **FAIL** | `#ef4444` | `rgba(239, 68, 68, 0.12)` | `XCircle` | Violation or DRC failure |
| **WARNING** | `#f59e0b` | `rgba(245, 158, 11, 0.12)` | `AlertTriangle` | Derating alert or risk factor |
| **RUNNING** | `#06b6d4` | `rgba(6, 182, 212, 0.12)` | `Loader2` (spin) | Background calculation active |
| **PENDING** | `#6366f1` | `rgba(99, 102, 241, 0.12)` | `Clock` | Queued pipeline execution |
| **BLOCKED** | `#a855f7` | `rgba(168, 85, 247, 0.12)` | `Ban` | Dependency unmet / gate closed |
| **UNKNOWN** | `#64748b` | `rgba(100, 116, 139, 0.12)` | `HelpCircle` | Incomplete data |
| **MOCKED** | `#d97706` | `rgba(217, 119, 6, 0.12)` | `ShieldAlert` | Staging mock data used |
| **NOT_CONFIGURED**| `#475569` | `rgba(71, 85, 105, 0.12)` | `AlertOctagon` | Parameter uninitialized |

---

## 4. Typography Hierarchy

Workline uses `Geist Sans` / `Inter` for general prose and UI chrome, and `Geist Mono` / `JetBrains Mono` for tabular metrics and code.

| Role | Font Size | Weight | Line Height | Tracking | OpenType Features |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display XL** | 40px | 300 | 1.15 | -0.96px | `cv02`, `cv03` |
| **Display LG** | 32px | 300 | 1.20 | -0.64px | `cv02`, `cv03` |
| **Heading LG** | 24px | 500 | 1.25 | -0.32px | - |
| **Heading MD** | 18px | 500 | 1.35 | -0.18px | - |
| **Heading SM** | 15px | 600 | 1.40 | 0.00px | - |
| **Body LG** | 15px | 400 | 1.50 | 0.00px | - |
| **Body MD** | 13.5px | 400 | 1.45 | 0.00px | - |
| **Body Monospace** | 12.5px | 400 | 1.40 | 0.00px | `tnum` (tabular nums) |
| **Caption** | 11.5px | 400 | 1.35 | 0.00px | - |
| **Micro / Eyebrow**| 10px | 600 | 1.15 | +0.08em | uppercase |

---

## 5. Spacing and Radii Scales

### Spacing Scale
- `xxs`: 2px
- `xs`: 4px
- `sm`: 8px
- `md`: 12px
- `lg`: 16px
- `xl`: 24px
- `2xl`: 32px
- `3xl`: 48px

### Radii Scale
- `xs`: 3px (inline tags, micro-badges)
- `sm`: 4px (table cells, small inputs)
- `md`: 6px (buttons, standard inputs)
- `lg`: 8px (cards, modal panels)
- `xl`: 12px (major dashboard widgets)
- `pill`: 9999px (primary action buttons)

---

## 6. Motion & Accessibility Standards

- **State-Driven Motion**: Motion is strictly functional (solver progress bars, modal opacity fades, accordion expansion).
- **Reduced Motion Support**: All CSS transitions and animations are constrained by `@media (prefers-reduced-motion: reduce)`.
- **Keyboard Traversal**: Full tab ordering, visible focus rings (`--ring`), and ARIA roles for status and dialog components.
- **High Information Density**: Tables and metrics maintain compact vertical footprints to maximize visible engineering parameters per screen.
