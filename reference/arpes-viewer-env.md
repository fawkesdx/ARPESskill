# ARPES-data-browser environment (Python ≥3.9 — separate from PyARPES)

Upstream: [DingPei1995/ARPES-data-browser](https://github.com/DingPei1995/ARPES-data-browser)
(package tree `ARPES_viewer/`). Backend id in this skill: **`arpes_viewer`**.

Needs a **dedicated Python ≥3.9** environment. Do **not** install into the
PyARPES 3.8 env (`arpes38` / `~/arpes-py38-venv` / `.venv-arpes`).

Scripted agent work uses Qt-free **`loader/`** and **`tools/`** only. Full GUI
(`ARPES_viewer.py`, PyQt5) is optional — install GUI deps only if the user
wants the interactive browser.

## Location policy (reuse — avoid reinstall)

**Prefer one shared env per machine.**

| Priority | Location | When |
|----------|----------|------|
| 1 | **conda** env `arpes-viewer` | Mac / conda available |
| 2 | **`~/arpes-viewer-venv`** | Shared venv (no conda) |
| 3 | User-stated path | Already working viewer env |
| 4 | Project-local venv | **Only if user asks** |

**Hard:** never mix viewer deps into the PyARPES 3.8 interpreter.

## Source tree

Upstream is not a PyPI package (as of this skill note). Agents need a clone
(or user path) whose `ARPES_viewer` directory is on `PYTHONPATH` (or is cwd)
so `import loader` / `import tools` work.

```text
ARPES-data-browser/
  ARPES_viewer/          ← put this on PYTHONPATH
    loader/
    tools/
    ui/                  ← Qt; not required for scripted load/analysis
    ARPES_viewer.py
```

Ask the user for the clone path if unknown. Do not invent install locations.

## Agent checklist (mandatory)

1. **Discover** existing env (below) → if Python ≥3.9 and `import loader` works
   with the user’s `ARPES_viewer` path → **use it**; state interpreter + path.  
2. If none / wrong Python — **STOP and ask** (do not silent-fall back to
   PyARPES for ANTARES/CASSIOPEE, and do not invent loaders).  
3. On yes to create: prefer **conda `arpes-viewer`** else **`~/arpes-viewer-venv`**.  
4. Install deps with that env’s pip/conda only.  
5. Re-verify imports.  
6. All later **`arpes_viewer`** analysis uses that interpreter — not bare
   `python3`, not the PyARPES 3.8 binary.

### Discover order (before create)

```bash
# Set to the user's ARPES_viewer directory (parent of loader/)
export ARPES_VIEWER_ROOT="/path/to/ARPES-data-browser/ARPES_viewer"

# 1) conda env arpes-viewer
command -v conda && conda run -n arpes-viewer env PYTHONPATH="$ARPES_VIEWER_ROOT" \
  python -c "import sys, loader; print(sys.executable, sys.version_info[:2])"

# 2) shared home venv
test -x "$HOME/arpes-viewer-venv/bin/python" && \
  PYTHONPATH="$ARPES_VIEWER_ROOT" "$HOME/arpes-viewer-venv/bin/python" -c \
  "import sys, loader, tools; print(sys.executable, sys.version_info[:2])"
```

First success with Python ≥ (3, 9) → reuse.

## Create env (recommended: conda `arpes-viewer`)

**Scripted load / tools only** (no GUI):

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda create -n arpes-viewer python=3.11 -y
conda activate arpes-viewer
pip install numpy h5py scipy
# optional: astropy if peeks need it elsewhere
```

**If user wants the GUI** (`python ARPES_viewer.py`):

```bash
# after activate arpes-viewer
pip install PyQt5 pyqtgraph
# or conda-forge pyqt / pyqtgraph if preferred
```

Verify:

```bash
export ARPES_VIEWER_ROOT="/path/to/ARPES-data-browser/ARPES_viewer"
PYTHONPATH="$ARPES_VIEWER_ROOT" python -c "import loader, tools; print('ok', loader)"
```

## Shared venv alternative: `~/arpes-viewer-venv`

```bash
python3.11 -m venv "$HOME/arpes-viewer-venv"
"$HOME/arpes-viewer-venv/bin/pip" install numpy h5py scipy
# + PyQt5 pyqtgraph if GUI asked
```

## Wrong env — what to say

| Situation | Say |
|-----------|-----|
| Only PyARPES 3.8 available | Need separate ≥3.9 env for `arpes_viewer`; offer create |
| User asks to pip into `arpes38` | Refuse; cite this doc |
| `import loader` fails | Check `PYTHONPATH` → `ARPES_viewer`; confirm clone path |
| GUI import fails but load OK | Fine for scripted path; offer GUI deps only if user wants UI |

## See also

- `reference/arpes-viewer-backend.md` — routing, kinds, callables  
- `reference/pyarpes-env.md` — PyARPES 3.8 (do not mix)  
- `reference/backend-capability-map.md` — Browser column  
- `reference/package-first.md` — A/B/C/D when a callable is missing  
