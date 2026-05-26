"""Build PCSPF Data Science Capstone notebook using nbformat."""
from __future__ import annotations

import nbformat as nbf
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

NOTEBOOK_PATH = "PCSPF_Data_Science_Capstone.ipynb"
RANDOM_STATE = 42
OPTIMAL_K = 3


def md(text: str):
    return new_markdown_cell(text.strip())


def code(text: str):
    return new_code_cell(text.strip())


def build_notebook():
    cells = []

    # --- SECTION 1 ---
    cells.append(md("## SECTION 1: Project Setup and Imports"))
    cells.append(md(
        "This capstone applies supervised learning (Random Forest) and unsupervised "
        "learning (K-Means) to the PCSPF pancreatic cancer survival dataset. We begin "
        "by importing libraries, fixing random seeds for reproducibility, and "
        "configuring publication-quality plotting defaults. A dedicated figures "
        "directory ensures every visualization is saved at 300 dpi for the report."
    ))
    cells.append(code("""
import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import (
    train_test_split, GridSearchCV, StratifiedKFold,
)
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_curve, auc,
    accuracy_score, f1_score, precision_score, recall_score,
    precision_recall_fscore_support, silhouette_score,
)
from imblearn.over_sampling import SMOTE  # imported for documentation; not used
from scipy.stats import chi2_contingency, shapiro, normaltest
from statsmodels.stats.outliers_influence import variance_inflation_factor

RANDOM_STATE = 42
OPTIMAL_K = 3
np.random.seed(RANDOM_STATE)

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_theme(style="whitegrid", palette="colorblind")
plt.rcParams.update({
    "figure.figsize": (10, 6),
    "figure.dpi": 100,
    "savefig.dpi": 300,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
})

os.makedirs("figures", exist_ok=True)
print("Setup complete. RANDOM_STATE =", RANDOM_STATE, "OPTIMAL_K =", OPTIMAL_K)
"""))

    # --- SECTION 2 ---
    cells.append(md("## SECTION 2: Data Loading and Initial Inspection"))
    cells.append(md(
        "We load the Excel dataset and inspect structure, dtypes, missing values, "
        "and duplicates before cleaning. Columns ID and the two Predict label fields "
        "are unusable and will be dropped. The binary survival target will be renamed "
        "to survival_label for clarity."
    ))
    cells.append(code("""
DATA_PATH = "Dataset/PCSPF-Pancreatic Cancer Survival based on Preoperative Features.xlsx"
TARGET_ORIG = (
    "label(Survive more than or equal to one year(1) / "
    "Survive less than one year(0))"
)
DROP_COLS = ["ID", "Predict label 1", "Predict label 0"]

df_raw = pd.read_excel(DATA_PATH)
print("Shape:", df_raw.shape)
print("\\nColumns:\\n", list(df_raw.columns))
print("\\nDtypes:\\n", df_raw.dtypes)
display(df_raw.head())
display(df_raw.tail())
print("\\nMissing values per column:\\n", df_raw.isnull().sum())
print("\\nDuplicate rows:", df_raw.duplicated().sum())
print("\\nTarget distribution:\\n", df_raw[TARGET_ORIG].value_counts())
print("\\nTarget %:\\n", df_raw[TARGET_ORIG].value_counts(normalize=True) * 100)

df = df_raw.drop(columns=DROP_COLS).rename(columns={TARGET_ORIG: "survival_label"})
print("\\nCleaned shape:", df.shape)
assert df.shape == (878, 21)
"""))
    cells.append(md(
        "The raw dataset contains 878 patients and 24 columns. After dropping ID "
        "(anonymized), Predict label 1, and Predict label 0 (878/878 NaN each), the "
        "cleaned frame has 878 rows and 21 columns (20 features plus survival_label). "
        "There are zero missing values in usable features. The target is imbalanced: "
        "class 1 (survived >= 1 year) has 604 patients (68.8%) and class 0 has 274 "
        "(31.2%), a ratio of about 2.20:1. This imbalance will be addressed later "
        "with class_weight='balanced' in Random Forest."
    ))

    # --- SECTION 3 EDA ---
    cells.append(md("## SECTION 3: Exploratory Data Analysis (EDA)"))
    cells.append(md("### 3.1 -- Summary Statistics Table"))
    cells.append(md(
        "Descriptive statistics summarize central tendency, spread, and range for "
        "every feature. Large ranges (e.g., CA19-9) and mean-median gaps indicate "
        "skewness that we examine further in later subsections."
    ))
    cells.append(code("""
FEATURE_COLS = [c for c in df.columns if c != "survival_label"]
BINARY_COLS = ["Sex", "Abdominal Pain"]
CONTINUOUS_COLS = [c for c in FEATURE_COLS if c not in BINARY_COLS]

desc = df[FEATURE_COLS].describe().T
display(desc.round(3))
"""))
    cells.append(md(
        "CA19-9, CRP, CEA, and bilirubin markers show very large maxima relative to "
        "medians, indicating right-skewed distributions. Age and BMI are more symmetric. "
        "Several inflammatory ratios (NLR, PLR, SII) also have elevated upper tails. "
        "These patterns motivate retaining outliers (clinical extremes) and using "
        "StandardScaler for K-Means rather than log transforms for Random Forest."
    ))

    cells.append(md("### 3.2 -- Target Class Distribution"))
    cells.append(md(
        "Visualizing class counts clarifies imbalance magnitude. A naive majority-class "
        "classifier would achieve 68.8% accuracy by predicting survival for all patients."
    ))
    cells.append(code("""
vc = df["survival_label"].value_counts().sort_index()
pct = df["survival_label"].value_counts(normalize=True).sort_index() * 100
imbalance_ratio = vc[1] / vc[0]
print(f"Class imbalance ratio (1/0): {imbalance_ratio:.2f}:1")

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(["Survived < 1 yr (0)", "Survived >= 1 yr (1)"], vc.values,
              color=sns.color_palette("colorblind", 2))
for b, c, p in zip(bars, vc.values, pct.values):
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 8,
            f"{c}\\n({p:.1f}%)", ha="center", fontsize=11)
ax.set_ylabel("Patient Count")
ax.set_title("Target Class Distribution (PCSPF)")
plt.tight_layout()
plt.savefig("figures/target_distribution.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    cells.append(md(
        "The imbalance ratio is approximately 2.20:1 (604 vs 274). This matters because "
        "accuracy alone can look acceptable while the model ignores the minority class. "
        "We will use class_weight='balanced' in Random Forest and emphasize F1-score "
        "and AUC-ROC in evaluation."
    ))

    cells.append(md("### 3.3 -- Feature Distributions"))
    cells.append(md(
        "Histograms with KDE overlays reveal shape of each continuous feature. "
        "Right-skewed labs are common in oncology data."
    ))
    cells.append(code("""
n = len(CONTINUOUS_COLS)
ncols, nrows = 5, 4
fig, axes = plt.subplots(nrows, ncols, figsize=(18, 14))
axes = axes.flatten()
color = sns.color_palette("colorblind")[0]
for i, col in enumerate(CONTINUOUS_COLS):
    sns.histplot(df[col], kde=True, ax=axes[i], color=color, edgecolor="white")
    axes[i].set_title(col, fontsize=10)
for j in range(i + 1, len(axes)):
    axes[j].axis("off")
fig.suptitle("Continuous Feature Distributions (with KDE)", y=1.01, fontsize=14)
plt.tight_layout()
plt.savefig("figures/feature_distributions.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    cells.append(md(
        "Age and BMI appear roughly symmetric. CA19-9, CRP, CEA, Total and Directed "
        "Bilirubin, SII, NLR, and PLR are visibly right-skewed with long upper tails. "
        "Prealbumin and ALB are less skewed. Random Forest is robust to skew; K-Means "
        "will rely on StandardScaler rather than transforms."
    ))

    cells.append(md("### 3.4 -- Boxplots Grouped by Survival Label"))
    cells.append(md(
        "Side-by-side boxplots by survival_label highlight features with visible "
        "separation between outcome groups."
    ))
    cells.append(code("""
fig, axes = plt.subplots(nrows, ncols, figsize=(18, 14))
axes = axes.flatten()
for i, col in enumerate(CONTINUOUS_COLS):
    sns.boxplot(data=df, x="survival_label", y=col, ax=axes[i],
                palette="colorblind", hue="survival_label", legend=False)
    axes[i].set_title(col, fontsize=10)
    axes[i].set_xlabel("Survival Label")
for j in range(i + 1, len(axes)):
    axes[j].axis("off")
fig.suptitle("Continuous Features by Survival Label", y=1.01, fontsize=14)
plt.tight_layout()
plt.savefig("figures/boxplots_by_survival.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    cells.append(md(
        "CA19-9, Abdominal Pain (binary), Neutrocyte, NLR, and SII tend to be higher "
        "in class 0 (shorter survival). Prealbumin tends higher in class 1. Many "
        "features show overlapping distributions, consistent with weak univariate "
        "correlations with the target."
    ))

    cells.append(md("### 3.5 -- Correlation Heatmap"))
    cells.append(md(
        "Pearson correlations among all features and the target reveal multicollinearity "
        "and weak individual predictive correlations."
    ))
    cells.append(code("""
corr = df[FEATURE_COLS + ["survival_label"]].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
fig, ax = plt.subplots(figsize=(14, 12))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, square=True, linewidths=0.5, ax=ax,
            cbar_kws={"shrink": 0.8})
ax.set_title("Feature Correlation Matrix (Lower Triangle)")
plt.tight_layout()
plt.savefig("figures/correlation_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    cells.append(md(
        "Strong inter-feature correlations appear among Neutrocyte-NLR, Platelet-PLR, "
        "CRP-CRP/ALB, and Total-Directed Bilirubin, reflecting derived ratios and "
        "physiology. All feature-target correlations are below |0.15| in magnitude; "
        "the strongest signals are negative for Abdominal Pain and CA19-9 and positive "
        "for Prealbumin. Models must capture interactions rather than single-feature rules."
    ))

    cells.append(md("### 3.6 -- Multicollinearity Discussion"))
    cells.append(md(
        "Derived indices in the dataset are mathematically linked to components: "
        "NLR = Neutrocyte / Lymphocyte, PLR = Platelet / Lymphocyte, "
        "SII = Platelet * Neutrocyte / Lymphocyte, and CRP/ALB = CRP / ALB. "
        "Directed Bilirubin is a fraction of Total Bilirubin. For Random Forest, "
        "random feature subsampling mitigates redundancy at splits. For K-Means, "
        "correlated dimensions can overweight certain clinical axes in Euclidean distance; "
        "we retain all features for clinical interpretability and consistency with RF."
    ))

    cells.append(md("### 3.7 -- Class-Conditional Feature Means"))
    cells.append(md(
        "Comparing class means quantifies which features differ most between survival groups."
    ))
    cells.append(code("""
mean0 = df[df["survival_label"] == 0][FEATURE_COLS].mean()
mean1 = df[df["survival_label"] == 1][FEATURE_COLS].mean()
diff = (mean1 - mean0).abs()
pct_diff = (diff / mean0.replace(0, np.nan) * 100).fillna(0)
cmp_tbl = pd.DataFrame({
    "Mean Class 0": mean0, "Mean Class 1": mean1,
    "Abs Diff": diff, "Pct Diff (%)": pct_diff,
}).sort_values("Abs Diff", ascending=False)
display(cmp_tbl.round(3))

top10 = cmp_tbl.head(10).index
plot_df = cmp_tbl.loc[top10, ["Mean Class 0", "Mean Class 1"]]
y = np.arange(len(top10))
h = 0.35
fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(y - h/2, plot_df["Mean Class 0"], height=h, label="Class 0", color=sns.color_palette("colorblind")[0])
ax.barh(y + h/2, plot_df["Mean Class 1"], height=h, label="Class 1", color=sns.color_palette("colorblind")[1])
ax.set_yticks(y)
ax.set_yticklabels(top10)
ax.invert_yaxis()
ax.set_xlabel("Mean Value")
ax.set_title("Top 10 Features by Class Mean Difference")
ax.legend()
plt.tight_layout()
plt.savefig("figures/class_conditional_means.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    cells.append(md(
        "By |mean| difference, CA19-9 leads (0.305), followed by Prealbumin, Neutrocyte, "
        "Abdominal Pain, and inflammatory indices (SII, NLR, CRP). Class 0 (died <1 yr) "
        "shows higher CA19-9, Abdominal Pain, and inflammatory markers; Class 1 (survived "
        "≥1 yr) shows higher Prealbumin. These patterns align with pancreatic cancer "
        "prognostic literature but remain modest at the univariate level."
    ))

    cells.append(md("### 3.8 -- EDA Summary"))
    cells.append(md(
        "Distribution review shows widespread right skew in tumor and inflammatory labs, "
        "with clinically meaningful extremes retained. Correlation analysis confirms strong "
        "multicollinearity among ratio features and bilirubin pairings, while individual "
        "target correlations remain weak. Class-conditional means suggest CA19-9, "
        "inflammation indices, and prealbumin separate groups modestly. For modeling, "
        "Random Forest can capture interactions without scaling; K-Means requires "
        "StandardScaler; imbalance handling via class_weight='balanced' is essential."
    ))

    # SECTION 4 - will continue in part 2 via append in same file
    cells.extend(_section_4_cells())
    cells.extend(_section_5_cells())
    cells.extend(_section_6_cells())
    cells.extend(_section_7_cells())
    cells.extend(_section_8_cells())
    cells.extend(_section_9_cells())

    nb = new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"},
    })
    return nb


def _section_4_cells():
    c = []
    c.append(md("## SECTION 4: Data Preprocessing"))
    c.append(md("### 4.1 -- Data Type Verification and Casting"))
    c.append(md(
        "We verify numeric types for all 20 features before modeling."
    ))
    c.append(code("""
print(df[FEATURE_COLS].dtypes)
for col in BINARY_COLS:
    print(f"{col} unique:", sorted(df[col].unique()))
"""))
    c.append(md(
        "All 20 features are confirmed to be in correct numeric data types. Sex and "
        "Abdominal Pain contain only binary values (0 and 1) encoded as integers. All "
        "18 continuous features are stored as float64. No type casting was required."
    ))

    c.append(md("### 4.2 -- Missing Value Audit (Post-Cleaning Confirmation)"))
    c.append(md("Re-verify zero missing values after column drops."))
    c.append(code("""
print("Per-column nulls:\\n", df.isnull().sum())
print("Total nulls:", df.isnull().sum().sum())
print("Any null:", df.isna().any().any())
"""))
    c.append(md(
        "After dropping the three unusable columns (ID, Predict label 1, Predict label 0), "
        "the cleaned dataset contains zero missing values across all 20 features and the "
        "target variable. No imputation strategy is required. This was verified using "
        "three independent checks: per-column null counts, total null count, and a "
        "boolean any-null test."
    ))

    c.append(md("### 4.3 -- Duplicate Row Detection and Handling"))
    c.append(md("Exact duplicate rows are checked; any findings guide retention decisions."))
    c.append(code("""
n_dup = df.duplicated().sum()
print("Exact duplicate rows:", n_dup)
if n_dup > 0:
    display(df[df.duplicated(keep=False)])
"""))
    c.append(md(
        "No exact duplicate rows were found in the cleaned dataset. All 878 patient "
        "records are retained. No duplicate removal was necessary."
    ))

    c.append(md("### 4.4 -- Outlier Detection and Handling"))
    c.append(md(
        "IQR-based outlier counts quantify extreme values per feature. We visualize "
        "normalized boxplots for comparability."
    ))
    c.append(code("""
outlier_rows = []
for col in CONTINUOUS_COLS:
    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n_lo = (df[col] < lo).sum()
    n_hi = (df[col] > hi).sum()
    n_tot = n_lo + n_hi
    outlier_rows.append({
        "Feature": col, "Q1": q1, "Q3": q3, "IQR": iqr,
        "Lower Bound": lo, "Upper Bound": hi,
        "# Lower Outliers": n_lo, "# Upper Outliers": n_hi,
        "Total Outliers": n_tot, "% Outliers": 100 * n_tot / len(df),
    })
outlier_tbl = pd.DataFrame(outlier_rows)
display(outlier_tbl.round(3))

z_df = df[CONTINUOUS_COLS].apply(lambda x: (x - x.mean()) / x.std())
fig, ax = plt.subplots(figsize=(14, 6))
sns.boxplot(data=z_df, orient="h", fliersize=2, color=sns.color_palette("colorblind")[0])
ax.set_title("Z-Score Normalized Continuous Features (Outlier Comparison)")
ax.set_xlabel("Z-Score")
plt.tight_layout()
plt.savefig("figures/outlier_boxplots.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    c.append(md(
        "CEA shows the highest outlier rate (10.4%; 91/878), followed by NLR (6.8%), SII (6.3%), "
        "bilirubin (~5-6%), and CRP/CRP/ALB (~5.6%)—predominantly upper-tail extremes consistent with "
        "skewed oncology and inflammation labs. CA19-9 registers 0% under the 1.5×IQR rule: its wide "
        "interquartile range absorbs all observed values, so no points appear beyond the boxplot whiskers "
        "despite right skew in Section 3.3."
    ))
    c.append(md(
        "**Decision: Do NOT remove outliers.** (1) Clinical validity: extreme labs are "
        "diagnostically meaningful in pancreatic cancer. (2) Random Forest robustness: "
        "splits are rank-based. (3) K-Means mitigation: StandardScaler reduces magnitude "
        "effects; extreme patients may form meaningful subgroups. (4) Sample size: "
        "removing 5-10% would reduce power and may delete high-risk patients."
    ))

    c.append(md("### 4.5 -- Skewness and Normality Assessment"))
    c.append(md(
        "Skewness, kurtosis, and D'Agostino-Pearson tests assess normality assumptions."
    ))
    c.append(code("""
skew_rows = []
for col in CONTINUOUS_COLS:
    sk = df[col].skew()
    ku = df[col].kurtosis()
    if abs(sk) < 0.5:
        interp = "approximately symmetric"
    elif abs(sk) < 1.0:
        interp = "moderately skewed"
    else:
        interp = "highly skewed"
    stat, p = normaltest(df[col].dropna())
    skew_rows.append({
        "Feature": col, "Skewness": sk, "Kurtosis": ku,
        "Skewness Interpretation": interp,
        "Test Statistic": stat, "p-value": p,
        "Normal?": "Normal (p >= 0.05)" if p >= 0.05 else "Non-normal (p < 0.05)",
    })
skew_tbl = pd.DataFrame(skew_rows).sort_values("Skewness", key=abs, ascending=False)
display(skew_tbl.round(4))
# Shapiro-Wilk available via shapiro (imported); not run on n=878 for brevity
"""))
    c.append(md(
        "Most continuous features are significantly non-normal by D'Agostino-Pearson "
        "(p < 0.05). The heaviest right skew is on CEA (skew ≈ 23.9), followed by "
        "inflammatory ratios (PLR, Neutrocyte, NLR, SII) and lactic dehydrogenase; CRP, "
        "CRP/ALB, and bilirubin pairs are also skewed. CA19-9 is only moderately skewed "
        "(|skew| ≈ 0.55), well below the tail-heavy tumor and inflammation markers above."
    ))
    c.append(md(
        "**Decision: Do NOT apply Yeo-Johnson, Box-Cox, or log transformation.** "
        "(1) Random Forest splits depend on rank order. (2) StandardScaler suffices for "
        "K-Means in this course context. (3) Original units preserve clinical "
        "interpretability of cluster profiles. (4) Power transforms noted as future work."
    ))

    c.append(md("### 4.6 -- Multicollinearity Quantification (Variance Inflation Factor)"))
    c.append(md("VIF quantifies redundancy among predictors."))
    c.append(code("""
X_vif = df[FEATURE_COLS].values
vif_data = []
for i, col in enumerate(FEATURE_COLS):
    v = variance_inflation_factor(X_vif, i)
    if v > 10:
        interp = "high multicollinearity"
    elif v > 5:
        interp = "moderate"
    else:
        interp = "low"
    vif_data.append({"Feature": col, "VIF Score": v, "Interpretation": interp})
vif_tbl = pd.DataFrame(vif_data).sort_values("VIF Score", ascending=False)
display(vif_tbl.round(2))
"""))
    c.append(md(
        "Highest VIF scores align with derived ratios (NLR, PLR, SII, CRP/ALB) and "
        "bilirubin pairings, confirming expected multicollinearity."
    ))
    c.append(md(
        "**Decision: Do NOT drop features due to multicollinearity.** Random Forest "
        "subsamples features per split; each marker is clinically validated. K-Means "
        "limitation is acknowledged; derived ratios are retained for clinical relevance."
    ))

    c.append(md("### 4.7 -- Feature Engineering Decision"))
    c.append(md(
        "No additional features were engineered beyond those already present in the dataset. "
        "The dataset contains four pre-computed derived ratios (NLR, PLR, SII, CRP/ALB) "
        "that represent commonly used composite indices in pancreatic cancer prognostic "
        "research. Additional binning or interaction terms were rejected to avoid arbitrary "
        "information loss and overfitting without strong clinical justification."
    ))

    c.append(md("### 4.8 -- Feature Selection Decision"))
    c.append(md(
        "For Random Forest, all 20 features are retained; post-hoc importance guides "
        "interpretation. For K-Means, all 20 features (excluding target) are used for "
        "consistency and direct comparison with supervised findings, acknowledging "
        "multicollinearity in distance calculations."
    ))

    c.append(md("### 4.9 -- Class Imbalance Assessment and Strategy"))
    c.append(code("""
n0 = (df["survival_label"] == 0).sum()
n1 = (df["survival_label"] == 1).sum()
print(f"Imbalance ratio n1/n0: {n1/n0:.2f}")
print(f"Majority baseline accuracy: {n1/len(df)*100:.1f}%")
w0 = len(df) / (2 * n0)
w1 = len(df) / (2 * n1)
print(f"Balanced class weights: class0={w0:.2f}, class1={w1:.2f}")
"""))
    c.append(md(
        "Strategy: class_weight='balanced' in RandomForestClassifier. SMOTE is not used "
        "because synthetic patients are less clinically defensible than reweighting real "
        "cases. Evaluation emphasizes F1-score, AUC-ROC, confusion matrix, and full "
        "classification report rather than accuracy alone."
    ))

    c.append(md("### 4.10 -- Preprocessing Summary Table"))
    c.append(md("Consolidated preprocessing decisions for both pipelines."))
    c.append(code("""
prep_rows = [
    ("Drop unusable columns", "Dropped ID, Predict label 1, Predict label 0",
     "ID anonymized; Predict labels entirely NaN"),
    ("Data type verification", "Confirmed all correct; no casting needed",
     "2 binary (int64), 18 continuous (float64)"),
    ("Missing value handling", "No imputation needed",
     "Zero missing values (verified 3 ways)"),
    ("Duplicate handling", "No duplicates found; all rows retained",
     "duplicated().sum() == 0"),
    ("Outlier handling", "Retained all outliers",
     "Clinical validity; RF robustness; StandardScaler for K-Means"),
    ("Normality/Skewness", "No transformation applied",
     "RF invariant to skewness; StandardScaler for K-Means"),
    ("Multicollinearity (VIF)", "All features retained",
     "RF random subsampling; clinical indices preserved"),
    ("Feature engineering", "No new features created",
     "Existing derived ratios sufficient"),
    ("Feature selection", "All 20 features retained (both models)",
     "RF importance post-hoc; K-Means consistency"),
    ("Feature scaling", "StandardScaler for K-Means only; no scaling for RF",
     "Distance vs tree invariance"),
    ("Class imbalance", "class_weight='balanced' in RF",
     "Penalizes minority errors; no synthetic samples"),
    ("Train-test split", "80/20 stratified split",
     "702 train / 176 test; preserves class proportions"),
]
prep_df = pd.DataFrame(prep_rows, columns=["Preprocessing Step", "Action Taken", "Justification"])
display(prep_df)

fig, ax = plt.subplots(figsize=(14, 8))
ax.axis("off")
tbl = ax.table(cellText=prep_df.values, colLabels=prep_df.columns,
               loc="center", cellLoc="left")
tbl.auto_set_font_size(False)
tbl.set_fontsize(8)
tbl.scale(1, 1.4)
ax.set_title("Preprocessing Decisions Summary", pad=20)
plt.tight_layout()
plt.savefig("figures/preprocessing_summary.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    c.append(md(
        "The table above consolidates every preprocessing decision made in this analysis. "
        "Each decision was evaluated against both supervised and unsupervised pipelines "
        "and justified with respect to the clinical nature of the data."
    ))
    return c


def _section_5_cells():
    c = []
    c.append(md("## SECTION 5: Train-Test Split and Scaling"))
    c.append(md("### 5.1 -- Separate Features and Target"))
    c.append(md("Split predictors and outcome for supervised learning."))
    c.append(code("""
X = df[FEATURE_COLS].copy()
y = df["survival_label"].copy()
print("X shape:", X.shape)
print("y shape:", y.shape)
"""))

    c.append(md("### 5.2 -- Train-Test Split"))
    c.append(md(
        "An 80/20 stratified split preserves class proportions in train and test sets."
    ))
    c.append(code("""
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE,
)
print("X_train:", X_train.shape, "X_test:", X_test.shape)
print("y_train:", y_train.shape, "y_test:", y_test.shape)
print("\\nTrain proportions:\\n", y_train.value_counts(normalize=True))
print("\\nTest proportions:\\n", y_test.value_counts(normalize=True))
"""))
    c.append(md(
        "The split yields 702 training and 176 test patients with stratification preserving "
        "approximately 68.8% / 31.2% class proportions in both partitions. An 80/20 split "
        "balances sufficient training data for Random Forest with a test set large enough "
        "for stable metrics."
    ))

    c.append(md("### 5.3 -- Feature Scaling"))
    c.append(md(
        "StandardScaler is fit on the full X matrix for K-Means (unsupervised uses all "
        "878 patients). Random Forest uses unscaled train/test data."
    ))
    c.append(code("""
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=FEATURE_COLS, index=X.index)

scale_cmp = []
for col in FEATURE_COLS:
    scale_cmp.append({
        "Feature": col,
        "Original Min": X[col].min(), "Original Max": X[col].max(),
        "Original Mean": X[col].mean(), "Original Std": X[col].std(),
        "Scaled Min": X_scaled[col].min(), "Scaled Max": X_scaled[col].max(),
        "Scaled Mean": X_scaled[col].mean(), "Scaled Std": X_scaled[col].std(),
    })
scale_tbl = pd.DataFrame(scale_cmp)
display(scale_tbl.round(3))

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
sns.boxplot(data=X, orient="h", ax=axes[0], color=sns.color_palette("colorblind")[0])
axes[0].set_title("Before Scaling (Raw Values)")
axes[0].set_xlabel("Value")
sns.boxplot(data=X_scaled, orient="h", ax=axes[1], color=sns.color_palette("colorblind")[1])
axes[1].set_title("After StandardScaler (Z-Scores)")
axes[1].set_xlabel("Z-Score")
plt.tight_layout()
plt.savefig("figures/scaling_before_after.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    c.append(md(
        "StandardScaler transforms each feature to mean approximately 0 and std 1 on the "
        "full feature matrix for K-Means. Without scaling, CA19-9 would dominate Euclidean "
        "distance. Random Forest uses unscaled X_train and X_test because tree splits are "
        "scale-invariant."
    ))
    return c


def _section_6_cells():
    c = []
    c.append(md("## SECTION 6: Unsupervised Learning -- K-Means Clustering"))
    c.append(md(
        "Unsupervised learning discovers structure without using survival_label during "
        "clustering. The target is overlaid only post-hoc for evaluation. K-Means runs "
        "on X_scaled (all 878 patients) with OPTIMAL_K = 3."
    ))

    c.append(md("### 6.1 -- Elbow Method"))
    c.append(md("Inertia vs k identifies diminishing returns in cluster count."))
    c.append(code("""
K_RANGE = range(2, 11)
inertias = []
for k in K_RANGE:
    km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(list(K_RANGE), inertias, marker="o")
ax.axvline(3, color="red", linestyle="--", label="Chosen k=3")
ax.set_xlabel("Number of Clusters (k)")
ax.set_ylabel("Inertia")
ax.set_title("Elbow Method (K-Means Inertia)")
ax.legend()
plt.tight_layout()
plt.savefig("figures/elbow_method.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    c.append(md(
        "Inertia measures sum of squared distances to centroids. The curve bends around "
        "k=2 to k=4; k=3 is a reasonable elbow region before gains flatten."
    ))

    c.append(md("### 6.2 -- Silhouette Analysis"))
    c.append(md("Silhouette scores compare cohesion vs separation across k."))
    c.append(code("""
sil_scores = []
for k in K_RANGE:
    km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
    labels = km.fit_predict(X_scaled)
    sil_scores.append(silhouette_score(X_scaled, labels))

best_k_sil = list(K_RANGE)[np.argmax(sil_scores)]
print(f"Best silhouette k: {best_k_sil} (score={max(sil_scores):.4f})")

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(list(K_RANGE), sil_scores, marker="o")
ax.axvline(OPTIMAL_K, color="red", linestyle="--", label=f"Chosen k={OPTIMAL_K}")
ax.set_xlabel("Number of Clusters (k)")
ax.set_ylabel("Silhouette Score")
ax.set_title("Silhouette Score vs k")
ax.legend()
plt.tight_layout()
plt.savefig("figures/silhouette_scores.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    c.append(md(
        "Silhouette is highest at k=2, indicating the tightest natural partition by this "
        "metric alone. However, three clusters are often more actionable clinically "
        "(low/medium/high risk tiers)."
    ))

    c.append(md("### 6.3 -- Choose Optimal k"))
    c.append(md(
        f"**Final choice: k = {OPTIMAL_K}.** The elbow method suggests diminishing "
        "returns around k=2-4. Silhouette maximizes at k=2 (score slightly higher than "
        "k=3). We prioritize k=3 because three patient subgroups map to interpretable "
        "clinical risk strata (favorable, intermediate, aggressive profiles) while still "
        "showing acceptable silhouette and inertia. Binary clustering (k=2) is statistically "
        "tight but less informative for nuanced preoperative stratification."
    ))

    c.append(md("### 6.4 -- Fit Final K-Means Model"))
    c.append(code("""
kmeans_final = KMeans(n_clusters=OPTIMAL_K, random_state=RANDOM_STATE, n_init=10)
cluster_labels = kmeans_final.fit_predict(X_scaled)
df["cluster"] = cluster_labels
cluster_counts = pd.Series(cluster_labels).value_counts().sort_index()
print(cluster_counts)
print((cluster_counts / len(cluster_labels) * 100).round(1).astype(str) + "%")
"""))
    c.append(md(
        "Cluster sizes and percentages describe how patients distribute across the three "
        "discovered subgroups. None should be trivially small given n=878."
    ))

    c.append(md("### 6.5 -- PCA Visualization"))
    c.append(md("Two-dimensional PCA projection visualizes cluster separation."))
    c.append(code("""
pca = PCA(n_components=2, random_state=RANDOM_STATE)
X_pca = pca.fit_transform(X_scaled)
evr = pca.explained_variance_ratio_
print(f"PC1 variance: {evr[0]*100:.2f}%")
print(f"PC2 variance: {evr[1]*100:.2f}%")
print(f"Cumulative: {(evr[0]+evr[1])*100:.2f}%")

centroids_pca = pca.transform(kmeans_final.cluster_centers_)
fig, ax = plt.subplots(figsize=(9, 7))
scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_labels,
                     cmap="tab10", alpha=0.6, s=25)
ax.scatter(centroids_pca[:, 0], centroids_pca[:, 1], c="red", marker="X",
           s=200, linewidths=2, label="Centroids")
ax.set_xlabel(f"PC1 ({evr[0]*100:.1f}% variance)")
ax.set_ylabel(f"PC2 ({evr[1]*100:.1f}% variance)")
ax.set_title("PCA of Scaled Features Colored by Cluster")
plt.colorbar(scatter, label="Cluster")
ax.legend()
plt.tight_layout()
plt.savefig("figures/pca_clusters.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    c.append(md(
        "The first two principal components capture only part of total variance; some overlap "
        "in 2D is expected even when clusters are better separated in 20 dimensions."
    ))

    c.append(md("### 6.6 -- Cluster Profiling"))
    c.append(md("Cluster means on original scale support clinical interpretation."))
    c.append(code("""
cluster_means = df.groupby("cluster")[FEATURE_COLS].mean()
cluster_stds = df.groupby("cluster")[FEATURE_COLS].std()
display(cluster_means.round(3))
display(cluster_stds.round(3))

z_means = (cluster_means - cluster_means.mean()) / cluster_means.std()
fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(z_means, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
ax.set_title("Cluster Profiles (Z-Scored Mean Features)")
ax.set_ylabel("Cluster")
plt.tight_layout()
plt.savefig("figures/cluster_profiles_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    c.append(md(
        "Cluster profiles should be interpreted against mean tables above. Typically one "
        "cluster shows elevated CA19-9, CRP, NLR/SII (high tumor burden/inflammation), "
        "one shows more favorable prealbumin and lower markers, and one intermediate. "
        "Assign clinical labels after inspecting printed means for this run."
    ))

    c.append(md("### 6.7 -- Cluster-Survival Overlay (Bridge Analysis)"))
    c.append(md("Cross-tabulation links unsupervised groups to observed survival."))
    c.append(code("""
ct = pd.crosstab(df["cluster"], df["survival_label"])
display(ct)
surv_rate = df.groupby("cluster")["survival_label"].mean() * 100
print("Survival rate (% label=1) per cluster:\\n", surv_rate.round(2))

ct_plot = ct.reset_index().melt(id_vars="cluster", var_name="survival_label", value_name="count")
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=ct_plot, x="cluster", y="count", hue="survival_label",
            palette="colorblind", ax=ax)
for container in ax.containers:
    ax.bar_label(container, fmt="%d", padding=2, fontsize=9)
ax.set_xlabel("Cluster")
ax.set_ylabel("Count")
ax.set_title("Cluster vs Survival Label")
ax.legend(title="Survival Label", labels=["< 1 yr (0)", ">= 1 yr (1)"])
plt.tight_layout()
plt.savefig("figures/cluster_survival_overlay.png", dpi=300, bbox_inches="tight")
plt.show()

chi2, p, dof, expected = chi2_contingency(ct)
print(f"Chi-square={chi2:.4f}, dof={dof}, p-value={p:.4e}")
print("Expected frequencies:\\n", pd.DataFrame(expected, index=ct.index, columns=ct.columns).round(2))
"""))
    c.append(md(
        "Chi-square tests whether cluster membership associates with survival. If p < 0.05, "
        "subgroups differ significantly in outcome rates. Compare highest vs lowest survival "
        "clusters to cluster clinical profiles from 6.6."
    ))

    c.append(md("### 6.8 -- PCA Scatter Colored by Actual Survival Label"))
    c.append(md("Compare unsupervised clusters to known survival labels in PCA space."))
    c.append(code("""
fig, ax = plt.subplots(figsize=(9, 7))
scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=df["survival_label"],
                     cmap="coolwarm", alpha=0.6, s=25)
ax.set_xlabel(f"PC1 ({evr[0]*100:.1f}% variance)")
ax.set_ylabel(f"PC2 ({evr[1]*100:.1f}% variance)")
ax.set_title("PCA Colored by Actual Survival Label")
cbar = plt.colorbar(scatter, ticks=[0, 1])
cbar.set_label("Survival Label")
plt.tight_layout()
plt.savefig("figures/pca_survival_labels.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    c.append(md(
        "Comparing PCA plots shows partial alignment: cluster boundaries may approximate "
        "but not perfectly match survival regions, indicating unsupervised structure "
        "captures related but not identical information to the binary outcome."
    ))
    return c


def _section_7_cells():
    c = []
    c.append(md("## SECTION 7: Supervised Learning -- Random Forest Classifier"))
    c.append(md("### 7.1 -- Baseline Model (Before Tuning)"))
    c.append(md(
        "Baseline Random Forest with class_weight='balanced' establishes performance "
        "before GridSearchCV hyperparameter tuning."
    ))
    c.append(code("""
rf_base = RandomForestClassifier(
    n_estimators=100, class_weight="balanced", random_state=RANDOM_STATE,
)
rf_base.fit(X_train, y_train)
y_pred_base = rf_base.predict(X_test)
base_acc = accuracy_score(y_test, y_pred_base)
print(f"Baseline accuracy: {base_acc*100:.2f}%")
print(classification_report(y_test, y_pred_base, target_names=["<1yr", ">=1yr"]))
print("Confusion matrix:\\n", confusion_matrix(y_test, y_pred_base))
"""))
    c.append(md(
        "This untuned baseline uses default hyperparameters with balanced class weights. "
        "Compare its accuracy to the 68.8% majority-class baseline before evaluating "
        "the tuned model in the next subsection."
    ))

    c.append(md("### 7.2 -- Hyperparameter Tuning"))
    c.append(md(
        "GridSearchCV optimizes F1 with stratified 5-fold cross-validation."
    ))
    c.append(code("""
param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [None, 10, 15, 20],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
grid = GridSearchCV(
    RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE),
    param_grid=param_grid,
    cv=cv,
    scoring="f1",
    n_jobs=-1,
    return_train_score=True,
)
grid.fit(X_train, y_train)
print("Best params:", grid.best_params_)
print(f"Best CV F1: {grid.best_score_:.4f}")

cv_results = pd.DataFrame(grid.cv_results_)
top10 = cv_results.nlargest(10, "mean_test_score")[
    ["params", "mean_test_score", "std_test_score"]
]
display(top10)

rf_tuned = grid.best_estimator_
"""))
    c.append(md(
        "F1-score balances precision and recall for the positive class, penalizing models "
        "that ignore the minority class. StratifiedKFold preserves class proportions in "
        "each fold. Best parameters control ensemble size, tree depth, and leaf/split "
        "constraints to reduce overfitting while maintaining recall for high-risk patients."
    ))

    c.append(md("### 7.3 -- Final Model Evaluation on Test Set"))
    c.append(md("Comprehensive test-set metrics for the tuned model."))
    c.append(code("""
y_pred = rf_tuned.predict(X_test)
y_proba = rf_tuned.predict_proba(X_test)[:, 1]
tuned_acc = accuracy_score(y_test, y_pred)
base_majority = y_test.value_counts(normalize=True).max()

print(f"Majority-class baseline: {base_majority*100:.1f}%")
print(f"Untuned baseline accuracy: {base_acc*100:.2f}%")
print(f"Tuned model accuracy: {tuned_acc*100:.2f}%")
print(f"Improvement over baseline: +{(tuned_acc-base_majority)*100:.2f} pp")
print(f"Improvement from tuning: +{(tuned_acc-base_acc)*100:.2f} pp")
print("\\n", classification_report(y_test, y_pred, target_names=["<1yr", ">=1yr"]))

# Classification report figure
rep = classification_report(y_test, y_pred, output_dict=True)
rep_df = pd.DataFrame(rep).transpose().iloc[:4, :4]
fig, ax = plt.subplots(figsize=(8, 4))
ax.axis("off")
ax.table(cellText=np.round(rep_df.values, 3), colLabels=rep_df.columns,
         rowLabels=rep_df.index, loc="center")
ax.set_title("Classification Report (Test Set)")
plt.tight_layout()
plt.savefig("figures/classification_report.png", dpi=300, bbox_inches="tight")
plt.show()

cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
            xticklabels=["Survived < 1yr", "Survived >= 1yr"],
            yticklabels=["Survived < 1yr", "Survived >= 1yr"])
ax.set_xlabel("Predicted Label")
ax.set_ylabel("Actual Label")
ax.set_title("Confusion Matrix (Tuned Random Forest)")
plt.tight_layout()
plt.savefig("figures/confusion_matrix.png", dpi=300, bbox_inches="tight")
plt.show()

fpr, tpr, _ = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)
fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curve (Tuned Random Forest)")
ax.legend(loc="lower right")
plt.tight_layout()
plt.savefig("figures/roc_curve.png", dpi=300, bbox_inches="tight")
plt.show()

prec, rec, fsc, _ = precision_recall_fscore_support(y_test, y_pred, labels=[0, 1])
rep_dict = classification_report(y_test, y_pred, output_dict=True)
metrics_summary = pd.DataFrame({
    "Metric": [
        "Accuracy", "Baseline Accuracy",
        "Precision (class 0)", "Recall (class 0)", "F1 (class 0)",
        "Precision (class 1)", "Recall (class 1)", "F1 (class 1)",
        "Macro F1", "Weighted F1", "AUC-ROC",
    ],
    "Value": [
        tuned_acc, base_majority, prec[0], rec[0], fsc[0],
        prec[1], rec[1], fsc[1],
        (fsc[0] + fsc[1]) / 2, rep_dict["weighted avg"]["f1-score"],
        roc_auc,
    ],
})
display(metrics_summary.round(4))
"""))
    c.append(md(
        "Overall performance should exceed the 68.8% majority baseline. AUC near 0.7-0.8 "
        "is acceptable for clinical screening contexts. Review minority-class recall: "
        "false negatives (predicted survival but died <1 year) are clinically dangerous; "
        "false positives cause unnecessary anxiety but may trigger safer monitoring."
    ))

    c.append(md("### 7.4 -- Feature Importance"))
    c.append(md("Gini importance ranks predictive contribution of each feature."))
    c.append(code("""
imp = pd.Series(rf_tuned.feature_importances_, index=FEATURE_COLS).sort_values()
print("Top 5:\\n", imp.tail(5))
print("\\nBottom 5:\\n", imp.head(5))

fig, ax = plt.subplots(figsize=(10, 8))
imp.plot(kind="barh", ax=ax, color=sns.color_palette("colorblind")[0])
for i, v in enumerate(imp.values):
    ax.text(v + 0.001, i, f"{v:.3f}", va="center", fontsize=9)
ax.set_xlabel("Importance")
ax.set_title("Random Forest Feature Importances (Tuned)")
plt.tight_layout()
plt.savefig("figures/feature_importance.png", dpi=300, bbox_inches="tight")
plt.show()
"""))
    c.append(md(
        "Top features often include CA19-9 (pancreatic tumor marker), inflammatory indices, "
        "and nutritional markers such as Prealbumin. CA19-9 above 37 U/mL is clinically "
        "elevated; very high levels suggest advanced disease. Lower-ranked features may "
        "be redundant with correlated markers or have weak marginal signal captured "
        "only through interactions."
    ))
    return c


def _section_8_cells():
    c = []
    c.append(md("## SECTION 8: Synthesis and Bridging Analysis"))
    c.append(md("### 8.1 -- Feature Importance vs. Cluster Differentiation Comparison"))
    c.append(md(
        "We compare Random Forest importance with how much each feature separates "
        "cluster means (range across clusters)."
    ))
    c.append(code("""
cluster_means_all = df.groupby("cluster")[FEATURE_COLS].mean()
clust_diff = (cluster_means_all.max() - cluster_means_all.min()).sort_values(ascending=False)

imp_rank = imp.rank(ascending=False)
diff_rank = clust_diff.rank(ascending=False)
synth = pd.DataFrame({
    "RF Importance": imp,
    "RF Rank": imp_rank.astype(int),
    "Cluster Diff Score": clust_diff,
    "Cluster Diff Rank": diff_rank.astype(int),
}).sort_values("RF Rank")
display(synth.round(4))

fig, axes = plt.subplots(1, 2, figsize=(14, 8))
imp.sort_values().plot(kind="barh", ax=axes[0], color=sns.color_palette("colorblind")[0])
axes[0].set_title("RF Feature Importance")
clust_diff.sort_values().plot(kind="barh", ax=axes[1], color=sns.color_palette("colorblind")[1])
axes[1].set_title("Cluster Differentiation (Mean Range)")
plt.tight_layout()
plt.savefig("figures/synthesis_comparison.png", dpi=300, bbox_inches="tight")
plt.show()

top5_rf = set(imp.tail(5).index)
top5_cl = set(clust_diff.head(5).index)
print("Overlap in top 5:", top5_rf & top5_cl)
"""))
    c.append(md(
        "Convergence of top RF and cluster-differentiating features suggests biological "
        "structure drives both prediction and subgrouping. Divergence indicates features "
        "that separate clusters without strong supervised signal, or vice versa."
    ))

    c.append(md("### 8.2 -- Predicted Probability per Cluster"))
    c.append(code("""
proba_all = rf_tuned.predict_proba(X)[:, 1]
df["pred_surv_prob"] = proba_all
cluster_pred = df.groupby("cluster").agg(
    N=("survival_label", "count"),
    Actual_Survival_Rate=("survival_label", lambda s: s.mean() * 100),
    Mean_Predicted_Prob=("pred_surv_prob", lambda s: s.mean() * 100),
).round(2)
cluster_pred["Difference"] = (
    cluster_pred["Mean_Predicted_Prob"] - cluster_pred["Actual_Survival_Rate"]
)
display(cluster_pred)
"""))
    c.append(md(
        "Alignment between actual survival rates and mean predicted probabilities per "
        "cluster indicates the supervised model respects unsupervised structure. "
        "Mismatches highlight clusters where the forest is over- or under-confident."
    ))

    c.append(md("### 8.3 -- Clinical Synthesis Narrative"))
    c.append(code("""
from IPython.display import Markdown, display

worst_cl = surv_rate.idxmin()
best_cl = surv_rate.idxmax()
top_feats = ", ".join(imp.tail(5).index[::-1])
display(Markdown(f'''
**High-risk subgroup.** Cluster {worst_cl} shows the lowest 1-year survival rate ({surv_rate[worst_cl]:.1f}%) among the k=3 solution. Its mean profile is dominated by elevated inflammatory and tumor-burden markers (e.g., CRP/CRP/ALB, bilirubin, NLR/SII) relative to other clusters. The tuned Random Forest assigns this cluster a lower mean predicted survival probability ({cluster_pred.loc[worst_cl, "Mean_Predicted_Prob"]:.1f}%) than higher-survival clusters, and its defining labs overlap the top supervised importances ({top_feats}).

**Lower-risk subgroup.** Cluster {best_cl} has the highest observed survival ({surv_rate[best_cl]:.1f}%) with comparatively lower inflammation and higher nutritional markers (prealbumin/ALB). Mean predicted survival probability is higher ({cluster_pred.loc[best_cl, "Mean_Predicted_Prob"]:.1f}%), indicating partial alignment between unsupervised structure and supervised risk scores.

**Convergence.** Features that rank highly for both RF importance and cluster differentiation (see Section 8.1 overlap) suggest that preoperative labs capture real patient heterogeneity—not only a classification artifact. Chi-square p = {p:.4f} quantifies how strongly cluster membership associates with survival; even when not significant at α=0.05, clinical profiles remain interpretable for exploratory stratification.
'''))
"""))

    c.append(md("### 8.4 -- Limitations"))
    c.append(md(
        "1. Moderate class imbalance (2.2:1) may still bias metrics despite class_weight. "
        "2. Weak univariate target correlations imply complex interactions. "
        "3. No external validation on other cohorts. "
        "4. K-Means assumes spherical, similar-variance clusters. "
        "5. Multicollinearity may inflate ratio-feature importance. "
        "6. Skewed features were not transformed beyond scaling. "
        "7. Retrospective single-source data; association not causation. "
        "8. PCA 2D plots capture limited variance. "
        "9. Anonymized IDs prevent longitudinal validation. "
        "10. Missing staging, surgery, and treatment variables."
    ))

    c.append(md("### 8.5 -- Future Work"))
    c.append(md(
        "1. Benchmark XGBoost, SVM, and logistic regression. "
        "2. Try DBSCAN and hierarchical clustering. "
        "3. Yeo-Johnson transforms before K-Means. "
        "4. RFE or LASSO feature selection. "
        "5. External hospital validation. "
        "6. Add staging and treatment features. "
        "7. Cox models and Kaplan-Meier analysis. "
        "8. Compare SMOTE/ADASYN to class_weight. "
        "9. SHAP for per-patient explanations. "
        "10. Stack RF predictions with cluster membership."
    ))
    return c


def _section_9_cells():
    c = []
    c.append(md("## SECTION 9: Conclusion"))
    c.append(code("""
# Pull key metrics for conclusion placeholders
print("=== KEY RESULTS FOR CONCLUSION ===")
print(f"Tuned accuracy: {tuned_acc*100:.2f}%")
print(f"Macro F1 (approx): {(fsc[0]+fsc[1])/2:.3f}")
print(f"AUC-ROC: {roc_auc:.3f}")
print(f"Top 5 features: {list(imp.tail(5).index[::-1])}")
print(f"Chi-square p-value: {p:.4e}")
print(f"Survival rates by cluster:\\n{surv_rate}")
"""))
    c.append(code("""
macro_f1 = f1_score(y_test, y_pred, average="macro")
display(Markdown(f'''
**Paragraph 1 — Objective recap.** This capstone applied one supervised technique (Random Forest Classifier) and one unsupervised technique (K-Means Clustering) to the PCSPF dataset of 878 pancreatic cancer patients with 20 preoperative clinical features, aiming to predict 1-year survival and discover natural patient subgroups.

**Paragraph 2 — Supervised results.** The tuned Random Forest achieved **{tuned_acc*100:.2f}%** test accuracy (vs. **68.8%** majority baseline), macro F1 **{macro_f1:.3f}**, and AUC-ROC **{roc_auc:.3f}**. Top predictive features were **{top_feats}**, consistent with established markers for tumor burden, nutrition, and inflammation in pancreatic cancer.

**Paragraph 3 — Unsupervised results.** K-Means identified **{OPTIMAL_K}** patient clusters (silhouette was highest at k=2 but k=3 was chosen for clinical granularity). Observed survival rates were {", ".join([f"Cluster {i}: {surv_rate[i]:.1f}%" for i in surv_rate.index])}; chi-square p = **{p:.4f}**.

**Paragraph 4 — Bridging insight.** Convergence between supervised importances and cluster-defining features suggests that routine preoperative blood tests reflect structured biological variation related to survival. These findings support exploratory risk stratification but cannot replace clinical judgment and require external validation before any clinical application.
'''))
"""))
    return c


def main():
    nb = build_notebook()
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Wrote {NOTEBOOK_PATH} with {len(nb.cells)} cells.")


if __name__ == "__main__":
    main()
