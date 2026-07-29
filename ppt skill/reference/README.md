# Reference: Master PPT Template - Standard

## Binary status

The full `Master PPT Template - Standard.pptx` (~39–95 MB) exceeds the Microsoft 365 MCP download limit (4 MB). This folder stores **extraction artifacts** instead of the binary.

## Canonical locations

| Source | Path / URL |
|--------|------------|
| OneDrive (Tyler) | `Documents/02 Logistics/Master PPT Template - Standard.pptx` (item `0154JJLDEQEAAK6EGQ2BGYDPXOUQ5MITAX`) |
| CreativeStudio | `Shared Documents/Master Templates/Master PPT Template/Master PPT Template - Standard.pptx` |

## Artifacts

- `extraction.json` — structured tokens mined from Standard Branding Assets / Grid System search hits plus theme-aligned design guides
- Skill docs at `../DESIGN_STYLE_GUIDANCE.md` and `../style-tokens.md` are authoritative for agents

## Re-extract when binary is available

```bash
python3 ../scripts/extract_pptx_tokens.py "/path/to/Master PPT Template - Standard.pptx" -o extraction.json
```
