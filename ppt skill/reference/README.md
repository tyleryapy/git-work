# Template extraction reference

Outputs from running **pptx-masters** and **ppt-parse-analyzer** against
CreativeStudio `Master PPT Template - Standard.pptx` (local path:
`ppt skill/Master PPT Template - Standard.pptx`).

## Regenerating

```bash
# pptx-masters (theme, layouts, agent docs)
npx pptx-masters "ppt skill/Master PPT Template - Standard.pptx" \
  -o .cursor/skills/sketch2deck/reference/slide-masters

# ppt-parse-analyzer
cd tools/ppt-parse-analyzer-skill/ppt-parser
node scripts/parse_pptx.js "../../../ppt skill/Master PPT Template - Standard.pptx"
cd ../ppt-template-analyzer
node scripts/analyze_template.js \
  "../../../ppt skill/Master PPT Template - Standard_YYYYMMDD" \
  "../../.cursor/skills/sketch2deck/reference/template_report.md" \
  "../../.cursor/skills/sketch2deck/reference/template_report.json"
```

Large artifacts (`preview.pptx`, `media/`, full OpenXML `raw/` trees) are gitignored.

## Contents

| Path | Source | Purpose |
|------|--------|---------|
| `slide-masters/theme.json` | pptx-masters | Theme colors, fonts, tint/shade palette, dimensions |
| `slide-masters/SLIDE_MASTERS.md` | pptx-masters | All 146 layouts for agents |
| `slide-masters/STYLE_GUIDE.md` | pptx-masters | Editable design prefs (not overwritten on re-extract if customized carefully) |
| `slide-masters/report.md` | pptx-masters | Extraction warnings |
| `slide-masters/masters.js` | pptx-masters | PptxGenJS masters (for later native PPTX) |
| `template_report.md` / `.json` | ppt-parse-analyzer | Template structure analysis |
| `parser-summary/` | ppt-parse-analyzer | Manifest + summary (incl. slide text) |
| `branding-assets-slides.md` | ppt-parse-analyzer | Branding Assets / Quick Guides slides 1–10 text |
