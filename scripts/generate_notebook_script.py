# -*- coding: utf-8 -*-
"""
Generate comprehensive notebook walkthrough script (PDF).
Typography: Poppins | Color scheme: professional blue palette.
Output: Documentations/PCSPF_Capstone_Comprehensive_Notebook_Script.pdf
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.utils import ImageReader

from audit_content import PREPROCESSING_DECISIONS, PROJECT, RESULTS, section_processes
from notebook_script_content import (
    FUTURE_WORK_SCRIPT,
    HOW_TO_USE,
    INTRODUCTION,
    KEY_RESULTS_TABLE,
    LIMITATIONS_SCRIPT,
    NOTEBOOK_SCRIPT,
    PIPELINE,
    SECTION_CLOSERS,
    SECTION_OPENERS,
    section_title,
)
from study_guide_content import SECTION_WALKTHROUGHS
from study_guide_figures import FIGURE_GUIDE

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "Documentations" / "fonts"
FIGURES_DIR = ROOT / "figures"
OUTPUT_PDF = ROOT / "Documentations" / NOTEBOOK_SCRIPT["output_filename"]

C_NAVY = colors.HexColor("#1E3A5F")
C_BLUE = colors.HexColor("#2563EB")
C_BLUE_LIGHT = colors.HexColor("#DBEAFE")
C_BLUE_PALE = colors.HexColor("#EFF6FF")
C_BORDER = colors.HexColor("#BFDBFE")
C_TEXT = colors.HexColor("#1E293B")
C_MUTED = colors.HexColor("#64748B")
C_WHITE = colors.white

MARGIN = 2.2 * cm
TOP_MARGIN = 2.6 * cm
BOTTOM_MARGIN = 2.2 * cm
USABLE_W = A4[0] - 2 * MARGIN
MAX_FIG_H = 7.5 * cm

for name, file in [
    ("Poppins", "Poppins-Regular.ttf"),
    ("Poppins-Bold", "Poppins-Bold.ttf"),
    ("Poppins-SemiBold", "Poppins-SemiBold.ttf"),
    ("Poppins-Italic", "Poppins-Italic.ttf"),
]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))


def build_styles():
    base = getSampleStyleSheet()
    st = {}

    def s(name, **kw):
        font = kw.pop("fontName", "Poppins")
        st[name] = ParagraphStyle(name, parent=base["Normal"], fontName=font, **kw)
        return st[name]

    s("CoverTitle", fontName="Poppins-Bold", fontSize=22, leading=28, alignment=TA_CENTER,
      textColor=C_NAVY, spaceAfter=6)
    s("CoverSubtitle", fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=C_MUTED, spaceAfter=4)
    s("Title", fontName="Poppins-Bold", fontSize=20, leading=26, alignment=TA_CENTER,
      textColor=C_NAVY, spaceAfter=8)
    s("Subtitle", fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=C_MUTED, spaceAfter=5)
    s("CoverMeta", fontSize=9, leading=13, alignment=TA_CENTER, textColor=C_TEXT, spaceAfter=3)
    s("H1", fontName="Poppins-Bold", fontSize=14, leading=19, textColor=C_NAVY,
      spaceBefore=0, spaceAfter=0)
    s("H2", fontName="Poppins-SemiBold", fontSize=11, leading=15, textColor=C_BLUE,
      spaceBefore=0, spaceAfter=0)
    s("H3", fontName="Poppins-SemiBold", fontSize=9.5, leading=13, textColor=C_NAVY,
      spaceBefore=0, spaceAfter=0)
    s("Body", fontSize=9.5, leading=14, alignment=TA_JUSTIFY, textColor=C_TEXT, spaceAfter=6)
    s("Bullet", fontSize=9.5, leading=13, leftIndent=14, textColor=C_TEXT, spaceAfter=3)
    s("TOC", fontName="Poppins-SemiBold", fontSize=9.5, leading=14, textColor=C_NAVY, spaceAfter=2)
    s("TOCSub", fontSize=9, leading=13, leftIndent=12, textColor=C_TEXT, spaceAfter=2)
    s("TH", fontName="Poppins-SemiBold", fontSize=7.5, leading=10, textColor=C_WHITE, alignment=TA_LEFT)
    s("TD", fontSize=7.5, leading=11, alignment=TA_LEFT, textColor=C_TEXT)
    s("Caption", fontName="Poppins-Italic", fontSize=8, leading=11, textColor=C_MUTED, spaceAfter=4)
    s("CalloutLabel", fontName="Poppins-SemiBold", fontSize=8.5, leading=11, textColor=C_BLUE, spaceAfter=0)
    s("CalloutBody", fontSize=9, leading=13, textColor=C_TEXT, spaceBefore=0, spaceAfter=0)
    s("ClinicalLabel", fontName="Poppins-SemiBold", fontSize=8.5, leading=11, textColor=C_NAVY, spaceAfter=0)
    return st


ST = build_styles()


def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def para(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(esc(text).replace("\n", "<br/>"), ST[style])


def bullet(text: str) -> Paragraph:
    return Paragraph(f"- {esc(text)}", ST["Bullet"])


def th_cell(text: str) -> Paragraph:
    return Paragraph(esc(str(text)), ST["TH"])


def td_cell(text: str) -> Paragraph:
    return Paragraph(esc(str(text)), ST["TD"])


def section_heading(title: str) -> list:
    return [
        Spacer(1, 6),
        para(title, "H1"),
        Spacer(1, 5),
        HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=0, spaceBefore=0),
        Spacer(1, 12),
    ]


def sub_heading(title: str) -> list:
    return [Spacer(1, 8), para(title, "H2"), Spacer(1, 5)]


def callout_box(label: str, body: str, label_style: str = "CalloutLabel") -> Table:
    t = Table(
        [[para(label, label_style)], [para(body, "CalloutBody")]],
        colWidths=[USABLE_W],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_BLUE_PALE),
        ("BOX", (0, 0), (-1, -1), 0.75, C_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
        ("TOPPADDING", (0, 1), (-1, 1), 4),
        ("BOTTOMPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def wrap_table(headers, rows, col_fracs) -> Table:
    widths = [USABLE_W * f for f in col_fracs]
    data = [[th_cell(h) for h in headers]]
    data += [[td_cell(c) for c in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_BLUE_PALE]),
        ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def embed_figure(filename: str, caption: str = "", max_h: float = MAX_FIG_H) -> list:
    path = FIGURES_DIR / filename
    out = [Spacer(1, 4)]
    if not path.exists():
        out.append(para(f"[Figure not found - run notebook: figures/{filename}]", "Caption"))
        if caption:
            out.append(para(caption, "Caption"))
        return out
    ir = ImageReader(str(path))
    iw, ih = ir.getSize()
    scale = min(USABLE_W / iw, max_h / ih)
    w, h = iw * scale, ih * scale
    out.append(Image(str(path), width=w, height=h))
    out.append(Spacer(1, 3))
    if caption:
        out.append(para(caption, "Caption"))
    return out


def figures_for_process(process_id: str) -> list[dict]:
    return [f for f in FIGURE_GUIDE if f["section"] == process_id]


def figure_block(fig: dict) -> list:
    s = []
    s.extend(sub_heading(f"Figure {fig['num']}: {fig['file']} (Notebook Section {fig['section']})"))
    s.append(para(f"What it shows: {fig['shows']}", "Body"))
    max_h = 6.0 * cm if "heatmap" in fig["file"] or "correlation" in fig["file"] else MAX_FIG_H
    s.extend(embed_figure(
        fig["file"],
        f"Source: {PROJECT['notebook']}, n={PROJECT['n_patients']} | Section {fig['section']}",
        max_h=max_h,
    ))
    s.append(callout_box("Statistical interpretation", fig["interpretation"]))
    s.append(Spacer(1, 4))
    s.append(callout_box("Clinical interpretation", fig["clinical_interpretation"], "ClinicalLabel"))
    s.append(Spacer(1, 4))
    s.append(para(f"Presenter note - emphasize: {fig['point_out']}", "Body"))
    s.append(para(f"Do not claim: {fig['dont_claim']}", "Body"))
    s.append(Spacer(1, 10))
    return s


def process_block(proc: tuple) -> list:
    pid, name, technique, what, params, output, decision, simple = proc
    s = []
    s.extend(sub_heading(f"{pid} - {name}"))
    s.append(wrap_table(
        ["Aspect", "Detail"],
        [
            ["Technique / method", technique],
            ["What we did", what],
            ["Parameters", params],
            ["Output / artifact", output],
            ["Decision / rationale", decision],
        ],
        [0.22, 0.78],
    ))
    s.append(Spacer(1, 6))
    s.append(callout_box("Say in plain language", simple))
    s.append(Spacer(1, 6))
    for fig in figures_for_process(pid):
        s.extend(figure_block(fig))
    return s


def section_block(key: str) -> list:
    walk = SECTION_WALKTHROUGHS[key]
    proc = section_processes()[key]
    s = []
    s.extend(section_heading(f"Section {key}: {section_title(key).split(': ', 1)[-1]}"))
    s.append(callout_box("Opening script", SECTION_OPENERS[key]))
    s.append(Spacer(1, 6))
    s.append(para(walk["summary"], "Body"))
    s.append(Spacer(1, 4))
    s.append(callout_box("Section takeaway", walk["interpretation"]))
    s.append(Spacer(1, 8))
    s.append(para("Key outputs from this section:", "H3"))
    for out in walk["outputs"]:
        s.append(bullet(out))
    s.append(Spacer(1, 8))

    for proc in proc["processes"]:
        s.extend(process_block(proc))

    s.append(callout_box("Closing script - transition", SECTION_CLOSERS[key]))
    s.append(Spacer(1, 6))
    if key in {"8", "9"}:
        return s
    s.append(PageBreak())
    return s


def on_page(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(C_NAVY)
    canvas.rect(0, h - 0.35 * cm, w, 0.35 * cm, fill=1, stroke=0)
    canvas.setFillColor(C_BLUE)
    canvas.rect(0, h - 0.42 * cm, w, 0.07 * cm, fill=1, stroke=0)
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 1.3 * cm, w - MARGIN, 1.3 * cm)
    canvas.setFont("Poppins", 7)
    canvas.setFillColor(C_MUTED)
    canvas.drawString(
        MARGIN, 0.8 * cm,
        f"PCSPF Comprehensive Notebook Script | v{NOTEBOOK_SCRIPT['version']}",
    )
    canvas.drawRightString(w - MARGIN, 0.8 * cm, f"Page {doc.page}")
    canvas.restoreState()


def on_cover(canvas, doc):
    canvas.saveState()
    w, h = A4
    band_h = 5.2 * cm
    canvas.setFillColor(C_NAVY)
    canvas.rect(0, h - band_h, w, band_h, fill=1, stroke=0)
    canvas.setFillColor(C_BLUE)
    canvas.rect(0, h - band_h - 0.12 * cm, w, 0.12 * cm, fill=1, stroke=0)
    canvas.setFillColor(C_BLUE_PALE)
    canvas.rect(0, 0, w, 1.0 * cm, fill=1, stroke=0)
    canvas.setFillColor(C_BLUE)
    canvas.rect(0, 1.0 * cm, w, 0.08 * cm, fill=1, stroke=0)
    canvas.restoreState()


def build_story():
    today = date.today().strftime("%B %d, %Y")
    s = []

    # Cover
    s.append(Spacer(1, 5.8 * cm))
    s.append(para(NOTEBOOK_SCRIPT["title"], "Title"))
    s.append(Spacer(1, 0.3 * cm))
    s.append(para(NOTEBOOK_SCRIPT["subtitle"], "Subtitle"))
    s.append(Spacer(1, 1.4 * cm))
    s.append(para(PROJECT["course"], "CoverMeta"))
    s.append(para(PROJECT["institution"], "CoverMeta"))
    s.append(Spacer(1, 0.9 * cm))
    s.append(HRFlowable(width="55%", thickness=1, color=C_BLUE, hAlign="CENTER", spaceAfter=12))
    s.append(para(f"Version {NOTEBOOK_SCRIPT['version']} | {today}", "CoverMeta"))
    s.append(para(
        f"{PROJECT['notebook']} | {PROJECT['n_sections']} sections | 21 figures",
        "CoverMeta"))
    s.append(PageBreak())

    # TOC
    s.extend(section_heading("Table of Contents"))
    toc = [
        ("1.", "Introduction and How to Use This Script"),
        ("2.", "End-to-End Pipeline Map"),
        ("3.", "Key Results at a Glance"),
        ("4.", "Preprocessing Decisions Summary"),
        ("5.", "Section 1 - Project Setup and Imports"),
        ("6.", "Section 2 - Data Loading and Initial Inspection"),
        ("7.", "Section 3 - Exploratory Data Analysis"),
        ("8.", "Section 4 - Data Preprocessing"),
        ("9.", "Section 5 - Train-Test Split and Scaling"),
        ("10.", "Section 6 - Unsupervised Learning (K-Means)"),
        ("11.", "Section 7 - Supervised Learning (Random Forest)"),
        ("12.", "Section 8 - Synthesis and Bridging Analysis"),
        ("13.", "Section 9 - Conclusion"),
        ("14.", "Limitations and Future Work (Presenter Scripts)"),
    ]
    for num, title in toc:
        s.append(para(f"{num}  {title}", "TOCSub"))
    s.append(PageBreak())

    # Introduction
    s.extend(section_heading("1. Introduction and How to Use This Script"))
    s.append(para(INTRODUCTION, "Body"))
    s.append(Spacer(1, 6))
    s.append(para("How to use:", "H2"))
    for item in HOW_TO_USE:
        s.append(bullet(item))
    s.append(PageBreak())

    # Pipeline
    s.extend(section_heading("2. End-to-End Pipeline Map"))
    s.append(wrap_table(["Phase", "Notebook", "Key outputs"], PIPELINE, [0.08, 0.22, 0.70]))
    s.append(PageBreak())

    # Key results
    s.extend(section_heading("3. Key Results at a Glance"))
    s.append(wrap_table(["Metric", "Value"], KEY_RESULTS_TABLE, [0.42, 0.58]))
    s.append(Spacer(1, 10))
    s.append(wrap_table(
        ["Model (Section 7.5)", "Test Acc.", "Macro F1", "AUC", "Importance", "Notes"],
        [(m, a, f, u, i, n) for m, a, f, u, i, n in RESULTS["model_comparison"]],
        [0.21, 0.11, 0.10, 0.09, 0.17, 0.32],
    ))
    s.append(Spacer(1, 8))
    s.append(wrap_table(
        ["Cluster", "N", "% cohort", "Survival rate", "Profile"],
        [(c, n, pct, surv, prof) for c, n, pct, surv, prof in RESULTS["clusters"]],
        [0.09, 0.11, 0.12, 0.14, 0.54],
    ))
    s.append(PageBreak())

    # Preprocessing summary
    s.extend(section_heading("4. Preprocessing Decisions Summary"))
    s.append(para(
        "Full detail lives in notebook Section 4.10 and figure preprocessing_summary.png. "
        "Use this table as a quick reference during walkthrough.",
        "Body"))
    s.append(Spacer(1, 6))
    s.append(wrap_table(["Step", "Action", "Justification"], PREPROCESSING_DECISIONS, [0.26, 0.20, 0.54]))
    s.append(PageBreak())

    # Sections 1-9
    s.extend(section_heading("Notebook Walkthrough - Sections 1 through 9"))
    s.append(para(
        "Each section below follows the notebook order: opening script, summary, subsections "
        "with methodology tables, embedded figures where applicable, and a closing transition line.",
        "Body"))
    s.append(Spacer(1, 8))
    for key in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        s.extend(section_block(key))

    # Limitations / future work
    s.append(PageBreak())
    s.extend(section_heading("14. Limitations and Future Work (Presenter Scripts)"))
    s.append(callout_box("Limitations - say this clearly", LIMITATIONS_SCRIPT))
    s.append(Spacer(1, 10))
    s.append(callout_box("Future work - credible next steps", FUTURE_WORK_SCRIPT))
    s.append(Spacer(1, 14))
    s.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    s.append(Spacer(1, 8))
    s.append(para(
        f"End of notebook script. Regenerate: python scripts/generate_notebook_script.py | "
        f"Notebook: {PROJECT['notebook']}",
        "Body"))
    return s


def main():
    if not FONT_DIR.exists():
        raise FileNotFoundError(f"Fonts missing: {FONT_DIR}")
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title=NOTEBOOK_SCRIPT["title"],
    )
    doc.build(build_story(), onFirstPage=on_cover, onLaterPages=on_page)
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
