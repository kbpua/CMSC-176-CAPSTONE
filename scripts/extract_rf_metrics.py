"""Fix invalid markdown cell fields and extract RF metrics from executed notebook."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "PCSPF_Data_Science_Capstone.ipynb"


def clean_markdown_cells(nb):
    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            cell.pop("execution_count", None)
            cell.pop("outputs", None)


def extract_metrics(nb):
    text = json.dumps(nb["cells"], ensure_ascii=False)
    metrics = {}

    # Primary model selection from cell 134 output
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell.get("source", []))
        if "PRIMARY MODEL SELECTED" not in src:
            continue
        out = "".join(
            o.get("text", "") if isinstance(o.get("text"), str) else "".join(o.get("text", []))
            for o in cell.get("outputs", [])
            if o.get("output_type") == "stream"
        )
        if "Best params:" in out:
            m = re.search(r"Best params: (\{[^}]+\})", out)
            if m:
                metrics["best_params"] = m.group(1)
            m = re.search(r"Best CV macro F1: ([0-9.]+)", out)
            if m:
                metrics["cv_macro_f1"] = m.group(1)

    # Test metrics from cell 140
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell.get("source", []))
        if "Tuned model accuracy:" in src and "classification_report.png" in src:
            out = "".join(
                o.get("text", "") if isinstance(o.get("text"), str) else "".join(o.get("text", []))
                for o in cell.get("outputs", [])
                if o.get("output_type") == "stream"
            )
            for pat, key in [
                (r"Tuned model accuracy: ([0-9.]+)%", "test_acc"),
                (r"Improvement over baseline: \+([0-9.]+) pp", "baseline_improvement_pp"),
            ]:
                m = re.search(pat, out)
                if m:
                    metrics[key] = m.group(1)

    # Overfit from cell 142
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell.get("source", []))
        if "OVERFITTING ASSESSMENT" in src:
            out = "".join(
                o.get("text", "") if isinstance(o.get("text"), str) else "".join(o.get("text", []))
                for o in cell.get("outputs", [])
                if o.get("output_type") == "stream"
            )
            m = re.search(r"Accuracy \(%\)\s+([0-9.]+)%\s+([0-9.]+)%\s+([+-][0-9.]+) pp", out)
            if m:
                metrics["train_acc"] = m.group(1)
                metrics["test_acc_overfit"] = m.group(2)
                metrics["overfit_gap"] = m.group(3).replace("+", "")
            m = re.search(r"Macro F1\s+([0-9.]+)\s+([0-9.]+)", out)
            if m:
                metrics["macro_f1_train"] = m.group(1)
                metrics["macro_f1"] = m.group(2)
            m = re.search(r"AUC-ROC\s+([0-9.]+)\s+([0-9.]+)", out)
            if m:
                metrics["auc"] = m.group(2)

    # Class-0 recall from reg or comp output
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell.get("source", []))
        if "Primary tuned (f1_macro)" in src and "REGULARIZATION TRADE-OFF" in src:
            out = "".join(
                o.get("text", "") if isinstance(o.get("text"), str) else "".join(o.get("text", []))
                for o in cell.get("outputs", [])
                if o.get("output_type") == "stream"
            )
            m = re.search(
                r"Primary tuned \(f1_macro\):[^\n]+\s+([0-9.]+)%\s+([0-9.]+)%\s+([0-9.]+) pp\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+% \([0-9]+/[0-9]+\))",
                out,
            )
            if m:
                metrics["primary_train_acc"] = m.group(1)
                metrics["primary_test_acc"] = m.group(2)
                metrics["primary_gap"] = m.group(3)
                metrics["primary_macro_f1"] = m.group(4)
                metrics["primary_auc"] = m.group(5)
                metrics["class0_recall"] = m.group(6)

    # Tuning comparison legacy row
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell.get("source", []))
        if "grid_f1_legacy" in src:
            out = "".join(
                o.get("text", "") if isinstance(o.get("text"), str) else "".join(o.get("text", []))
                for o in cell.get("outputs", [])
                if o.get("output_type") == "stream"
            )
            m = re.search(r"Reference: scoring='f1'.*?Best CV score \(f1\): ([0-9.]+)", out, re.S)
            if m:
                metrics["legacy_cv_f1_binary"] = m.group(1)

    return metrics


def main():
    nb = json.loads(NB_PATH.read_text(encoding="utf-8"))
    clean_markdown_cells(nb)
    metrics = extract_metrics(nb)
    NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

    out_path = ROOT / "scripts" / "_rf_metrics.json"
    out_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
