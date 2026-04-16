"""Generate a pilot submission for Task 3.1 evaluation testing.

Creates three types of predictions to sanity-check the scoring:
  1. Gold copy — identical to gold summaries (should get lowest contradiction)
  2. Shuffled — summaries randomly reassigned across sequences (moderate contradiction)
  3. Generic — a fixed generic summary for every sequence (high contradiction)
"""

import argparse
import json
import random


def load_gold(gold_file):
    with open(gold_file) as f:
        return json.load(f)


def create_gold_copy(gold):
    """Prediction = exact copy of gold summaries."""
    return [
        {
            "timeline_id": r["timeline_id"],
            "sequence_id": r["sequence_id"],
            "summary": r["summary"],
        }
        for r in gold
    ]


def create_shuffled(gold, seed=42):
    """Prediction = summaries shuffled across sequences."""
    rng = random.Random(seed)
    summaries = [r["summary"] for r in gold]
    rng.shuffle(summaries)
    return [
        {
            "timeline_id": r["timeline_id"],
            "sequence_id": r["sequence_id"],
            "summary": summaries[i],
        }
        for i, r in enumerate(gold)
    ]


GENERIC_SUMMARY = (
    "The individual experiences psychological distress. "
    "The maladaptive self-state becomes increasingly dominant over time. "
    "The adaptive self-state diminishes throughout the sequence. "
    "This represents a change in the individual's well-being."
)


def create_generic(gold):
    """Prediction = same generic summary for every sequence."""
    return [
        {
            "timeline_id": r["timeline_id"],
            "sequence_id": r["sequence_id"],
            "summary": GENERIC_SUMMARY,
        }
        for r in gold
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Generate pilot Task 3 submissions for evaluation testing")
    parser.add_argument("--gold-file", required=True,
                        help="Gold Task 3 JSON file (train_task3.json)")
    parser.add_argument("--output-dir", default=".",
                        help="Directory to write pilot files (default: current dir)")
    args = parser.parse_args()

    gold = load_gold(args.gold_file)
    print("Loaded %d gold sequences." % len(gold))

    variants = {
        "task3_pilot_gold_copy.json": create_gold_copy(gold),
        "task3_pilot_shuffled.json": create_shuffled(gold),
        "task3_pilot_generic.json": create_generic(gold),
    }

    for fname, preds in variants.items():
        path = "%s/%s" % (args.output_dir, fname)
        with open(path, "w") as f:
            json.dump(preds, f, indent=2)
        print("  Written %s (%d entries)" % (path, len(preds)))


if __name__ == "__main__":
    main()
