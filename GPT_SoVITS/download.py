# GPT_SoVITS/download.py
# English-only safe bootstrapper for Hugging Face Spaces.
# - When ENGLISH_ONLY=1 (default): do NOT import Chinese g2pw / pypinyin or download CN models.
#   We just create the expected folder so webui.py is satisfied and exit cleanly.
# - When ENGLISH_ONLY=0: fall back to the original CN behavior (if you need it later).

import os
import sys

now_dir = os.getcwd()
sys.path.insert(0, now_dir)

ENGLISH_ONLY = os.getenv("ENGLISH_ONLY", "1") == "1"

G2PW_DIR = os.path.join("GPT_SoVITS", "text", "G2PWModel")
CN_BERT_DIR = os.path.join("GPT_SoVITS", "pretrained_models", "chinese-roberta-wwm-ext-large")
CN_HUBERT_DIR = os.path.join("GPT_SoVITS", "pretrained_models", "chinese-hubert-base")

def ensure_dir(path: str):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"[download.py] warn: could not create {path}: {e}")

def english_only_bootstrap():
    print("[download.py] ENGLISH_ONLY=1 → skipping Chinese downloads and imports.")
    # Create the directory webui.py checks for so it won't try to run this again.
    ensure_dir(G2PW_DIR)
    # Nothing else to do for English-only mode.
    print("[download.py] Created placeholder:", G2PW_DIR)
    print("[download.py] Done.")

def chinese_bootstrap():
    # Optional: only run if you explicitly set ENGLISH_ONLY=0
    print("[download.py] ENGLISH_ONLY=0 → initializing Chinese g2pw + model paths.")
    try:
        # Lazy import to avoid pulling deps in ENGLISH_ONLY mode
        from text.g2pw import G2PWPinyin  # requires pypinyin, onnx runtime, etc.
    except Exception as e:
        print("[download.py] error: failed to import Chinese g2pw stack:", e)
        return

    ensure_dir(G2PW_DIR)
    # If you actually keep CN models in your Space, you can ensure their dirs too:
    ensure_dir(CN_BERT_DIR)
    ensure_dir(CN_HUBERT_DIR)

    try:
        # Initialize to trigger any on‑first‑run setup the library might do.
        _ = G2PWPinyin(
            model_dir=G2PW_DIR,
            model_source=CN_BERT_DIR,
            v_to_u=False,
            neutral_tone_with_five=True,
        )
        print("[download.py] Chinese g2pw initialized.")
    except Exception as e:
        print("[download.py] warn: G2PWPinyin init failed (you may be missing CN models/deps):", e)

    print("[download.py] Done.")

if __name__ == "__main__":
    if ENGLISH_ONLY:
        english_only_bootstrap()
    else:
        chinese_bootstrap()
