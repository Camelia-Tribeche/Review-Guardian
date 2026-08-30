"""
Portage direct de 08_summarizer.ipynb. Charge BART (résumé) + Flan-T5 (reformatage structuré)
une seule fois au chargement du module -> tourne sur CPU par défaut (voir device ci-dessous).

⚠️ Lourd en mémoire et en temps de calcul : à n'appeler que depuis la commande
`generate_summaries` (tâche batch/cron), jamais depuis une vue Django synchrone.
"""
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from .pi_defense import defend_and_build_prompt, verify_summary_safety

device = "cuda" if torch.cuda.is_available() else "cpu"

_bart_tokenizer = None
_bart_model = None
_flan_tokenizer = None
_flan_model = None


def _load_models():
    """Chargement paresseux : les poids ne sont téléchargés/chargés qu'au premier appel."""
    global _bart_tokenizer, _bart_model, _flan_tokenizer, _flan_model
    if _bart_model is None:
        _bart_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
        _bart_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn").to(device)
        _flan_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        _flan_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base").to(device)


def chunk_reviews(reviews, chunk_size=40):
    return [reviews[i:i + chunk_size] for i in range(0, len(reviews), chunk_size)]


def summarize_chunk(review_chunk):
    """Filtre les injections (pi_defense) puis résume le chunk avec BART."""
    _load_models()
    prompt, kept, blocked = defend_and_build_prompt(review_chunk, log_blocked=True)
    if not kept:
        return "[Aucune review de ce lot n'a passé le filtre de sécurité.]"

    inputs = _bart_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
    outputs = _bart_model.generate(
        **inputs, max_new_tokens=300, num_beams=4,
        no_repeat_ngram_size=3, repetition_penalty=1.3,
        early_stopping=True, do_sample=False,
    )
    raw_summary = _bart_tokenizer.decode(outputs[0], skip_special_tokens=True)
    safe_summary, _ = verify_summary_safety(raw_summary)
    return safe_summary


def reformat_to_structured(plain_summary):
    """Reformate un résumé en texte libre vers PROS/CONS/VERDICT via Flan-T5."""
    _load_models()
    prompt = f"""Reformat this product review summary into this exact format:
PROS:
- point
CONS:
- point
VERDICT:
one sentence

Summary: {plain_summary}"""
    inputs = _flan_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
    outputs = _flan_model.generate(**inputs, max_new_tokens=200)
    return _flan_tokenizer.decode(outputs[0], skip_special_tokens=True)


FINAL_SUMMARY_PROMPT = """Below are several aspect-based summaries, each generated from a different
batch of customer reviews for the same product. Combine them into ONE final aspect-based summary.

STRICT RULES:
1. Merge overlapping points; do not repeat the same point twice.
2. Only keep a point as a general trend if it appears in multiple batch summaries.
3. Format your response EXACTLY as:
PROS:
- point
CONS:
- point
VERDICT:
one to two sentence recommendation

Batch summaries:
{summaries_text}

Final combined summary:
PROS:"""

MAX_INPUT_TOKENS = 512
SAFETY_MARGIN = 8
MIN_BATCH = 2


def _render_summaries(summaries):
    return FINAL_SUMMARY_PROMPT.format(summaries_text="\n\n".join(summaries))


def _token_aware_pack(items, render_fn, tok, max_length=MAX_INPUT_TOKENS,
                       safety_margin=SAFETY_MARGIN, min_batch=MIN_BATCH):
    batches, current = [], []
    for item in items:
        candidate = current + [item]
        n_tokens = len(tok(render_fn(candidate), truncation=False)["input_ids"])
        if n_tokens <= max_length - safety_margin or len(current) < min_batch:
            current = candidate
        else:
            batches.append(current)
            current = [item]
    if current:
        batches.append(current)
    return batches


def _merge_once(summaries):
    _load_models()
    merged = []
    for batch in _token_aware_pack(summaries, _render_summaries, _flan_tokenizer):
        prompt = _render_summaries(batch)
        inputs = _flan_tokenizer(prompt, return_tensors="pt", truncation=True,
                                  max_length=MAX_INPUT_TOKENS).to(device)
        outputs = _flan_model.generate(**inputs, max_new_tokens=250)
        merged.append("PROS:" + _flan_tokenizer.decode(outputs[0], skip_special_tokens=True))
    return merged


def merge_summaries(summaries):
    """Fusionne récursivement les résumés par chunk jusqu'à n'en avoir plus qu'un seul."""
    current = list(summaries)
    while len(current) > 1:
        current = _merge_once(current)
    return current[0] if current else ""


def parse_structured_summary(text):
    pros = re.findall(r'PROS:\s*(.*?)(?=CONS:|VERDICT:|$)', text, re.DOTALL)
    cons = re.findall(r'CONS:\s*(.*?)(?=VERDICT:|$)', text, re.DOTALL)
    verdict = re.findall(r'VERDICT:\s*(.*)', text, re.DOTALL)

    def to_list(block):
        if not block:
            return []
        return [line.strip('- ').strip() for line in block[0].strip().split('\n') if line.strip()]

    return {
        'pros': to_list(pros),
        'cons': to_list(cons),
        'verdict': verdict[0].strip() if verdict else '',
    }
