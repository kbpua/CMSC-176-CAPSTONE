# -*- coding: utf-8 -*-
"""Update notebook markdown cells after RF optimization."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "PCSPF_Data_Science_Capstone.ipynb"

CELL_143 = """### Overfitting Assessment

The primary **f1_macro** tuned model achieves **85.8% accuracy on the training set** versus **61.93% on the test set**, a gap of **23.8 percentage points**. This is still meaningful overfitting, but **substantially reduced** versus the legacy **`f1` (binary)** winner (**100% train / 71.02% test / 29 pp gap**).

**Why this happens:** Even with a regularized search grid, Random Forest can fit training noise when preoperative signal is weak (all feature-target |r| < 0.15). The legacy `f1` objective pushed toward deeper trees (depth=15, leaf=1) that memorized the 702 training patients.

**Why we still adopted f1_macro tuning:** Accuracy alone is misleading under 68.8% majority-class baseline. Macro-aligned tuning **improves test macro F1 (0.507 to 0.550)** and **class-0 recall (10.9% to 36.4%, 20/55)** at the cost of **test accuracy falling below baseline (61.93% vs 68.8%)**. That trade-off is documented honestly in the tuning comparison table (Section 7.2) and regularization analysis below."""

CELL_145 = """### Regularization Trade-Off Analysis

The table above demonstrates the unavoidable trade-off in this dataset:

| Direction | What improves | What worsens |
|---|---|---|
| Legacy `f1` tuning (depth=15) | Highest test accuracy (71.0%), highest AUC (0.613) | Severe overfitting (100% train), very low class-0 recall (10.9%) |
| **Primary `f1_macro` tuning (depth=5, leaf=4)** | **Better macro F1 (0.550), better class-0 recall (36.4%)**, smaller overfit gap (23.8 pp) | **Test accuracy below 68.8% baseline (61.9%)**, lower AUC (0.563) |
| Heavier manual regularization (depth=3) | Lowest overfit gap (~11 pp), class-0 recall up to ~51% | Accuracy drops further (~61%), AUC ~0.564 |

**Decision: Retain the f1_macro tuned model as the primary model** for four reasons:
1. **Tuning metric aligns with evaluation** - we report macro F1 and class-0 recall in defense materials, not binary F1 on class 1.
2. **Improved minority-class detection** - 20/55 high-risk patients flagged vs 6/55 under legacy `f1` tuning (still clinically insufficient alone).
3. **Reduced overfitting** - 85.8% train vs 100% train documents a more honest generalization profile.
4. **Feature importance stability** - top features (CA19-9, CEA, Prealbumin, CRP/ALB, BMI) remain clinically coherent across tuning objectives and regularization levels.

The regularization analysis confirms that the weak preoperative signal - not only the model configuration - is the binding constraint on performance."""

CELL_146 = """### Clinical Interpretation of the Confusion Matrix

The confusion matrix reveals both progress and limits after macro-aligned tuning:

- **Class 0 (survived < 1 year):** Of 55 actual high-risk patients in the test set, the model correctly identifies **20 (36.4% recall)** - up from **6 (10.9%)** under legacy `f1` tuning. It still misses **35** patients who will die within a year.
- **Class 1 (survived >= 1 year):** Of 121 actual survivors, the model correctly identifies most low-risk patients, but with more false alarms than the legacy model (trade-off from prioritizing macro balance).

**What this means clinically:** The model is still imperfect for screening, but **macro-aligned tuning materially improves high-risk detection** relative to both the majority baseline (0/55) and the legacy tuned model (6/55). It remains **research-grade, not deployment-ready**.

**Why accuracy dropped below 68.8%:** Predicting survival for every patient (majority-class baseline) yields high accuracy but **zero** high-risk detection. Optimizing macro F1 shifts predictions toward the minority class - the correct trade-off for an imbalanced medical classification problem when both classes matter.

**Context against benchmarks:** SVM RBF still achieves higher macro F1 (0.590) and class-0 recall (56.4%, 31/55) on the same split. Random Forest is retained for **Gini feature importance** (Section 8), not because it wins every metric."""

SYNTHESIS_CELL = """**Ranking comparison (Section 8.1).** Random Forest Gini importance and cluster mean-range differentiation use different metrics and answer different questions. On this cohort, **only CRP/ALB overlaps in the top-5 of both lists** (notebook output: `Overlap in top 5: {'CRP/ALB'}`).

| Feature | RF rank | Cluster diff rank |
|---------|---------|-------------------|
| CA19-9 | 1 | 15 |
| CEA | 2 | 20 (lowest) |
| Prealbumin | 3 | 9 |
| CRP/ALB | 4 | 2 |
| CRP | 10 | 1 |

**Correct reading:** Partial convergence at the clinical-theme level (tumor burden, nutrition, inflammation), **not** identical feature rankings. Tumor markers dominate supervised prediction; inflammatory/hepatobiliary markers dominate unsupervised phenotypes. Do not claim CA19-9 or CEA "define" clusters - the chart shows the opposite."""

CONVERGENCE_PARA = """**Partial convergence.** Only CRP/ALB ranks in both top-5 lists. RF and K-Means weight different markers because prediction and phenotype grouping are different tasks. Together they still support a coherent clinical story about tumor burden, nutrition, and inflammation - without implying the same features drive both analyses equally."""

CELL_153 = """### 7.5 Model Comparison: Benchmarking Random Forest Against Alternatives

To validate our model choice, we benchmarked the **f1_macro tuned** Random Forest against three alternatives - Logistic Regression, SVM RBF, and Gradient Boosting - on the same train-test split with the same random seed.

**All models perform within the same weak-signal band.** No model crosses the 0.7 AUC threshold commonly cited for clinical utility. SVM RBF leads on macro F1 (0.590) and AUC (0.622). Our tuned RF (0.550 macro F1, 0.563 AUC) is **competitive with Logistic Regression (0.539)** and **better on macro F1 than Gradient Boosting (0.482)**, while improving class-0 recall versus the legacy RF configuration.

**SVM RBF achieves the best balanced performance** with the highest macro F1 and strong class-0 recall (56.4%, 31/55). Logistic Regression achieves the highest class-0 recall (61.8%, 34/55) but lower test accuracy (55.1%). Neither provides built-in feature importance - essential for Section 8 synthesis.

**Random Forest overfitting is reduced but not eliminated** after f1_macro tuning (85.8% train vs 61.9% test). Legacy `f1` tuning had reached 100% train accuracy with depth=15.

**Why Random Forest was retained as the primary model despite SVM's higher macro F1:**

1. **Feature importance is essential for this project.** Section 8 depends on comparing RF Gini rankings against K-Means cluster differentiation.
2. **Macro-aligned tuning improved RF balance metrics** versus the original `f1` objective (macro F1 0.507 to 0.550; class-0 recall 10.9% to 36.4%).
3. **Interpretability for a Fundamentals course** - tree ensembles and Gini importance are defensible without SHAP.
4. **Feature importance stability** - top predictive features remain consistent across tuning objectives.

**Conclusion:** Random Forest was chosen for **interpretability and synthesis**, not the highest benchmark score. Optimization with `f1_macro` made that choice more metric-aligned without pretending the weak-signal ceiling disappeared."""


def main():
    nb = json.loads(NB_PATH.read_text(encoding="utf-8"))
    updates = {143: CELL_143, 145: CELL_145, 146: CELL_146, 153: CELL_153}
    for idx, text in updates.items():
        cell = nb["cells"][idx]
        cell["source"] = [line + "\n" for line in text.split("\n")]
        if cell["source"] and cell["source"][-1] == "\n":
            cell["source"].pop()
        cell.pop("outputs", None)
        cell.pop("execution_count", None)

    for cell in nb["cells"]:
        src = "".join(cell.get("source", []))
        if "reinforces the supervised model's modest AUC (0.613)" in src:
            cell["source"] = [
                line.replace("AUC (0.613)", "AUC (0.563)")
                for line in cell["source"]
            ]
        if src.strip() == (
            "Convergence of top RF and cluster-differentiating features suggests biological "
            "structure drives both prediction and subgrouping. Divergence indicates features "
            "that separate clusters without strong supervised signal, or vice versa."
        ):
            cell["source"] = [SYNTHESIS_CELL + "\n"]
        if "**Convergence.** Features that rank highly for both RF importance and cluster differentiation" in src:
            cell["source"] = [
                CONVERGENCE_PARA + "\n" if "**Convergence.**" in line else line
                for line in cell["source"]
            ]
        if "Paragraph 4" in src and "Bridging insight" in src and "Convergence between supervised importances" in src:
            cell["source"] = [
                "**Paragraph 4 - Bridging insight.** Partial convergence (CRP/ALB in both top-5 lists; shared clinical themes of tumor burden, nutrition, and inflammation) suggests preoperative labs capture structured biological variation - even though RF and clustering rank different markers highest. These findings support exploratory risk stratification but cannot replace clinical judgment and require external validation before any clinical application.\n"
                if "Bridging insight" in line and "Convergence between" in line else line
                for line in cell["source"]
            ]

    NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Updated notebook markdown cells 143, 145, 146, 153 and Section 8 synthesis text")


if __name__ == "__main__":
    main()
