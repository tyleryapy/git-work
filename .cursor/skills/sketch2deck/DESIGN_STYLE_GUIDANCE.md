# sketch2deck — Design Style Guidance

Style rules for the sketch2deck HTML slide skill, derived from **Master PPT Template - Standard.pptx** (Payoneer 2024 master template family `11506_New_PPT_template_2024_v1` / theme `3_Payoneer Theme`).

Cross-checked against:

- Standard Branding Assets / Grid System / QUICK GUIDES slides (SharePoint-indexed content)
- Prior Short-template instrumentation (`DESIGN_STYLE_GUIDANCE` for Short)
- SAGE `presentation-designer/STYLE_GUIDE.md` (icon cards, photo/mockup, chart selection)

Structured extraction cache: [reference/extraction.json](reference/extraction.json).

When the `.pptx` binary is available locally, re-run:

```bash
python3 scripts/extract_pptx_tokens.py "/path/to/Master PPT Template - Standard.pptx" -o reference/extraction.json
```

---

## 1. Template overview

| Property | Value |
|----------|-------|
| File | `Master PPT Template - Standard.pptx` |
| Theme name | `3_Payoneer Theme` |
| Theme family | `11506_New_PPT_template_2024_v1` |
| Company | Payoneer |
| Embedded fonts | Yes (`embedTrueTypeFonts=1`) |
| Design mood | Polished corporate, high contrast, clean geometry, generous whitespace |

### Slide dimensions

| Property | Value |
|----------|-------|
| Aspect ratio | 16:9 |
| Width | 26.67 in (24,384,000 EMU) |
| Height | 15.00 in (13,716,000 EMU) |
| CSS stage | `1920px × 1080px` |
| Background | White (`#FFFFFF` / `bg1`) |

---

## 2. Grid system and margins

From Standard **Grid System / QUICK GUIDES TO USING THIS TEMPLATE**:

- Section header title and subtitle align to the **horizontal content grid**.
- Detailed tables stretch within the content columns — do not float off-grid.
- Keep one clear visual hierarchy: title → subject/tagline → body → footnote.

| Guideline | Value |
|-----------|-------|
| Left content margin | ~0.89 in (812,800 EMU) ≈ **5.5%** / CSS `106px` at 1920 |
| Right content margin | Mirror left (~5.5%) |
| Title top | ~5% from top ≈ CSS `54px` |
| Content start | ~15% from top (below title) |
| Title placeholder width | ~24.9 in |
| Bottom safe area | Leave room for footnote (left) + slide number (right) |
| Slide number | Bottom-right |
| Logo placeholder | Bottom-left on master (Payoneer logo); optional in HTML inserts |

CSS stage padding (shell): `54px 106px 72px`.

---

## 3. Color palette

### Theme colors

| Role | Hex | Theme token | Usage |
|------|-----|-------------|-------|
| Text primary | `#000000` | `dk1` / `tx1` | Titles, body text |
| Text secondary | `#808080` | — | Slide numbers, footnotes, attribution |
| Background | `#FFFFFF` | `lt1` / `bg1` | Slide background |
| Background secondary | `#B1B1B0` | `lt2` / `bg2` | Chart baseline bars, muted fills, secondary diagram strokes |
| Accent 1 — Primary blue | `#0092F4` | `accent1` | Primary chart series, key highlights, diagram strokes |
| Accent 2 — Green | `#20DC86` | `accent2` | Secondary series; **positive / `.pos` status** |
| Accent 3 — Yellow | `#DFD902` | `accent3` | Tertiary series; **warning / attention** |
| Accent 4 — Orange | `#F7931E` | `accent4` | Fourth series; process / transition |
| Accent 5 — Red-orange | `#FF4800` | `accent5` | Fifth series; **negative waterfall / `.neg` / risk** |
| Accent 6 — Magenta | `#DA54D8` | `accent6` | Sixth series / distinct category |
| Hyperlink | `#0563C1` | `hlink` | Links only |
| Followed link | `#954F72` | — | Followed links only |
| Table border | `#E3E3E3` | — | Table row separators |
| Highlight callout | `#FFE832` | — | Callout / highlight fills |
| Midnight blue (brand) | `#002373` | — | HTML report headers only — **not** chart accent or slide fill |
| Design guides | `#F26B43` | — | Internal layout guides only — **never output** |

### Diagram tint ladder (Standard Branding Assets)

Use these tints for multi-step process diagrams, comparison fills, and soft category chips — not as random decoration.

| Family | Base | Mid | Light |
|--------|------|-----|-------|
| Blue (primary) | `#0092F4` | `#5FBFFF` | `#95D4FF` |
| Green (positive) | `#20DC86` | `#78EBB7` | `#A5F2CF` |
| Coral / warm | `#FF9166` | `#FFB699` | `#FBC7B2` |
| Gray (baseline) | `#B1B1B0` | `#BFBFBF` | — |

Dark panel option for shaded covers only: `#1E1E28` with shade steps **80% / 60% / 40% / 20%**. Prefer soft linear gradients or broad shaded bands on headline-only slides — **no circles/orbs** behind content-heavy slides.

### Color rules

- Prefer **one** primary accent per section; max 6–7 distinct colors per chart.
- Same category = same color across all charts in a deck.
- Green / Yellow / Red-orange are **semantic** for status when possible.
- Never use `#F26B43` or purple AI-default palettes.
- Midnight blue `#002373` is brand header only — not charts.

Charts cycle `accent1`→`accent6`. Default primary series: `#0092F4`.

---

## 4. Typography

### Font families

| Role | Font | CSS / PPT reference |
|------|------|---------------------|
| Headings (major) | Avenir Next LT Pro **Demi** | `+mj-lt` / title style |
| Body (minor) | Avenir Next LT Pro | `+mn-lt` / body style |

**Fallback stack (preview / web):** `"Avenir Next LT Pro", "Avenir Next", "Segoe UI", Arial, system-ui, sans-serif`

### Type scale (from slide master)

| Element | Font | Size | Weight | Color | CSS @ 1920×1080 |
|---------|------|-----:|--------|-------|----------------:|
| Slide title | Demi | **65 pt** | 600 | `#000` | ~86px |
| Section header / subject | Demi | **40–65 pt** | 600 | `#000` | ~53–86px |
| Body level 1 | Regular | **40 pt** | 400 | `#000` | ~53px |
| Body level 2 / tagline | Regular | **30 pt** | 400 | `#000` | ~40px |
| Body levels 3–5 | Regular | **24 pt** | 400 | `#000` | ~32px |
| Quote body | Demi | large (~48–64 pt) | 600 | `#000` | ~64–86px |
| Quote attribution | Demi | **30 pt** | 600 | `#808080` | ~40px |
| Table header | Bold | **24 pt** | 700 | `#000` | ~32px |
| Table body | Regular | **20 pt** | 400 | `#000` | ~27px |
| Footnote | Regular | **16 pt** | 400 | muted gray | ~21px |
| Slide number | Regular | **20 pt** | 400 | `#808080` | ~27px |
| Chart axis labels | Regular | **22 pt** | 400 | ~65% gray | ~29px |
| Chart data labels | Demi | **20–28 pt** | 600 | `#fff` on bar | ~27–37px |
| Caption / other | Regular | **18 pt** | 400 | `#000` | ~24px |

Conversion: `css_px ≈ pt × (1920 / (26.67 × 72))` ≈ **pt × 1.333**. Prefer fixed px inside a fixed 1920×1080 stage.

Line spacing: **100%** for body levels. First-level indent: 450,000 EMU (~0.49 in).

### Bullets and lists

| Level | Character | Size | Spacing after |
|------:|-----------|-----:|--------------:|
| 1 | `•` | 40 pt | 18 pt |
| 2 | `–` (en-dash) | 30 pt | 24 pt |
| 3 | `>` | 24 pt | 9 pt |
| 4 | `–` | 24 pt | 9 pt |
| 5 | `>` | 24 pt | 9 pt |

---

## 5. Template slide sections

Standard organizes examples into:

1. Front Covers (Light)
2. Agenda (Light)
3. Section Titles (Light)
4. Call Outs / Statements Text only (Light)
5. Text Only & Plain Slide
6. Charts / Diagrams / Tables
7. Branding Assets / Grid System / Quick Guides
8. Extended patterns: icon cards, image/mockup, timelines, comparison grids, shaded dividers

---

## 6. Slide layouts

Use these names when choosing a layout:

| Layout name | Best for |
|-------------|----------|
| Front Cover - Light B | Title / cover slide, tagline |
| Big title and Content - Light | Agenda with table (`#` \| Agenda Item \| Owner) |
| Divider Cover - Light B | Section divider |
| Numbered Divider - Light | Numbered section header |
| Big text / Quotes / Testimonials - Light A | Large quote, callout |
| Big text / Quotes / Testimonials - Light B | Quote with attribution |
| Title only | Minimal header |
| Titles and Content A | Title + main content or chart |
| Titles and 3 highlights | Three highlight columns |
| Titles, Table and Status | Table with status column |
| Titles, 2 Content boxes and paragraphs | Two-column bullets |
| Titles, 3 Content boxes and paragraphs | Three-column content |
| Titles and 4 text boxes with content inside | Dense multi-box layout |
| Icon cards (2–4) | Equal cards with short label + optional icon |
| Image / mockup | Photo or product screenshot with caption |
| Timeline / process | Numbered steps, horizontal timeline, vertical stages |
| Comparison grid | 2–3 mirrored columns |

---

## 7. Element rules

### Title / header

- Position: top-left, ~5% from top, ~3% from left margin.
- Font: Avenir Next LT Pro Demi, 65 pt, black, left-aligned.
- Prefer single line; wrap if necessary (max 2 lines; stay inside margins).

### Tagline / subject / subtitle

- Directly below title.
- 30–40 pt Regular (subject/section labels may use Demi when acting as mini-headers).
- Used on cover, section, and quote slides.

### Body text / paragraph

- 40 pt (L1) or 30 pt (L2), left-aligned.
- Avoid dense paragraph slides — prefer bullets or cards.

### Bullet lists

- Use template hierarchy (`•`, `–`, `>`).
- Level 1: 40 pt; indent per master.

### Quotes / testimonials

- Layout: Big text / Quotes — Light A or B.
- Opening `❝` top-right; closing `❞` bottom-right of quote block.
- Quote body: large Demi text.
- Attribution: name + title, 30 pt Demi, muted gray, below quote.

### Agenda

- Layout: Big title and Content - Light.
- Columns: **#** | **Agenda Item** | **Owner**.
- Header: bold 24 pt; body: 20 pt; row separators `#E3E3E3`.

### Footnote

- Prefix with `*`.
- 16 pt muted gray; bottom-left.
- Optional right footer: 20 pt `#808080`, right-aligned.

### Slide number

- Bottom-right, 20 pt `#808080`.

### Tables

- First row: header style, bold 24 pt.
- Banded rows enabled.
- Header bottom border: ~85% luminosity of `bg1`.
- Cell padding: ~0.08 in top/bottom.
- Border color: `#E3E3E3` between rows.
- Status column: Green `#20DC86` / Yellow `#DFD902` / Red-orange `#FF4800` semantically.

### Diagrams (process, flow, arrows)

- Primary strokes/shapes: `#0092F4` (`accent1`).
- Secondary: `#B1B1B0` (`bg2`) or 65% gray.
- Arrows: simple triangular heads, **no drop shadows**.
- Process boxes: rounded rectangles, no fill or light tint from Branding Assets ladder.
- Connectors: ~35% gray.
- Labels: body L2/L3, left or centered on node; keep short.

### Icons and graphic symbols

- Prefer simple line or flat filled icons in **accent1** or black; avoid multi-color skeuomorphism.
- Icon cards: equal-width cards; icon top or left; short Demi label; Regular body.
- Align icons to a consistent size within a slide (e.g. 48–72 CSS px at 1920 stage).
- Do not place decorative icon clusters that compete with charts.
- No drop shadows on icons.

### Photos and mockups

- Place on clean white content slides or soft shaded covers — never busy patterned backgrounds.
- Prefer rectangular crops aligned to the grid; light or no border.
- Caption: 18 pt Regular, black or `#808080`.
- Do not apply heavy filters, neon overlays, or purple gradients.
- Product mockups: keep aspect truthful; leave margin from title and footnote.

---

## 8. Chart styling

### Bar chart (default in template)

Clustered columns (`barDir=col`, `grouping=clustered`).

| Property | Value |
|----------|-------|
| Chart title | Hidden |
| Value axis | Usually hidden |
| Category axis | Visible; bottom border line (black) |
| Axis label size | 22 pt, 65% gray |
| Data labels | Inside end of bar, white Demi |
| Gap width | 34–51 |
| Overlap | Negative (~−12 to −22) for grouped appearance |
| Primary series | `accent1` (`#0092F4`) |
| Baseline / comparison | `bg2` (`#B1B1B0`) or lighter accent tint |

### Line chart

- Stroke: `accent1` `#0092F4`, 2–3 pt.
- Markers: none or small circles.
- Axes: same as bar; no 3D.

### Pie chart

- Slice colors: cycle accent1–6.
- No 3D, no explosion.
- Data labels: percent values, 20 pt, outside or inside per space.
- No chart title.

### Waterfall

- Totals / baseline: `#B1B1B0`.
- Positive: `#0092F4`.
- Negative: `#FF4800`.
- Connectors: 35% gray.
- Data labels: inside bar, white text.

### Stacked / 100% stacked

- Use for composition over time; keep legend above chart, directly under any chart subtitle.
- Cycle accents consistently; label segments when space allows.

### Chart selection (analytics)

| Need | Preferred chart |
|------|-----------------|
| Trend over time | Line |
| Discrete periods | Vertical bar |
| Rankings / long labels | Sorted horizontal bar |
| Composition over time | Stacked or 100% stacked bar |
| Actual vs target | Bar + target marker / KPI card |
| Funnel | Funnel or stepped bars with conversion rates |

Avoid 3D charts, decorative gauges, crowded pies, unlabeled dual axes, rainbow decoration.

---

## 9. Sketch → element detection hints

| Sketch signal | Likely element | Layout hint |
|---------------|----------------|-------------|
| Large text at top | `title` | Titles and Content A |
| Dashed box "Tagline" | `tagline` | Front Cover / section |
| Paragraph placeholder | `body` | Titles and Content A |
| Bullets placeholder | `bulletList` | 2/3 Content boxes |
| Vertical bars | `chart` bar | Titles and Content A |
| Wavy line | `chart` line | Titles and Content A |
| Circle with slices | `chart` pie | Titles and Content A |
| Stepped bars +/- | `chart` waterfall | Titles and Content A |
| Table grid | `table` | Titles, Table and Status |
| Numbered rows | `agenda` | Big title and Content - Light |
| Large quote marks | `quote` | Quotes Light A/B |
| `*` small text at bottom | `footnote` | Any content layout |
| Horizontal divider | `sectionDivider` | Divider Cover |
| Icon + short labels in cards | `iconCards` | Icon cards 2–4 |
| Photo rectangle | `image` | Image / mockup |

**Priority:** Typed text box content overrides handwriting inference for the same region.

---

## 10. HTML slide output notes

- Self-contained HTML; inline CSS only; stage exactly 16:9 (`1920×1080` recommended).
- Export chrome (print/screenshot tips) **outside** `.slide`.
- Match tokens in [style-tokens.md](style-tokens.md).
- Visual inserts for PowerPoint — not native editable PPT shapes unless a separate PPTX pipeline is used.

---

## 11. What not to do

- Do not use non-theme decorative colors / purple AI defaults.
- Do not use 3D chart effects, text drop shadows, or non-template fonts.
- Do not output design-guide color `#F26B43`.
- Do not invent metrics, quotes, or PII.
- Do not put circles/orbs behind content-heavy chart/table slides.
- Do not use Midnight Blue `#002373` as a chart series or full-slide fill.
- Do not dump multiple unrelated stories on one slide — one job per slide.
