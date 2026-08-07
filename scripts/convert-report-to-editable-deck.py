#!/usr/bin/env python3
"""Convert the overseas procurement report HTML into an improved editable slide deck."""

from __future__ import annotations

import ast
import html as html_lib
import json
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


def slide_shell(slide_id: int, inner_html: str, oid: str, extra_class: str = "") -> str:
    visible = " visible" if slide_id == 0 else ""
    cls = f"slide{extra_class}" if extra_class else "slide"
    return f'''<section class="{cls}{visible}" id="slide-{slide_id}">
  <div class="slide-edit-layer">
    <div class="slide-object" data-slide-object data-oid="{oid}" data-object-type="text"
         style="left:2.5%;top:2.5%;width:95%;height:95%;">
      <button type="button" class="slide-object-move" aria-label="Move object" title="Drag to move">⠿</button>
      <button type="button" class="slide-object-delete" aria-label="Delete object">×</button>
      <button type="button" class="slide-object-resize" aria-label="Resize"></button>
      <div class="slide-object-text report-slide-body" contenteditable="false">{inner_html}</div>
    </div>
  </div>
</section>'''


def block_wrap(bh: str, bd: str, *, static: bool = False, open_: bool = True) -> str:
    cls = "block"
    if static:
        cls += " static"
    if open_:
        cls += " open"
    return f'<div class="{cls}"><div class="bh">{bh}</div><div class="bd">{bd}</div></div>'


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


def js_to_python(raw: str) -> str:
    raw = re.sub(r"\btrue\b", "True", raw)
    raw = re.sub(r"\bfalse\b", "False", raw)
    raw = re.sub(r"\bnull\b", "None", raw)
    return raw


def parse_js_array(script: str, name: str):
    m = re.search(rf"(?:^|[,\s]){re.escape(name)}\s*=\s*\[", script, re.M)
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    in_str = False
    quote = ""
    escape = False
    for i in range(start, len(script)):
        ch = script[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_str = False
            continue
        if ch in "\"'":
            in_str = True
            quote = ch
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                raw = script[start : i + 1]
                return ast.literal_eval(js_to_python(raw))
    return None


def render_kadian_html(kadian: list) -> str:
    lv_map = {"高": ("tg-h", "高"), "中": ("tg-m", "中"), "低": ("tg-l", "低")}
    chunks: list[str] = []
    for row in kadian:
        tg1 = lv_map.get(row[1], ("tg-l", row[1]))
        tg2 = lv_map.get(row[2], ("tg-l", row[2]))
        items = "".join(f"<li>{html_lib.escape(str(x))}</li>" for x in row[3])
        chunks.append(
            f'<div class="kd"><div class="kh"><span>{html_lib.escape(row[0])}</span>'
            f'<span class="lv">时间杠杆<span class="tg {tg1[0]}">{tg1[1]}</span> '
            f'自主可控<span class="tg {tg2[0]}">{tg2[1]}</span></span></div><ul>{items}</ul></div>'
        )
    return "".join(chunks)


def render_steps_html(steps: list[tuple[str, str]]) -> str:
    rows: list[str] = []
    for i, (prio, text) in enumerate(steps, 1):
        rows.append(
            f'<li draggable="true" data-i="{i - 1}">'
            f'<span class="rk">{i}</span>'
            f'<span class="pr pr-{html_lib.escape(prio)}">{html_lib.escape(prio)}</span>'
            f'<span class="tx">{html_lib.escape(text)}</span>'
            f'<span class="mv"><button type="button" data-mv="-1" aria-label="Move up">▲</button>'
            f'<button type="button" data-mv="1" aria-label="Move down">▼</button></span></li>'
        )
    return f'<ol id="steps" class="steps-static">{"".join(rows)}</ol>'


def render_detail_section(group: dict, cats: list[str]) -> str:
    opts = lambda current: "".join(
        f'<option{" selected" if c == current else ""}>{html_lib.escape(c)}</option>' for c in cats
    )
    html_parts: list[str] = []
    flag = group.get("flag") or ""
    flag_html = f' <span style="color:#e74c3c">{html_lib.escape(flag)}</span>' if flag else ""
    html_parts.append(
        f'<div class="l1 open"><div class="l1h">'
        f'<span class="nm">{html_lib.escape(group["name"])}{flag_html}</span>'
        f'<span class="tv">{html_lib.escape(group["tv"])}</span></div><div class="l1b">'
    )
    for s in group.get("l2", []):
        html_parts.append(
            f'<div class="l2blk"><div class="l2t">{html_lib.escape(s["name"])} '
            f'<span>{html_lib.escape(s["days"])} · {html_lib.escape(s["owner"])}</span></div>'
        )
        for it in s.get("chips", []):
            uid = f"{group['name']}_{s['name']}_{it.get('code','')}_{it['name']}"
            uid = re.sub(r"\W+", "_", uid)[:40]
            has_pop = bool(it.get("sols"))
            a_cls = "a clk" if has_pop else "a"
            onclick = ' onclick="this.closest(\'.itm\').classList.toggle(\'open\')"' if has_pop else ""
            nb = '<span class="nb">新</span>' if it.get("new") else ""
            ex = '<span class="ex">▾方案</span>' if has_pop else ""
            html_parts.append(
                f'<div class="itm{" open" if has_pop and it.get("new") else ""}" id="i{uid}">'
                f'<div class="row"><div class="{a_cls}"{onclick}>'
                f'<span class="cd">{html_lib.escape(it.get("code") or "")}</span>'
                f'{html_lib.escape(it["name"])}{nb}{ex}</div>'
                f'<div><select data-id="{uid}" data-f="cat">{opts(it.get("cat", cats[0]))}</select></div>'
                f'<div><input data-id="{uid}" data-f="own" value="{html_lib.escape(it.get("owner") or "")}"></div></div>'
            )
            if it.get("pain"):
                html_parts.append(f'<div class="pain">⚠ {html_lib.escape(it["pain"])}</div>')
            if has_pop:
                html_parts.append('<div class="pop">')
                for x in it["sols"]:
                    owner = f'<div class="so">👤 {html_lib.escape(x["o"])}</div>' if x.get("o") and x["o"] != "—" else ""
                    html_parts.append(
                        f'<div class="si"><div class="st">{html_lib.escape(x["t"])}</div>{owner}'
                        f'<div class="sb">{x["b"]}</div></div>'
                    )
                if it.get("note"):
                    html_parts.append(f'<div class="snote">⚠️ {html_lib.escape(it["note"])}</div>')
                html_parts.append("</div>")
            html_parts.append("</div>")
        html_parts.append("</div>")
    html_parts.append("</div></div>")
    return "".join(html_parts)


def chunk_list(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def main() -> None:
    ref = REF.read_text(encoding="utf-8")
    src = SRC.read_text(encoding="utf-8")

    ref_style = extract_between(ref, "<style>", "</style>")
    ref_chrome = extract_between(ref, '<div class="deck-left-hover-anchor"', '<div class="slides-offset">')
    ref_script = extract_between(ref, "<script>", "</script>")
    orig_script = extract_between(src, "<script>", "</script>")

    wrap = extract_between(src, '<div class="wrap">', '</div>\n\n<script>')
    head_match = re.search(r"<div class=\"head\">(.*?)</div>", wrap, re.S)
    kpi_match = re.search(r'<div class="kpi">(.*?)</div>\s*', wrap, re.S)
    foot_match = re.search(r'<div class="foot">(.*?)</div>\s*$', wrap, re.S)

    kadian = parse_js_array(orig_script, "KADIAN") or []
    steps = parse_js_array(orig_script, "STEPS") or []
    data = parse_js_array(orig_script, "DATA") or []
    cats = parse_js_array(orig_script, "CATS") or []

    slides: list[str] = []
    sid = 0

    if head_match:
        slides.append(
            slide_shell(
                sid,
                f'<div class="head reveal-block">{head_match.group(1)}</div>',
                f"s{sid}-o0",
                extra_class=" title-slide",
            )
        )
        sid += 1

    if kpi_match:
        slides.append(
            slide_shell(sid, f'<div class="kpi reveal-block">{kpi_match.group(1)}</div>', f"s{sid}-o0")
        )
        sid += 1

    for cls, block_html in extract_div_blocks(wrap, "block"):
        bh_match = re.search(
            r'<div class="bh">(.*?)</div>\s*<div class="bd">(.*?)</div>\s*$', block_html, re.S
        )
        if not bh_match:
            continue
        bh, bd = bh_match.group(1), bh_match.group(2)

        if "整体总结" in bh:
            for chunk in split_summary_slides(bd):
                slides.append(
                    slide_shell(
                        sid,
                        block_wrap("整体总结", chunk, static=True),
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
                        block_wrap(bh, lead_match.group(0) + table_match.group(0)),
                        f"s{sid}-o0",
                    )
                )
                sid += 1
                rest = bd[table_match.end() :].strip()
            else:
                rest = bd
            if rest:
                bullets = re.search(r"<h3 class=\"sub\">规律</h3>\s*<ul class=\"clean\">.*?</ul>", rest, re.S)
                if bullets:
                    slides.append(
                        slide_shell(
                            sid,
                            block_wrap(bh, bullets.group(0)),
                            f"s{sid}-o0",
                        )
                    )
                    sid += 1
        elif "关键洞察 3" in bh:
            intro = (
                '<p class="lead">把数据分析与原始拆解中发现的<b>所有卡点</b>按根因归为五类,'
                "并标注各类的时间杠杆与自主可控度(先解卡点、再谈方案)。</p>"
            )
            warn = (
                '<div class="warn">时间杠杆高 + 自主可控度高的前两类,是应优先啃的大头;'
                "第五类(外部与物理约束)提效空间有限;香港全段拖、意大利偶发卡死属个例,不进系统主线。</div>"
            )
            for i, chunk in enumerate(chunk_list(kadian, 2)):
                body = intro if i == 0 else ""
                body += render_kadian_html(chunk)
                if i == len(chunk_list(kadian, 2)) - 1:
                    body += warn
                slides.append(
                    slide_shell(
                        sid,
                        block_wrap(
                            "关键洞察 3 · 卡点分类"
                            + (f" ({i + 1}/{len(chunk_list(kadian, 2))})" if len(kadian) > 2 else ""),
                            body,
                        ),
                        f"s{sid}-o0",
                    )
                )
                sid += 1
        elif "下一步计划" in bh:
            intro = (
                '<p class="lead lead-muted">以下为全部建议动作,按当前优先级从高到低排列;'
                "可拖动或用 ▲▼ 调整顺序。</p>"
            )
            warn = (
                '<div class="warn"><b>建议先行的前置动作:</b>验证关键路径——取延误单比对"PO / 发货计划就绪时间"'
                '与"货物物理可发时间",判断"货等纸"还是"纸等货",据此校准单证流投入的收益权重。</div>'
            )
            high = [s for s in steps if s[0] == "高"]
            mid = [s for s in steps if s[0] == "中"]
            low = [s for s in steps if s[0] in ("低", "降本")]
            bands = [("高优先级", high), ("中优先级", mid), ("低优先级 / 降本", low)]
            for label, band in bands:
                if not band:
                    continue
                body = intro if label == "高优先级" else ""
                body += render_steps_html(band)
                if label == "低优先级 / 降本":
                    body += warn
                slides.append(
                    slide_shell(
                        sid,
                        block_wrap(f"下一步计划 · {label}", body, static=True),
                        f"s{sid}-o0",
                    )
                )
                sid += 1
        elif "各环节详细拆解" in bh:
            bar = (
                '<div class="bar"><span class="note-edit">点动作名可展开方案详情;'
                '<span style="color:#EC008C">带 新</span> 为本次新增;分类/负责人可修改。</span>'
                '<button class="btn" type="button" onclick="exportCfg()">导出当前配置</button></div>'
                '<div class="colhdr"><div>环节动作</div><div>分类</div><div>负责人</div></div>'
            )
            for group in data:
                slides.append(
                    slide_shell(
                        sid,
                        block_wrap(
                            "各环节详细拆解 · " + group["name"],
                            bar + render_detail_section(group, cats),
                            open_=True,
                        ),
                        f"s{sid}-o0",
                        extra_class=" detail-slide",
                    )
                )
                sid += 1
        else:
            open_cls = "open" if "open" in cls else ""
            slides.append(
                slide_shell(
                    sid,
                    f'<div class="block {open_cls}"><div class="bh">{bh}</div><div class="bd">{bd}</div></div>',
                    f"s{sid}-o0",
                )
            )
            sid += 1

    if foot_match:
        slides.append(
            slide_shell(
                sid,
                f'<div class="foot reveal-block">{foot_match.group(1)}</div>',
                f"s{sid}-o0",
            )
        )

    slides_html = "\n\n".join(slides)

    extra_css = """
    /* === Report theme (Payoneer-adjacent pink) === */
    :root {
      --slide-bg-deep: #f5f5f5;
      --slide-bg-gradient: linear-gradient(165deg, #ffffff 0%, #fdf8fa 45%, #f5f0f3 100%);
      --text-primary: #383838;
      --font-display: 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
      --font-body: 'Microsoft YaHei', '微软雅黑', 'PingFang SC', sans-serif;
      --deck-chrome-bg: rgba(255, 255, 255, 0.97);
      --deck-chrome-border: rgba(236, 0, 140, 0.22);
      --deck-chrome-text: #383838;
      --deck-chrome-muted: #888;
      --deck-chrome-accent: #EC008C;
      --deck-chrome-shadow: 0 12px 40px rgba(196, 38, 117, 0.18);
      --deck-chrome-surface: #fffafd;
      --brand-deep: #C42675;
      --brand-accent: #EC008C;
    }
    body { font-family: var(--font-body); color: var(--text-primary); }
    .slide { background: var(--slide-bg-gradient); }
    .slide.title-slide .report-slide-body { display: flex; align-items: center; justify-content: center; }
    .slide.title-slide .head { width: 100%; margin: 0; }
    .slide.detail-slide .report-slide-body { font-size: clamp(0.5rem, 0.82vw, 0.68rem); }
    .report-slide-body {
      width: 100%; height: 100%; overflow: hidden;
      font-size: clamp(0.58rem, 0.98vw, 0.78rem);
      line-height: 1.5; pointer-events: auto;
    }
    body:not(.deck-edit-mode) .report-slide-body .deck-interactive { pointer-events: auto; }
    body.deck-edit-mode .report-slide-body .deck-interactive { pointer-events: none; }
    .report-slide-body .head {
      background: linear-gradient(135deg,var(--brand-deep),var(--brand-accent));
      color: #fff; padding: clamp(0.8rem,2vh,1.4rem) clamp(1rem,2.5vw,1.6rem);
      border-radius: clamp(8px,1vw,14px); margin-bottom: 0;
      box-shadow: 0 8px 28px rgba(196,38,117,.22);
    }
    .report-slide-body .head h1 {
      font-size: clamp(1.1rem, 2.6vw, 1.65rem); margin-bottom: clamp(0.2rem,.8vh,.45rem); font-weight: 700;
    }
    .report-slide-body .head p { font-size: clamp(0.58rem, 1.05vw, 0.78rem); opacity: .93; max-width: 95%; }
    .report-slide-body .kpi {
      display: grid; grid-template-columns: repeat(4, 1fr);
      gap: clamp(0.35rem, 1vw, 0.75rem); height: 100%; align-content: center;
    }
    .report-slide-body .kpi .c {
      background: #fff; border-radius: clamp(8px,1vw,12px);
      padding: clamp(0.5rem, 1.2vh, 0.85rem); text-align: center;
      box-shadow: 0 2px 8px rgba(0,0,0,.06); border: 1px solid rgba(236,0,140,.08);
    }
    .report-slide-body .kpi .v { font-size: clamp(0.95rem, 2vw, 1.35rem); font-weight: 700; color: var(--brand-accent); }
    .report-slide-body .kpi .l { font-size: clamp(0.52rem,.9vw,.68rem); color: #666; margin-top: .15rem; }
    .report-slide-body .kpi .s { font-size: clamp(0.48rem,.75vw,.58rem); color: #aaa; margin-top: .1rem; }
    .report-slide-body .block {
      background: #fff; border-radius: clamp(8px,1vw,12px);
      box-shadow: 0 2px 8px rgba(0,0,0,.05); overflow: hidden; height: 100%;
      display: flex; flex-direction: column; border: 1px solid rgba(236,0,140,.06);
    }
    .report-slide-body .block > .bh {
      flex-shrink: 0;
      padding: clamp(0.4rem, 1vh, 0.6rem) clamp(0.65rem, 1.5vw, 1rem);
      font-size: clamp(0.68rem, 1.25vw, 0.88rem); font-weight: 700;
      border-left: 4px solid var(--brand-accent);
      background: linear-gradient(90deg, rgba(236,0,140,.04), transparent);
    }
    .report-slide-body .block > .bd {
      flex: 1; min-height: 0; overflow: hidden;
      padding: 0 clamp(0.55rem, 1.4vw, 0.85rem) clamp(0.4rem, 1vh, 0.65rem);
      display: block !important;
    }
    .report-slide-body .block:not(.static) > .bh { cursor: pointer; }
    .report-slide-body h3.sub {
      font-size: clamp(0.65rem, 1.1vw, 0.8rem); color: var(--brand-deep);
      margin: clamp(0.25rem,.6vh,.4rem) 0 clamp(0.15rem,.4vh,.25rem);
    }
    .report-slide-body p.lead { font-size: clamp(0.58rem, .98vw, .74rem); margin: .2rem 0; }
    .report-slide-body p.lead-muted { color: #888; }
    .report-slide-body .hi {
      background: #F5D0E0; padding: 1px 4px; border-radius: 3px;
      font-weight: 600; color: var(--brand-deep);
    }
    .report-slide-body b.k { color: var(--brand-deep); }
    .report-slide-body ul.clean { list-style: none; margin: .15rem 0; }
    .report-slide-body ul.clean li {
      position: relative; padding: clamp(0.12rem,.3vh,.2rem) 0 clamp(0.12rem,.3vh,.2rem) .95rem;
      font-size: clamp(0.54rem, .9vw, .7rem);
    }
    .report-slide-body ul.clean li:before {
      content: "—"; position: absolute; left: 0; color: var(--brand-accent); font-weight: 700;
    }
    .report-slide-body .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: .4rem; margin-top: .3rem; }
    .report-slide-body .pcard {
      border: 1px solid #F5D0E0; border-radius: 8px; padding: .4rem .5rem; background: #fffafd;
    }
    .report-slide-body .pcard h4 { font-size: clamp(.58rem,.95vw,.72rem); color: var(--brand-accent); margin-bottom: .15rem; }
    .report-slide-body .pcard .row { font-size: clamp(.52rem,.85vw,.65rem); color: #555; margin: .1rem 0; }
    .report-slide-body .warn {
      background: #fff8ec; border: 1px solid #f5d99b; border-radius: 8px;
      padding: .4rem .55rem; font-size: clamp(.52rem,.85vw,.65rem); color: #7a5a1e; margin-top: .3rem;
    }
    .report-slide-body table.heat {
      border-collapse: collapse; width: 100%;
      font-size: clamp(.46rem,.72vw,.58rem); margin-top: .2rem;
    }
    .report-slide-body table.heat th {
      background: #faf0f6; color: #888; padding: 2px 2px; border: 1px solid #f0e0ea;
    }
    .report-slide-body table.heat td { padding: 3px 2px; text-align: center; border: 1px solid #f5eef2; }
    .report-slide-body table.heat td.cn { text-align: left; font-weight: 600; background: #fafafa; white-space: nowrap; }
    .report-slide-body .h0{background:#fff}.report-slide-body .h1{background:#fce8f3}
    .report-slide-body .h2{background:#fcbfe0}.report-slide-body .h3{background:#f987c2;color:#fff}
    .report-slide-body .h4{background:#EC008C;color:#fff}.report-slide-body .hx{color:#ccc}
    .report-slide-body .legend { font-size: clamp(.44rem,.65vw,.54rem); color: #aaa; margin-top: .15rem; }
    .report-slide-body .kd {
      border: 1px solid #F5D0E0; border-radius: 8px; padding: .35rem .5rem;
      margin-bottom: .28rem; background: #fffafd;
    }
    .report-slide-body .kd .kh {
      font-size: clamp(.58rem,.95vw,.72rem); font-weight: 700; color: var(--brand-deep);
      display: flex; justify-content: space-between; gap: .4rem; flex-wrap: wrap;
    }
    .report-slide-body .tg {
      display: inline-block; padding: 1px 6px; border-radius: 8px;
      font-size: clamp(.42rem,.6vw,.52rem); margin-left: 3px;
    }
    .report-slide-body .tg-h { background: #EC008C; color: #fff; }
    .report-slide-body .tg-m { background: #FCA1D4; color: #7a2555; }
    .report-slide-body .tg-l { background: #eee; color: #999; }
    .report-slide-body .kd ul { list-style: none; }
    .report-slide-body .kd li {
      font-size: clamp(.5rem,.82vw,.64rem); color: #555;
      padding: .08rem 0 .08rem .85rem; position: relative;
    }
    .report-slide-body .kd li:before {
      content: "·"; position: absolute; left: 2px; color: var(--brand-accent); font-weight: 700;
    }
    .report-slide-body #steps, .report-slide-body .steps-static { list-style: none; margin: 0; padding: 0; }
    .report-slide-body #steps li, .report-slide-body .steps-static li {
      display: flex; align-items: flex-start; gap: 5px; background: #fff; border: 1px solid #eee;
      border-radius: 6px; padding: clamp(4px,.8vh,6px) clamp(6px,1vw,8px);
      margin-bottom: 4px; cursor: grab; font-size: clamp(.5rem,.82vw,.64rem);
    }
    .report-slide-body #steps li .rk { font-weight: 700; color: var(--brand-accent); width: 16px; text-align: center; flex-shrink: 0; }
    .report-slide-body .pr-高{background:#EC008C;color:#fff}.report-slide-body .pr-中{background:#FCA1D4;color:#7a2555}
    .report-slide-body .pr-低{background:#f0e0ea;color:#a05a80}.report-slide-body .pr-降本{background:#eee;color:#888}
    .report-slide-body .l1 { border: 1px solid #eee; border-radius: 8px; margin-bottom: .28rem; overflow: hidden; }
    .report-slide-body .l1 > .l1h {
      padding: .35rem .5rem; cursor: pointer; background: #fafafa;
      display: flex; justify-content: space-between; gap: .4rem; align-items: center;
    }
    .report-slide-body .l1 > .l1h .nm { font-size: clamp(.58rem,.95vw,.72rem); font-weight: 700; }
    .report-slide-body .l1 > .l1b { display: block; padding: .2rem .4rem .35rem; overflow: hidden; }
    .report-slide-body .l2blk .l2t {
      font-size: clamp(.52rem,.85vw,.65rem); font-weight: 700; color: var(--brand-deep);
      padding: .2rem 0; border-bottom: 1px solid #f2e6ee;
    }
    .report-slide-body .colhdr {
      display: grid; grid-template-columns: 1.8fr 110px 120px; gap: 6px;
      font-size: clamp(.44rem,.65vw,.54rem); color: #aaa; padding: 2px 2px 0; font-weight: 600;
    }
    .report-slide-body .itm .row {
      display: grid; grid-template-columns: 1.8fr 110px 120px; gap: 6px;
      align-items: center; padding: 4px 2px;
    }
    .report-slide-body .itm .a { font-weight: 600; font-size: clamp(.48rem,.78vw,.62rem); }
    .report-slide-body .itm .a.clk { cursor: pointer; }
    .report-slide-body .itm .a.clk:hover { color: var(--brand-accent); }
    .report-slide-body .itm select, .report-slide-body .itm input {
      width: 100%; font-size: clamp(.44rem,.68vw,.56rem); padding: 2px 3px;
      border: 1px solid #e2d2dc; border-radius: 4px; background: #fffafd; font-family: inherit;
    }
    .report-slide-body .pop {
      display: none; background: #f8faff; border-left: 3px solid var(--brand-accent);
      margin: 0 2px 6px; padding: 6px 8px; border-radius: 0 6px 6px 0;
    }
    .report-slide-body .itm.open .pop { display: block; }
    .report-slide-body .btn {
      font-size: clamp(.48rem,.75vw,.6rem); padding: 3px 8px; border: 1px solid var(--brand-accent);
      color: var(--brand-accent); background: #fff; border-radius: 5px; cursor: pointer;
    }
    .report-slide-body .bar { display: flex; gap: 6px; align-items: center; margin: .25rem 0; flex-wrap: wrap; }
    .report-slide-body .note-edit { font-size: clamp(.44rem,.65vw,.54rem); color: #bbb; flex: 1; }
    .report-slide-body .foot {
      font-size: clamp(.5rem,.8vw,.65rem); color: #aaa; text-align: center;
      display: flex; align-items: center; justify-content: center; height: 100%;
    }
    body.deck-edit-mode .report-slide-body select,
    body.deck-edit-mode .report-slide-body input,
    body.deck-edit-mode .report-slide-body button,
    body.deck-edit-mode .report-slide-body #steps li { pointer-events: none; }
    @media (max-height: 700px) {
      .report-slide-body { font-size: clamp(.52rem,.88vw,.68rem); }
      .slide.detail-slide .report-slide-body { font-size: clamp(.46rem,.75vw,.58rem); }
    }
    @media (max-height: 600px) {
      .report-slide-body .kpi { grid-template-columns: repeat(2, 1fr); }
    }
    """

    deck_interactive_js = """
// === Deck-local interactivity (present mode) ===
(function() {
  function initReportBlocks() {
    document.querySelectorAll('.report-slide-body .block:not(.static) > .bh').forEach(function(h) {
      if (h.dataset.bound) return;
      h.dataset.bound = '1';
      h.addEventListener('click', function() { h.parentElement.classList.toggle('open'); });
    });
  }
  function bindSteps(root) {
    var ol = root || document;
    ol.querySelectorAll('.steps-static li, #steps li').forEach(function(li) {
      if (li.dataset.stepBound) return;
      li.dataset.stepBound = '1';
      li.querySelectorAll('.mv button').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
          e.stopPropagation();
          if (document.body.classList.contains('deck-edit-mode')) return;
          var list = li.parentElement;
          var items = Array.from(list.children);
          var i = items.indexOf(li);
          var d = parseInt(btn.getAttribute('data-mv') || btn.textContent.trim() === '▲' ? -1 : 1, 10);
          if (btn.textContent.trim() === '▲') d = -1;
          if (btn.textContent.trim() === '▼') d = 1;
          var j = i + d;
          if (j < 0 || j >= items.length) return;
          list.insertBefore(li, d < 0 ? items[j] : items[j].nextSibling);
          Array.from(list.children).forEach(function(x, idx) {
            var rk = x.querySelector('.rk');
            if (rk) rk.textContent = idx + 1;
          });
        });
      });
    });
  }
  function exportCfg() {
    var rows = [['环节','编码','动作','分类','负责人']];
    document.querySelectorAll('.itm').forEach(function(itm) {
      var id = itm.id.replace(/^i/, '');
      var nameEl = itm.querySelector('.a');
      var catEl = itm.querySelector('select[data-f="cat"]');
      var ownEl = itm.querySelector('input[data-f="own"]');
      if (!nameEl || !catEl || !ownEl) return;
      var code = (itm.querySelector('.cd') || {}).textContent || '';
      rows.push(['', code.trim(), nameEl.textContent.replace(/▾方案|新/g,'').trim(), catEl.value, ownEl.value]);
    });
    var text = rows.map(function(r){ return r.join('\\t'); }).join('\\n');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function(){ alert('已复制配置到剪贴板'); });
    } else {
      prompt('复制以下配置', text);
    }
  }
  window.exportCfg = exportCfg;
  function boot() {
    initReportBlocks();
    bindSteps(document);
    document.querySelectorAll('.report-slide-body .block > .bd').forEach(function(bd) {
      if (!bd.querySelector('.deck-interactive')) {
        var w = document.createElement('div');
        w.className = 'deck-interactive';
        while (bd.firstChild) w.appendChild(bd.firstChild);
        bd.appendChild(w);
      }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  window.addEventListener('deck-slides-refreshed', boot);
})();
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-deck-id="haiwai-caimai-leader-v2" data-mobile-adaptation="desktop-default" data-template-edit-mode="components">
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
{deck_interactive_js}
</script>
</body>
</html>
"""

    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
