# Scores.txt Key Reference — Task 3 (v3-rouge-pkg)

All metric keys are <=36 characters for Codabench compatibility.

## Metrics

| Key | Description | Direction |
|-----|-------------|-----------|
| `t3_cs` | Mean Consistency Score (1 − mean NLI contradiction) | Higher = better |
| `t3_ct` | Mean Contradiction Top (NLI max) | Lower = better |
| `t3_rouge_l_recall` | Mean ROUGE-L Recall (rouge-score pkg, Porter stemmer) | Higher = better |
| `t3_bertscore_recall` | Mean BERTScore Recall | Higher = better |
| `t3_n_seq` | Number of sequences scored | — |
| `t3_n_trunc` | Predictions truncated to 350 words | — |
| `t3_rank` | Ranking metric = `t3_cs` | Higher = better |

## Ranking

| Key | Formula | Description |
|-----|---------|-------------|
| `t3_rank` | `t3_cs` | Task 3.1 ranking: Mean CS (higher is better) |

## Total: 7 metrics
