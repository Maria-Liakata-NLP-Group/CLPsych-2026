Here is a **clean, copy-paste ready GitHub README.md** (minimal, structured, no redundancy, polished for repo use):

---

```markdown
# CLPsych-2026

This repository contains the evaluation framework for the **CLPsych 2026 Shared Task**, which focuses on modeling psychological self-states and moments of change in timelines.

---

# Tasks Overview

- **Task 1.1** — ABCD Element & Subelement Classification  
- **Task 1.2** — Presence Rating (1–5 ordinal)  
- **Task 2** — Moments of Change (Switch & Escalation)

---

# Task 1.1 — Element & Subelement Classification

Each post may contain:
- **adaptive-state**
- **maladaptive-state**

Each state has up to **6 elements**:

```

A, B-O, B-S, C-O, C-S, D

```

Each element:
- Binary presence (present / absent)
- If present → exactly **one subelement**

---

## Evaluation Logic

### 1. Post Filtering

Only posts with at least one valid gold `Presence` are evaluated.

```

~375 posts → ~225 evaluated → ~150 skipped

```

---

### 2. Valence Filtering

Each valence is evaluated independently:

- If `adaptive-state.Presence` exists → evaluate adaptive
- If `maladaptive-state.Presence` missing → skip maladaptive

---

### 3. Element Presence (Binary)

Each element is treated as a binary classification:

- TP / FP / FN / TN computed per element × valence (12 total)

Metrics:
- Precision, Recall, F1 (per element)
- Macro F1 (per valence)
- Micro F1 (per valence)
- Avg (adaptive + maladaptive)
- Overall across all 12

---

### 4. Subelement Classification (Multi-class)

Each element is a multi-class problem:

```

Classes = {1..K} (class 0 = absent, excluded)

```

Rules:
- Wrong subelement → FP + FN
- Missing element → FN
- Spurious element → FP
- Both absent → ignored

Metrics per element:
- Macro F1 (average over subelements)
- Micro F1 (pooled)

Aggregation:
- Adaptive Macro F1 (6 elements)
- Maladaptive Macro F1 (6 elements)
- Avg Macro F1 = mean(adaptive, maladaptive)

---

## 🏆 Ranking (Task 1.1)

```

t1_1_rank = Avg Macro F1 (subelement classification)

```

---

# Task 1.2 — Presence Rating

Each state has a **Presence score (1–5)** indicating psychological centrality.

---

## Evaluation Logic

### 1. Filtering

Same as Task 1.1 (only posts with gold Presence).

---

### 2. Pair Collection

For each (post, valence):

```

(gold Presence, predicted Presence)

```

If prediction is missing:
```

pred = 1 (default)

```

---

### 3. Metrics

Computed for:
- adaptive
- maladaptive
- combined

| Metric | Description |
|--------|------------|
| MAE | Mean Absolute Error |
| RMSE | Root Mean Squared Error |
| QWK | Quadratic Weighted Kappa |
| Spearman | Rank correlation |

---

## 🏆 Ranking (Task 1.2)

```

t1_2_rank = mean(adaptive RMSE, maladaptive RMSE)
(lower is better)

```

---

# Task 2 — Moments of Change

Each post has:

- **Switch**: `"S"` or `"0"`
- **Escalation**: `"E"` or `"0"`

Independent labels (can both be 1).

---

## Evaluation Logic

### 1. No Filtering

All posts are evaluated.

---

### 2. Binary Mapping

```

"S" → 1
"E" → 1
"0" → 0

```

---

## Post-Level Metrics

Computed across all posts:

- Precision, Recall, F1 (per label)
- Macro F1 = mean(Switch F1, Escalation F1)

---

## Timeline-Level Metrics

1. Group by `timeline_id`
2. Compute metrics per timeline
3. Macro-average across timelines

Edge case:
```

No gold positives AND no predictions → score = 1.0

```

---

## 🏆 Ranking (Task 2)

```

t2_rank = mean(post-level Macro F1, timeline-level Macro F1)

````

---

# Subelement Schema

## Adaptive

| Element | Classes |
|--------|--------|
| A | 7 |
| B-O | 2 |
| B-S | 1 |
| C-O | 2 |
| C-S | 1 |
| D | 3 |

## Maladaptive

| Element | Classes |
|--------|--------|
| A | 7 |
| B-O | 2 |
| B-S | 1 |
| C-O | 2 |
| C-S | 1 |
| D | 3 |

---

# Submission Format

## Task 1 (`task1_pred.json`)

```json
{
  "timeline_id": "...",
  "post_id": "...",
  "adaptive-state": {
    "A": {"subelement": 3},
    "Presence": 3
  }
}
````

---

## Task 2 (`task2_pred.json`)

```json
{
  "timeline_id": "...",
  "post_id": "...",
  "Switch": "S",
  "Escalation": "0"
}
```

---

# Running Evaluation

```bash
# Task 1
python evaluate_task1.py --gold-dir <gold_dir> --pred-file task1_pred.json

# Task 2
python evaluate_task2.py --gold-dir <gold_dir> --pred-file task2_pred.json

# Combined
python run_evaluation.py \
  --gold-dir <gold_dir> \
  --task1-pred task1_pred.json \
  --task2-pred task2_pred.json \
  --output scores.txt
```

---

# Score Key Prefixes

| Prefix | Meaning                   |
| ------ | ------------------------- |
| t1ep   | Element presence          |
| t1sc   | Subelement classification |
| t1pr   | Presence rating           |
| t2pl   | Post-level                |
| t2tl   | Timeline-level            |

---

# Summary

```
Task 1.1 → classification (binary + multi-class)
Task 1.2 → ordinal regression
Task 2   → binary event detection (post + timeline level)
```
