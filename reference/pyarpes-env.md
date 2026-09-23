# PyARPES environment (Python 3.8 — shared preferred)

PyARPES (`arpes` on PyPI, v3.0.x) declares:

```text
python_requires = ">=3.8.0,<3.9"
```

Needs a **dedicated Python 3.8** environment. Do **not** install into the
user’s default 3.10/3.11/3.12 system or generic project venv.

## Location policy (reuse — avoid reinstall)

**Prefer one shared env per machine** so every analysis project reuses it.

| Priority | Location | When |
|----------|----------|------|
| 1 | **conda** env `arpes38` | Mac / conda available (best for Qt/HDF) |
| 2 | **`~/arpes-py38-venv`** | Shared venv (no conda) |
| 3 | Legacy names if present | `arpes_agent_test`, `~/arpes-py38-venv`, project `.venv-arpes` |
| 4 | **Project `.venv-arpes`** | **Only if user asks** for per-project isolation |

**Never** create a new project `.venv-arpes` by default when a shared env
already works.

Also accept user-stated path if they already have a working PyARPES 3.8 env.

---

## Agent checklist (mandatory)

1. **Discover** existing env (below) → if `import arpes` + Python 3.8.x →
   **use it**; state full interpreter path; stop.  
2. If none / wrong Python — **STOP and ask** (`SKILL.md` Stack policy).  
3. On yes to create: prefer **conda `arpes38`** (Mac) else **`~/arpes-py38-venv`**;
   project `.venv-arpes` only if user requests.  
4. Install with that env’s `pip` / conda only.  
5. Re-verify import + version.  
6. All later analysis uses that interpreter — not bare `python3`.

### Discover order (before create)

```bash
# 1) conda env arpes38 (or legacy arpes_agent_test)
command -v conda && conda run -n arpes38 python -c "import arpes, sys; print(sys.executable, sys.version_info[:2])"
# also try: conda run -n arpes_agent_test …

# 2) shared home venv
test -x "$HOME/arpes-py38-venv/bin/python" && \
  "$HOME/arpes-py38-venv/bin/python" -c "import arpes, sys; print(sys.executable, sys.version_info[:2])"

# 3) project-local (legacy / user-requested only)
test -x .venv-arpes/bin/python && \
  .venv-arpes/bin/python -c "import arpes, sys; print(sys.executable, sys.version_info[:2])"
```

First success with `(3, 8)` → reuse. Do not reinstall.

---

## Find Python 3.8 (for create)

```bash
command -v python3.8
python3.8 -V   # expect Python 3.8.x
```

If missing, tell user and offer Homebrew vs conda vs their 3.8 path.
Do not invent install paths.

**macOS Homebrew:**

```bash
brew install python@3.8
# $(brew --prefix python@3.8)/bin/python3.8
```

---

## Create env + install (recommended on Mac: conda `arpes38`)

Bare `pip install arpes` often **fails/hangs on PyQt5** (qmake). Prefer
**conda for Qt/HDF**, then `arpes` with `--no-deps`.

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"

conda create -n arpes38 python=3.8 -y
conda activate arpes38

conda install -c conda-forge "pyqt=5" pyqtgraph h5py netcdf4 xarray \
  matplotlib numpy scipy astropy -y

pip install "PyQt5==5.15.10"   # optional if conda pyqt enough

pip install "arpes==3.0.1" --no-deps
pip install "pyqtgraph>=0.12.0,<0.13.0" colorcet pint pandas \
  "numpy>=1.20.0,<2.0.0" "scipy>=1.6.0,<2.0.0" "lmfit>=1.0.0,<2.0.0" \
  scikit-learn "matplotlib>=3.0.3" "bokeh>=2.0.0,<3.0.0" \
  "ipywidgets>=7.0.1,<8.0.0" packaging colorama imageio titlecase tqdm rx dill \
  "ase>=3.17.0,<3.22.0" "numba>=0.53.0,<1.0.0" netCDF4

python -c "import arpes, h5py, astropy, sys; print('OK', sys.executable, sys.version)"
```

**Loader I/O packages:**

| Package | Why |
|---------|-----|
| **h5py** | `.h5` / HDF5 (modern MAESTRO) |
| **astropy** | `.fits` via `astropy.io.fits` |
| **netCDF4** | NetCDF / some exports |

---

## Create shared venv (no conda): `~/arpes-py38-venv`

```bash
PY38="$(command -v python3.8)"
"$PY38" -V   # must be 3.8.x

"$PY38" -m venv "$HOME/arpes-py38-venv"
source "$HOME/arpes-py38-venv/bin/activate"   # Windows: Scripts\activate

python -V
python -m pip install --upgrade pip
python -m pip install "PyQt5==5.15.10" h5py astropy netCDF4
python -m pip install "arpes==3.0.1" --no-deps
# remaining deps: same pip list as conda recipe (minus PyQt5 if already installed)

python -c "import arpes, h5py, astropy, sys; print('arpes OK', sys.executable, sys.version)"
```

Reuse: `"$HOME/arpes-py38-venv/bin/python"` from any project.

---

## Project-local `.venv-arpes` (only if user asks)

```bash
# from analysis project root
"$PY38" -m venv .venv-arpes
# then same pip steps as shared venv
```

---

## After install — Cursor / agent

- Run with absolute env python, e.g.  
  `…/envs/arpes38/bin/python` or `$HOME/arpes-py38-venv/bin/python`  
- State path once per session.  
- MAESTRO `.h5`: pass `location=` (micro/nano) when known.

## Wrong Python — what to say

> PyARPES needs Python **3.8.x** only. Current interpreter is X.Y.  
> I should reuse or create a **shared** env (`conda arpes38` or
> `~/arpes-py38-venv`) and install there — OK?  
> (Project `.venv-arpes` only if you want isolation.)

Do **not** `pip install arpes` on 3.9+.

## Inspect-only fallback

Only if user declines env/install: xarray + h5py load/inspect
(`formats-and-axes.md`). No fit / k / kz.
