# -*- coding: utf-8 -*-
"""Patch Section 7.2+ for f1_macro tuning optimization."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "PCSPF_Data_Science_Capstone.ipynb"

CELL_133 = """GridSearchCV compares three tuning objectives on the same stratified 5-fold split:

1. **`f1` (binary, legacy grid)** - original approach; optimizes majority-class F1 for reference.
2. **`f1_macro` (primary, regularized grid)** - aligns tuning with our test evaluation metric under class imbalance.
3. **`recall_macro` (stretch, regularized grid)** - explores whether maximizing average recall improves high-risk detection.

The primary model (`rf_tuned`) is the **`f1_macro`** winner. The regularized grid raises the floor on leaf/split constraints and removes unbounded depth to reduce overfitting."""

CELL_134 = """from sklearn.model_selection import cross_val_score
from sklearn.metrics import roc_auc_score

LEGACY_PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "max_depth": [None, 10, 15, 20],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
}

REGULARIZED_PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "max_depth": [5, 7, 10, 12, 15],
    "min_samples_split": [5, 10, 20],
    "min_samples_leaf": [2, 4, 8],
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)


def _test_metrics(model):
    y_tr_pred = model.predict(X_train)
    y_te_pred = model.predict(X_test)
    y_te_proba = model.predict_proba(X_test)[:, 1]
    cm = confusion_matrix(y_test, y_te_pred)
    rec_0 = cm[0, 0] / cm[0].sum()
    train_acc = accuracy_score(y_train, y_tr_pred) * 100
    test_acc = accuracy_score(y_test, y_te_pred) * 100
    return {
        "train_acc": train_acc,
        "test_acc": test_acc,
        "gap_pp": train_acc - test_acc,
        "macro_f1": f1_score(y_test, y_te_pred, average="macro"),
        "auc": roc_auc_score(y_test, y_te_proba),
        "class0_recall": rec_0,
        "class0_recall_str": f"{rec_0:.1%} ({cm[0, 0]}/{cm[0].sum()})",
        "best_params": model.get_params(),
    }


def run_grid_search(scoring, param_grid, label):
    grid = GridSearchCV(
        RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE),
        param_grid=param_grid,
        cv=cv,
        scoring=scoring,
        n_jobs=-1,
        return_train_score=True,
    )
    grid.fit(X_train, y_train)
    metrics = _test_metrics(grid.best_estimator_)
    print(f"\\n{label}")
    print(f"  Best params: {grid.best_params_}")
    print(f"  Best CV score ({scoring}): {grid.best_score_:.4f}")
    print(
        f"  Test: acc={metrics['test_acc']:.1f}%, macro F1={metrics['macro_f1']:.3f}, "
        f"AUC={metrics['auc']:.3f}, class-0 recall={metrics['class0_recall_str']}"
    )
    return grid, metrics


print("=" * 90)
print("RANDOM FOREST TUNING COMPARISON - same train/test split, seed=42")
print("=" * 90)

grid_f1_legacy, metrics_f1_legacy = run_grid_search(
    "f1", LEGACY_PARAM_GRID, "Reference: scoring='f1' (binary) + legacy grid"
)
grid_f1_macro, metrics_f1_macro = run_grid_search(
    "f1_macro", REGULARIZED_PARAM_GRID, "Primary: scoring='f1_macro' + regularized grid"
)
grid_recall_macro, metrics_recall_macro = run_grid_search(
    "recall_macro", REGULARIZED_PARAM_GRID, "Stretch: scoring='recall_macro' + regularized grid"
)

tuning_comparison_rows = []
for label, grid, metrics in [
    ("f1 (binary, legacy grid)", grid_f1_legacy, metrics_f1_legacy),
    ("f1_macro (primary, regularized grid)", grid_f1_macro, metrics_f1_macro),
    ("recall_macro (stretch, regularized grid)", grid_recall_macro, metrics_recall_macro),
]:
    tuning_comparison_rows.append(
        {
            "Tuning objective": label,
            "Best CV score": f"{grid.best_score_:.4f}",
            "Best params": str(grid.best_params_),
            "Train acc": f"{metrics['train_acc']:.1f}%",
            "Test acc": f"{metrics['test_acc']:.1f}%",
            "Overfit gap": f"{metrics['gap_pp']:.1f} pp",
            "Test macro F1": f"{metrics['macro_f1']:.3f}",
            "Test AUC": f"{metrics['auc']:.3f}",
            "Class-0 recall": metrics["class0_recall_str"],
        }
    )

tuning_comparison_df = pd.DataFrame(tuning_comparison_rows)
print("\\n" + "=" * 90)
print("TUNING OBJECTIVE COMPARISON (held-out test set)")
print("=" * 90)
display(tuning_comparison_df)

grid = grid_f1_macro
rf_tuned = grid.best_estimator_
primary_metrics = metrics_f1_macro

print("\\nPRIMARY MODEL SELECTED: f1_macro tuned Random Forest")
print("Best params:", grid.best_params_)
print(f"Best CV macro F1: {grid.best_score_:.4f}")
"""

CELL_135 = """**Threshold sweep (exploratory).** Default classification uses probability threshold 0.5. Lower thresholds trade overall accuracy for higher class-0 recall - useful for discussion, not deployed as the primary metric."""

CELL_136 = """# Exploratory decision-threshold sweep on the primary (f1_macro) model
y_proba_primary = rf_tuned.predict_proba(X_test)[:, 1]
thresholds = np.arange(0.20, 0.81, 0.05)
threshold_rows = []

for threshold in thresholds:
    y_pred_t = (y_proba_primary >= threshold).astype(int)
    cm_t = confusion_matrix(y_test, y_pred_t)
    rec_0 = cm_t[0, 0] / cm_t[0].sum()
    rec_1 = cm_t[1, 1] / cm_t[1].sum()
    threshold_rows.append(
        {
            "Threshold": threshold,
            "Test Acc": f"{accuracy_score(y_test, y_pred_t) * 100:.1f}%",
            "Macro F1": f"{f1_score(y_test, y_pred_t, average='macro'):.3f}",
            "Class-0 Recall": f"{rec_0:.1%} ({cm_t[0, 0]}/{cm_t[0].sum()})",
            "Class-1 Recall": f"{rec_1:.1%} ({cm_t[1, 1]}/{cm_t[1].sum()})",
        }
    )

threshold_df = pd.DataFrame(threshold_rows)
print("=" * 90)
print("THRESHOLD SWEEP - primary f1_macro model (test set, exploratory)")
print("Default threshold = 0.50 used for all primary metrics in Sections 7.3-9")
print("=" * 90)
display(threshold_df)

best_thresh_row = threshold_df.loc[threshold_df["Macro F1"].astype(float).idxmax()]
print(
    f"\\nBest test macro F1 in sweep: {best_thresh_row['Macro F1']} at threshold "
    f"{best_thresh_row['Threshold']} (exploratory only - not re-tuned on test)"
)
"""

CELL_137 = """### Tuning Optimization Summary

We retuned Random Forest after recognizing that the original **`scoring='f1'`** objective optimizes **binary F1 on class 1** (the majority survived >= 1 year), which can look strong in CV while **macro F1 on the test set stays modest**.

**What changed:**
- **Primary tuning** now uses **`scoring='f1_macro'`** with a **regularized grid** (no unbounded depth; higher min leaf/split floors).
- **Reference row** keeps the legacy **`f1` + original grid** for before/after comparison.
- **Stretch row** adds **`recall_macro`** on the same regularized grid to probe high-risk recall.

**What to expect:** Macro-aligned tuning should **reduce the train-test gap** and **improve class-0 recall** versus the legacy `f1` winner, but **will not eliminate** the weak-signal ceiling (all feature-target |r| < 0.15). SVM may still lead on macro F1/AUC in Section 7.5; Random Forest remains primary for **Gini feature importance** and Section 8 synthesis."""

CELL_144 = """# Regularization comparison - demonstrating the overfitting trade-off
primary_params = {
    k: rf_tuned.get_params()[k]
    for k in ["n_estimators", "max_depth", "min_samples_split", "min_samples_leaf"]
}

reg_configs = [
    (
        f"Primary tuned (f1_macro): depth={primary_params['max_depth']}, leaf={primary_params['min_samples_leaf']}",
        primary_params,
    ),
    ("Moderate (depth=7, leaf=10)", {"n_estimators": 300, "max_depth": 7, "min_samples_split": 10, "min_samples_leaf": 10}),
    ("Heavy (depth=5, leaf=20)", {"n_estimators": 300, "max_depth": 5, "min_samples_split": 20, "min_samples_leaf": 20}),
    ("Very heavy (depth=3, leaf=30)", {"n_estimators": 300, "max_depth": 3, "min_samples_split": 30, "min_samples_leaf": 30}),
    (
        "Legacy f1 winner (depth=15, leaf=1)",
        {"n_estimators": 300, "max_depth": 15, "min_samples_split": 2, "min_samples_leaf": 1},
    ),
]

reg_results = []
for name, params in reg_configs:
    rf_reg = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE, **params)
    rf_reg.fit(X_train, y_train)

    y_tr_pred = rf_reg.predict(X_train)
    y_te_pred = rf_reg.predict(X_test)
    y_te_proba = rf_reg.predict_proba(X_test)[:, 1]

    tr_acc = accuracy_score(y_train, y_tr_pred) * 100
    te_acc = accuracy_score(y_test, y_te_pred) * 100
    te_f1m = f1_score(y_test, y_te_pred, average="macro")
    te_auc = roc_auc_score(y_test, y_te_proba)
    cm_reg = confusion_matrix(y_test, y_te_pred)
    rec_0 = cm_reg[0, 0] / cm_reg[0].sum()

    reg_results.append(
        {
            "Configuration": name,
            "Train Acc": f"{tr_acc:.1f}%",
            "Test Acc": f"{te_acc:.1f}%",
            "Gap": f"{tr_acc - te_acc:.1f} pp",
            "Macro F1": f"{te_f1m:.3f}",
            "AUC": f"{te_auc:.3f}",
            "Class-0 Recall": f"{rec_0:.1%} ({cm_reg[0, 0]}/{cm_reg[0].sum()})",
        }
    )

reg_df = pd.DataFrame(reg_results)
print("=" * 100)
print("REGULARIZATION TRADE-OFF ANALYSIS")
print("=" * 100)
print(reg_df.to_string(index=False))
print(f"\\nMajority-class baseline accuracy: 68.8%")
"""


def set_cell_source(nb, idx, source_text):
    cell = nb["cells"][idx]
    cell["source"] = [line + "\n" for line in source_text.split("\n")]
    if cell["source"] and cell["source"][-1] == "\n":
        cell["source"].pop()
    if cell["cell_type"] == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    else:
        cell.pop("outputs", None)
        cell.pop("execution_count", None)


def patch_cell_151(nb):
    src = "".join(nb["cells"][151]["source"])
    if "primary_rf_params" not in src:
        insert_at = src.index("# Define models")
        rf_params_block = (
            "primary_rf_params = {\n"
            "    k: rf_tuned.get_params()[k]\n"
            '    for k in ["n_estimators", "max_depth", "min_samples_split", "min_samples_leaf", "class_weight", "random_state"]\n'
            "}\n\n"
        )
        src = src[:insert_at] + rf_params_block + src[insert_at:]
    old_model = (
        "        'model': RandomForestClassifier(n_estimators=300, max_depth=15, min_samples_split=2,\n"
        "                                         min_samples_leaf=1, class_weight='balanced',\n"
        "                                         random_state=RANDOM_STATE),"
    )
    new_model = "        'model': RandomForestClassifier(**primary_rf_params),"
    if old_model in src:
        src = src.replace(old_model, new_model)
    nb["cells"][151]["source"] = [line + "\n" for line in src.split("\n")]
    if nb["cells"][151]["source"] and nb["cells"][151]["source"][-1] == "\n":
        nb["cells"][151]["source"].pop()
    nb["cells"][151]["outputs"] = []
    nb["cells"][151]["execution_count"] = None


def main():
    nb = json.loads(NB_PATH.read_text(encoding="utf-8"))
    set_cell_source(nb, 133, CELL_133)
    set_cell_source(nb, 134, CELL_134)
    set_cell_source(nb, 135, CELL_135)
    set_cell_source(nb, 136, CELL_136)
    set_cell_source(nb, 137, CELL_137)
    set_cell_source(nb, 144, CELL_144)
    patch_cell_151(nb)
    NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Patched {NB_PATH}")


if __name__ == "__main__":
    main()
