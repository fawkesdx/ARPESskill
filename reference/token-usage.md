# Token usage (inform the user)

ARPES work can use many LLM tokens when the agent dumps large arrays, walks
whole beamtime folders in-chat, or re-reads big logs. **Warn the user before
expensive steps** — not to discourage, but so they can choose scope / batching.

Tone: calm, factual. Offer a lighter path when useful.

## When to warn (say this pattern)

> **Token note:** This next step may use a lot of context/tokens because
> [reason]. I can instead [lighter option]. Proceed with the full step,
> or prefer the lighter option?

Wait for a clear preference when the step is clearly high-cost. For mild
cost, a one-line note + continue is enough.

## High-cost steps (warn before starting)

| Step | Why tokens spike | Lighter alternative |
|------|------------------|---------------------|
| Catalog **many** files in one reply | Metadata + shapes × N in chat | Build `analysis/manifest.json` (+ short `manifest.md`); chat = counts by kind only (`folder-manifest.md`) |
| Paste **full array / DataArray** into chat | Huge numeric dumps | Print shape, coords, min/max/mean; save `.nc` / plot PNG under `analysis/` |
| Re-load whole **measurement log** repeatedly | Long CSV in context | Cache summary once; store `log_comment` on manifest rows |
| Re-walk folder every follow-up turn | Wastes tokens | **Recall** `analysis/manifest.json`; refresh only if mtime/hash changed |
| **Broadcast fits** over full 2D/3D maps | Long fit reports × many curves | Fit one EDC/MDC first; then scripted broadcast → save params CSV |
| **Spatial XY** full-volume plots / PCA / all-pixel fits | Huge cubes × many PNGs / fits | Hot-spot kind analysis first; stated ROI \(R\); broadcast only if asked (`spatial-xy-scans.md`) |
| **In-operando** full stack along every \(P\) step | Many slices × fits | Mid \(P^*\) (or asked step) first; broadcast along \(P\) only if asked (`in-operando-param-scans.md`) |
| **trARPES** full delay cube fits / k | Many delays × heavy steps | delay\* near t0 + Δ map first; convert/fit one delay if asked (`tr-arpes.md`) |
| **Self-energy** full-cut MDC broadcast + Σ | Long fit reports × many energies | One energy/window first; then scripted `fit_for_self_energy` → save Σ (`self-energy.md`) |
| **Band enhance** many slices / 3D volume | Many derived PNGs | One 2D cut first; both maps only (`band-enhance.md`) |
| **FS pocket** dense radial EDCs | Many angles × curves | Sample curves first; full EDCs only if asked (`fs-pocket.md`) |
| **Deconvolve** many iterations / full volume | Heavy arrays + many trials | One 2D cut; state PSF; stop if artifacts (`smooth-deconvolve.md`) |
| **Background** hull on huge maps | Many 1D ops × pixels | One EDC / ROI first (`backgrounds.md`) |
| **BZ** many `repeat` zones + GUI tools | Extra plots / Qt | One FS + stated rotate/repeat; scripted overlay (`bz-overlay.md`) |
| **Rebin / normalize** whole volumes silently | Hidden intensity change | Echo factors; one cut first (`axis-prep.md`) |
| **Mask** huge cubes without stated ROI | Waste + wrong mean | Echo condition; reduce after mask (`masks.md`) |
| **Align** many pairs / full volumes | Many correlations | One ROI pair first (`align.md`) |
| **NMF/ICA/PCA** large hypercubes | Heavy sklearn + many maps | Ask; small ROI / fewer components first (`decomposition.md`) |
| **Stack** many axes / huge max_stacks | Dense PNGs | One stack_axis; let package rebin (`stack-plots.md`) |
| Full **k / kz conversion** volumes + prose dump | Large grids in text | Convert in script; plot or save; chat = axes + assumptions only |
| Attach / describe **many PNG** overviews | Image tokens add up | Few representative figures; rest on disk |
| Install + long **pip/conda logs** in chat | Noisy build output | Run install quietly; report only success/fail + env path |
| Re-read entire `reference/` every turn | Skill context bloat | Read one matching reference file when needed |

## Low-cost steps (usually no warning)

- One file: load → dims/coords/units sanity print  
- One mid-cut or near-EF map plot saved to `analysis/figures/`  
- One EDC/MDC extract + one peak fit  
- Short checklist / yes-no questions  

## Agent habits that save tokens

1. Prefer **scripts under `analysis/`** that write reports/figures; summarize results in chat.
2. Never paste raw intensity arrays into the conversation.
3. Cap catalogs: default to a **sample** (e.g. 3–5 peek loads) before offering
   full-folder Pass B; always write **manifest** rather than pasting rows in chat.
4. After a long tool log, reply with a **short** status — do not echo the whole log.
5. Keep PyARPES env path in one line; do not re-paste install recipes every turn.
6. Follow-ups: open `analysis/manifest.json` first (`folder-manifest.md`).

## Example one-liners

- Full folder catalog:  
  *“Token note: I’ll build `analysis/manifest.json` (listing, then peek) and only
  paste kind counts here — OK?”*

- Broadcast MDC fits across a cut:  
  *“Token note: broadcast fits produce long reports. I’ll fit one MDC here, then run the rest in a script and save `widths.csv` — OK?”*
