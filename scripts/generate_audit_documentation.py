# -*- coding: utf-8 -*-
"""
Generate capstone project audit documentation (PDF).
Typography: Poppins | Color scheme: standard professional blue palette.
Output: Documentations/PCSPF_Capstone_Project_Audit_Documentation.pdf
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
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from audit_content import (
    AUDIT_ENHANCEMENTS,
    FIGURES,
    PREPROCESSING_DECISIONS,
    PROJECT,
    RESULTS,
    TECHNIQUES_GLOSSARY,
    section_processes,
)

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "Documentations" / "fonts"
OUTPUT_PDF = ROOT / "Documentations" / "PCSPF_Capstone_Project_Audit_Documentation.pdf"

# --- Standard blue palette (consistent, professional) ---
C_NAVY = colors.HexColor("#1E3A5F")       # primary headings, table headers, cover band
C_BLUE = colors.HexColor("#2563EB")       # accents, subheadings, rules
C_BLUE_MID = colors.HexColor("#3B82F6")   # secondary accent
C_BLUE_LIGHT = colors.HexColor("#DBEAFE") # callout / label column backgrounds
C_BLUE_PALE = colors.HexColor("#EFF6FF")  # alternating row / box fill
C_BORDER = colors.HexColor("#BFDBFE")     # table borders
C_TEXT = colors.HexColor("#1E293B")       # body text
C_MUTED = colors.HexColor("#64748B")      # secondary text, footer
C_WHITE = colors.white

MARGIN = 2.2 * cm
TOP_MARGIN = 2.6 * cm
BOTTOM_MARGIN = 2.2 * cm
USABLE_W = A4[0] - 2 * MARGIN

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

    s("CoverTitle", fontName="Poppins-Bold", fontSize=24, leading=30, alignment=TA_CENTER,
      textColor=C_WHITE, spaceAfter=6)
    s("CoverSubtitle", fontSize=11, leading=15, alignment=TA_CENTER, textColor=C_BLUE_LIGHT, spaceAfter=4)
    s("Title", fontName="Poppins-Bold", fontSize=22, leading=28, alignment=TA_CENTER,
      textColor=C_NAVY, spaceAfter=8)
    s("Subtitle", fontSize=11, leading=15, alignment=TA_CENTER, textColor=C_MUTED, spaceAfter=5)
    s("CoverMeta", fontSize=9.5, leading=14, alignment=TA_CENTER, textColor=C_TEXT, spaceAfter=4)
    s("H1", fontName="Poppins-Bold", fontSize=14, leading=20, textColor=C_NAVY,
      spaceBefore=0, spaceAfter=0)
    s("H2", fontName="Poppins-SemiBold", fontSize=11, leading=15, textColor=C_BLUE,
      spaceBefore=0, spaceAfter=0)
    s("Body", fontSize=9.5, leading=14, alignment=TA_JUSTIFY, textColor=C_TEXT, spaceAfter=8)
    s("TOC", fontName="Poppins-SemiBold", fontSize=10, leading=16, leftIndent=0,
      textColor=C_NAVY, spaceAfter=2)
    s("TOCSub", fontSize=9.5, leading=14, leftIndent=14, textColor=C_TEXT, spaceAfter=3)
    s("TH", fontName="Poppins-SemiBold", fontSize=8, leading=11, textColor=C_WHITE, alignment=TA_LEFT)
    s("TD", fontSize=8, leading=11.5, alignment=TA_LEFT, textColor=C_TEXT)
    s("TDBold", fontName="Poppins-SemiBold", fontSize=8, leading=11.5, textColor=C_NAVY)
    s("CalloutLabel", fontName="Poppins-SemiBold", fontSize=9, leading=12, textColor=C_BLUE,
      spaceBefore=0, spaceAfter=0)
    s("CalloutBody", fontSize=9, leading=13, textColor=C_TEXT, spaceBefore=0, spaceAfter=0)
    s("Footer", fontSize=7.5, textColor=C_MUTED)
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


def section_heading(title: str) -> list:
    """H1 with separator — extra vertical space prevents text/rule overlap."""
    return [
        Spacer(1, 8),
        para(title, "H1"),
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=0, spaceBefore=0),
        Spacer(1, 14),
    ]


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
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def callout_box(label: str, body: str) -> Table:
    """Light-blue info box with proper padding (avoids Paragraph backColor clipping)."""
    t = Table(
        [[para(label, "CalloutLabel")], [para(body, "CalloutBody")]],
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


def simple_block(text: str) -> list:
    return [callout_box("In simple terms", text), Spacer(1, 12)]


def process_table(proc: tuple) -> Table:
    pid, name, technique, what, params, output, decision, _simple = proc
    rows = [
        ["Process ID", pid],
        ["Step name", name],
        ["Technique / method", technique],
        ["What we did (detailed)", what],
        ["Parameters / settings", params],
        ["Output / artifact", output],
        ["Decision / rationale", decision],
    ]
    label_w = 3.4 * cm
    data = [[td_cell(r[0], bold=True), td_cell(r[1])] for r in rows]
    t = Table(data, colWidths=[label_w, USABLE_W - label_w])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), C_BLUE_LIGHT),
        ("TEXTCOLOR", (0, 0), (0, -1), C_NAVY),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [C_WHITE, C_BLUE_PALE]),
        ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def process_entry(proc: tuple) -> list:
    """Render one process step: heading, detail table, plain-language callout."""
    pid, name, *_rest = proc
    simple_text = proc[-1]
    return [
        Spacer(1, 10),
        para(f"Process {pid}: {name}", "H2"),
        Spacer(1, 6),
        process_table(proc),
        Spacer(1, 10),
        callout_box("In simple terms", simple_text),
        Spacer(1, 16),
    ]


def on_page(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    w, h = A4
    # Top accent bar
    canvas.setFillColor(C_NAVY)
    canvas.rect(0, h - 0.35 * cm, w, 0.35 * cm, fill=1, stroke=0)
    canvas.setFillColor(C_BLUE)
    canvas.rect(0, h - 0.42 * cm, w, 0.07 * cm, fill=1, stroke=0)
    # Footer rule + text
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 1.35 * cm, w - MARGIN, 1.35 * cm)
    canvas.setFont("Poppins", 7.5)
    canvas.setFillColor(C_MUTED)
    canvas.drawString(MARGIN, 0.85 * cm, f"PCSPF Capstone Audit Documentation  ·  v{PROJECT['version']}")
    canvas.drawRightString(w - MARGIN, 0.85 * cm, f"Page {doc.page}")
    canvas.restoreState()


def on_cover(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Full-width navy header band
    band_h = 5.5 * cm
    canvas.setFillColor(C_NAVY)
    canvas.rect(0, h - band_h, w, band_h, fill=1, stroke=0)
    canvas.setFillColor(C_BLUE)
    canvas.rect(0, h - band_h - 0.12 * cm, w, 0.12 * cm, fill=1, stroke=0)
    # Bottom accent
    canvas.setFillColor(C_BLUE_PALE)
    canvas.rect(0, 0, w, 1.0 * cm, fill=1, stroke=0)
    canvas.setFillColor(C_BLUE)
    canvas.rect(0, 1.0 * cm, w, 0.08 * cm, fill=1, stroke=0)
    canvas.restoreState()


def build_story():
    today = date.today().strftime("%B %d, %Y")
    s = []
    sec = section_processes()

    # --- Cover (title below navy band drawn on canvas) ---
    s.append(Spacer(1, 6.2 * cm))
    s.append(para(PROJECT["title"], "Title"))
    s.append(Spacer(1, 0.35 * cm))
    s.append(para(PROJECT["subtitle"], "Subtitle"))
    s.append(Spacer(1, 1.8 * cm))
    s.append(para(PROJECT["course"], "CoverMeta"))
    s.append(para(PROJECT["institution"], "CoverMeta"))
    s.append(Spacer(1, 1.2 * cm))
    s.append(HRFlowable(width="60%", thickness=1, color=C_BLUE, hAlign="CENTER", spaceAfter=14))
    s.append(para(
        f"Version {PROJECT['version']}  ·  {today}",
        "CoverMeta"))
    s.append(para(
        f"{PROJECT['notebook']}  ·  {PROJECT['n_cells']} cells  ·  {PROJECT['n_sections']} sections",
        "CoverMeta"))
    s.append(para(
        f"{PROJECT['n_patients']} patients  ·  {PROJECT['n_features']} features  ·  seed {PROJECT['random_state']}",
        "CoverMeta"))
    s.append(PageBreak())

    # --- Table of Contents ---
    s.extend(section_heading("Table of Contents"))
    toc = [
        ("1.", "Document Purpose and How to Read This Guide"),
        ("2.", "Executive Overview"),
        ("3.", "End-to-End Pipeline Map"),
        ("4.", "Audit Enhancements Register"),
        ("5.", "Techniques and Methods Glossary"),
        ("6.", "Repository and File Inventory"),
        ("7.", "Complete Process Documentation (Sections 1–9)"),
        ("8.", "Preprocessing Decisions Register"),
        ("9.", "Visualizations Register (21 Figures)"),
        ("10.", "Quantitative Results Reference"),
        ("11.", "Model Justification Summaries"),
        ("12.", "Compliance, Limitations, and Reproducibility"),
    ]
    for num, title in toc:
        s.append(para(f"{num}  {title}", "TOCSub"))
    s.append(PageBreak())

    # --- 1 Purpose ---
    s.extend(section_heading("1. Document Purpose and How to Read This Guide"))
    s.append(para(
        "This document is the formal audit record of the PCSPF capstone project. It documents every "
        "major process step, the technique used, parameters applied, outputs produced, and decisions "
        "made—including steps deliberately not taken. It reflects the notebook as executed through "
        "Section 9, including post-audit enhancements (overfitting analysis, metric clarifications, "
        "Cramér's V, model comparisons) and optimization sections (Why Random Forest?, Why K-Means?, "
        "enhanced supervised benchmark).",
        "Body"))
    s.append(para(
        "How to read: Each process entry contains (a) a technical description for instructors and "
        "reviewers, and (b) an \"In simple terms\" box for non-technical readers. Tables use wrapped "
        "text. Metrics match the executed notebook unless noted as approximate (~).",
        "Body"))
    s.append(PageBreak())

    # --- 2 Executive ---
    s.extend(section_heading("2. Executive Overview"))
    s.append(para(
        "Problem: Predict 1-year pancreatic cancer survival and discover patient subgroups using 20 "
        "preoperative clinical features from 878 patients. Methods: Random Forest (supervised, primary) "
        "and K-Means (unsupervised, k=3). The pipeline loads and cleans data (3 columns removed), "
        "explores distributions and correlations, documents preprocessing decisions, splits 80/20 "
        "stratified, clusters on scaled features, tunes Random Forest with GridSearchCV "
        "(class_weight=balanced), benchmarks alternative models, and synthesizes supervised and "
        "unsupervised findings in Section 8.",
        "Body"))
    s.extend(simple_block(
        "We studied hospital lab data to (1) estimate who is likely to live at least one year and "
        "(2) find natural groups of similar patients. We wrote down every step—including what we "
        "deliberately did not do—so the work can be verified, defended, and repeated."
    ))
    s.append(Spacer(1, 6))
    s.append(wrap_table(
        ["Deliverable", "Status", "Location"],
        [
            [f"Jupyter notebook ({PROJECT['n_cells']} cells, 9 sections)", "Complete", PROJECT["notebook"]],
            ["Figures (21 PNG, 300 DPI)", "Generated on notebook run", "figures/"],
            ["Audit documentation PDF", f"v{PROJECT['version']}", "Documentations/PCSPF_Capstone_Project_Audit_Documentation.pdf"],
            ["Notebook builder script", "Available", "scripts/assemble_notebook.py"],
            ["PDF generator script", "Available", "scripts/generate_audit_documentation.py"],
        ],
        [0.38, 0.17, 0.45],
    ))
    s.append(PageBreak())

    # --- 3 Pipeline ---
    s.extend(section_heading("3. End-to-End Pipeline Map"))
    pipeline = [
        ("A", "Setup", "Imports, RANDOM_STATE=42, figures/ folder, plotting defaults"),
        ("B", "Load & clean", "Excel → drop 3 cols → survival_label → 878 × 21"),
        ("C", "EDA", "Stats, 5 chart groups, correlation, class means, EDA summary"),
        ("D", "Preprocess", "Types, nulls, outliers, normality, VIF, decisions table"),
        ("E", "Split & scale", "702/176 stratified; StandardScaler on full X for K-Means only"),
        ("F", "Unsupervised", "Method comparison → elbow/silhouette → K-Means k=3 → PCA → chi-square"),
        ("G", "Supervised", "RF justification → baseline → GridSearchCV → evaluation → model comparison"),
        ("H", "Synthesis", "RF vs cluster features, probability bridge, limitations, future work"),
        ("I", "Conclusion", "Dynamic four-paragraph recap with runtime metrics"),
    ]
    s.append(wrap_table(["Phase", "Notebook section", "Key outputs"], pipeline, [0.09, 0.26, 0.65]))
    s.append(PageBreak())

    # --- 4 Audit ---
    s.extend(section_heading("4. Audit Enhancements Register"))
    s.append(para(
        "The following cells were added after a full project audit to address gaps in justification, "
        "metric interpretation, and methodological transparency. No existing cells were deleted or reordered.",
        "Body"))
    s.append(wrap_table(
        ["Location", "Enhancement", "What was added", "Why it matters"],
        [(a, b, c, d) for a, b, c, d in AUDIT_ENHANCEMENTS],
        [0.11, 0.17, 0.38, 0.34],
    ))
    s.append(PageBreak())

    # --- 5 Glossary ---
    s.extend(section_heading("5. Techniques and Methods Glossary"))
    s.append(wrap_table(
        ["Technique", "What it is", "How we used it", "Key settings"],
        TECHNIQUES_GLOSSARY,
        [0.17, 0.30, 0.30, 0.23],
    ))
    s.append(PageBreak())

    # --- 6 Files ---
    s.extend(section_heading("6. Repository and File Inventory"))
    files = [
        (PROJECT["notebook"], "Main analysis notebook (all sections, audit cells, optimizations)"),
        (PROJECT["data_file"], "Source data: 878 patients, 24 columns raw"),
        ("figures/*.png", "21 exported visualizations at 300 DPI"),
        ("scripts/audit_content.py", "Structured text content for this PDF"),
        ("scripts/generate_audit_documentation.py", "Regenerates this PDF document"),
        ("scripts/assemble_notebook.py", "Programmatic notebook builder"),
        ("requirements.txt", "Python package dependencies"),
        ("Documentations/fonts/", "Poppins font files for PDF typography"),
    ]
    s.append(wrap_table(["File / path", "Purpose"], files, [0.40, 0.60]))
    s.append(PageBreak())

    # --- 7 Sections ---
    s.extend(section_heading("7. Complete Process Documentation (Sections 1–9)"))
    s.append(para(
        "The following subsections mirror the Jupyter notebook. Process IDs match notebook subsection "
        "numbers. Audit additions are marked (audit) in the process name.",
        "Body"))
    s.append(Spacer(1, 6))

    section_keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    for idx, key in enumerate(section_keys):
        block = sec[key]
        if idx > 0:
            s.append(PageBreak())
        s.extend(section_heading(block["title"]))
        s.append(para(block["overview"], "Body"))
        s.append(Spacer(1, 8))
        s.extend(simple_block(block["simple"]))

        for proc in block["processes"]:
            s.extend(process_entry(proc))

    # --- 8 Preprocessing ---
    s.append(PageBreak())
    s.extend(section_heading("8. Preprocessing Decisions Register"))
    s.append(wrap_table(["Step", "Action", "Justification"], PREPROCESSING_DECISIONS, [0.26, 0.22, 0.52]))
    s.append(PageBreak())

    # --- 9 Figures ---
    s.extend(section_heading("9. Visualizations Register (21 Figures)"))
    s.append(wrap_table(
        ["#", "Filename", "Sec.", "Description"],
        [(a, b, c, d) for a, b, c, d in FIGURES],
        [0.05, 0.27, 0.08, 0.60],
    ))
    s.append(PageBreak())

    # --- 10 Results ---
    s.extend(section_heading("10. Quantitative Results Reference"))

    s.append(para("10.1 Dataset and split", "H2"))
    s.append(wrap_table(
        ["Metric", "Value"],
        [
            ("Patients", str(PROJECT["n_patients"])),
            ("Features (predictors)", str(PROJECT["n_features"])),
            ("Target", "survival_label (1 = survived ≥ 1 year)"),
            ("Train / test", "702 / 176 (80/20 stratified)"),
            ("Class 1 / Class 0", "604 (68.8%) / 274 (31.2%)"),
            ("Imbalance ratio", "2.20 : 1"),
            ("Majority baseline accuracy", RESULTS["baseline_acc"]),
        ],
        [0.36, 0.64],
    ))

    s.append(Spacer(1, 10))
    s.append(para("10.2 Supervised learning (Random Forest)", "H2"))
    bp = RESULTS["best_rf_params"]
    s.append(wrap_table(
        ["Metric or item", "Value", "Notes"],
        [
            ("Untuned RF test accuracy", RESULTS["untuned_acc"], "100 trees, before grid search"),
            ("Tuned RF test accuracy", RESULTS["tuned_acc"],
             f"{RESULTS['improvement_pp']} pp vs {RESULTS['baseline_acc']} baseline"),
            ("Tuned RF train accuracy", RESULTS["train_acc"], "Overfitting indicator"),
            ("Train–test accuracy gap", RESULTS["overfit_gap"], "Documented in audit Section 7.3"),
            ("Macro F1 (test)", RESULTS["macro_f1"], "Average of both classes"),
            ("AUC-ROC (test)", RESULTS["auc"], "Below 0.7 clinical utility threshold"),
            ("CV F1 binary (tuning)", RESULTS["cv_f1_binary"], "GridSearch scoring metric"),
            ("CV F1 macro (comparison)", RESULTS["cv_f1_macro"], "Fair cross-model benchmark"),
            ("Best n_estimators", str(bp["n_estimators"]), "GridSearch winner"),
            ("Best max_depth", str(bp["max_depth"]), "GridSearch winner"),
            ("Top 5 features", ", ".join(RESULTS["top_features"]), "Gini importance"),
        ],
        [0.30, 0.20, 0.50],
    ))

    s.append(Spacer(1, 10))
    s.append(para("10.3 Unsupervised learning (K-Means, k=3)", "H2"))
    s.append(wrap_table(
        ["Cluster", "N", "% cohort", "Survival rate", "Clinical profile (summary)"],
        [(c, n, pct, surv, prof) for c, n, pct, surv, prof in RESULTS["clusters"]],
        [0.09, 0.11, 0.12, 0.15, 0.53],
    ))
    s.append(Spacer(1, 6))
    s.append(para(
        f"Chi-square (cluster vs survival): p = {RESULTS['chi2_p']} (not significant at α = 0.05). "
        f"Cramér's V = {RESULTS['cramers_v']} (negligible effect). "
        f"PCA visualization captures only {RESULTS['pca_var_cumulative']} of total variance.",
        "Body"))
    s.append(PageBreak())

    # --- 11 Model justifications ---
    s.extend(section_heading("11. Model Justification Summaries"))

    s.append(para("11.1 Supervised model comparison (Section 7.5)", "H2"))
    s.append(para(
        "Random Forest, Logistic Regression, SVM RBF, and Gradient Boosting were evaluated on the "
        "same 702/176 stratified split with random seed 42. All models achieve AUC below 0.63—below "
        "the 0.7 threshold commonly cited for clinical utility. SVM RBF achieves the highest macro F1 "
        "and class-0 recall, but Random Forest was retained because Gini feature importance is required "
        "for the Section 8 synthesis bridge analysis.",
        "Body"))
    s.append(Spacer(1, 6))
    s.append(wrap_table(
        ["Model", "Test Acc.", "Macro F1", "AUC", "Importance", "Notes"],
        [(m, a, f, u, i, n) for m, a, f, u, i, n in RESULTS["model_comparison"]],
        [0.21, 0.11, 0.10, 0.09, 0.17, 0.32],
    ))

    s.append(Spacer(1, 10))
    s.append(para("11.2 Unsupervised method comparison (Section 6, top)", "H2"))
    s.append(para(
        "K-Means, GMM, Agglomerative Ward, and DBSCAN were compared on the same scaled 878×20 matrix. "
        "No partition method achieves statistically significant cluster–survival association at k=3. "
        "K-Means was selected for highest silhouette at k=3, complete patient assignment (100%), "
        "interpretable centroids, and balanced cluster sizes suitable for clinical profiling.",
        "Body"))
    s.append(Spacer(1, 6))
    s.append(wrap_table(
        ["Method (k=3 unless noted)", "Silhouette", "Chi-sq p", "Assignment", "Centroids"],
        [(m, sil, p, a, c) for m, sil, p, a, c in RESULTS["unsup_comparison_k3"]],
        [0.27, 0.17, 0.14, 0.17, 0.25],
    ))

    s.append(Spacer(1, 10))
    s.append(para("11.3 Why Random Forest? (five factors)", "H2"))
    rf_factors = [
        "Non-linear interactions: all univariate |r| < 0.15; trees capture feature combinations.",
        "Built-in Gini importance: required for Section 8 synthesis without SHAP/permutation methods.",
        "Multicollinearity robustness: random feature subsampling at each split mitigates VIF issues.",
        "No scaling required: clean separation from K-Means preprocessing pipeline.",
        "Course-appropriate complexity: transparent ensemble mechanics suitable for defense.",
    ]
    for i, f in enumerate(rf_factors, 1):
        s.append(para(f"{i}. {f}", "Body"))
    s.append(PageBreak())

    # --- 12 Compliance ---
    s.extend(section_heading("12. Compliance, Limitations, and Reproducibility"))

    s.append(para("12.1 Critical rules compliance", "H2"))
    s.append(wrap_table(
        ["Rule", "Implementation evidence", "Status"],
        [
            ("No supervised leakage via scaler", "StandardScaler fit on full X for K-Means only; RF unscaled", "Met"),
            ("K-Means excludes target", "fit_predict on X_scaled; survival overlaid post-hoc", "Met"),
            ("Drop unusable columns", "ID, Predict label 1, Predict label 0 removed", "Met"),
            ("Beyond accuracy", "F1, macro F1, AUC, CM, classification report, overfitting table", "Met"),
            ("class_weight balanced", "All RandomForestClassifier instances", "Met"),
            ("random_state = 42", "Split, models, CV, PCA, K-Means", "Met"),
            ("Model justification with metrics", "Sections 6.0 and 7.0 + enhanced 7.5 comparisons", "Met"),
            ("Normality testing", "D'Agostino-Pearson on 18 continuous features", "Met"),
        ],
        [0.28, 0.54, 0.18],
    ))

    s.append(Spacer(1, 8))
    s.append(para("12.2 Known limitations", "H2"))
    limits = [
        "Moderate class imbalance (2.2:1) despite balanced weights; low class-0 recall persists.",
        "Weak univariate correlations (all |r| < 0.15) — prediction requires multivariate interactions.",
        "Severe RF overfitting: 100% train vs 71% test accuracy with tuned hyperparameters.",
        "AUC 0.613 — limited discrimination; no model in comparison exceeds AUC 0.63.",
        "Cluster–survival association not significant (p = 0.2546; Cramér's V ≈ 0.048).",
        "K-Means assumes spherical, equal-variance clusters; geometry may differ in reality.",
        "Multicollinearity among NLR, PLR, SII, CRP/ALB and component labs.",
        "Single internal test split; no external hospital validation cohort.",
        "Released features are pre-standardized (z-scores); raw clinical units not in file.",
        "Retrospective data — association, not causation; missing staging and treatment variables.",
    ]
    for i, L in enumerate(limits, 1):
        s.append(para(f"{i}. {L}", "Body"))

    s.append(Spacer(1, 8))
    s.append(para("12.3 Reproducibility", "H2"))
    s.append(para(
        "1. pip install -r requirements.txt  (add reportlab for PDF generation)\n"
        "2. Open terminal in project root (contains Dataset/ and figures/)\n"
        "3. jupyter notebook → open PCSPF_Data_Science_Capstone.ipynb\n"
        "4. Kernel → Restart & Run All (~3–8 min including grid search and model comparisons)\n"
        "5. Regenerate this PDF: python scripts/generate_audit_documentation.py",
        "Body"))
    s.append(Spacer(1, 20))
    s.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    s.append(Spacer(1, 8))
    s.append(para(
        "End of document. This record reflects the executed capstone pipeline including all audit "
        "enhancements and model justification optimizations. Intended for audit, written report "
        "support, and oral defense preparation.",
        "Body"))
    return s


def main():
    if not FONT_DIR.exists():
        raise FileNotFoundError(f"Fonts missing: {FONT_DIR}. Run font download first.")
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="PCSPF Capstone Audit Documentation",
    )
    doc.build(build_story(), onFirstPage=on_cover, onLaterPages=on_page)
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
