# Payoneer slide style tokens

Condensed from `DESIGN_STYLE_GUIDANCE.md` / `Master PPT Template - Short.pptx`. Prefer the project file when present.

## Canvas

| Property | Value |
|----------|-------|
| Aspect | 16:9 |
| Recommended CSS size | `1920px × 1080px` |
| Background | `#FFFFFF` |
| Content left margin | ~5.5% (~0.89 in on 26.67 in template) |
| Title top | ~5% from top |
| Content start | ~15% from top (below title) |
| Slide number | bottom-right, `#808080` |
| Footnote | bottom-left, `*`-prefixed |

## Colors

| Role | Hex |
|------|-----|
| Text primary | `#000000` |
| Text secondary / footnotes / slide # | `#808080` |
| Background | `#FFFFFF` |
| Muted fill / baseline bars | `#B1B1B0` |
| Accent 1 (primary) | `#0092F4` |
| Accent 2 | `#20DC86` |
| Accent 3 | `#DFD902` |
| Accent 4 | `#F7931E` |
| Accent 5 (negative) | `#FF4800` |
| Accent 6 | `#DA54D8` |
| Table borders | `#E3E3E3` |
| Highlight callout | `#FFE832` |
| **Never output** | `#F26B43` (internal guides only) |

Chart series cycle accent1→accent6. Default primary series: `#0092F4`.

## Typography

**Stack:** `"Avenir Next LT Pro", "Avenir Next", "Segoe UI", system-ui, sans-serif`

Titles use Demi / `font-weight: 600`. Body uses Regular / `400`.

| Element | Size (template pt) | CSS at 1920×1080 | Weight | Color |
|---------|-------------------:|------------------:|--------|-------|
| Slide title | 65 pt | ~86px | 600 | `#000` |
| Body L1 | 40 pt | ~53px | 400 | `#000` |
| Body L2 / tagline | 30 pt | ~40px | 400 | `#000` |
| Body L3–5 | 24 pt | ~32px | 400 | `#000` |
| Quote attribution | 30 pt | ~40px | 600 | `#808080` |
| Table header | 24 pt | ~32px | 700 | `#000` |
| Table body | 20 pt | ~27px | 400 | `#000` |
| Footnote | 16 pt | ~21px | 400 | `#808080` |
| Slide number | 20 pt | ~27px | 400 | `#808080` |
| Chart axis | 22 pt | ~29px | 400 | ~65% gray |
| Chart data label | 20–28 pt | ~27–37px | 600 | `#fff` on bar |

Scale with `clamp()` only if the slide stage itself scales; prefer fixed px inside a fixed 1920×1080 stage.

## Bullets

| Level | Character | Size |
|-------|-----------|------|
| 1 | `•` | body L1 |
| 2 | `–` | body L2 |
| 3 | `>` | body L3 |

## Layouts

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

## Element rules

**Title:** top-left, Demi, black, left-aligned.

**Tagline:** directly under title, 30–40 pt body.

**Quote:** opening `❝` top-right of block; closing `❞` bottom-right; attribution muted gray below.

**Agenda table:** header bold 24 pt; body 20 pt; row separators `#E3E3E3`.

**Diagrams:** strokes `#0092F4`; secondary `#B1B1B0`; simple arrow heads; no drop shadows; rounded rects with no/light fill.

## Charts

| Type | Rules |
|------|--------|
| Bar (default) | Clustered columns; hide chart title; category axis on; value axis usually off; labels inside end, white Demi; gap modest; baseline/comparison `#B1B1B0` |
| Line | Stroke `#0092F4` 2–3px; no/small markers; no 3D |
| Pie | accent1–6; no 3D/explosion; percent labels |
| Waterfall | totals `#B1B1B0`; positive `#0092F4`; negative `#FF4800`; connectors ~35% gray |

## Forbidden

- Non-theme decorative colors / purple AI defaults
- 3D effects, text drop shadows, non-template fonts
- Design-guide `#F26B43`
- Invented PII or metrics
