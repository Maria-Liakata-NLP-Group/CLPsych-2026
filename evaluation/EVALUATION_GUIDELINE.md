# CLPsych 2026 Shared Task — Evaluation Guideline (v8)

## 1. Evaluation Metrics

### Task 1.1 — ABCD Element & Subelement Classification

Each post may contain an adaptive and/or maladaptive self-state. Within each self-state, up to 6 ABCD elements (A, B-O, B-S, C-O, C-S, D) may be present, each with exactly one subelement selected from an element-specific set of categories.

**Element Presence (binary):**
Each of the 6 elements × 2 valences = 12 binary classifications. Metrics computed:
- Per-element Precision, Recall, F1
- Per-valence (adaptive/maladaptive) Macro F1 and Micro F1
- Avg Macro/Micro F1 (mean of adaptive and maladaptive)
- Overall Macro/Micro F1 across all 12 element-valence pairs

**Subelement Classification (multi-class):**
Each element is a multi-class classification over its valid subelement categories (e.g., A has classes 1–7). Class 0 (element absent) is excluded since element presence is evaluated separately. Metrics computed:
- Per-element Macro F1 and Micro F1 (across subelement classes)
- Per-valence (adaptive/maladaptive) Macro F1 and Micro F1
- Avg Macro/Micro F1 (mean of adaptive and maladaptive)
- Overall Macro/Micro F1 across all 12 element-valence pairs

**Ranking metric — aggregation (subelement classification only; element presence is not used for ranking):**
1. Compute subelement classification **Macro F1 per element** (12 total: 6 adaptive + 6 maladaptive)
2. **Macro** average across 6 elements within each valence → Adaptive Macro F1, Maladaptive Macro F1
3. Average of Adaptive and Maladaptive Macro F1 → **Ranking = Subelement Classification Avg Macro F1**

### Task 1.2 — Presence Rating

Each self-state (adaptive/maladaptive) has a Presence rating on a 1–5 ordinal scale measuring psychological centrality.

Metrics (reported separately for adaptive, maladaptive, and combined):
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **QWK** (Quadratic Weighted Kappa) — standard for ordinal agreement
- **Spearman correlation**

**Ranking = mean(Adaptive RMSE, Maladaptive RMSE)** — lower is better.

### Task 2 — Moments of Change (Switch & Escalation)

Switch and Escalation are evaluated as independent binary classifications. A post can have both.

**Post-level evaluation** (all posts pooled):
- Per-label (Switch, Escalation): Precision, Recall, F1
- Macro F1 = mean of Switch F1 and Escalation F1

**Timeline-level evaluation** (per-timeline metrics, macro-averaged across timelines):
- Per-label: Precision, Recall, F1 averaged over all timelines
- Macro F1 = mean of Switch F1 and Escalation F1
- Timelines with no positive events in both gold and prediction score 1.0

**Ranking = mean(Post-level Macro F1, Timeline-level Macro F1)**

### Post Filtering

- **Task 1**: Only posts with annotated evidence in the gold data are evaluated (i.e., posts where at least one of adaptive-state or maladaptive-state has a valid numeric `Presence` value). Posts with empty evidence are skipped.
- **Task 2**: ALL posts are evaluated. Switch/Escalation labels are always present.

---

## 2. Environment

| Component | Value |
|-----------|-------|
| Docker image | `codalab/codalab-legacy:py37` |
| Python | 3.7.3 |
| numpy | 1.17.2 (pre-installed) |
| scikit-learn | 0.21.3 (pre-installed) |
| scipy | 1.3.1 (pre-installed) |

All dependencies are pre-installed in the Docker image. No additional `pip install` is required.

---

# 8. Subelement Schema

## Adaptive State

| Element | # | Subelements                                                                                                                                                                                                  |
| ------- | - | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| A       | 7 | 1=Calm / laid back, 3=Sad / emotional pain / grieving, 5=Content / happy / joy / hopeful, 7=Vigor / energetic, 9=Justifiable anger / assertive anger / justifiable outrage, 11=Proud, 13=Feel loved / belong |
| B-O     | 2 | 1=Relating behavior, 3=Autonomous or adaptive control behavior                                                                                                                                               |
| B-S     | 1 | 1=Self care and improvement                                                                                                                                                                                  |
| C-O     | 2 | 1=Perception of the other as related, 3=Perception of the other as facilitating autonomy needs                                                                                                               |
| C-S     | 1 | 1=Self-acceptance and compassion                                                                                                                                                                             |
| D       | 3 | 1=Relatedness, 3=Autonomy and adaptive control, 5=Competence / self esteem / self-care                                                                                                                       |

## Maladaptive State

| Element | # | Subelements                                                                                                                                                                               |
| ------- | - | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A       | 7 | 2=Anxious / fearful / tense, 4=Depressed / despair / hopeless, 6=Mania, 8=Apathic / don’t care / blunted, 10=Angry / aggression / disgust / contempt, 12=Ashamed / guilty, 14=Feel lonely |
| B-O     | 2 | 2=Fight or flight behavior, 4=Over controlled or controlling behavior                                                                                                                     |
| B-S     | 1 | 2=Self harm, neglect and avoidance                                                                                                                                                        |
| C-O     | 2 | 2=Perception of the other as detached or over attached, 4=Perception of the other as blocking autonomy needs                                                                              |
| C-S     | 1 | 2=Self criticism                                                                                                                                                                          |
| D       | 3 | 2=Expectation that relatedness needs will not be met, 4=Expectation that autonomy needs will not be met, 6=Expectation that competence needs will not be met                              |

---

## 4. Submission Format

Participants submit **separate ZIP files** for Task 1 and Task 2 on their respective Codabench pages.



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



## Important — Privacy

Do **not** include post text fields such as:

* `post`
* `text`
* `body`

These must be removed before submission.



## Note

Participants may submit predictions for one or both tasks.
If a prediction file for a task is not provided, that task will be skipped and only the other task will be scored.



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
  },
  {
    "timeline_id": "306d938d4b",
    "post_id": "308b0c2c6c",
    "adaptive-state": {
      "Presence": 2,
      "B-S": { "subelement": 1 },
      "B-O": { "subelement": 1 }
    },
    "maladaptive-state": {
      "Presence": 2,
      "A": { "subelement": 2 }
    }
  }
]
```


### Field constraints

| Field                          | Type          | Required                   | Description                                      |
| ------------------------------ | ------------- | -------------------------- | ------------------------------------------------ |
| `timeline_id`                  | string        | Yes                        | Must match a timeline in the test data           |
| `post_id`                      | string        | Yes                        | Must match a post in the test data               |
| `adaptive-state`               | object        | No                         | Omit entirely if no adaptive state predicted     |
| `maladaptive-state`            | object        | No                         | Omit entirely if no maladaptive state predicted  |
| `{state}.Presence`             | integer (1–5) | Yes, if state is present   | Psychological centrality rating                  |
| `{state}.{element}`            | object        | No                         | Omitted elements will be scored as not present   |
| `{state}.{element}.subelement` | integer       | Yes, if element is present | Must be a valid index for this element × valence |


### Additional rules

* **Elements**: `A`, `B-O`, `B-S`, `C-O`, `C-S`, `D`
* Exactly **one subelement per element per valence**
* Include **only elements predicted as present**
* Only include entries for posts that have annotated evidence in the gold data
  → Posts without gold evidence are **ignored during evaluation**

## Task 2 Submission (`task2_pred.json`)

A JSON array. Each entry corresponds to one post with Switch and Escalation labels.

All posts from all timelines must be included in a **single flat list**.

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


### Field constraints

| Field         | Type   | Required | Description                                   |
| ------------- | ------ | -------- | --------------------------------------------- |
| `timeline_id` | string | Yes      | Must match a timeline in the test data        |
| `post_id`     | string | Yes      | Must match a post in the test data            |
| `Switch`      | string | Yes      | `"S"` for switch, `"0"` for no switch         |
| `Escalation`  | string | Yes      | `"E"` for escalation, `"0"` for no escalation |


### Additional rules

* Must include **one entry for every post in the test data**
* All timelines must be merged into a **single JSON array**
* No grouping or nesting by timeline
* Switch and Escalation are **independent labels**

  * A post may be:

    * neither
    * Switch only
    * Escalation only
    * both `"S"` and `"E"`

---

## 5. Submission Validation Script

A local validation script (`validate_submission.py`) is provided for participants to check their submission files before uploading. It requires no dependencies beyond Python 3 and checks:

- **Privacy**: warns if submission entries contain post text fields (e.g., `post`, `text`, `body`)
- **Task 1**: required fields (`timeline_id`, `post_id`), at least one valence present per entry, `Presence` is integer 1-5, element keys are valid, each element has a `subelement` integer within the valid range for that element x valence, no duplicate entries
- **Task 2**: required fields, `Switch` is `"0"` or `"S"`, `Escalation` is `"0"` or `"E"`, no duplicate entries
- **Coverage** (optional, with `--test-dir`): verifies every test post is covered and no extra posts are included

```bash
# Format checks only
python validate_submission.py --task1 task1_pred.json --task2 task2_pred.json

# Format + coverage checks against test data
python validate_submission.py --task1 task1_pred.json --task2 task2_pred.json --test-dir <test_data_dir>
```

---

## 6. Running the Evaluation Locally

```bash
# Task 1 only
python evaluate_task1.py --gold-dir <gold_dir> --pred-file task1_pred.json

# Task 2 only
python evaluate_task2.py --gold-dir <gold_dir> --pred-file task2_pred.json

# Both tasks — scores.txt output (Codabench format)
python run_evaluation.py --gold-dir <gold_dir> \
    --task1-pred task1_pred.json \
    --task2-pred task2_pred.json \
    --output scores.txt

# Also save nested JSON for debugging
python run_evaluation.py --gold-dir <gold_dir> \
    --task1-pred task1_pred.json \
    --task2-pred task2_pred.json \
    --output scores.txt --json-output results.json
```

`<gold_dir>` is a directory containing gold-standard timeline JSON files (one `*.json` per timeline).

If a prediction file is missing or not provided, that task is skipped gracefully and scores are produced only for the available task(s).

---

## 7. Scores.txt Key Names

All metric key names are ≤36 characters for Codabench compatibility. The output file uses `key: value` format, one metric per line.

**Prefix convention:**

| Prefix | Meaning |
|--------|---------|
| `t1ep` | Task 1.1 Element Presence |
| `t1sc` | Task 1.1 Subelement Classification |
| `t1pr` | Task 1.2 Presence Rating |
| `t2pl` | Task 2 Post-Level |
| `t2tl` | Task 2 Timeline-Level |
| `t2_comb` | Task 2 Combined (for ranking) |

**Common abbreviations:** `ada` = adaptive, `mal` = maladaptive, `avg` = average, `comb` = combined, `maF1` = macro F1, `miF1` = micro F1, `prec` = precision, `rec` = recall, `sup` = support, `sw` = Switch, `esc` = Escalation, `spear` = Spearman, `BO/BS/CO/CS` = B-O/B-S/C-O/C-S.

**Ranking keys (one per task):**

| Key | Formula | Description |
|-----|---------|-------------|
| `t1_1_rank` | `t1sc_avg_maF1` | Task 1.1: subelement classification Avg Macro F1 |
| `t1_2_rank` | (`t1pr_ada_rmse` + `t1pr_mal_rmse`) / 2 | Task 1.2: avg RMSE across adaptive + maladaptive (lower is better) |
| `t2_rank` | (`t2pl_maF1` + `t2tl_maF1`) / 2 | Task 2: avg of post-level + timeline-level macro F1 |

See `SCORES_KEY.md` for the complete key reference.
