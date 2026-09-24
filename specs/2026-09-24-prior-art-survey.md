# Prior art survey — ARPES tooling & agentic work

**Date:** 2026-09-24  
**Purpose:** Avoid novelty claims. Map what already exists vs ARPESskill.  
**Status:** Living notes (exploration); not a product claim.

## Headline

**`arpespythontools` is not an LLM/agent system** — it is a classical Python
analysis library (load / k-convert / plot). Name can mislead (“tools” ≠ agents).

Closest **agent-skill** prior art found: **ERLabPy ships `skills/arpes-analysis/`**
(full `SKILL.md` + reference packs + `agents/openai.yaml` + Custom GPT badge).
Same *genre* as this repo (agent instructions over an ARPES Python stack),
different backend (ERLabPy vs PyARPES).

### Whose lab is ERLabPy?

| | |
|--|--|
| **Author** | [Kimoon Higashihira Han](https://github.com/kmnhan) (`khan@kaist.ac.kr`), PhD student, KAIST Physics ([kimoonhan.com](https://kimoonhan.com/)) |
| **Lab** | **Electronic structure Research Laboratory (ERLab)**, KAIST — PI **Prof. Yeongkwan Kim** — [erlab.kaist.ac.kr](https://erlab.kaist.ac.kr/people/professor) |
| **Package name** | README also expands ERLab as “Extensible and Reproducible Library for the Analysis of Band structures”; affiliation is Kim group |
| **Related** | `1KARPES_DAQ` (ultra-low-T ARPES DAQ at KAIST); Custom GPT: “ARPES Analysis Assistant” on README |

### Claim hygiene (fawkesdx / ARPESskill)

Local scan of `README.md` + `SKILL.md` on `main` / `feat/multi-agent`: **no**
“first / novel / pioneer / world-first” novelty claims. Soft phrasing only:
“General LLM agent skill for ARPES analysis via PyARPES.” “What this is not”
already defers to PyARPES. Prior-art survey explicitly forbids first-skill
claims. (Full org-wide GitHub code search blocked here by `gh` auth; re-check
other public repos after `gh auth refresh` if needed.)

No evidence (as of this survey) of a mature **multi-role Cursor/Claude
ARPES multi-agent product** that matches Catalog/Overview/Analysis/Report or
Report-maker / DFT-expert / panel-drawer. Broader **scientific agent skills**
(e.g. AtomisticSkills) exist outside ARPES.

---

## 1. Classical ARPES analysis software (not agentic)

| Project | Link | What it is |
|---------|------|------------|
| **PyARPES** | [chstan/arpes](https://github.com/chstan/arpes), [docs](https://arpes.readthedocs.io/), SoftwareX 2020 | Full analysis framework; loaders; k/kz; fits; interactive tools; MAESTRO etc. **ARPESskill’s default backend.** |
| **ERLabPy (`erlab`)** | [kmnhan/erlabpy](https://github.com/kmnhan/erlabpy) | Complete Python ARPES workflow + Qt ImageTool; xarray; fitting; many beamline plugins. |
| **arpespythontools** | [pranabdas/arpespythontools](https://github.com/pranabdas/arpespythontools), [PyPI](https://pypi.org/project/arpespythontools/) | Load SES spectra, k-conversion, visualization docs site. **Library, not LLM agents.** |
| **PIVA** | [pudeIko/piva](https://github.com/pudeIko/piva) | PyQt GUI for 2D/3D/4D ARPES inspection; beamtime utilities; Jupyter export. |
| **Igor Pro ecosystem** | (legacy standard) | Waves + beamline macros; PyARPES/ERLabPy/PIVA all position against this. |

ML-on-ARPES (compression / clustering, e.g. **ARPESNet** autoencoder papers) is
**data ML**, not coding agents — cite separately if claiming AI for ARPES.

---

## 2. Agentic / LLM skill prior art (closest)

| Project | Link | Relevance |
|---------|------|-----------|
| **ERLabPy `arpes-analysis` skill** | [skills/arpes-analysis/](https://github.com/kmnhan/erlabpy/tree/main/skills/arpes-analysis) | **Direct peer.** Agent skill: load → EF → Γ → k → EDC/MDC → publication figures; notebook-first; strong calibration gates; auxiliary skills coordination; `agents/openai.yaml`. |
| **AtomisticSkills** | [learningmatter-mit/AtomisticSkills](https://github.com/learningmatter-mit/AtomisticSkills), arXiv 2605.24002 | Agentic IDE skills for **atomistic/DFT/MLIP** (Cursor/Claude/etc.). Pattern: Workflows → Skills → Tools. **DFT-expert persona** should cite this lineage, not invent vacuum. |
| Domain skills generally | e.g. PyMC analytics skills, many Cursor/Claude `SKILL.md` packs | Genre: domain skill packages for coding agents — not ARPES-specific. |

### ERLabPy skill depth (read 2026-09-24)

Layout under [`skills/arpes-analysis/`](https://github.com/kmnhan/erlabpy/tree/main/skills/arpes-analysis):

- `SKILL.md` — operating contract; notebook-first; analysis order 1–9; decision
  rules; interactive ImageTool / goldtool / ktool / ftool / Figure Composer;
  **user must approve Γ for publication k**.
- `references/fermi-calibration.md` — Au/Ag `gold.poly`, flat `quick_fit`,
  no sample-band curvature invent, **per-hv** centers.
- `references/momentum-conversion.md` — alignment groups; `set_normal` /
  `set_normal_like`; KTool handoff; underdetermined → ask.
- `references/curve-analysis.md` — EDC/MDC / dispersion.
- `references/publication-plotting.md` — panels, styles, export (close to a
  “panel drawer” role).
- `agents/openai.yaml` — display name **“ARPES Research Assistant”**.

### ERLabPy skill vs ARPESskill (honest delta)

| | ERLabPy skill | ARPESskill (this repo) |
|--|---------------|-------------------------|
| Backend | ERLabPy (Python ≥3.11) | PyARPES (Python 3.8) |
| Artifact | Executable Jupyter notebook primary | Scripts + `analysis/` products + recipes |
| Physics gates | Strong EF / normal-emission / no invent | Strong EF / Γ / V₀ / anti-claims |
| GUI | ImageTool / KTool first-class | Prefer scripted; GUIs optional |
| Pub figures | Dedicated `publication-plotting.md` | Spread across overview + recipes |
| Multi-agent | Coordinator + *auxiliary skills* (notebook/viz/file) | Spec: Catalog / Overview / Analysis / Report |
| Folder / beamtime | Alignment tables in notebook | `folder-manifest` + header-only peek |
| Distribution | Inside analysis package + Custom GPT | Standalone Cursor/Claude skill repo |

**Do not claim “first ARPES agent skill.”** ERLabPy already published one
(and a Custom GPT).

**Possible honest niches (if any):** PyARPES-oriented portable skill;
reliability-first multi-role dispatch; living capability map; MAESTRO/ALS
conventions as used here — always framed as **complement / fork of practice**,
not invention of agentic ARPES. Learn from their gates (esp. Γ approval +
notebook provenance) rather than rebranding the same idea.

---

## 3. Scientific multi-agent platforms (adjacent, not ARPES)

Examples only — patterns to acknowledge if writing papers/README “related work”:

- ChemGraph (LangGraph + ASE chemistry)
- NexusSci / S1-NexusAgent (multi-tool science agents)
- Various LangGraph paper-RAG / extraction agents

These show **role-specialized agents** are common; ARPES-specific roles are not.

---

## 4. Survey gaps / revisit

- GitHub code search for other `SKILL.md` + ARPES (rate-limited during this pass;
  re-run periodically).
- Beamline-internal copilots (often private) — assume they exist; don’t claim
  uniqueness of “assistant for beamtime.”
- TensorSpec / lab-specific stacks — deferred in this skill by design.

---

## 5. Process note (this repo)

Exploration of new agent **names/roles** → short-lived `explore/roles-*`
branches + `specs/` only → promote winners into `feat/multi-agent` → merge
`main` only when locked.

Prior-art updates belong in this file (or dated successors), not in `SKILL.md`
until intentional.
