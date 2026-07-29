---
name: sketch2deck
description: >-
  Convert data, key messages, design concepts, or hand-drawn sketches into a
  Payoneer-styled HTML slide ready to screenshot or export into a PowerPoint
  deck. Use when the user says PPT, create slide, slide, deck, blank,
  presentation, PowerPoint, sketch2deck, sketch to deck, HTML slide, blank
  slide, make a slide, design a slide, or asks to turn notes, data, concepts,
  or sketches into a slide or presentation.
---

# sketch2deck

Produce a **single self-contained HTML slide** (16:9) styled to the Payoneer master template. The user screenshots or exports it into their PowerPoint deck.

Canonical style source (read when available):

- `C:\Users\tylerya\Cursor projects\sketch2deck\DESIGN_STYLE_GUIDANCE.md`
- `C:\Users\tylerya\Cursor projects\sketch2deck\Master PPT Template - Short.pptx`

If those paths are unavailable, follow [style-tokens.md](style-tokens.md) in this skill.

## Workflow

Copy and track:

```
Task Progress:
- [ ] 1. Parse inputs
- [ ] 2. Choose layout
- [ ] 3. Draft content
- [ ] 4. Write HTML slide
- [ ] 5. Open / instruct export
```

### 1. Parse inputs

Accept any mix of:

| Input | How to use |
|-------|------------|
| Key messages / bullets | Map to title, tagline, body, bulletList |
| Data (tables, CSV, numbers) | Prefer chart or table; keep numbers exact |
| Design concept (prose) | Infer layout + hierarchy; do not invent facts |
| Hand-drawn sketch / image | Read the image; typed overlays override handwriting |
| Layout hint | Honor named layout if user specifies one |

If content is ambiguous (missing title, unclear chart type, conflicting numbers), ask **one** short clarifying question before generating.

**Do not invent** metrics, quotes, or PII. Use only what the user provided.

### 2. Choose layout

Pick the closest Payoneer layout (see [style-tokens.md](style-tokens.md)):

| Signal | Layout |
|--------|--------|
| Cover / title + tagline | Front Cover - Light B |
| Agenda / numbered list with owners | Big title and Content - Light |
| Section break | Divider Cover - Light B |
| Large quote | Big text / Quotes / Testimonials - Light A or B |
| Title + bullets or one chart | Titles and Content A |
| Three highlight columns | Titles and 3 highlights |
| Table + status | Titles, Table and Status |
| Two / three columns | Titles, 2/3 Content boxes and paragraphs |
| Dense multi-box | Titles and 4 text boxes with content inside |

Sketch heuristics: large top text → title; dashed "Tagline" → tagline; bar/wavy/pie shapes → chart; grid → table; `❝` → quote; `*` at bottom → footnote.

### 3. Draft content

- One clear title (prefer single line).
- One job per slide — cut secondary clutter.
- Bullets: `•` level 1, `–` level 2, `>` level 3.
- Charts: clustered column default; primary series `#0092F4`; no chart title; white data labels on bars when space allows.
- Footnotes: prefix `*`, muted gray, bottom-left.
- Slide number: optional, bottom-right, `#808080`.

### 4. Write HTML slide

1. Start from [templates/slide-shell.html](templates/slide-shell.html).
2. Write a **self-contained** `.html` file (inline CSS only; no external deps).
3. Save under the active project when possible, e.g. `slides/<slug>.html`; otherwise use a path the user names.
4. Slide stage must be exactly **16:9** (`1920×1080` CSS pixels recommended).
5. Match tokens in [style-tokens.md](style-tokens.md): white background, black text, Avenir Next fallback stack, accent blue for charts/highlights.
6. No drop shadows on text, no 3D charts, no non-theme colors except semantic waterfall negatives (`#FF4800`).
7. Never use design-guide orange `#F26B43` in output.
8. Add a minimal off-slide toolbar (outside `.slide`) with **Screenshot tip** / **Print** only — never include chrome inside the 16:9 frame.

Structure:

```html
<body>
  <div class="export-bar">…</div>  <!-- outside slide -->
  <div class="slide" data-layout="…">
    <!-- only deck-visible content -->
  </div>
</body>
```

### 5. Open / instruct export

After writing the file:

1. Open it in the default browser when possible (`start` on Windows).
2. Tell the user how to capture for PowerPoint:

**Screenshot (fastest)**
- Zoom browser so the white `.slide` fills the view (or use fullscreen).
- Capture only the slide frame (Win+Shift+S), paste into PPT as a picture.

**Print / PDF**
- Ctrl+P → destination **Save as PDF** or **Microsoft Print to PDF**.
- Enable background graphics; set margins to none; landscape; scale to fit one page.
- Place PDF page or exported image into the deck.

HTML slides are **visual inserts**. They are not editable native PPT shapes/charts unless the user separately uses the sketch2deck PPTX pipeline.

## Output contract

Return briefly:

1. Layout chosen and why (one line).
2. File path written.
3. Export reminder (screenshot of `.slide` or print-to-PDF).

Do not dump the full HTML in chat unless the user asks.

## Revision loop

When the user requests changes ("make title shorter", "switch to 3 columns", "use pie"):

1. Edit the same HTML file in place.
2. Keep style tokens unchanged unless they explicitly request a brand exception.
3. Re-open or point them to refresh the browser.

## Anti-patterns

- Flat purple/cream AI-default aesthetics — use Payoneer tokens only.
- Cards, pill clusters, glow, or decorative gradients inside the slide.
- Invented data or filler Latin text.
- Full PII unless the user supplied it for the slide.
- Multiple slides in one file unless the user explicitly asks for a pack (then one `.slide` per section, still 16:9 each).
