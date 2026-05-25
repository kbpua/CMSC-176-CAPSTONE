# -*- coding: utf-8 -*-
"""Structured presenter scripts and metadata for the notebook walkthrough PDF."""

from audit_content import PROJECT, RESULTS
from study_guide_content import CORE_FINDING, SECTION_WALKTHROUGHS

NOTEBOOK_SCRIPT = {
    "title": "PCSPF Capstone - Comprehensive Notebook Script",
    "subtitle": (
        "Section-by-Section Walkthrough with Figures, Interpretations, and Presenter Notes"
    ),
    "version": "1.0",
    "output_filename": "PCSPF_Capstone_Comprehensive_Notebook_Script.pdf",
}

INTRODUCTION = (
    "This document is a presenter-ready script for PCSPF_Data_Science_Capstone.ipynb. "
    "It mirrors the notebook's nine sections in order, summarizes what each subsection does "
    "and why, embeds every exported figure with statistical and clinical interpretation, "
    "and provides opening and closing lines you can speak during a defense or walkthrough. "
    "It is not a line-by-line code dump; it focuses on methodology, decisions, outputs, "
    "and how to explain results honestly."
)

HOW_TO_USE = [
    "Read each section's Opening script before you present that notebook block.",
    "Use subsection headings (e.g., 4.4 - Outliers) to match your place in the notebook.",
    "When a figure appears, point to the image and use the Interpretation and Clinical reading boxes.",
    "Closing script lines transition to the next major section.",
    "Numbers match the executed notebook (seed 42, primary f1_macro RF tuning).",
]

PIPELINE = [
    ("A", "Section 1", "Environment, imports, RANDOM_STATE=42, figures/ at 300 DPI"),
    ("B", "Section 2", "Load Excel, clean 878x21, survival_label, class audit"),
    ("C", "Section 3", "EDA: distributions, correlations, class-conditional means"),
    ("D", "Section 4", "Preprocessing register: outliers, VIF, imbalance strategy"),
    ("E", "Section 5", "702/176 stratified split; StandardScaler for K-Means only"),
    ("F", "Section 6", "Unsupervised benchmark, K-Means k=3, PCA, chi-square"),
    ("G", "Section 7", "RF justification, f1_macro tuning, evaluation, benchmark"),
    ("H", "Section 8", "Synthesis: importance vs clusters, limitations, future work"),
    ("I", "Section 9", "Dynamic conclusion with runtime metrics"),
]

SECTION_OPENERS = {
    "1": (
        "We begin by fixing reproducibility and visualization standards. Every split, cluster, "
        "and model in this notebook uses random_state forty-two, and every figure saves at "
        "three hundred DPI into the figures folder. This section does not analyze patients yet; "
        "it sets the rules so our results can be verified and defended."
    ),
    "2": (
        "We load the PCSPF cohort of eight hundred seventy-eight pancreatic cancer patients "
        "from Excel. After dropping the anonymized ID and two empty predict columns, we retain "
        "twenty preoperative features plus a binary survival target: one means survived at least "
        "one year, zero means died within one year. About sixty-nine percent are class one, and "
        "that majority baseline will matter for every metric we report later."
    ),
    "3": (
        "Before any modeling, we characterize the data visually and statistically. This section "
        "answers: How imbalanced is survival? How are labs distributed? Do survivors and "
        "non-survivors differ on any single marker? How correlated are features with each other "
        "and with the target? The EDA conclusion is consistent: weak univariate signal, strong "
        "multicollinearity among inflammatory ratios, which motivates Random Forest and careful "
        "preprocessing documentation."
    ),
    "4": (
        "Section four is our audit trail. For each preprocessing question (missing values, "
        "outliers, normality, multicollinearity, SMOTE) we document both what we did and what "
        "we deliberately did not do. Many rows say 'retained' or 'not applied' with clinical "
        "justification. This section proves we thought about data quality rather than running "
        "default sklearn pipelines blindly."
    ),
    "5": (
        "We separate features from the target, hold out twenty percent for final Random Forest "
        "testing (one hundred seventy-six patients) and keep class proportions with stratified "
        "sampling. StandardScaler is applied to the full feature matrix for K-Means only; "
        "Random Forest trains on unscaled data because tree splits are scale-invariant. This "
        "dual pipeline is intentional and we explain it whenever scaling questions arise."
    ),
    "6": (
        "Unsupervised learning discovers patient phenotypes without using survival labels during "
        "clustering. We first benchmark K-Means against GMM, Ward, and DBSCAN, then select k equals "
        "three using elbow, silhouette, and clinical interpretability. After profiling three "
        "clusters, we overlay survival post-hoc with chi-square and Cramer's V. The honest "
        "headline: three clinically readable phenotypes, but no statistically significant "
        "prognostic separation from labs alone."
    ),
    "7": (
        "Supervised learning predicts one-year survival with Random Forest. We justify RF before "
        "training, compare tuning objectives (legacy binary F1 versus primary macro F1) and "
        "report train-test overfitting honestly. The primary tuned model trades some accuracy for "
        "better minority recall. We benchmark LR, SVM, and Gradient Boosting on the same split, "
        "then keep RF for Gini feature importance required in Section eight synthesis."
    ),
    "8": (
        "Synthesis is the intellectual core: do supervised importances and unsupervised cluster "
        "profiles point to the same biology? We compare rankings side by side, bridge predicted "
        "probabilities by cluster, and write a clinical narrative. We then list limitations and "
        "future work explicitly; staging data, external validation, and advanced explainability "
        "are named, not hidden."
    ),
    "9": (
        "The conclusion auto-fills from executed variables so numbers never go stale. In four "
        "paragraphs we restate the objective, supervised results, unsupervised results, and "
        "bridging insight. The one-sentence takeaway: "
        + CORE_FINDING
    ),
}

SECTION_CLOSERS = {
    "1": "With the environment fixed, we load and inspect the cohort in Section two.",
    "2": "Clean data in hand, we explore patterns in Section three before any modeling.",
    "3": "EDA complete; we document every preprocessing decision in Section four.",
    "4": "Preprocessing locked in; Section five splits data and scales for clustering.",
    "5": "Train-test ready; Section six clusters patients without using survival labels.",
    "6": "Clusters defined; Section seven builds the survival prediction model.",
    "7": "Supervised results documented; Section eight connects both analyses.",
    "8": "Synthesis complete; Section nine summarizes with runtime metrics.",
    "9": "End of notebook walkthrough. Use appendix slides for detailed tables during Q&A.",
}

KEY_RESULTS_TABLE = [
    ("Patients / features", f"{PROJECT['n_patients']} / {PROJECT['n_features']}"),
    ("Train / test split", "702 / 176 (80/20 stratified, seed 42)"),
    ("Majority baseline accuracy", RESULTS["baseline_acc"]),
    ("Primary RF test accuracy", RESULTS["tuned_acc"]),
    ("Primary RF macro F1", RESULTS["macro_f1"]),
    ("Primary RF AUC-ROC", RESULTS["auc"]),
    ("Train-test overfit gap (RF)", RESULTS["overfit_gap"]),
    ("K-Means clusters", f"k = {PROJECT['optimal_k']}"),
    ("Chi-square (cluster vs survival)", f"p = {RESULTS['chi2_p']}"),
    ("Cramer's V", f"~{RESULTS['cramers_v']} (negligible effect)"),
    ("Best RF params (primary)", (
        f"n_estimators={RESULTS['best_rf_params']['n_estimators']}, "
        f"max_depth={RESULTS['best_rf_params']['max_depth']}, "
        f"min_samples_leaf={RESULTS['best_rf_params']['min_samples_leaf']}"
    )),
]

LIMITATIONS_SCRIPT = (
    "State clearly: preoperative labs alone do not reach clinical utility thresholds; "
    "class-zero recall remains low; clusters are phenotypes not proven prognostic groups; "
    "missing staging, resectability, and treatment variables limit real-world deployment; "
    "single-center cohort requires external validation."
)

FUTURE_WORK_SCRIPT = (
    "Name concrete next steps: add TNM staging and treatment data, external hospital validation, "
    "Cox survival models, SHAP for non-tree models, nested cross-validation, and deeper validation "
    "of GMM or hierarchical clustering on larger cohorts."
)


def section_title(key: str) -> str:
    return SECTION_WALKTHROUGHS[key]["title"]
