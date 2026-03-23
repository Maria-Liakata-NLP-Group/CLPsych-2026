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
