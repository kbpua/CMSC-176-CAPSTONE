# -*- coding: utf-8 -*-
"""Export PCSPF defense presentation slides to PDF (16:9, defense-ready sizing)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_presentation_html import CSS, build_slides

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PDF = ROOT / "Documentations" / "PCSPF_Capstone_Defense_Presentation.pdf"
PRINT_HTML = ROOT / "Documentations" / "_presentation_print.html"
FIGURES_URI = (ROOT / "figures").as_uri()

# 16:9 slide canvas (matches standard projector resolution)
SLIDE_W = 1920
SLIDE_H = 1080

CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]

# Print-only stylesheet: fixed px canvas, large fonts, full slide usage.
PRINT_CSS = f"""
@page {{ size: {SLIDE_W}px {SLIDE_H}px; margin: 0; }}
* {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}

html, body {{
  margin: 0 !important; padding: 0 !important;
  width: {SLIDE_W}px !important; overflow: visible !important;
  background: #fff !important; font-size: 30px !important;
}}

#deck {{ width: {SLIDE_W}px !important; height: auto !important; }}

.slide {{
  display: flex !important;
  flex-direction: column !important;
  width: {SLIDE_W}px !important;
  height: {SLIDE_H}px !important;
  min-height: {SLIDE_H}px !important;
  max-height: {SLIDE_H}px !important;
  overflow: hidden !important;
  page-break-after: always !important;
  break-after: page !important;
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  padding: 36px 44px 40px !important;
  box-sizing: border-box !important;
  background: #fff !important;
  position: relative !important;
}}
.slide:last-child {{ page-break-after: auto !important; break-after: auto !important; }}

.si {{
  max-width: none !important;
  width: 100% !important;
  height: 100% !important;
  flex: 1 !important;
  min-height: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  margin: 0 !important;
}}

.st {{
  font-size: 52px !important;
  line-height: 1.15 !important;
  margin-bottom: 20px !important;
  padding-bottom: 12px !important;
  flex-shrink: 0 !important;
}}

.snum {{ font-size: 22px !important; top: 0 !important; right: 4px !important; }}

.sb {{
  flex: 1 !important;
  min-height: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  font-size: 30px !important;
  line-height: 1.45 !important;
  overflow: hidden !important;
}}

.sb ul, .sb ol {{ margin: 8px 0 8px 32px !important; }}
.sb li {{ margin-bottom: 10px !important; font-size: 30px !important; }}
.sb h3 {{ font-size: 34px !important; margin: 10px 0 8px !important; }}
.sb p {{ margin-bottom: 10px !important; font-size: 30px !important; }}
.muted {{ font-size: 28px !important; }}
.fn {{ font-size: 20px !important; }}

/* Hero slides */
.hero-slide {{
  padding: 0 !important;
  background: linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#1e40af 100%) !important;
  color: #fff !important;
}}
.hero-slide .si {{
  justify-content: center !important;
  align-items: center !important;
  position: relative !important;
}}
.hero-inner {{
  max-width: 88% !important;
  width: 88% !important;
  padding: 0 !important;
  text-align: center !important;
}}
.hero-label {{
  font-size: 24px !important;
  padding: 12px 28px !important;
  margin-bottom: 28px !important;
}}
.hero-inner h1 {{
  font-size: 68px !important;
  line-height: 1.2 !important;
  margin-bottom: 18px !important;
}}
.section-inner h1 {{ font-size: 60px !important; }}
.hero-accent-bar {{ width: 120px !important; height: 5px !important; margin: 0 auto 24px !important; }}
.hero-sub {{ font-size: 36px !important; margin-bottom: 36px !important; }}
.hero-info p {{ font-size: 32px !important; }}
.hero-info .info-bold {{ font-size: 34px !important; }}
.hero-members {{ gap: 48px !important; margin-top: 16px !important; }}
.hero-members .member-name {{ font-size: 32px !important; }}

/* Two-column layout */
.lr-layout {{
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 36px !important;
  flex: 1 !important;
  min-height: 0 !important;
  align-items: start !important;
}}
.lr-left, .lr-right {{
  display: flex !important;
  flex-direction: column !important;
  min-height: 0 !important;
  justify-content: flex-start !important;
  gap: 12px !important;
}}

/* Problem statement slide */
.slide[data-slide="3"] .st {{
  margin-bottom: 16px !important;
  padding-bottom: 10px !important;
}}
.slide[data-slide="3"] .sb {{
  padding-top: 6px !important;
}}
.problem-layout {{
  grid-template-columns: 1.12fr 0.88fr !important;
  gap: 36px !important;
  align-items: flex-start !important;
  align-content: flex-start !important;
}}
.problem-layout .lr-left {{
  justify-content: flex-start !important;
  gap: 12px !important;
}}
.problem-layout .lr-right {{
  justify-content: flex-start !important;
}}
.problem-lead {{
  font-size: 30px !important;
  line-height: 1.55 !important;
  color: var(--tx) !important;
  margin: 0 0 20px 0 !important;
  padding: 0 !important;
  border: none !important;
}}
.problem-list {{
  list-style: none !important;
  margin: 0 !important;
  padding: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 14px !important;
}}
.problem-list li {{
  display: flex !important;
  gap: 18px !important;
  align-items: flex-start !important;
  background: var(--bp) !important;
  border-left: 5px solid var(--blue) !important;
  padding: 18px 22px !important;
  border-radius: 0 10px 10px 0 !important;
  flex: 0 0 auto !important;
}}
.problem-list .pli-n {{
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-width: 44px !important;
  height: 44px !important;
  background: var(--navy) !important;
  color: #fff !important;
  border-radius: 50% !important;
  font-size: 24px !important;
  font-weight: 700 !important;
  flex-shrink: 0 !important;
}}
.problem-list li span:last-child {{
  font-size: 28px !important;
  line-height: 1.45 !important;
  flex: 1 !important;
  padding-top: 4px !important;
}}
.problem-rq {{
  background: var(--navy) !important;
  color: #fff !important;
  border-radius: 12px !important;
  padding: 28px 30px !important;
  border-left: 6px solid var(--blue) !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 12px !important;
  flex: 0 0 auto !important;
}}
.problem-rq-tag {{
  font-size: 20px !important;
  font-weight: 600 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: #93c5fd !important;
}}
.problem-rq p {{
  font-size: 30px !important;
  line-height: 1.5 !important;
  margin: 0 !important;
  color: #f1f5f9 !important;
}}

/* Figures */
.fig-wrap {{
  flex: 0 0 auto !important;
  display: flex !important;
  flex-direction: column !important;
  margin-bottom: 8px !important;
}}
.fig-label {{ font-size: 28px !important; margin-bottom: 8px !important; flex-shrink: 0 !important; }}
.fig-slide .lr-left {{ justify-content: center !important; align-items: center !important; }}
.fig-slide .lr-left .fig-wrap {{ width: 100% !important; height: 100% !important; }}
.fig-wrap img {{
  width: 100% !important;
  max-width: 100% !important;
  height: auto !important;
  max-height: 460px !important;
  min-height: 0 !important;
  object-fit: contain !important;
  flex: 0 0 auto !important;
  border-radius: 6px !important;
}}
.fig-slide .fig-wrap img {{
  max-height: 520px !important;
  min-height: 380px !important;
}}
.fig-slide.dense-slide .lr-layout {{
  align-items: stretch !important;
  flex: 1 !important;
  min-height: 0 !important;
}}
.fig-slide.dense-slide .fig-wrap img {{
  max-height: 480px !important;
  min-height: 320px !important;
}}
.fig-right {{
  display: flex !important;
  flex-direction: column !important;
  gap: 10px !important;
  min-height: 0 !important;
  overflow: hidden !important;
  justify-content: space-evenly !important;
  flex: 1 !important;
}}
.fig-right.dense {{ gap: 10px !important; justify-content: space-evenly !important; }}
.fig-right.dense .dt {{ font-size: 22px !important; margin-bottom: 6px !important; }}
.fig-right.dense .dt th, .fig-right.dense .dt td {{ padding: 7px 10px !important; font-size: 22px !important; line-height: 1.35 !important; }}
.fig-right.dense .tbl-label {{ font-size: 24px !important; margin-bottom: 4px !important; }}
.fig-right.dense .banner {{ padding: 10px 14px !important; font-size: 24px !important; margin: 4px 0 !important; line-height: 1.4 !important; }}
.fig-right.dense .callout.compact {{ padding: 10px 14px !important; margin: 4px 0 !important; }}
.fig-right.dense .callout.compact p {{ font-size: 24px !important; line-height: 1.38 !important; }}
.fig-right.dense .callout.compact strong {{ font-size: 20px !important; }}
.fig-right ul {{ margin: 6px 0 6px 28px !important; }}
.fig-right li {{ font-size: 28px !important; margin-bottom: 8px !important; line-height: 1.45 !important; }}
.fig-right h3 {{ font-size: 30px !important; margin: 6px 0 !important; }}
.fig-right p {{ font-size: 28px !important; }}
.fig-right .banner {{ padding: 12px 16px !important; font-size: 26px !important; margin: 6px 0 !important; line-height: 1.4 !important; }}
.fig-label {{ font-size: 26px !important; }}
.callout.compact {{
  padding: 12px 16px !important;
  margin: 6px 0 !important;
  font-size: 26px !important;
  line-height: 1.42 !important;
}}
.callout.compact strong {{ font-size: 22px !important; margin-bottom: 6px !important; letter-spacing: 0.03em !important; }}
.callout.compact p {{ font-size: 26px !important; }}
.callout.defense {{ display: none !important; }}

/* Vertical lists */
.vt-list {{
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
  flex: 1 !important;
  min-height: 0 !important;
  justify-content: flex-start !important;
}}
.vt-list.balanced {{ justify-content: space-evenly !important; gap: 16px !important; }}
.vt-list.balanced .vt-item {{ padding: 20px 24px !important; }}
.vt-list.balanced .vt-item strong {{ font-size: 30px !important; }}
.vt-list.balanced .vt-item p {{ font-size: 26px !important; }}
.vt-item {{
  display: flex !important;
  gap: 18px !important;
  align-items: flex-start !important;
  padding: 18px 22px !important;
  border-left: 5px solid var(--blue) !important;
  border-radius: 0 10px 10px 0 !important;
  background: var(--bp) !important;
}}
.vt-num {{
  min-width: 44px !important;
  height: 44px !important;
  line-height: 44px !important;
  text-align: center !important;
  font-size: 22px !important;
  flex-shrink: 0 !important;
  background: var(--navy) !important;
  color: #fff !important;
  border-radius: 50% !important;
  font-weight: 700 !important;
}}
.vt-item strong {{ font-size: 28px !important; display: block !important; margin-bottom: 6px !important; }}
.vt-item p {{ font-size: 26px !important; line-height: 1.45 !important; margin: 0 !important; }}
.vt-list.compact {{ gap: 10px !important; justify-content: space-evenly !important; }}
.vt-list.compact .vt-item {{ padding: 11px 16px !important; }}
.vt-list.compact .vt-num {{ min-width: 34px !important; height: 34px !important; line-height: 34px !important; font-size: 18px !important; }}
.vt-list.compact .vt-item strong {{ font-size: 25px !important; margin-bottom: 4px !important; }}
.vt-list.compact .vt-item p {{ font-size: 22px !important; line-height: 1.38 !important; }}

/* Future Work (slide 28) - two-column grid avoids compressed single-column overflow */
.vt-list.future-work-grid {{
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 12px 28px !important;
  align-content: start !important;
  justify-content: stretch !important;
}}
.vt-list.future-work-grid .vt-item {{ padding: 12px 16px !important; }}
.vt-list.future-work-grid .vt-item strong {{ font-size: 24px !important; }}
.vt-list.future-work-grid .vt-item p {{ font-size: 21px !important; line-height: 1.42 !important; }}
.slide[data-slide="28"] .sb {{ overflow: visible !important; }}

/* Dual-table appendix (A4) - all 20 VIF rows visible in PDF */
.dual-table-layout {{
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 24px !important;
  align-items: start !important;
  flex: 1 !important;
}}
.dual-table-layout .tbl-label {{ display: none !important; }}
.dual-table-layout .dt {{ font-size: 19px !important; margin-bottom: 0 !important; }}
.dual-table-layout .dt th, .dual-table-layout .dt td {{
  padding: 7px 10px !important;
  font-size: 19px !important;
  line-height: 1.32 !important;
}}
.slide[data-slide="A4"] .sb {{ overflow: visible !important; }}
.slide[data-slide="A4"] .st {{ margin-bottom: 14px !important; }}

/* RF tuning comparison appendix (A9) - stacked full-width tables */
.slide[data-slide="A9"] .sb {{ overflow: visible !important; gap: 8px !important; }}
.slide[data-slide="A9"] .st {{ margin-bottom: 12px !important; padding-bottom: 8px !important; }}
.slide[data-slide="A9"] .sub {{ font-size: 20px !important; margin-bottom: 8px !important; }}
.slide[data-slide="A9"] .tuning-stack {{
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
  margin-bottom: 6px !important;
}}
.slide[data-slide="A9"] .tbl-label {{
  font-size: 18px !important;
  margin-bottom: 4px !important;
}}
.slide[data-slide="A9"] .tuning-stack .dt {{
  width: 100% !important;
  font-size: 17px !important;
  margin-bottom: 0 !important;
}}
.slide[data-slide="A9"] .tuning-stack .dt th, .slide[data-slide="A9"] .tuning-stack .dt td {{
  padding: 5px 10px !important;
  font-size: 17px !important;
  line-height: 1.28 !important;
}}
.slide[data-slide="A9"] .tuning-note {{
  padding: 10px 14px !important;
  margin: 0 !important;
  font-size: 18px !important;
  line-height: 1.35 !important;
}}
.slide[data-slide="A9"] .tuning-note strong {{
  font-size: 16px !important;
  margin-bottom: 4px !important;
  letter-spacing: 0.03em !important;
}}
.slide[data-slide="A9"] .tuning-note p {{ font-size: 18px !important; line-height: 1.35 !important; margin: 0 !important; }}
.slide[data-slide="A9"] .fn {{ font-size: 16px !important; margin-top: 4px !important; }}

/* Roadmap (legacy) */
.roadmap {{
  display: grid !important;
  grid-template-columns: repeat(4, 1fr) !important;
  grid-template-rows: 1fr 1fr !important;
  gap: 20px !important;
  flex: 1 !important;
  min-height: 0 !important;
  margin: 16px 0 !important;
  align-content: stretch !important;
}}
.ri {{
  display: flex !important;
  align-items: center !important;
  padding: 24px 20px !important;
  font-size: 30px !important;
  line-height: 1.3 !important;
  border-radius: 10px !important;
}}
.ri span {{
  font-size: 22px !important;
  padding: 4px 10px !important;
  margin-right: 10px !important;
}}

.fig-cap {{ font-size: 20px !important; margin-top: 6px !important; flex-shrink: 0 !important; }}
.full-fig {{
  width: auto !important;
  max-width: 100% !important;
  max-height: 780px !important;
  margin: 0 auto !important;
  display: block !important;
}}
.dual-fig {{
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 28px !important;
  flex: 1 !important;
  min-height: 0 !important;
}}
.dual-fig .fig-wrap img {{ max-height: 420px !important; min-height: 220px !important; }}

/* Tables */
.tbl-label {{ font-size: 24px !important; margin-bottom: 8px !important; }}
.dt {{ font-size: 22px !important; width: 100% !important; margin-bottom: 12px !important; }}
.dt th, .dt td {{ padding: 10px 14px !important; font-size: 22px !important; line-height: 1.35 !important; }}

/* Callouts & banners */
.callout {{
  padding: 14px 18px !important;
  margin: 8px 0 !important;
  font-size: 26px !important;
  line-height: 1.4 !important;
  border-radius: 8px !important;
}}
.callout strong {{ font-size: 22px !important; margin-bottom: 6px !important; }}
.callout p {{ font-size: 26px !important; margin: 0 !important; }}
.banner {{
  padding: 14px 20px !important;
  font-size: 28px !important;
  margin-bottom: 14px !important;
  line-height: 1.4 !important;
}}

/* Objectives, conclusion, checklist grids (legacy) */
.obj-grid, .conc-grid, .check-grid {{
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 20px !important;
  flex: 1 !important;
  min-height: 0 !important;
  align-content: stretch !important;
}}
.obj, .conc, .ci {{
  padding: 20px !important;
  font-size: 24px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
}}
.obj h3, .conc h3 {{ font-size: 28px !important; margin-bottom: 10px !important; }}
.obj p, .conc p {{ font-size: 24px !important; line-height: 1.4 !important; }}
.on {{
  width: 36px !important; height: 36px !important;
  line-height: 36px !important; font-size: 20px !important;
  margin-bottom: 8px !important;
}}
.ck {{ font-size: 28px !important; }}

/* Flow diagrams */
.flow-v {{ gap: 10px !important; margin-bottom: 16px !important; }}
.flow-h {{ gap: 12px !important; margin: 12px 0 !important; }}
.fb {{ padding: 14px 20px !important; font-size: 24px !important; }}
.fa {{ font-size: 28px !important; }}

/* Cluster cards */
.cluster-cards {{ gap: 16px !important; flex: 1 !important; align-items: stretch !important; }}
.cc {{ padding: 16px !important; font-size: 22px !important; line-height: 1.4 !important; flex: 1 !important; }}

/* Narrative / transparency */
.pq {{
  font-size: 26px !important;
  line-height: 1.5 !important;
  padding: 24px 28px !important;
  flex: 1 !important;
}}
.pq p {{ margin-bottom: 16px !important; font-size: 26px !important; }}
.transp {{ padding: 20px !important; flex: 1 !important; }}
.transp ul {{ font-size: 26px !important; }}
.fw-list {{ font-size: 26px !important; column-gap: 40px !important; flex: 1 !important; }}
.fw-list li {{ margin-bottom: 12px !important; }}

/* Thank you */
.ty {{ flex: 1 !important; justify-content: center !important; }}
.ty h1 {{ font-size: 72px !important; }}
.ty .sub {{ font-size: 36px !important; }}
.ty .team {{ font-size: 32px !important; }}

/* Sparse slides - vertically balance content */
.sb > .lr-layout {{ align-self: stretch !important; }}
.sb > .obj-grid, .sb > .check-grid, .sb > .conc-grid, .sb > .transp {{
  flex: 1 !important;
}}
.sb > .vt-list {{ flex: 1 !important; }}

.hero-members .member-name {{ font-size: 32px !important; }}
.hero-footer {{ margin-top: 28px !important; font-size: 24px !important; color: rgba(203,213,225,.85) !important; }}
.thank-hero .hero-inner h1 {{ font-size: 72px !important; }}
.thank-hero .hero-sub {{ font-size: 34px !important; margin-bottom: 36px !important; }}

.snotes, #ctl {{ display: none !important; }}
"""

PRINT_TMPL = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width={sw}, initial-scale=1"/>
<title>PCSPF Capstone Defense Presentation (Print)</title>
<style>{base_css}</style>
<style>{print_css}</style>
</head><body>
<div id="deck">{slides}</div>
</body></html>"""


def fix_asset_paths(html: str) -> str:
    return html.replace('src="../figures/', f'src="{FIGURES_URI}/')


def find_browser() -> Path:
    for path in CHROME_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Chrome or Edge not found. Install Google Chrome to export PDF.")


def build_print_html() -> str:
    slides = fix_asset_paths(build_slides())
    return PRINT_TMPL.format(
        sw=SLIDE_W, base_css=CSS, print_css=PRINT_CSS, slides=slides
    )


def export_pdf() -> None:
    PRINT_HTML.parent.mkdir(parents=True, exist_ok=True)
    PRINT_HTML.write_text(build_print_html(), encoding="utf-8")

    browser = find_browser()
    html_uri = PRINT_HTML.resolve().as_uri()
    if OUTPUT_PDF.exists():
        OUTPUT_PDF.unlink()

    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        f"--window-size={SLIDE_W},{SLIDE_H}",
        "--force-device-scale-factor=1",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=15000",
        f"--print-to-pdf={OUTPUT_PDF.resolve()}",
        html_uri,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0 or not OUTPUT_PDF.exists():
        raise RuntimeError(
            f"PDF export failed (code {result.returncode}).\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    pages = len(re.findall(r'<section class="slide', PRINT_HTML.read_text(encoding="utf-8")))
    size_kb = OUTPUT_PDF.stat().st_size / 1024
    PRINT_HTML.unlink(missing_ok=True)
    print(f"Wrote {OUTPUT_PDF} ({pages} slides, {size_kb:.0f} KB)")


def main() -> None:
    export_pdf()


if __name__ == "__main__":
    main()
