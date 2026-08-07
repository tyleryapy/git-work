#!/usr/bin/env python3
"""Build single-slide editable 整体总结 deck with individually movable objects."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / ".cursor/skills/frontend-slides-editable/examples/editable-deck-reference.html"
THEME_SRC = ROOT / "presentations/海外采买时效分析_买手leader版-editable.html"
OUT = ROOT / "presentations/整体总结-editable.html"
CONVERT = ROOT / "scripts/convert-report-to-editable-deck.py"

# Body content (matches user brief); key phrases highlighted for scanability.
SUMMARY_OBJECTS: list[tuple[str, float, float, float, float]] = [
    (
        '<p class="lead"><b class="k">一句话定性:</b>海外提货到首次上架,典型单约 40 天(目标 21 天)。'
        '时间主要不消耗在"货在路上",而在<span class="hi">单证与资料在链路里的等待和反复处理</span>。</p>',
        2.5,
        5.0,
        95.0,
        9.0,
    ),
    (
        """<h3 class="sub">问题的本质:两条</h3>
<ul class="clean">
<li><b>瓶颈在"单证与资料流",不在物理搬运。</b>三个最耗时环节全部是建单 / 备案 / 资料 / 发运单证类;而提货、入仓、运输等物理环节都不慢——说明货往往是"备好了在等资料与单证"。</li>
<li><b>资料与单证靠人工重复处理、流程串行且缺前置。</b>同一批信息在多环节被反复录入,资料要等质检报告出来才开始做,该早提醒的没前置——这才是资料流慢、且偶发卡死的根因。</li>
</ul>""",
        2.5,
        14.0,
        95.0,
        17.0,
    ),
    (
        """<h3 class="sub">三个最耗时的环节(按严重度)</h3>
<ul class="clean">
<li><b>① 质检报告 → 建 PR 资料</b>(全链路<span class="hi">最大单块,典型约 12 天</span>):资料、备案、建单的手工工作。</li>
<li><b>② PR 审核 → PO 生成</b>:正常单 &lt;1 天,但少数单卡到上百天,<span class="hi">具体原因待下钻</span>。</li>
<li><b>③ PO → 发货计划提交</b>:供应商资料(发票 / CheckList / SLI)不及时,叠加物流拖累。</li>
</ul>""",
        2.5,
        31.0,
        95.0,
        15.0,
    ),
    (
        '<div class="warn"><b>一个结构性认知:</b>这条链是"物理流(提货→质检→运输)"和"单证流(建PR→PO→发运)"'
        "<b>并行推进</b>,各段时间不能简单相加。因此决定总时长的是关键路径。初步判断单证流很可能就是关键路径"
        "(货已备好、在等资料/PO/清关),此点建议团队优先验证——它决定后续投入的重心。</div>",
        2.5,
        46.0,
        95.0,
        11.0,
    ),
    ('<h3 class="sub">分四类来解决</h3>', 2.5, 57.0, 95.0, 4.0),
    (
        """<div class="pcard"><h4>A · 造工具、减重复(AI + 系统串联)</h4>
<div class="row"><b>最关键:</b>从供单信息前置生成商品基础资料 / PDC,减少建 PR 时重复录入(主资料与合格证的复用流程需另行梳理,不宜一刀切)</div></div>""",
        2.5,
        61.0,
        46.0,
        17.0,
    ),
    (
        """<div class="pcard"><h4>B · 抓异常、通审批</h4>
<div class="row"><b>最关键:</b>下钻 PR→PO 卡到上百天的具体原因,据此改进</div>
<div class="row"><b>可较快启动:</b>启用现有全链路看板的超时预警 + 主动督办机制</div></div>""",
        51.5,
        61.0,
        46.0,
        17.0,
    ),
    (
        """<div class="pcard"><h4>C · 供应商前置(资料 + 备货)</h4>
<div class="row"><b>最关键:</b>推行随货资料包,一次前置消掉下游多段"催资料"</div>
<div class="row"><b>可较快启动:</b>先对头部供应商试点</div></div>""",
        2.5,
        79.0,
        46.0,
        17.0,
    ),
    (
        """<div class="pcard"><h4>D · 结构性物理(欧洲物流 / Hub)</h4>
<div class="row"><b>最关键:</b>Hub 仓招标(意 / 港)+ 货代 SLA</div>
<div class="row"><b>节奏:</b>周期长,非近期主战场</div></div>""",
        51.5,
        79.0,
        46.0,
        17.0,
    ),
]

EXTRA_CSS = """
    /* === Summary slide: single-page density === */
    .slide.summary-slide .report-slide-body {
      font-size: clamp(0.52rem, 0.88vw, 0.72rem);
      line-height: 1.42;
    }
    .slide.summary-slide .slide-block-chrome {
      padding-top: clamp(0.25rem, 0.6vh, 0.45rem);
    }
    .slide.summary-slide .report-slide-body h3.sub {
      margin: clamp(0.12rem, 0.35vh, 0.22rem) 0 clamp(0.08rem, 0.25vh, 0.15rem);
    }
    .slide.summary-slide .report-slide-body ul.clean li {
      padding: clamp(0.1rem, 0.3vh, 0.18rem) 0 clamp(0.1rem, 0.3vh, 0.18rem) 1rem;
    }
    .slide.summary-slide .report-slide-body .warn {
      margin: 0;
      padding: clamp(0.25rem, 0.65vh, 0.4rem) clamp(0.4rem, 0.95vw, 0.6rem);
      font-size: clamp(0.5rem, 0.82vw, 0.66rem);
      line-height: 1.38;
    }
    .slide.summary-slide .report-slide-body .pcard {
      padding: clamp(0.25rem, 0.6vh, 0.38rem) clamp(0.32rem, 0.75vw, 0.48rem);
    }
    @media (max-height: 700px) {
      .slide.summary-slide .report-slide-body { font-size: clamp(0.48rem, 0.82vw, 0.64rem); }
    }
    @media (max-height: 600px) {
      .slide.summary-slide .report-slide-body { font-size: clamp(0.44rem, 0.75vw, 0.58rem); line-height: 1.35; }
    }
"""

REPORT_BOOT = """
// === Deck-local interactivity (present mode) ===
(function() {
  function initReportBlocks() {
    document.querySelectorAll('.report-slide-body .block:not(.static) > .bh').forEach(function(h) {
      if (h.dataset.bound) return;
      h.dataset.bound = '1';
      h.addEventListener('click', function() { h.parentElement.classList.toggle('open'); });
    });
  }
  function boot() { initReportBlocks(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  window.addEventListener('deck-slides-refreshed', boot);
})();
"""


def load_convert_module():
    spec = importlib.util.spec_from_file_location("convert_report", CONVERT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["convert_report"] = module
    spec.loader.exec_module(module)
    return module


def extract_styles(html: str) -> str:
    start = html.index("<style>") + len("<style>")
    end = html.index("</style>")
    return html[start:end]


def extract_chrome(html: str) -> str:
    body_start = html.index("<body>") + len("<body>")
    slides_start = html.index('<div class="slides-offset">')
    return html[body_start:slides_start].strip()


def extract_script(html: str) -> str:
    start = html.index("<script>") + len("<script>")
    end = html.rindex("</script>")
    return html[start:end]


def main() -> None:
    convert = load_convert_module()
    theme_html = THEME_SRC.read_text(encoding="utf-8")
    ref_html = REF.read_text(encoding="utf-8")

    styles = extract_styles(theme_html).rstrip()
    if EXTRA_CSS.strip() not in styles:
        styles += "\n" + EXTRA_CSS

    slide_html = convert.build_slide(
        0,
        SUMMARY_OBJECTS,
        block_header="整体总结",
        extra_class=" summary-slide",
    )

    chrome = extract_chrome(ref_html)
    script = extract_script(ref_html).rstrip()
    if "initReportBlocks" not in script:
        script += "\n" + REPORT_BOOT

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN" data-deck-id="zhengti-zongjie-v2" data-mobile-adaptation="desktop-default" data-template-edit-mode="components">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>整体总结 · Editable</title>
  <style>
{styles}
  </style>
</head>
<body>
{chrome}

<div class="slides-offset">
{slide_html}
</div>

<script>
{script}
</script>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"Wrote {OUT} ({len(doc):,} bytes, {len(SUMMARY_OBJECTS)} objects)")


if __name__ == "__main__":
    main()
