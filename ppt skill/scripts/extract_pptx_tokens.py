#!/usr/bin/env python3
"""Extract design tokens from a Payoneer Master PPT Template .pptx (stdlib only).

Usage:
  python3 extract_pptx_tokens.py "/path/to/Master PPT Template - Standard.pptx" -o extraction.json
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

EMU_PER_INCH = 914400
PT_PER_INCH = 72


def emu_to_in(emu: int | None) -> float | None:
    if emu is None:
        return None
    return round(emu / EMU_PER_INCH, 4)


def hundredths_pt_to_pt(val: str | None) -> float | None:
    if not val:
        return None
    return int(val) / 100.0


def srgb(el: ET.Element | None) -> str | None:
    if el is None:
        return None
    srgb = el.find(".//a:srgbClr", NS)
    if srgb is not None and srgb.get("val"):
        return f"#{srgb.get('val').upper()}"
    sys = el.find(".//a:sysClr", NS)
    if sys is not None and sys.get("lastClr"):
        return f"#{sys.get('lastClr').upper()}"
    return None


def parse_theme(z: zipfile.ZipFile) -> dict:
    themes = [n for n in z.namelist() if n.startswith("ppt/theme/") and n.endswith(".xml")]
    if not themes:
        return {}
    root = ET.fromstring(z.read(themes[0]))
    scheme = root.find(".//a:clrScheme", NS)
    colors = {}
    if scheme is not None:
        for child in list(scheme):
            tag = child.tag.split("}")[-1]
            colors[tag] = srgb(child)
    fonts = {}
    major = root.find(".//a:majorFont/a:latin", NS)
    minor = root.find(".//a:minorFont/a:latin", NS)
    if major is not None:
        fonts["major"] = major.get("typeface")
    if minor is not None:
        fonts["minor"] = minor.get("typeface")
    return {"colors": colors, "fonts": fonts, "theme_file": themes[0]}


def parse_layouts(z: zipfile.ZipFile) -> list[dict]:
    layouts = []
    for name in sorted(n for n in z.namelist() if n.startswith("ppt/slideLayouts/") and n.endswith(".xml")):
        root = ET.fromstring(z.read(name))
        c_sld = root.find("p:cSld", NS)
        layout_name = c_sld.get("name") if c_sld is not None else Path(name).stem
        phs = []
        for ph in root.findall(".//p:ph", NS):
            phs.append(
                {
                    "type": ph.get("type") or "body",
                    "idx": ph.get("idx"),
                    "sz": ph.get("sz"),
                }
            )
        layouts.append({"file": name, "name": layout_name, "placeholders": phs})
    return layouts


def parse_master_text_styles(z: zipfile.ZipFile) -> dict:
    masters = [n for n in z.namelist() if n.startswith("ppt/slideMasters/") and n.endswith(".xml")]
    if not masters:
        return {}
    root = ET.fromstring(z.read(masters[0]))
    out: dict = {"file": masters[0], "levels": {}}
    for style_name in ("titleStyle", "bodyStyle", "otherStyle"):
        style = root.find(f"p:{style_name}", NS)
        if style is None:
            continue
        levels = []
        for lvl in style:
            tag = lvl.tag.split("}")[-1]
            def_rpr = lvl.find("a:defRPr", NS)
            size = hundredths_pt_to_pt(def_rpr.get("sz") if def_rpr is not None else None)
            bold = def_rpr.get("b") if def_rpr is not None else None
            latin = def_rpr.find("a:latin", NS) if def_rpr is not None else None
            color = srgb(def_rpr) if def_rpr is not None else None
            levels.append(
                {
                    "level": tag,
                    "size_pt": size,
                    "bold": bold,
                    "font": latin.get("typeface") if latin is not None else None,
                    "color": color,
                }
            )
        out["levels"][style_name] = levels
    return out


def slide_text_samples(z: zipfile.ZipFile, limit: int = 40) -> list[dict]:
    samples = []
    slides = sorted(
        n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)
    )
    for name in slides[:limit]:
        root = ET.fromstring(z.read(name))
        texts = [t.text.strip() for t in root.findall(".//a:t", NS) if t.text and t.text.strip()]
        hexes = sorted(set(re.findall(r"[0-9A-Fa-f]{6}", ET.tostring(root, encoding="unicode"))))
        # Keep only hexes that look like colors used as srgb
        samples.append(
            {
                "file": name,
                "text_preview": texts[:30],
                "text_count": len(texts),
            }
        )
    return samples


def extract(pptx_path: Path) -> dict:
    with zipfile.ZipFile(pptx_path) as z:
        sld_sz = None
        for name in z.namelist():
            if name == "ppt/presentation.xml":
                root = ET.fromstring(z.read(name))
                sz = root.find("p:sldSz", NS)
                if sz is not None:
                    sld_sz = {
                        "cx_emu": int(sz.get("cx", 0)),
                        "cy_emu": int(sz.get("cy", 0)),
                        "width_in": emu_to_in(int(sz.get("cx", 0))),
                        "height_in": emu_to_in(int(sz.get("cy", 0))),
                    }
        fonts = [n for n in z.namelist() if n.startswith("ppt/fonts/")]
        return {
            "source_file": str(pptx_path),
            "slide_size": sld_sz,
            "theme": parse_theme(z),
            "layouts": parse_layouts(z),
            "master_text_styles": parse_master_text_styles(z),
            "embedded_fonts": fonts,
            "slide_text_samples": slide_text_samples(z),
            "part_count": len(z.namelist()),
        }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pptx", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()
    data = extract(args.pptx)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} ({len(data.get('layouts', []))} layouts)")


if __name__ == "__main__":
    main()
