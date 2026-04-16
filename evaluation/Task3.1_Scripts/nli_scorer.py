"""NLI-based consistency and contradiction scoring for Task 3.1 summary evaluation.

Adapted from CLPsych 2025 evaluation (Maria-Liakata-NLP-Group/clpsych2025).

Computes two metrics per sequence:
  CS (Consistency Score): 1 minus mean contradiction probability, following
      CLPsych 2025. Higher = better (more consistent with gold).
      CS = 1/(|S||G|) * sum_s sum_g (1 - NLI(Contradict|g, s))
  CT (Contradiction Top): For each predicted sentence, max contradiction
      probability across all gold sentences. Averaged over predicted sentences.
      Lower = better (less contradiction with gold).

NLI direction: gold sentence = premise, predicted sentence = hypothesis.
"""

import hashlib
import nltk
import numpy as np

NLI_MODEL_NAME = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
# Label order for this model: 0=entailment, 1=neutral, 2=contradiction
CONTRADICTION_IDX = 2


def ensure_nltk_data():
    """Download NLTK punkt tokenizer if not present."""
    for resource in ["punkt", "punkt_tab"]:
        try:
            nltk.data.find("tokenizers/" + resource)
        except (LookupError, OSError):
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                pass


class MockNLIScorer:
    """Deterministic mock scorer for pipeline testing without the NLI model.

    Uses string similarity (character-level overlap) to produce reproducible
    pseudo-contradiction scores. Identical strings -> low score, unrelated -> higher.
    """

    def __init__(self):
        print("[MockNLIScorer] Using mock scorer (no NLI model loaded)")
        ensure_nltk_data()

    @staticmethod
    def sentence_tokenize(text):
        if not text or not text.strip():
            return []
        return nltk.sent_tokenize(text.strip())

    @staticmethod
    def _pseudo_contradiction(premise, hypothesis):
        """Deterministic pseudo-contradiction based on character overlap."""
        p_set = set(premise.lower().split())
        h_set = set(hypothesis.lower().split())
        if not p_set or not h_set:
            return 0.5
        overlap = len(p_set & h_set) / max(len(p_set | h_set), 1)
        h = int(hashlib.md5((premise + hypothesis).encode()).hexdigest()[:8], 16)
        noise = (h % 100) / 1000.0
        return max(0.0, min(1.0, (1.0 - overlap) * 0.6 + noise))

    def score_sequence(self, gold_sents, pred_sents):
        if not pred_sents:
            return {"cs": 0.0, "ct": 1.0}
        if not gold_sents:
            return {"cs": 1.0, "ct": 0.0}

        n_pred = len(pred_sents)
        n_gold = len(gold_sents)
        prob_matrix = np.zeros((n_pred, n_gold))
        for pi, ps in enumerate(pred_sents):
            for gi, gs in enumerate(gold_sents):
                prob_matrix[pi, gi] = self._pseudo_contradiction(gs, ps)

        cs = float(1.0 - prob_matrix.mean(axis=1).mean())
        ct = float(prob_matrix.max(axis=1).mean())
        return {"cs": cs, "ct": ct}


class NLIScorer:
    """Computes NLI contradiction scores between gold and predicted summaries."""

    def __init__(self, model_name=NLI_MODEL_NAME, device=None, batch_size=32):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.model_name = model_name
        self.batch_size = batch_size

        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        print("Loading NLI model: %s (device: %s)" % (model_name, self.device))
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        ensure_nltk_data()

    def _get_contradiction_probs(self, premise_hypothesis_pairs):
        import torch

        if not premise_hypothesis_pairs:
            return []

        all_probs = []
        for i in range(0, len(premise_hypothesis_pairs), self.batch_size):
            batch = premise_hypothesis_pairs[i : i + self.batch_size]
            premises = [p for p, _ in batch]
            hypotheses = [h for _, h in batch]

            inputs = self.tokenizer(
                premises,
                hypotheses,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                contradiction_probs = probs[:, CONTRADICTION_IDX].cpu().numpy()
                all_probs.extend(contradiction_probs.tolist())

        return all_probs

    def score_sequence(self, gold_sents, pred_sents):
        """Compute CS and CT for a single sequence.

        CS (Consistency Score) = 1 - mean contradiction probability.
        Higher = better. Follows CLPsych 2025 formula:
            CS = 1/(|S||G|) * sum_s sum_g (1 - NLI(Contradict|g, s))

        CT (Contradiction Top) = mean of per-sentence max contradiction.
        Lower = better.

        Args:
            gold_sents: List of gold summary sentences.
            pred_sents: List of predicted summary sentences.

        Returns:
            dict with keys: cs, ct
        """
        if not pred_sents:
            # Empty prediction: worst possible scores
            return {"cs": 0.0, "ct": 1.0}
        if not gold_sents:
            # Empty gold (shouldn't happen): no contradiction measurable
            return {"cs": 1.0, "ct": 0.0}

        pairs = []
        pair_indices = []
        for pi, ps in enumerate(pred_sents):
            for gi, gs in enumerate(gold_sents):
                pairs.append((gs, ps))  # premise=gold, hypothesis=pred
                pair_indices.append((pi, gi))

        contra_probs = self._get_contradiction_probs(pairs)

        n_pred = len(pred_sents)
        n_gold = len(gold_sents)
        prob_matrix = np.zeros((n_pred, n_gold))
        for idx, (pi, gi) in enumerate(pair_indices):
            prob_matrix[pi, gi] = contra_probs[idx]

        # CS: consistency = 1 - mean contradiction (higher = better)
        cs = float(1.0 - prob_matrix.mean(axis=1).mean())
        # CT: max contradiction per predicted sentence, averaged (lower = better)
        ct = float(prob_matrix.max(axis=1).mean())

        return {"cs": cs, "ct": ct}
