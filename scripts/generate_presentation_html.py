# -*- coding: utf-8 -*-
"""Generate PCSPF Capstone defense presentation (HTML slide deck)."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from study_guide_content import CORE_FINDING, PREPROCESSING_EXTENDED
from study_guide_figures import FIGURE_GUIDE

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Documentations" / "PCSPF_Capstone_Defense_Presentation.html"
FIGURES = "../figures"

FIG_BY_FILE = {f["file"]: f for f in FIGURE_GUIDE}

_fig_counter = 0
_tbl_counter = 0


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def next_fig() -> int:
    global _fig_counter
    _fig_counter += 1
    return _fig_counter


def next_tbl() -> int:
    global _tbl_counter
    _tbl_counter += 1
    return _tbl_counter


def fig_img(filename: str, label: str = "", caption: str = "") -> str:
    n = next_fig()
    f = FIG_BY_FILE.get(filename, {})
    path = f"{FIGURES}/{filename}"
    sec = f.get("section", "")
    cap = caption or f"Source: PCSPF Capstone, n=878, Section {sec}"
    lbl = label or filename
    return f'''<div class="fig-wrap">
      <p class="fig-label">Figure {n}. {esc(lbl)}</p>
      <img src="{path}" alt="{esc(lbl)}" loading="lazy"/>
      <p class="fig-cap">{cap}</p>
    </div>'''


def slide_text(text: str, max_sentences: int = 2) -> str:
    parts = re.split(r"(?<=[.!?])\s+", str(text).strip())
    return " ".join(parts[:max_sentences])


def fig_left_slide(filename: str, label: str, right_html: str, dense: bool = False) -> str:
    """Figure on left; bullets, statistical reading, and clinical note on right."""
    f = FIG_BY_FILE.get(filename, {})
    n = 1 if dense else 2
    interp = slide_text(f.get("interpretation", ""), n)
    clin = slide_text(f.get("clinical_interpretation", ""), n)
    right_cls = "lr-right fig-right dense" if dense else "lr-right fig-right"
    layout_cls = "lr-layout fig-slide dense-slide" if dense else "lr-layout fig-slide"
    return f'''<div class="{layout_cls}">
      <div class="lr-left">{fig_img(filename, label)}</div>
      <div class="{right_cls}">
        {right_html}
        <div class="callout stat compact"><strong>Statistical reading</strong><p>{esc(interp)}</p></div>
        <div class="callout clinical compact"><strong>Clinical interpretation</strong><p>{esc(clin)}</p></div>
      </div>
    </div>'''


def vt_list(
    items: list[tuple[str, str, str]],
    compact: bool = False,
    balanced: bool = False,
    grid: bool = False,
) -> str:
    """Vertical list: (marker, title, description)."""
    cls = "vt-list"
    if compact:
        cls += " compact"
    if balanced:
        cls += " balanced"
    if grid:
        cls += " future-work-grid"
    rows = []
    for marker, title, desc in items:
        rows.append(
            f'<div class="vt-item"><span class="vt-num">{esc(marker)}</span>'
            f"<div><strong>{esc(title)}</strong><p>{esc(desc)}</p></div></div>"
        )
    return f'<div class="{cls}">' + "".join(rows) + "</div>"


def dual_table(title: str, headers: list[str], rows: list[list[str]]) -> str:
    """Split a long table into two side-by-side tables (PDF-safe layout)."""
    n = next_tbl()
    mid = (len(rows) + 1) // 2
    left = table(f"{title} (features 1-{mid})", headers, rows[:mid])
    right = table(f"{title} (features {mid + 1}-{len(rows)})", headers, rows[mid:])
    return f'<p class="tbl-label">Table {n}. {esc(title)}</p><div class="dual-table-layout">{left}{right}</div>'


VIF_ROWS = [
    ["CRP/ALB", "131.02", "High"],
    ["CRP", "130.21", "High"],
    ["Dir. Bilirubin", "77.61", "High"],
    ["Tot. Bilirubin", "76.98", "High"],
    ["SII", "18.30", "High"],
    ["NLR", "12.38", "High"],
    ["PLR", "8.21", "Moderate"],
    ["Neutrocyte", "7.97", "Moderate"],
    ["Platelet", "3.56", "Low"],
    ["Lymphocyte", "3.29", "Low"],
    ["Leukocyte", "2.48", "Low"],
    ["ALB", "1.89", "Low"],
    ["Sex", "1.61", "Low"],
    ["Abdominal Pain", "1.58", "Low"],
    ["Prealbumin", "1.38", "Low"],
    ["Lactic Dehydrogenase", "1.22", "Low"],
    ["Age", "1.10", "Low"],
    ["BMI", "1.06", "Low"],
    ["CA19-9", "1.03", "Low"],
    ["CEA", "1.01", "Low"],
]

RF_TUNING_COMPARISON_ROWS = [
    ["Test accuracy", "71.02%", "61.93%", "Legacy"],
    ["vs 68.8% majority baseline", "+2.27 pp", "-6.87 pp", "Legacy"],
    ["Train accuracy", "100.0%", "85.8%", "Primary"],
    ["Overfit gap (train - test)", "29.0 pp", "23.8 pp", "Primary"],
    ["Macro F1 (test)", "0.507", "0.550", "Primary"],
    ["AUC-ROC (test)", "0.613", "0.563", "Legacy"],
    ["Class-0 recall (test)", "10.9% (6/55)", "36.4% (20/55)", "Primary"],
    ["CV score (GridSearch)", "0.809 (binary F1)", "0.579 (macro F1)", "—"],
]

RF_TUNING_PARAMS_ROWS = [
    ["GridSearch scoring", "f1 (binary / class 1)", "f1_macro (primary)"],
    ["Param grid", "Legacy (108 combos)", "Regularized (135 combos)"],
    ["n_estimators", "300", "100"],
    ["max_depth", "15", "5"],
    ["min_samples_split", "2", "10"],
    ["min_samples_leaf", "1", "4"],
]


def dual_fig(fn1: str, lbl1: str, fn2: str, lbl2: str) -> str:
    return f'<div class="dual-fig">{fig_img(fn1, lbl1)}{fig_img(fn2, lbl2)}</div>'


def bullets(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def table(title: str, headers: list[str], rows: list[list[str]]) -> str:
    n = next_tbl()
    h = "".join(f"<th>{esc(x)}</th>" for x in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
    return f'<p class="tbl-label">Table {n}. {esc(title)}</p><table class="dt"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'


def table_bare(headers: list[str], rows: list[list[str]]) -> str:
    h = "".join(f"<th>{esc(x)}</th>" for x in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
    return f'<table class="dt"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'


def paired_tables(
    left_title: str,
    left_headers: list[str],
    left_rows: list[list[str]],
    right_title: str,
    right_headers: list[str],
    right_rows: list[list[str]],
) -> str:
    """Two related tables side-by-side (PDF-safe appendix layout)."""
    n_left = next_tbl()
    n_right = next_tbl()
    left = (
        f'<div class="paired-tbl"><p class="tbl-mini-label">Table {n_left}. {esc(left_title)}</p>'
        f"{table_bare(left_headers, left_rows)}</div>"
    )
    right = (
        f'<div class="paired-tbl"><p class="tbl-mini-label">Table {n_right}. {esc(right_title)}</p>'
        f"{table_bare(right_headers, right_rows)}</div>"
    )
    return f'<div class="dual-table-layout tuning-dual">{left}{right}</div>'


def hero_orbs() -> str:
    return """<div class="hero-orb orb1"></div>
    <div class="hero-orb orb2"></div>
    <div class="hero-orb orb3"></div>"""


def title_slide(notes: str = "") -> str:
    notes_html = f'<aside class="snotes"><strong>Speaker notes:</strong> {notes}</aside>' if notes else ""
    return f"""
<section class="slide hero-slide title-hero" data-slide="1" data-part="Front">
  <div class="si">
    {hero_orbs()}
    <div class="hero-inner">
      <span class="hero-label">Capstone Defense &middot; CMSC 176</span>
      <h1>Pancreatic Cancer Survival Prediction Based on Preoperative Clinical Features</h1>
      <div class="hero-accent-bar"></div>
      <p class="hero-sub">Supervised and Unsupervised Learning Approaches</p>
      <div class="hero-info">
        <p class="info-bold">Fundamentals of Data Science</p>
        <p>University of the Philippines Manila</p>
      </div>
      <div class="hero-members">
        <div class="member"><p class="member-name">Alysa Mariel G. Jayme</p></div>
        <div class="member"><p class="member-name">Kurt Benedict Wilbur B. Pua</p></div>
        <div class="member"><p class="member-name">Louis Conrad Andrei S. Tinio</p></div>
      </div>
    </div>
    {notes_html}
  </div>
</section>"""


def thank_you_slide(notes: str = "") -> str:
    notes_html = f'<aside class="snotes"><strong>Speaker notes:</strong> {notes}</aside>' if notes else ""
    return f"""
<section class="slide hero-slide thank-hero" data-slide="30" data-part="Front">
  <div class="si">
    {hero_orbs()}
    <div class="hero-inner">
      <h1>Thank You</h1>
      <div class="hero-accent-bar"></div>
      <p class="hero-sub">Questions &amp; Discussion</p>
      <div class="hero-members">
        <div class="member"><p class="member-name">Alysa Mariel G. Jayme</p></div>
        <div class="member"><p class="member-name">Kurt Benedict Wilbur B. Pua</p></div>
        <div class="member"><p class="member-name">Louis Conrad Andrei S. Tinio</p></div>
      </div>
      <p class="hero-footer">Appendix slides available for detailed Q&amp;A backup</p>
    </div>
    {notes_html}
  </div>
</section>"""


def section_divider(part_label: str, title: str, part_id: str, notes: str = "") -> str:
    notes_html = f'<aside class="snotes"><strong>Speaker notes:</strong> {notes}</aside>' if notes else ""
    return f"""
<section class="slide hero-slide section-hero" data-slide="{esc(part_id)}" data-part="{esc(part_id)}">
  <div class="si">
    {hero_orbs()}
    <div class="hero-inner section-inner">
      <span class="hero-label">{esc(part_label)}</span>
      <h1>{esc(title)}</h1>
      <div class="hero-accent-bar"></div>
    </div>
    {notes_html}
  </div>
</section>"""


def slide(num, part: str, title: str, body: str, notes: str = "", divider: bool = False) -> str:
    if divider:
        return section_divider(part if part in {"APP"} else f"PART {part}", title, part, notes)
    num_html = "" if num == 0 else f'<span class="snum">{num}</span>'
    notes_html = f'<aside class="snotes"><strong>Speaker notes:</strong> {notes}</aside>' if notes else ""
    return f'''
<section class="slide" data-slide="{num}" data-part="{esc(part)}">
  <div class="si">
    {num_html}
    <h2 class="st">{esc(title)}</h2>
    <div class="sb">{body}</div>
    {notes_html}
  </div>
</section>'''


def build_slides() -> str:
    global _fig_counter, _tbl_counter
    _fig_counter = 0
    _tbl_counter = 0
    s = []

    # 1 Title
    s.append(title_slide("Introduce team in 30 seconds."))

    # 2 Agenda
    s.append(slide(2, "Front", "Presentation Roadmap", vt_list([
        ("I", "Problem & Objectives", "Clinical background, research question, and four project goals"),
        ("II", "Dataset & EDA", "PCSPF cohort (n=878), target imbalance, distributions, and correlations"),
        ("III", "Preprocessing", "Data quality, outliers, VIF, scaling, and train-test split decisions"),
        ("IV", "K-Means Clustering", "Cluster selection (k=3), PCA visualization, profiles, and survival overlay"),
        ("V", "Random Forest", "Model tuning, test performance, ROC/AUC, and feature importance"),
        ("VI", "Synthesis", "Bridging supervised predictions with unsupervised cluster structure"),
        ("VII", "Limitations & Conclusion", "Honest limitations, future work, and key takeaways"),
    ], compact=True), "Slide numbers are content IDs (1-29), not PDF page numbers. Part dividers add extra pages."))

    s.append(slide(0, "I", "Problem Context and Objectives", '<p class="dlbl">PART I</p>', divider=True))

    # 3 Problem
    s.append(slide(3, "I", "Problem Statement and Clinical Background", '''
    <div class="lr-layout problem-layout">
      <div class="lr-left">
        <p class="problem-lead">Pancreatic cancer remains one of the most lethal malignancies. Preoperative risk stratification helps surgical teams, patients, and families plan treatment intensity and supportive care.</p>
        <ul class="problem-list">
          <li><span class="pli-n">1</span><span>Low overall survival compared with many other cancers</span></li>
          <li><span class="pli-n">2</span><span>Routine preoperative labs and tumor markers collected before surgery</span></li>
          <li><span class="pli-n">3</span><span>Can these features predict 1-year survival and reveal patient subgroups?</span></li>
        </ul>
      </div>
      <div class="lr-right">
        <div class="problem-rq">
          <span class="problem-rq-tag">Research Question</span>
          <p>Can routine preoperative blood tests and tumor markers predict 1-year survival in pancreatic cancer patients &mdash; and do the same features define clinically meaningful subgroups?</p>
        </div>
      </div>
    </div>
    ''', "Emphasize clinical motivation. Do not overclaim deployment."))

    # 4 Objectives
    s.append(slide(4, "I", "Project Objectives", vt_list([
        ("1", "Supervised Learning",
         "Train a tuned Random Forest to classify 1-year survival (survived >=1 yr vs died <1 yr) "
         "from 20 preoperative features. Report accuracy, macro F1, AUC-ROC, and per-class recall."),
        ("2", "Unsupervised Learning",
         "Apply K-Means (k=3) on scaled features to identify preoperative patient phenotypes. "
         "Profile clusters clinically and test survival association post hoc (chi-square)."),
        ("3", "Synthesis",
         "Compare Gini feature importance with cluster-differentiating features. "
         "Bridge RF predicted probabilities across clusters to assess directional alignment."),
        ("4", "Reproducible Pipeline",
         "Document every preprocessing choice and deliberate non-action (no SMOTE, no outlier removal, "
         "no transform). Use random_state=42 for split, tuning, and clustering reproducibility."),
    ]), "Map each objective to later slides."))

    s.append(slide(0, "II", "Dataset and Exploration", '<p class="dlbl">PART II</p>', divider=True))

    # 5 Dataset
    s.append(slide(5, "II", "Dataset Overview", '''
    <div class="lr-layout">
      <div class="lr-left">
        ''' + table("Dataset Summary", ["Item", "Detail"], [
            ["Source", "PCSPF Pancreatic Cancer Survival (Preoperative Features)"],
            ["Patients", "878"],
            ["Raw columns", "24"],
            ["After cleaning", "21 (20 features + target)"],
            ["Binary features", "2 (Sex, Abdominal Pain)"],
            ["Continuous features", "18 (z-scored in released file)"],
            ["Target", "survival_label: 1 = survived >=1 yr; 0 = died <1 yr"],
            ["Dropped", "ID, Predict label 1, Predict label 0 (100% NaN)"],
        ]) + '''
      </div>
      <div class="lr-right">
        <div class="flow-v">
          <div class="fb">24 columns</div><div class="fa">&darr;</div>
          <div class="fb accent">Drop 3 unusable</div><div class="fa">&darr;</div>
          <div class="fb">21 columns (20 + target)</div>
        </div>
        <div class="callout clinical"><strong>Clinical note</strong><p>Surgical cohort with complete preoperative labs. Released continuous values are pre-standardized (z-scores).</p></div>
      </div>
    </div>
    ''', "Mention z-score scale if asked about raw units."))

    # 6 Target distribution
    s.append(slide(6, "II", "Target Distribution and Class Imbalance",
        fig_left_slide("target_distribution.png", "Target distribution (Class 0 vs Class 1)",
            bullets([
                "Class 1 (survived &ge;1 yr): 604 patients (68.8%)",
                "Class 0 (died &lt;1 yr): 274 patients (31.2%)",
                "Imbalance ratio 2.20:1 &mdash; moderate, not severe",
                "Majority baseline = 68.8%; mitigation: class_weight='balanced'",
            ]) + '<div class="banner warn">Must beat 68.8% baseline and detect high-risk patients</div>'
        ), "Explain why accuracy alone is misleading. Class-0 recall is the clinical priority."))

    # 7 Distributions
    s.append(slide(7, "II", "EDA: Feature Distributions and Skewness",
        fig_left_slide("feature_distributions.png", "Histograms + KDE for 18 continuous features",
            bullets([
                "Right-skewed: CEA, PLR/NLR/SII, CRP, bilirubin (CA19-9 moderate only)",
                "D'Agostino-Pearson: most features non-normal (p &lt; 0.05)",
                "Decision: no Yeo-Johnson transform (RF rank-invariant; scaler for K-Means)",
            ])
        ), "Connect skewness to outlier retention on slide 11."))

    # 8 Correlation
    s.append(slide(8, "II", "EDA: Correlation Structure and Multicollinearity",
        fig_left_slide("correlation_heatmap.png", "Pearson correlation matrix (20 features + target)",
            bullets([
                "All feature-target |r| &lt; 0.15 &mdash; no strong linear predictor",
                "Strong blocks: NLR, PLR, SII, CRP/ALB, bilirubin pairs",
                "Implication: need interaction-capable model (RF)",
            ])
        ), "This justifies RF over logistic regression."))

    # 9 Class conditional
    s.append(slide(9, "II", "EDA: Class-Conditional Differences",
        fig_left_slide("class_conditional_means.png", "Top 10 mean differences by survival class",
            bullets([
                "Largest gaps: Abdominal Pain, CA19-9, Prealbumin, inflammatory markers",
            ])
        ), "Reinforce weak signal theme."))

    s.append(slide(0, "III", "Preprocessing", '<p class="dlbl">PART III</p>', divider=True))

    # 10 Data quality
    s.append(slide(10, "III", "Preprocessing: Data Quality Checks", vt_list([
        ("1", "Data Types Verified",
         "20 predictors + target after cleaning: 2 binary (Sex, Abdominal Pain) as integers; "
         "18 continuous labs as float64. Confirmed before any modeling step."),
        ("2", "Missing Values: None",
         "Zero nulls across all 878 rows and 21 columns. Verified with isnull().sum(), "
         "df.info(), and df.describe() -- no imputation required."),
        ("3", "Duplicate Rows: None",
         "0 duplicate patient records detected. Each row represents one unique surgical case "
         "with complete preoperative feature set."),
        ("4", "Imputation: Not Applied",
         "Because the released PCSPF file is complete, we did not introduce synthetic values. "
         "This preserves the original clinical cohort without imputation bias."),
        ("5", "Column Cleaning and Released Scale",
         "Dropped ID and Predict label 1/0 (100% NaN in raw file). Clean frame: 878 rows &times; 21 columns "
         "(20 features + target). Continuous labs are pre-z-scored in the released PCSPF file (mean &asymp; 0, std &asymp; 1)."),
    ]), "Speak slowly; professor audits preprocessing."))

    # 11 Outliers
    s.append(slide(11, "III", "Preprocessing: Outlier and Normality Assessment",
        fig_left_slide("outlier_boxplots.png", "Per-feature z-score boxplots with IQR outliers",
            '<p><strong>IQR rule (1.5&times;)</strong> on 18 continuous features</p>' +
            bullets([
                "Extreme values on CEA, CRP, inflammatory ratios, and bilirubin &mdash; retained",
                "Clinically severe patients, not recording errors",
                "Removing outliers would bias toward healthier cases",
                "No normality transform applied (RF rank-invariant)",
            ])
        ), "Stress clinical validity of extreme labs. Defense: outliers carry prognostic signal."))

    # 12 VIF
    s.append(slide(12, "III", "Preprocessing: Multicollinearity (VIF) and Feature Decisions", '''
    <div class="lr-layout">
      <div class="lr-left">
        ''' + table("Top 8 VIF scores (all 20 in notebook Section 4.6)", ["Feature", "VIF", "Level"], [
            ["CRP/ALB", "131.02", "High"], ["CRP", "130.21", "High"],
            ["Dir. Bilirubin", "77.61", "High"], ["Tot. Bilirubin", "76.98", "High"],
            ["SII", "18.30", "High"], ["NLR", "12.38", "High"],
            ["PLR", "8.21", "Moderate"], ["Neutrocyte", "7.97", "Moderate"],
        ]) + '''
      </div>
      <div class="lr-right">
        ''' + bullets([
            "Derived ratios (NLR, PLR, SII, CRP/ALB) correlate with components &mdash; expected",
            "Decision: retain all 20 features (RF subsampling + clinical validity)",
            "No new feature engineering; no pre-emptive feature drop",
        ]) + '''
        <div class="callout clinical"><strong>Defense</strong><p>NLR and PLR are standard preoperative indices &mdash; dropping them for VIF loses clinically validated markers.</p></div>
      </div>
    </div>
    ''', "Prepare to explain why NLR not dropped despite VIF > 10."))

    # 13 Preprocessing summary
    n13 = next_fig()
    s.append(slide(13, "III", "Preprocessing: Complete Decision Summary", f'''
    <p class="fig-label">Figure {n13}. Preprocessing decision register (Section 4.10)</p>
    <img class="full-fig" src="{FIGURES}/preprocessing_summary.png" alt="Preprocessing summary"/>
    <p class="fig-cap">Source: PCSPF Capstone, n=878. Every row documents what we did and deliberately did not do.</p>
    ''', "Professor anchor slide. Offer to expand any row in Q&A."))

    # 14 Split and scale
    s.append(slide(14, "III", "Train-Test Split and Scaling Strategy",
        fig_left_slide("scaling_before_after.png", "Feature distributions before/after StandardScaler",
            table("Split and scaling parameters", ["Setting", "Value"], [
                ["Split", "80/20 stratified"],
                ["Train / test", "702 / 176 patients"],
                ["random_state", "42"],
                ["RF inputs", "Unscaled X_train / X_test"],
                ["K-Means inputs", "StandardScaler on full X (878x20)"],
                ["Class imbalance", "class_weight='balanced'"],
            ]) + '<div class="banner warn">Anti-leakage: label never used in scaling/clustering; RF trained on train set only.</div>',
            dense=True,
        ), "Critical slide for data leakage questions."))

    s.append(slide(0, "IV", "Unsupervised Learning (K-Means)", '<p class="dlbl">PART IV</p>', divider=True))

    # 15 Elbow + silhouette
    s.append(slide(15, "IV", "K-Means: Cluster Selection (Elbow + Silhouette)", f'''
    <div class="banner info">Survival label NOT used during clustering &mdash; only post-hoc overlay</div>
    {dual_fig("elbow_method.png", "Elbow method (inertia vs k)", "silhouette_scores.png", "Silhouette score vs k")}
    ''' + bullets([
        "Silhouette max at k=2 (~0.206); k=3 (~0.133)",
        "Elbow region k=2-4",
        "Chosen k=3: three clinical phenotypes over pure silhouette optimum",
    ]), "Explain statistical vs clinical trade-off."))

    # 16 PCA clusters
    s.append(slide(16, "IV", "K-Means: Cluster Visualization (PCA)",
        fig_left_slide("pca_clusters.png", "2D PCA scatter colored by K-Means cluster",
            table("Cluster summary", ["Cluster", "N", "% cohort", "Survival rate"], [
                ["0", "519", "59.1%", "70.1%"],
                ["1", "204", "23.2%", "69.6%"],
                ["2", "155", "17.7%", "63.2%"],
            ]) + bullets([
                "PC1=20.3%, PC2=10.5% (cumulative 30.8%)",
                "69.2% of variance not visible in 2D",
                "Clustering in full 20D &mdash; PCA for visualization only",
            ])
        ), "PCA is not the clustering space."))

    # 17 Cluster profiles
    s.append(slide(17, "IV", "K-Means: Cluster Clinical Profiles",
        fig_left_slide("cluster_profiles_heatmap.png", "Z-scored mean features per cluster (heatmap)",
            '''<div class="cluster-cards">
              <div class="cc c0"><strong>Cluster 0</strong><br>Stable / Lower inflammation<br>Higher prealbumin &amp; albumin</div>
              <div class="cc c1"><strong>Cluster 1</strong><br>Hepatobiliary burden<br>Elevated bilirubin, NLR, SII</div>
              <div class="cc c2"><strong>Cluster 2</strong><br>High inflammation<br>High CRP, CRP/ALB, abdominal pain</div>
            </div>'''
        ), "Clinical heart of unsupervised section."))

    # 18 Survival overlay
    s.append(slide(18, "IV", "K-Means: Survival Overlay and Chi-Square",
        fig_left_slide("cluster_survival_overlay.png", "Survival rates per cluster with chi-square test",
            '''<div class="banner warn">Chi-square p = 0.2546 &mdash; NOT significant at &alpha;=0.05<br>Cramer's V ~ 0.048 &mdash; negligible effect</div>''' +
            bullets([
                "Cluster 0: 70.1%, Cluster 1: 69.6%, Cluster 2: 63.2%",
                "Directional trend (Cluster 2 lowest) but not statistically conclusive",
                "Honest framing: coherent direction, not proof",
            ])
        ), "Own the non-significance; professor respects honesty."))

    s.append(slide(0, "V", "Supervised Learning (Random Forest)", '<p class="dlbl">PART V</p>', divider=True))

    # 19 RF setup
    s.append(slide(19, "V", "Random Forest: Why RF, Setup, and Tuning", '''
    <div class="lr-layout">
      <div class="lr-left">
        <h3>Why Random Forest?</h3>
        ''' + bullets([
            "All |r| with target &lt; 0.15 &mdash; need nonlinear interactions",
            "Built-in Gini importance for Section 8 synthesis",
            "Robust to multicollinearity via random feature subsets",
            "No scaling required (separate pipeline from K-Means)",
        ]) + '''
        <h3>Pipeline</h3>
        <div class="flow-h">
          <div class="fb">Baseline RF<br><small>100 trees / 68.18%</small></div>
          <div class="fa">&rarr;</div>
          <div class="fb accent">GridSearchCV<br><small>3 objectives / 5-fold</small></div>
          <div class="fa">&rarr;</div>
          <div class="fb">Tuned RF (f1_macro)<br><small>61.93% test</small></div>
        </div>
      </div>
      <div class="lr-right">
        ''' + table("Primary hyperparameters (f1_macro)", ["Hyperparameter", "Value"], [
            ["n_estimators", "100"], ["max_depth", "5"],
            ["min_samples_split", "10"], ["min_samples_leaf", "4"],
            ["class_weight", "balanced"],
            ["CV scoring", "f1_macro (primary)"],
            ["Best CV macro F1", "0.579"],
        ]) + '''
        ''' + table("Tuning comparison (test set)", ["Objective", "Macro F1", "AUC", "Cl-0 Recall"], [
            ["f1 binary (legacy)", "0.507", "0.613", "10.9% (6/55)"],
            ["f1_macro (primary)", "0.550", "0.563", "36.4% (20/55)"],
            ["recall_macro", "0.550", "0.563", "36.4% (20/55)"],
        ]) + '''
        <p class="fn">Legacy f1 tuning hit 71.0% accuracy but 100% train overfit; f1_macro prioritizes balanced classes.</p>
      </div>
    </div>
    ''', "Walk through f1 vs f1_macro vs recall_macro comparison table."))

    # 20 Performance
    s.append(slide(20, "V", "Random Forest: Test Set Performance", f'''
    <div class="banner">Test acc: <strong>61.93%</strong> vs baseline <strong>68.8%</strong> (-6.87 pp) &middot; Macro F1: <strong>0.550</strong> &middot; Class-0 recall: <strong>36.4% (20/55)</strong></div>
    {dual_fig("confusion_matrix.png", "Confusion matrix (176-patient test set)", "classification_report.png", "Per-class precision, recall, F1")}
    <div class="callout clinical"><strong>Clinical impact</strong><p>Macro-aligned tuning flags 20/55 high-risk patients (up from 6/55 under legacy f1 tuning). Still misses 35/55 &mdash; research-grade, not clinic-ready.</p></div>
    ''', "Frame as modest improvement, not breakthrough."))

    # 21 ROC
    s.append(slide(21, "V", "Random Forest: ROC Curve",
        fig_left_slide("roc_curve.png", "ROC curve with AUC = 0.563",
            '<div class="banner">AUC = 0.563</div>' +
            bullets([
                "Above random (0.5) but below ~0.7 clinical utility",
                "Lower than legacy f1 tuning (0.613) by design - macro F1 trade-off",
                "All benchmark models also AUC &lt; 0.63",
            ])
        ), "Preempt 'is 0.563 good enough?'"))

    # 22 Feature importance
    s.append(slide(22, "V", "Random Forest: Feature Importance",
        fig_left_slide("feature_importance.png", "All 20 Gini importances (top 5 highlighted)",
            '<h3>Top 5 (Gini)</h3>' + bullets([
                "CEA - tumor marker",
                "Prealbumin - nutritional reserve (low = poor prognosis)",
                "CA19-9 - classic pancreatic marker",
                "CRP/ALB - inflammatory ratio",
                "BMI - body composition",
            ])
        ), "Tie back to EDA class-conditional findings."))

    # 23 Transparency
    s.append(slide(23, "V", "Performance Context (Honest Transparency)", f'''
    <div class="transp">
      {bullets([
          "Majority baseline = 68.8% - accuracy alone is misleading under imbalance",
          "All feature-target |r| &lt; 0.15 - weak univariate signal",
          "Missing staging, resectability, and treatment variables",
          "Train 85.8% vs test 61.9% - 23.8 pp overfit gap (down from 29 pp legacy f1)",
          "Retuned with scoring='f1_macro'; test macro F1 0.550 vs 0.507 legacy f1",
          "Class-0 recall 36.4% (20/55) vs 10.9% (6/55) under legacy f1 tuning",
      ])}
      <div class="callout clinical hbox"><strong>Core finding</strong><p>{esc(CORE_FINDING)}</p></div>
    </div>
    ''', "Deliver confidently, not apologetically."))

    s.append(slide(0, "VI", "Synthesis and Bridging", '<p class="dlbl">PART VI</p>', divider=True))

    # 24 Synthesis comparison
    s.append(slide(24, "VI", "Synthesis: Feature Importance vs Cluster Differentiation",
        fig_left_slide("synthesis_comparison.png", "RF importance vs cluster differentiation (top 10)",
            '<div class="callout clinical hbox"><strong>Partial convergence</strong><p>Only <strong>CRP/ALB</strong> appears in both top-5 lists. RF emphasizes tumor markers (CA19-9, CEA); clustering emphasizes inflammation and bilirubin (CRP, SII). Related clinical biology, different rankings.</p></div>'
        ), "Intellectual core &mdash; slow down."))

    # 25 Bridge table
    s.append(slide(25, "VI", "Synthesis: Predicted Probability per Cluster", '''
    ''' + table("Predicted survival probability per cluster", ["Cluster", "N", "Actual survival %", "Mean predicted %", "Difference"], [
        ["0", "519", "70.13", "70.42", "+0.29"],
        ["1", "204", "69.61", "67.29", "-2.32"],
        ["2", "155", "63.23", "62.32", "-0.91"],
    ]) + bullets([
        "Cluster 2: lowest actual and predicted &mdash; aligned ranking",
        "Cluster 0: slightly over-confident (+0.29 pp)",
        "Cluster 1: largest gap (-2.32 pp) &mdash; under-confident for hepatobiliary phenotype",
        "Directional alignment despite modest AUC",
    ]) + '''
    <div class="callout clinical"><strong>Clinical reading</strong><p>Even a modest model ranks clusters coherently &mdash; high-inflammation Cluster 2 receives lowest predicted survival.</p></div>
    ''', "Bridge supervised probabilities to unsupervised structure."))

    # 26 Narrative
    s.append(slide(26, "VI", "Synthesis: Clinical Narrative", vt_list([
        ("1", "High-Risk Subgroup (Cluster 2)",
         "Lowest 1-year survival at 63.2%. Profile dominated by elevated inflammatory "
         "and tumor-burden markers. Tuned RF assigns a lower mean predicted probability (62.3%)."),
        ("2", "Lower-Risk Subgroup (Cluster 0)",
         "Highest observed survival at 70.1% with lower inflammation and higher prealbumin. "
         "Mean predicted probability is 70.4% — partial alignment between unsupervised and supervised views."),
        ("3", "Partial Convergence Across Both Analyses",
         "Only CRP/ALB overlaps in both top-5 rankings (notebook Section 8.1). RF prioritizes tumor/nutrition markers; "
         "clusters prioritize inflammation/hepatobiliary markers. Chi-square p = 0.2546: not significant, but probability bridge (Slide 25) shows directional alignment."),
    ], balanced=True), "Most important slide — read or paraphrase carefully."))

    s.append(slide(0, "VII", "Limitations, Future Work, Conclusion", '<p class="dlbl">PART VII</p>', divider=True))

    # 27 Limitations
    s.append(slide(27, "VII", "Limitations", '''
    <div class="lr-layout">
      <div class="lr-left">
        <h3>Data</h3>
        <ol><li>Moderate class imbalance (2.2:1) despite class_weight</li>
        <li>Weak univariate correlations (all |r| &lt; 0.15)</li>
        <li>Retrospective single-source; no external validation</li>
        <li>Missing staging, surgery, treatment variables</li>
        <li>Pre-standardized labs &mdash; raw units not in file</li></ol>
      </div>
      <div class="lr-right">
        <h3>Model &amp; Analysis</h3>
        <ol start="6"><li>RF overfit reduced but present (85.8% train vs 61.9% test)</li>
        <li>Class-0 recall 36.4% (20/55) - improved vs legacy tuning but still insufficient alone</li>
        <li>K-Means assumes spherical, equal-variance clusters</li>
        <li>Multicollinearity may affect ratio-feature interpretation</li>
        <li>Cluster-survival association not significant (p=0.2546)</li>
        <li>PCA 2D captures only 30.8% of variance</li></ol>
      </div>
    </div>
    ''', "Show scientific maturity. Invite questions."))

    # 28 Future work
    s.append(slide(28, "VII", "Future Work", vt_list([
        ("1", "Model Benchmarking", "Compare XGBoost/SVM; deploy best model with SHAP explanations."),
        ("2", "Alternative Clustering", "Evaluate DBSCAN and hierarchical methods with survival validation."),
        ("3", "Feature Transformations", "Apply Yeo-Johnson before K-Means to reduce skewness effects."),
        ("4", "Feature Selection", "Use RFE or LASSO for a minimal interpretable predictor set."),
        ("5", "External Validation", "Test models on an independent hospital cohort."),
        ("6", "Richer Clinical Data", "Add TNM staging, resectability, and treatment variables."),
        ("7", "Survival Analysis", "Extend to Cox proportional hazards and Kaplan-Meier curves."),
        ("8", "Resampling Methods", "Compare SMOTE/ADASYN against class_weight='balanced'."),
        ("9", "Patient Explainability", "Apply SHAP or LIME for individualized risk review."),
        ("10", "Nested Cross-Validation", "Obtain unbiased hyperparameter tuning estimates."),
    ], compact=True, grid=True), "Connect each item to a limitation from the previous slide."))

    # 29 Conclusion
    s.append(slide(29, "VII", "Conclusion", vt_list([
        ("1", "Supervised Learning",
         "RF (f1_macro tuned): 61.93% test accuracy, AUC 0.563, macro F1 0.550. Top features: CA19-9, CEA, Prealbumin."),
        ("2", "Unsupervised Learning",
         "K-Means k=3 identified three clinical phenotypes. Cluster 2 lowest survival (63.2%). Chi-square p = 0.2546."),
        ("3", "Synthesis",
         "Complementary views: RF tumor/nutrition markers vs cluster inflammation markers; CRP/ALB is the explicit top-5 overlap."),
        ("4", "Key Takeaway",
         f"{CORE_FINDING} Staging and treatment data needed for clinical utility."),
    ], balanced=True), "60-second close. No new claims."))

    # 30 Thank you
    s.append(thank_you_slide("Point to appendix for detailed tables."))

    # APPENDIX
    s.append(section_divider("APPENDIX", "Q&A Backup Slides", "APP", "Backup slides for detailed Q&A."))

    s.append(slide("A1", "APP", "Appendix: PCA Colored by Survival Label",
        fig_left_slide("pca_survival_labels.png", "PCA scatter colored by true survival label",
            bullets(["Survival classes intermix in 2D", "Explains modest AUC", "Confirms weak linear signal"])
        ), "Backup for PCA questions."))

    s.append(slide("A2", "APP", "Appendix: Full Preprocessing Summary", f'''
    {fig_img("preprocessing_summary.png", "Full preprocessing decision register")}
    ''', "Backup for preprocessing Q&A."))

    s.append(slide("A3", "APP", "Appendix: Full Classification Report", f'''
    {fig_img("classification_report.png", "Per-class precision, recall, F1")}
    ''', "Per-class detail."))

    s.append(slide("A4", "APP", "Appendix: VIF Table (All 20 Features)",
        dual_table("Complete VIF scores", ["Feature", "VIF", "Level"], VIF_ROWS),
        "Full VIF register — all 20 features in two columns for PDF readability."))

    s.append(slide("A5", "APP", "Appendix: Model Comparison Highlights",
        table("Supervised benchmark (Section 7.5)", ["Model", "Test Acc", "Macro F1", "AUC", "Cl-0 Recall"], [
            ["RF (f1_macro tuned)","61.9%","0.550","0.563","36.4% (20/55)"],
            ["SVM RBF","61.9%","0.590","0.622","56.4% (31/55)"],
            ["Logistic Regression","55.1%","0.539","0.599","61.8% (34/55)"],
            ["Gradient Boosting","63.6%","0.482","0.581","14.5% (8/55)"],
        ]) + '<p class="fn">RF retained for Gini importance - f1_macro tuning improved macro F1 vs legacy f1 (0.507).</p>' +
        table("Unsupervised benchmark (Section 6.0, k=3)", ["Method", "Chi-sq p", "Assignment", "Selected?"], [
            ["K-Means","0.2546","100%","Yes"],["GMM","0.5259","100%","Benchmark"],
            ["Ward (k=3)","0.6478","100%","Benchmark"],["DBSCAN","0.0090","~49%","Rejected"],
        ]), "Quick-reference test and unsupervised tables. Overfitting gaps on A5b; see A6–A7 for figures and A9 for RF tuning."))

    s.append(slide("A5b", "APP", "Appendix: Train-Test Overfitting (Section 7.5)",
        '<p class="sub">Same train-test split (702/176), random_state=42 &mdash; from notebook Section 7.5</p>' +
        table("Train-test overfitting (Section 7.5)", ["Model", "Train Acc", "Test Acc", "Overfit Gap"], [
            ["RF (f1_macro tuned)","85.8%","61.9%","23.8 pp"],
            ["SVM RBF","75.5%","61.9%","13.6 pp"],
            ["Logistic Regression","65.0%","55.1%","9.8 pp"],
            ["Gradient Boosting","98.3%","63.6%","34.7 pp"],
        ]) + '<p class="fn">GB shows the largest gap (34.7 pp); LR generalizes best on this split.</p>' +
        bullets([
            "RF: 23.8 pp gap (down from 29 pp under legacy f1 tuning)",
            "GB: highest test acc (63.6%) but worst overfit &mdash; not selected",
            "All models: test accuracy near or below 68.8% majority baseline",
        ]), "Use when panel asks about overfitting or why RF was kept despite lower test acc than GB."))

    s.append(slide("A6", "APP", "Appendix: Supervised Model Comparison (Section 7.5)", f'''
    <p class="sub">Same train-test split (702/176), random_state=42 &mdash; from notebook Section 7.5</p>
    {fig_img("supervised_model_comparison.png", "Test accuracy, macro F1, AUC-ROC, and class-0 recall across four classifiers")}
    ''' + bullets([
        "SVM RBF: highest macro F1 (0.590) and AUC (0.622)",
        "RF (f1_macro): 36.4% class-0 recall (20/55) vs 10.9% under legacy f1 tuning",
        "RF retained as primary model for built-in Gini importance (Section 8 synthesis)",
        "All models: AUC &lt; 0.63 &mdash; no clinical utility threshold (0.7)",
    ]) + '', "Point to bars during model-choice Q&amp;A."))

    s.append(slide("A7", "APP", "Appendix: Unsupervised Method Comparison (Section 6.0)", f'''
    <p class="sub">K-Means vs GMM vs Ward vs DBSCAN on scaled features (878 patients) &mdash; notebook Section 6.0</p>
    {fig_img("unsupervised_model_comparison.png", "Silhouette, chi-square p-value, and survival spread at k=3")}
    ''' + bullets([
        "K-Means (k=3): selected &mdash; 100% assignment, interpretable centroids",
        "Chi-square p = 0.2546 (not significant); clusters are phenotypes, not proven prognostic groups",
        "DBSCAN: lower p but ~49% patients unassigned &mdash; rejected for defense cohort coverage",
        "Silhouette best at k=2; k=3 chosen for three clinical profiles",
    ]) + '', "Backup when panel asks why not GMM/DBSCAN."))

    s.append(slide("A8", "APP", "Appendix: Preprocessing Decision Register",
        table("Full preprocessing register", ["Step", "Action", "Justification"],
            [(a, b, c) for a, b, c, _ in PREPROCESSING_EXTENDED]
        ), "Full register for audit questions."))

    s.append(slide("A9", "APP", "Appendix: RF Tuning Comparison (Section 7.2)", '''
    <p class="sub">Legacy <code>f1</code> (binary) vs primary <code>f1_macro</code> &mdash; same split (702/176), random_state=42</p>
    <div class="tuning-stack">
    ''' + table(
        "Performance comparison (held-out test set)",
        ["Metric", "Legacy f1", "Primary f1_macro", "Better on"],
        RF_TUNING_COMPARISON_ROWS,
    ) + table(
        "Best hyperparameters from GridSearchCV",
        ["Setting", "Legacy f1", "Primary f1_macro"],
        RF_TUNING_PARAMS_ROWS,
    ) + '''
    </div>
    <div class="callout clinical compact tuning-note">
      <strong>Why primary f1_macro was adopted</strong>
      <p>Tuning aligns with our evaluation metric under class imbalance. Primary model improves macro F1 and class-0 recall (20/55 vs 6/55) with a smaller overfit gap, at the cost of test accuracy below the 68.8% majority baseline.</p>
    </div>
    <p class="fn">Stretch objective recall_macro selected the same params as f1_macro on this grid (Section 7.2).</p>
    ''', "Backup when panel asks why accuracy dropped after retuning."))

    return "\n".join(s)


CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
:root{--navy:#1E3A5F;--blue:#2563EB;--bl:#DBEAFE;--bp:#EFF6FF;--bd:#BFDBFE;--tx:#1E293B;--mt:#64748B}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;font-family:'Poppins',sans-serif;background:#0f172a;color:var(--tx)}
#deck{height:100vh}

/* --- Slide shell --- */
.slide{display:none;width:100vw;height:100vh;overflow-y:auto;background:#fff;padding:1.4rem 2.8rem 3.4rem;flex-direction:column}
.slide.active{display:flex}
.si{max-width:1140px;margin:0 auto;position:relative;width:100%;flex:1;display:flex;flex-direction:column}
.snum{position:absolute;top:0;right:0;font-size:.82rem;color:var(--mt);font-weight:600}
.st{font-size:1.45rem;font-weight:700;color:var(--navy);border-bottom:2.5px solid var(--blue);padding-bottom:.4rem;margin-bottom:.8rem}
.sb{font-size:.88rem;line-height:1.6;flex:1;display:flex;flex-direction:column}
.sb ul{margin:.4rem 0 .4rem 1.2rem}
.sb li{margin-bottom:.3rem}
.sb ol{margin:.4rem 0 .4rem 1.3rem}
.sb ol li{margin-bottom:.3rem}
.sb h3{font-size:.95rem;color:var(--navy);margin:.55rem 0 .25rem}
.sb p{margin-bottom:.35rem}
.sub{font-size:1rem;color:var(--mt);margin-bottom:.6rem}
.team{color:var(--blue);font-weight:600;font-size:1.05rem}
.muted{color:var(--mt);font-size:.82rem}
.fn{font-size:.72rem;color:var(--mt);margin-top:.25rem}

/* --- Hero slides (title + section dividers) --- */
.hero-slide{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#1e40af 100%);padding:0;overflow:hidden;color:#fff}
.hero-slide .si{max-width:100%;padding:0;justify-content:center;align-items:center;position:relative}
.hero-slide .snum{display:none}
.hero-slide .st{display:none}
.hero-inner{position:relative;z-index:2;text-align:center;max-width:840px;padding:2rem}
.hero-label{display:inline-block;background:rgba(37,99,235,.25);border:1px solid rgba(96,165,250,.4);color:#93c5fd;font-size:.72rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;padding:.35rem 1.1rem;border-radius:40px;margin-bottom:1.4rem}
.hero-inner h1{font-size:2.3rem;font-weight:700;color:#fff;line-height:1.25;margin-bottom:.6rem;letter-spacing:-.01em}
.section-inner h1{font-size:2rem}
.hero-accent-bar{width:80px;height:3px;background:linear-gradient(90deg,#60a5fa,#a78bfa);margin:0 auto 1rem;border-radius:2px}
.hero-sub{font-size:1.05rem;font-weight:400;color:rgba(191,219,254,.9);margin-bottom:2.4rem;letter-spacing:.02em}
.hero-info{display:flex;flex-direction:column;align-items:center;gap:.3rem;margin-bottom:1.8rem}
.hero-info p{margin:0;font-size:.88rem;color:rgba(203,213,225,.85);font-weight:400}
.hero-info .info-bold{color:#e2e8f0;font-weight:500}
.hero-members{display:flex;gap:2rem;justify-content:center;flex-wrap:wrap;margin-top:.4rem}
.hero-members .member{text-align:center}
.hero-members .member-name{font-size:.92rem;font-weight:600;color:#fff;letter-spacing:.01em}
.hero-footer{margin-top:1.5rem;font-size:.82rem;color:rgba(203,213,225,.85)}
.thank-hero .hero-inner h1{font-size:3.2rem}
.thank-hero .hero-sub{margin-bottom:2rem}
.hero-orb{position:absolute;border-radius:50%;filter:blur(80px);opacity:.18;pointer-events:none}
.hero-orb.orb1{width:420px;height:420px;background:#3b82f6;top:-120px;right:-80px}
.hero-orb.orb2{width:300px;height:300px;background:#8b5cf6;bottom:-100px;left:-60px}
.hero-orb.orb3{width:200px;height:200px;background:#06b6d4;bottom:60px;right:120px;opacity:.1}

/* --- Two-panel layout: figure left, content right --- */
.lr-layout{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;align-items:stretch;flex:1}
.lr-left,.lr-right{min-width:0;display:flex;flex-direction:column}

/* --- Problem statement slide --- */
.slide[data-slide="3"] .st{margin-bottom:.55rem;padding-bottom:.38rem}
.slide[data-slide="3"] .sb{padding-top:.15rem}
.problem-layout{grid-template-columns:1.12fr .88fr;gap:1.75rem;align-items:flex-start;align-content:flex-start}
.problem-layout .lr-left{justify-content:flex-start;gap:.5rem}
.problem-layout .lr-right{justify-content:flex-start}
.problem-lead{font-size:1.05rem;line-height:1.7;color:var(--tx);margin:0 0 1rem 0}
.problem-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.65rem}
.problem-list li{display:flex;gap:.85rem;align-items:flex-start;background:var(--bp);border-left:4px solid var(--blue);padding:.88rem 1.05rem;border-radius:0 8px 8px 0}
.problem-list .pli-n{display:flex;align-items:center;justify-content:center;min-width:2rem;height:2rem;background:var(--navy);color:#fff;border-radius:50%;font-size:.82rem;font-weight:700;flex-shrink:0}
.problem-list li span:last-child{font-size:.98rem;line-height:1.55;color:var(--tx);flex:1;padding-top:.2rem}
.problem-rq{background:var(--navy);color:#fff;border-radius:10px;padding:1.35rem 1.4rem;border-left:5px solid var(--blue);display:flex;flex-direction:column;gap:.55rem}
.problem-rq-tag{font-size:.74rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#93c5fd}
.problem-rq p{font-size:1.05rem;line-height:1.65;margin:0;color:#f1f5f9}

/* --- Figures --- */
.fig-wrap{margin-bottom:.5rem;flex:1;display:flex;flex-direction:column}
.fig-label{font-size:.8rem;font-weight:600;color:var(--navy);margin-bottom:.25rem}
.fig-wrap img{max-width:100%;max-height:420px;height:auto;object-fit:contain;display:block;border:1px solid var(--bd);border-radius:4px;flex:1;min-height:0}
.fig-cap{font-size:.68rem;color:var(--mt);font-style:italic;margin-top:.2rem}
.full-fig{max-width:100%;max-height:440px;object-fit:contain;display:block;margin:0 auto;border:1px solid var(--bd);border-radius:4px}
.dual-fig{display:grid;grid-template-columns:1fr 1fr;gap:.85rem;margin-bottom:.5rem}
.dual-fig .fig-wrap img{max-height:300px}

/* --- Tables --- */
.tbl-label{font-size:.8rem;font-weight:600;color:var(--navy);margin-bottom:.2rem}
.dt{width:100%;border-collapse:collapse;font-size:.78rem;margin-bottom:.5rem}
.dt th{background:var(--navy);color:#fff;padding:.35rem .5rem;text-align:left}
.dt td{border:1px solid var(--bd);padding:.3rem .5rem;vertical-align:top}
.dt tr:nth-child(even) td{background:var(--bp)}

/* --- Callouts --- */
.callout{border-radius:6px;padding:.55rem .75rem;margin:.4rem 0;font-size:.8rem;border:1px solid var(--bd)}
.callout strong{display:block;margin-bottom:.15rem;font-size:.72rem;text-transform:uppercase;letter-spacing:.03em}
.callout.stat{background:var(--bp)}
.callout.clinical{background:#f0fdf4;border-color:#86efac}
.callout.clinical strong{color:#166534}
.callout.defense{background:#fefce8;border-color:#fde047}
.callout.defense strong{color:#854d0e}
.callout.warn{background:#fff7ed;border-color:#fdba74}
.callout.warn strong{color:#9a3412}
.hbox{text-align:center}

/* --- Banners --- */
.banner{background:var(--navy);color:#fff;padding:.5rem .8rem;border-radius:6px;font-size:.82rem;text-align:center;margin-bottom:.6rem}
.banner.warn{background:#9a3412}
.banner.info{background:var(--blue)}

/* --- Vertical list (roadmap, objectives, checks) --- */
.vt-list{display:flex;flex-direction:column;gap:.65rem;flex:1;min-height:0;justify-content:flex-start}
.vt-list.balanced{justify-content:space-evenly;gap:.75rem}
.vt-list.balanced .vt-item{padding:1rem 1.1rem}
.vt-list.balanced .vt-item strong{font-size:1.05rem}
.vt-list.balanced .vt-item p{font-size:.95rem}
.vt-item{display:flex;gap:.85rem;align-items:flex-start;background:var(--bp);border-left:4px solid var(--blue);padding:.85rem 1rem;border-radius:0 8px 8px 0}
.vt-num{display:flex;align-items:center;justify-content:center;min-width:2.2rem;height:2.2rem;background:var(--navy);color:#fff;border-radius:50%;font-size:.88rem;font-weight:700;flex-shrink:0;margin-top:.05rem}
.vt-item strong{display:block;color:var(--navy);font-size:1rem;margin-bottom:.25rem}
.vt-item p{font-size:.92rem;line-height:1.5;margin:0;color:var(--tx)}
.vt-list.compact{gap:.55rem;justify-content:space-evenly}
.vt-list.compact .vt-item{padding:.72rem .95rem}
.vt-list.compact .vt-item strong{font-size:1rem}
.vt-list.compact .vt-item p{font-size:.94rem;line-height:1.42}
.vt-list.compact .vt-num{min-width:2.1rem;height:2.1rem;font-size:.82rem}
.vt-list.future-work-grid{display:grid;grid-template-columns:1fr 1fr;gap:.55rem 1rem;align-content:start}
.vt-list.future-work-grid .vt-item{padding:.65rem .85rem}
.vt-list.future-work-grid .vt-item p{font-size:.88rem;line-height:1.4}

/* --- Dual table layout (appendix) --- */
.dual-table-layout{display:grid;grid-template-columns:1fr 1fr;gap:1rem;align-items:start}
.dual-table-layout .tbl-label{display:none}
.dual-table-layout .dt{font-size:.82rem}
.dual-table-layout .dt th,.dual-table-layout .dt td{padding:.35rem .45rem;font-size:.82rem;line-height:1.35}

/* --- RF tuning appendix (A9) --- */
.tuning-stack{display:flex;flex-direction:column;gap:.35rem;margin-bottom:.35rem}
.tuning-stack .tbl-label{margin-bottom:.15rem}
.tuning-stack .dt{font-size:.78rem;width:100%}
.tuning-stack .dt th,.tuning-stack .dt td{padding:.3rem .55rem;line-height:1.32}
.tuning-note{margin-top:.35rem}
.slide[data-slide="A9"] .sb{gap:.3rem}

/* --- Figure slides: image left, all text right --- */
.fig-slide .lr-left{justify-content:center;align-items:center}
.fig-slide .lr-left .fig-wrap{width:100%;height:100%;justify-content:center}
.fig-slide.dense-slide .lr-layout{align-items:stretch;flex:1;min-height:0}
.fig-slide.dense-slide .fig-wrap img{max-height:500px;min-height:320px}
.fig-right{display:flex;flex-direction:column;gap:.65rem;min-height:0;flex:1;justify-content:space-evenly}
.fig-right.dense{gap:.55rem;justify-content:space-evenly}
.fig-right.dense .banner{font-size:.95rem;padding:.55rem .75rem;margin:.3rem 0;line-height:1.42}
.fig-right.dense .dt{font-size:.82rem;margin-bottom:.35rem}
.fig-right.dense .dt th,.fig-right.dense .dt td{padding:.32rem .45rem;font-size:.82rem;line-height:1.35}
.fig-right.dense .tbl-label{font-size:.9rem;margin-bottom:.15rem}
.fig-right.dense .callout.compact{padding:.55rem .72rem;font-size:.92rem;line-height:1.42}
.fig-right.dense .callout.compact p{font-size:.92rem}
.fig-right.dense .callout.compact strong{font-size:.78rem}
.fig-right ul{margin:.4rem 0 .4rem 1.3rem}
.fig-right li{margin-bottom:.45rem;font-size:.95rem;line-height:1.5}
.fig-right h3{font-size:1rem;color:var(--navy);margin:.2rem 0}
.fig-right p{font-size:.95rem}
.fig-right .banner{margin:.35rem 0;font-size:.92rem;padding:.55rem .75rem;line-height:1.45}
.fig-label{font-size:.92rem}
.callout.compact{padding:.6rem .8rem;margin:.3rem 0;font-size:.92rem;line-height:1.5}
.callout.compact strong{font-size:.82rem;margin-bottom:.15rem;letter-spacing:.03em}
.callout.compact p{font-size:.92rem;margin:0}

/* --- Roadmap (legacy) --- */
.roadmap{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem;margin:.8rem 0}
.ri{background:var(--bp);border:1px solid var(--bd);border-radius:6px;padding:.6rem .7rem;font-size:.85rem;font-weight:500}
.ri span{display:inline-block;background:var(--navy);color:#fff;border-radius:3px;padding:.08rem .4rem;margin-right:.35rem;font-size:.72rem}

/* --- Objectives --- */
.obj-grid{display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin-top:.5rem}
.obj{background:var(--bp);border-left:3px solid var(--blue);padding:.75rem;border-radius:0 6px 6px 0;display:flex;flex-direction:column;justify-content:center}
.obj h3{font-size:.88rem;color:var(--navy);margin-bottom:.2rem}
.on{display:inline-block;background:var(--blue);color:#fff;width:1.5rem;height:1.5rem;border-radius:50%;text-align:center;line-height:1.5rem;font-size:.75rem;margin-bottom:.25rem}

/* --- Flow diagrams --- */
.flow-v{display:flex;flex-direction:column;align-items:center;gap:.3rem;margin-bottom:.6rem}
.flow-h{display:flex;align-items:center;justify-content:center;gap:.45rem;flex-wrap:wrap;margin:.45rem 0}
.fb{background:var(--bp);border:1px solid var(--bd);padding:.45rem .75rem;border-radius:6px;font-weight:600;font-size:.8rem;text-align:center}
.fb.accent{background:var(--bl);border-color:var(--blue)}
.fa{font-size:1.1rem;color:var(--blue);font-weight:700}

/* --- Checklist --- */
.check-grid{display:grid;grid-template-columns:1fr 1fr;gap:.6rem;margin-bottom:.5rem}
.ci{display:flex;gap:.6rem;align-items:flex-start;background:var(--bp);padding:.6rem;border-radius:6px;border:1px solid var(--bd)}
.ci strong{font-size:.85rem}
.ci p{font-size:.82rem}
.ck{color:#16a34a;font-size:1.1rem;font-weight:700}

/* --- Cluster cards --- */
.cluster-cards{display:flex;gap:.6rem;margin:.45rem 0}
.cc{padding:.55rem .7rem;border-radius:6px;font-size:.8rem;border:1px solid var(--bd);flex:1}
.cc.c0{background:#ecfdf5}.cc.c1{background:#fef9c3}.cc.c2{background:#fee2e2}

/* --- Transparency --- */
.transp{background:#f8fafc;padding:.9rem;border-radius:6px;border:1px solid var(--bd)}
.transp ul{font-size:.88rem}
.transp li{margin-bottom:.4rem}

/* --- Pull quote --- */
.pq{border-left:4px solid var(--blue);padding:.8rem 1rem;background:var(--bp);font-size:.88rem;line-height:1.6;flex:1}
.pq p{margin-bottom:.55rem}

/* --- Conclusion --- */
.conc-grid{display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin-top:.5rem}
.conc{background:var(--bp);border-top:3px solid var(--blue);padding:.75rem;border-radius:0 0 6px 6px;display:flex;flex-direction:column;justify-content:center}
.conc h3{color:var(--navy);font-size:.88rem;margin-bottom:.25rem}
.conc p{font-size:.85rem}

/* --- Future work --- */
.fw-list{columns:2;column-gap:1.8rem;margin-left:1.2rem;font-size:.88rem}
.fw-list li{margin-bottom:.45rem}

/* --- Thank you --- */
.ty{text-align:center;padding-top:0;flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center}
.ty h1{font-size:2.8rem;color:var(--navy);margin-bottom:.4rem}
.ty .sub{font-size:1.15rem}
.ty .team{font-size:1.1rem}

/* --- Speaker notes --- */
.snotes{display:none;margin-top:.6rem;padding:.5rem .65rem;background:#f1f5f9;border-left:3px solid var(--mt);font-size:.72rem;color:var(--mt)}
body.show-notes .snotes{display:block}
.hero-slide .snotes{background:rgba(15,23,42,.55);color:rgba(226,232,240,.85);border-left-color:#60a5fa}

/* --- Controls --- */
#ctl{position:fixed;bottom:0;left:0;right:0;height:42px;background:rgba(30,58,95,.95);display:flex;align-items:center;justify-content:space-between;padding:0 1.2rem;z-index:100;color:#fff}
#ctl button{background:var(--blue);color:#fff;border:none;padding:.3rem .75rem;border-radius:5px;font-family:inherit;font-weight:600;cursor:pointer;font-size:.78rem}
#ctl button:hover{background:#1d4ed8}
#prog{font-size:.78rem;font-weight:500}
#hint{font-size:.65rem;opacity:.8}

@media print{html,body{overflow:visible}.slide{display:block!important;page-break-after:always;height:auto;min-height:100vh}#ctl{display:none}}
"""

JS = r"""
const S=[...document.querySelectorAll('.slide')];let i=0;
const P=document.getElementById('prog');
function go(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,j)=>s.classList.toggle('active',j===i));P.textContent=`Slide ${S[i].dataset.slide||i+1} / ${S.length}`}
document.getElementById('pv').onclick=()=>go(i-1);
document.getElementById('nx').onclick=()=>go(i+1);
document.onkeydown=e=>{
  if(['ArrowRight',' ','PageDown'].includes(e.key)){e.preventDefault();go(i+1)}
  if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(i-1)}
  if(e.key==='Home')go(0);if(e.key==='End')go(S.length-1);
  if(e.key==='f'||e.key==='F'){if(!document.fullscreenElement)document.documentElement.requestFullscreen();else document.exitFullscreen()}
  if(e.key==='s'||e.key==='S')document.body.classList.toggle('show-notes');
};go(0);
"""

TMPL = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>PCSPF Capstone Defense Presentation</title><style>{css}</style></head><body>
<div id="deck">{slides}</div>
<div id="ctl">
  <button id="pv" type="button">&#8592; Prev</button>
  <span id="prog">Slide 1</span>
  <span id="hint">Arrow / Space = navigate &middot; F = fullscreen &middot; S = speaker notes</span>
  <button id="nx" type="button">Next &#8594;</button>
</div>
<script>{js}</script></body></html>"""


def main():
    slides_html = build_slides()
    doc = TMPL.format(css=CSS, slides=slides_html, js=JS)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(doc, encoding="utf-8")
    n = len(re.findall(r'<section class="slide', doc))
    print(f"Wrote {OUTPUT} ({n} slides, {_fig_counter} figures, {_tbl_counter} tables)")


if __name__ == "__main__":
    main()
