# English-only stub to satisfy "from text.g2pw.g2pw import *"
class G2PWPinyin:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        # Return empty result so callers safely no-op on English text.
        return []
