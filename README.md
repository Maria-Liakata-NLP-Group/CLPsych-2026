# CLPsych 2026 — Shared Task Evaluation

This repository contains the evaluation logic, metrics, and submission format for the **CLPsych 2026 Shared Task**.

The task consists of:

* **Task 1.1** — ABCD Element & Subelement Classification
* **Task 1.2** — Presence Rating (ordinal regression)
* **Task 2** — Moments of Change (Switch & Escalation detection)

---

# 1. Evaluation Overview

## Task 1.1 — ABCD Element & Subelement Classification

Each post may contain:

* **Adaptive self-state**
* **Maladaptive self-state**

Within each self-state, up to **6 elements** may be present:

```
A, B-O, B-S, C-O, C-S, D
```

Each element:

* Has **binary presence** (present / absent)
* If present → exactly **one subelement** must be predicted

---

## Task 1.2 — Presence Rating

Each self-state has a **Presence score (1–5)** indicating psychological centrality.

---

## Task 2 — Moments of Change

Each post has two independent binary labels:

* **Switch** (`S` or `0`)
* **Escalation** (`E` or `0`)

---

# 2. Task 1.1 — Evaluation Logic

## Overview

Two levels are evaluated:

1. **Element presence** (binary)
2. **Subelement classification** (multi-class)

---

## Step 1: Post Filtering

Only posts with at least one valid `Presence` in gold are evaluated.

```
375 total posts
→ ~225 with evidence → evaluated
→ ~150 without evidence → skipped
```

---

## Step 2: Per-Valence Filtering

Each valence is evaluated independently.

Example:

* Adaptive has Presence → evaluated
* Maladaptive missing → **not evaluated at all**

---

## Step 3: Data Collection

### Element Presence (binary)

| Element | Gold    | Pred    | Result |
| ------- | ------- | ------- | ------ |
| A       | present | present | TP     |
| B-O     | present | absent  | FN     |
| B-S     | absent  | present | FP     |
| C-O     | absent  | absent  | TN     |
| C-S     | absent  | absent  | TN     |
| D       | present | present | TP     |

---

### Subelement Classification (multi-class)

```
Gold: [A:3, BO:1, BS:0, CO:0, CS:0, D:2]
Pred: [A:5, BO:0, BS:1, CO:0, CS:0, D:1]
```

* `0 = absent`
* `1..K = subelement`

---

## Step 4: Element Presence Metrics

Computed for **12 element × valence pairs**:

* Precision, Recall, F1 (per element)
* Macro / Micro F1 (per valence)
* Avg Macro / Micro F1
* Overall Macro / Micro F1

---

## Step 5: Subelement Classification Metrics

Each element is treated as:

```
Multi-class classification over {1..K}
(Class 0 excluded from scoring)
```

### Important Rules

* Wrong subelement → FP + FN
* Missing element → FN
* False element → FP
* Both absent → ignored

---

### Per-element Metrics

* **Macro F1** — average over subelement classes
* **Micro F1** — pooled across classes

---

### Aggregation

* Adaptive Macro F1 (6 elements)
* Maladaptive Macro F1 (6 elements)
* Avg Macro F1 = mean(adaptive, maladaptive)

---

## 🔑 Task 1.1 Ranking

```
Ranking = Subelement Classification Avg Macro F1
```

---

## Pipeline Summary

```
Post filtering
  └─ Valence filtering
       ├─ Element presence → binary metrics
       └─ Subelement classification → multi-class F1
```

---

# 3. Task 1.2 — Presence Rating

## Overview

Evaluates **ordinal prediction (1–5)** per self-state.

---

## Step 1: Post Filtering

Same as Task 1.1.

---

## Step 2: Per-Valence Filtering

Only valences with gold Presence are evaluated.

---

## Step 3: Pair Collection

| Post | Valence     | Gold | Pred |
| ---- | ----------- | ---- | ---- |
| 1    | adaptive    | 3    | 3    |
| 1    | maladaptive | 4    | 2    |
| 2    | maladaptive | 2    | 3    |

### Default Rule

If prediction is missing:

```
Pred Presence = 1
```

---

## Step 4: Metrics

| Metric   | Description              |
| -------- | ------------------------ |
| MAE      | Mean Absolute Error      |
| RMSE     | Root Mean Squared Error  |
| QWK      | Quadratic Weighted Kappa |
| Spearman | Rank correlation         |

Computed for:

* Adaptive
* Maladaptive
* Combined

---

## 🔑 Task 1.2 Ranking

```
Ranking = mean(Adaptive RMSE, Maladaptive RMSE)
(lower is better)
```

---

## Pipeline Summary

```
Post filtering
  └─ Valence filtering
       └─ Pair collection
            └─ Metrics (MAE, RMSE, QWK, Spearman)
```

---

# 4. Task 2 — Moments of Change

## Overview

Binary classification per post:

* Switch
* Escalation

---

## Step 1: Post Filtering

```
ALL posts are evaluated
```

---

## Step 2: Label Parsing

| Value | Binary |
| ----- | ------ |
| S / E | 1      |
| 0     | 0      |

---

# Post-Level Evaluation

All posts pooled together.

Metrics per label:

* Precision
* Recall
* F1

```
Macro F1 = mean(Switch F1, Escalation F1)
```

---

# Timeline-Level Evaluation

* Group posts by `timeline_id`
* Compute metrics per timeline
* Macro-average across timelines

---

## Edge Case

If no positives in both gold and prediction:

```
Score = 1.0
```

---

## 🔑 Task 2 Ranking

```
Ranking = mean(Post-level Macro F1, Timeline-level Macro F1)
```

---

## Pipeline Summary

```
All posts
  ├─ Post-level metrics
  └─ Timeline-level metrics
```

---

# 5. Subelement Schema

## Adaptive

| Element | Classes                                                |
| ------- | ------------------------------------------------------ |
| A       | Calm, Sad, Happy, Vigor, Justified anger, Proud, Loved |
| B-O     | Relating, Autonomous                                   |
| B-S     | Self-care                                              |
| C-O     | Related, Facilitate autonomy                           |
| C-S     | Self-acceptance                                        |
| D       | Relatedness, Autonomy, Competence                      |

---

## Maladaptive

| Element | Classes                                                      |
| ------- | ------------------------------------------------------------ |
| A       | Anxious, Depressed, Mania, Apathetic, Angry, Ashamed, Lonely |
| B-O     | Fight/flight, Overcontrolled                                 |
| B-S     | Self-harm                                                    |
| C-O     | Detached/over-attached, Blocking autonomy                    |
| C-S     | Self-criticism                                               |
| D       | Relatedness unmet, Autonomy unmet, Competence unmet          |

---

# 6. Submission Format

## Task 1 (`task1_pred.json`)

```json
{
  "timeline_id": "...",
  "post_id": "...",
  "adaptive-state": {
    "A": {"subelement": 3},
    "Presence": 3
  },
  "maladaptive-state": {
    "Presence": 2
  }
}
```

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

## ⚠️ Privacy Rule

Do **NOT** include post text fields:

```
post, text, body → forbidden
```

---

# 7. Running Evaluation

```bash
python evaluate_task1.py --gold-dir <gold_dir> --pred-file task1_pred.json

python evaluate_task2.py --gold-dir <gold_dir> --pred-file task2_pred.json

python run_evaluation.py \
  --gold-dir <gold_dir> \
  --task1-pred task1_pred.json \
  --task2-pred task2_pred.json \
  --output scores.txt
```

---

# 8. Environment

| Component | Version |
| --------- | ------- |
| Python    | 3.7.3   |
| numpy     | 1.17.2  |
| sklearn   | 0.21.3  |
| scipy     | 1.3.1   |

Docker:

```
codalab/codalab-legacy:py37
```

---

# 9. Metric Key Names

| Prefix | Meaning                   |
| ------ | ------------------------- |
| t1ep   | Element presence          |
| t1sc   | Subelement classification |
| t1pr   | Presence rating           |
| t2pl   | Post-level                |
| t2tl   | Timeline-level            |

---

## Ranking Keys

| Key         | Meaning                 |
| ----------- | ----------------------- |
| `t1_1_rank` | Subelement Avg Macro F1 |
| `t1_2_rank` | Avg RMSE                |
| `t2_rank`   | Avg Macro F1            |

---

# Final Summary

```
Task 1.1 → classification (binary + multi-class)
Task 1.2 → ordinal regression
Task 2   → binary detection (post + timeline)

Each task has its own ranking metric.
```
