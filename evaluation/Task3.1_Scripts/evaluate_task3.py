"""Evaluation for Task 3.1 — Sequence Summary.

Standalone evaluation script for the CLPsych 2026 Task 3 Codabench page.
Separate from Task 1/2 evaluation (different dependencies).

Metrics:
  CS: Mean NLI consistency score, 1 - mean contradiction (higher = better)
  CT: Max NLI contradiction score (lower = better)
  ROUGE-L Recall: rouge-score package (Porter stemmer) (higher = better)
  BERTScore Recall: Semantic coverage recall (higher = better)

CS follows the CLPsych 2025 definition: consistency = 1 - contradiction.

All metrics are computed after truncating predicted summaries to 350 words.
"""

import argparse
import json
import sys

import nltk
import numpy as np

from nli_scorer import NLIScorer, MockNLIScorer, ensure_nltk_data
from bertscore_scorer import BERTScoreScorer, MockBERTScoreScorer

MAX_PRED_WORDS = 350


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def truncate_to_words(text, max_words=MAX_PRED_WORDS):
    """Truncate text to first max_words words."""
    if not text:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


def sentence_tokenize(text):
    """Split text into sentences using NLTK."""
    if not text or not text.strip():
        return []
    return nltk.sent_tokenize(text.strip())


# ---------------------------------------------------------------------------
# ROUGE-L Recall (via Google's rouge-score package with Porter stemmer)
# ---------------------------------------------------------------------------

_ROUGE_SCORER = None


def _get_rouge_scorer():
    """Lazy-load the rouge-score package scorer (Porter stemmer enabled)."""
    global _ROUGE_SCORER
    if _ROUGE_SCORER is None:
        from rouge_score import rouge_scorer
        _ROUGE_SCORER = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    return _ROUGE_SCORER


def rouge_l_recall(gold_text, pred_text):
    """Compute ROUGE-L Recall using Google's rouge-score package.

    Uses Porter stemmer and standard tokenization (word-boundary regex),
    matching conventional ROUGE-L implementations.
    """
    if not gold_text or not pred_text:
        return 0.0
    scorer = _get_rouge_scorer()
    return float(scorer.score(gold_text, pred_text)["rougeL"].recall)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_gold_task3(gold_file):
    """Load gold Task 3 data.

    Returns dict mapping (timeline_id, sequence_id) -> gold record.
    """
    with open(gold_file) as f:
        data = json.load(f)

    gold = {}
    for record in data:
        key = (record["timeline_id"], record["sequence_id"])
        gold[key] = record
    return gold


def load_predictions_task3(pred_file):
    """Load Task 3 predictions.

    Returns dict mapping (timeline_id, sequence_id) -> prediction record.
    """
    with open(pred_file) as f:
        data = json.load(f)

    preds = {}
    for record in data:
        key = (record["timeline_id"], record["sequence_id"])
        preds[key] = record
    return preds


def validate_coverage(gold, preds):
    """Check prediction coverage against gold. Returns matched keys."""
    missing = []
    matched = []
    for key in gold:
        if key in preds:
            matched.append(key)
        else:
            missing.append(key)

    if missing:
        print("[Task 3.1] WARNING: %d gold sequences missing from predictions:" % len(missing))
        for tid, sid in missing[:10]:
            print("  timeline=%s, sequence=%s" % (tid, sid))
        if len(missing) > 10:
            print("  ... and %d more" % (len(missing) - 10))

    extra = set(preds.keys()) - set(gold.keys())
    if extra:
        print("[Task 3.1] WARNING: %d extra sequences in predictions (not in gold)." % len(extra))

    print("[Task 3.1] Matched %d / %d gold sequences." % (len(matched), len(gold)))
    return matched


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(gold_file, pred_file, device=None, batch_size=32, mock=False,
             enable_rouge=True, enable_bertscore=True):
    """Run Task 3.1 evaluation. Returns results dict.

    Args:
        enable_rouge: Compute ROUGE-L Recall (default: True).
        enable_bertscore: Compute BERTScore Recall (default: True).
            Disable these for faster Codabench runs (NLI-only).
    """
    gold = load_gold_task3(gold_file)
    preds = load_predictions_task3(pred_file)
    matched = validate_coverage(gold, preds)

    if not matched:
        print("[Task 3.1] ERROR: No matched sequences. Aborting.")
        sys.exit(1)

    ensure_nltk_data()

    if mock:
        nli = MockNLIScorer()
        bsc = MockBERTScoreScorer() if enable_bertscore else None
    else:
        nli = NLIScorer(device=device, batch_size=batch_size)
        bsc = BERTScoreScorer() if enable_bertscore else None

    disabled = []
    if not enable_rouge:
        disabled.append("ROUGE-L")
    if not enable_bertscore:
        disabled.append("BERTScore")
    if disabled:
        print("[Task 3.1] Disabled metrics: %s" % ", ".join(disabled))

    per_sequence = {}
    all_cs, all_ct, all_rouge, all_bert = [], [], [], []
    n_truncated = 0

    for key in sorted(matched):
        tid, sid = key
        gold_summary = gold[key]["summary"]
        raw_pred = preds[key].get("summary", "")

        # Enforce word limit
        pred_summary = truncate_to_words(raw_pred, MAX_PRED_WORDS)
        if len(raw_pred.split()) > MAX_PRED_WORDS:
            n_truncated += 1

        # Sentence tokenize
        gold_sents = sentence_tokenize(gold_summary)
        pred_sents = sentence_tokenize(pred_summary)

        # NLI: CS, CT (always computed)
        nli_scores = nli.score_sequence(gold_sents, pred_sents)

        seq_result = {
            "cs": nli_scores["cs"],
            "ct": nli_scores["ct"],
            "n_gold_sents": len(gold_sents),
            "n_pred_sents": len(pred_sents),
            "pred_words": len(pred_summary.split()),
        }

        # ROUGE-L Recall (optional)
        if enable_rouge:
            rl_recall = rouge_l_recall(gold_summary, pred_summary)
            seq_result["rouge_l_recall"] = rl_recall
            all_rouge.append(rl_recall)

        # BERTScore Recall (optional)
        if enable_bertscore:
            bert_scores = bsc.score_sequence(gold_sents, pred_sents)
            seq_result["bertscore_recall"] = bert_scores["bertscore_recall"]
            all_bert.append(bert_scores["bertscore_recall"])

        per_sequence["%s/%s" % (tid, sid)] = seq_result
        all_cs.append(seq_result["cs"])
        all_ct.append(seq_result["ct"])

    if n_truncated:
        print("[Task 3.1] Truncated %d / %d predictions to %d words." % (
            n_truncated, len(matched), MAX_PRED_WORDS))

    results = {
        "per_sequence": per_sequence,
        "mean_cs": float(np.mean(all_cs)),
        "mean_ct": float(np.mean(all_ct)),
        "n_sequences": len(matched),
        "n_truncated": n_truncated,
    }
    if enable_rouge:
        results["mean_rouge_l_recall"] = float(np.mean(all_rouge))
    if enable_bertscore:
        results["mean_bertscore_recall"] = float(np.mean(all_bert))

    print_results(results)
    return results


# ---------------------------------------------------------------------------
# Printing
# ---------------------------------------------------------------------------

def print_results(results):
    has_rouge = "mean_rouge_l_recall" in results
    has_bert = "mean_bertscore_recall" in results

    print("=" * 72)
    print("TASK 3.1 — Sequence Summary Evaluation")
    print("=" * 72)

    # Build dynamic header and row format
    cols = [("CS", 7), ("CT", 7)]
    if has_rouge:
        cols.append(("ROU-L", 7))
    if has_bert:
        cols.append(("BERT-R", 7))
    cols += [("G_sn", 5), ("P_sn", 5)]

    header_fmt = "%-35s " + " ".join("%%%ds" % w for _, w in cols)
    print("\n--- Per-Sequence Scores ---")
    print(header_fmt % tuple(["Sequence"] + [n for n, _ in cols]))
    print("-" * 72)

    for seq_key, m in sorted(results["per_sequence"].items()):
        vals = [m["cs"], m["ct"]]
        if has_rouge:
            vals.append(m["rouge_l_recall"])
        if has_bert:
            vals.append(m["bertscore_recall"])
        vals += [m["n_gold_sents"], m["n_pred_sents"]]
        fmt = "%-35s " + " ".join("%7.4f" if isinstance(v, float) else "%5d" for v in vals)
        print(fmt % tuple([seq_key] + vals))

    print("-" * 72)
    print("\n--- Aggregate (mean over %d sequences) ---" % results["n_sequences"])
    print("%-25s %8.4f   (higher = better)" % ("Mean CS", results["mean_cs"]))
    print("%-25s %8.4f   (lower = better)" % ("Mean CT", results["mean_ct"]))
    if has_rouge:
        print("%-25s %8.4f   (higher = better)" % ("Mean ROUGE-L Recall", results["mean_rouge_l_recall"]))
    if has_bert:
        print("%-25s %8.4f   (higher = better)" % ("Mean BERTScore Recall", results["mean_bertscore_recall"]))
    if results["n_truncated"]:
        print("\n[Note] %d predictions truncated to %d words." % (
            results["n_truncated"], MAX_PRED_WORDS))


# ---------------------------------------------------------------------------
# Codabench scores.txt output
# ---------------------------------------------------------------------------

def flatten_results(results):
    """Convert results to flat dict with short key names for Codabench."""
    flat = {}
    flat["t3_cs"] = results["mean_cs"]
    flat["t3_ct"] = results["mean_ct"]
    if "mean_rouge_l_recall" in results:
        flat["t3_rouge_l_recall"] = results["mean_rouge_l_recall"]
    if "mean_bertscore_recall" in results:
        flat["t3_bertscore_recall"] = results["mean_bertscore_recall"]
    flat["t3_n_seq"] = results["n_sequences"]
    flat["t3_n_trunc"] = results["n_truncated"]
    # Ranking: mean CS (higher is better)
    flat["t3_rank"] = results["mean_cs"]
    return flat


def write_scores_txt(flat, output_path):
    """Write flat results dict to scores.txt format (Codabench)."""
    with open(output_path, "w") as f:
        for key in sorted(flat.keys()):
            value = flat[key]
            if isinstance(value, float):
                f.write("%s: %s\n" % (key, value))
            elif isinstance(value, (np.integer,)):
                f.write("%s: %s\n" % (key, int(value)))
            else:
                f.write("%s: %s\n" % (key, value))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Task 3.1 — Sequence Summary",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python evaluate_task3.py \\
      --gold-file ../fulldata/clpsych2026_task3/train_task3.json \\
      --pred-file task3_pred.json

  python evaluate_task3.py \\
      --gold-file ../fulldata/clpsych2026_task3/train_task3.json \\
      --pred-file task3_pred.json \\
      --output scores.txt --json-output results.json --device cuda
""",
    )
    parser.add_argument("--gold-file", required=True,
                        help="Gold Task 3 JSON file (train_task3.json)")
    parser.add_argument("--pred-file", required=True,
                        help="Prediction JSON file for Task 3.1")
    parser.add_argument("--output", help="Output scores.txt file (Codabench format)")
    parser.add_argument("--json-output", help="Optional: save nested JSON results")
    parser.add_argument("--device", default=None,
                        help="Device for NLI model (cuda/mps/cpu, auto-detected if omitted)")
    parser.add_argument("--batch-size", type=int, default=32,
                        help="Batch size for NLI inference (default: 32)")
    parser.add_argument("--mock", action="store_true",
                        help="Use mock scorers (no models, for pipeline testing)")
    parser.add_argument("--no-rouge", action="store_true",
                        help="Disable ROUGE-L Recall (faster evaluation)")
    parser.add_argument("--no-bertscore", action="store_true",
                        help="Disable BERTScore Recall (saves ~1.4GB model download)")
    args = parser.parse_args()

    results = evaluate(args.gold_file, args.pred_file,
                       device=args.device, batch_size=args.batch_size,
                       mock=args.mock,
                       enable_rouge=not args.no_rouge,
                       enable_bertscore=not args.no_bertscore)

    if args.output:
        flat = flatten_results(results)
        write_scores_txt(flat, args.output)
        print("\nScores saved to %s" % args.output)

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
            json.dump(results, f, indent=2, default=convert)
        print("JSON results saved to %s" % args.json_output)


if __name__ == "__main__":
    main()
