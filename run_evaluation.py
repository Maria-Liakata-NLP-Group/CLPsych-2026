"""Entry point to run evaluation for all CLPsych 2026 tasks (v8).

v7 changes from v6:
- Task 1.1 ranking simplified: t1_1_rank = subelement classification Avg Macro F1
  (previously averaged element presence and subelement classification)

v6 changes from v5:
- Added 3 ranking keys: t1_1_rank, t1_2_rank, t2_rank

v5 changes from v4:
- Output format: scores.txt (Codabench format) instead of JSON
- All metric key names shortened to <=36 characters
- Key naming convention: t1ep/t1sc/t1pr/t2pl/t2tl prefixes with abbreviations

Key name abbreviations:
    t1 = Task 1, t2 = Task 2
    ep = element presence, sc = subelement classification, pr = presence rating
    pl = post-level, tl = timeline-level
    ada = adaptive, mal = maladaptive, avg = average, comb = combined
    maF1 = macro F1, miF1 = micro F1
    prec = precision, rec = recall, sup = support
    sw = Switch, esc = Escalation
"""

import argparse
import json
import os
import sys

import numpy as np

import evaluate_task1
import evaluate_task2


# ---- Key name abbreviation mappings ----

VALENCE_SHORT = {
    "adaptive-state": "ada",
    "maladaptive-state": "mal",
    "combined": "comb",
}

ELEM_SHORT = {
    "A": "A", "B-O": "BO", "B-S": "BS",
    "C-O": "CO", "C-S": "CS", "D": "D",
}

LABEL_SHORT = {
    "Switch": "sw",
    "Escalation": "esc",
}

METRIC_SHORT = {
    "precision": "prec",
    "recall": "rec",
    "support": "sup",
    "spearman": "spear",
    "num_timelines": "n_tl",
    "support_positive": "sup_pos",
    "support_total": "sup_tot",
}

# Aggregate F1 keys (used in both element_presence and subelement_classification)
AGG_F1_SHORT = {
    "adaptive_macro_f1": "ada_maF1",
    "adaptive_micro_f1": "ada_miF1",
    "maladaptive_macro_f1": "mal_maF1",
    "maladaptive_micro_f1": "mal_miF1",
    "avg_macro_f1": "avg_maF1",
    "avg_micro_f1": "avg_miF1",
    "macro_f1": "maF1",
    "micro_f1": "miF1",
}


def flatten_results(all_results):
    """Convert nested results dict to flat dict with short key names (<=36 chars).

    See SCORES_KEY.md for the full key reference.
    """
    flat = {}

    # --- Task 1 ---
    if "task1" in all_results:
        t1 = all_results["task1"]
        t11 = t1.get("task1_1", {})

        # Task 1.1 Element Presence — per element
        ep = t11.get("element_presence", {})
        for label, m in ep.get("per_element", {}).items():
            val, elem = label.split(":")
            v = VALENCE_SHORT[val]
            e = ELEM_SHORT[elem]
            for metric, value in m.items():
                ms = METRIC_SHORT.get(metric, metric)
                flat["t1ep_%s_%s_%s" % (v, e, ms)] = value

        # Task 1.1 Element Presence — aggregates
        for agg_key, short in AGG_F1_SHORT.items():
            if agg_key in ep:
                flat["t1ep_%s" % short] = ep[agg_key]

        # Task 1.1 Subelement Classification — per element
        sc = t11.get("subelement_classification", {})
        for label, m in sc.get("per_element", {}).items():
            val, elem = label.split(":")
            v = VALENCE_SHORT[val]
            e = ELEM_SHORT[elem]
            for metric, value in m.items():
                if metric == "macro_f1":
                    ms = "maF1"
                elif metric == "micro_f1":
                    ms = "miF1"
                else:
                    ms = METRIC_SHORT.get(metric, metric)
                flat["t1sc_%s_%s_%s" % (v, e, ms)] = value

        # Task 1.1 Subelement Classification — aggregates
        for agg_key, short in AGG_F1_SHORT.items():
            if agg_key in sc:
                flat["t1sc_%s" % short] = sc[agg_key]

        # Task 1.2 Presence Rating
        t12 = t1.get("task1_2", {})
        for valence_key in ["adaptive-state", "maladaptive-state", "combined"]:
            if valence_key not in t12:
                continue
            v = VALENCE_SHORT[valence_key]
            m = t12[valence_key]
            for metric, value in m.items():
                ms = METRIC_SHORT.get(metric, metric)
                flat["t1pr_%s_%s" % (v, ms)] = value

    # --- Task 2 ---
    if "task2" in all_results:
        t2 = all_results["task2"]

        # Post-level
        pl = t2.get("post_level", {})
        for label in ["Switch", "Escalation"]:
            if label not in pl:
                continue
            ls = LABEL_SHORT[label]
            m = pl[label]
            for metric, value in m.items():
                ms = METRIC_SHORT.get(metric, metric)
                flat["t2pl_%s_%s" % (ls, ms)] = value
        if "macro_f1" in pl:
            flat["t2pl_maF1"] = pl["macro_f1"]

        # Timeline-level
        tl = t2.get("timeline_level", {})
        for label in ["Switch", "Escalation"]:
            if label not in tl:
                continue
            ls = LABEL_SHORT[label]
            m = tl[label]
            for metric, value in m.items():
                ms = METRIC_SHORT.get(metric, metric)
                flat["t2tl_%s_%s" % (ls, ms)] = value
        if "macro_f1" in tl:
            flat["t2tl_maF1"] = tl["macro_f1"]

        # Combined
        if "combined_macro_f1" in t2:
            flat["t2_comb_maF1"] = t2["combined_macro_f1"]

    # --- Ranking keys (one per task) ---
    # Task 1.1: subelement classification Avg Macro F1
    if "t1sc_avg_maF1" in flat:
        flat["t1_1_rank"] = flat["t1sc_avg_maF1"]

    # Task 1.2: avg of adaptive RMSE and maladaptive RMSE
    if "t1pr_ada_rmse" in flat and "t1pr_mal_rmse" in flat:
        flat["t1_2_rank"] = (flat["t1pr_ada_rmse"] + flat["t1pr_mal_rmse"]) / 2.0

    # Task 2: same as combined macro F1 (avg of post-level + timeline-level macro F1)
    if "t2_comb_maF1" in flat:
        flat["t2_rank"] = flat["t2_comb_maF1"]

    return flat


def format_value(value):
    """Format a value for scores.txt output."""
    if isinstance(value, (np.integer,)):
        return str(int(value))
    if isinstance(value, (np.floating, float)):
        return str(float(value))
    if isinstance(value, np.ndarray):
        return str(value.tolist())
    return str(value)


def write_scores_txt(flat, output_path):
    """Write flat results dict to scores.txt format (Codabench).

    Format: one metric per line, "key: value"
    """
    with open(output_path, "w") as f:
        for key in sorted(flat.keys()):
            f.write("%s: %s\n" % (key, format_value(flat[key])))


def main():
    parser = argparse.ArgumentParser(
        description="CLPsych 2026 Shared Task Evaluation (v5)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Both tasks — scores.txt output (Codabench format)
  python run_evaluation.py --gold-dir ../fulldata/train/ \\
      --task1-pred task1_pred.json --task2-pred task2_pred.json \\
      --output scores.txt

  # Also save nested JSON for debugging
  python run_evaluation.py --gold-dir ../fulldata/train/ \\
      --task1-pred task1_pred.json --task2-pred task2_pred.json \\
      --output scores.txt --json-output results.json
""",
    )
    parser.add_argument("--gold-dir", required=True,
                        help="Directory with gold JSON timeline files")
    parser.add_argument("--task1-pred",
                        help="Task 1 prediction JSON file")
    parser.add_argument("--task2-pred",
                        help="Task 2 prediction JSON file")
    parser.add_argument("--output",
                        help="Output scores.txt file (Codabench format)")
    parser.add_argument("--json-output",
                        help="Optional: also save nested JSON results")
    args = parser.parse_args()

    if not args.task1_pred and not args.task2_pred:
        parser.error("At least one of --task1-pred or --task2-pred is required")

    all_results = {}

    # --- Task 1 ---
    if args.task1_pred:
        if os.path.isfile(args.task1_pred):
            print("\n" + "#" * 70)
            print("# TASK 1 EVALUATION")
            print("#" * 70)
            all_results["task1"] = evaluate_task1.evaluate(
                args.gold_dir, args.task1_pred)
        else:
            print("\n[Task 1] Prediction file not found: %s — skipping." % args.task1_pred)

    # --- Task 2 ---
    if args.task2_pred:
        if os.path.isfile(args.task2_pred):
            print("\n" + "#" * 70)
            print("# TASK 2 EVALUATION")
            print("#" * 70)
            all_results["task2"] = evaluate_task2.evaluate(
                args.gold_dir, args.task2_pred)
        else:
            print("\n[Task 2] Prediction file not found: %s — skipping." % args.task2_pred)

    if not all_results:
        print("\nNo valid prediction files found. Nothing to evaluate.")
        sys.exit(1)

    # Flatten to short keys
    flat = flatten_results(all_results)

    # Validate key lengths
    over_limit = [k for k in flat if len(k) > 36]
    if over_limit:
        print("\nWARNING: %d keys exceed the 36-char limit:" % len(over_limit))
        for k in over_limit:
            print("  '%s' (%d chars)" % (k, len(k)))

    # Write scores.txt (Codabench format)
    if args.output:
        write_scores_txt(flat, args.output)
        print("\nScores saved to %s (%d metrics)" % (args.output, len(flat)))

    # Optionally save nested JSON
    if args.json_output:
        def convert(obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        with open(args.json_output, "w") as f:
            json.dump(all_results, f, indent=2, default=convert)
        print("Nested JSON saved to %s" % args.json_output)


if __name__ == "__main__":
    main()
