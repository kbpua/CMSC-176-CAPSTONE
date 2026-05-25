# -*- coding: utf-8 -*-
"""Figure guide entries with statistical + clinical interpretation for the study guide PDF."""

FIGURE_GUIDE = [
    {
        "num": 1, "file": "target_distribution.png", "section": "3.2",
        "shows": "Bar chart of survival_label: Class 1 = survived >=1 year (604, 68.8%); Class 0 = died within 1 year (274, 31.2%).",
        "interpretation": "Moderate class imbalance (2.20:1). A majority-class classifier predicting 'survived' for everyone scores 68.8% accuracy without learning anything.",
        "clinical_interpretation": (
            "In this cohort, roughly 7 in 10 pancreatic cancer patients survived at least one year after surgery, "
            "while about 3 in 10 did not. That reflects both the severity of pancreatic cancer and the fact that "
            "surgical candidates are often selected patients - not the general population incidence of early mortality."
        ),
        "implications": "Requires class_weight='balanced', macro F1, and AUC - not accuracy alone.",
        "clinical_implication": (
            "For defense: tell the panel that any model must do more than 'predict everyone survives.' "
            "The clinically important group is Class 0 - patients who die within a year - because catching them "
            "earlier affects palliative planning, family counseling, and resource allocation."
        ),
        "point_out": "2.20:1 ratio; majority baseline = 68.8%.",
        "dont_claim": "Do not call this 'severe' imbalance - it is moderate (2.2:1).",
    },
    {
        "num": 2, "file": "feature_distributions.png", "section": "3.3",
        "shows": "4x5 grid of histograms + KDE for 18 continuous preoperative features.",
        "interpretation": "Right-skewed distributions on CA19-9, CRP, CEA, and bilirubin. Released file values are already z-scored (mean~0, std>=1).",
        "clinical_interpretation": (
            "Most tumor markers and inflammation labs have long right tails - a few patients with very high CA19-9, "
            "CRP, or bilirubin. Clinically, those extremes often reflect advanced obstructive jaundice, heavy "
            "tumor burden, or systemic inflammation rather than 'bad data points.'"
        ),
        "implications": "Non-normality documented; no transform applied (RF rank-invariant; scaler for K-Means).",
        "clinical_implication": (
            "When defending outlier retention (Section 4), point back to this figure: the sickest patients "
            "drive the tails. Removing them would silently drop the highest-risk cases from both clustering and prediction."
        ),
        "point_out": "Right skew on tumor markers and inflammation indices.",
        "dont_claim": "Do not claim distributions are raw clinical units - file is pre-standardized.",
    },
    {
        "num": 3, "file": "boxplots_by_survival.png", "section": "3.4",
        "shows": "Boxplots of each continuous feature split by survival outcome (Class 0 vs Class 1).",
        "interpretation": "Modest separation on CA19-9, prealbumin, and inflammatory markers. Heavy overlap between outcome groups for most features.",
        "clinical_interpretation": (
            "Patients who died within one year tend to show slightly higher CA19-9, lower prealbumin, and more "
            "abnormal inflammatory indices - patterns oncologists expect in malnourished, high-burden disease. "
            "However, the boxplots overlap heavily, meaning no single lab cleanly separates survivors from non-survivors."
        ),
        "implications": "Weak univariate signal ? need multivariate models (RF) that combine labs, not one threshold.",
        "clinical_implication": (
            "This figure supports your core finding: preoperative labs alone cannot replace staging or pathology. "
            "They carry a real but limited signal - enough to motivate modeling, not enough for standalone triage."
        ),
        "point_out": "Separation exists but overlap dominates - no single biomarker threshold works.",
        "dont_claim": "Do not claim any single boxplot proves predictive power.",
    },
    {
        "num": 4, "file": "correlation_heatmap.png", "section": "3.5",
        "shows": "Lower-triangle Pearson correlation matrix (20 features + survival_label).",
        "interpretation": "All feature-target |r| < 0.15. Strong red blocks among NLR, PLR, SII, CRP/ALB, and bilirubin pairs.",
        "clinical_interpretation": (
            "No single preoperative lab linearly predicts 1-year survival strongly - survival is influenced by many "
            "factors acting together (tumor biology, nutrition, inflammation, biliary obstruction). The tight "
            "correlation blocks among NLR, PLR, SII, and CRP/ALB reflect one underlying clinical story: systemic "
            "inflammatory response in advanced disease."
        ),
        "implications": "Justifies Random Forest over logistic regression; explains high VIF; sets modest AUC expectation.",
        "clinical_implication": (
            "Tell the panel: we did not expect one 'magic number' like CA19-9 alone to predict survival. "
            "Pancreatic cancer prognosis depends on combinations - which is why we chose a model that learns "
            "interactions between tumor markers, nutrition (prealbumin), and inflammation indices."
        ),
        "point_out": "Target correlations all weak; ratio features correlate with their components.",
        "dont_claim": "Do not say 'no relationship' - weak linear, possible nonlinear interactions.",
    },
    {
        "num": 5, "file": "class_conditional_means.png", "section": "3.7",
        "shows": "Horizontal bar chart of top 10 mean differences between survival classes.",
        "interpretation": "Largest gaps: Abdominal Pain, CA19-9, Prealbumin, inflammatory markers. Differences are visible but modest.",
        "clinical_interpretation": (
            "Patients who died within a year reported more abdominal pain and had higher CA19-9 with lower prealbumin - "
            "a pattern consistent with symptomatic, nutritionally depleted, higher-burden disease at presentation. "
            "These are clinically recognizable risk signals even though none dominates alone."
        ),
        "implications": "Foreshadows top RF features and cluster profiles; reinforces weak-signal theme.",
        "clinical_implication": (
            "Use this slide to connect EDA to later results: Abdominal Pain and CA19-9 reappear in cluster profiles "
            "and RF importance. The same patient profile - symptomatic, inflamed, malnourished - shows up across analyses."
        ),
        "point_out": "Abdominal Pain and CA19-9 among largest univariate gaps.",
        "dont_claim": "Do not rank these as final 'most important predictors' - RF importance differs.",
    },
    {
        "num": 6, "file": "outlier_boxplots.png", "section": "4.4",
        "shows": "Per-feature z-score boxplots highlighting IQR outliers.",
        "interpretation": "Outliers concentrate on CA19-9, CRP, CEA, and bilirubin - extreme lab values, not data errors.",
        "clinical_interpretation": (
            "The flagged outliers are exactly the markers that spike in aggressive pancreatic cancer: markedly elevated "
            "CA19-9 or CEA, high CRP from inflammation, and bilirubin from biliary obstruction. These patients are "
            "often the most clinically complex - not statistical noise."
        ),
        "implications": "Supports retaining all outliers; removal would discard the sickest patients.",
        "clinical_implication": (
            "Defense line: 'We kept outliers because removing a CA19-9 of 1000 or bilirubin in obstructive jaundice "
            "would mean training on a healthier, easier subset.' That would inflate accuracy and misrepresent real preoperative practice."
        ),
        "point_out": "Outliers = clinical severity, not noise.",
        "dont_claim": "Do not say outliers were removed or winsorized.",
    },
    {
        "num": 7, "file": "preprocessing_summary.png", "section": "4.10",
        "shows": "Master table: Step -> Action -> Justification for all preprocessing decisions.",
        "interpretation": "Single audit anchor documenting every choice including deliberate non-actions (no SMOTE, no transform, retain outliers).",
        "clinical_interpretation": (
            "Every preprocessing row maps to a clinical reasoning decision: we kept real patient extremes, avoided "
            "synthetic data (SMOTE), and preserved validated indices like NLR and PLR that clinicians actually use "
            "in preoperative assessment."
        ),
        "implications": "Professor defense anchor slide - pause here; every row is defensible.",
        "clinical_implication": (
            "If the professor asks 'Why didn't you drop correlated features?' - open this table. The justification "
            "column ties each statistical choice to clinical validity, not just sklearn defaults."
        ),
        "point_out": "Includes SMOTE rejected, no transform, retain outliers.",
        "dont_claim": "Do not omit 'did not do' rows - they are intentional decisions.",
    },
    {
        "num": 8, "file": "scaling_before_after.png", "section": "5.3",
        "shows": "Side-by-side boxplots before/after StandardScaler on full X.",
        "interpretation": "Features already near z-score scale; StandardScaler enforces mean=0, std=1 for K-Means Euclidean distance. RF uses unscaled data.",
        "clinical_interpretation": (
            "Scaling puts all labs on equal footing for grouping patients - so BMI does not overpower CA19-9 just "
            "because of unit differences. Random Forest still uses the original scale because tree models compare "
            "each marker only to itself, the way clinicians read one lab against its own reference range."
        ),
        "implications": "Scaler on full 878 - 20 for K-Means only - NOT for RF train/test (anti-leakage).",
        "clinical_implication": (
            "Defense against leakage: 'Survival label never entered scaling or clustering. We only scaled inputs "
            "for distance-based grouping - the same preoperative profile a clinician sees before knowing the outcome.'"
        ),
        "point_out": "Anti-leakage: RF trained on unscaled X_train only.",
        "dont_claim": "Do not claim scaler was fit on train only for K-Means - it was fit on full X.",
    },
    {
        "num": 9, "file": "unsupervised_model_comparison.png", "section": "6.0",
        "shows": "Bar comparison: K-Means vs GMM vs Ward vs DBSCAN on silhouette, chi-sq p, survival spread.",
        "interpretation": "No method achieves significant cluster-survival association at k=3. K-Means: best silhouette, 100% assignment, interpretable centroids.",
        "clinical_interpretation": (
            "We tested whether another clustering algorithm would magically find strong prognostic groups - none did. "
            "That tells us the limitation is in preoperative data itself, not a wrong clustering button. K-Means still "
            "gives every patient a phenotype label and clear centroids for clinical description."
        ),
        "implications": "Algorithm choice is practical (interpretability + full assignment), not performance-driven.",
        "clinical_implication": (
            "If asked 'Why not DBSCAN with lower p-value?' - DBSCAN labels nearly half of patients as noise and "
            "cannot profile the full surgical cohort. K-Means lets us describe all 878 patients in three phenotypes."
        ),
        "point_out": "K-Means selected for silhouette + centroids + 100% assignment.",
        "dont_claim": "Do not claim DBSCAN 'won' because lower p - only ~49% assigned.",
    },
    {
        "num": 10, "file": "elbow_method.png", "section": "6.1",
        "shows": "Inertia vs k (2-10) with elbow region near k=2-4.",
        "interpretation": "Inertia decreases with k; diminishing returns after k~3. Elbow suggests 2-4 clusters are reasonable.",
        "clinical_interpretation": (
            "Adding more patient groups beyond three yields smaller clinical payoff - extra clusters split hairs without "
            "clear new phenotypes. The elbow near k=2-4 aligns with thinking in terms of low-, medium-, and high-risk "
            "preoperative profiles rather than many tiny subgroups."
        ),
        "implications": "Supports k=3 alongside silhouette analysis and clinical reasoning.",
        "clinical_implication": (
            "Defense: 'We did not pick k=3 arbitrarily - elbow and silhouette both point to 2-4 groups, and three "
            "maps to interpretable clinical phenotypes we can name and discuss with a surgeon or oncologist.'"
        ),
        "point_out": "Elbow is subjective - used with silhouette, not alone.",
        "dont_claim": "Do not claim elbow mathematically proves k=3.",
    },
    {
        "num": 11, "file": "silhouette_scores.png", "section": "6.2",
        "shows": "Mean silhouette score vs k (2-10). Max at k=2 (~0.206); k=3 (~0.133).",
        "interpretation": "Lower overall silhouette scores indicate overlapping patient groups in 20-dimensional lab space.",
        "clinical_interpretation": (
            "Patients do not fall into perfectly separated preoperative categories - real clinics see gradients of "
            "severity, not crisp bins. k=2 is statistically tightest but merges distinct clinical stories; k=3 "
            "separates stable, hepatobiliary-burden, and high-inflammation profiles worth naming separately."
        ),
        "implications": "k=3 chosen for clinical granularity over pure silhouette optimum.",
        "clinical_implication": (
            "Say openly: 'Silhouette favored two clusters, but we chose three because surgeons think in multiple "
            "phenotypes - jaundice-heavy vs inflammation-heavy vs relatively stable - even when boundaries blur.'"
        ),
        "point_out": "Trade-off: statistical optimum (k=2) vs clinical granularity (k=3).",
        "dont_claim": "Do not say silhouette 'proves' k=3 is optimal.",
    },
    {
        "num": 12, "file": "pca_clusters.png", "section": "6.5",
        "shows": "2D PCA scatter colored by K-Means cluster with centroids.",
        "interpretation": "Three partially separated groups. PC1+PC2 = 30.8% variance - 69.2% of structure not visible in 2D.",
        "clinical_interpretation": (
            "In two dimensions, three patient clouds appear with overlap - mirroring how preoperative risk is a "
            "spectrum, not discrete boxes. Clustering was done in full 20-feature space; this plot is a simplified "
            "map for presentation, like projecting a 3D tumor scan onto a slide."
        ),
        "implications": "Visualization only - clustering in full 20D scaled space, not PCA space.",
        "clinical_implication": (
            "If overlap looks 'messy,' explain: 'Most clinical information lives in dimensions we cannot draw - "
            "PC1 and PC2 capture less than one-third of lab variation. Overlap here does not mean clusters are meaningless.'"
        ),
        "point_out": "69.2% of variance invisible in this plot.",
        "dont_claim": "Do not say clusters are 'well separated' - silhouette is low.",
    },
    {
        "num": 13, "file": "cluster_profiles_heatmap.png", "section": "6.6",
        "shows": "Z-scored mean feature values per cluster (heatmap).",
        "interpretation": (
            "Cluster 0: lower inflammation, higher prealbumin - 'Stable/Low-Risk.' "
            "Cluster 1: elevated bilirubin, NLR, SII - 'Hepatobiliary Burden.' "
            "Cluster 2: highest CRP, CRP/ALB, abdominal pain - 'High-Inflammation.'"
        ),
        "clinical_interpretation": (
            "Cluster 0 looks like relatively well-nourished patients with less systemic inflammation - the profile "
            "you hope for before pancreatectomy. Cluster 1 resembles obstructive jaundice with elevated bilirubin "
            "and immune ratios. Cluster 2 is the sickest inflammatory phenotype: high CRP, high pain, high CRP/ALB - "
            "often the patient who already feels very unwell preoperatively."
        ),
        "implications": "Clinically coherent phenotypes for descriptive subgrouping - not standalone prognostic tools.",
        "clinical_implication": (
            "Spend defense time here: name the three phenotypes in plain language. Even without significant survival "
            "separation, these groups help clinicians think about who needs aggressive nutritional support, biliary "
            "drainage optimization, or inflammation monitoring before surgery."
        ),
        "point_out": "Three distinct clinical stories from preoperative labs alone.",
        "dont_claim": "Do not equate cluster label with guaranteed survival outcome.",
    },
    {
        "num": 14, "file": "cluster_survival_overlay.png", "section": "6.7",
        "shows": "Grouped bar chart: survival rates per cluster - 70.1%, 69.6%, 63.2%. Chi-square p=0.2546; Cram - r's V~0.056.",
        "interpretation": "Cluster 2 directionally lowest survival but association NOT statistically significant. Negligible effect size.",
        "clinical_interpretation": (
            "High-inflammation Cluster 2 shows about 7 percentage points lower 1-year survival than Clusters 0 and 1 "
            "(63.2% vs ~70%) - the direction clinicians would expect - but the gap is not statistically confirmed. "
            "Preoperative labs alone cannot reliably stratify prognosis the way TNM staging can."
        ),
        "implications": "Honest limitation: directional trend without conclusive proof - do not claim significance.",
        "clinical_implication": (
            "Own this result confidently: 'We report p=0.2546 because scientific honesty matters. The trend still "
            "supports our synthesis - sickest phenotype, lowest survival - but we would not use clusters alone for "
            "prognostic counseling without adding staging and treatment data.'"
        ),
        "point_out": "Own non-significance; directional narrative still valid.",
        "dont_claim": "Never say 'significant' or 'proves clusters predict survival'.",
    },
    {
        "num": 15, "file": "pca_survival_labels.png", "section": "6.8",
        "shows": "Same PCA projection colored by true survival_label (survived vs died <1 year).",
        "interpretation": "Survival classes overlap heavily in 2D - consistent with weak linear signal and modest AUC.",
        "clinical_interpretation": (
            "Patients who died within a year (Class 0) are intermixed with survivors in the plot - exactly what you "
            "see in practice when two patients with similar preoperative labs have different outcomes because of "
            "tumor stage, resection margin, or postoperative complications not in this dataset."
        ),
        "implications": "Bridges unsupervised structure to supervised outcome; explains why labs-only models plateau.",
        "clinical_implication": (
            "Use this to justify missing variables in limitations: 'The overlap shows why our model caps around "
            "AUC 0.61 - preoperative bloodwork captures part of the story, not surgery, pathology, or comorbidity.'"
        ),
        "point_out": "Both classes intermingle - explains modest AUC.",
        "dont_claim": "Do not claim clear class separation in PCA space.",
    },
    {
        "num": 16, "file": "confusion_matrix.png", "section": "7.3",
        "shows": "Tuned RF (f1_macro) predictions on 176-patient test set. 20/55 (36.4%) high-risk patients correctly identified (up from 6/55 under legacy f1 tuning).",
        "interpretation": "Model predicts majority class well but misses 49 of 55 Class-0 patients (false negatives).",
        "clinical_interpretation": (
            "Of 55 patients who actually died within a year, the model flagged only 6 - it would send 49 high-risk "
            "patients into the 'likely survivor' bucket. In clinical terms, that is dangerous as a standalone screening "
            "tool, though it is slightly better than predicting everyone survives (0/55 caught)."
        ),
        "implications": "Clinically insufficient for deployment; report per-class recall, not accuracy alone.",
        "clinical_implication": (
            "Defense framing: 'We are transparent that this model is research-grade, not clinic-ready. Its value is "
            "identifying which preoperative markers matter - CEA, prealbumin, CA19-9 - for building a future model "
            "with staging and treatment variables.'"
        ),
        "point_out": "False negatives dominate - 49 high-risk patients missed.",
        "dont_claim": "Do not claim model is 'safe' for clinical triage.",
    },
    {
        "num": 17, "file": "roc_curve.png", "section": "7.3",
        "shows": "ROC curve with AUC = 0.563 vs diagonal (random = 0.5). Lower than legacy f1 tuning (0.613) by macro-F1 design.",
        "interpretation": "Better than random but below ~0.7 threshold often cited for clinical utility.",
        "clinical_interpretation": (
            "AUC 0.563 means if you pick one patient who died within a year and one who survived, the model ranks "
            "the higher-risk patient higher about 61% of the time - better than a coin flip, but far from the ~0.70+ "
            "discrimination oncologists want for treatment decisions."
        ),
        "implications": "Performance ceiling is data-limited; all benchmark models also AUC < 0.63.",
        "clinical_implication": (
            "Preempt the 'is 0.563 good enough?' question: 'No - not for deployment. Yes - for research, because it "
            "proves preoperative labs contain real but incomplete prognostic information, and it tells us where to "
            "add staging, pathology, and treatment features next.'"
        ),
        "point_out": "AUC 0.563 = limited but non-zero discrimination; macro F1 tuning trades AUC for class-0 recall.",
        "dont_claim": "Do not call 0.563 'good' or 'clinical-grade'.",
    },
    {
        "num": 18, "file": "classification_report.png", "section": "7.3",
        "shows": "Per-class precision, recall, and F1 for Class 0 (died <1 yr) and Class 1 (survived >=1 yr).",
        "interpretation": "Class 1 (majority): moderate recall. Class 0 (minority): improved recall (36.4%) after f1_macro tuning - macro F1 = 0.550.",
        "clinical_interpretation": (
            "The model is good at confirming patients who will survive at least a year - the easier, majority case. "
            "It performs poorly on the minority who die within a year - the patients clinicians most need to identify "
            "early for goals-of-care discussions and aggressive supportive care."
        ),
        "implications": "Always report macro F1 and per-class metrics alongside accuracy.",
        "clinical_implication": (
            "Explain class_weight='balanced': 'We penalized missing sick patients more heavily, but weak preoperative "
            "signal still limits minority recall. This is why we list SMOTE, staging features, and external validation "
            "as future work - not because we ignored imbalance.'"
        ),
        "point_out": "Class imbalance mitigation insufficient for minority recall.",
        "dont_claim": "Do not cite accuracy without noting poor Class-0 recall.",
    },
    {
        "num": 19, "file": "feature_importance.png", "section": "7.4",
        "shows": "Horizontal bar chart of all 20 Gini importances. Top 5: CEA, Prealbumin, CA19-9, Total Bilirubin, BMI.",
        "interpretation": "Importance spread across tumor markers, nutrition, and inflammation - no single dominant predictor.",
        "clinical_interpretation": (
            "CEA and CA19-9 - classic pancreatic tumor markers - rank highly, validating clinical intuition. "
            "Prealbumin reflects nutritional reserve; low prealbumin before surgery is a known poor prognostic sign. "
            "Bilirubin captures obstructive jaundice burden. The model learns a composite surgical-risk picture, not one lab."
        ),
        "implications": "Feeds Section 8 synthesis; multivariate ranking differs from univariate correlation order.",
        "clinical_implication": (
            "If asked 'Why is CEA #1 not CA19-9?' - explain that Gini importance reflects combinations: CEA may "
            "interact with nutrition and inflammation markers to split high-risk patients. Both markers remain clinically relevant."
        ),
        "point_out": "Multivariate ranking - tumor markers + nutrition + biliary burden.",
        "dont_claim": "Do not call Gini importance 'causal' - it is split contribution in the forest.",
    },
    {
        "num": 20, "file": "supervised_model_comparison.png", "section": "7.5",
        "shows": "Grouped bars: RF vs LR vs SVM vs GB on accuracy, macro F1, AUC.",
        "interpretation": "All models in weak band (AUC < 0.63). SVM RBF best macro F1 (~0.590) and AUC (~0.622). RF kept for Gini importance.",
        "clinical_interpretation": (
            "Switching to SVM would not transform this into a clinic-ready predictor - every model stays below "
            "useful discrimination. SVM catches somewhat more high-risk patients, but none reach the threshold "
            "where an oncologist would trust labs-only risk scores alone."
        ),
        "implications": "Model choice driven by interpretability and synthesis requirements, not marginal metric gains.",
        "clinical_implication": (
            "Defense: 'We chose Random Forest not because it wins every metric, but because it gives feature "
            "importance we can compare to cluster profiles - the bridge analysis is our project's intellectual core. "
            "SVM would leave that synthesis blind without advanced SHAP methods.'"
        ),
        "point_out": "SVM wins metrics; RF wins interpretability for Section 8.",
        "dont_claim": "Do not say RF is 'best model' - say 'primary model for synthesis'.",
    },
    {
        "num": 21, "file": "synthesis_comparison.png", "section": "8.1",
        "shows": "Side-by-side top-10 RF importance vs cluster-differentiation rankings.",
        "interpretation": "Overlap in CEA, Prealbumin, CA19-9, and inflammatory markers - supervised and unsupervised analyses converge.",
        "clinical_interpretation": (
            "Two independent methods - one predicting survival, one grouping similar patients - both highlight the "
            "same clinical themes: tumor burden (CEA, CA19-9), nutritional status (prealbumin), and systemic inflammation. "
            "That convergence is medically coherent even though neither method achieves strong standalone performance."
        ),
        "implications": "Core project contribution: mutual validation of limited preoperative signal.",
        "clinical_implication": (
            "This is your strongest defense slide: 'We are not claiming excellent prediction. We are showing that "
            "when two different analyses point to the same preoperative markers, we gain confidence that those markers "
            "truly describe surgical risk biology - and that adding staging data should target the same pathways.'"
        ),
        "point_out": "Convergence on inflammation/tumor/nutrition markers - synthesis headline.",
        "dont_claim": "Do not claim convergence proves strong prediction - it shows directional alignment.",
    },
]
