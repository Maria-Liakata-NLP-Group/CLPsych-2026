"""Validate Task 3 submission files for CLPsych 2026 Shared Task.

Usage:
  python validate_submission.py --pred task3_pred.json
  python validate_submission.py --pred task3_pred.json --gold-file train_task3.json
"""

import argparse
import json
import sys

# Keys that suggest post text is included — these should NOT be in submissions
POST_TEXT_KEYS = {"post", "post_text", "text", "content", "body", "Post Summary"}


def load_json(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return None, "Invalid JSON: %s" % e
    except FileNotFoundError:
        return None, "File not found: %s" % path
    if not isinstance(data, list):
        return None, "Top-level structure must be a JSON array"
    return data, None


def check_post_text(data):
    """Warn if any entry contains fields that look like post text."""
    warnings = []
    flagged = 0
    for i, entry in enumerate(data):
        found_keys = [k for k in entry if k in POST_TEXT_KEYS]
        if found_keys:
            flagged += 1
            if flagged <= 3:
                warnings.append(
                    "Entry %d: contains text field(s) %s — please remove before submitting"
                    % (i, found_keys))
    if flagged > 3:
        warnings.append("... and %d more entries with text fields" % (flagged - 3))
    if flagged > 0:
        warnings.insert(0,
            "WARNING: %d entries contain post text. "
            "For privacy reasons, please remove all post text fields "
            "(e.g., 'post', 'text', 'body') before uploading your submission."
            % flagged)
    return warnings


def load_gold_sequences(gold_file):
    """Load gold Task 3 sequence IDs for coverage validation."""
    with open(gold_file) as f:
        data = json.load(f)
    return {(r["timeline_id"], r["sequence_id"]) for r in data}


def validate_task3(data, gold_sequences=None):
    errors = []
    seen = set()

    for i, entry in enumerate(data):
        prefix = "Entry %d" % i

        if "timeline_id" not in entry:
            errors.append("%s: missing 'timeline_id'" % prefix)
            continue
        if "sequence_id" not in entry:
            errors.append("%s: missing 'sequence_id'" % prefix)
            continue

        tid = entry["timeline_id"]
        sid = entry["sequence_id"]
        prefix = "Entry %d (timeline=%s, sequence=%s)" % (i, tid, sid)

        if not isinstance(tid, str) or not isinstance(sid, str):
            errors.append("%s: 'timeline_id' and 'sequence_id' must be strings" % prefix)
            continue

        key = (tid, sid)
        if key in seen:
            errors.append("%s: duplicate entry" % prefix)
        seen.add(key)

        if "summary" not in entry:
            errors.append("%s: missing 'summary'" % prefix)
        elif not isinstance(entry["summary"], str):
            errors.append("%s: 'summary' must be a string" % prefix)
        elif len(entry["summary"].strip()) == 0:
            errors.append("%s: 'summary' is empty" % prefix)

    if gold_sequences is not None:
        missing = gold_sequences - seen
        extra = seen - gold_sequences
        if missing:
            errors.append("Missing %d gold sequences (first 5: %s)" % (
                len(missing), sorted(missing)[:5]))
        if extra:
            errors.append("Found %d sequences not in gold data (first 5: %s)" % (
                len(extra), sorted(extra)[:5]))

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate CLPsych 2026 Task 3 submission files")
    parser.add_argument("--pred", required=True,
                        help="Task 3 prediction JSON file")
    parser.add_argument("--gold-file",
                        help="Task 3 gold JSON file (for sequence coverage checks)")
    args = parser.parse_args()

    gold_sequences = None
    if args.gold_file:
        gold_sequences = load_gold_sequences(args.gold_file)
        print("Loaded %d sequences from gold data\n" % len(gold_sequences))

    data, load_err = load_json(args.pred)
    if load_err:
        print("FAILED: %s" % load_err)
        sys.exit(1)

    text_warnings = check_post_text(data)
    if text_warnings:
        for w in text_warnings:
            print("  * %s" % w)
        print()

    errors = validate_task3(data, gold_sequences)
    if errors:
        print("FAILED: %d error(s) found:\n" % len(errors))
        for e in errors[:20]:
            print("  - %s" % e)
        if len(errors) > 20:
            print("  ... and %d more" % (len(errors) - 20))
        sys.exit(1)
    else:
        print("PASSED: %d entries, all valid." % len(data))
        sys.exit(0)


if __name__ == "__main__":
    main()
