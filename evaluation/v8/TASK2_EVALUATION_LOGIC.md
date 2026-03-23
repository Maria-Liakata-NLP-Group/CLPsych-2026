# Task 2 Evaluation Logic

## Overview

Task 2 evaluates **Moments of Change** detection: Switch and Escalation are independent binary labels per post. A post can have both, either, or neither.

- **Switch** (`"S"` or `"0"`): An abrupt change in well-being between consecutive posts
- **Escalation** (`"E"` or `"0"`): A gradual mood progression over a sequence of posts

## Step 1: Post Filtering

**ALL posts are evaluated** — no filtering. Unlike Task 1, Switch/Escalation labels are always present in gold data, even for posts without ABCD evidence.

## Step 2: Label Parsing

Each label is parsed to binary:

| Raw value | Binary |
| --------- | ------ |
| `"S"`     | 1      |
| `"0"`     | 0      |
| `"E"`     | 1      |
| `"0"`     | 0      |

Switch and Escalation are evaluated independently — they produce two separate binary classification problems.

## Post-Level Evaluation

All posts are pooled together regardless of timeline. For each label (Switch, Escalation):

### Example — Switch across 8 posts

| Post | Gold | Pred | Result |
| ---- | ---- | ---- | ------ |
| 1    | S    | S    | TP     |
| 2    | 0    | S    | FP     |
| 3    | S    | 0    | FN     |
| 4    | 0    | 0    | TN     |
| 5    | S    | S    | TP     |
| 6    | 0    | S    | FP     |
| 7    | 0    | 0    | TN     |
| 8    | S    | S    | TP     |

- Precision = 3 TP / (3 TP + 2 FP) = 0.600
- Recall = 3 TP / (3 TP + 1 FN) = 0.750
- F1 = 2 × 0.600 × 0.750 / (0.600 + 0.750) = 0.667

### Metrics

| Key                | Description                                                              |
| ------------------ | ------------------------------------------------------------------------ |
| `precision`        | Of all posts predicted positive, the fraction truly positive in gold     |
| `recall`           | Of all truly positive posts in gold, the fraction predicted positive     |
| `f1`               | Harmonic mean of precision and recall                                    |
| `support_positive` | Number of gold-positive posts for this label                             |
| `support_total`    | Total number of posts evaluated                                          |
| `macro_f1`         | Mean of Switch F1 and Escalation F1                                      |

## Timeline-Level Evaluation

Posts are grouped by `timeline_id`. Metrics are computed **per timeline**, then **macro-averaged** across all timelines.

### Example — 3 timelines, Switch label

**Timeline A** (4 posts):

| Post | Gold | Pred |
| ---- | ---- | ---- |
| 1    | S    | S    |
| 2    | 0    | 0    |
| 3    | S    | 0    |
| 4    | 0    | 0    |

- Precision = 1/1 = 1.000
- Recall = 1/2 = 0.500
- F1 = 0.667

**Timeline B** (3 posts):

| Post | Gold | Pred |
| ---- | ---- | ---- |
| 1    | 0    | S    |
| 2    | 0    | 0    |
| 3    | 0    | 0    |

- Precision = 0/1 = 0.000
- Recall = 0/0 → undefined (no gold positives, but there is a false positive)
- F1 = 0.000

**Timeline C** (3 posts):

| Post | Gold | Pred |
| ---- | ---- | ---- |
| 1    | 0    | 0    |
| 2    | 0    | 0    |
| 3    | 0    | 0    |

- No gold positives AND no predicted positives → **score 1.0** (perfect agreement on absence)

**Macro-average across timelines:**

- Precision = (1.000 + 0.000 + 1.000) / 3 = 0.667
- Recall = (0.500 + 0.000 + 1.000) / 3 = 0.500
- F1 = (0.667 + 0.000 + 1.000) / 3 = 0.556

### Edge Case: No-Event Timelines

When both gold and prediction have **zero positive instances** for a label in a timeline, the timeline scores 1.0 for precision, recall, and F1. This avoids penalizing correct identification of timelines with no events.

### Metrics

| Key              | Description                                                 |
| ---------------- | ----------------------------------------------------------- |
| `precision`      | Per-timeline precision, macro-averaged across all timelines |
| `recall`         | Per-timeline recall, macro-averaged across all timelines    |
| `f1`             | Per-timeline F1, macro-averaged across all timelines        |
| `num_timelines`  | Number of timelines evaluated                               |
| `macro_f1`       | Mean of timeline-level Switch F1 and Escalation F1          |

## Why Both Levels?

- **Post-level**: Overall system accuracy across the full dataset. Larger timelines contribute more.
- **Timeline-level**: Ensures the system works well across all timelines equally, not just the large ones. A system that works perfectly on 2 large timelines but fails on 28 small ones would score well post-level but poorly timeline-level.

## Pipeline Summary

```
All posts (no filtering)
  ├─ Post-level:     pool all posts → P/R/F1 per label → macro F1
  └─ Timeline-level: group by timeline_id → P/R/F1 per timeline → macro-average → macro F1
```
