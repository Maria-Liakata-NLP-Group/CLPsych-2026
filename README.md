# CLPsych-2026
CLPsyc 2026 Evaluation Code
# Task 1.1 Evaluation Logic

## Overview

Task 1.1 evaluates two levels:
1. **Element presence** (binary): Is element X present in this valence?
2. **Subelement classification** (multi-class): If present, which subelement was selected?

## Step 1: Post Filtering

Only posts with at least one valid `Presence` value in gold are evaluated. Posts with empty evidence are skipped entirely.

```
375 total posts → ~225 posts with evidence → evaluated
~150 posts with no evidence → skipped
```

## Step 2: Per-Valence Filtering

Within an evaluated post, each valence is checked independently. If a post has `adaptive-state.Presence = 3` but no maladaptive-state evidence, only the adaptive side is evaluated. The 6 element slots for maladaptive-state are **not evaluated at all** for that post — no TP, FP, FN, or TN counted.

## Step 3: Data Collection

For each valence that passed Step 2, all 6 elements are compared between gold and prediction. Two types of data are collected:

**Element presence** — binary (present/absent):

| Element | Gold            | Pred            | Binary (g, p) | Result |
| ------- | --------------- | --------------- | ------------- | ------ |
| A       | present (sub=3) | present (sub=5) | (1, 1)        | TP     |
| B-O     | present (sub=1) | absent          | (1, 0)        | FN     |
| B-S     | absent          | present (sub=1) | (0, 1)        | **FP** |
| C-O     | absent          | absent          | (0, 0)        | TN     |
| C-S     | absent          | absent          | (0, 0)        | TN     |
| D       | present (sub=2) | present (sub=1) | (1, 1)        | TP     |

**Subelement classification** — multi-class label (0=absent, 1..K=subelement index):

| Element | Gold label | Pred label |
| ------- | ---------- | ---------- |
| A       | 3          | 5          |
| B-O     | 1          | 0          |
| B-S     | 0          | 1          |
| C-O     | 0          | 0          |
| C-S     | 0          | 0          |
| D       | 2          | 1          |

This gives the per-post vector the colleague described:
```
Gold adaptive:  [A:3, BO:1, BS:0, CO:0, CS:0, D:2]
Pred adaptive:  [A:5, BO:0, BS:1, CO:0, CS:0, D:1]
```

## Step 4: Element Presence Metrics

After processing all posts, each element×valence has two accumulated binary lists:

```
adaptive-state:A → gold: [1,0,1,1,0,0,1,...], pred: [1,0,0,1,1,0,1,...]
                    ↑ one entry per evaluated post
```

Metrics computed:

- **Per-element P/R/F1**: for each of 12 element×valence pairs
- **Per-valence**: adaptive macro/micro F1 (across 6 adaptive elements), maladaptive macro/micro F1 (across 6 maladaptive elements)
- **Avg macro/micro F1**: mean of adaptive and maladaptive
- **Overall macro/micro F1**: across all 12 element×valence pairs
- **`support`**: number of gold positives for each element×valence

## Step 5: Subelement Classification Metrics

Each element is treated as a **multi-class classification** problem with classes = {0=absent, 1, 2, ..., K} where K is the number of subelements for that element.

After processing all posts, each element×valence has two accumulated label lists:

```
adaptive-state:A → gold: [3,0,5,3,0,0,7,...], pred: [5,0,0,3,2,0,7,...]
                    ↑ multi-class labels (0=absent, 1-7=subelement)
```

F1 is computed **over positive classes only** (class 0=absent is excluded from metrics, since element presence is already evaluated in Step 4). This means:
- Predicting the wrong subelement (gold=3, pred=5) penalizes F1 for both class 3 (FN) and class 5 (FP)
- Missing an element entirely (gold=3, pred=0) penalizes F1 for class 3 (FN)
- Falsely predicting an element (gold=0, pred=5) penalizes F1 for class 5 (FP)
- Both absent (gold=0, pred=0) is ignored (already covered by element presence)

### Per-element metrics

For each element, `f1_score(gold, pred, labels=positive_classes, average=...)`:

- **Macro F1**: mean of per-class F1 within this element (e.g., for A: mean of F1 for classes 1-7)
- **Micro F1**: pooled TP/FP/FN across all positive classes within this element

### Aggregation

- **Adaptive macro F1**: mean of 6 adaptive element macro F1s
- **Adaptive micro F1**: pooled across all adaptive elements (using globally unique labels like `A:1`, `BO:1`, etc.)
- **Maladaptive macro/micro F1**: same for maladaptive
- **Avg macro/micro F1**: mean of adaptive and maladaptive
- **Overall macro/micro F1**: across all 12 element×valence pairs

### Example

For `adaptive-state:A` (7 subelement classes) across 5 posts:

| Post | Gold | Pred | Effect on class-level F1              |
| ---- | ---- | ---- | ------------------------------------- |
| 1    | 3    | 3    | TP for class 3                        |
| 2    | 5    | 3    | FN for class 5, FP for class 3        |
| 3    | 0    | 0    | ignored (both absent)                 |
| 4    | 3    | 0    | FN for class 3                        |
| 5    | 0    | 2    | FP for class 2                        |

Note: Elements with only 1 subelement (B-S, C-S) have their subelement F1 equal to element presence F1, since the only question is present vs absent.

## Pipeline Summary

```
Post filtering:          only posts with gold Presence
  └─ Valence filtering:  only valences with gold Presence in that post
       ├─ Element presence: binary per element → P/R/F1 per element, per valence, overall
       └─ Subelement classification: multi-class per element → F1 per element, per valence, overall
```
# Task 1.2 Evaluation Logic

## Overview

Task 1.2 evaluates the **Presence rating** (1–5 ordinal scale) for each self-state, measuring how psychologically central the self-state is in the post.

## Step 1: Post Filtering

Same as Task 1.1 — only posts with at least one valid `Presence` value in gold are evaluated.

## Step 2: Per-Valence Filtering

Within an evaluated post, each valence is checked independently. A Presence rating is only evaluated for a valence if the gold data has a valid numeric `Presence` value (integer 1–5) for that valence.

## Step 3: Collect Rating Pairs

For each (post, valence) that passed filtering, extract the gold and predicted Presence values:

| Post | Valence           | Gold Presence | Pred Presence | Pair     |
| ---- | ----------------- | ------------- | ------------- | -------- |
| 1    | adaptive-state    | 3             | 3             | (3, 3)   |
| 1    | maladaptive-state | 4             | 2             | (4, 2)   |
| 2    | adaptive-state    | —             | —             | skipped  |
| 2    | maladaptive-state | 2             | 3             | (2, 3)   |
| 3    | adaptive-state    | 1             | —             | (1, **1**) |

**Default behavior**: If gold has a Presence value but the prediction omits the entire valence (or omits Presence), the predicted Presence defaults to **1** (lowest centrality). This penalizes missing predictions rather than skipping them.

## Step 4: Compute Metrics

Metrics are computed separately for each valence and for all ratings combined:

| Metric       | Description                                                                                  |
| ------------ | -------------------------------------------------------------------------------------------- |
| **MAE**      | Mean Absolute Error — average of \|gold - pred\| across all pairs                            |
| **RMSE**     | Root Mean Squared Error — sqrt of average squared differences                                |
| **QWK**      | Quadratic Weighted Kappa — ordinal agreement measure (1.0 = perfect, 0.0 = chance agreement) |
| **Spearman** | Spearman rank correlation — measures monotonic relationship between gold and pred rankings    |
| **`n`**      | Number of rating pairs used to compute the metrics                                           |

### Example

Given 5 rating pairs for adaptive-state:

| Post | Gold | Pred | \|Error\| | Error² |
| ---- | ---- | ---- | --------- | ------ |
| 1    | 3    | 3    | 0         | 0      |
| 2    | 4    | 2    | 2         | 4      |
| 3    | 1    | 1    | 0         | 0      |
| 4    | 5    | 4    | 1         | 1      |
| 5    | 2    | 3    | 1         | 1      |

- MAE = (0 + 2 + 0 + 1 + 1) / 5 = 0.800
- RMSE = sqrt((0 + 4 + 0 + 1 + 1) / 5) = sqrt(1.2) = 1.095
- QWK and Spearman computed via sklearn/scipy on the full vectors

### Combined

The `combined` metrics concatenate all adaptive-state and maladaptive-state pairs into one pool, then compute all four metrics on the combined vectors.

## Reporting Structure

```json
{
  "adaptive-state":    { "mae", "rmse", "qwk", "spearman", "n" },
  "maladaptive-state": { "mae", "rmse", "qwk", "spearman", "n" },
  "combined":          { "mae", "rmse", "qwk", "spearman", "n" }
}
```

## Pipeline Summary

```
Post filtering:          only posts with gold Presence
  └─ Valence filtering:  only valences with valid gold Presence (int 1-5)
       └─ Pair collection: gold Presence vs pred Presence (default 1 if missing)
            └─ Metrics: MAE, RMSE, QWK, Spearman per valence and combined
```

