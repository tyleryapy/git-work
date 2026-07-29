# Payoneer slide style tokens

Condensed from **Master PPT Template - Standard.pptx** (Branding Assets / Grid System / theme `3_Payoneer Theme`). Full reference: [DESIGN_STYLE_GUIDANCE.md](DESIGN_STYLE_GUIDANCE.md). Extraction cache: [reference/extraction.json](reference/extraction.json).

Prefer project `DESIGN_STYLE_GUIDANCE.md` / Standard `.pptx` when present.

## Canvas

| Property | Value |
|----------|-------|
| Aspect | 16:9 |
| Recommended CSS size | `1920px × 1080px` |
| PPT size | 26.67 in × 15.00 in |
| Background | `#FFFFFF` |
| Stage padding (CSS) | `54px 106px 72px` |

## Grid and margins

| Property | Value |
|----------|-------|
| Content left margin | ~5.5% (~0.89 in / 812,800 EMU / ~106px) |
| Title top | ~5% from top |
| Content start | ~15% from top (below title) |
| Title placeholder width | ~24.9 in |
| Align | Titles, subjects, tables, and charts to horizontal content grid |
| Slide number | bottom-right, `#808080` |
| Footnote | bottom-left, `*`-prefixed |
| Logo (master) | bottom-left (optional in HTML inserts) |

## Colors

| Role | Hex |
|------|-----|
| Text primary | `#000000` |
| Text secondary / footnotes / slide # | `#808080` |
| Background | `#FFFFFF` |
| Muted fill / baseline bars | `#B1B1B0` |
| Accent 1 (primary) | `#0092F4` |
| Accent 2 (positive status) | `#20DC86` |
| Accent 3 (warning) | `#DFD902` |
| Accent 4 (process) | `#F7931E` |
| Accent 5 (negative) | `#FF4800` |
| Accent 6 | `#DA54D8` |
| Hyperlink | `#0563C1` |
| Followed link | `#954F72` |
| Table borders | `#E3E3E3` |
| Highlight callout | `#FFE832` |
| Midnight blue (HTML report headers only) | `#002373` |
| Dark cover panel (shaded covers only) | `#1E1E28` |
| **Never output** | `#F26B43` (internal guides only) |

Chart series cycle accent1→accent6. Default primary series: `#0092F4`.

### Diagram tint ladder (Standard Branding Assets)

| Family | Base | Mid | Light |
|--------|------|-----|-------|
| Blue | `#0092F4` | `#5FBFFF` | `#95D4FF` |
| Green | `#20DC86` | `#78EBB7` | `#A5F2CF` |
| Coral | `#FF9166` | `#FFB699` | `#FBC7B2` |
| Gray | `#B1B1B0` | `#BFBFBF` | — |

Shade steps for dark panels: 80% / 60% / 40% / 20%.

### Status semantics

| Status | Hex | Class hint |
|--------|-----|------------|
| Positive / complete | `#20DC86` | `.status-pos` |
| Warning / attention | `#DFD902` | `.status-warn` |
| Risk / negative | `#FF4800` | `.status-neg` |

## Typography

**Stack:** `"Avenir Next LT Pro", "Avenir Next", "Segoe UI", Arial, system-ui, sans-serif`

Titles / section headers / subjects use Demi / `font-weight: 600`. Body uses Regular / `400`.

| Element | Size (template pt) | CSS at 1920×1080 | Weight | Color |
|---------|-------------------:|------------------:|--------|-------|
| Slide title | 65 pt | ~86px | 600 | `#000` |
| Section header / subject | 40–65 pt | ~53–86px | 600 | `#000` |
| Body L1 | 40 pt | ~53px | 400 | `#000` |
| Body L2 / tagline | 30 pt | ~40px | 400 | `#000` |
| Body L3–5 | 24 pt | ~32px | 400 | `#000` |
| Quote body | ~48–64 pt | ~64–86px | 600 | `#000` |
| Quote attribution | 30 pt | ~40px | 600 | `#808080` |
| Table header | 24 pt | ~32px | 700 | `#000` |
| Table body | 20 pt | ~27px | 400 | `#000` |
| Footnote | 16 pt | ~21px | 400 | `#808080` |
| Slide number | 20 pt | ~27px | 400 | `#808080` |
| Chart axis | 22 pt | ~29px | 400 | ~65% gray |
| Chart data label | 20–28 pt | ~27–37px | 600 | `#fff` on bar |
| Caption | 18 pt | ~24px | 400 | `#000` / `#808080` |

Scale: `css_px ≈ pt × 1.333` at 1920×1080. Prefer fixed px inside a fixed stage.

## Bullets

| Level | Character | Size | Spacing after |
|-------|-----------|------|---------------|
| 1 | `•` | body L1 (40 pt) | 18 pt |
| 2 | `–` | body L2 (30 pt) | 24 pt |
| 3 | `>` | body L3 (24 pt) | 9 pt |

Line spacing: 100%. First-level indent ≈ 0.49 in.

## Layouts

### Core (master layouts)

- Front Cover - Light B
- Big title and Content - Light (agenda: `#` \| Agenda Item \| Owner)
- Divider Cover - Light B
- Numbered Divider - Light
- Big text / Quotes / Testimonials - Light A
- Big text / Quotes / Testimonials - Light B
- Title only
- Titles and Content A
- Titles and 3 highlights
- Titles, Table and Status
- Titles, 2 Content boxes and paragraphs
- Titles, 3 Content boxes and paragraphs
- Titles and 4 text boxes with content inside

### Extended (Standard patterns)

- Icon cards (2–4 equal cards + optional icon)
- Image / mockup layouts
- Timeline / process steps
- Comparison grids (2–3 columns)
- Shaded headline-only covers / chapter starts

## Element rules

**Title:** top-left, Demi, black, left-aligned; prefer one line (max two).

**Subject / tagline:** directly under title, 30–40 pt; Demi when used as section subject label.

**Quote:** opening `❝` top-right of block; closing `❞` bottom-right; attribution muted gray below.

**Agenda table:** header bold 24 pt; body 20 pt; row separators `#E3E3E3`.

**Tables:** header row bold; banded rows; cell padding ~0.08 in; borders `#E3E3E3`; status column uses semantic greens/yellows/red-oranges.

**Diagrams:** strokes `#0092F4`; secondary `#B1B1B0`; simple arrow heads; no drop shadows; rounded rects with no/light tint fill; connectors ~35% gray; labels short (L2/L3).

**Icons:** flat line or fill in accent1/black; consistent size per slide (~48–72px CSS); no shadows; optional on equal-height cards with short Demi label.

**Photos / mockups:** grid-aligned rectangular crop; white or soft shaded slide; caption 18 pt; no heavy filters or neon overlays.

**Footnote:** `*` prefix, 16 pt muted, bottom-left.

**Slide number:** 20 pt `#808080`, bottom-right.

## Charts

| Type | Rules |
|------|--------|
| Bar (default) | Clustered columns; hide chart title; category axis on; value axis usually off; labels inside end, white Demi; gap 34–51; baseline/comparison `#B1B1B0` |
| Line | Stroke `#0092F4` 2–3px; no/small markers; no 3D |
| Pie | accent1–6; no 3D/explosion; percent labels ~20 pt |
| Waterfall | totals `#B1B1B0`; positive `#0092F4`; negative `#FF4800`; connectors ~35% gray |
| Stacked | composition over time; legend above chart; consistent series colors |

## Forbidden

- Non-theme decorative colors / purple AI defaults
- 3D effects, text drop shadows, non-template fonts
- Design-guide `#F26B43`
- Midnight blue `#002373` as chart series or full-slide fill
- Circles/orbs behind content-heavy slides
- Invented PII or metrics
