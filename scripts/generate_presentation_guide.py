# -*- coding: utf-8 -*-
"""
Generate presentation production guide PDF (outline + slide-maker notes).
Output: Documentations/PCSPF_Presentation_Production_Guide.pdf
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

sys.path.insert(0, str(Path(__file__).resolve().parent))
from presentation_outline_data import (
    APPENDIX_SLIDES,
    DELIVERABLES_CHECKLIST,
    DESIGN_SYSTEM,
    GLOBAL_SLIDE_MAKER_RULES,
    PARTS_ORDER,
    SLIDES,
    TIMING_GUIDE,
)

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "Documentations" / "fonts"
OUTPUT_PDF = ROOT / "Documentations" / "PCSPF_Presentation_Production_Guide.pdf"

for name, file in [
    ("Poppins", "Poppins-Regular.ttf"),
    ("Poppins-Bold", "Poppins-Bold.ttf"),
    ("Poppins-SemiBold", "Poppins-SemiBold.ttf"),
    ("Poppins-Italic", "Poppins-Italic.ttf"),
]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))

MARGIN = 2 * cm
USABLE_W = A4[0] - 2 * MARGIN


def build_styles():
    base = getSampleStyleSheet()
    ST = {}

    def s(name, **kw):
        font = kw.pop("fontName", "Poppins")
        ST[name] = ParagraphStyle(name, parent=base["Normal"], fontName=font, **kw)
        return ST[name]

    s("Title", fontName="Poppins-Bold", fontSize=20, leading=26, alignment=TA_CENTER,
      textColor=colors.HexColor("#1a365d"), spaceAfter=10)
    s("Subtitle", fontSize=11, leading=15, alignment=TA_CENTER, textColor=colors.HexColor("#4a5568"), spaceAfter=6)
    s("H1", fontName="Poppins-Bold", fontSize=15, leading=19, textColor=colors.HexColor("#1a365d"),
      spaceBefore=14, spaceAfter=8)
    s("H2", fontName="Poppins-SemiBold", fontSize=12, leading=16, textColor=colors.HexColor("#2c5282"),
      spaceBefore=10, spaceAfter=6)
    s("H3", fontName="Poppins-SemiBold", fontSize=10.5, leading=14, textColor=colors.HexColor("#2d3748"),
      spaceBefore=6, spaceAfter=4)
    s("Body", fontSize=9, leading=12.5, alignment=TA_JUSTIFY, spaceAfter=5)
    s("TOC", fontSize=9.5, leading=14, leftIndent=8)
    s("TD", fontSize=7.5, leading=10)
    s("NoteLabel", fontName="Poppins-SemiBold", fontSize=8.5, textColor=colors.HexColor("#2b6cb0"), spaceAfter=2)
    s("MakerNote", fontSize=8.5, leading=12, backColor=colors.HexColor("#ebf8ff"),
      borderPadding=5, leftIndent=4, rightIndent=4, spaceAfter=4)
    s("PresenterNote", fontSize=8.5, leading=12, backColor=colors.HexColor("#f7fafc"),
      borderPadding=5, leftIndent=4, rightIndent=4, spaceAfter=4)
    s("OutlineBullet", fontSize=8.5, leading=12, leftIndent=12, spaceAfter=2)
    return ST


ST = build_styles()


def esc(t: str) -> str:
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def para(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(esc(text).replace("\n", "<br/>"), ST[style])


def cell(text: str, bold: bool = False) -> Paragraph:
    return Paragraph(esc(str(text)), ST["TD"])


def table_wrap(headers, rows, fracs):
    widths = [USABLE_W * f for f in fracs]
    data = [[cell(h, True) for h in headers]] + [[cell(c) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def note_block(label: str, text: str, style: str) -> list:
    return [para(label, "NoteLabel"), para(text, style), Spacer(1, 3)]


def slide_entry(sl: dict) -> list:
    flow = []
    flow.append(para(f"Slide {sl['num']} — {sl['title']}", "H2"))
    flow.append(para(f"<i>{sl['part']}</i>", "Body"))
    flow.append(para("<b>Planned content (outline only — not final slide copy):</b>", "Body"))
    for b in sl["outline"]:
        flow.append(para(f"&#8226; {b}", "OutlineBullet"))
    if sl.get("figures"):
        flow.append(para("<b>Figure assets:</b> " + ", ".join(sl["figures"]), "Body"))
    if sl.get("layout"):
        flow.append(para(f"<b>Layout suggestion:</b> {sl['layout']}", "Body"))
    flow.extend(note_block("Slide maker notes (design & production)", sl["maker_notes"], "MakerNote"))
    flow.extend(note_block("Presenter notes (defense & delivery)", sl["presenter_notes"], "PresenterNote"))
    flow.append(Spacer(1, 8))
    return flow


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Poppins", 7)
    canvas.setFillColor(colors.HexColor("#718096"))
    canvas.drawString(MARGIN, 1.0 * cm, "PCSPF Capstone — Presentation Production Guide")
    canvas.drawRightString(A4[0] - MARGIN, 1.0 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build_story():
    today = date.today().strftime("%B %d, %Y")
    s = []

    # Cover
    s.append(Spacer(1, 2.2 * cm))
    s.append(para("Presentation Production Guide", "Title"))
    s.append(para("PCSPF Capstone Project — Slide Outline & Designer Brief", "Subtitle"))
    s.append(para("Fundamentals of Data Science (CMSC 176)", "Subtitle"))
    s.append(para("University of the Philippines Manila", "Subtitle"))
    s.append(Spacer(1, 0.8 * cm))
    s.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e0")))
    s.append(Spacer(1, 0.3 * cm))
    s.append(para(
        f"Version 1.0 | {today}<br/>"
        "Audience: Slide designer / template builder<br/>"
        "Purpose: Structure, visual standards, and production notes — NOT final slide content<br/>"
        "Main deck: 30 slides | Appendix backup: 5 slides (31–35)",
        "Body"))
    s.append(PageBreak())

    # TOC
    s.append(para("Table of Contents", "H1"))
    for item in [
        "1. How to Use This Guide",
        "2. Design System (Poppins & Color Palette)",
        "3. Global Rules for Slide Makers",
        "4. Capstone Deliverables Alignment Checklist",
        "5. Presentation Structure Overview",
        "6. Suggested Timing Guide",
        "7. Complete Slide Outline with Production Notes (Slides 1–30)",
        "8. Appendix Slides (31–35, Q&A Backup Only)",
        "9. Figure Asset Register",
    ]:
        s.append(para(item, "TOC"))
    s.append(PageBreak())

    # 1 How to use
    s.append(para("1. How to Use This Guide", "H1"))
    s.append(para(
        "This PDF is a production brief for the person building the PowerPoint or Google Slides template. "
        "It does NOT contain final slide wording, exact statistics in presentation copy, or completed speaker scripts. "
        "The team will add specific content later using outputs from PCSPF_Data_Science_Capstone.ipynb and the figures/ folder.",
        "Body"))
    s.append(para(
        "Each slide entry includes: (a) planned outline bullets, (b) figure file paths where applicable, "
        "(c) layout suggestions, (d) slide maker notes for visual design and compliance, and "
        "(e) presenter notes for honest, defensible delivery. Follow the design system in Section 2 for consistency "
        "with the project audit documentation PDF.",
        "Body"))
    s.append(PageBreak())

    # 2 Design system
    s.append(para("2. Design System (Poppins & Color Palette)", "H1"))
    s.append(table_wrap(
        ["Element", "Specification"],
        [
            ("Primary font", f"{DESIGN_SYSTEM['font_primary']} (Bold / SemiBold / Regular)"),
            ("Primary color (titles)", DESIGN_SYSTEM["color_primary"]),
            ("Secondary color (headers)", DESIGN_SYSTEM["color_secondary"]),
            ("Accent color (callouts)", DESIGN_SYSTEM["color_accent"]),
            ("Body text", DESIGN_SYSTEM["color_text"]),
            ("Muted text / footer", DESIGN_SYSTEM["color_muted"]),
            ("Light background", DESIGN_SYSTEM["color_bg_light"]),
            ("Callout background", DESIGN_SYSTEM["color_callout"]),
            ("Charts", DESIGN_SYSTEM["chart_palette"]),
        ],
        [0.35, 0.65],
    ))
    s.append(Spacer(1, 8))
    s.append(para(
        "Slide template: white or #f7fafc background; title bar optional in #2c5282 with white text for part dividers. "
        "Minimum font on projected slides: 18pt body, 24pt+ titles. Export charts from figures/ at native 300 DPI—do not redraw.",
        "Body"))
    s.append(PageBreak())

    # 3 Global rules
    s.append(para("3. Global Rules for Slide Makers", "H1"))
    s.append(para(
        "These rules protect scientific integrity and align with course expectations. Violating them may cause "
        "failure during oral defense even if slides look visually polished.",
        "Body"))
    for i, rule in enumerate(GLOBAL_SLIDE_MAKER_RULES, 1):
        s.append(para(f"{i}. {rule}", "Body"))
    s.append(PageBreak())

    # 4 Deliverables
    s.append(para("4. Capstone Deliverables Alignment Checklist", "H1"))
    s.append(para(
        "Verify the slide deck addresses every row before declaring the presentation complete. "
        "Cross-reference PCSPF_Data_Science_Capstone.ipynb and Documentations/PCSPF_Capstone_Project_Audit_Documentation.pdf.",
        "Body"))
    s.append(table_wrap(
        ["Deliverable / requirement", "Slide(s)", "Designer verification"],
        DELIVERABLES_CHECKLIST,
        [0.38, 0.18, 0.44],
    ))
    s.append(PageBreak())

    # 5 Structure
    s.append(para("5. Presentation Structure Overview", "H1"))
    s.append(table_wrap(
        ["Part", "Slide range"],
        PARTS_ORDER,
        [0.55, 0.45],
    ))
    s.append(Spacer(1, 10))
    s.append(para(
        "Total main presentation: 30 slides across 7 content parts plus front matter. "
        "Preprocessing (Part III) and Synthesis (Part VI) are the highest-stakes sections for grading.",
        "Body"))
    s.append(PageBreak())

    # 6 Timing
    s.append(para("6. Suggested Timing Guide", "H1"))
    s.append(para(
        "Approximate timing for a 35–40 minute slot including questions. Adjust during rehearsal.",
        "Body"))
    s.append(table_wrap(
        ["Part", "Slides", "Suggested time"],
        TIMING_GUIDE,
        [0.45, 0.20, 0.35],
    ))
    s.append(PageBreak())

    # 7 Slides 1-30
    s.append(para("7. Complete Slide Outline with Production Notes (Slides 1–30)", "H1"))
    s.append(para(
        "The following pages document each slide in order. Content bullets are structural placeholders only.",
        "Body"))
    current_part = None
    for sl in SLIDES:
        if sl["part"] != current_part:
            current_part = sl["part"]
            if sl["num"] > 2:
                s.append(Spacer(1, 6))
            s.append(para(current_part, "H1"))
        s.extend(slide_entry(sl))
    s.append(PageBreak())

    # 8 Appendix
    s.append(para("8. Appendix Slides (31–35, Q&A Backup Only)", "H1"))
    s.append(para(
        "Hide these from the main slide show during the standard presentation. Keep them in the file for "
        "Q&A if the professor requests full tables. Use same design system; denser tables acceptable.",
        "Body"))
    for num, title, desc, figs in APPENDIX_SLIDES:
        s.append(para(f"Slide {num} — {title}", "H2"))
        s.append(para(desc, "Body"))
        if figs:
            s.append(para("Figures: " + ", ".join(figs), "Body"))
        s.append(para(
            "Slide maker: use landscape orientation if table is wide; minimum 14pt table text; "
            "include 'Appendix — Q&A backup' header.",
            "MakerNote"))
        s.append(Spacer(1, 6))
    s.append(PageBreak())

    # 9 Figure register
    s.append(para("9. Figure Asset Register", "H1"))
    fig_rows = []
    for sl in SLIDES:
        for f in sl.get("figures", []):
            fig_rows.append((f"Slide {sl['num']}", sl["title"][:40], f))
    for num, title, _, figs in APPENDIX_SLIDES:
        for f in figs:
            fig_rows.append((f"Slide {num}", title[:40], f))
    # dedupe
    seen = set()
    unique = []
    for r in fig_rows:
        if r[2] not in seen:
            seen.add(r[2])
            unique.append(r)
    s.append(table_wrap(
        ["Used on", "Slide title", "File path (project root)"],
        unique,
        [0.12, 0.38, 0.50],
    ))
    s.append(Spacer(1, 16))
    s.append(para(
        "End of Presentation Production Guide. Team adds final content; designer builds template per this brief.",
        "Body"))
    return s


def main():
    if not FONT_DIR.exists():
        raise FileNotFoundError(f"Fonts not found: {FONT_DIR}")
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title="PCSPF Presentation Production Guide",
    )
    doc.build(build_story(), onFirstPage=on_page, onLaterPages=on_page)
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
