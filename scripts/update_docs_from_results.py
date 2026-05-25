# -*- coding: utf-8 -*-
"""Bulk-update documentation files with post-optimization metrics."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = [
    ("71.02%", "61.93%"),
    ("71.0%", "61.9%"),
    ("+2.27 pp", "-6.87 pp"),
    ("(+2.27 pp vs baseline)", "(macro F1 trade-off vs 68.8% baseline)"),
    ("AUC = 0.613", "AUC = 0.563"),
    ("AUC 0.613", "AUC 0.563"),
    ("AUC-ROC 0.613", "AUC-ROC 0.563"),
    ("AUC-ROC (test)\", \"0.613\"", "AUC-ROC (test)\", \"0.563\""),
    ("macro F1 0.507", "macro F1 0.550"),
    ("Macro F1 0.507", "Macro F1 0.550"),
    ("Macro F1 (test)\", \"0.507\"", "Macro F1 (test)\", \"0.550\""),
    ("Macro F1\", \"0.507\"", "Macro F1\", \"0.550\""),
    ("0.507", "0.550"),  # careful - may over-replace
    ("10.9% (6/55)", "36.4% (20/55)"),
    ("10.9% (6 / 55", "36.4% (20 / 55"),
    ("Class-0 recall\", \"10.9%", "Class-0 recall\", \"36.4%"),
    ("100% train", "85.8% train"),
    ("100.0%", "85.8%"),
    ("29 pp", "23.8 pp"),
    ("29.0 pp", "23.8 pp"),
    ("scoring='f1'", "scoring='f1_macro'"),
    ("scoring=\"f1\"", "scoring=\"f1_macro\""),
    ("f1 (binary / positive class)", "f1_macro (primary)"),
    ("f1 (binary / class 1)", "f1_macro (primary)"),
    ("CV F1 (GridSearch, binary)\", \"~0.809\"", "CV macro F1 (GridSearch)\", \"0.579\""),
    ("CV F1 ~0.809", "CV macro F1 0.579"),
    ("~0.809", "0.579"),
    ("max_depth=15, min_samples_leaf=1", "max_depth=5, min_samples_leaf=4"),
    ("n_estimators=300, max_depth=15", "n_estimators=100, max_depth=5"),
    ("CEA, Prealbumin, CA19-9", "CA19-9, CEA, Prealbumin"),
]

# Files where blanket 0.507 -> 0.550 is unsafe
SKIP_BROAD = {
    ROOT / "scripts" / "capstone_results.py",
    ROOT / "scripts" / "update_docs_from_results.py",
    ROOT / "PCSPF_Data_Science_Capstone.ipynb",
}

TARGETS = [
    ROOT / "scripts" / "study_guide_content.py",
    ROOT / "scripts" / "study_guide_figures.py",
    ROOT / "scripts" / "presentation_outline_data.py",
    ROOT / "scripts" / "audit_content.py",
    ROOT / "scripts" / "generate_audit_documentation.py",
]


def apply_replacements(text, path):
    for old, new in REPLACEMENTS:
        if old == "0.507" and "0.507" in text:
            # only replace standalone metric 0.507 in doc strings, keep legacy references
            text = text.replace("macro F1 0.507", "macro F1 0.550")
            text = text.replace("Macro F1 0.507", "Macro F1 0.550")
            text = text.replace('"0.507"', '"0.550"')
            text = text.replace("'0.507'", "'0.550'")
            text = text.replace("0.5070", "0.5500")
            continue
        text = text.replace(old, new)
    return text


def main():
    for path in TARGETS:
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        updated = apply_replacements(original, path)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"Updated {path.name}")


if __name__ == "__main__":
    main()
