# English-only stub: disable Chinese g2pw so imports don't fail.
class G2PWPinyin:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        # Return an empty result; English path should handle text instead.
        return []
