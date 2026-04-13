# CLPsych 2026 Shared Task — Evaluation Guideline (v9, Task 3.1 CS-fixed)

## 1. Evaluation Metrics

### Task 1.1 — ABCD Element & Subelement Classification

Each post may contain an adaptive and/or maladaptive self-state. Within each self-state, up to 6 ABCD elements (`A`, `B-O`, `B-S`, `C-O`, `C-S`, `D`) may be present. Each present element must receive exactly one valid subelement label from the element-specific schema.

#### Element Presence (binary)

Each of the 6 elements × 2 valences gives **12 binary classifications**.

Metrics computed:
- Per-element Precision, Recall, F1
- Per-valence (adaptive/maladaptive) Macro F1 and Micro F1
- Avg Macro F1 / Avg Micro F1 (mean of adaptive and maladaptive)
- Overall Macro F1 / Overall Micro F1 across all 12 element-valence pairs

#### Subelement Classification (multi-class)

Each element is a multi-class classification over its **valid subelement labels for that element and valence**.  
Class `0` (element absent) is excluded from subelement scoring because element presence is evaluated separately.

Metrics computed:
- Per-element Macro F1 and Micro F1 across valid subelement classes
- Per-valence (adaptive/maladaptive) Macro F1 and Micro F1
- Avg Macro F1 / Avg Micro F1 (mean of adaptive and maladaptive)
- Overall Macro F1 / Overall Micro F1 across all 12 element-valence pairs

#### Ranking metric — aggregation

Ranking uses **subelement classification only**. Element presence is **not** used for ranking.

1. Compute subelement classification **Macro F1 per element** (12 total: 6 adaptive + 6 maladaptive)
2. **Macro-average** across the 6 elements within each valence  
   → Adaptive Macro F1, Maladaptive Macro F1
3. Average Adaptive Macro F1 and Maladaptive Macro F1

```text
Task 1.1 Ranking = Subelement Classification Avg Macro F1
````

---

### Task 1.2 — Presence Rating

Each self-state (adaptive/maladaptive) has a **Presence** rating on a 1–5 ordinal scale measuring psychological centrality.

Metrics reported separately for **adaptive**, **maladaptive**, and **combined**:

* **MAE** (Mean Absolute Error)
* **RMSE** (Root Mean Squared Error)
* **QWK** (Quadratic Weighted Kappa)
* **Spearman correlation**

```text
Task 1.2 Ranking = mean(Adaptive RMSE, Maladaptive RMSE)
```

Lower is better.

---

### Task 2 — Moments of Change (Switch & Escalation)

Switch and Escalation are evaluated as independent binary classifications. A post can have:

* neither
* only Switch
* only Escalation
* both

#### Post-level evaluation

All posts are pooled together.

Reported:

* Per-label (Switch, Escalation): Precision, Recall, F1
* Macro F1 = mean of Switch F1 and Escalation F1

#### Timeline-level evaluation

Metrics are computed per timeline, then macro-averaged across timelines.

Reported:

* Per-label: Precision, Recall, F1 averaged over timelines
* Macro F1 = mean of Switch F1 and Escalation F1
* Timelines with no positive events in both gold and prediction receive a score of `1.0`

```text
Task 2 Ranking = mean(Post-level Macro F1, Timeline-level Macro F1)
```

---

### Task 3.1 — Sequence Summary Evaluation

Task 3.1 evaluates **Sequence Summary** quality using four complementary metrics:

* **CS (Consistency Score)** — NLI consistency (`1 − mean contradiction`); higher is better
* **CT (Contradiction Top)** — NLI contradiction max; lower is better
* **ROUGE-L Recall** — lexical/temporal coverage; higher is better
* **BERTScore Recall** — semantic coverage; higher is better

#### v2 change: CS definition fix

In earlier wording, CS was described as raw contradiction mean.
This is corrected here to match the CLPsych 2025 definition and implementation:

```text
CS = 1 − mean contradiction
```

That is, CS is a **consistency** score, so **higher is better**.

#### Prediction truncation (350 words)

Before scoring, each predicted summary is truncated to the first **350 words**. This:

* prevents gaming recall metrics with overly long predictions
* supports the use of recall-oriented metrics
* is enforced automatically in the evaluation code

#### CS and CT

These follow CLPsych 2025 Task B.

* Model: `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli`
* Direction: **gold = premise**, **prediction = hypothesis**

**CS**:
For each predicted sentence:

1. compute contradiction probability against each gold sentence
2. take the **mean** contradiction probability across gold sentences
3. convert to consistency as `1 − mean contradiction`

Then average over predicted sentences.

**CT**:
For each predicted sentence:

1. compute contradiction probability against each gold sentence
2. take the **max** contradiction probability across gold sentences

Then average over predicted sentences.

#### ROUGE-L Recall

ROUGE-L Recall is computed as longest common subsequence recall between the full gold summary and the truncated predicted summary at the word level:

```text
ROUGE-L Recall = LCS(gold, pred) / len(gold_words)
```

This captures how well the predicted summary covers temporal progression and dynamic keywords present in the gold summary.

#### BERTScore Recall

Adapted from CLPsych 2025 Task A evidence extraction.

* Model: `microsoft/deberta-xlarge-mnli`
* Baseline rescaling: enabled

For each gold sentence `g_i`, compute BERTScore F1 against all predicted sentences and take the maximum:

```text
BERTScore_Recall(g_i) = max_j BERTScore_F1(g_i, s_j)
```

Then average across gold sentences:

```text
BERTScore_Recall = (1/m) * sum_i BERTScore_Recall(g_i)
```

This measures whether the semantic content of each gold sentence is covered somewhere in the prediction, including paraphrases.

#### Edge cases

| Condition              | CS              | CT              | ROUGE-L         | BERTScore       |
| ---------------------- | --------------- | --------------- | --------------- | --------------- |
| Empty prediction       | 0.0             | 1.0             | 0.0             | 0.0             |
| Empty gold             | 1.0             | 0.0             | 0.0             | 0.0             |
| Prediction > 350 words | Truncated first | Truncated first | Truncated first | Truncated first |

```text
Task 3.1 Ranking = t3_cs
```

Higher is better.

---

### Task 3.2 — Identifying Recurrent Dynamic Signatures of Change Across Timelines

Task 3.2 evaluates proposed **Signatures of Deterioration** and **Signatures of Improvement** through **human evaluation**, separately for deterioration and improvement.

Each submitted signature is evaluated on three criteria:

#### 1. Fit of Evidence Support

**Definition:** how well the proposed signature is supported by the submitted sequences. A strong signature is one whose supporting sequences clearly express the same proposed dynamic.

This criterion includes both:

* correctness
* coherence of evidence support

Incoherence refers to cases where the submitted supporting sequences reflect different phenomena that should be treated as separate signatures.

**Evaluation:** evaluators inspect the supporting sequences and judge how many genuinely support the proposed signature. A higher proportion of supporting sequences that fit the proposed signature yields a higher score.

#### 2. Recurrence

**Definition:** how recurrent the proposed signature is across sequences. A minimum of **2 occurrences** is required for a signature to be considered recurrent.

**Evaluation:** after excluding sequences that do not fit under **Fit of Evidence Support**, recurrence is calculated as the number of remaining valid supporting sequences. A higher number indicates a more recurrent pattern.

#### 3. Specificity

**Definition:** how specific, fine-grained, and non-generic the proposed signature is.

A strong signature should describe an informative dynamic pattern rather than a broad description that could apply to many cases. Signatures that clearly capture both:

* within-self-state dynamics
* between-self-state dynamics

will generally be considered more specific, provided both are supported by the evidence.

**Evaluation:** judges assess how precise and informative the wording of the signature is. Specificity is evaluated independently of recurrence.

#### Final ranking

Each signature receives a **Best-Worst Scaling (BWS)-derived score** for each criterion based on comparative human judgments.

```text
Task 3.2 Ranking = 0.5 * Fit + 0.5 * HarmonicMean(Recurrence, Specificity)
```

This rewards signatures that are both well-supported and recurrent/specific.

---

### Post Filtering

* **Task 1**: Only posts with annotated evidence in the gold data are evaluated, meaning posts where at least one of `adaptive-state.Presence` or `maladaptive-state.Presence` has a valid numeric value. Posts with empty evidence are skipped.
* **Task 2**: **All posts** are evaluated.
* **Task 3.1**: All evaluated sequence summaries are scored. Predicted summaries are truncated to the first **350 words** before scoring.
* **Task 3.2**: No held-out Task 3.2 test set is used. Participants derive signatures from the designated training resources and submit them for human evaluation.

---

## 2. Environment

| Component    | Value                         |
| ------------ | ----------------------------- |
| Docker image | `codalab/codalab-legacy:py37` |
| Python       | 3.7.3                         |
| numpy        | 1.17.2 (pre-installed)        |
| scikit-learn | 0.21.3 (pre-installed)        |
| scipy        | 1.3.1 (pre-installed)         |

All dependencies are pre-installed in the Docker image. No additional `pip install` is required.

---

## 3. Task 3 Models

| Metric    | Model                                                      | Size    |
| --------- | ---------------------------------------------------------- | ------- |
| CS, CT    | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` | ~1.7 GB |
| BERTScore | `microsoft/deberta-xlarge-mnli`                            | ~1.4 GB |

---

## 4. Submission Format

Participants submit **separate ZIP files** for Task 1, Task 2, and Task 3.1 on their respective Codabench pages.

Task 3.2 is submitted separately by email.

### Required archive structure

#### Task 1 submission

```text
predictions.zip
|- task1_pred.json
```

#### Task 2 submission

```text
predictions.zip
|- task2_pred.json
```

#### Task 3.1 submission

```text
predictions.zip
|- task3_pred.json
```

### Important — Privacy

Do **not** include post text fields such as:

* `post`
* `text`
* `body`

These must be removed before submission.

### Note

Participants may submit predictions for one or more tasks.
If a prediction file for a task is not provided, that task is skipped and only the available task(s) are scored.

### Task 1 Submission (`task1_pred.json`)

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

#### Field constraints

| Field                          | Type          | Required                   | Description                                      |
| ------------------------------ | ------------- | -------------------------- | ------------------------------------------------ |
| `timeline_id`                  | string        | Yes                        | Must match a timeline in the test data           |
| `post_id`                      | string        | Yes                        | Must match a post in the test data               |
| `adaptive-state`               | object        | No                         | Omit entirely if no adaptive state predicted     |
| `maladaptive-state`            | object        | No                         | Omit entirely if no maladaptive state predicted  |
| `{state}.Presence`             | integer (1–5) | Yes, if state is present   | Psychological centrality rating                  |
| `{state}.{element}`            | object        | No                         | Omitted elements are scored as not present       |
| `{state}.{element}.subelement` | integer       | Yes, if element is present | Must be a valid label for this element × valence |

#### Additional rules

* **Elements**: `A`, `B-O`, `B-S`, `C-O`, `C-S`, `D`
* Exactly **one subelement per element per valence**
* Include **only elements predicted as present**
* Only include entries for posts that have annotated evidence in the gold data
  → Posts without gold evidence are **ignored during evaluation**

### Task 2 Submission (`task2_pred.json`)

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

#### Field constraints

| Field         | Type   | Required | Description                                   |
| ------------- | ------ | -------- | --------------------------------------------- |
| `timeline_id` | string | Yes      | Must match a timeline in the test data        |
| `post_id`     | string | Yes      | Must match a post in the test data            |
| `Switch`      | string | Yes      | `"S"` for switch, `"0"` for no switch         |
| `Escalation`  | string | Yes      | `"E"` for escalation, `"0"` for no escalation |

#### Additional rules

* Must include **one entry for every post in the test data**
* All timelines must be merged into a **single JSON array**
* No grouping or nesting by timeline
* Switch and Escalation are **independent labels**

  * A post may be:

    * neither
    * Switch only
    * Escalation only
    * both `"S"` and `"E"`

### Task 3.1 Submission (`task3_pred.json`)

A JSON array. Each entry corresponds to one predicted sequence summary.

```json
[
  {
    "timeline_id": "3db8573df5",
    "summary": "The sequence begins with..."
  },
  {
    "timeline_id": "91b6a42835",
    "summary": "Across the sequence..."
  }
]
```

#### Field constraints

| Field         | Type   | Required | Description                                                    |
| ------------- | ------ | -------- | -------------------------------------------------------------- |
| `timeline_id` | string | Yes      | Must match a sequence/timeline in the Task 3.1 evaluation data |
| `summary`     | string | Yes      | Predicted sequence summary                                     |

#### Additional rules

* One summary per evaluated sequence
* Predictions longer than **350 words** are automatically truncated before scoring
* Empty predictions receive the defined edge-case scores

### Task 3.2 Submission

There is **no separate training or test dataset** for Task 3.2.

Participants should use:

* the training data provided for **Task 3.1**, including the provided sequence summaries
* and may also use the training data from **Task 1** and **Task 2**

Using this data, participants must extract:

* **Signatures of Deterioration**
* **Signatures of Improvement**

The test data used in Task 1, Task 2, and Task 3.1 will **not** be used for Task 3.2.

Task 3.2 outputs must be submitted **via email** in the specified JSON format for human evaluation to both:

* `iqra.ali@qmul.ac.uk`
* `t.tseriotou@qmul.ac.uk`

---

## 5. Submission Validation Script

A local validation script (`validate_submission.py`) is provided for participants to check their submission files before uploading. It requires no dependencies beyond Python 3.

It checks:

* **Privacy**: warns if entries contain post text fields such as `post`, `text`, `body`
* **Task 1**:

  * required fields (`timeline_id`, `post_id`)
  * at least one valence present per entry
  * `Presence` is an integer in `1–5`
  * element keys are valid
  * each element has a `subelement` integer within the valid range for that element × valence
  * no duplicate entries
* **Task 2**:

  * required fields
  * `Switch` is `"0"` or `"S"`
  * `Escalation` is `"0"` or `"E"`
  * no duplicate entries
* **Task 3.1**:

  * required fields
  * valid `timeline_id`
  * `summary` present and string-typed
  * no duplicate entries
* **Coverage** (optional, with `--test-dir`):

  * verifies every test post/sequence is covered where applicable
  * checks that no extra items are included

```bash
# Format checks only
python validate_submission.py --task1 task1_pred.json --task2 task2_pred.json --task3 task3_pred.json

# Format + coverage checks against test data
python validate_submission.py --task1 task1_pred.json --task2 task2_pred.json --task3 task3_pred.json --test-dir <test_data_dir>
```

---

## 6. Running the Evaluation Locally

```bash
# Task 1 only
python evaluate_task1.py --gold-dir <gold_dir> --pred-file task1_pred.json

# Task 2 only
python evaluate_task2.py --gold-dir <gold_dir> --pred-file task2_pred.json

# Task 3.1 only
python evaluate_task3.py --gold-dir <gold_dir> --pred-file task3_pred.json

# Tasks 1 + 2 + 3.1 — scores.txt output (Codabench format)
python run_evaluation.py --gold-dir <gold_dir> \
    --task1-pred task1_pred.json \
    --task2-pred task2_pred.json \
    --task3-pred task3_pred.json \
    --output scores.txt

# Also save nested JSON for debugging
python run_evaluation.py --gold-dir <gold_dir> \
    --task1-pred task1_pred.json \
    --task2-pred task2_pred.json \
    --task3-pred task3_pred.json \
    --output scores.txt --json-output results.json
```

`<gold_dir>` is a directory containing gold-standard JSON files.

If a prediction file is missing or not provided, that task is skipped gracefully and scores are produced only for the available task(s).

---

## 7. scores.txt Key Names

All metric key names are kept at **36 characters or fewer** for Codabench compatibility. Output format is:

```text
key: value
```

one metric per line.

### Prefix convention

| Prefix    | Meaning                                  |
| --------- | ---------------------------------------- |
| `t1ep`    | Task 1.1 Element Presence                |
| `t1sc`    | Task 1.1 Subelement Classification       |
| `t1pr`    | Task 1.2 Presence Rating                 |
| `t2pl`    | Task 2 Post-Level                        |
| `t2tl`    | Task 2 Timeline-Level                    |
| `t2_comb` | Task 2 Combined (ranking-related fields) |
| `t3`      | Task 3.1 Sequence Summary                |

### Common abbreviations

* `ada` = adaptive
* `mal` = maladaptive
* `avg` = average
* `comb` = combined
* `maF1` = macro F1
* `miF1` = micro F1
* `prec` = precision
* `rec` = recall
* `sup` = support
* `sw` = Switch
* `esc` = Escalation
* `spear` = Spearman
* `BO/BS/CO/CS` = `B-O` / `B-S` / `C-O` / `C-S`

### Ranking keys

| Key         | Formula                                 | Description      |
| ----------- | --------------------------------------- | ---------------- |
| `t1_1_rank` | `t1sc_avg_maF1`                         | Task 1.1 ranking |
| `t1_2_rank` | (`t1pr_ada_rmse` + `t1pr_mal_rmse`) / 2 | Task 1.2 ranking |
| `t2_rank`   | (`t2pl_maF1` + `t2tl_maF1`) / 2         | Task 2 ranking   |
| `t3_rank`   | `t3_cs`                                 | Task 3.1 ranking |

### Task 3.1 keys

| Key                   | Description                     | Direction       |
| --------------------- | ------------------------------- | --------------- |
| `t3_cs`               | Mean CS (consistency)           | Higher = better |
| `t3_ct`               | Mean CT                         | Lower = better  |
| `t3_rouge_l_recall`   | Mean ROUGE-L Recall             | Higher = better |
| `t3_bertscore_recall` | Mean BERTScore Recall           | Higher = better |
| `t3_n_seq`            | Number of sequences             | —               |
| `t3_n_trunc`          | Number of truncated predictions | —               |
| `t3_rank`             | `t3_cs`                         | Higher = better |

See `SCORES_KEY.md` for the complete key reference.

---

## 8. Subelement Schema

### Adaptive State

| Element | # | Subelements                                                                                                                                                                                                           |
| ------- | - | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A       | 7 | 1 = Calm / laid back, 3 = Sad, emotional pain, grieving, 5 = Content, happy, joy, hopeful, 7 = Vigor / energetic, 9 = Justifiable anger / assertive anger / justifiable outrage, 11 = Proud, 13 = Feel loved / belong |
| B-O     | 2 | 1 = Relating behavior, 3 = Autonomous or adaptive control behavior                                                                                                                                                    |
| B-S     | 1 | 1 = Self-care and improvement                                                                                                                                                                                         |
| C-O     | 2 | 1 = Perception of the other as related, 3 = Perception of the other as facilitating autonomy needs                                                                                                                    |
| C-S     | 1 | 1 = Self-acceptance and compassion                                                                                                                                                                                    |
| D       | 3 | 1 = Relatedness, 3 = Autonomy and adaptive control, 5 = Competence / self-esteem / self-care                                                                                                                          |

### Maladaptive State

| Element | # | Subelements                                                                                                                                                                                             |
| ------- | - | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A       | 7 | 2 = Anxious / fearful / tense, 4 = Depressed / despair / hopeless, 6 = Mania, 8 = Apathic / don’t care / blunted, 10 = Angry (aggression) / disgust / contempt, 12 = Ashamed / guilty, 14 = Feel lonely |
| B-O     | 2 | 2 = Fight or flight behavior, 4 = Over-controlled or controlling behavior                                                                                                                               |
| B-S     | 1 | 2 = Self-harm, neglect, and avoidance                                                                                                                                                                   |
| C-O     | 2 | 2 = Perception of the other as detached or over-attached, 4 = Perception of the other as blocking autonomy needs                                                                                        |
| C-S     | 1 | 2 = Self-criticism                                                                                                                                                                                      |
| D       | 3 | 2 = Expectation that relatedness needs will not be met, 4 = Expectation that autonomy needs will not be met, 6 = Expectation that competence needs will not be met                                      
