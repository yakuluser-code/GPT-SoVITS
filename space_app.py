# space_app.py — place this file at the repo ROOT (same level as webui.py)

import os, sys, importlib.util
from pathlib import Path

# ---- Space-friendly envs & caching ----
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_cache")
Path("/tmp/mpl_cache").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", "/data")
os.environ.setdefault("HF_HUB_CACHE", "/data/hf_cache")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

HF_TOKEN = (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN") or "").strip()
if HF_TOKEN.startswith("hf_"):
    os.environ["HF_TOKEN"] = HF_TOKEN

root = Path(__file__).parent.resolve()

# 1) helper used by the snippet you asked about
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

# 2) point to likely entry files (make sure "webui.py" is here)
CANDIDATES = [
    "webui.py",          # <-- your UI file
    "app.py",
    "infer-web.py",
    "gui.py",
]

ui = None

# ========= YOUR SNIPPET GOES RIGHT HERE =========
for name in CANDIDATES:
    p = root / name
    if p.exists():
        try:
            m = import_module_from_path(p)
            # finds your `demo = app`
            for attr in ("demo", "app", "iface", "interface"):
                if hasattr(m, attr):
                    ui = getattr(m, attr)
                    break
            # optional: try common factory names if no variable was found
            if ui is None:
                for factory in ("build_ui", "create_ui", "get_app"):
                    if hasattr(m, factory):
                        ui = getattr(m, factory)()
                        break
            if ui is not None:
                break
        except Exception as e:
            print(f"[space] import failed for {name}: {e}")
# ================================================

# 3) fallback tiny UI if nothing was found
if ui is None:
    import gradio as gr
    with gr.Blocks(title="GPT-SoVITS (Space Wrapper)") as ui:
        gr.Markdown(
            "### ⚠️ Could not auto-find the upstream Gradio app.\n"
            "Update `CANDIDATES` in `space_app.py` or expose `demo = app` in your `webui.py`."
        )

# 4) Spaces expects a top-level `demo` object
demo = ui
