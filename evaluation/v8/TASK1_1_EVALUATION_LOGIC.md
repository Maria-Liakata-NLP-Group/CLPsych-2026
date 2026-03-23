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
