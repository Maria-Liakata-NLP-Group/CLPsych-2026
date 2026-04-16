#!/bin/bash
# Setup script for Task 3 evaluation on Codabench.
# Installs PyTorch (CPU-only), Transformers, NLTK, BERTScore, and rouge-score at scoring time.
#
# Target image: codalab/codalab-legacy:py37 (Python 3.7.3, pip 19.1.1)
# pip must be upgraded first so it can find prebuilt wheels and respect python_requires.

set -e

echo "[setup.sh] Upgrading pip..."
pip install --upgrade "pip<24"

echo "[setup.sh] Installing Task 3 dependencies..."

# Pin typing-extensions before torch (pytorch CPU index serves py3-none-any
# wheels without python_requires, so old pip grabs 4.15+ which needs py3.9)
pip install --no-cache-dir "typing-extensions>=3.7,<4.8"

pip install --no-cache-dir \
    "torch==1.13.1+cpu" \
    --extra-index-url https://download.pytorch.org/whl/cpu

pip install --no-cache-dir \
    "transformers==4.26.1" \
    "nltk==3.8.1" \
    "bert-score==0.3.13" \
    "rouge-score==0.1.2"

echo "[setup.sh] Downloading NLTK punkt tokenizer..."
python -c "import nltk; nltk.download('punkt', quiet=True)"

echo "[setup.sh] Downloading NLI model (~1.7GB)..."
python -c "
from transformers import AutoTokenizer, AutoModelForSequenceClassification
model_name = 'MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli'
AutoTokenizer.from_pretrained(model_name)
AutoModelForSequenceClassification.from_pretrained(model_name)
print('[setup.sh] NLI model cached.')
"

echo "[setup.sh] Downloading BERTScore model (~1.4GB)..."
python -c "
from bert_score import BERTScorer
scorer = BERTScorer(model_type='microsoft/deberta-xlarge-mnli', lang='en', rescale_with_baseline=True)
print('[setup.sh] BERTScore model cached.')
"

echo "[setup.sh] Setup complete."
