# Task 3.1 Evaluation Logic (v3-rouge-pkg)

## Overview

Task 3.1 evaluates **Sequence Summary** quality using four complementary metrics:

| Metric | What it measures | Direction | Source |
|--------|-----------------|-----------|--------|
| **CS** (Consistency Score) | NLI consistency (1 − mean contradiction) | Higher = better | CLPsych 2025 Task B |
| **CT** (Contradiction Top) | NLI contradiction (max) | Lower = better | CLPsych 2025 Task B |
| **ROUGE-L Recall** | Temporal/dynamic word coverage | Higher = better | `rouge-score` pkg (Porter stem) |
| **BERTScore Recall** | Semantic content coverage | Higher = better | CLPsych 2025 Task A |

### v2 change: CS direction fix

In v1, CS was computed as raw mean contradiction probability (lower = better).
This was inconsistent with the CLPsych 2025 paper and codebase, which define
CS as **consistency = 1 − mean contradiction** (higher = better).

v2 applies the `1 −` transformation to match the published definition:

    CS = 1/(|S||G|) * Σ_s∈S Σ_g∈G (1 − NLI(Contradict|g, s))

Reference: CLPsych 2025 `nli_scorer.py` line `mean_consistency = 1 - contradict_scores.mean()`

### v3 change: ROUGE-L now uses the `rouge-score` package

In v1/v2, ROUGE-L was a custom pure-Python LCS with whitespace-only tokenization
and no stemming. v3 switches to Google's `rouge-score` package (`use_stemmer=True`)
to match standard ROUGE-L practice. Scores differ from v2 (typically +1 to +6
points higher) because the package handles punctuation properly via word-boundary
tokenization and applies Porter stemming.

## Prediction Truncation (350 words)

Before any scoring, predicted summaries are truncated to the first **350 words**. This:
- Prevents gaming recall metrics with verbose text
- Supports the use of Recall (vs Precision/F1) metrics
- Is enforced automatically in the evaluation code

## CS and CT (NLI)

- Model: `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli`
- Direction: gold = premise, predicted = hypothesis
- **CS**: 1 − (for each predicted sentence, mean contradiction prob across gold sentences; averaged)
- **CT**: For each predicted sentence, max contradiction prob across gold sentences; averaged

## ROUGE-L Recall

Computed via Google's `rouge-score` package (v0.1.2) with `use_stemmer=True`
(Porter stemmer). Uses word-boundary tokenization (handles punctuation) and
standard ROUGE-L LCS recall:

    ROUGE-L Recall = LCS(gold_tokens, pred_tokens) / len(gold_tokens)

This captures how well the predicted summary covers the temporal progression and dynamic keywords present in the gold summary. ABCD terminology (e.g., "self-criticism", "hopelessness", "relating behavior") is captured naturally since these are word sequences.

## BERTScore Recall

Adapted from CLPsych 2025 Task A evidence extraction (span_scorer.py).

- Model: `microsoft/deberta-xlarge-mnli`
- Baseline rescaling: enabled

For each gold sentence g_i, compute BERTScore F1 against all predicted sentences and take the max:

    BERTScore_Recall(g_i) = max_j BERTScore_F1(g_i, s_j)

Then average across gold sentences:

    BERTScore_Recall = (1/m) * sum_i BERTScore_Recall(g_i)

This measures how well the semantic content of each gold sentence is covered somewhere in the predicted summary. Operating at the token level via contextual embeddings, it captures paraphrases and semantic equivalence beyond exact word match.

## Edge Cases

| Condition | CS/CT | ROUGE-L | BERTScore |
|-----------|-------|---------|-----------|
| Empty prediction | 0.0 / 1.0 | 0.0 | 0.0 |
| Empty gold | 1.0 / 0.0 | 0.0 | 0.0 |
| Prediction > 350 words | Truncated first | Truncated first | Truncated first |

## Codabench scores.txt Keys

| Key | Description | Direction |
|-----|-------------|-----------|
| `t3_cs` | Mean CS (consistency) | Higher = better |
| `t3_ct` | Mean CT (contradiction) | Lower = better |
| `t3_rouge_l_recall` | Mean ROUGE-L Recall | Higher = better |
| `t3_bertscore_recall` | Mean BERTScore Recall | Higher = better |
| `t3_n_seq` | Number of sequences | — |
| `t3_n_trunc` | Predictions truncated | — |
| `t3_rank` | = t3_cs | Higher = better |

## Pipeline Summary

```
Predicted summary
  |-- Truncate to 350 words
  |-- Sentence tokenize (NLTK)
  |
  |-- CS/CT: NLI (DeBERTa-v3-large) — CS = 1 − mean contradiction
  |-- ROUGE-L Recall: rouge-score pkg, Porter stemmer, word-boundary tokens
  +-- BERTScore Recall: per-gold-sentence max BERTScore F1 (DeBERTa-xlarge)
```

## Models

| Metric | Model | Size |
|--------|-------|------|
| CS, CT | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` | ~1.7 GB |
| BERTScore | `microsoft/deberta-xlarge-mnli` | ~1.4 GB |
