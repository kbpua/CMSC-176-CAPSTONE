# -*- coding: utf-8 -*-
"""
Generate PCSPF Capstone Ultimate Study Guide (PDF).
Typography: Poppins | Color scheme: standard professional blue palette.
Output: Documentations/PCSPF_Capstone_Ultimate_Study_Guide.pdf
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
from reportlab.lib.utils import ImageReader
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

from audit_content import PROJECT
from study_guide_content import (
    CORE_FINDING,
    DATASET_FEATURES,
    DATASET_OVERVIEW,
    DEFENSE_SCRIPTS,
    EXECUTIVE_OVERVIEW,
    FUNCTION_REFERENCE,
    NUMBER_BANK,
    PREPROCESSING_EXTENDED,
    PROJECT_IDENTITY,
    QA_BANK,
    SECTION_WALKTHROUGHS,
    SLIDE_SECTION_MAP,
    STUDY_GUIDE,
    SUPERVISED_COMPARISON_A,
    SUPERVISED_COMPARISON_B,
    SUPERVISED_TECHNIQUE_JUSTIFICATION,
    TECHNIQUE_DEEP_DIVES,
    UNSUPERVISED_COMPARISON_A,
    UNSUPERVISED_COMPARISON_B,
    UNSUPERVISED_TECHNIQUE_JUSTIFICATION,
    WHY_DID,
    WHY_DID_NOT,
    WHY_NOT_DIFFERENT_MODEL,
)
from study_guide_figures import FIGURE_GUIDE

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "Documentations" / "fonts"
FIGURES_DIR = ROOT / "figures"
OUTPUT_PDF = ROOT / "Documentations" / "PCSPF_Capstone_Ultimate_Study_Guide.pdf"

C_NAVY = colors.HexColor("#1E3A5F")
C_BLUE = colors.HexColor("#2563EB")
C_BLUE_LIGHT = colors.HexColor("#DBEAFE")
C_BLUE_PALE = colors.HexColor("#EFF6FF")
C_BORDER = colors.HexColor("#BFDBFE")
C_TEXT = colors.HexColor("#1E293B")
C_MUTED = colors.HexColor("#64748B")
C_WHITE = colors.white

MARGIN = 2.0 * cm
TOP_MARGIN = 2.4 * cm
BOTTOM_MARGIN = 2.0 * cm
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
    ST = {}

    def s(name, **kw):
        font = kw.pop("fontName", "Poppins")
        ST[name] = ParagraphStyle(name, parent=base["Normal"], fontName=font, **kw)
        return ST[name]

    s("CoverTitle", fontName="Poppins-Bold", fontSize=22, leading=28, alignment=TA_CENTER,
      textColor=C_WHITE, spaceAfter=6)
    s("CoverSubtitle", fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=C_BLUE_LIGHT, spaceAfter=4)
    s("Title", fontName="Poppins-Bold", fontSize=20, leading=26, alignment=TA_CENTER,
      textColor=C_NAVY, spaceAfter=8)
    s("Subtitle", fontSize=10, leading=14, alignment=TA_CENTER, textColor=C_MUTED, spaceAfter=5)
    s("CoverMeta", fontSize=9, leading=13, alignment=TA_CENTER, textColor=C_TEXT, spaceAfter=3)
    s("H1", fontName="Poppins-Bold", fontSize=13.5, leading=18, textColor=C_NAVY, spaceBefore=0, spaceAfter=0)
    s("H2", fontName="Poppins-SemiBold", fontSize=10.5, leading=14, textColor=C_BLUE, spaceBefore=0, spaceAfter=0)
    s("H3", fontName="Poppins-SemiBold", fontSize=9.5, leading=13, textColor=C_NAVY, spaceBefore=0, spaceAfter=0)
    s("Body", fontSize=9, leading=13.5, alignment=TA_JUSTIFY, textColor=C_TEXT, spaceAfter=6)
    s("TOC", fontName="Poppins-SemiBold", fontSize=9.5, leading=14, textColor=C_NAVY, spaceAfter=2)
    s("TOCSub", fontSize=9, leading=13, leftIndent=12, textColor=C_TEXT, spaceAfter=2)
    s("TH", fontName="Poppins-SemiBold", fontSize=7, leading=10, textColor=C_WHITE, alignment=TA_LEFT)
    s("TD", fontSize=7, leading=10, alignment=TA_LEFT, textColor=C_TEXT)
    s("TDBold", fontName="Poppins-SemiBold", fontSize=7, leading=10, textColor=C_NAVY)
    s("Caption", fontName="Poppins-Italic", fontSize=8, leading=11, textColor=C_MUTED, spaceAfter=4)
    s("CalloutLabel", fontName="Poppins-SemiBold", fontSize=8.5, leading=11, textColor=C_BLUE, spaceAfter=0)
    s("ClinicalLabel", fontName="Poppins-SemiBold", fontSize=8.5, leading=11, textColor=C_NAVY, spaceAfter=0)
    s("CalloutBody", fontSize=8.5, leading=12.5, textColor=C_TEXT, spaceAfter=0)
    s("Bullet", fontSize=9, leading=13, leftIndent=14, bulletIndent=6, textColor=C_TEXT, spaceAfter=3)
    return ST


ST = build_styles()


def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def para(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(esc(text).replace("\n", "<br/>"), ST[style])


def th_cell(text: str) -> Paragraph:
    return Paragraph(esc(str(text)), ST["TH"])


def td_cell(text: str, bold: bool = False) -> Paragraph:
    return Paragraph(esc(str(text)), ST["TDBold" if bold else "TD"])


def bullet(text: str) -> Paragraph:
    return Paragraph(f"• {esc(text)}", ST["Bullet"])


def section_heading(title: str) -> list:
    return [
        Spacer(1, 6),
        para(title, "H1"),
        Spacer(1, 5),
        HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=0, spaceBefore=0),
        Spacer(1, 12),
    ]


def sub_heading(title: str) -> list:
    return [Spacer(1, 6), para(title, "H2"), Spacer(1, 4)]


def wrap_table(headers, rows, col_fracs, header_bg=C_NAVY):
    widths = [USABLE_W * f for f in col_fracs]
    header_row = [th_cell(h) for h in headers]
    body = [[td_cell(c) for c in row] for row in rows]
    data = [header_row] + body
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_BLUE_PALE]),
        ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def callout_box(label: str, body: str, label_style: str = "CalloutLabel") -> Table:
    t = Table(
        [[para(label, label_style)], [para(body, "CalloutBody")]],
        colWidths=[USABLE_W],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_BLUE_PALE),
        ("BOX", (0, 0), (-1, -1), 0.75, C_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (0, 0), 8),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
        ("TOPPADDING", (0, 1), (-1, 1), 3),
        ("BOTTOMPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def embed_figure(filename: str, caption: str = "", max_h: float = MAX_FIG_H) -> list:
    path = FIGURES_DIR / filename
    out = [Spacer(1, 4)]
    if not path.exists():
        out.append(para(f"[Figure not found — run notebook: figures/{filename}]", "Caption"))
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


def comparison_table_block(table_def: dict) -> list:
    """Render a comparison sub-table with optional clinical note."""
    out = [
        para(table_def["title"], "H3"),
        wrap_table(table_def["headers"], table_def["rows"], table_def["col_fracs"]),
        Spacer(1, 6),
        callout_box("Clinical reading", table_def["clinical_note"], "ClinicalLabel"),
        Spacer(1, 12),
    ]
    return out


def figure_block(fig: dict, include_image: bool = True) -> list:
    s = []
    s.extend(sub_heading(f"Figure {fig['num']}: {fig['file']} (Section {fig['section']})"))
    s.append(para(f"What it shows: {fig['shows']}", "Body"))
    if include_image:
        max_h = 6.0 * cm if "heatmap" in fig["file"] or "correlation" in fig["file"] else MAX_FIG_H
        s.extend(embed_figure(
            fig["file"],
            f"Source: PCSPF Capstone Analysis, n=878  ·  Section {fig['section']}",
            max_h=max_h,
        ))
    s.append(callout_box("Statistical reading", fig["interpretation"]))
    s.append(Spacer(1, 4))
    s.append(callout_box("Clinical interpretation", fig["clinical_interpretation"], "ClinicalLabel"))
    s.append(Spacer(1, 4))
    s.append(callout_box("Study implication", fig["implications"]))
    s.append(Spacer(1, 4))
    s.append(callout_box("Clinical implication for defense", fig["clinical_implication"], "ClinicalLabel"))
    s.append(Spacer(1, 6))
    s.append(para(f"If the professor asks — point out: {fig['point_out']}", "Body"))
    s.append(para(f"Do NOT claim: {fig['dont_claim']}", "Body"))
    s.append(Spacer(1, 12))
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
    canvas.drawString(MARGIN, 0.8 * cm, f"PCSPF Capstone Ultimate Study Guide  ·  v{STUDY_GUIDE['version']}")
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
    s.append(para(STUDY_GUIDE["title"], "Title"))
    s.append(Spacer(1, 0.3 * cm))
    s.append(para(STUDY_GUIDE["subtitle"], "Subtitle"))
    s.append(Spacer(1, 1.5 * cm))
    s.append(para(PROJECT["course"], "CoverMeta"))
    s.append(para(PROJECT["institution"], "CoverMeta"))
    s.append(Spacer(1, 1.0 * cm))
    s.append(HRFlowable(width="55%", thickness=1, color=C_BLUE, hAlign="CENTER", spaceAfter=12))
    s.append(para(f"Version {STUDY_GUIDE['version']}  ·  {today}", "CoverMeta"))
    s.append(para(f"{PROJECT['notebook']}  ·  {PROJECT['n_patients']} patients  ·  seed {PROJECT['random_state']}", "CoverMeta"))
    s.append(PageBreak())

    # TOC
    s.extend(section_heading("Table of Contents"))
    toc = [
        "PART 1: Executive Overview",
        "PART 2: Dataset Overview (Features & Clinical Implications)",
        "PART 3: Project Identity",
        "PART 4: Number Bank",
        "PART 5: Notebook Section-by-Section Walkthrough",
        "PART 6: Preprocessing Decision Register",
        "PART 7: Function and Method Reference (Code Review)",
        "PART 8: Technique Deep Dives",
        "PART 9: Why Decision Map",
        "PART 10: Weak Results Defense Scripts",
        "PART 11: Model Comparison Summary Tables",
        "PART 12: Visualization Guide (21 Figures with Interpretations)",
        "PART 13: Curveball Q&A Bank",
        "PART 14: Slide-to-Section Mapping",
    ]
    for item in toc:
        s.append(para(item, "TOCSub"))
    s.append(PageBreak())

    # PART 1 — Executive Overview
    s.extend(section_heading("PART 1: Executive Overview"))
    s.append(para(EXECUTIVE_OVERVIEW["purpose"], "Body"))
    s.append(Spacer(1, 4))
    s.extend(sub_heading("Clinical problem and research question"))
    s.append(para(EXECUTIVE_OVERVIEW["problem"], "Body"))
    s.extend(sub_heading("Analytical approach"))
    s.append(para(EXECUTIVE_OVERVIEW["approach"], "Body"))
    s.extend(sub_heading("Headline results (memorize these)"))
    for item in EXECUTIVE_OVERVIEW["headline_results"]:
        s.append(bullet(item))
    s.append(Spacer(1, 6))
    s.extend(sub_heading("Why Random Forest (supervised)"))
    s.append(para(SUPERVISED_TECHNIQUE_JUSTIFICATION, "Body"))
    s.extend(sub_heading("Why K-Means (unsupervised)"))
    s.append(para(UNSUPERVISED_TECHNIQUE_JUSTIFICATION, "Body"))
    s.append(Spacer(1, 6))
    s.append(callout_box("How to use this guide", EXECUTIVE_OVERVIEW["how_to_use"]))
    s.append(PageBreak())

    # PART 2 — Dataset Overview
    s.extend(section_heading("PART 2: Dataset Overview (Features & Clinical Implications)"))
    s.append(para(DATASET_OVERVIEW["intro"], "Body"))
    s.append(Spacer(1, 6))
    s.append(callout_box("Derived ratio formulas", DATASET_OVERVIEW["ratio_formulas"], "ClinicalLabel"))
    s.append(Spacer(1, 10))
    s.extend(sub_heading("Feature catalog — all 20 preoperative variables"))
    s.append(para(
        "Each row explains what the feature measures and why it matters clinically for pancreatic cancer "
        "survival. These foundations support every EDA plot, preprocessing choice, and model interpretation.",
        "Body"))
    s.append(wrap_table(
        ["Feature", "What it is", "Clinical implication"],
        [(f, d, c) for f, d, c in DATASET_FEATURES],
        [0.14, 0.30, 0.56],
    ))
    s.append(PageBreak())

    # PART 3 — Project Identity
    s.extend(section_heading("PART 3: Project Identity"))
    s.append(para(PROJECT_IDENTITY["summary"], "Body"))
    s.append(Spacer(1, 6))
    d = PROJECT_IDENTITY["dataset"]
    s.append(wrap_table(
        ["Item", "Detail"],
        [
            ["Patients", str(d["n_patients"])],
            ["Columns (raw → clean)", f"{d['raw_columns']} → {d['clean_columns']}"],
            ["Features", str(d["n_features"])],
            ["Target", d["target"]],
            ["Source", d["source"]],
            ["Class 1 / Class 0", f"{d['class_1']} / {d['class_0']}"],
            ["Imbalance ratio", d["ratio"]],
        ],
        [0.28, 0.72],
    ))
    s.append(Spacer(1, 8))
    s.append(para(f"Techniques: {PROJECT_IDENTITY['techniques']}", "Body"))
    s.append(Spacer(1, 8))
    s.append(callout_box("Core finding (one sentence)", CORE_FINDING))
    s.append(PageBreak())

    # PART 4 — Number Bank
    s.extend(section_heading("PART 4: Number Bank"))
    s.append(para("Every number you must know cold — organized by category.", "Body"))
    for category, items in NUMBER_BANK.items():
        s.extend(sub_heading(category))
        s.append(wrap_table(["Metric", "Value"], items, [0.42, 0.58]))
        s.append(Spacer(1, 6))
    s.append(PageBreak())

    # PART 5 — Notebook walkthrough
    s.extend(section_heading("PART 5: Notebook Section-by-Section Walkthrough"))
    for key in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        sec = SECTION_WALKTHROUGHS[key]
        s.extend(sub_heading(f"Section {key}: {sec['title'].split(': ', 1)[-1]}"))
        s.append(para(sec["summary"], "Body"))
        s.append(para("Key code functions / methods:", "H3"))
        for fn in sec["functions"]:
            s.append(bullet(fn))
        s.append(para("Key parameters and why:", "H3"))
        for p in sec["parameters"]:
            s.append(bullet(p))
        s.append(para("Outputs produced:", "H3"))
        for o in sec["outputs"]:
            s.append(bullet(o))
        s.append(para("Key decisions — what we DID:", "H3"))
        for d in sec["decisions_did"]:
            s.append(bullet(d))
        s.append(para("Key decisions — what we did NOT do:", "H3"))
        for d in sec["decisions_did_not"]:
            s.append(bullet(d))
        s.append(callout_box("Interpretation", sec["interpretation"]))
        s.append(Spacer(1, 4))
        s.append(para("Potential professor questions:", "H3"))
        for q in sec["professor_questions"]:
            s.append(bullet(q))
        s.append(Spacer(1, 10))
    s.append(PageBreak())

    # PART 6 — Preprocessing
    s.extend(section_heading("PART 6: Preprocessing Decision Register"))
    s.append(wrap_table(
        ["Step", "Action Taken", "Justification", "If we did the opposite"],
        [(a, b, c, d) for a, b, c, d in PREPROCESSING_EXTENDED],
        [0.18, 0.16, 0.33, 0.33],
    ))
    s.append(PageBreak())

    # PART 7 — Function reference
    s.extend(section_heading("PART 7: Function and Method Reference (Code Review)"))
    s.append(para(
        "Lookup table of Python functions/methods used in the notebook, organized by section. "
        "Format: function — source — plain English — key parameters — returns.",
        "Body"))
    for section_name, funcs in FUNCTION_REFERENCE.items():
        s.extend(sub_heading(section_name))
        rows = [[f[0], f[1], f[2], f[3], f[4]] for f in funcs]
        s.append(wrap_table(
            ["Function", "Import", "What it does", "Parameters set", "Returns"],
            rows,
            [0.16, 0.14, 0.28, 0.22, 0.20],
        ))
        s.append(Spacer(1, 8))
    s.append(PageBreak())

    # PART 8 — Technique deep dives
    s.extend(section_heading("PART 8: Technique Deep Dives"))
    for name, text in TECHNIQUE_DEEP_DIVES.items():
        s.extend(sub_heading(name))
        s.append(para(text, "Body"))
        s.append(Spacer(1, 6))
    s.append(PageBreak())

    # PART 9 — Why decision map
    s.extend(section_heading("PART 9: Why Decision Map"))
    s.extend(sub_heading("Why we DID this"))
    for title, reasons in WHY_DID:
        s.append(para(title, "H3"))
        for r in reasons:
            s.append(bullet(r))
        s.append(Spacer(1, 4))
    s.extend(sub_heading("Why we DID NOT do this"))
    for title, reasons in WHY_DID_NOT:
        s.append(para(title, "H3"))
        for r in reasons:
            s.append(bullet(r))
        s.append(Spacer(1, 4))
    s.extend(sub_heading("Why not a different model"))
    for title, reason in WHY_NOT_DIFFERENT_MODEL:
        s.append(bullet(f"{title}: {reason}"))
    s.append(PageBreak())

    # PART 10 — Defense scripts
    s.extend(section_heading("PART 10: Weak Results Defense Scripts"))
    s.append(para(
        "Full acknowledge → contextualize → reframe → show value scripts. Practice speaking these aloud.",
        "Body"))
    for title, script in DEFENSE_SCRIPTS:
        s.extend(sub_heading(title))
        s.append(para(script, "Body"))
        s.append(Spacer(1, 6))
    s.append(PageBreak())

    # PART 11 — Model comparison
    s.extend(section_heading("PART 11: Model Comparison Summary Tables"))
    s.append(para(
        "Wide metrics are split into readable tables. Each table includes a clinical reading for defense.",
        "Body"))
    s.extend(sub_heading("Supervised comparison (Section 7.5)"))
    s.extend(comparison_table_block(SUPERVISED_COMPARISON_A))
    s.extend(comparison_table_block(SUPERVISED_COMPARISON_B))
    s.extend(sub_heading("Unsupervised comparison (Section 6.0)"))
    s.extend(comparison_table_block(UNSUPERVISED_COMPARISON_A))
    s.extend(comparison_table_block(UNSUPERVISED_COMPARISON_B))
    s.append(PageBreak())

    # PART 12 — Visualization guide
    s.extend(section_heading("PART 12: Visualization Guide (21 Figures)"))
    s.append(para(
        "Each figure includes the image (when available), statistical and clinical readings, "
        "defense talking points, and common misinterpretations to avoid.",
        "Body"))
    for fig in FIGURE_GUIDE:
        s.extend(figure_block(fig, include_image=True))
    s.append(PageBreak())

    # PART 13 — Q&A
    s.extend(section_heading("PART 13: Curveball Q&A Bank"))
    for i, (q, a) in enumerate(QA_BANK, 1):
        s.append(para(f"Q{i}. {q}", "H3"))
        s.append(para(a, "Body"))
        s.append(Spacer(1, 4))
    s.append(PageBreak())

    # PART 14 — Slide mapping
    s.extend(section_heading("PART 14: Slide-to-Section Mapping"))
    s.append(para(
        "Quick reference connecting each presentation slide to its notebook section. "
        "Use this to pull up code instantly if the professor asks.",
        "Body"))
    s.append(wrap_table(
        ["Slide", "Title", "Notebook Section", "Notes"],
        SLIDE_SECTION_MAP,
        [0.08, 0.28, 0.14, 0.50],
    ))
    s.append(Spacer(1, 12))
    s.append(callout_box(
        "Appendix slides (Q&A backup only)",
        "Slide 31 → preprocessing_summary.png (Section 4.10)  ·  "
        "Slide 32 → classification_report.png (Section 7.3)  ·  "
        "Slide 33 → VIF table (Section 4.6)  ·  "
        "Slide 34 → Normality tests (Section 4.5)  ·  "
        "Slide 35 → Outlier summary (Section 4.4)",
    ))
    s.append(Spacer(1, 16))
    s.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    s.append(Spacer(1, 8))
    s.append(para(
        "End of Ultimate Study Guide. Regenerate: python scripts/generate_study_guide.py  ·  "
        "Re-run notebook for missing comparison figures (supervised_model_comparison.png, "
        "unsupervised_model_comparison.png). Good luck on your defense.",
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
        title="PCSPF Capstone Ultimate Study Guide",
    )
    doc.build(build_story(), onFirstPage=on_cover, onLaterPages=on_page)
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
