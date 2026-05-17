# -*- coding: utf-8 -*-
"""
Generate comprehensive capstone project documentation (PDF), Poppins typography.
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
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from audit_content import (
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
      spaceBefore=16, spaceAfter=8)
    s("H2", fontName="Poppins-SemiBold", fontSize=12, leading=16, textColor=colors.HexColor("#2c5282"),
      spaceBefore=12, spaceAfter=6)
    s("H3", fontName="Poppins-SemiBold", fontSize=10.5, leading=14, textColor=colors.HexColor("#2d3748"),
      spaceBefore=8, spaceAfter=4)
    s("Body", fontSize=9.5, leading=13, alignment=TA_JUSTIFY, spaceAfter=6)
    s("TOC", fontSize=9.5, leading=14, leftIndent=10)
    s("TH", fontName="Poppins-SemiBold", fontSize=8, leading=10, textColor=colors.white)
    s("TD", fontSize=7.5, leading=10, alignment=TA_LEFT)
    s("TDBold", fontName="Poppins-SemiBold", fontSize=7.5, leading=10)
    s("Simple", fontSize=9, leading=12, backColor=colors.HexColor("#ebf8ff"),
      borderPadding=6, leftIndent=4, rightIndent=4, spaceAfter=6)
    s("SimpleLabel", fontName="Poppins-SemiBold", fontSize=9, textColor=colors.HexColor("#2b6cb0"), spaceAfter=2)
    return ST


ST = build_styles()


def esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def para(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(esc(text).replace("\n", "<br/>"), ST[style])


def cell_para(text: str, bold: bool = False) -> Paragraph:
    return Paragraph(esc(str(text)), ST["TDBold" if bold else "TD"])


def wrap_table(headers: list[str], rows: list[list], col_fracs: list[float]) -> Table:
    """Build table with Paragraph cells so text wraps (fixes overlap)."""
    widths = [USABLE_W * f for f in col_fracs]
    header_row = [cell_para(h, bold=True) for h in headers]
    body = [[cell_para(c) for c in row] for row in rows]
    data = [header_row] + body
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def simple_block(text: str) -> list:
    return [
        para("In simple terms", "SimpleLabel"),
        para(text, "Simple"),
        Spacer(1, 4),
    ]


def process_table(proc: tuple) -> Table:
    pid, name, technique, what, params, output, decision, simple = proc
    rows = [
        ["Process ID", pid],
        ["Step name", name],
        ["Technique / method", technique],
        ["What we did (detailed)", what],
        ["Parameters / settings", params],
        ["Output / artifact", output],
        ["Decision / rationale", decision],
    ]
    widths = [3.2 * cm, USABLE_W - 3.2 * cm]
    data = [[cell_para(r[0], bold=True), cell_para(r[1])] for r in rows]
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#edf2f7")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Poppins", 7)
    canvas.setFillColor(colors.HexColor("#718096"))
    canvas.drawString(MARGIN, 1.0 * cm, "PCSPF Capstone — Complete Project Documentation (v2.0)")
    canvas.drawRightString(A4[0] - MARGIN, 1.0 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build_story():
    today = date.today().strftime("%B %d, %Y")
    s = []
    sec = section_processes()

    # Cover
    s.append(Spacer(1, 2.5 * cm))
    s.append(para(PROJECT["title"], "Title"))
    s.append(para(PROJECT["subtitle"], "Subtitle"))
    s.append(para(PROJECT["course"], "Subtitle"))
    s.append(para(PROJECT["institution"], "Subtitle"))
    s.append(Spacer(1, 1.2 * cm))
    s.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e0")))
    s.append(Spacer(1, 0.4 * cm))
    s.append(para(
        f"Document version: 2.0 | Date: {today}\n"
        f"Primary artifact: {PROJECT['notebook']}\n"
        f"Dataset: {PROJECT['data_file']}\n"
        f"Patients: {PROJECT['n_patients']} | Features: {PROJECT['n_features']} | Random seed: {PROJECT['random_state']}",
        "Body"))
    s.append(PageBreak())

    # TOC
    s.append(para("Table of Contents", "H1"))
    toc = [
        "1. Document Purpose and How to Read This Guide",
        "2. Executive Overview",
        "3. End-to-End Pipeline Map",
        "4. Techniques and Methods Glossary",
        "5. Repository and File Inventory",
        "6. Complete Process Documentation (Sections 1–9)",
        "7. Preprocessing Decisions Register",
        "8. Visualizations Register (19 Figures)",
        "9. Quantitative Results Reference",
        "10. Compliance, Limitations, and Reproducibility",
    ]
    for item in toc:
        s.append(para(item, "TOC"))
    s.append(PageBreak())

    # 1 Purpose
    s.append(para("1. Document Purpose and How to Read This Guide", "H1"))
    s.append(para(
        "This document is the formal technical record of the PCSPF capstone project. Unlike a brief summary, "
        "it documents every major process step, the technique used, parameters applied, outputs produced, "
        "and decisions made—including steps deliberately not taken. Each notebook section (1 through 9) "
        "is expanded into process tables suitable for audit, defense preparation, and report writing.",
        "Body"))
    s.append(para(
        "How to read: Each process entry contains (a) a technical description for instructors and reviewers, "
        "and (b) an 'In simple terms' box for non-technical readers. Tables use wrapped text to prevent "
        "formatting overlap. All metrics match the executed notebook run unless noted as approximate.",
        "Body"))
    s.append(PageBreak())

    # 2 Executive
    s.append(para("2. Executive Overview", "H1"))
    s.append(para(
        "Problem: Predict 1-year pancreatic cancer survival and discover patient subgroups using 20 "
        "preoperative clinical features from 878 patients. Methods: Random Forest (supervised) and "
        "K-Means (unsupervised). Data were cleaned (3 columns removed), explored, preprocessed with "
        "documented decisions, split 80/20 stratified, clustered on scaled features (k=3), and classified "
        "with tuned Random Forest (class_weight=balanced).",
        "Body"))
    s.extend(simple_block(
        "We studied hospital lab and patient data to (1) estimate who is likely to live at least one year "
        "and (2) find natural groups of similar patients. We wrote down every step so others can verify "
        "and repeat the work."
    ))
    s.append(wrap_table(
        ["Deliverable", "Status", "Location"],
        [
            ["Jupyter notebook (152 cells, 9 sections)", "Complete & executed", PROJECT["notebook"]],
            ["Figures (19 PNG, 300 DPI)", "Complete", "figures/"],
            ["Notebook builder script", "Complete", "scripts/assemble_notebook.py"],
            ["This documentation PDF", "v2.0", "Documentations/PCSPF_Capstone_Project_Audit_Documentation.pdf"],
            ["Separate written report", "Not in repository", "Student deliverable"],
            ["Presentation slides", "Not in repository", "Student deliverable"],
        ],
        [0.42, 0.18, 0.40],
    ))
    s.append(PageBreak())

    # 3 Pipeline map
    s.append(para("3. End-to-End Pipeline Map", "H1"))
    pipeline = [
        ("Phase A", "Setup", "Imports, seeds, figures/ folder"),
        ("Phase B", "Load & clean", "Excel → drop 3 cols → survival_label → 878×21"),
        ("Phase C", "EDA", "Stats, 5 chart groups, correlation, class means"),
        ("Phase D", "Preprocess", "Types, nulls, outliers, normality, VIF, decisions table"),
        ("Phase E", "Split & scale", "702/176 stratified; scaler on full X for K-Means only"),
        ("Phase F", "Unsupervised", "Elbow, silhouette, K-Means k=3, PCA, profiles, chi-square"),
        ("Phase G", "Supervised", "Baseline RF, GridSearchCV, test metrics, importance"),
        ("Phase H", "Synthesis", "Compare RF vs clusters, bridge table, limitations"),
        ("Phase I", "Conclusion", "Dynamic metrics recap"),
    ]
    s.append(wrap_table(
        ["Phase", "Notebook section", "Key outputs"],
        pipeline,
        [0.12, 0.28, 0.60],
    ))
    s.extend(simple_block(
        "The work flows left to right: prepare tools, clean data, explore, document choices, "
        "split data, find groups, build predictor, connect findings, summarize."
    ))
    s.append(PageBreak())

    # 4 Glossary
    s.append(para("4. Techniques and Methods Glossary", "H1"))
    s.append(wrap_table(
        ["Technique", "What it is", "How we used it", "Key settings"],
        TECHNIQUES_GLOSSARY,
        [0.20, 0.30, 0.28, 0.22],
    ))
    s.append(PageBreak())

    # 5 Files
    s.append(para("5. Repository and File Inventory", "H1"))
    files = [
        (PROJECT["notebook"], "Main analysis: all code, markdown, outputs"),
        (PROJECT["data_file"], "Source: 878 patients, 24 columns raw"),
        ("figures/*.png", "19 exported visualizations"),
        ("scripts/assemble_notebook.py", "Regenerates notebook programmatically"),
        ("scripts/generate_audit_documentation.py", "Regenerates this PDF"),
        ("scripts/audit_content.py", "Structured text for this PDF"),
        ("requirements.txt", "Python dependencies"),
        ("Documentations/CMSC 176 Capstone Guidelines (Clean).pdf", "Course blueprint"),
    ]
    s.append(wrap_table(["File / path", "Purpose"], files, [0.45, 0.55]))
    s.append(PageBreak())

    # 6 Sections — full process documentation
    s.append(para("6. Complete Process Documentation (Sections 1–9)", "H1"))
    s.append(para(
        "The following subsections mirror the Jupyter notebook exactly. Every listed process step was "
        "implemented in code and executed. Process IDs (e.g., 4.5) match notebook subsection numbers.",
        "Body"))

    for key in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        block = sec[key]
        s.append(para(block["title"], "H1"))
        s.append(para(block["overview"], "Body"))
        s.extend(simple_block(block["simple"]))

        for proc in block["processes"]:
            pid, name, *_ = proc
            s.append(para(f"Process {pid}: {name}", "H2"))
            s.append(process_table(proc))
            s.extend(simple_block(proc[-1]))  # simple explanation
            s.append(Spacer(1, 6))

        if key != "9":
            s.append(PageBreak())

    # 7 Preprocessing register
    s.append(PageBreak())
    s.append(para("7. Preprocessing Decisions Register", "H1"))
    s.append(para(
        "Complete list of preprocessing actions from Section 4.10. Each row is a deliberate project decision.",
        "Body"))
    s.append(wrap_table(
        ["Step", "Action", "Justification"],
        PREPROCESSING_DECISIONS,
        [0.28, 0.22, 0.50],
    ))
    s.append(PageBreak())

    # 8 Figures
    s.append(para("8. Visualizations Register (19 Figures)", "H1"))
    s.append(wrap_table(
        ["#", "Filename", "Section", "Description"],
        [(a, b, c, d) for a, b, c, d in FIGURES],
        [0.06, 0.30, 0.10, 0.54],
    ))
    s.append(PageBreak())

    # 9 Results — fixed column layout
    s.append(para("9. Quantitative Results Reference", "H1"))
    s.append(para("9.1 Dataset and split", "H2"))
    s.append(wrap_table(
        ["Metric", "Value"],
        [
            ("Patients", str(PROJECT["n_patients"])),
            ("Features", str(PROJECT["n_features"])),
            ("Target", "survival_label (1 = survived >= 1 year)"),
            ("Train / test", "702 / 176 (80/20 stratified)"),
            ("Class 1 / Class 0", "604 (68.8%) / 274 (31.2%)"),
            ("Imbalance ratio", "2.20 : 1"),
        ],
        [0.35, 0.65],
    ))
    s.append(Spacer(1, 8))
    s.append(para("9.2 Supervised learning (Random Forest)", "H2"))
    top_feat_str = ", ".join(RESULTS["top_features"])
    bp = RESULTS["best_rf_params"]
    s.append(wrap_table(
        ["Metric or item", "Value", "Notes"],
        [
            ("Majority-class baseline", RESULTS["baseline_acc"], "Always predict survived"),
            ("Untuned RF accuracy", RESULTS["untuned_acc"], "100 trees, before grid search"),
            ("Tuned RF test accuracy", RESULTS["tuned_acc"], f"{RESULTS['improvement_pp']} pp vs baseline"),
            ("Macro F1 (test)", RESULTS["macro_f1"], "Both classes combined"),
            ("AUC-ROC (test)", RESULTS["auc"], "Ranking ability"),
            ("Best CV F1 (mean)", RESULTS["cv_f1"], "On training folds only"),
            ("Best n_estimators", str(bp["n_estimators"]), "GridSearch winner"),
            ("Best max_depth", str(bp["max_depth"]), "GridSearch winner"),
            ("Best min_samples_split", str(bp["min_samples_split"]), "GridSearch winner"),
            ("Best min_samples_leaf", str(bp["min_samples_leaf"]), "GridSearch winner"),
            ("Top 5 features (importance)", top_feat_str, "Gini impurity decrease"),
        ],
        [0.32, 0.22, 0.46],
    ))
    s.extend(simple_block(
        "The prediction model beats always guessing 'survived' by about 2 percentage points on accuracy. "
        "It is only modestly better at ranking risk (AUC near 0.61). CEA, prealbumin, and CA19-9 are among "
        "the strongest inputs."
    ))
    s.append(Spacer(1, 8))
    s.append(para("9.3 Unsupervised learning (K-Means, k=3)", "H2"))
    s.append(wrap_table(
        ["Cluster", "N", "% cohort", "Survival rate", "Clinical profile (summary)"],
        [(c, n, pct, surv, prof) for c, n, pct, surv, prof in RESULTS["clusters"]],
        [0.10, 0.12, 0.12, 0.16, 0.50],
    ))
    s.append(para(
        f"Chi-square test (cluster vs survival): p = {RESULTS['chi2_p']} (not significant at alpha = 0.05). "
        "Cluster 2 has the lowest survival (63.2%) and highest inflammatory profile.",
        "Body"))
    s.append(PageBreak())

    # 10 Compliance
    s.append(para("10. Compliance, Limitations, and Reproducibility", "H1"))
    s.append(para("10.1 Critical rules compliance", "H2"))
    s.append(wrap_table(
        ["Rule", "Implementation evidence", "Status"],
        [
            ("No supervised leakage via scaler", "StandardScaler fit on full X for K-Means only; RF uses unscaled train/test", "Met"),
            ("K-Means excludes target", "fit_predict on X_scaled only; survival overlaid post-hoc", "Met"),
            ("Drop unusable columns", "ID, Predict label 1, Predict label 0 removed", "Met"),
            ("RF not scaled", "X_train, X_test raw", "Met"),
            ("K-Means scaled", "StandardScaler on X", "Met"),
            ("Beyond accuracy", "F1, AUC, CM, classification report", "Met"),
            ("class_weight balanced", "All RandomForestClassifier instances", "Met"),
            ("random_state = 42", "Split, models, CV, PCA", "Met"),
            ("Normality testing", "D'Agostino-Pearson on all 18 continuous features", "Met"),
            ("Shapiro-Wilk", "Imported; not executed (see Process 4.5)", "Partial"),
        ],
        [0.30, 0.55, 0.15],
    ))
    s.append(para("10.2 Known limitations", "H2"))
    limits = [
        "Moderate class imbalance (2.2:1) despite balanced weights.",
        "Weak univariate correlations (all |r| < 0.15) — interactions required.",
        "Single internal test split; no external hospital validation.",
        "K-Means assumes spherical, similar-variance clusters.",
        "Multicollinearity among NLR, PLR, SII, CRP/ALB and components.",
        "AUC 0.613 — limited discrimination for clinical screening.",
        "Features in released file are pre-standardized (z-scores).",
        "Retrospective data — association, not causation.",
        "Missing tumor staging and treatment variables.",
    ]
    for i, L in enumerate(limits, 1):
        s.append(para(f"{i}. {L}", "Body"))
    s.append(para("10.3 Reproducibility", "H2"))
    s.append(para(
        "1. pip install -r requirements.txt\n"
        "2. Open terminal in project root (contains Dataset/ and figures/)\n"
        "3. jupyter notebook → open PCSPF_Data_Science_Capstone.ipynb\n"
        "4. Kernel → Restart & Run All (~2–5 min for grid search)\n"
        "5. Regenerate notebook: python scripts/assemble_notebook.py\n"
        "6. Regenerate this PDF: python scripts/generate_audit_documentation.py",
        "Body"))
    s.append(Spacer(1, 20))
    s.append(para(
        "End of document. This record reflects the executed capstone pipeline and is intended for "
        "audit, reporting, and oral defense preparation.",
        "Body"))
    return s


def main():
    if not FONT_DIR.exists():
        raise FileNotFoundError(f"Fonts missing: {FONT_DIR}")
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title="PCSPF Capstone Complete Documentation",
    )
    doc.build(build_story(), onFirstPage=on_page, onLaterPages=on_page)
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
