# space_app.py
import os
import importlib
import sys
from pathlib import Path

# ---- Space-friendly envs & caching ----
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_cache")
Path("/tmp/mpl_cache").mkdir(parents=True, exist_ok=True)

# Keep HF caches on persistent /data (survives Space restarts)
os.environ.setdefault("HF_HOME", "/data")
os.environ.setdefault("HF_HUB_CACHE", "/data/hf_cache")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

HF_TOKEN = (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN") or "").strip()
if HF_TOKEN and HF_TOKEN.startswith("hf_"):
    # Many upstream helpers will auto-detect; we just make sure it's in env.
    os.environ["HF_TOKEN"] = HF_TOKEN

# ---- Where is the upstream app entry file? ----
# GPT-SoVITS repos often ship a Gradio UI in a file like webui.py or app.py.
# Update this if the upstream UI file name differs in your fork.
CANDIDATES = [
    "webui.py",
    "app.py",
    "infer-web.py",
    "gui.py",
]

root = Path(__file__).parent.resolve()

# Prefer importing as a module (keeps Gradio object alive for Spaces).
def import_module_from_path(py_path: Path):
    mod_name = py_path.stem  # e.g., "webui"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location(mod_name, py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {py_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod

ui = None
for name in CANDIDATES:
    p = root / name
    if p.exists():
        try:
            m = import_module_from_path(p)
            # Try common Gradio variables exported by upstream
            for attr in ("demo", "app", "iface", "interface"):
                if hasattr(m, attr):
                    ui = getattr(m, attr)
                    break
            # Or a factory function that returns a Blocks/Interface
            if ui is None:
                for attr in ("build_ui", "create_ui", "get_app"):
                    if hasattr(m, attr):
                        ui = getattr(m, attr)()
                        break
            if ui is not None:
                break
        except Exception as e:
            print(f"[space] import failed for {name}: {e}")

if ui is None:
    # Last resort: provide a tiny fallback so the Space doesn't crash.
    import gradio as gr
    with gr.Blocks(title="GPT-SoVITS (Space Wrapper)") as ui:
        gr.Markdown("### ⚠️ Could not auto-find the upstream Gradio app.\n"
                    "Update **CANDIDATES** in `space_app.py` to the correct entry file "
                    "(e.g., `webui.py`) or expose a variable named `demo` in that file.")
        gr.Markdown("1) Make sure the upstream UI file exists in your fork.\n"
                    "2) If the app creates the UI programmatically, return it from a function "
                    "like `build_ui()` and add that name above.\n"
                    "3) Commit & redeploy.")

# Spaces expects a top-level `demo` or `app` object.
demo = ui
