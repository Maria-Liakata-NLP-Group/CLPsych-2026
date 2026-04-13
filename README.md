# CLPsych 2026 — Shared Task Evaluation

This repository contains the evaluation logic, metrics, submission format, and scoring pipeline for the **CLPsych 2026 Shared Task**.

The shared task consists of:

* **Task 1.1** — ABCD Element & Subelement Classification
* **Task 1.2** — Presence Rating
* **Task 2** — Moments of Change (Switch & Escalation)
* **Task 3.1** — Sequence Summary Evaluation
* **Task 3.2** — Identifying Recurrent Dynamic Signatures of Change Across Timelines

# Table of Contents

* [Evaluation Pipeline](#evaluation-pipeline)
* [Concept Overview](#concept-overview)
* [1. Evaluation Overview](#1-evaluation-overview)

  * [Task 1.1 — ABCD Element & Subelement Classification](#task-11--abcd-element--subelement-classification)
  * [Task 1.2 — Presence Rating](#task-12--presence-rating)
  * [Task 2 — Moments of Change](#task-2--moments-of-change)
  * [Task 3.1 — Sequence Summary Evaluation](#task-31--sequence-summary-evaluation)
  * [Task 3.2 — Identifying Recurrent Dynamic Signatures of Change Across Timelines](#task-32--identifying-recurrent-dynamic-signatures-of-change-across-timelines)
* [2. Task 1.1 Evaluation Logic](#2-task-11-evaluation-logic)

  * [Overview](#overview)
  * [Step 1: Post Filtering](#step-1-post-filtering)
  * [Step 2: Per-Valence Filtering](#step-2-per-valence-filtering)
  * [Step 3: Data Collection](#step-3-data-collection)
  * [Step 4: Element Presence Metrics](#step-4-element-presence-metrics)
  * [Step 5: Subelement Classification Metrics](#step-5-subelement-classification-metrics)
  * [Task 1.1 Ranking](#task-11-ranking)
  * [Task 1.1 Pipeline Summary](#task-11-pipeline-summary)
* [3. Task 1.2 Evaluation Logic](#3-task-12-evaluation-logic)

  * [Overview](#overview-1)
  * [Step 1: Post Filtering](#step-1-post-filtering-1)
  * [Step 2: Per-Valence Filtering](#step-2-per-valence-filtering-1)
  * [Step 3: Collect Rating Pairs](#step-3-collect-rating-pairs)
  * [Step 4: Compute Metrics](#step-4-compute-metrics)
  * [Reporting Structure](#reporting-structure)
  * [Task 1.2 Ranking](#task-12-ranking)
  * [Task 1.2 Pipeline Summary](#task-12-pipeline-summary)
* [4. Task 2 Evaluation Logic](#4-task-2-evaluation-logic)

  * [Overview](#overview-2)
  * [Step 1: Post Filtering](#step-1-post-filtering-2)
  * [Step 2: Label Parsing](#step-2-label-parsing)
  * [Post-Level Evaluation](#post-level-evaluation)
  * [Timeline-Level Evaluation](#timeline-level-evaluation)
  * [Why both post-level and timeline-level?](#why-both-post-level-and-timeline-level)
  * [Task 2 Ranking](#task-2-ranking)
  * [Task 2 Pipeline Summary](#task-2-pipeline-summary)
* [5. Task 3.1 Evaluation Logic](#5-task-31-evaluation-logic)

  * [Overview](#overview-3)
  * [Prediction Truncation (350 words)](#prediction-truncation-350-words)
  * [CS and CT (NLI Contradiction)](#cs-and-ct-nli-contradiction)
  * [ROUGE-L Recall](#rouge-l-recall)
  * [BERTScore Recall](#bertscore-recall)
  * [Edge Cases](#edge-cases)
  * [Codabench scores.txt Keys](#codabench-scorestxt-keys)
  * [Task 3.1 Ranking](#task-31-ranking)
  * [Task 3.1 Pipeline Summary](#task-31-pipeline-summary)
* [6. Task 3.2 Evaluation Logic](#6-task-32-evaluation-logic)

  * [Overview](#overview-4)
  * [Criterion 1: Fit of Evidence Support](#criterion-1-fit-of-evidence-support)
  * [Criterion 2: Recurrence](#criterion-2-recurrence)
  * [Criterion 3: Specificity](#criterion-3-specificity)
  * [Task 3.2 Final Ranking](#task-32-final-ranking)
  * [Task 3.2 Data](#task-32-data)
  * [Task 3.2 Submission Format](#task-32-submission-format)
* [7. Evaluation Metrics Summary](#7-evaluation-metrics-summary)
* [8. Post Filtering Rules](#8-post-filtering-rules)
* [9. Environment](#9-environment)
* [10. Subelement Schema](#10-subelement-schema)
* [11. Submission Format](#11-submission-format)
* [12. Submission Validation Script](#12-submission-validation-script)
* [13. Running the Evaluation Locally](#13-running-the-evaluation-locally)
* [14. scores.txt Key Names](#14-scorestxt-key-names)
* [15. Final Summary](#15-final-summary)
* [16. Evaluation Flow Diagram](#16-evaluation-flow-diagram)

# Evaluation Pipeline

## What the flowchart shows

* **Task 1** starts from all posts, then filters to only posts with gold evidence
* It then evaluates each valence independently:

  * **Element presence**
  * **Subelement classification**
  * **Presence rating**
* **Task 2** uses **all posts**

  * Converts Switch/Escalation labels into binary form
  * Computes both **post-level** and **timeline-level** metrics
* **Task 3.1** uses **sequence summaries**

  * Truncates predictions to 350 words
  * Computes contradiction, lexical recall, and semantic recall
* **Task 3.2** uses **submitted signatures plus supporting sequences**

  * Human judges evaluate evidence fit, recurrence, and specificity
* Final ranking metrics are derived separately for:

  * **Task 1.1**
  * **Task 1.2**
  * **Task 2**
  * **Task 3.1**
  * **Task 3.2**

# Concept Overview

The diagram also captures the conceptual relationship between the tasks:

* **Task 1** focuses on:

  * Presence filtering
  * Element-level binary prediction
  * Subelement multi-class prediction
  * Presence rating
* **Task 2** focuses on:

  * Switch detection
  * Escalation detection
  * Evaluation both at post level and timeline level
* **Task 3.1** focuses on:

  * Summary quality over full sequences
  * Contradiction minimization
  * Lexical and semantic content coverage
* **Task 3.2** focuses on:

  * Recurring cross-sequence dynamic patterns
  * Human evaluation of support, recurrence, and specificity

# 1. Evaluation Overview

## Task 1.1 — ABCD Element & Subelement Classification

Each post may contain an adaptive and/or maladaptive self-state. Within each self-state, up to **6 ABCD elements** may be present:

```text
A, B-O, B-S, C-O, C-S, D
````

Each present element must receive exactly **one valid subelement** label.

### Two evaluation layers

1. **Element presence** — binary classification for each element
2. **Subelement classification** — multi-class classification for the selected subelement when the element is present

## Task 1.2 — Presence Rating

Each self-state also has a **Presence rating (1–5)** measuring psychological centrality.

## Task 2 — Moments of Change

Each post is evaluated for two independent binary labels:

* **Switch**
* **Escalation**

A post may have:

* neither
* only Switch
* only Escalation
* both

## Task 3.1 — Sequence Summary Evaluation

Each sequence receives a generated summary that is compared against a gold summary using four complementary metrics:

* **CS** — contradiction score
* **CT** — contradiction top score
* **ROUGE-L Recall** — lexical temporal coverage
* **BERTScore Recall** — semantic coverage

## Task 3.2 — Identifying Recurrent Dynamic Signatures of Change Across Timelines

Participants must propose **Signatures of Deterioration** and **Signatures of Improvement** across timelines, along with supporting sequence evidence.

These signatures are evaluated by **human judges**, separately for deterioration and improvement, on:

* **Fit of Evidence Support**
* **Recurrence**
* **Specificity**

# 2. Task 1.1 Evaluation Logic

## Overview

Task 1.1 evaluates two levels:

1. **Element presence** (binary): is element X present in this valence?
2. **Subelement classification** (multi-class): if present, which subelement was selected?

## Step 1: Post Filtering

Only posts with at least one valid `Presence` value in gold are evaluated. Posts with empty evidence are skipped entirely.

```text
375 total posts → ~225 posts with evidence → evaluated
~150 posts with no evidence → skipped
```

## Step 2: Per-Valence Filtering

Within an evaluated post, each valence is checked independently.

If a post has `adaptive-state.Presence = 3` but no `maladaptive-state` evidence, then only the adaptive side is evaluated.

The 6 maladaptive element slots are **not evaluated at all** for that post:

* no TP
* no FP
* no FN
* no TN

## Step 3: Data Collection

For each valence that passed Step 2, all 6 elements are compared between gold and prediction.

### Element presence — binary

| Element | Gold            | Pred            | Binary (g, p) | Result |
| ------- | --------------- | --------------- | ------------- | ------ |
| A       | present (sub=3) | present (sub=5) | (1, 1)        | TP     |
| B-O     | present (sub=1) | absent          | (1, 0)        | FN     |
| B-S     | absent          | present (sub=1) | (0, 1)        | FP     |
| C-O     | absent          | absent          | (0, 0)        | TN     |
| C-S     | absent          | absent          | (0, 0)        | TN     |
| D       | present (sub=2) | present (sub=1) | (1, 1)        | TP     |

### Subelement classification — multi-class label

| Element | Gold label | Pred label |
| ------- | ---------- | ---------- |
| A       | 3          | 5          |
| B-O     | 1          | 0          |
| B-S     | 0          | 1          |
| C-O     | 0          | 0          |
| C-S     | 0          | 0          |
| D       | 2          | 1          |

This gives the per-post vector:

```text
Gold adaptive:  [A:3, BO:1, BS:0, CO:0, CS:0, D:2]
Pred adaptive:  [A:5, BO:0, BS:1, CO:0, CS:0, D:1]
```

## Step 4: Element Presence Metrics

After processing all posts, each element × valence accumulates binary gold/prediction lists.

Example:

```text
adaptive-state:A
gold: [1,0,1,1,0,0,1,...]
pred: [1,0,0,1,1,0,1,...]
```

Metrics computed:

* **Per-element Precision, Recall, F1**
* **Per-valence Macro F1 and Micro F1**
* **Avg Macro F1 / Avg Micro F1**
* **Overall Macro F1 / Overall Micro F1**
* **Support** = number of gold positives for each element × valence pair

## Step 5: Subelement Classification Metrics

Each element is treated as a multi-class problem over:

```text
{0 = absent, 1, 2, ..., K}
```

where `K` is the number of valid subelements for that element.

### Important scoring rule

F1 is computed **only over positive classes**.
Class `0` (absent) is excluded because absence is already handled in element presence evaluation.

This means:

* wrong subelement (`gold=3, pred=5`) → FN for class 3, FP for class 5
* missing element (`gold=3, pred=0`) → FN for class 3
* false element (`gold=0, pred=5`) → FP for class 5
* both absent (`gold=0, pred=0`) → ignored

### Per-element metrics

For each element:

* **Macro F1** = mean F1 across valid subelement classes
* **Micro F1** = pooled TP/FP/FN across valid subelement classes

### Aggregation

* **Adaptive Macro F1** = mean of 6 adaptive element macro F1 scores
* **Adaptive Micro F1** = pooled across all adaptive elements
* **Maladaptive Macro F1 / Micro F1** = same
* **Avg Macro F1 / Avg Micro F1** = mean of adaptive and maladaptive
* **Overall Macro F1 / Overall Micro F1** = across all 12 element × valence pairs

### Example

For `adaptive-state:A` across 5 posts:

| Post | Gold | Pred | Effect                         |
| ---- | ---- | ---- | ------------------------------ |
| 1    | 3    | 3    | TP for class 3                 |
| 2    | 5    | 3    | FN for class 5, FP for class 3 |
| 3    | 0    | 0    | ignored                        |
| 4    | 3    | 0    | FN for class 3                 |
| 5    | 0    | 2    | FP for class 2                 |

**Note:** For elements with only one subelement (`B-S`, `C-S`), subelement F1 is equivalent to element presence F1.

## Task 1.1 Ranking

Ranking uses **subelement classification only**.

1. Compute **Macro F1 per element** for all 12 element × valence pairs
2. Macro-average over the 6 elements within each valence
3. Average adaptive and maladaptive macro F1

```text
Task 1.1 Ranking = Subelement Classification Avg Macro F1
```

## Task 1.1 Pipeline Summary

```text
Post filtering:          only posts with gold Presence
  └─ Valence filtering:  only valences with gold Presence in that post
       ├─ Element presence: binary per element → P/R/F1 per element, per valence, overall
       └─ Subelement classification: multi-class per element → F1 per element, per valence, overall
```

# 3. Task 1.2 Evaluation Logic

## Overview

Task 1.2 evaluates the **Presence rating** (1–5 ordinal scale) for each self-state.

## Step 1: Post Filtering

Same as Task 1.1: only posts with at least one valid gold `Presence` are evaluated.

## Step 2: Per-Valence Filtering

A Presence score is evaluated for a valence only if the gold data has a valid integer `Presence` from 1 to 5.

## Step 3: Collect Rating Pairs

For each evaluated `(post, valence)` pair:

| Post | Valence           | Gold Presence | Pred Presence | Pair    |
| ---- | ----------------- | ------------- | ------------- | ------- |
| 1    | adaptive-state    | 3             | 3             | (3,3)   |
| 1    | maladaptive-state | 4             | 2             | (4,2)   |
| 2    | adaptive-state    | —             | —             | skipped |
| 2    | maladaptive-state | 2             | 3             | (2,3)   |
| 3    | adaptive-state    | 1             | —             | (1,1)   |

### Default behavior

If gold has a Presence value but the prediction omits the valence or omits `Presence`, the predicted Presence defaults to:

```text
1
```

This penalizes missing predictions instead of skipping them.

## Step 4: Compute Metrics

Metrics are computed separately for:

* adaptive-state
* maladaptive-state
* combined

| Metric       | Description                      |
| ------------ | -------------------------------- |
| **MAE**      | Mean Absolute Error              |
| **RMSE**     | Root Mean Squared Error          |
| **QWK**      | Quadratic Weighted Kappa         |
| **Spearman** | Spearman rank correlation        |
| **n**        | Number of evaluated rating pairs |

### Example

Given 5 adaptive pairs:

| Post | Gold | Pred | Error | Error² |
| ---- | ---- | ---- | ----- | ------ |
| 1    | 3    | 3    | 0     | 0      |
| 2    | 4    | 2    | 2     | 4      |
| 3    | 1    | 1    | 0     | 0      |
| 4    | 5    | 4    | 1     | 1      |
| 5    | 2    | 3    | 1     | 1      |

* MAE = (0 + 2 + 0 + 1 + 1) / 5 = 0.800
* RMSE = sqrt((0 + 4 + 0 + 1 + 1) / 5) = sqrt(1.2) = 1.095

QWK and Spearman are computed on the full vectors.

### Combined metrics

The `combined` split concatenates adaptive and maladaptive rating pairs into one pool and computes all metrics on the combined vectors.

## Reporting Structure

```json
{
  "adaptive-state":    { "mae", "rmse", "qwk", "spearman", "n" },
  "maladaptive-state": { "mae", "rmse", "qwk", "spearman", "n" },
  "combined":          { "mae", "rmse", "qwk", "spearman", "n" }
}
```

## Task 1.2 Ranking

```text
Task 1.2 Ranking = mean(Adaptive RMSE, Maladaptive RMSE)
```

Lower is better.

## Task 1.2 Pipeline Summary

```text
Post filtering:          only posts with gold Presence
  └─ Valence filtering:  only valences with valid gold Presence (int 1-5)
       └─ Pair collection: gold Presence vs pred Presence (default 1 if missing)
            └─ Metrics: MAE, RMSE, QWK, Spearman per valence and combined
```

# 4. Task 2 Evaluation Logic

## Overview

Task 2 evaluates **Moments of Change** detection.

The two labels are independent:

* **Switch** (`"S"` or `"0"`)
* **Escalation** (`"E"` or `"0"`)

A post may have both.

## Step 1: Post Filtering

All posts are evaluated.

Unlike Task 1, there is **no evidence-based filtering**.

## Step 2: Label Parsing

Each label is converted to binary:

| Raw value | Binary |
| --------- | ------ |
| `"S"`     | 1      |
| `"0"`     | 0      |
| `"E"`     | 1      |
| `"0"`     | 0      |

Switch and Escalation are evaluated independently.

## Post-Level Evaluation

All posts are pooled together across the full dataset.

For each label:

* Precision
* Recall
* F1

### Example — Switch over 8 posts

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

* Precision = 3 / (3 + 2) = 0.600
* Recall = 3 / (3 + 1) = 0.750
* F1 = 0.667

### Reported metrics

| Key                | Description                                      |
| ------------------ | ------------------------------------------------ |
| `precision`        | fraction of predicted positives that are correct |
| `recall`           | fraction of gold positives recovered             |
| `f1`               | harmonic mean of precision and recall            |
| `support_positive` | number of gold-positive posts                    |
| `support_total`    | total number of posts                            |
| `macro_f1`         | mean of Switch F1 and Escalation F1              |

## Timeline-Level Evaluation

Posts are grouped by `timeline_id`.

Metrics are computed **per timeline**, then macro-averaged across timelines.

### Example — Switch label across 3 timelines

#### Timeline A

| Post | Gold | Pred |
| ---- | ---- | ---- |
| 1    | S    | S    |
| 2    | 0    | 0    |
| 3    | S    | 0    |
| 4    | 0    | 0    |

* Precision = 1.000
* Recall = 0.500
* F1 = 0.667

#### Timeline B

| Post | Gold | Pred |
| ---- | ---- | ---- |
| 1    | 0    | S    |
| 2    | 0    | 0    |
| 3    | 0    | 0    |

* Precision = 0.000
* Recall = 0.000
* F1 = 0.000

#### Timeline C

| Post | Gold | Pred |
| ---- | ---- | ---- |
| 1    | 0    | 0    |
| 2    | 0    | 0    |
| 3    | 0    | 0    |

* No gold positives and no predicted positives
* Precision = 1.000
* Recall = 1.000
* F1 = 1.000

### Macro-average across timelines

* Precision = (1.000 + 0.000 + 1.000) / 3 = 0.667
* Recall = (0.500 + 0.000 + 1.000) / 3 = 0.500
* F1 = (0.667 + 0.000 + 1.000) / 3 = 0.556

### Edge case: no-event timelines

If both gold and prediction contain zero positives for a label within a timeline, that timeline receives:

```text
precision = 1.0
recall = 1.0
f1 = 1.0
```

This avoids penalizing correct prediction of complete absence.

### Reported metrics

| Key             | Description                                        |
| --------------- | -------------------------------------------------- |
| `precision`     | per-timeline precision, macro-averaged             |
| `recall`        | per-timeline recall, macro-averaged                |
| `f1`            | per-timeline F1, macro-averaged                    |
| `num_timelines` | number of timelines                                |
| `macro_f1`      | mean of timeline-level Switch F1 and Escalation F1 |

## Why both post-level and timeline-level?

* **Post-level** rewards overall accuracy across the full dataset
* **Timeline-level** ensures performance is distributed across timelines, not only driven by large timelines

A model that performs well only on large timelines may still score poorly on timeline-level evaluation.

## Task 2 Ranking

```text
Task 2 Ranking = mean(Post-level Macro F1, Timeline-level Macro F1)
```

## Task 2 Pipeline Summary

```text
All posts (no filtering)
  ├─ Post-level:     pool all posts → P/R/F1 per label → macro F1
  └─ Timeline-level: group by timeline_id → P/R/F1 per timeline → macro-average → macro F1
```

# 5. Task 3.1 Evaluation Logic

## Overview

Task 3.1 evaluates **Sequence Summary** quality using four complementary metrics:

| Metric                       | What it measures               | Direction       | Source              |
| ---------------------------- | ------------------------------ | --------------- | ------------------- |
| **CS** (Contradiction Score) | NLI contradiction (mean)       | Lower = better  | CLPsych 2025 Task B |
| **CT** (Contradiction Top)   | NLI contradiction (max)        | Lower = better  | CLPsych 2025 Task B |
| **ROUGE-L Recall**           | Temporal/dynamic word coverage | Higher = better | New                 |
| **BERTScore Recall**         | Semantic content coverage      | Higher = better | CLPsych 2025 Task A |

## Prediction Truncation (350 words)

Before any scoring, predicted summaries are truncated to the first **350 words**. This:

* prevents gaming recall metrics with verbose text
* supports the use of Recall rather than Precision/F1 metrics
* is enforced automatically in the evaluation code

## CS and CT (NLI Contradiction)

Unchanged from CLPsych 2025 Task B.

* Model: `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli`
* Direction: gold = premise, predicted = hypothesis

### CS

For each predicted sentence:

1. compute contradiction probability against each gold sentence
2. take the **mean** contradiction probability across gold sentences

Then average over all predicted sentences.

### CT

For each predicted sentence:

1. compute contradiction probability against each gold sentence
2. take the **max** contradiction probability across gold sentences

Then average over all predicted sentences.

## ROUGE-L Recall

Computes longest common subsequence recall between the full gold summary and the truncated predicted summary at the word level.

```text
ROUGE-L Recall = LCS(gold, pred) / len(gold_words)
```

This captures how well the predicted summary covers the temporal progression and dynamic keywords present in the gold summary.

ABCD terminology such as:

* `self-criticism`
* `hopelessness`
* `relating behavior`

is captured naturally when those word sequences appear in both summaries.

## BERTScore Recall

Adapted from CLPsych 2025 Task A evidence extraction (`span_scorer.py`).

* Model: `microsoft/deberta-xlarge-mnli`
* Baseline rescaling: enabled

For each gold sentence `g_i`, compute BERTScore F1 against all predicted sentences and take the maximum:

```text
BERTScore_Recall(g_i) = max_j BERTScore_F1(g_i, s_j)
```

Then average over all gold sentences:

```text
BERTScore_Recall = (1/m) * sum_i BERTScore_Recall(g_i)
```

This measures whether the semantic content of each gold sentence is covered somewhere in the predicted summary, including paraphrases and semantically equivalent phrasing.

## Edge Cases

| Condition              | CS/CT           | ROUGE-L         | BERTScore       |
| ---------------------- | --------------- | --------------- | --------------- |
| Empty prediction       | 1.0 / 1.0       | 0.0             | 0.0             |
| Empty gold             | 0.0 / 0.0       | 0.0             | 0.0             |
| Prediction > 350 words | Truncated first | Truncated first | Truncated first |

## Codabench scores.txt Keys

| Key                   | Description           | Direction       |
| --------------------- | --------------------- | --------------- |
| `t3_cs`               | Mean CS               | Lower = better  |
| `t3_ct`               | Mean CT               | Lower = better  |
| `t3_rouge_l_recall`   | Mean ROUGE-L Recall   | Higher = better |
| `t3_bertscore_recall` | Mean BERTScore Recall | Higher = better |
| `t3_n_seq`            | Number of sequences   | —               |
| `t3_n_trunc`          | Predictions truncated | —               |
| `t3_rank`             | = t3_cs               | Lower = better  |

## Task 3.1 Ranking

```text
Task 3.1 Ranking = t3_cs
```

Lower is better.

## Task 3.1 Pipeline Summary

```text
Predicted summary
  |-- Truncate to 350 words
  |-- Sentence tokenize (NLTK)
  |
  |-- CS/CT: NLI contradiction (DeBERTa-v3-large)
  |-- ROUGE-L Recall: LCS(gold, pred) / len(gold)
  +-- BERTScore Recall: per-gold-sentence max BERTScore F1 (DeBERTa-xlarge)
```

## Models

| Metric    | Model                                                      | Size    |
| --------- | ---------------------------------------------------------- | ------- |
| CS, CT    | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` | ~1.7 GB |
| BERTScore | `microsoft/deberta-xlarge-mnli`                            | ~1.4 GB |

# 6. Task 3.2 Evaluation Logic

## Overview

Task 3.2 evaluates **Signatures of Deterioration** and **Signatures of Improvement** across timelines.

These outputs are evaluated by **human judges**, separately for deterioration and improvement, based on three criteria:

1. **Fit of Evidence Support**
2. **Recurrence**
3. **Specificity**

## Criterion 1: Fit of Evidence Support

### Definition

Fit of evidence support evaluates how well the proposed signature is supported by the sequences submitted as evidence.

A strong signature is one whose supporting sequences clearly express the same proposed dynamic.

This criterion includes both:

* **correctness**
* **coherence of evidence support**

Incoherence refers to cases where the submitted supporting sequences reflect phenomena that should be treated as separate signatures rather than one coherent dynamic.

### Evaluation

For each submitted signature, evaluators inspect the supporting sequences provided by the team and assess how many of them support the proposed signature.

The key question is whether the same signature is genuinely present across the supporting evidence and accurately represented by them.

A higher proportion of supporting sequences judged to fit the signature accurately results in a higher **Fit of Evidence Support** score.

## Criterion 2: Recurrence

### Definition

Recurrence evaluates how recurrent the proposed signature is across sequences.

A minimum of **2 occurrences** is required for a signature to be considered recurrent.

It is derived from the evidence support assessment and reflects the number of supporting sequences that are judged to genuinely express the proposed dynamic.

### Evaluation

After excluding supporting sequences that do not fit the signature under **Fit of Evidence Support**, recurrence is calculated as the number of remaining valid supporting sequences.

A higher recurrence score reflects a pattern that is supported by a larger number of sequences.

## Criterion 3: Specificity

### Definition

Specificity evaluates how specific and non-generic the proposed signature is.

A strong signature should capture a sufficiently fine-grained and informative dynamic pattern, rather than a broad description that could apply to many different cases.

Specificity may also be reflected in the precision and significance of the wording used in the summary.

In general, signatures that capture both:

* **within-self-state dynamics**
* **between-self-state dynamics**

will be considered more specific than signatures describing only one of these levels, provided that both are clearly supported by the evidence.

### Evaluation

Specificity is evaluated based on how specific, fine-grained, and informative the proposed signature is.

Lower scores are assigned to signatures that remain overly broad or generic.

Additionally, signatures that capture both the dynamics between self-states and within self-states are considered more specific and receive higher scores.

Specificity is assessed independently of recurrence, so a signature supported by few sequences can still receive a high specificity score if its wording is precise and its dynamic is well-defined.

## Task 3.2 Final Ranking

Each signature receives a **Best-Worst Scaling (BWS)-derived score** for each criterion based on comparative human judgments.

The final score is computed as:

```text
Ranking = 0.5 * Fit + 0.5 * HarmonicMean(Recurrence, Specificity)
```

This formulation ensures that signatures are evaluated both by:

* how well they are supported by the submitted evidence
* how recurrent and specific they are across sequences

## Task 3.2 Data

### Important

There is **no separate training or test dataset** for Task 3.2.

Participants should use the **training data provided for Task 3.1**, including the provided sequence summaries.

They may also use the training data from:

* **Task 1**
* **Task 2**

as inputs for Task 3.2.

Using this data, participants are required to extract:

* **Signatures of Deterioration**
* **Signatures of Improvement**

The test data used in Tasks 1, 2, and 3.1 will **not** be used for Task 3.2.

## Task 3.2 Submission Format

Task 3.2 outputs must be submitted **via email** in the specified JSON format for human evaluation.

Send submissions to both:

* `iqra.ali@qmul.ac.uk`
* `t.tseriotou@qmul.ac.uk`

# 7. Evaluation Metrics Summary

## Task 1.1 — Element Presence

Each of the 6 elements × 2 valences gives **12 binary classifications**.

Reported:

* Per-element Precision, Recall, F1
* Per-valence Macro F1 and Micro F1
* Avg Macro F1 / Avg Micro F1
* Overall Macro F1 / Overall Micro F1

## Task 1.1 — Subelement Classification

Each element is a multi-class classification over valid subelements.

Class `0` is excluded from scoring.

Reported:

* Per-element Macro F1 and Micro F1
* Per-valence Macro F1 and Micro F1
* Avg Macro F1 / Avg Micro F1
* Overall Macro F1 / Overall Micro F1

### Ranking aggregation

1. Macro F1 per element
2. Macro average across 6 elements within each valence
3. Average adaptive and maladaptive

```text
Ranking = Subelement Classification Avg Macro F1
```

## Task 1.2 — Presence Rating

Reported separately for:

* adaptive
* maladaptive
* combined

Metrics:

* **MAE**
* **RMSE**
* **QWK**
* **Spearman correlation**

```text
Ranking = mean(Adaptive RMSE, Maladaptive RMSE)
```

Lower is better.

## Task 2 — Moments of Change

Reported for both post-level and timeline-level evaluation:

* Precision
* Recall
* F1
* Macro F1

```text
Ranking = mean(Post-level Macro F1, Timeline-level Macro F1)
```

## Task 3.1 — Sequence Summary Evaluation

Reported:

* **CS**
* **CT**
* **ROUGE-L Recall**
* **BERTScore Recall**
* number of sequences
* number of truncated predictions

```text
Ranking = t3_cs
```

Lower is better.

## Task 3.2 — Dynamic Signature Evaluation

Human-evaluated criteria:

* **Fit of Evidence Support**
* **Recurrence**
* **Specificity**

```text
Ranking = 0.5 * Fit + 0.5 * HarmonicMean(Recurrence, Specificity)
```

Higher is better.

# 8. Post Filtering Rules

## Task 1

Only posts with annotated evidence are evaluated.

A post is evaluated if at least one of:

* `adaptive-state.Presence`
* `maladaptive-state.Presence`

contains a valid numeric value.

Posts with empty evidence are skipped.

## Task 2

All posts are evaluated.

Switch and Escalation labels are always present.

## Task 3.1

All evaluated sequence summaries are scored.

Predictions are truncated to the first **350 words** before scoring.

## Task 3.2

No held-out evaluation dataset is used.

Participants derive signatures from the available training resources and submit them for human evaluation.

# 9. Environment

| Component    | Value                         |
| ------------ | ----------------------------- |
| Docker image | `codalab/codalab-legacy:py37` |
| Python       | 3.7.3                         |
| numpy        | 1.17.2                        |
| scikit-learn | 0.21.3                        |
| scipy        | 1.3.1                         |

All dependencies are pre-installed. No additional `pip install` is required.

# 10. Subelement Schema

## Adaptive State

| Element | # | Subelements                                                                                                                                                                                                |
| ------- | - | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A       | 7 | 1= Calm/ laid back, 3= Sad, Emotional pain, grieving, 5= Content, happy, joy, hopeful, 7= Vigor / energetic, 9= Justifiable anger/ assertive anger, justifiable outrage, 11= Proud, 13= Feel loved, belong |
| B-O     | 2 | 1= Relating behavior, 3= Autonomous or adaptive control behavior                                                                                                                                           |
| B-S     | 1 | 1= Self care and improvement                                                                                                                                                                               |
| C-O     | 2 | 1= Perception of the other as related, 3= Perception of the other as facilitating autonomy needs                                                                                                           |
| C-S     | 1 | 1= Self-acceptance and compassion                                                                                                                                                                          |
| D       | 3 | 1= Relatedness, 3= Autonomy and adaptive control, 5= Competence, self esteem, self-care                                                                                                                    |

## Maladaptive State

| Element | # | Subelements                                                                                                                                                                            |
| ------- | - | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A       | 7 | 2= Anxious/ fearful/ tense, 4= Depressed, despair, hopeless, 6= Mania, 8= Apathic, don’t care, blunted, 10= Angry (aggression), disgust, contempt, 12= Ashamed, guilty, 14=Feel lonely |
| B-O     | 2 | 2= Fight or flight behavior, 4= Over controlled or controlling behavior                                                                                                                |
| B-S     | 1 | 2= Self harm, neglect and avoidance                                                                                                                                                    |
| C-O     | 2 | 2= Perception of the other as detached or over attached, 4= Perception of the other as blocking autonomy needs                                                                         |
| C-S     | 1 | 2= Self criticism                                                                                                                                                                      |
| D       | 3 | 2= Expectation that relatedness needs will not be met, 4= Expectation that autonomy needs will not be met, 6= Expectation that competence needs will not be met                        |

# 11. Submission Format

Participants submit **separate ZIP files** for Task 1, Task 2, and Task 3.1 on their respective Codabench pages.

Task 3.2 is submitted separately by email.

## Required archive structure

### Task 1 submission

```text
predictions.zip
|- task1_pred.json
```

### Task 2 submission

```text
predictions.zip
|- task2_pred.json
```

### Task 3.1 submission

```text
predictions.zip
|- task3_pred.json
```

## Important — Privacy

Do **not** include post text fields such as:

* `post`
* `text`
* `body`

These must be removed before submission.

## Note

Participants may submit predictions for one or more tasks.
If a prediction file for a task is not provided, that task will be skipped and only the provided tasks will be scored.

## Task 1 Submission (`task1_pred.json`)

A JSON array. Each entry corresponds to one post with predicted self-states.

```json
[
  {
    "timeline_id": "91b6a42835",
    "post_id": "28641e5b6d",
    "adaptive-state": {
      "Presence": 5,
      "B-S": { "subelement": 1 },
      "B-O": { "subelement": 1 },
      "C-S": { "subelement": 1 },
      "D": { "subelement": 3 }
    },
    "maladaptive-state": {
      "Presence": 2,
      "C-S": { "subelement": 2 }
    }
  }
]
```

## Task 2 Submission (`task2_pred.json`)

A JSON array. Each entry corresponds to one post with Switch and Escalation labels.

```json
[
  {
    "timeline_id": "3db8573df5",
    "post_id": "e383f54895",
    "Switch": "0",
    "Escalation": "0"
  },
  {
    "timeline_id": "3db8573df5",
    "post_id": "77cbbd5cc2",
    "Switch": "S",
    "Escalation": "E"
  }
]
```

## Task 3.1 Submission (`task3_pred.json`)

A JSON array. Each entry corresponds to one sequence summary prediction.

```json
[
  {
    "timeline_id": "3db8573df5",
    "summary": "The sequence begins with..."
  },
  {
    "timeline_id": "91b6a42835",
    "summary": "Across the timeline..."
  }
]
```

### Additional Task 3.1 rules

* one summary per evaluated sequence
* summaries longer than 350 words are automatically truncated before scoring
* empty predictions receive the edge-case scores described above

## Task 3.2 Submission

Task 3.2 must be submitted by email in the specified JSON format to:

* `iqra.ali@qmul.ac.uk`
* `t.tseriotou@qmul.ac.uk`

# 12. Submission Validation Script

A local validation script `validate_submission.py` is provided.

It requires only Python 3.

## What it checks

It checks both **file format and submission completeness**.

### Privacy

* warns if post text fields are present

### Task 1 checks

* required fields
* at least one valence present
* Presence in range 1–5
* valid element keys
* valid subelement ranges
* no duplicate entries

### Task 2 checks

* required fields
* valid Switch values
* valid Escalation values
* no duplicate entries

### Task 3.1 checks

* required fields
* one summary per sequence
* no duplicate entries
* summary field present and string-typed

### Coverage checks (optional with `--test-dir`)

* every test post covered
* no extra posts included
* Task 2 contains one entry for every post
* Task 1 may omit posts without gold evidence
* Task 3.1 may be checked against expected sequence IDs

# 13. Running the Evaluation Locally

## Task 1 only

```bash
python evaluate_task1.py --gold-dir <gold_dir> --pred-file task1_pred.json
```

## Task 2 only

```bash
python evaluate_task2.py --gold-dir <gold_dir> --pred-file task2_pred.json
```

## Task 3.1 only

```bash
python evaluate_task3.py --gold-dir <gold_dir> --pred-file task3_pred.json
```

## Both tasks — Codabench style output

```bash
python run_evaluation.py --gold-dir <gold_dir> \
    --task1-pred task1_pred.json \
    --task2-pred task2_pred.json \
    --task3-pred task3_pred.json \
    --output scores.txt
```

## Also save nested JSON for debugging

```bash
python run_evaluation.py --gold-dir <gold_dir> \
    --task1-pred task1_pred.json \
    --task2-pred task2_pred.json \
    --task3-pred task3_pred.json \
    --output scores.txt --json-output results.json
```

### Additional note for Codabench submissions

For Codabench submission:

* The JSON prediction file must be placed inside a ZIP archive named:

```text
predictions.zip
```

* The required filename must be at the root:

  * `task1_pred.json` for Task 1
  * `task2_pred.json` for Task 2
  * `task3_pred.json` for Task 3.1

# 14. scores.txt Key Names

All metric keys are kept at **36 characters or fewer** for Codabench compatibility.

Each line in `scores.txt` has format:

```text
key: value
```

## Prefix convention

| Prefix    | Meaning                            |
| --------- | ---------------------------------- |
| `t1ep`    | Task 1.1 Element Presence          |
| `t1sc`    | Task 1.1 Subelement Classification |
| `t1pr`    | Task 1.2 Presence Rating           |
| `t2pl`    | Task 2 Post-Level                  |
| `t2tl`    | Task 2 Timeline-Level              |
| `t2_comb` | Task 2 Combined ranking fields     |
| `t3`      | Task 3.1 Sequence Summary          |

## Common abbreviations

| Abbrev        | Meaning               |
| ------------- | --------------------- |
| `ada`         | adaptive              |
| `mal`         | maladaptive           |
| `avg`         | average               |
| `comb`        | combined              |
| `maF1`        | macro F1              |
| `miF1`        | micro F1              |
| `prec`        | precision             |
| `rec`         | recall                |
| `sup`         | support               |
| `sw`          | Switch                |
| `esc`         | Escalation            |
| `spear`       | Spearman              |
| `BO/BS/CO/CS` | B-O / B-S / C-O / C-S |

## Ranking keys

| Key         | Formula                                 | Description      |
| ----------- | --------------------------------------- | ---------------- |
| `t1_1_rank` | `t1sc_avg_maF1`                         | Task 1.1 ranking |
| `t1_2_rank` | (`t1pr_ada_rmse` + `t1pr_mal_rmse`) / 2 | Task 1.2 ranking |
| `t2_rank`   | (`t2pl_maF1` + `t2tl_maF1`) / 2         | Task 2 ranking   |
| `t3_rank`   | `t3_cs`                                 | Task 3.1 ranking |

See `SCORES_KEY.md` for the complete metric key reference.

# 15. Final Summary

```text
Task 1.1 → classification:
            - element presence (binary)
            - subelement classification (multi-class)

Task 1.2 → ordinal regression:
            - Presence rating (1–5)

Task 2   → binary detection:
            - Switch
            - Escalation
            - post-level and timeline-level scoring

Task 3.1 → sequence summary evaluation:
            - contradiction
            - lexical recall
            - semantic recall

Task 3.2 → human-evaluated signature discovery:
            - fit of evidence support
            - recurrence
            - specificity
```

Each task has its own ranking metric.

# 16. Evaluation Flow Diagram

```mermaid
flowchart TD
    A["All posts in dataset"]

    %% Task 1
    A --> T1F["Task 1: Filter to posts with at least one valid gold Presence"]
    T1F --> T1V["Per-valence filtering: adaptive and maladaptive checked independently"]

    T1V --> EP["Task 1.1 Element Presence"]
    T1V --> SC["Task 1.1 Subelement Classification"]
    T1V --> PR["Task 1.2 Presence Rating"]

    EP --> EP1["Binary evaluation for 6 elements: A, B-O, B-S, C-O, C-S, D"]
    EP1 --> EP2["Per-element Precision / Recall / F1"]
    EP2 --> EP3["Per-valence Macro F1 / Micro F1"]
    EP3 --> EP4["Overall element presence metrics"]

    SC --> SC1["Multi-class evaluation per element"]
    SC1 --> SC2["Class 0 absent excluded from scoring"]
    SC2 --> SC3["Per-element Macro F1 / Micro F1"]
    SC3 --> SC4["Per-valence and overall subelement metrics"]
    SC4 --> T11R["Task 1.1 rank = Avg Macro F1 of subelement classification"]

    PR --> PR1["Collect gold and predicted Presence pairs for valid valences"]
    PR1 --> PR2["Default predicted Presence = 1 if missing"]
    PR2 --> PR3["Compute MAE / RMSE / QWK / Spearman"]
    PR3 --> T12R["Task 1.2 rank = mean of adaptive RMSE and maladaptive RMSE"]

    %% Task 2
    A --> T2A["Task 2: Use all posts with no evidence filtering"]
    T2A --> T2P["Parse Switch and Escalation into binary labels"]

    T2P --> PL["Post-level evaluation"]
    T2P --> TL["Timeline-level evaluation"]

    PL --> PL1["Pool all posts"]
    PL1 --> PL2["Compute Precision / Recall / F1 for Switch and Escalation"]
    PL2 --> PL3["Post-level Macro F1"]

    TL --> TL1["Group posts by timeline_id"]
    TL1 --> TL2["Compute per-timeline Precision / Recall / F1"]
    TL2 --> TL3["Macro-average across timelines"]
    TL3 --> TL4["Timeline-level Macro F1"]

    PL3 --> T2R["Task 2 rank = mean of post-level Macro F1 and timeline-level Macro F1"]
    TL4 --> T2R

    %% Task 3.1
    A --> T31["Task 3.1: Sequence summaries"]
    T31 --> T31T["Truncate predictions to first 350 words"]
    T31T --> T31S["Sentence tokenize"]
    T31S --> T31NLI["CS / CT contradiction scoring"]
    T31S --> T31R["ROUGE-L Recall"]
    T31S --> T31B["BERTScore Recall"]
    T31NLI --> T31Rank["Task 3.1 rank = t3_cs"]
    T31R --> T31Rank
    T31B --> T31Rank

    %% Task 3.2
    A --> T32["Task 3.2: Signature discovery from training resources"]
    T32 --> T32Sig["Submit deterioration and improvement signatures with evidence"]
    T32Sig --> T32Fit["Human evaluation: Fit of Evidence Support"]
    T32Sig --> T32Rec["Human evaluation: Recurrence"]
    T32Sig --> T32Spec["Human evaluation: Specificity"]
    T32Fit --> T32Rank["Task 3.2 rank = 0.5 * Fit + 0.5 * HM(Recurrence, Specificity)"]
    T32Rec --> T32Rank
    T32Spec --> T32Rank
