# ARPESskill multi-agent orchestration — Design Spec

**Date:** 2026-09-23  
**Status:** Draft for user review  
**Branch:** `feat/multi-agent`  
**Repo:** https://github.com/fawkesdx/ARPESskill  

## 1. Purpose

Keep ARPESskill as one portable Cursor skill, but add an **optional multi-agent
mode**: an orchestrator delegates catalog / overview / analysis / report work to
specialist agents with **hard fences** (reliability first), **thin context**
(specialists do not load the whole skill), and **parallelism last** (only when
fences allow).

This does **not** replace the existing single-agent workflow. Single-agent
remains the default for simple one-file asks.

## 2. Priority order (locked)

1. **Reliability** — role allowlists; no invent axes/physics; wrong role cannot
   run forbidden steps.  
2. **Context** — each specialist gets only the docs + file row it needs.  
3. **Speed** — parallel only for independent stems/tasks after (1)–(2).

## 3. Approach (locked)

**Approach A:** One skill (`arpes`) + dispatch rules in
`reference/multi-agent.md` (+ short wire in `SKILL.md`).

**Out of scope for v1:**  
- Separate Cursor skills per role (Approach B)  
- External graphs / LangGraph / SDK product (Approach C)  
- Changing PyARPES itself  

## 4. Roles

| Role | Responsibility | May use | Must not |
|------|----------------|---------|----------|
| **Orchestrator** | Clarify ask; choose role(s); merge short reports; ask user on ambiguity | Full `SKILL.md` hard rules; decide handoffs | Invent axes/EF/Γ/k; silent full-folder `load_data` |
| **Catalog** | Folder listing + **header-only peek** → manifest rows | `folder-manifest.md`, `formats-and-axes.md` (header bits), `pyarpes-env.md` if import check only | `load_data`; read FITS `HDU.data` / HDF5 `[:]`; fits; k; Σ |
| **Overview** | One stem: `load_data` + default overview PNGs | `default-overview-plots.md`, `formats-and-axes.md`, load path | Peak fit / k / kz / Σ / dichroism invent; catalog whole folder |
| **Analysis** | One user-asked workflow on a **stated** product | Matching `reference/<workflow>.md` + `package-first` / capability map rows for that ID only | Change `kind` without ask; skip EF/Γ/V₀ rules; DIY outside package |
| **Report** | Summarize assumptions, paths, anti-claims | Manifest + PNG/npz paths + prior agent notes | Re-run heavy analysis; invent numbers |

Capability IDs (living list) act as **allowlists** per role — see §6.

## 5. Shared state (blackboard)

Primary: `analysis/manifest.json` (or `analysis/<label>/manifest.json` if the
skill already uses labeled folders).

Optional append-only: `analysis/agent_log.jsonl` — one JSON object per handoff:

```json
{
  "ts": "ISO-8601",
  "role": "catalog|overview|analysis|report|orchestrator",
  "stem": "...",
  "action": "...",
  "ok": true,
  "notes": "short",
  "paths": ["analysis/..."]
}
```

**Handoff payload** (orchestrator → specialist): role, stem, absolute/relative
`path`, relevant manifest row fields, allowed capability IDs, output paths to
write, and **which reference file(s)** to open. Not the full chat history.

**Handoff return** (specialist → orchestrator): short caveman/summary status,
updated manifest fields, artifact paths, assumptions echoed, errors quoted.

## 6. Reliability gates

1. Catalog never calls `load_data` / spectrum arrays.  
2. Overview only after Catalog row exists (or single-file path user gave).  
3. Analysis only when prerequisites for that workflow are met (e.g. EF before k
   per `k-and-kz-conversion.md`); else return “blocked: ask user”.  
4. One Analysis agent **per spectrum product** at a time — no two writers.  
5. Hard rules in `SKILL.md` still apply to every role (orchestrator enforces).  
6. Package-first: specialists may not write new loaders without orchestrator
   escalating to user ask.  
7. Anti-claims (Γ / k / EF / kz) listed in Report always.

### Suggested allowlist sketch (v1)

| Role | Example capability IDs |
|------|------------------------|
| Catalog | `folder_manifest`, `folder_header_peek`, `state_axes` (header-only) |
| Overview | `load_spectrum`, `overview_plot`, `spatial_overview` (if spatial) |
| Analysis | Subset matching the asked workflow only (e.g. `fit_peak`, `convert_k`, …) |
| Report | none that mutate data — read-only |

Exact tables ship in `reference/multi-agent.md` at implementation.

## 7. Context policy

- Orchestrator: thin plan + manifest summary; does not paste arrays.  
- Specialist Task prompt: role card + 1–3 reference paths + one stem/path +
  allowlist. Prefer compressed return (caveman-style bullets).  
- Do not inject entire `reference/` tree into every specialist.

## 8. Speed / parallelism (last)

| Allowed parallel | Forbidden parallel |
|------------------|--------------------|
| Catalog peeks on different stems | Two writers on same stem/spectrum |
| Overview on different stems (after rows exist) | Analysis + Overview on same stem without lock |
| Independent Analysis on **different** stems if user asked batch | Cross-role mutation of same `product_paths` |

Default concurrency: low (e.g. 2–4 Catalog peeks). Token note before large
parallel batches (`token-usage.md`).

## 9. When to use multi-agent vs single-agent

| Situation | Mode |
|-----------|------|
| One file, one ask (fit / overview / k) | **Single-agent** (current) |
| Folder map / many stems | **Multi-agent** (Catalog ± parallel) |
| User asks several independent analyses | **Multi-agent** (Analysis per stem) |
| Ambiguous physics / missing V₀ / Γ | Orchestrator **asks user**; do not spawn Analysis |

## 10. Deliverables (implementation — after this spec approved)

1. `reference/multi-agent.md` — roles, allowlists, handoff schema, spawn
   checklist.  
2. Wire `SKILL.md` — short “Multi-agent (optional)” section + workflow step.  
3. `reference/failure-modes.md` + `token-usage.md` rows.  
4. Capability IDs if needed (`orchestrate`, `agent_handoff`) in
   `backend-capability-map.md`.  
5. Optional `examples/multi_agent.md` — one folder-map scenario.  

No Python package in v1. No change to PyARPES.

## 11. Git / process

- Develop on **`feat/multi-agent`**.  
- Recipe work on `main` continues independently.  
- Merge multi-agent docs to `main` when user approves implementation PR.  
- Delete feature branch after merge (same hygiene as other feats).

## 12. Non-goals (v1)

- Guaranteed wall-clock speedups  
- Separate published skills per role  
- Autonomous overnight beamtime without user gates  
- TensorSpec / external orchestrator products  

## 13. Success criteria

- Agent facing a folder uses Catalog header peek, not full loads, when
  multi-agent mode applies.  
- Analysis specialist cannot “casually” invent k without EF/Γ policy docs.  
- Orchestrator chat stays short; heavy detail lives in manifest + files.  
- Single-file simple asks still work without forcing multi-agent.

## 14. Open points (resolve at implementation if needed)

- Exact concurrency default (2 vs 4).  
- Whether `agent_log.jsonl` is required or optional.  
- Named manifest dirs `analysis/<label>/` vs flat `analysis/manifest.json`
  (follow whatever `folder-manifest.md` on `main` says at implement time).
