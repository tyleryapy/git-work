#!/usr/bin/env python3
"""Convert the overseas procurement report HTML into an editable slide deck."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / ".cursor/skills/frontend-slides-editable/examples/editable-deck-reference.html"
SRC = ROOT / "presentations/海外采买时效分析_买手leader版.html"
OUT = ROOT / "presentations/海外采买时效分析_买手leader版-editable.html"


def extract_between(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i + len(start) : j]


def slide_shell(slide_id: int, inner_html: str, oid: str) -> str:
    visible = ' visible' if slide_id == 0 else ''
    return f'''<section class="slide{visible}" id="slide-{slide_id}">
  <div class="slide-edit-layer">
    <div class="slide-object" data-slide-object data-oid="{oid}" data-object-type="text"
         style="left:3%;top:3%;width:94%;height:94%;">
      <button type="button" class="slide-object-move" aria-label="Move object" title="Drag to move">⠿</button>
      <button type="button" class="slide-object-delete" aria-label="Delete object">×</button>
      <button type="button" class="slide-object-resize" aria-label="Resize"></button>
      <div class="slide-object-text report-slide-body" contenteditable="false">{inner_html}</div>
    </div>
  </div>
</section>'''


def split_summary_slides(summary_bd: str) -> list[str]:
    parts: list[str] = []
    h3_splits = re.split(r'(?=<h3 class="sub">)', summary_bd)
    if h3_splits:
        parts.append(h3_splits[0])
        parts.extend(h3_splits[1:])
    else:
        parts = [summary_bd]
    return [p.strip() for p in parts if p.strip()]


def extract_div_blocks(html: str, class_prefix: str = "block") -> list[tuple[str, str]]:
    """Return list of (class_attr, full_block_html) for top-level block divs."""
    blocks: list[tuple[str, str]] = []
    pattern = re.compile(rf'<div class="({class_prefix}[^"]*)">', re.I)
    pos = 0
    while True:
        m = pattern.search(html, pos)
        if not m:
            break
        start = m.start()
        cls = m.group(1)
        depth = 0
        i = start
        while i < len(html):
            if html.startswith("<div", i):
                depth += 1
                i = html.find(">", i) + 1
                continue
            if html.startswith("</div>", i):
                depth -= 1
                i += 6
                if depth == 0:
                    blocks.append((cls, html[start:i]))
                    pos = i
                    break
                continue
            i += 1
        else:
            break
    return blocks


def main() -> None:
    ref = REF.read_text(encoding="utf-8")
    src = SRC.read_text(encoding="utf-8")

    ref_style = extract_between(ref, "<style>", "</style>")
    ref_chrome = extract_between(ref, '<div class="deck-left-hover-anchor"', '<div class="slides-offset">')
    ref_script = extract_between(ref, "<script>", "</script>")

    orig_style = extract_between(src, "<style>", "</style>")
    orig_script = extract_between(src, "<script>", "</script>")

    wrap = extract_between(src, '<div class="wrap">', '</div>\n\n<script>')

    head_match = re.search(r'<div class="head">(.*?)</div>', wrap, re.S)
    kpi_match = re.search(r'<div class="kpi">(.*?)</div>\s*', wrap, re.S)
    foot_match = re.search(r'<div class="foot">(.*?)</div>\s*$', wrap, re.S)

    slides: list[str] = []
    sid = 0

    if head_match:
        slides.append(slide_shell(sid, f'<div class="head">{head_match.group(1)}</div>', f"s{sid}-o0"))
        sid += 1

    if kpi_match:
        slides.append(slide_shell(sid, f'<div class="kpi">{kpi_match.group(1)}</div>', f"s{sid}-o0"))
        sid += 1

    for cls, block_html in extract_div_blocks(wrap, "block"):
        bh_match = re.search(r'<div class="bh">(.*?)</div>\s*<div class="bd">(.*?)</div>\s*$', block_html, re.S)
        if not bh_match:
            continue
        bh, bd = bh_match.group(1), bh_match.group(2)

        if "整体总结" in bh:
            for chunk in split_summary_slides(bd):
                slides.append(
                    slide_shell(
                        sid,
                        f'<div class="block static"><div class="bh">整体总结</div><div class="bd">{chunk}</div></div>',
                        f"s{sid}-o0",
                    )
                )
                sid += 1
        elif "关键洞察 2" in bh:
            lead_match = re.search(r'<p class="lead">.*?</p>', bd, re.S)
            table_match = re.search(
                r'<table class="heat">.*?</table>\s*<div class="legend">.*?</div>',
                bd,
                re.S,
            )
            if lead_match and table_match:
                slides.append(
                    slide_shell(
                        sid,
                        f'<div class="block open"><div class="bh">{bh}</div><div class="bd">{lead_match.group(0)}{table_match.group(0)}</div></div>',
                        f"s{sid}-o0",
                    )
                )
                sid += 1
                rest = bd[table_match.end() :].strip()
            else:
                rest = bd
            if rest:
                slides.append(
                    slide_shell(
                        sid,
                        f'<div class="block open"><div class="bh">{bh}</div><div class="bd">{rest}</div></div>',
                        f"s{sid}-o0",
                    )
                )
                sid += 1
        else:
            open_cls = " open" if "open" in cls or "详细拆解" in bh else ""
            slides.append(slide_shell(sid, f'<div class="block{open_cls}"><div class="bh">{bh}</div><div class="bd">{bd}</div></div>', f"s{sid}-o0"))
            sid += 1

    if foot_match:
        slides.append(
            slide_shell(
                sid,
                f'<div class="foot">{foot_match.group(1)}</div>',
                f"s{sid}-o0",
            )
        )

    slides_html = "\n\n".join(slides)

    extra_css = """
    /* === Report theme (from original) === */
    :root {
      --slide-bg-deep: #f5f5f5;
      --slide-bg-gradient: linear-gradient(160deg, #ffffff 0%, #f8f4f6 55%, #f5f5f5 100%);
      --text-primary: #383838;
      --font-display: 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
      --font-body: 'Microsoft YaHei', '微软雅黑', 'PingFang SC', sans-serif;
      --deck-chrome-bg: rgba(255, 255, 255, 0.96);
      --deck-chrome-border: rgba(236, 0, 140, 0.22);
      --deck-chrome-text: #383838;
      --deck-chrome-muted: #888;
      --deck-chrome-accent: #EC008C;
      --deck-chrome-shadow: 0 12px 40px rgba(196, 38, 117, 0.18);
      --deck-chrome-surface: #fffafd;
    }
    body { font-family: var(--font-body); color: var(--text-primary); }
    .slide { background: var(--slide-bg-gradient); }
    .report-slide-body {
      width: 100%;
      height: 100%;
      overflow: hidden;
      font-size: clamp(0.62rem, 1.05vw, 0.82rem);
      line-height: 1.55;
      pointer-events: auto;
    }
    .report-slide-body .wrap { max-width: none; margin: 0; padding: 0; }
    .report-slide-body .head {
      background: linear-gradient(135deg,#C42675,#EC008C);
      color: #fff; padding: clamp(0.6rem,1.5vh,1rem) clamp(0.8rem,2vw,1.2rem);
      border-radius: 10px; margin-bottom: 0.6rem;
    }
    .report-slide-body .head h1 { font-size: clamp(1rem, 2.2vw, 1.35rem); margin-bottom: 0.25rem; }
    .report-slide-body .head p { font-size: clamp(0.55rem, 1vw, 0.72rem); opacity: .92; }
    .report-slide-body .kpi {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: clamp(0.35rem, 1vw, 0.7rem);
    }
    .report-slide-body .kpi .c {
      background: #fff; border-radius: 8px; padding: clamp(0.4rem, 1vh, 0.7rem);
      text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.05);
    }
    .report-slide-body .kpi .v { font-size: clamp(0.9rem, 1.8vw, 1.2rem); font-weight: 700; color: #EC008C; }
    .report-slide-body .block { background: #fff; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.05); overflow: hidden; }
    .report-slide-body .block > .bh {
      padding: clamp(0.45rem, 1vh, 0.65rem) clamp(0.6rem, 1.5vw, 0.9rem);
      font-size: clamp(0.72rem, 1.3vw, 0.9rem); font-weight: 700;
      border-left: 4px solid #EC008C;
    }
    .report-slide-body .block > .bd { padding: 0 clamp(0.6rem, 1.5vw, 0.9rem) clamp(0.5rem, 1vh, 0.75rem); display: block !important; }
    .report-slide-body .block:not(.static) > .bh { cursor: pointer; }
    .report-slide-body h3.sub { font-size: clamp(0.68rem, 1.15vw, 0.82rem); color: #C42675; margin: 0.45rem 0 0.25rem; }
    .report-slide-body p.lead { font-size: clamp(0.62rem, 1vw, 0.78rem); margin: 0.25rem 0; }
    .report-slide-body .hi { background: #F5D0E0; padding: 1px 4px; border-radius: 3px; font-weight: 600; color: #C42675; }
    .report-slide-body b.k { color: #C42675; }
    .report-slide-body ul.clean { list-style: none; margin: 0.2rem 0; }
    .report-slide-body ul.clean li { position: relative; padding: 0.2rem 0 0.2rem 1rem; font-size: clamp(0.58rem, 0.95vw, 0.74rem); }
    .report-slide-body ul.clean li:before { content: "—"; position: absolute; left: 0; color: #EC008C; font-weight: 700; }
    .report-slide-body .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.45rem; margin-top: 0.35rem; }
    .report-slide-body .pcard { border: 1px solid #F5D0E0; border-radius: 8px; padding: 0.45rem 0.55rem; background: #fffafd; }
    .report-slide-body .pcard h4 { font-size: clamp(0.62rem, 1vw, 0.76rem); color: #EC008C; margin-bottom: 0.2rem; }
    .report-slide-body .pcard .row { font-size: clamp(0.55rem, 0.9vw, 0.68rem); color: #555; margin: 0.15rem 0; }
    .report-slide-body .warn {
      background: #fff8ec; border: 1px solid #f5d99b; border-radius: 8px;
      padding: 0.45rem 0.6rem; font-size: clamp(0.55rem, 0.9vw, 0.68rem); color: #7a5a1e; margin-top: 0.35rem;
    }
    .report-slide-body table.heat { border-collapse: collapse; width: 100%; font-size: clamp(0.48rem, 0.75vw, 0.62rem); margin-top: 0.25rem; }
    .report-slide-body table.heat th { background: #faf0f6; color: #888; padding: 3px 2px; border: 1px solid #f0e0ea; }
    .report-slide-body table.heat td { padding: 4px 2px; text-align: center; border: 1px solid #f5eef2; }
    .report-slide-body table.heat td.cn { text-align: left; font-weight: 600; background: #fafafa; }
    .report-slide-body .h0{background:#fff}.report-slide-body .h1{background:#fce8f3}
    .report-slide-body .h2{background:#fcbfe0}.report-slide-body .h3{background:#f987c2;color:#fff}
    .report-slide-body .h4{background:#EC008C;color:#fff}.report-slide-body .hx{color:#ccc}
    .report-slide-body .legend { font-size: clamp(0.48rem, 0.7vw, 0.58rem); color: #aaa; margin-top: 0.2rem; }
    .report-slide-body .kd { border: 1px solid #F5D0E0; border-radius: 8px; padding: 0.45rem 0.6rem; margin-bottom: 0.35rem; background: #fffafd; }
    .report-slide-body .kd .kh { font-size: clamp(0.62rem, 1vw, 0.76rem); font-weight: 700; color: #C42675; display: flex; justify-content: space-between; }
    .report-slide-body .tg { display: inline-block; padding: 1px 6px; border-radius: 8px; font-size: 0.55rem; margin-left: 4px; }
    .report-slide-body .tg-h { background: #EC008C; color: #fff; }
    .report-slide-body .tg-m { background: #FCA1D4; color: #7a2555; }
    .report-slide-body .tg-l { background: #eee; color: #999; }
    .report-slide-body #steps li {
      display: flex; align-items: flex-start; gap: 6px; background: #fff; border: 1px solid #eee;
      border-radius: 7px; padding: 6px 8px; margin-bottom: 5px; cursor: grab; font-size: clamp(0.55rem, 0.9vw, 0.68rem);
    }
    .report-slide-body .pr-高{background:#EC008C;color:#fff}.report-slide-body .pr-中{background:#FCA1D4;color:#7a2555}
    .report-slide-body .pr-低{background:#f0e0ea;color:#a05a80}.report-slide-body .pr-降本{background:#eee;color:#888}
    .report-slide-body .l1 { border: 1px solid #eee; border-radius: 8px; margin-bottom: 0.35rem; overflow: hidden; }
    .report-slide-body .l1 > .l1h { padding: 0.4rem 0.55rem; cursor: pointer; background: #fafafa; display: flex; justify-content: space-between; }
    .report-slide-body .l1 > .l1b { display: none; padding: 0.25rem 0.45rem 0.45rem; max-height: 52vh; overflow: auto; }
    .report-slide-body .l1.open > .l1b { display: block; }
    .report-slide-body .itm select, .report-slide-body .itm input {
      width: 100%; font-size: clamp(0.48rem, 0.75vw, 0.62rem); padding: 2px 3px;
      border: 1px solid #e2d2dc; border-radius: 4px; background: #fffafd;
    }
    .report-slide-body .btn {
      font-size: clamp(0.52rem, 0.8vw, 0.65rem); padding: 4px 8px; border: 1px solid #EC008C;
      color: #EC008C; background: #fff; border-radius: 5px; cursor: pointer;
    }
    .report-slide-body .foot { font-size: clamp(0.52rem, 0.8vw, 0.65rem); color: #aaa; text-align: center; }
    body.deck-edit-mode .report-slide-body select,
    body.deck-edit-mode .report-slide-body input,
    body.deck-edit-mode .report-slide-body button,
    body.deck-edit-mode .report-slide-body #steps li { pointer-events: none; }
    body.deck-edit-mode .slide-object.is-selected .report-slide-body { pointer-events: none; }
    @media (max-height: 700px) {
      .report-slide-body { font-size: clamp(0.55rem, 0.95vw, 0.72rem); }
    }
    """

    # Patch storage key in script
    ref_script = ref_script.replace(
        "const STORAGE_KEY = 'editable-deck:' + (document.documentElement.getAttribute('data-deck-id') || 'default');",
        "const STORAGE_KEY = 'editable-deck:' + (document.documentElement.getAttribute('data-deck-id') || 'default');",
    )

    orig_script_clean = re.sub(
        r"^document\.querySelectorAll\('\.block:not\(\.static\)>\.bh'\).*?;\s*",
        "",
        orig_script.strip(),
        count=1,
        flags=re.S,
    )

    orig_script_wrapped = f"""
// === Original report interactivity ===
(function() {{
  function initReportBlocks() {{
    document.querySelectorAll('.report-slide-body .block:not(.static) > .bh').forEach(function(h) {{
      if (h.dataset.bound) return;
      h.dataset.bound = '1';
      h.addEventListener('click', function() {{ h.parentElement.classList.toggle('open'); }});
    }});
  }}
  {orig_script_clean}
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initReportBlocks);
  else initReportBlocks();
  window.addEventListener('deck-slides-refreshed', initReportBlocks);
}})();
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-deck-id="haiwai-caimai-leader" data-mobile-adaptation="desktop-default" data-template-edit-mode="components">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>海外采买全链路时效 · 分析结论与提效方向 (Editable)</title>
  <style>
{ref_style}
{extra_css}
  </style>
</head>
<body>
<div class="deck-left-hover-anchor" id="deckLeftHover" aria-label="Deck controls">
{ref_chrome}
<div class="slides-offset">
{slides_html}
</div>

<script>
{ref_script}
{orig_script_wrapped}
</script>
</body>
</html>
"""

    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
