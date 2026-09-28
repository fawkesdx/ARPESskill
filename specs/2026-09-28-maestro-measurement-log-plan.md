# MAESTRO measurement log + Pass A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a FITS-first MAESTRO measurement logger in the skill and wire agents to write `MAESTRO_Measurement_Log.csv` in the data folder then Pass-A-merge into `analysis/manifest.json` on trigger phrases like “log the maestro data in XXX.”

**Architecture:** Port the user’s proven MH1 `.h5` header/comment/0D extractor into `scripts/maestro_measurement_log.py`, preferring `.fits` as CSV `File Name` while still reading sibling `.h5` for rich columns. Docs teach the trigger + Pass A join; no graphify; no Pass B/C on this trigger.

**Tech Stack:** Python 3 + `h5py` + `numpy`; Markdown skill docs; optional filesystem sibling `.fits` (astropy not required for logging).

**Spec:** `specs/2026-09-28-maestro-measurement-log-design.md`  
**Branch:** `feat/maestro-measurement-log` (local commits OK; **do not push** unless user asks)

## Global Constraints

- CSV filename `MAESTRO_Measurement_Log.csv` **inside the target data folder**.
- Keep the **same 14 CSV columns** as the original logger (compatible with existing CSVs).
- Per stem: prefer `.fits`/`.fit` as `File Name`; parse rich fields from sibling `.h5` when present; H5-only OK; FITS-only → mostly `N/A` (do not invent MH1 groups).
- Measurement Type = **log label only** → store as `meas_type_log` / CSV column; never copy into manifest `kind`.
- Pass A merge sets `kind=unknown` until later peek; `backend=pyarpes` for MAESTRO.
- No blanket token note for running the logger; never paste full CSV into chat.
- No graphify.
- Flat folder enumeration (not recursive); nested parent → ask or per-leaf (document that).
- Canonical script in skill; if user points at a **newer** NAS `maestro_logger.py`, prefer it once and state which ran.
- Local commits OK; **do not push** unless asked.
- Living-list: add capability row in `backend-capability-map.md` in the same change set as the feature docs.

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `scripts/maestro_measurement_log.py` | Canonical FITS-first + H5-meta logger CLI |
| Create | `scripts/merge_maestro_log_to_manifest.py` | Thin Pass A: CSV → `analysis/manifest.json` |
| Create | `tests/test_maestro_measurement_log.py` | Unit tests with tiny fake MH1 + sibling names |
| Create | `reference/maestro-measurement-log.md` | Trigger, CLI, sibling rules, Pass A, NAS fork |
| Create | `examples/maestro_measurement_log.md` | Short recipe |
| Modify | `reference/folder-manifest.md` | Pass A MAESTRO recipe + `maestro_log` fields |
| Modify | `reference/backend-capability-map.md` | `maestro_measurement_log` (+ merge) rows |
| Modify | `reference/token-usage.md` | Logger cheap; dumping CSV expensive |
| Modify | `reference/failure-modes.md` | Log-type≠kind; FITS/H5 sibling rules |
| Modify | `SKILL.md` | Trigger + workflow bullet + references |
| Modify | `README.md` | One-liner |

---

### Task 1: Logger script + tests

**Files:**
- Create: `scripts/maestro_measurement_log.py`
- Create: `tests/test_maestro_measurement_log.py`

**Interfaces:**
- Produces: `extract_maestro_metadata(folder_path: str) -> str` (returns CSV path written)
- Produces: CLI `python scripts/maestro_measurement_log.py <folder>` exit 0 on success
- Consumes: original logic from `/Volumes/MAESTROdata/uARPES/2026/2026_06/Katoch_Jyoti - 045552/maestro_logger.py` (copy helpers: `clean_string`, `deep_clean`, `find_value`, H5 Headers/Comments/0D extract)

- [ ] **Step 1: Create `scripts/` and port script with FITS-first stem logic**

  Port the original file. Replace the flat `*.h5` loop with:

  ```python
  def collect_stems(folder_path):
      """Return sorted unique stems that have .h5 and/or .fits/.fit."""
      stems = {}
      for name in os.listdir(folder_path):
          lower = name.lower()
          if not (lower.endswith(".h5") or lower.endswith(".fits") or lower.endswith(".fit")):
              continue
          stem, ext = os.path.splitext(name)
          ext = ext.lower()
          if ext == ".fit":
              ext = ".fits"
          stems.setdefault(stem, {})[ext] = name
      return dict(sorted(stems.items()))

  def preferred_file_name(ext_map):
      """CSV File Name: .fits first, else .h5."""
      if ".fits" in ext_map:
          return ext_map[".fits"]
      return ext_map[".h5"]

  def h5_path_for_stem(folder_path, ext_map):
      if ".h5" not in ext_map:
          return None
      return os.path.join(folder_path, ext_map[".h5"])
  ```

  For each stem:
  1. `file_name = preferred_file_name(ext_map)`
  2. If `h5_path_for_stem` is not None → open H5 and run **existing** extractors unchanged → build `row_data` with `file_name` as column 0.
  3. Else (FITS-only) → write row `[file_name, "unknown (fits-only)", "None", ... "N/A"...]` (14 cols); do not invent Headers.

  Quiet stdout: print start count; print every 25 files optional; always print final CSV path. Avoid one line per file by default (`--verbose` flag for per-file).

  CLI:

  ```python
  if __name__ == "__main__":
      import sys
      if len(sys.argv) >= 2:
          target = sys.argv[1].strip().strip("'\"")
      else:
          target = input("Paste the path to your MAESTRO data folder: ").strip().strip("'\"")
      # unescape shell backslash-spaces like original
      target = target.replace("\\ ", " ").replace("\\(", "(").replace("\\)", ")")
      if not os.path.isdir(target):
          print(f"Error: not a directory: {target}")
          sys.exit(1)
      extract_maestro_metadata(target)
  ```

  Keep headers list and ERROR row behavior from original. Keep Bad-file-descriptor ignore.

- [ ] **Step 2: Write tests with a tiny synthetic MH1 + fake sibling fits name**

  Create `tests/test_maestro_measurement_log.py` using `tmp_path` and h5py to write a minimal MH1:

  ```python
  import csv
  from pathlib import Path
  import h5py
  import numpy as np
  import sys
  sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
  from maestro_measurement_log import extract_maestro_metadata

  def _write_minimal_mh1(path: Path, comment="hello note"):
      with h5py.File(path, "w") as f:
          # Headers/Beamline as structured array matching logger expectations
          dt = np.dtype([("longname", "O"), ("name", "O"), ("value", "O"), ("comment", "O")])
          rows = np.array([
              ("Beamline Energy", "bl_e", "91.5", ""),
              ("EPU Polarization", "epu_pol", "0", ""),
              ("Pass Energy", "epass", "20", ""),
              ("Lens Mode Name", "lens", "Angular30", ""),
              ("Low Level Scan Mode Name", "scan", "Cut", ""),
          ], dtype=dt)
          g = f.create_group("Headers")
          g.create_dataset("Beamline", data=rows)
          # Minimal other groups the skip-logic may touch
          f.create_group("Comments").create_dataset("PreScan", data=np.bytes_(comment))
          d0 = f.create_group("0D_Data")
          d0.create_dataset("Cryostat_A", data=np.array([8.5]))
          d0.create_dataset("Cryostat_B", data=np.array([80.0]))
          d0.create_dataset("Cryostat_C", data=np.array([240.0]))
          d0.create_dataset("Cryostat_D", data=np.array([7.0]))

  def test_fits_preferred_file_name_reads_sibling_h5(tmp_path):
      stem = "20260101_00001"
      _write_minimal_mh1(tmp_path / f"{stem}.h5")
      (tmp_path / f"{stem}.fits").write_bytes(b"")  # empty sibling is enough for identity
      out = extract_maestro_metadata(str(tmp_path))
      assert Path(out).name == "MAESTRO_Measurement_Log.csv"
      with open(out, newline="", encoding="utf-8") as f:
          rows = list(csv.DictReader(f))
      assert len(rows) == 1
      assert rows[0]["File Name"] == f"{stem}.fits"
      assert "91.5" in rows[0]["Photon Energy (eV)"]
      assert "hello note" in rows[0]["Pre/Post Comments"] or rows[0]["Pre/Post Comments"] != "None"

  def test_h5_only_stem(tmp_path):
      _write_minimal_mh1(tmp_path / "only.h5")
      extract_maestro_metadata(str(tmp_path))
      with open(tmp_path / "MAESTRO_Measurement_Log.csv", newline="", encoding="utf-8") as f:
          rows = list(csv.DictReader(f))
      assert rows[0]["File Name"] == "only.h5"
  ```

  Note: original Headers loop expects `len(row) >= 3` with short_key=row[0], val=row[2], desc=row[3]. Match that layout in the synthetic file (field order may be longname/name/value/comment — **align the test dataset columns with what the ported code indexes**: row[0], row[2], row[3]). If the ported code indexes by position on structured rows, use a plain tuple/list dataset or fix indexing to named fields — prefer keeping original index logic and shaping test data so `row[0]`/`row[2]`/`row[3]` work (e.g. store as `(name, unused, value, comment)` objects).

- [ ] **Step 3: Run tests**

  ```bash
  /opt/homebrew/Caskroom/miniforge/base/envs/arpes_agent_test/bin/python -m pytest tests/test_maestro_measurement_log.py -v
  ```

  Expected: PASS (install pytest in that env only if missing: `pip install pytest` in that env after asking is OK for local; or run unittest). Prefer:

  ```bash
  /opt/homebrew/Caskroom/miniforge/base/envs/arpes_agent_test/bin/python -m pytest tests/test_maestro_measurement_log.py -v
  ```

  If pytest missing, use:

  ```bash
  /opt/homebrew/Caskroom/miniforge/base/envs/arpes_agent_test/bin/python -c "import pytest" || /opt/homebrew/Caskroom/miniforge/base/envs/arpes_agent_test/bin/pip install pytest
  ```

- [ ] **Step 4: Commit**

  ```bash
  git add scripts/maestro_measurement_log.py tests/test_maestro_measurement_log.py
  git commit -m "$(cat <<'EOF'
  feat: add FITS-first MAESTRO measurement logger script

  Prefer .fits as CSV identity; keep MH1 .h5 header/comment/0D extract.
  EOF
  )"
  ```

---

### Task 2: Pass A merge script

**Files:**
- Create: `scripts/merge_maestro_log_to_manifest.py`
- Create: `tests/test_merge_maestro_log_to_manifest.py`

**Interfaces:**
- Consumes: `MAESTRO_Measurement_Log.csv` from Task 1
- Produces: `merge_maestro_log(data_root: str, analysis_root: str | None = None) -> Path` writing `analysis/manifest.json`
- Manifest `FileEntry` additive fields: `log_comment`, `maestro_log` dict; `kind="unknown"`; `backend="pyarpes"`; `path` prefers fits

- [ ] **Step 1: Implement merge script**

  ```python
  # scripts/merge_maestro_log_to_manifest.py
  """Merge MAESTRO_Measurement_Log.csv into analysis/manifest.json (Pass A)."""
  import csv, json, os, re
  from datetime import datetime, timezone
  from pathlib import Path

  def stem_of(filename: str) -> str:
      return Path(filename).stem

  def parse_hv(cell: str):
      if not cell or cell == "N/A":
          return None
      m = re.search(r"([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)", cell)
      return float(m.group(1)) if m else None

  def merge_maestro_log(data_root: str, analysis_root: str | None = None) -> Path:
      data_root = Path(data_root).resolve()
      csv_path = data_root / "MAESTRO_Measurement_Log.csv"
      if not csv_path.is_file():
          raise FileNotFoundError(csv_path)
      analysis_root = Path(analysis_root).resolve() if analysis_root else (data_root / "analysis")
      analysis_root.mkdir(parents=True, exist_ok=True)
      manifest_path = analysis_root / "manifest.json"

      # load existing or new
      if manifest_path.is_file():
          manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
          by_stem = {e["stem"]: e for e in manifest.get("files", [])}
      else:
          now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
          manifest = {
              "schema_version": 1,
              "created_utc": now,
              "updated_utc": now,
              "data_root": str(data_root),
              "skill_ref": "arpes",
              "files": [],
          }
          by_stem = {}

      with csv_path.open(newline="", encoding="utf-8") as f:
          for row in csv.DictReader(f):
              fname = row["File Name"]
              st = stem_of(fname)
              fits = data_root / f"{st}.fits"
              fit = data_root / f"{st}.fit"
              h5 = data_root / f"{st}.h5"
              if fits.is_file():
                  path, path_alt, ext = str(fits), (str(h5) if h5.is_file() else None), ".fits"
              elif fit.is_file():
                  path, path_alt, ext = str(fit), (str(h5) if h5.is_file() else None), ".fits"
              elif h5.is_file():
                  path, path_alt, ext = str(h5), None, ".h5"
              else:
                  path, path_alt, ext = str(data_root / fname), None, Path(fname).suffix.lower() or ".h5"

              p = Path(path)
              entry = by_stem.get(st, {})
              entry.update({
                  "stem": st,
                  "path": path,
                  "path_alt": path_alt,
                  "ext": ext,
                  "preferred_loader": "arpes.io.load_data location=MAESTRO",
                  "backend": "pyarpes",
                  "loader": "MAESTRO",
                  "size_bytes": p.stat().st_size if p.is_file() else entry.get("size_bytes", 0),
                  "mtime_utc": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if p.is_file() else entry.get("mtime_utc", ""),
                  "log_comment": row.get("Pre/Post Comments") or None,
                  "kind": entry.get("kind") if entry.get("kind") not in (None, "unknown", "load_error") else "unknown",
                  # if kind already set by Pass B to cut/fermi/..., keep it
                  "maestro_log": {
                      "meas_type_log": row.get("Measurement Type"),
                      "photon_energy": row.get("Photon Energy (eV)"),
                      "polarization": row.get("Polarization"),
                      "cryostat_A_K": row.get("Cryostat A (K)"),
                      "cryostat_B_K": row.get("Cryostat B (K)"),
                      "cryostat_C_K": row.get("Cryostat C (K)"),
                      "cryostat_D_K": row.get("Cryostat D (K)"),
                      "manipulator": row.get("Manipulator Position"),
                      "deflection": row.get("Deflection Settings"),
                      "smu": row.get("SMU 1 & 2 Settings"),
                      "analyzer": row.get("Analyzer Settings"),
                      "energy_resolution": row.get("Energy Resolution"),
                  },
                  "hv_eV": parse_hv(row.get("Photon Energy (eV)", "")),
              })
              # Never overwrite a real kind with unknown:
              if st in by_stem and by_stem[st].get("kind") not in (None, "unknown", "load_error"):
                  entry["kind"] = by_stem[st]["kind"]
              else:
                  entry.setdefault("kind", "unknown")
              by_stem[st] = entry

      manifest["files"] = [by_stem[k] for k in sorted(by_stem)]
      manifest["updated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
      manifest["data_root"] = str(data_root)
      manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

      # optional short manifest.md
      md = analysis_root / "manifest.md"
      lines = ["| stem | backend | kind | hv | comment |", "|---|---|---|---|---|"]
      for e in manifest["files"]:
          c = (e.get("log_comment") or "")[:60].replace("|", "/")
          lines.append(f"| {e['stem']} | {e.get('backend','')} | {e.get('kind','')} | {e.get('hv_eV','')} | {c} |")
      md.write_text("\n".join(lines) + "\n", encoding="utf-8")
      return manifest_path

  if __name__ == "__main__":
      import sys
      if len(sys.argv) < 2:
          print("Usage: merge_maestro_log_to_manifest.py <data_folder> [analysis_folder]")
          sys.exit(1)
      data = sys.argv[1]
      analysis = sys.argv[2] if len(sys.argv) > 2 else None
      print(merge_maestro_log(data, analysis))
  ```

  Fix the `kind` logic carefully when implementing: if existing entry has real kind, keep it; else `unknown`. Do not use Measurement Type as kind.

- [ ] **Step 2: Test merge prefers fits path and fills maestro_log**

  ```python
  def test_merge_prefers_fits_and_keeps_comment(tmp_path):
      # write csv + empty fits + h5 names
      ...
      assert entry["path"].endswith(".fits")
      assert entry["maestro_log"]["meas_type_log"]
      assert entry["kind"] == "unknown"
  ```

- [ ] **Step 3: Run tests + commit**

  ```bash
  git add scripts/merge_maestro_log_to_manifest.py tests/test_merge_maestro_log_to_manifest.py
  git commit -m "$(cat <<'EOF'
  feat: merge MAESTRO CSV into analysis/manifest.json

  Pass A join by stem; FITS-preferred path; kind stays unknown.
  EOF
  )"
  ```

---

### Task 3: Skill docs (reference + example)

**Files:**
- Create: `reference/maestro-measurement-log.md`
- Create: `examples/maestro_measurement_log.md`
- Modify: `reference/folder-manifest.md` (Pass A MAESTRO subsection + `maestro_log` on FileEntry table)

- [ ] **Step 1: Write `reference/maestro-measurement-log.md`**

  Must include: when to use / triggers; CLI for both scripts; FITS-first + H5-meta; 14 columns; Measurement Type ≠ kind; quiet stdout; CSV freshness reuse; NAS fork rule; chat summary shape; no graphify; link folder-manifest Pass A.

- [ ] **Step 2: Write `examples/maestro_measurement_log.md`**

  ~20–40 lines: user says log folder → agent runs logger → merge → reports counts.

- [ ] **Step 3: Patch `folder-manifest.md`**

  - Add FileEntry optional `maestro_log` object.
  - In Build algorithm step 2, MAESTRO: run `scripts/maestro_measurement_log.py` if user asked log or CSV missing; then merge script / fill `log_comment` + `maestro_log`.
  - State Pass A ≠ Pass B.

- [ ] **Step 4: Commit**

  ```bash
  git add reference/maestro-measurement-log.md examples/maestro_measurement_log.md reference/folder-manifest.md
  git commit -m "docs: MAESTRO measurement log Pass A recipe"
  ```

---

### Task 4: Wire SKILL / README / capability / token / failures

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `reference/backend-capability-map.md`
- Modify: `reference/token-usage.md`
- Modify: `reference/failure-modes.md`

- [ ] **Step 1: SKILL.md**

  - Hard rules / Folder first: if user asks to log MAESTRO folder → `maestro-measurement-log.md` (CSV in folder + Pass A merge).
  - Workflow step near folder inventory.
  - References + examples lists.

- [ ] **Step 2: README one-liner** in What it does table.

- [ ] **Step 3: capability map rows**

  | `maestro_measurement_log` | Write MAESTRO_Measurement_Log.csv | `scripts/maestro_measurement_log.py` | same | | `maestro-measurement-log.md` |
  | `maestro_log_to_manifest` | Pass A CSV → manifest | `scripts/merge_maestro_log_to_manifest.py` | same | | `folder-manifest.md` |

- [ ] **Step 4: token-usage.md** — logger/merge scripts cheap; dumping CSV expensive.

- [ ] **Step 5: failure-modes.md** — treat log Measurement Type as kind; ignore FITS sibling; paste full CSV.

- [ ] **Step 6: Commit**

  ```bash
  git add SKILL.md README.md reference/backend-capability-map.md reference/token-usage.md reference/failure-modes.md
  git commit -m "docs: wire MAESTRO logger into skill entrypoints"
  ```

---

## Self-review (plan author)

| Spec requirement | Task |
|------------------|------|
| FITS-first File Name + H5 meta | Task 1 |
| CSV in data folder, 14 cols | Task 1 |
| CLI non-interactive | Task 1 |
| Quiet stdout | Task 1 |
| Pass A manifest merge + maestro_log | Task 2 |
| kind unknown / dims win | Task 2 + 3 |
| Trigger docs + SKILL wire | Task 3–4 |
| No graphify / no blanket token note | Task 3–4 |
| NAS fork documented | Task 3 |
| Capability living list | Task 4 |

No TBD placeholders. Merge script added (thin glue) so agents do not reimplement JSON join.

---

## Execution

User chose **Subagent-Driven** (token-saving). Controller: feature branch + SDD ledger; fresh implementer per task (fast model for Tasks 1–2, standard for docs); caveman-compressed return; review between tasks; no push.
