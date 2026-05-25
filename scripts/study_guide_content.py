# -*- coding: utf-8 -*-
"""Structured content for the PCSPF Capstone Ultimate Study Guide PDF."""

from audit_content import FIGURES, PREPROCESSING_DECISIONS, PROJECT, RESULTS, section_processes

STUDY_GUIDE = {
    "title": "PCSPF Capstone — Ultimate Study Guide",
    "subtitle": "Complete Defense Preparation: Numbers, Code, Methods, Visualizations, and Q&A",
    "version": "1.2",
}

CORE_FINDING = (
    "Preoperative features carry limited but real signal for pancreatic cancer survival prediction."
)

# ---------------------------------------------------------------------------
# PART 1 — Executive Overview
# ---------------------------------------------------------------------------
EXECUTIVE_OVERVIEW = {
    "purpose": (
        "This study guide is your single defense reference for the PCSPF capstone: a dual-track "
        "analysis of 878 pancreatic cancer patients using supervised Random Forest classification "
        "and unsupervised K-Means clustering on 20 preoperative clinical features."
    ),
    "problem": (
        "Pancreatic cancer has poor prognosis and high clinical heterogeneity. Clinicians routinely "
        "collect preoperative labs, tumor markers, and inflammatory indices before surgery or treatment. "
        "Our research question: can these routinely available preoperative features predict 1-year "
        "survival (binary classification), and do unsupervised patient subgroups align with that outcome?"
    ),
    "approach": (
        "We cleaned the PCSPF Excel cohort (878 patients, 20 features + binary survival target), "
        "documented every preprocessing decision, trained a tuned Random Forest with class_weight='balanced' "
        "on an 80/20 stratified split, and ran K-Means (k=3) on StandardScaler-normalized features "
        "without using the survival label during clustering. Section 8 synthesizes whether the same "
        "biomarkers drive both prediction and grouping."
    ),
    "headline_results": [
        "Primary RF (f1_macro tuned): 61.93% test accuracy, macro F1 0.550, AUC 0.563, class-0 recall 36.4% (20/55).",
        "Legacy f1 tuning (reference): 71.02% accuracy, macro F1 0.507, class-0 recall 10.9% (6/55) — higher accuracy, worse minority recall.",
        "K-Means k=3: three phenotypes with survival ranging 63.2%-70.1%; chi-square p = 0.2546 (not significant).",
        "Top RF features (CA19-9, CEA, Prealbumin) overlap with cluster differentiation - directional convergence.",
        CORE_FINDING,
    ],
    "how_to_use": (
        "Memorize the Number Bank (Part 4), walk through preprocessing justifications (Part 6), "
        "practice defense scripts for weak metrics (Part 10), and use the Visualization Guide (Part 12) "
        "to connect every figure to a clinical sentence you can say aloud."
    ),
}

SUPERVISED_TECHNIQUE_JUSTIFICATION = (
    "We applied Random Forest because all feature–target Pearson correlations are below |0.15|, "
    "meaning no single lab provides a linear rule for survival — an ensemble of decision trees can "
    "capture nonlinear interactions among tumor markers, nutrition, and inflammation that linear models miss. "
    "Random Forest also provides Gini-based feature importance for defense and synthesis, handles "
    "multicollinearity among derived ratios (NLR, PLR, SII) via random feature subsampling, and does "
    "not require scaling — keeping the supervised pipeline cleanly separated from K-Means preprocessing. "
    "We used class_weight='balanced' rather than SMOTE so every prediction is grounded in real patients."
)

UNSUPERVISED_TECHNIQUE_JUSTIFICATION = (
    "We applied K-Means to discover preoperative patient phenotypes independent of the survival label, "
    "answering whether similar lab profiles form natural groups before we evaluate outcome overlap. "
    "K-Means requires StandardScaler so Euclidean distance treats each clinical dimension fairly — "
    "otherwise high-magnitude features would dominate cluster assignment. "
    "We chose k=3 over the silhouette-optimal k=2 because three clusters map to interpretable clinical "
    "profiles (lower-risk, hepatobiliary-burden, high-inflammation) that we could compare post-hoc "
    "against Random Forest predictions and feature importance in Section 8."
)

# ---------------------------------------------------------------------------
# PART 2 — Dataset Overview (feature catalog)
# ---------------------------------------------------------------------------
DATASET_OVERVIEW = {
    "intro": (
        "Source: Dataset/PCSPF-Pancreatic Cancer Survival based on Preoperative Features.xlsx. "
        "After removing ID and two 100%-NaN predict columns, the analysis frame is 878 rows × 21 columns "
        "(20 features + survival_label). The target is binary: 1 = survived ≥ 1 year, 0 = died within 1 year "
        "(604 vs 274 patients; 2.20:1 imbalance). Eighteen continuous features in the released file are "
        "already z-scored (mean ≈ 0, std ≈ 1); Sex and Abdominal Pain remain binary (0/1). "
        "Understanding each feature below is essential — every model result traces back to these variables."
    ),
    "ratio_formulas": (
        "Derived indices in the dataset: NLR = Neutrocyte / Lymphocyte; PLR = Platelet / Lymphocyte; "
        "SII = (Platelet × Neutrocyte) / Lymphocyte; CRP/ALB = CRP / ALB. Directed Bilirubin is a "
        "component of Total Bilirubin. These ratios compress systemic inflammation and nutrition into "
        "single numbers clinicians already interpret at bedside."
    ),
}

# (feature_name, what_it_is, clinical_implication)
DATASET_FEATURES = [
    (
        "Sex",
        "Binary indicator (0/1) for patient sex.",
        "Sex influences baseline risk, comorbidity burden, and treatment tolerance. In pancreatic cancer, "
        "it is a standard demographic covariate; modest association with survival may reflect biology or care-path differences.",
    ),
    (
        "Abdominal Pain",
        "Binary indicator (0/1) for presence of abdominal pain at presentation.",
        "Pain often signals advanced local disease, biliary obstruction, or perineural invasion. "
        "In our EDA it shows one of the largest mean differences between survival classes — a symptom marker of aggressiveness.",
    ),
    (
        "Age",
        "Patient age in years (z-scored in the released file).",
        "Older age is linked to reduced physiologic reserve and higher perioperative risk. "
        "Age contextualizes how well a patient may tolerate resection or tolerate systemic stress from advanced disease.",
    ),
    (
        "BMI",
        "Body Mass Index — weight relative to height (z-scored).",
        "Low BMI or cachexia suggests malnutrition and frailty common in pancreatic cancer. "
        "BMI ranked in the top five RF importances — nutritional status matters even before surgery.",
    ),
    (
        "CRP",
        "C-Reactive Protein — acute-phase inflammatory protein (z-scored).",
        "Elevated CRP reflects systemic inflammation driven by tumor, infection, or biliary obstruction. "
        "High CRP identifies the high-inflammation cluster profile and aligns with shorter survival phenotypes.",
    ),
    (
        "ALB",
        "Albumin — major serum protein reflecting nutrition and liver synthetic function (z-scored).",
        "Low albumin indicates malnutrition, chronic inflammation, or hepatic dysfunction. "
        "It is the denominator of CRP/ALB; together they capture the inflammation–nutrition balance.",
    ),
    (
        "CRP/ALB",
        "Ratio of CRP to albumin — combined inflammatory and nutritional index (z-scored).",
        "Higher values mean inflammation outweighs nutritional reserve. "
        "Clinicians use CRP/ALB as a prognostic score in several cancers; it strongly characterizes Cluster 2 (high-inflammation).",
    ),
    (
        "Leukocyte",
        "Total white blood cell count (z-scored).",
        "Leukocytosis may reflect infection, steroid use, or paraneoplastic inflammation. "
        "It feeds into NLR and SII — part of the broader immune–inflammatory picture before treatment.",
    ),
    (
        "Neutrocyte",
        "Absolute neutrophil count (z-scored).",
        "Neutrophils rise with bacterial infection, stress, and tumor-associated inflammation. "
        "Elevated neutrophils increase NLR and SII — markers linked to immunosuppressive tumor microenvironment.",
    ),
    (
        "Platelet",
        "Platelet count (z-scored).",
        "Thrombocytosis can occur in malignancy (paraneoplastic) and inflammation. "
        "Platelets enter PLR and SII calculations — high values suggest active systemic inflammatory response.",
    ),
    (
        "Lymphocyte",
        "Absolute lymphocyte count (z-scored).",
        "Lymphocytes reflect adaptive immune competence; low counts suggest immunosuppression. "
        "Because NLR, PLR, and SII all divide by lymphocyte, low lymphocytes amplify inflammatory ratio signals.",
    ),
    (
        "NLR",
        "Neutrophil-to-lymphocyte ratio (z-scored).",
        "NLR balances innate vs adaptive immunity — high NLR implies neutrophil-driven inflammation dominating. "
        "Widely studied in pancreatic cancer prognosis; elevated in Cluster 1 (hepatobiliary burden) in our analysis.",
    ),
    (
        "PLR",
        "Platelet-to-lymphocyte ratio (z-scored).",
        "PLR captures platelet-driven inflammation relative to lymphocyte immunity. "
        "Correlates with NLR and SII clinically; retained despite high VIF because it is a standard bedside index.",
    ),
    (
        "SII",
        "Systemic Immune-Inflammation Index: (Platelet × Neutrocyte) / Lymphocyte (z-scored).",
        "SII integrates platelets, neutrophils, and lymphocytes into one systemic inflammation score. "
        "High SII marks aggressive biology; it differentiates cluster profiles alongside CRP and abdominal pain.",
    ),
    (
        "Lactic Dehydrogenase",
        "LDH — enzyme released with tissue breakdown and high tumor burden (z-scored).",
        "Elevated LDH indicates extensive cell turnover or liver involvement. "
        "It is a non-specific but important marker of disease bulk and metabolic stress preoperatively.",
    ),
    (
        "CA19-9",
        "Carbohydrate antigen 19-9 — classic pancreatic tumor marker (z-scored).",
        "CA19-9 rises with tumor volume and biliary obstruction; among the most cited markers in pancreatic cancer. "
        "Top univariate separator in EDA and rank-3 RF feature — central to both supervised and unsupervised findings.",
    ),
    (
        "CEA",
        "Carcinoembryonic antigen — broad epithelial tumor marker (z-scored).",
        "CEA elevation suggests mucin-producing or advanced epithelial malignancy. "
        "Ranked #1 in RF Gini importance in our model — strongest single contributor to survival classification splits.",
    ),
    (
        "Prealbumin",
        "Transthyretin precursor — sensitive marker of nutritional status and catabolism (z-scored).",
        "Low prealbumin reflects short-term malnutrition and inflammation-driven protein loss. "
        "Rank-2 RF feature and higher in longer-survival class in EDA — nutritional reserve is prognostic.",
    ),
    (
        "Total Bilirubin",
        "Total serum bilirubin — pigment from hemoglobin breakdown; rises with biliary obstruction (z-scored).",
        "Hyperbilirubinemia in pancreatic cancer often reflects head-of-pancreas tumors compressing the bile duct. "
        "Elevated in Cluster 1; obstructive jaundice is both a symptom and a severity marker.",
    ),
    (
        "Directed Bilirubin",
        "Conjugated (direct) fraction of total bilirubin (z-scored).",
        "Elevated direct bilirubin specifically indicates hepatobiliary obstruction or cholestasis. "
        "Correlates strongly with Total Bilirubin; together they define the hepatobiliary burden phenotype in clustering.",
    ),
]

# ---------------------------------------------------------------------------
# PART 3 — Project Identity
# ---------------------------------------------------------------------------
PROJECT_IDENTITY = {
    "summary": (
        "This capstone applies supervised Random Forest classification and unsupervised K-Means "
        "clustering to the PCSPF dataset of 878 pancreatic cancer patients with 20 preoperative "
        "clinical features. The goal is to predict 1-year survival (binary target) and discover "
        "patient subgroups, then synthesize whether the same biomarkers drive both prediction and grouping."
    ),
    "dataset": {
        "n_patients": 878,
        "raw_columns": 24,
        "clean_columns": 21,
        "n_features": 20,
        "target": "survival_label (1 = survived ≥ 1 year; 0 = died within 1 year)",
        "source": "Dataset/PCSPF-Pancreatic Cancer Survival based on Preoperative Features.xlsx",
        "class_1": "604 (68.8%)",
        "class_0": "274 (31.2%)",
        "ratio": "2.20 : 1",
    },
    "techniques": (
        "Random Forest (supervised primary classifier) and K-Means (unsupervised clustering, k=3). "
        "Benchmarks: LR, SVM RBF, Gradient Boosting (supervised); GMM, Ward, DBSCAN (unsupervised)."
    ),
}

# ---------------------------------------------------------------------------
# PART 2 — Number Bank
# ---------------------------------------------------------------------------
NUMBER_BANK = {
    "Dataset": [
        ("Patients", "878"),
        ("Raw columns → clean", "24 → 21 (20 features + 1 target)"),
        ("Class 1 (survived ≥ 1 yr)", "604 (68.8%)"),
        ("Class 0 (< 1 yr)", "274 (31.2%)"),
        ("Imbalance ratio", "2.20 : 1"),
        ("Dropped columns", "ID, Predict label 1, Predict label 0"),
        ("Target name", "survival_label"),
    ],
    "Train-test split": [
        ("Train / test", "702 / 176"),
        ("Split ratio", "80 / 20"),
        ("Method", "Stratified (preserves class proportions)"),
        ("random_state", "42"),
    ],
    "Supervised (primary RF, f1_macro tuned)": [
        ("Test accuracy", "61.93%"),
        ("Majority baseline", "68.8%"),
        ("Vs baseline", "-6.87 percentage points (macro F1 trade-off)"),
        ("Untuned RF test acc", "68.18%"),
        ("Train accuracy", "85.8%"),
        ("Overfit gap", "23.8 pp"),
        ("Macro F1 (test)", "0.550"),
        ("AUC-ROC (test)", "0.563"),
        ("Class-0 recall", "36.4% (20 / 55 in test set)"),
        ("CV macro F1 (GridSearch primary)", "0.579"),
        ("Legacy f1 tuning (reference)", "71.02% acc, 0.507 macro F1, 10.9% cl-0 recall"),
    ],
    "Tuned hyperparameters (primary)": [
        ("n_estimators", "100"),
        ("max_depth", "5"),
        ("min_samples_leaf", "4"),
        ("min_samples_split", "10"),
        ("Grid combinations (regularized)", "135 per objective"),
        ("Tuning objectives compared", "f1 (legacy), f1_macro (primary), recall_macro (stretch)"),
        ("Cross-validation", "5-fold StratifiedKFold"),
        ("GridSearch scoring (primary)", "f1_macro"),
        ("class_weight", "balanced"),
    ],
    "class_weight formula": [
        ("Formula", "weight_c = n_samples / (n_classes × count_c)"),
        ("Class 0 weight", "~1.60"),
        ("Class 1 weight", "~0.73"),
        ("Effect", "Minority class errors penalized more during tree building"),
    ],
    "Unsupervised (K-Means k=3)": [
        ("Optimal k", "3 (clinical interpretability over k=2 silhouette peak)"),
        ("Silhouette at k=3", "~0.133"),
        ("Silhouette max (k=2)", "~0.206"),
        ("Cluster 0", "519 patients (59.1%) — 70.1% survival"),
        ("Cluster 1", "204 patients (23.2%) — 69.6% survival"),
        ("Cluster 2", "155 patients (17.7%) — 63.2% survival"),
        ("Chi-square p", "0.2546 (NOT significant at α=0.05)"),
        ("Cramér's V", "~0.056 (negligible effect)"),
    ],
    "PCA": [
        ("PC1 variance", "20.3%"),
        ("PC2 variance", "10.5%"),
        ("Cumulative (PC1+PC2)", "30.8%"),
        ("Not visible in 2D", "69.2% of variance"),
    ],
    "Top RF features (Gini)": [
        ("Rank 1-5", "CA19-9, CEA, Prealbumin, CRP/ALB, BMI"),
    ],
    "Model comparison highlight": [
        ("Best macro F1", "SVM RBF ~0.590"),
        ("Best AUC", "SVM RBF ~0.622"),
        ("RF retained for", "Gini feature importance → Section 8 synthesis"),
    ],
}

# ---------------------------------------------------------------------------
# PART 4 — Preprocessing Decision Register (extended)
# ---------------------------------------------------------------------------
PREPROCESSING_EXTENDED = [
    ("Drop ID, Predict labels", "Removed 3 columns",
     "ID anonymized; Predict columns 100% NaN — unusable labels.",
     "If kept: model would fail on NaN or leak unusable information."),
    ("Missing values", "No imputation",
     "Zero nulls after column drop; verified three ways.",
     "If imputed: invented values for clinically measured labs — unjustifiable."),
    ("Duplicates", "None removed",
     "0 duplicate rows confirmed.",
     "If removed aggressively: no duplicates exist anyway."),
    ("Outliers", "Retained all",
     "IQR/z-score documented; extremes are clinically severe patients.",
     "If removed: lose 5–10% of data including highest-risk cases; bias toward mild disease."),
    ("Normality transform (Yeo-Johnson)", "Not applied",
     "RF rank-invariant; StandardScaler sufficient for K-Means.",
     "If applied: distorts clinical interpretability of lab values; no RF benefit."),
    ("Multicollinearity (VIF)", "Retain all 20 features",
     "RF random feature subsampling; ratio features clinically validated.",
     "If dropped: lose validated indices (NLR, PLR, SII); arbitrary threshold at VIF>10."),
    ("Feature engineering", "None added",
     "NLR, PLR, SII, CRP/ALB already in dataset.",
     "If added: risk overfitting without domain validation."),
    ("Feature selection", "All 20 retained",
     "Same set for RF and K-Means; importance post-hoc.",
     "If pre-dropped: removes features RF might combine nonlinearly."),
    ("SMOTE", "Not used",
     "class_weight='balanced' preferred; real patients only.",
     "If SMOTE: synthetic minority samples; harder to defend clinically."),
    ("RF scaling", "None",
     "Tree splits are scale-invariant.",
     "If scaled for RF: no accuracy change; unnecessary step."),
    ("K-Means scaling", "StandardScaler on full X (878×20)",
     "Euclidean distance requires comparable scales.",
     "If unscaled: large-magnitude features dominate distance."),
    ("Train-test split", "80/20 stratified, seed=42",
     "702 train / 176 test; proportions preserved.",
     "If random split without stratify: test set might have different class ratio."),
]

# ---------------------------------------------------------------------------
# PART 9 — Model comparison tables (split for readable PDF layout)
# ---------------------------------------------------------------------------
SUPERVISED_COMPARISON_A = {
    "title": "Table 9A — Accuracy and discrimination",
    "headers": ["Model", "Train Acc", "Test Acc", "Overfit Gap", "Macro F1", "AUC"],
    "rows": [
        ["RF (f1_macro tuned)", "85.8%", "61.9%", "23.8 pp", "0.550", "0.563"],
        ["Logistic Regression", "65.0%", "55.1%", "9.8 pp", "0.539", "0.599"],
        ["SVM RBF", "75.5%", "61.9%", "13.6 pp", "0.590", "0.622"],
        ["Gradient Boosting", "98.3%", "63.6%", "34.7 pp", "0.482", "0.581"],
    ],
    "col_fracs": [0.22, 0.13, 0.13, 0.16, 0.16, 0.20],
    "clinical_note": (
        "Clinically: all models stay below AUC 0.63 — none reach deployable discrimination from labs alone. "
        "SVM RBF ranks highest but still cannot reliably separate 1-year survivors from non-survivors. "
        "RF's 23.8 pp overfit gap is reduced vs legacy f1 tuning (29 pp) but test accuracy falls below baseline by design."
    ),
}

SUPERVISED_COMPARISON_B = {
    "title": "Table 9B — Minority class and interpretability",
    "headers": ["Model", "F1 Class 0", "F1 Class 1", "Class-0 Recall", "CV Macro F1", "Feature Importance"],
    "rows": [
        ["RF (f1_macro tuned)", "0.374", "0.727", "36.4% (20/55)", "0.579", "Yes — Gini"],
        ["Logistic Regression", "0.463", "0.615", "61.8% (34/55)", "0.572", "No — needs SHAP"],
        ["SVM RBF", "0.481", "0.700", "56.4% (31/55)", "0.587", "No — needs SHAP"],
        ["Gradient Boosting", "0.200", "0.765", "14.5% (8/55)", "0.550", "Yes — Gini"],
    ],
    "col_fracs": [0.20, 0.14, 0.14, 0.18, 0.16, 0.18],
    "clinical_note": (
        "Clinically: Class-0 recall is what matters for catching patients who die within a year. "
        "RF (f1_macro tuned) finds 20 of 55 high-risk patients — still insufficient alone but improved vs legacy f1 tuning (6/55) and baseline (0/55)."
        "We kept RF because Gini importance powers the synthesis bridge in Section 8."
    ),
}

UNSUPERVISED_COMPARISON_A = {
    "title": "Table 9C — Cluster quality and survival association",
    "headers": ["Method (k=3)", "Silhouette", "Chi-sq p", "Cramér's V", "Survival Spread"],
    "rows": [
        ["K-Means", "Highest (~0.133)", "0.2546", "~0.056", "70.1% → 63.2%"],
        ["GMM", "Lower", "~0.53", "Negligible", "Similar band"],
        ["Agglomerative Ward", "Mid", "~0.65", "Negligible", "Similar band"],
        ["DBSCAN (best)", "Outlier pockets", "<0.01", "Varies", "Uneven"],
    ],
    "col_fracs": [0.22, 0.18, 0.14, 0.16, 0.30],
    "clinical_note": (
        "Clinically: no algorithm proves clusters predict survival (all p > 0.05 at k=3 except DBSCAN's "
        "partial assignment). K-Means Cluster 2 still shows the directionally sickest group (63.2% survival). "
        "The weak association confirms labs describe phenotype, not definitive prognosis."
    ),
}

UNSUPERVISED_COMPARISON_B = {
    "title": "Table 9D — Practical clustering properties",
    "headers": ["Method (k=3)", "Smallest Cluster", "Assignment %", "Centroids", "Selected?"],
    "rows": [
        ["K-Means", "155 (Cluster 2)", "100%", "Yes", "Yes — primary"],
        ["GMM", "Varies", "100%", "Yes (means)", "Benchmark"],
        ["Agglomerative Ward", "Varies", "100%", "No", "Benchmark"],
        ["DBSCAN (best)", "Small noise clusters", "~49%", "No", "Rejected — incomplete"],
    ],
    "col_fracs": [0.22, 0.22, 0.16, 0.18, 0.22],
    "clinical_note": (
        "Clinically: every patient must map to a phenotype for hospital-wide profiling — K-Means assigns all 878. "
        "DBSCAN leaving 51% unlabeled is unusable for describing a surgical cohort. "
        "Centroids let us name Cluster 1 'hepatobiliary burden' and Cluster 2 'high inflammation.'"
    ),
}

# FIGURE_GUIDE imported from study_guide_figures.py

# ---------------------------------------------------------------------------
# PART 8 — Weak results defense scripts
# ---------------------------------------------------------------------------
DEFENSE_SCRIPTS = [
    ("Test accuracy 61.93% (below 68.8% majority baseline)",
     "Acknowledge: Primary f1_macro tuning yields 61.93% test accuracy — below the 68.8% majority baseline. "
     "Contextualize: Baseline accuracy is misleading under imbalance (0% high-risk detection). "
     "Reframe: Macro-aligned tuning improves macro F1 (0.507 to 0.550) and class-0 recall (10.9% to 36.4%). "
     "Value: Shows we optimized for balanced evaluation, not accuracy alone."),
    ("AUC 0.563 (below clinical utility ~0.7)",
     "Acknowledge: 0.563 is below the 0.7 threshold often cited for clinical deployment — and lower than legacy f1 tuning (0.613). "
     "Contextualize: SVM RBF, the best benchmark, reaches 0.622 — the ceiling is dataset-level. "
     "Reframe: AUC > 0.5 confirms non-random signal; macro F1 tuning trades AUC for minority recall. Value: "
     "Identifies which markers matter (CA19-9, CEA, Prealbumin) for future multimodal models."),
    ("Overfitting (85.8% train vs 61.9% test)",
     "Acknowledge: Primary model still overfits with a 23.8 pp gap. "
     "Contextualize: Legacy f1 tuning reached 100% train / 29 pp gap; f1_macro tuning reduced memorization. "
     "Reframe: Regularization analysis and three-objective tuning table document the trade-off transparently. "
     "Value: Demonstrates understanding of bias-variance trade-off under weak signal."),
    ("Class-0 recall 36.4% (20/55)",
     "Acknowledge: The model still misses 35 of 55 high-risk test patients — clinically unacceptable alone. "
     "Contextualize: Improved from 6/55 under legacy f1 tuning; SVM reaches 31/55 and LR 34/55 on same split. "
     "Reframe: vs baseline (0/55), macro-aligned RF provides meaningful risk detection progress. "
     "Value: Frames honest clinical limitation; threshold sweep in Section 7.2 explores trade-offs."),
    ("Chi-square p = 0.2546 (not significant)",
     "Acknowledge: We cannot reject independence of cluster and survival at α=0.05. "
     "Contextualize: GMM and Ward also fail significance — algorithm choice is not the issue. "
     "Reframe: Cluster 2 shows directionally lowest survival (63.2% vs ~70%) — coherent clinical "
     "story without statistical proof. Value: Scientific honesty strengthens credibility."),
    ("Cramér's V ≈ 0.056 (negligible)",
     "Acknowledge: Effect size is negligible even if sample size were larger. "
     "Contextualize: p-value alone can mislead with n=878 — V confirms association is weak in "
     "magnitude, not just non-significant. Reframe: Clustering adds descriptive phenotypes, not "
     "prognostic stratification. Value: Shows effect-size literacy beyond p-hacking."),
    ("Legacy f1 CV ~0.809 vs primary test macro F1 0.550",
     "Acknowledge: Legacy binary-F1 tuning reported CV ~0.809 while primary test macro F1 is 0.550. "
     "Contextualize: We now compare three objectives (f1, f1_macro, recall_macro) in Section 7.2. "
     "Reframe: Primary model uses f1_macro (CV 0.579) aligned with test macro F1; legacy row kept for reference. "
     "Value: Shows iterative optimization and metric literacy."),
    ("Baseline RF 68.18% below majority baseline 68.8%",
     "Acknowledge: Untuned RF underperforms predicting-all-survivors. Contextualize: Untuned model "
     "with 100 trees and default depth still tries to predict minority class, hurting accuracy. "
     "Reframe: Tuning to 71.02% shows hyperparameter search adds value; untuned result motivates "
     "GridSearchCV. Value: Shows full pipeline narrative from baseline → tuned."),
]

# ---------------------------------------------------------------------------
# PART 11 — Curveball Q&A (25 questions)
# ---------------------------------------------------------------------------
QA_BANK = [
    ("What if you removed derived ratios (NLR, PLR, SII, CRP/ALB) and retrained?",
     "VIF would drop, but clinically validated inflammation indices would be lost. RF handles "
     "multicollinearity via random feature subsets. Retraining might shift importance rankings "
     "slightly but AUC would likely stay in the same ~0.61 band given weak overall signal."),
    ("Why did GridSearchCV pick the least regularized params?",
     "scoring='f1' on positive class rewards catching survivors (majority). Deep trees maximize "
     "training F1, producing 100% train accuracy. Less regularized params win CV even though they "
     "overfit — we document this and show regularization trade-offs separately."),
    ("Is 176 test patients enough for reliable evaluation?",
     "176 is modest — class 0 has only 55 test samples, so recall estimates have wide confidence "
     "intervals. Stratification preserves proportions. External validation on another cohort would "
     "be needed for deployment claims."),
    ("Why not nested cross-validation?",
     "Nested CV is best practice for unbiased performance estimation but computationally expensive "
     "with 108 grid combinations. We use holdout test set for final evaluation and 5-fold CV for "
     "tuning — standard for course scope; nested CV listed as future work."),
    ("How do you know original values if data is pre-standardized?",
     "We work with released z-scores (mean≈0, std≈1). Rankings, correlations, and model splits are "
     "valid. Absolute clinical units are not recoverable from this file — noted as limitation."),
    ("Why is CEA #1 instead of CA19-9?",
     "Gini importance measures multivariate split contribution, not univariate correlation. CEA may "
     "interact with nutrition/inflammation markers. CA19-9 still ranks top 3 — both are relevant."),
    ("Could you combine cluster membership as a feature for RF?",
     "Possible, but risks leakage if clusters were built with target information — ours were not. "
     "Adding cluster labels might help slightly but mixes supervised/unsupervised pipelines; "
     "we kept them separate for clean synthesis comparison."),
    ("What does the confusion matrix tell you about clinical deployment?",
     "High false-negative rate for class 0 — deploying this model alone would miss most patients "
     "who die within a year. Suitable for research exploration, not standalone triage."),
    ("What is the false negative cost vs false positive cost?",
     "False negative (predict survive, dies <1yr): high clinical cost — missed palliative planning. "
     "False positive (predict die, survives): causes unnecessary anxiety. Our model skews toward "
     "false negatives for class 0 despite balanced weights."),
    ("What would you need to make this clinically deployable?",
     "AUC ≥ 0.7+, external validation, staging/treatment variables, calibration on prospective "
     "cohort, regulatory pathway, and acceptable recall for high-risk class."),
    ("If you had 10× more data, what would change?",
     "More stable metrics, possible deep learning, reliable minority-class recall estimates, "
     "potentially significant cluster-survival association if signal exists."),
    ("What assumptions does chi-square test require?",
     "Expected counts ≥ 5 per cell, independent observations, categorical variables. Our cluster × "
     "survival table meets count assumptions with n=878."),
    ("Why is silhouette score low (0.133 at k=3)?",
     "Patients overlap in 20D preoperative space — no crisp natural partitions. Low silhouette "
     "reflects data geometry, not coding error."),
    ("What does n_init=10 do in K-Means?",
     "Runs K-Means 10 times with different centroid seeds; keeps best inertia result. Reduces "
     "bad-local-minimum risk from random initialization."),
    ("What happens if you change random_state from 42?",
     "Train/test split, cluster labels, and RF predictions change slightly. Metrics stay in same "
     "band (~71% acc, AUC ~0.61) — conclusions robust qualitatively."),
    ("What is bootstrap aggregating and how does it reduce variance?",
     "Each tree trains on a bootstrap sample (~63% unique points); predictions vote/average. "
     "Averaging decorrelated trees reduces variance vs single deep tree."),
    ("Why 5-fold and not 10-fold CV?",
     "5-fold balances bias-variance in CV estimate with compute cost (108 combos × 5 fits). "
     "10-fold would be more expensive with minimal change for n=702."),
    ("What is the difference between Gini importance and permutation importance?",
     "Gini: mean impurity decrease at splits using a feature. Permutation: shuffles feature, "
     "measures performance drop. Permutation is more reliable but costlier — Gini sufficient here."),
    ("What would SHAP values show that Gini importance doesn't?",
     "SHAP gives per-patient feature contributions and interaction effects. Gini is global ranking "
     "only. SHAP listed as future work for richer interpretability."),
    ("If you could add one feature to the dataset, what would it be and why?",
     "TNM staging or resectability status — strongest prognostic factor missing from preoperative "
     "labs-only dataset; would likely raise AUC substantially."),
    ("Why retain outliers instead of capping?",
     "Extreme CA19-9/CRP values identify severe disease; capping would compress signal from "
     "sickest patients."),
    ("Why D'Agostino-Pearson instead of Shapiro-Wilk?",
     "Shapiro-Wilk is recommended for n < 5000 but degrades with large n; D'Agostino-Pearson "
     "handles n=878 continuous features appropriately."),
    ("Does scaling for K-Means leak survival information?",
     "No — scaler fit on X only (features), not y. Survival label never enters clustering fit."),
    ("Why k=3 over k=2 when silhouette favors k=2?",
     "Three clusters map to low/medium/high inflammation phenotypes clinically; k=2 merges "
     "distinct hepatobiliary vs inflammation profiles."),
    ("How does synthesis add value if both analyses are weak?",
     "Independent convergence on CEA, Prealbumin, CA19-9 strengthens biomarker narrative beyond "
     "either analysis alone — mutual validation of limited signal."),
]

# ---------------------------------------------------------------------------
# PART 12 — Slide-to-section mapping
# ---------------------------------------------------------------------------
SLIDE_SECTION_MAP = [
    ("1", "Title Slide", "—", "Front matter"),
    ("2", "Agenda", "—", "Front matter"),
    ("3", "Problem Statement", "—", "Clinical context (pre-notebook)"),
    ("4", "Project Objectives", "—", "Maps to Sections 6–8 objectives"),
    ("5", "Dataset Overview", "2", "Data loading, column drop, 878×21"),
    ("6", "Target Distribution", "2.3, 3.2", "target_distribution.png"),
    ("7", "Feature Distributions", "3.3, 4.5", "feature_distributions.png"),
    ("8", "Correlation / Multicollinearity", "3.5–3.6, 4.6", "correlation_heatmap.png"),
    ("9", "Class-Conditional Differences", "3.4, 3.7", "class_conditional_means.png, boxplots"),
    ("10", "Data Quality Checks", "4.1–4.3", "Types, nulls, duplicates"),
    ("11", "Outliers & Normality", "4.4–4.5", "outlier_boxplots.png"),
    ("12", "VIF & Feature Decisions", "4.6–4.8", "VIF table in notebook"),
    ("13", "Preprocessing Summary", "4.10", "preprocessing_summary.png"),
    ("14", "Split & Scaling", "5.1–5.3", "scaling_before_after.png"),
    ("15", "K-Means Selection", "6.1–6.3", "elbow_method.png, silhouette_scores.png"),
    ("16", "PCA Clusters", "6.5", "pca_clusters.png"),
    ("17", "Cluster Profiles", "6.6", "cluster_profiles_heatmap.png"),
    ("18", "Survival Overlay / Chi-square", "6.7", "cluster_survival_overlay.png"),
    ("19", "RF Setup & Tuning", "7.1–7.2", "GridSearchCV, baseline 68.18%"),
    ("20", "RF Test Performance", "7.3", "confusion_matrix.png, classification_report.png"),
    ("21", "ROC Curve", "7.3", "roc_curve.png"),
    ("22", "Feature Importance", "7.4", "feature_importance.png"),
    ("23", "Performance Context", "7.3 audit", "Overfitting, CV F1 vs macro F1"),
    ("24", "Synthesis Comparison", "8.1", "synthesis_comparison.png"),
    ("25", "Predicted Probability per Cluster", "8.2", "Bridge table"),
    ("26", "Clinical Narrative", "8.3", "Convergence paragraph"),
    ("27", "Limitations", "8.4", "10 numbered items"),
    ("28", "Future Work", "8.5", "10 numbered items"),
    ("29", "Conclusion", "9", "Dynamic metrics recap"),
    ("30", "Thank You / Q&A", "—", "Appendix slides A1–A9 for backup"),
]

# ---------------------------------------------------------------------------
# PART 3 — Section walkthroughs (9 sections)
# ---------------------------------------------------------------------------
SECTION_WALKTHROUGHS = {
    "1": {
        "title": "Section 1: Project Setup and Imports",
        "summary": (
            "Establishes the Python environment, imports all libraries, sets RANDOM_STATE=42 for "
            "reproducibility, configures matplotlib/seaborn defaults, and creates the figures/ directory."
        ),
        "functions": [
            "import pandas as pd, numpy as np, matplotlib.pyplot, seaborn as sns",
            "from sklearn.ensemble import RandomForestClassifier",
            "from sklearn.cluster import KMeans",
            "from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold",
            "from sklearn.preprocessing import StandardScaler",
            "from sklearn.decomposition import PCA",
            "from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score, confusion_matrix, ...)",
            "from scipy.stats import chi2_contingency, normaltest",
            "from statsmodels.stats.outliers_influence import variance_inflation_factor",
            "warnings.filterwarnings('ignore')",
            "os.makedirs('figures', exist_ok=True)",
        ],
        "parameters": [
            "RANDOM_STATE = 42 — all splits, models, CV, PCA, K-Means use this seed",
            "OPTIMAL_K = 3 — documented before clustering for reproducibility",
            "plt.style.use('seaborn-v0_8-whitegrid') — readable grid backgrounds",
            "sns.set_palette('colorblind') — accessible colors",
            "savefig dpi=300, bbox_inches='tight' — publication-quality exports",
        ],
        "outputs": ["figures/ directory", "Configured plotting defaults", "All imports verified"],
        "decisions_did": [
            "Import SMOTE (imblearn) but document as rejected alternative",
            "Suppress warnings for cleaner notebook output",
            "Fix seed before any stochastic operation",
        ],
        "decisions_did_not": [
            "Did not set different seeds per model — single seed for fair comparison",
            "Did not use TensorFlow/PyTorch — outside course scope",
        ],
        "interpretation": (
            "Foundation for reproducible analysis. Every downstream result can be recreated with "
            "Restart & Run All. The import list defines the complete methodological toolkit."
        ),
        "professor_questions": [
            "Why random_state=42 specifically? — Convention; any fixed seed works; 42 ensures identical reruns.",
            "Why import SMOTE if not used? — Documents considered alternative; rejected in favor of class_weight.",
            "What happens if figures/ doesn't exist? — os.makedirs creates it before first savefig.",
        ],
    },
    "2": {
        "title": "Section 2: Data Loading and Initial Inspection",
        "summary": (
            "Loads the PCSPF Excel file (878×24), inspects structure, drops ID and Predict label columns, "
            "renames target to survival_label, and documents pre-standardized continuous features."
        ),
        "functions": [
            "pd.read_excel('Dataset/PCSPF-Pancreatic Cancer Survival based on Preoperative Features.xlsx')",
            "df.shape, df.columns, df.dtypes, df.head(), df.tail()",
            "df.isnull().sum()",
            "df.duplicated().sum()",
            "df['survival_label'].value_counts()",
            "df.drop(columns=DROP_COLS, inplace=True)",
            "df.rename(columns={'Survival label': 'survival_label'})",
            "df.describe().T",
        ],
        "parameters": [
            "DROP_COLS = ['ID', 'Predict label 1', 'Predict label 0']",
            "Expected final shape: (878, 21) = 20 features + target",
        ],
        "outputs": [
            "Clean DataFrame 878×21",
            "Class distribution table: 604/274",
            "Structural audit printed to notebook",
        ],
        "decisions_did": [
            "Drop Predict columns (100% NaN)",
            "Drop ID (all 'xxx' — no analytic value)",
            "Rename target for code clarity",
            "Document z-score scale in released file",
        ],
        "decisions_did_not": [
            "Did not impute Predict columns",
            "Did not encode ID as feature",
        ],
        "interpretation": (
            "878 patients with complete preoperative features and binary 1-year survival outcome. "
            "Moderate imbalance (68.8% vs 31.2%) sets the evaluation framework."
        ),
        "professor_questions": [
            "Why 24 → 21 columns? — Removed 3 unusable columns; 20 predictors + 1 target remain.",
            "What is survival_label? — 1 = survived ≥1 year; 0 = died within 1 year.",
            "Are features raw lab values? — Released file uses z-scores for 18 continuous features.",
        ],
    },
    "3": {
        "title": "Section 3: Exploratory Data Analysis (EDA)",
        "summary": (
            "Characterizes feature distributions, class imbalance, correlations, and survival-group "
            "differences through summary statistics and five figure groups before any modeling."
        ),
        "functions": [
            "df.describe().T",
            "value_counts(), bar plot → target_distribution.png",
            "sns.histplot + kde → feature_distributions.png",
            "sns.boxplot by survival_label → boxplots_by_survival.png",
            "df.corr(), sns.heatmap → correlation_heatmap.png",
            "groupby('survival_label').mean(), bar chart → class_conditional_means.png",
        ],
        "parameters": [
            "Pearson correlation — standard for continuous features",
            "Upper triangle masked in heatmap — avoid duplicate pairs",
            "30 histogram bins — balance detail and noise",
            "colorblind palette — accessibility",
        ],
        "outputs": [
            "target_distribution.png", "feature_distributions.png", "boxplots_by_survival.png",
            "correlation_heatmap.png", "class_conditional_means.png", "EDA summary markdown",
        ],
        "decisions_did": [
            "Visualize all 18 continuous features",
            "Report all feature-target correlations (all |r| < 0.15)",
            "Document multicollinearity among ratio features",
        ],
        "decisions_did_not": [
            "Did not perform statistical tests on every feature-target pair — scope",
            "Did not drop correlated features at EDA stage",
        ],
        "interpretation": (
            "Weak univariate signal and strong inter-feature correlation. Right-skewed tumor/inflammation "
            "markers. Modest class-conditional differences on CA19-9, Prealbumin, Abdominal Pain. "
            "Multivariate nonlinear models warranted."
        ),
        "professor_questions": [
            "Strongest correlate with survival? — All |r| < 0.15; Abdominal Pain among largest mean diffs.",
            "Why Pearson not Spearman? — Pearson standard for z-scored continuous; rank correlation similar here.",
            "Does EDA prove RF will work? — No; it sets realistic expectations for modest AUC.",
        ],
    },
    "4": {
        "title": "Section 4: Data Preprocessing",
        "summary": (
            "Documents every preprocessing decision including deliberate non-actions: types, nulls, "
            "duplicates, outliers, normality, VIF, feature engineering, selection, and class imbalance."
        ),
        "functions": [
            "df.dtypes, df.nunique()",
            "df.isnull().sum() — triple verification",
            "df.duplicated().sum()",
            "IQR outlier counts per feature",
            "z-score boxplots → outlier_boxplots.png",
            "scipy.stats.normaltest per feature",
            "skew(), kurtosis()",
            "variance_inflation_factor from statsmodels",
            "matplotlib table → preprocessing_summary.png",
        ],
        "parameters": [
            "IQR rule: Q1 - 1.5×IQR, Q3 + 1.5×IQR",
            "normaltest alpha = 0.05 — reject normality if p < 0.05",
            "VIF threshold reference: >10 suggests multicollinearity (not used to drop)",
            "class_weight='balanced' — auto-computed weights ~1.60 / ~0.73",
        ],
        "outputs": [
            "outlier_boxplots.png", "preprocessing_summary.png",
            "Skewness/normality table", "VIF table for all 20 features",
        ],
        "decisions_did": [
            "Retain all outliers (clinical extremes)",
            "Retain all 20 features despite high VIF on ratios",
            "Use class_weight not SMOTE",
            "No Yeo-Johnson or log transform",
        ],
        "decisions_did_not": [
            "No imputation", "No SMOTE", "No feature dropping", "No outlier removal",
        ],
        "interpretation": (
            "Data quality is high (zero nulls, zero duplicates). Non-normal distributions documented "
            "but not corrected for RF. Multicollinearity acknowledged but retained for clinical validity."
        ),
        "professor_questions": [
            "Why not drop NLR when VIF is high? — RF handles collinearity; NLR is clinically standard.",
            "Why D'Agostino-Pearson not Shapiro-Wilk? — n=878 too large for Shapiro assumptions.",
            "Four reasons to keep outliers? — Clinical severity, not errors; removal biases sample.",
        ],
    },
    "5": {
        "title": "Section 5: Train-Test Split and Scaling",
        "summary": (
            "Separates X (878×20) and y, performs 80/20 stratified split (702/176), and applies "
            "StandardScaler to full X for K-Means only — RF uses unscaled train/test data."
        ),
        "functions": [
            "X = df.drop('survival_label', axis=1); y = df['survival_label']",
            "train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)",
            "StandardScaler().fit_transform(X) → X_scaled",
            "Boxplot comparison → scaling_before_after.png",
        ],
        "parameters": [
            "test_size=0.2 — 176 holdout patients",
            "stratify=y — preserves 68.8/31.2 ratio in train and test",
            "random_state=42 — reproducible split",
            "Scaler fit on full X (878) — unsupervised; no y used",
        ],
        "outputs": [
            "X_train (702×20), X_test (176×20), y_train, y_test",
            "X_scaled (878×20)", "scaling_before_after.png",
        ],
        "decisions_did": [
            "Stratified split for imbalanced target",
            "Scale only for K-Means pipeline",
            "Keep RF on original scale",
        ],
        "decisions_did_not": [
            "Did not scale before split for RF",
            "Did not use survival label in scaler",
        ],
        "interpretation": (
            "702 patients for training, 176 unseen for final RF evaluation. Class proportions preserved. "
            "Scaling ensures fair Euclidean distances in K-Means without affecting tree-based RF."
        ),
        "professor_questions": [
            "Is scaler fit on full data leakage? — For unsupervised K-Means on all patients: acceptable; "
            "RF never sees scaled data and uses train-only fit for prediction.",
            "Why 80/20 not 70/30? — Standard split; 176 test samples adequate for course scope.",
            "Train class counts? — ~483 class 1, ~219 class 0 (stratified from 604/274).",
        ],
    },
    "6": {
        "title": "Section 6: Unsupervised Learning — K-Means Clustering",
        "summary": (
            "Benchmarks K-Means vs GMM/Ward/DBSCAN, selects k=3 via elbow/silhouette/clinical reasoning, "
            "profiles clusters, and tests survival association post-hoc with chi-square and Cramér's V."
        ),
        "functions": [
            "KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(X_scaled)",
            "GaussianMixture, AgglomerativeClustering, DBSCAN — comparison",
            "inertia_ for elbow → elbow_method.png",
            "silhouette_score(X_scaled, labels) → silhouette_scores.png",
            "PCA(n_components=2).fit_transform(X_scaled) → pca_clusters.png",
            "groupby('cluster').mean(), heatmap → cluster_profiles_heatmap.png",
            "chi2_contingency(crosstab), Cramér's V → cluster_survival_overlay.png",
            "PCA colored by survival → pca_survival_labels.png",
        ],
        "parameters": [
            "k range 2–10 for elbow/silhouette",
            "n_init=10 — 10 random starts, keep best inertia",
            "OPTIMAL_K=3 — clinical granularity over k=2 silhouette peak",
            "PCA n_components=2 — visualization only",
        ],
        "outputs": [
            "unsupervised_model_comparison.png", "elbow_method.png", "silhouette_scores.png",
            "pca_clusters.png", "cluster_profiles_heatmap.png", "cluster_survival_overlay.png",
            "pca_survival_labels.png", "Cluster labels in df['cluster']",
        ],
        "decisions_did": [
            "Compare 4 clustering algorithms before selecting K-Means",
            "Choose k=3 despite k=2 max silhouette",
            "Overlay survival only after clustering (no target leakage)",
            "Report chi-square AND Cramér's V",
        ],
        "decisions_did_not": [
            "Did not cluster on unscaled data",
            "Did not use survival in fit_predict",
            "Did not claim significant cluster-survival association",
        ],
        "interpretation": (
            "Three clinically interpretable phenotypes emerge. Cluster 2 has directionally lowest survival "
            "(63.2%) but chi-square p=0.2546 — not significant. Weak preoperative signal limits all "
            "clustering methods equally."
        ),
        "professor_questions": [
            "Why K-Means over DBSCAN? — DBSCAN assigns only ~49%; K-Means gives 100% assignment + centroids.",
            "Why k=3 not k=2? — Three clinical phenotypes; k=2 max silhouette (~0.206) but less granular.",
            "Was survival used in clustering? — No; only post-hoc chi-square test.",
        ],
    },
    "7": {
        "title": "Section 7: Supervised Learning — Random Forest Classifier",
        "summary": (
            "Justifies RF, trains baseline (68.18%), compares three GridSearch objectives (f1 legacy, f1_macro primary, "
            "recall_macro stretch), threshold sweep, full metric suite, regularization comparison, and 4-model benchmark."
        ),
        "functions": [
            "RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)",
            "GridSearchCV(RF, param_grid, cv=StratifiedKFold(5), scoring='f1_macro')",
            "GridSearchCV comparison: f1 (legacy grid), f1_macro, recall_macro",
            "Threshold sweep on predict_proba (exploratory)",
            "accuracy_score, f1_score, roc_auc_score, confusion_matrix, classification_report",
            "roc_curve, auc -> roc_curve.png",
            "sns.heatmap(confusion_matrix) -> confusion_matrix.png",
            "feature_importances_ -> feature_importance.png",
            "LR, SVC(RBF), GradientBoostingClassifier — comparison",
        ],
        "parameters": [
            "Legacy grid: 108 combos, scoring='f1' (reference row)",
            "Regularized grid: 135 combos, scoring='f1_macro' (primary) and recall_macro (stretch)",
            "Best primary: 100 trees, depth 5, leaf 4, split 10",
            "class_weight='balanced' on all classifiers",
        ],
        "outputs": [
            "confusion_matrix.png", "roc_curve.png", "classification_report.png",
            "feature_importance.png", "supervised_model_comparison.png",
            "Tuned model rf_tuned, metrics tables, overfitting analysis",
        ],
        "decisions_did": [
            "Compare f1, f1_macro, and recall_macro tuning objectives",
            "Adopt f1_macro winner as primary rf_tuned",
            "Exploratory threshold sweep on test probabilities",
            "Document 85.8% train vs 61.9% test overfitting (vs 100%/71% legacy)",
            "Compare regularized RF configs including legacy f1 winner",
            "Benchmark LR, SVM, GB on same split",
            "Retain RF despite SVM winning some metrics — Gini importance for synthesis",
        ],
        "decisions_did_not": [
            "Did not use SMOTE", "Did not scale RF inputs",
            "Did not switch to SVM as primary — loses built-in importance",
        ],
        "interpretation": (
            "Primary f1_macro tuned RF: 61.93% test accuracy, macro F1 0.550, AUC 0.563, class-0 recall 36.4% (20/55). "
            "Legacy f1 tuning retained as reference (71.02% acc, 0.507 macro F1, 10.9% recall). "
            "Top features: CA19-9, CEA, Prealbumin, CRP/ALB, BMI."
        ),
        "professor_questions": [
            "Why RF over SVM if SVM has higher macro F1? — Gini importance required for Section 8 synthesis.",
            "Why retune with f1_macro if accuracy drops below baseline? — Macro F1 and class-0 recall align with evaluation goals under imbalance.",
            "Why 85.8% train accuracy? — Regularized f1_macro grid reduces memorization vs legacy depth=15 model (100% train).",
        ],
    },
    "8": {
        "title": "Section 8: Synthesis and Bridging Analysis",
        "summary": (
            "Compares RF Gini importance vs cluster-differentiation rankings, bridges predicted "
            "probabilities by cluster, writes clinical narrative, and lists limitations and future work."
        ),
        "functions": [
            "rf_tuned.feature_importances_",
            "cluster mean range ranking",
            "Side-by-side bar chart → synthesis_comparison.png",
            "rf_tuned.predict_proba(X) grouped by cluster",
            "Dynamic markdown f-strings for narrative",
        ],
        "parameters": [
            "Top 10 features from each analysis compared",
            "predict_proba on full X for cluster bridge table",
        ],
        "outputs": [
            "synthesis_comparison.png", "Probability bridge table",
            "Clinical synthesis paragraph", "10 limitations", "10 future work items",
        ],
        "decisions_did": [
            "Rank convergence explicitly",
            "Report mean predicted vs actual survival per cluster",
            "Number limitations and future work (≥8 each)",
        ],
        "decisions_did_not": [
            "Did not merge cluster labels into RF features",
            "Did not claim clinical deployability",
        ],
        "interpretation": (
            "Supervised and unsupervised analyses converge on CEA, Prealbumin, CA19-9, and inflammatory "
            "markers — mutual validation of limited preoperative signal. Cluster 2 lowest survival aligns "
            "with high-inflammation profile."
        ),
        "professor_questions": [
            "What is the synthesis contribution? — Independent methods pointing same direction strengthens biomarker story.",
            "Does convergence mean good prediction? — No; means consistent weak signal, not strong performance.",
            "Top limitation you'd emphasize? — Missing staging/treatment; labs alone insufficient.",
        ],
    },
    "9": {
        "title": "Section 9: Conclusion",
        "summary": (
            "Dynamic four-paragraph recap using runtime variables (tuned_acc, auc, macro_f1, cluster "
            "survival rates, chi-square p) so conclusion always matches latest notebook execution."
        ),
        "functions": [
            "f-string markdown with {tuned_acc:.2f}, {auc:.3f}, {macro_f1:.3f}, {p:.4f}",
            "KEY RESULTS summary block",
        ],
        "parameters": ["All metrics pulled from executed variables — not hard-coded stale values"],
        "outputs": ["Rendered conclusion markdown", "KEY RESULTS block"],
        "decisions_did": ["Auto-fill metrics from runtime", "Restate core finding in one sentence"],
        "decisions_did_not": ["Did not overclaim clinical utility"],
        "interpretation": CORE_FINDING,
        "professor_questions": [
            "Summarize in one sentence? — " + CORE_FINDING,
            "What would you do differently? — Add staging, external validation, SHAP, nested CV.",
            "Main takeaway for clinicians? — Preoperative labs alone have limited prognostic value.",
        ],
    },
}

# ---------------------------------------------------------------------------
# PART 5 — Function reference (by section)
# ---------------------------------------------------------------------------
FUNCTION_REFERENCE = {
    "Section 1 — Setup": [
        ("warnings.filterwarnings", "built-in", "Suppress non-critical warnings", "N/A", "Cleaner output"),
        ("os.makedirs", "os", "Create figures/ if missing", "exist_ok=True", "Directory path"),
        ("plt.style.use", "matplotlib", "Set global plot style", "seaborn-v0_8-whitegrid", "None"),
        ("sns.set_palette", "seaborn", "Colorblind-friendly colors", "'colorblind'", "None"),
    ],
    "Section 2 — Loading": [
        ("pd.read_excel", "pandas", "Load Excel workbook into DataFrame", "path to .xlsx", "DataFrame 878×24"),
        ("df.drop", "pandas", "Remove ID and Predict columns", "columns=DROP_COLS", "DataFrame 878×21"),
        ("df.rename", "pandas", "Rename target column", "columns dict", "DataFrame with survival_label"),
        ("value_counts", "pandas Series", "Count class frequencies", "N/A", "Series with counts"),
        ("df.describe", "pandas", "Summary statistics", ".T transpose", "Stats table"),
    ],
    "Section 3 — EDA": [
        ("df.corr", "pandas", "Pearson correlation matrix", "method='pearson' default", "20×20 matrix"),
        ("sns.heatmap", "seaborn", "Correlation visualization", "mask upper triangle", "Heatmap figure"),
        ("sns.histplot", "seaborn", "Histogram + optional KDE", "bins=30, kde=True", "Distribution plot"),
        ("sns.boxplot", "seaborn", "Compare feature by survival class", "x=survival_label", "Boxplot figure"),
        ("groupby().mean()", "pandas", "Class-conditional means", "by survival_label", "Mean table"),
    ],
    "Section 4 — Preprocessing": [
        ("df.isnull().sum()", "pandas", "Count missing per column", "N/A", "Series of counts"),
        ("df.duplicated().sum()", "pandas", "Count duplicate rows", "N/A", "Integer count"),
        ("scipy.stats.normaltest", "scipy", "D'Agostino-Pearson normality test", "per feature array", "statistic, p-value"),
        ("variance_inflation_factor", "statsmodels", "VIF for multicollinearity", "exog matrix", "VIF float per feature"),
    ],
    "Section 5 — Split & Scale": [
        ("train_test_split", "sklearn.model_selection", "Split into train/test sets",
         "X, y, test_size=0.2, stratify=y, random_state=42",
         "X_train, X_test, y_train, y_test (702/176)"),
        ("StandardScaler", "sklearn.preprocessing", "Z-score normalize features", "with_mean=True, with_std=True",
         "Scaler object; fit_transform → X_scaled"),
        ("scaler.fit_transform(X)", "sklearn", "Learn mean/std on X, transform", "full 878×20",
         "X_scaled array"),
    ],
    "Section 6 — K-Means": [
        ("KMeans", "sklearn.cluster", "Partition data into k clusters", "n_clusters=3, n_init=10, random_state=42",
         "KMeans object; labels via fit_predict"),
        ("inertia_", "KMeans attribute", "Within-cluster sum of squared distances", "N/A", "Float — lower = tighter"),
        ("silhouette_score", "sklearn.metrics", "Cluster quality -1 to 1", "X_scaled, labels", "Float score"),
        ("PCA", "sklearn.decomposition", "Linear dimensionality reduction", "n_components=2",
         "2D projection; explained_variance_ratio_"),
        ("chi2_contingency", "scipy.stats", "Test cluster vs survival independence", "crosstab array",
         "chi2, p-value, dof, expected"),
    ],
    "Section 7 — Random Forest": [
        ("RandomForestClassifier", "sklearn.ensemble", "Ensemble of decision trees",
         "n_estimators, max_depth, class_weight='balanced', random_state=42", "Trained classifier"),
        ("GridSearchCV", "sklearn.model_selection", "Exhaustive hyperparameter search with CV",
         "estimator, param_grid, cv=5, scoring='f1'", "best_estimator_, best_params_, cv_results_"),
        ("StratifiedKFold", "sklearn.model_selection", "CV preserving class ratio", "n_splits=5, shuffle=True, random_state=42",
         "5 train/val folds"),
        ("accuracy_score", "sklearn.metrics", "Fraction correct", "y_true, y_pred", "Float 0–1"),
        ("f1_score", "sklearn.metrics", "Harmonic mean precision/recall", "average='macro' or 'binary'",
         "Float 0–1"),
        ("roc_auc_score", "sklearn.metrics", "Area under ROC curve", "y_true, y_proba[:,1]", "Float 0–1"),
        ("confusion_matrix", "sklearn.metrics", "TP/TN/FP/FN table", "y_true, y_pred", "2×2 array"),
        ("classification_report", "sklearn.metrics", "Per-class precision/recall/F1", "y_true, y_pred", "Text report"),
        ("roc_curve", "sklearn.metrics", "FPR/TPR at thresholds", "y_true, y_scores", "fpr, tpr, thresholds"),
        ("feature_importances_", "RF attribute", "Gini importance per feature", "N/A", "Array length 20"),
    ],
    "Section 8 — Synthesis": [
        ("predict_proba", "classifier method", "Class probabilities per patient", "X", "n×2 array"),
        ("groupby('cluster')", "pandas", "Aggregate by cluster", "mean, count", "Bridge table"),
    ],
}

# ---------------------------------------------------------------------------
# PART 6 — Technique deep dives
# ---------------------------------------------------------------------------
TECHNIQUE_DEEP_DIVES = {
    "Random Forest": (
        "How it works: Bootstrap samples (bagging) train each tree; at each split a random subset of "
        "features is considered; trees vote for classification. Gini impurity measures node purity — "
        "splits minimize weighted Gini. Feature importance = mean decrease in Gini across splits using "
        "that feature. class_weight='balanced' sets weight_c = n / (n_classes × count_c) — class 0 "
        "~1.60, class 1 ~0.73. max_depth=15 allows deep trees (overfitting); min_samples_leaf=1 allows "
        "single-sample leaves. Trees do NOT need scaling because splits are rank-based on individual features."
    ),
    "K-Means": (
        "How it works: Initialize k centroids → assign each point to nearest centroid (Euclidean distance) "
        "→ update centroids to cluster means → repeat until convergence. Inertia = within-cluster sum of "
        "squared distances (elbow method tracks this vs k). Silhouette = (b-a)/max(a,b) where a = intra-cluster "
        "distance, b = nearest-cluster distance — range [-1,1]; higher = better separation. Requires scaling "
        "because features on different scales dominate distance. Elbow shows diminishing inertia reduction; "
        "k=2 has max silhouette (~0.206) but k=3 chosen for three clinical phenotypes (~0.133 silhouette)."
    ),
    "StandardScaler": (
        "Z-score: z = (x - mean) / std → mean 0, variance 1 per feature. Critical for K-Means Euclidean "
        "distance so CEA and BMI contribute comparably. Irrelevant for RF tree splits which compare "
        "within-feature thresholds only."
    ),
    "PCA": (
        "Reduces 20D → 2D for visualization by projecting onto orthogonal axes of maximum variance. "
        "explained_variance_ratio_ gives fraction per component — PC1=20.3%, PC2=10.5%, cumulative=30.8%. "
        "Low cumulative variance means 2D plots hide 69.2% of structure — used ONLY for visualization, "
        "NOT for clustering or classification."
    ),
    "GridSearchCV": (
        "Exhaustive search over 108 hyperparameter combinations. StratifiedKFold(n=5) creates 5 train/val "
        "splits preserving class ratio. scoring='f1' optimizes binary F1 on positive class (class 1) — "
        "explains CV ~0.809 vs test macro F1 0.507. CV F1 measures validation-fold performance averaged "
        "over 5 folds; NOT the same as test set macro F1."
    ),
    "Chi-square test": (
        "Tests independence of two categorical variables (cluster × survival). p-value = probability of "
        "observed table if variables independent. p=0.2546 > 0.05 → fail to reject independence. Cramér's V "
        "adds effect size: V ≈ 0.056 on 0–1 scale — negligible regardless of sample size."
    ),
    "D'Agostino-Pearson": (
        "Tests whether distribution is normal using skewness and kurtosis combined. Chosen over Shapiro-Wilk "
        "because n=878 exceeds Shapiro's reliable range. Most features p < 0.05 → reject normality."
    ),
    "VIF": (
        "Variance Inflation Factor measures how much variance of a coefficient estimate increases due to "
        "collinearity. VIF > 10 conventionally indicates problematic multicollinearity. NLR, PLR, SII, "
        "CRP/ALB show elevated VIF because they are ratios of correlated components — retained because "
        "RF handles collinearity and they are clinically validated indices."
    ),
}

# ---------------------------------------------------------------------------
# PART 7 — Why decision map
# ---------------------------------------------------------------------------
WHY_DID = [
    ("Random Forest (supervised)", [
        "All feature-target |r| < 0.15 — need nonlinear interaction capture",
        "Built-in Gini importance for Section 8 synthesis",
        "Robust to multicollinearity via random feature subsets",
        "No scaling needed — clean pipeline separation from K-Means",
        "Course-appropriate ensemble method for defense",
    ]),
    ("K-Means (unsupervised)", [
        "Highest silhouette among partition methods at k=3",
        "100% patient assignment vs DBSCAN ~49%",
        "Interpretable centroids for clinical profiling",
        "Simple, well-understood algorithm for course scope",
        "Three balanced clusters for phenotype narrative",
    ]),
    ("class_weight='balanced'", [
        "Adjusts for 2.2:1 imbalance without synthetic data",
        "Clinically defensible — real patients only",
        "Improves minority class consideration in splits",
        "Standard sklearn parameter",
    ]),
    ("Stratified 80/20 split", [
        "Preserves class proportions in train and test",
        "176 test patients for holdout evaluation",
        "random_state=42 for reproducibility",
    ]),
    ("Retain all outliers", [
        "Extreme labs indicate severe disease",
        "Not data entry errors",
        "Removal would bias toward healthier patients",
        "RF and K-Means can handle extremes",
    ]),
]

WHY_DID_NOT = [
    ("No outlier removal", [
        "Clinical extremes are informative, not noise",
        "Would lose 5–10% of sickest patients",
        "IQR rule is descriptive, not prescriptive here",
        "Outlier removal did not improve defensibility",
    ]),
    ("No Yeo-Johnson transform", [
        "RF splits are rank-invariant",
        "StandardScaler sufficient for K-Means",
        "Transform would obscure clinical interpretability",
    ]),
    ("No SMOTE", [
        "Synthetic minority samples hard to defend clinically",
        "class_weight achieves similar goal",
        "SMOTE can create unrealistic feature combinations",
    ]),
    ("No feature dropping (VIF)", [
        "Ratio features clinically validated (NLR, PLR, SII)",
        "RF handles multicollinearity",
        "Arbitrary VIF>10 threshold would lose information",
    ]),
    ("No scaling for RF", [
        "Tree splits invariant to monotonic scaling",
        "Keeps RF pipeline distinct from K-Means",
    ]),
    ("No Shapiro-Wilk", [
        "n=878 too large — Shapiro loses power interpretation",
        "D'Agostino-Pearson appropriate for this sample size",
    ]),
]

WHY_NOT_DIFFERENT_MODEL = [
    ("RF over Logistic Regression", "LR macro F1 ~0.55 vs RF 0.507; LR better balanced metrics but no Gini importance; linear assumption weak given |r|<0.15."),
    ("RF over SVM RBF", "SVM best macro F1 (0.590) and AUC (0.622) but no built-in importance — synthesis impossible without SHAP."),
    ("RF over XGBoost", "Not in course scope; GB benchmark ~0.51 macro F1 similar to RF; RF simpler to defend."),
    ("RF over single Decision Tree", "Single tree high variance; RF bagging reduces variance; course requires ensemble."),
    ("K-Means over DBSCAN", "DBSCAN p<0.01 but only ~49% assigned; noise labels unusable for full cohort profiling."),
    ("K-Means over GMM", "GMM lower silhouette at k=3; soft assignment adds complexity without survival benefit."),
    ("K-Means over Agglomerative Ward", "Ward chi-sq p~0.65 (worse); no centroids; similar survival spread."),
]
