"""BERTScore Recall for Task 3.1 summary evaluation.

Adapted from CLPsych 2025 Task A span_scorer.py (Jenny Chim).

For each gold sentence, computes BERTScore F1 against all predicted sentences
and takes the maximum. The average across gold sentences gives the recall:
how well the gold content is semantically covered by the prediction.

Model: microsoft/deberta-xlarge-mnli (same as CLPsych 2025 Task A).
"""

import hashlib
import numpy as np


BERTSCORE_MODEL_NAME = "microsoft/deberta-xlarge-mnli"


class MockBERTScoreScorer:
    """Deterministic mock for pipeline testing without the BERTScore model."""

    def __init__(self):
        print("[MockBERTScoreScorer] Using mock scorer (no BERTScore model loaded)")

    @staticmethod
    def _pseudo_bertscore(gold, pred):
        """Deterministic pseudo-BERTScore based on word overlap."""
        g_set = set(gold.lower().split())
        p_set = set(pred.lower().split())
        if not g_set or not p_set:
            return 0.0
        overlap = len(g_set & p_set) / max(len(g_set | p_set), 1)
        h = int(hashlib.md5((gold + pred).encode()).hexdigest()[:8], 16)
        noise = (h % 100) / 2000.0  # 0.000 - 0.049
        return min(1.0, overlap * 0.8 + 0.1 + noise)

    def score_sequence(self, gold_sents, pred_sents):
        if not pred_sents:
            return {"bertscore_recall": 0.0}
        if not gold_sents:
            return {"bertscore_recall": 0.0}

        recalls = []
        for gs in gold_sents:
            scores = [self._pseudo_bertscore(gs, ps) for ps in pred_sents]
            recalls.append(max(scores))

        return {"bertscore_recall": float(np.mean(recalls))}


class BERTScoreScorer:
    """Computes BERTScore Recall between gold and predicted summary sentences.

    For each gold sentence, compute BERTScore F1 against all predicted sentences,
    take the max. Average across gold sentences.
    """

    def __init__(self, model_name=BERTSCORE_MODEL_NAME, rescale_with_baseline=True):
        from bert_score import BERTScorer

        self.model_name = model_name
        self.rescale_with_baseline = rescale_with_baseline

        print("Loading BERTScore model: %s" % model_name)
        self.scorer = BERTScorer(
            model_type=self.model_name,
            lang="en",
            rescale_with_baseline=self.rescale_with_baseline,
        )

    def score_sequence(self, gold_sents, pred_sents):
        """Compute BERTScore Recall for a single sequence.

        Args:
            gold_sents: List of gold summary sentences.
            pred_sents: List of predicted summary sentences.

        Returns:
            dict with key: bertscore_recall
        """
        if not pred_sents:
            return {"bertscore_recall": 0.0}
        if not gold_sents:
            return {"bertscore_recall": 0.0}

        recalls = []
        for gold_sent in gold_sents:
            # Score each predicted sentence against this gold sentence
            _, _, F = self.scorer.score(
                pred_sents, [gold_sent] * len(pred_sents)
            )
            recalls.append(F.max().item())

        return {"bertscore_recall": float(np.mean(recalls))}
