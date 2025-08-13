# space_app.py — Hugging Face loader for GPT-SoVITS
import os, sys, importlib.util
from pathlib import Path

# ---- Space-friendly envs & caching ----
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_cache")
Path("/tmp/mpl_cache").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", "/data")
os.environ.setdefault("HF_HUB_CACHE", "/data/hf_cache")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("ENGLISH_ONLY", "1")


# Pass through HF token if provided in Space settings
HF_TOKEN = (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN") or "").strip()
if HF_TOKEN.startswith("hf_"):
    os.environ["HF_TOKEN"] = HF_TOKEN

root = Path(__file__).parent.resolve()

# ---- fetch small runtime assets we excluded from Git push ----
# (Requires 'requests' in requirements.txt)
def _download(url: str, dest: str):
    import requests
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    dest_path.write_bytes(r.content)

RUNTIME_FETCH = [
    (
        "https://raw.githubusercontent.com/RVC-Boss/GPT-SoVITS/main/GPT_SoVITS/text/engdict_cache.pickle",
        "GPT_SoVITS/text/engdict_cache.pickle",
    ),
    (
        "https://raw.githubusercontent.com/RVC-Boss/GPT-SoVITS/main/GPT_SoVITS/text/g2pw/polyphonic.pickle",
        "GPT_SoVITS/text/g2pw/polyphonic.pickle",
    ),
    (
        "https://raw.githubusercontent.com/RVC-Boss/GPT-SoVITS/main/GPT_SoVITS/text/namedict_cache.pickle",
        "GPT_SoVITS/text/namedict_cache.pickle",
    ),
    # If you need the Japanese user dictionary, uncomment below (this file is >10MB):
    # (
    #     "https://raw.githubusercontent.com/RVC-Boss/GPT-SoVITS/main/GPT_SoVITS/text/ja_userdic/userdict.csv",
    #     "GPT_SoVITS/text/ja_userdic/userdict.csv",
    # ),
]
for url, dest in RUNTIME_FETCH:
    try:
        if not Path(dest).exists():
            print(f"[space] fetching {url} -> {dest}")
            _download(url, dest)
    except Exception as e:
        print(f"[space] warn: could not fetch {url} -> {dest}: {e}")

# ---- import helper ----
def import_module_from_path(py_path: Path):
    mod_name = py_path.stem  # e.g., "webui"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location(mod_name, py_path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot import {py_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod

import gradio as gr

def ensure_gradio(obj):
    """Return obj if it looks like a Gradio app, else None."""
    if obj is None:
        return None
    # Blocks & Interface both have .launch
    return obj if hasattr(obj, "launch") else None

CANDIDATES = ["webui.py", "app.py", "infer-web.py", "gui.py"]

ui = None
for name in CANDIDATES:
    p = root / name
    if not p.exists():
        continue
    try:
        m = import_module_from_path(p)
        # Try exported variables first
        for attr in ("demo", "app", "iface", "interface"):
            if hasattr(m, attr):
                cand = getattr(m, attr)
                ui = ensure_gradio(cand)
                if ui:
                    print(f"[space] loaded UI from {name} using attr `{attr}`")
                    break
        # If not found, try common factories
        if ui is None:
            for factory in ("build_ui", "create_ui", "get_app"):
                if hasattr(m, factory):
                    cand = getattr(m, factory)()
                    ui = ensure_gradio(cand)
                    if ui:
                        print(f"[space] loaded UI from {name} via factory `{factory}()`")
                        break
        if ui:
            break
        else:
            print(f"[space] {name} imported but no Gradio app found in exports/factories.")
    except Exception as e:
        print(f"[space] import failed for {name}: {e}")

# Fallback minimal UI so the Space always initializes
if ui is None:
    with gr.Blocks(title="GPT-SoVITS (Space Wrapper)") as ui:
        gr.Markdown(
            "### ⚠️ Could not find a Gradio app to serve.\n"
            "Make sure `webui.py` ends with:\n"
            "`demo = app`  and (optionally for local) `if __name__ == '__main__': demo.queue().launch(...)`"
        )

# Spaces serves a top-level `demo`
demo = ui
