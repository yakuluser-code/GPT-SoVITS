import os
import sys

now_dir = os.getcwd()
sys.path.insert(0, now_dir)

# Flag to control language behavior (default to English-only)
ENGLISH_ONLY = os.getenv("ENGLISH_ONLY", "1") == "1"

if ENGLISH_ONLY:
    print("[download.py] ENGLISH_ONLY=1 → Skipping Chinese g2pw import and CN model downloads.")
    # Stub instance so any code using g2pw still works without errors
    class G2PWPinyin:
        def __init__(self, *args, **kwargs):
            pass
        def __call__(self, *args, **kwargs):
            return []
    g2pw = G2PWPinyin()
else:
    from text.g2pw import G2PWPinyin
    g2pw = G2PWPinyin(
        model_dir="GPT_SoVITS/text/G2PWModel",
        model_source="GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large",
        v_to_u=False,
        neutral_tone_with_five=True,
    )
