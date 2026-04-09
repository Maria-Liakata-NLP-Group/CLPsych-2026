# Scores.txt Key Reference (v7)

All metric keys are ≤36 characters for Codabench compatibility.

## Naming Convention


| Prefix    | Meaning                                            |
| --------- | -------------------------------------------------- |
| `t1ep`    | Task 1.1 — Element Presence (binary)               |
| `t1sc`    | Task 1.1 — Subelement Classification (multi-class) |
| `t1pr`    | Task 1.2 — Presence Rating (1-5 scale)             |
| `t2pl`    | Task 2 — Post-Level                                |
| `t2tl`    | Task 2 — Timeline-Level                            |
| `t2_comb` | Task 2 — Combined (for ranking)                    |



| Abbreviation | Meaning                                     |
| ------------ | ------------------------------------------- |
| `ada`        | adaptive-state                              |
| `mal`        | maladaptive-state                           |
| `avg`        | average of adaptive and maladaptive         |
| `comb`       | combined                                    |
| `maF1`       | macro F1                                    |
| `miF1`       | micro F1                                    |
| `prec`       | precision                                   |
| `rec`        | recall                                      |
| `sup`        | support (number of gold-positive instances) |
| `sw`         | Switch                                      |
| `esc`        | Escalation                                  |
| `spear`      | Spearman correlation                        |
| `n_tl`       | number of timelines                         |
| `sup_pos`    | support (gold-positive count)               |
| `sup_tot`    | support (total count)                       |


Element abbreviations: `A`, `BO` (B-O), `BS` (B-S), `CO` (C-O), `CS` (C-S), `D`

---

## Task 1.1 — Element Presence (`t1ep_*`)

### Per-element (12 elements × 4 metrics = 48 keys)

Format: `t1ep_{valence}_{element}_{metric}`


| Example Key       | Description                                     |
| ----------------- | ----------------------------------------------- |
| `t1ep_ada_A_prec` | Adaptive Affect — precision                     |
| `t1ep_ada_A_rec`  | Adaptive Affect — recall                        |
| `t1ep_ada_A_f1`   | Adaptive Affect — F1                            |
| `t1ep_ada_A_sup`  | Adaptive Affect — support (gold-positive count) |
| `t1ep_mal_BO_f1`  | Maladaptive Behavior-Other — F1                 |


### Aggregates (8 keys)


| Key             | Description                                                   |
| --------------- | ------------------------------------------------------------- |
| `t1ep_ada_maF1` | Adaptive macro F1 (mean of 6 adaptive element F1s)            |
| `t1ep_ada_miF1` | Adaptive micro F1 (pooled across 6 adaptive elements)         |
| `t1ep_mal_maF1` | Maladaptive macro F1                                          |
| `t1ep_mal_miF1` | Maladaptive micro F1                                          |
| `t1ep_avg_maF1` | Average macro F1 (mean of adaptive + maladaptive)             |
| `t1ep_avg_miF1` | Average micro F1 (mean of adaptive + maladaptive)             |
| `t1ep_maF1`     | Overall macro F1 (mean across all 12 element-valence pairs)   |
| `t1ep_miF1`     | Overall micro F1 (pooled across all 12 element-valence pairs) |


---

## Task 1.1 — Subelement Classification (`t1sc_*`)

### Per-element (12 elements × 3 metrics = 36 keys)

Format: `t1sc_{valence}_{element}_{metric}`


| Example Key       | Description                                          |
| ----------------- | ---------------------------------------------------- |
| `t1sc_ada_A_maF1` | Adaptive Affect — macro F1 across subelement classes |
| `t1sc_ada_A_miF1` | Adaptive Affect — micro F1 across subelement classes |
| `t1sc_ada_A_sup`  | Adaptive Affect — support (gold-positive count)      |


### Aggregates (8 keys)


| Key             | Description                                              |
| --------------- | -------------------------------------------------------- |
| `t1sc_ada_maF1` | Adaptive macro F1 (mean of 6 adaptive element macro F1s) |
| `t1sc_ada_miF1` | Adaptive micro F1 (pooled with globally unique labels)   |
| `t1sc_mal_maF1` | Maladaptive macro F1                                     |
| `t1sc_mal_miF1` | Maladaptive micro F1                                     |
| `t1sc_avg_maF1` | Average macro F1                                         |
| `t1sc_avg_miF1` | Average micro F1                                         |
| `t1sc_maF1`     | Overall macro F1                                         |
| `t1sc_miF1`     | Overall micro F1                                         |


---

## Task 1.2 — Presence Rating (`t1pr_*`)

### Per-valence (3 groups × 5 metrics = 15 keys)

Format: `t1pr_{valence}_{metric}`


| Example Key      | Description                         |
| ---------------- | ----------------------------------- |
| `t1pr_ada_mae`   | Adaptive — Mean Absolute Error      |
| `t1pr_ada_rmse`  | Adaptive — Root Mean Squared Error  |
| `t1pr_ada_qwk`   | Adaptive — Quadratic Weighted Kappa |
| `t1pr_ada_spear` | Adaptive — Spearman correlation     |
| `t1pr_ada_n`     | Adaptive — number of rated posts    |
| `t1pr_mal_mae`   | Maladaptive — MAE                   |
| `t1pr_comb_mae`  | Combined — MAE                      |


---

## Task 2 — Post-Level (`t2pl_*`)

### Per-label (2 labels × 5 metrics = 10 keys)

Format: `t2pl_{label}_{metric}`


| Example Key       | Description                  |
| ----------------- | ---------------------------- |
| `t2pl_sw_prec`    | Switch — precision           |
| `t2pl_sw_rec`     | Switch — recall              |
| `t2pl_sw_f1`      | Switch — F1                  |
| `t2pl_sw_sup_pos` | Switch — gold-positive count |
| `t2pl_sw_sup_tot` | Switch — total post count    |
| `t2pl_esc_prec`   | Escalation — precision       |


### Aggregate (1 key)


| Key         | Description                                          |
| ----------- | ---------------------------------------------------- |
| `t2pl_maF1` | Post-level macro F1 (mean of Switch + Escalation F1) |


---

## Task 2 — Timeline-Level (`t2tl_*`)

### Per-label (2 labels × 4 metrics = 8 keys)

Format: `t2tl_{label}_{metric}`


| Example Key    | Description                                        |
| -------------- | -------------------------------------------------- |
| `t2tl_sw_prec` | Switch — precision (macro-averaged over timelines) |
| `t2tl_sw_rec`  | Switch — recall (macro-averaged over timelines)    |
| `t2tl_sw_f1`   | Switch — F1 (macro-averaged over timelines)        |
| `t2tl_sw_n_tl` | Switch — number of timelines                       |
| `t2tl_esc_f1`  | Escalation — F1                                    |


### Aggregate (1 key)


| Key         | Description             |
| ----------- | ----------------------- |
| `t2tl_maF1` | Timeline-level macro F1 |


---

## Task 2 — Combined (`t2_comb_*`)


| Key            | Description                                                                    |
| -------------- | ------------------------------------------------------------------------------ |
| `t2_comb_maF1` | Combined macro F1 = mean of post-level + timeline-level macro F1 (for ranking) |


---

## Ranking Keys (one per task)


| Key         | Formula                                          | Description                                                         |
| ----------- | ------------------------------------------------ | ------------------------------------------------------------------- |
| `t1_1_rank` | `t1sc_avg_maF1`                                  | Task 1.1 ranking: subelement classification Avg Macro F1            |
| `t1_2_rank` | (`t1pr_ada_rmse` + `t1pr_mal_rmse`) / 2          | Task 1.2 ranking: avg RMSE across adaptive + maladaptive (lower is better) |
| `t2_rank`   | (`t2pl_maF1` + `t2tl_maF1`) / 2 = `t2_comb_maF1` | Task 2 ranking: avg of post-level + timeline-level macro F1         |


---

## Total: 139 metrics

- Task 1.1 Element Presence: 56 (48 per-element + 8 aggregate)
- Task 1.1 Subelement Classification: 44 (36 per-element + 8 aggregate)
- Task 1.2 Presence Rating: 15
- Task 2 Post-Level: 11
- Task 2 Timeline-Level: 9
- Task 2 Combined: 1
- Ranking: 3

