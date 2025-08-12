# Minimal English-only download.py for Spaces
import os

def main():
    target = os.path.join("GPT_SoVITS", "text", "G2PWModel")
    os.makedirs(target, exist_ok=True)
    print("[download.py] Created", target, "- English-only mode; no CN models downloaded.")

if __name__ == "__main__":
    main()
