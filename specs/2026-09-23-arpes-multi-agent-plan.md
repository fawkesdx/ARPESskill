# Multi-agent ARPESskill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship optional multi-agent orchestration docs so Cursor agents can split ARPES work into Catalog / Overview / Analysis / Report roles with hard fences, thin context, and parallelism last.

**Architecture:** Approach A — one `arpes` skill; new `reference/multi-agent.md` is the dispatch bible; `SKILL.md` wires when to use multi-agent vs single-agent; manifest remains the blackboard. No Python package; no PyARPES changes.

**Tech Stack:** Markdown Agent Skills layout; Cursor Task/subagents for spawn; existing `analysis/manifest.json` schema from `folder-manifest.md`.

**Spec:** `specs/2026-09-23-arpes-multi-agent-design.md`

## Global Constraints

- Priority locked: reliability → context → speed.
- Single-agent remains default for simple one-file asks.
- Catalog = header-only peek (never `load_data` / `HDU.data` / HDF5 `[:]`).
- One Analysis writer per spectrum product at a time.
- Living-list: new capability IDs in `backend-capability-map.md` same change.
- Branch: `feat/multi-agent` until user merges PR.
- `docs/` is gitignored — keep plans/specs under `specs/`.

## File map

| File | Role |
|------|------|
| Create `reference/multi-agent.md` | Roles, allowlists, handoff schema, spawn checklist, parallel rules |
| Create `examples/multi_agent.md` | One folder-map scenario |
| Modify `SKILL.md` | Short multi-agent section + workflow step + refs/examples |
| Modify `reference/backend-capability-map.md` | IDs `orchestrate`, `agent_handoff` (+ role notes) |
| Modify `reference/failure-modes.md` | Wrong-role / parallel-writer / force-multi failures |
| Modify `reference/token-usage.md` | Parallel spawn token note |
| Modify `reference/folder-manifest.md` | Point to multi-agent for folder map (1 short cross-link) |
| Modify `README.md` | One row: optional multi-agent orchestration |
| Modify `specs/2026-09-23-arpes-multi-agent-design.md` | Status → Approved / implementing |

---

### Task 1: `reference/multi-agent.md` core

**Files:**
- Create: `reference/multi-agent.md`
- Spec: `specs/2026-09-23-arpes-multi-agent-design.md` §§4–9

**Produces:** Complete dispatch reference agents will open.

- [ ] **Step 1: Write `reference/multi-agent.md`** with sections:
  - Gate / when multi-agent vs single-agent (copy table from spec §9)
  - Priority order (reliability → context → speed)
  - Role table (Orchestrator, Catalog, Overview, Analysis, Report) with May / Must not
  - Capability allowlists per role (use real IDs from `backend-capability-map.md`; Analysis = “only IDs for the asked workflow”)
  - Blackboard: `manifest.json` + optional `agent_log.jsonl` schema (spec §5)
  - Handoff payload + return contract (bullet lists; keep short)
  - Reliability gates (spec §6 numbered list)
  - Parallel rules (allowed / forbidden table)
  - Spawn checklist for Orchestrator (numbered)
  - Hard: no invent axes; escalate ambiguity to user; package-first

- [ ] **Step 2: Self-check** — grep file for `load_data` in Catalog section only as **forbidden**; ensure Overview/Analysis not mixed.

- [ ] **Step 3: Commit**

```bash
git add reference/multi-agent.md
git commit -m "docs: add multi-agent dispatch reference"
```

---

### Task 2: Example + capability map

**Files:**
- Create: `examples/multi_agent.md`
- Modify: `reference/backend-capability-map.md` (append rows after `folder_header_peek` or at end of inventory)

**Produces:** Example scenario + living-list IDs.

- [ ] **Step 1: Write `examples/multi_agent.md`** — folder beamtime scenario:
  1. Orchestrator → Catalog (header peek) → manifest
  2. User picks stem → Overview
  3. User asks fit → Analysis (`edc-mdc-fitting.md` only)
  4. Report summarizes paths + anti-claims  
  Note parallel Catalog peeks OK; no dual Analysis on same stem.

- [ ] **Step 2: Add capability rows:**

| ID | Meaning | PyARPES default | Reference |
|----|---------|-----------------|-----------|
| `orchestrate` | Choose single vs multi; spawn roles | Cursor Task / main agent — not a PyARPES call | `multi-agent.md` |
| `agent_handoff` | Write/read handoff + optional `agent_log.jsonl` | thin glue under `analysis/` | `multi-agent.md` |

- [ ] **Step 3: Commit**

```bash
git add examples/multi_agent.md reference/backend-capability-map.md
git commit -m "docs: multi-agent example + capability IDs"
```

---

### Task 3: Wire SKILL + README

**Files:**
- Modify: `SKILL.md` (Hard rules, Workflow, References, Examples; optional When to use)
- Modify: `README.md` (What it does table — one row)

**Produces:** Agents discover multi-agent from entry skill.

- [ ] **Step 1: Add hard rule** after Folder first (or near Token awareness):

```markdown
- **Multi-agent (optional):** folder maps / independent multi-stem work →
  `reference/multi-agent.md` (roles + allowlists). Default single-agent for
  one-file simple asks. Reliability fences before parallel.
```

- [ ] **Step 2: Add workflow step** after folder/manifest step (renumber if needed):  
  If folder map or user asks multi-agent / parallel stems → follow `multi-agent.md`; else continue single-agent.

- [ ] **Step 3: Add** References + Examples links to `multi-agent.md` / `examples/multi_agent.md`.

- [ ] **Step 4: README** row e.g. `| Multi-agent | Optional Catalog/Overview/Analysis/Report dispatch (reliability-first) |`

- [ ] **Step 5: Commit**

```bash
git add SKILL.md README.md
git commit -m "docs: wire multi-agent into SKILL and README"
```

---

### Task 4: Failure modes, tokens, folder cross-link

**Files:**
- Modify: `reference/failure-modes.md`
- Modify: `reference/token-usage.md`
- Modify: `reference/folder-manifest.md` (short cross-link only)
- Modify: `specs/2026-09-23-arpes-multi-agent-design.md` (status line)

**Produces:** Guardrails consistent with other workflows.

- [ ] **Step 1: failure-modes rows** e.g.:
  - Analysis role runs Catalog-forbidden `load_data` on whole folder
  - Two Analysis writers on same stem
  - Force multi-agent on trivial one-EDC ask
  - Specialist missing allowlist / invents DIY

- [ ] **Step 2: token-usage** — parallel Catalog/Overview batch note; prefer manifest over chat dumps.

- [ ] **Step 3: folder-manifest** — one line: folder first-map may use multi-agent Catalog role (`multi-agent.md`).

- [ ] **Step 4: Spec status** → `Approved — implementing` or `Implemented` when PR ready.

- [ ] **Step 5: Commit**

```bash
git add reference/failure-modes.md reference/token-usage.md reference/folder-manifest.md specs/2026-09-23-arpes-multi-agent-design.md
git commit -m "docs: multi-agent failure/token cross-links"
```

---

### Task 5: Verify + PR

**Files:** none new — verification only.

- [ ] **Step 1: Grep checks**

```bash
rg -n "multi-agent" SKILL.md README.md reference/ examples/
rg -n "orchestrate|agent_handoff" reference/backend-capability-map.md
# Catalog must-not still forbids load_data in multi-agent.md
rg -n "load_data" reference/multi-agent.md
```

Expected: SKILL/README/example/map wired; `load_data` appears only as forbidden for Catalog (or Overview/Analysis allowed context).

- [ ] **Step 2: Push + open PR** against `main` (do **not** merge until user says merge).

```bash
git push -u origin HEAD
gh pr create --title "docs: optional multi-agent orchestration" --body "## Summary
- Add reference/multi-agent.md + example
- Reliability-first roles; manifest blackboard; parallel last
- Wire SKILL / map / failure / token

## Test plan
- [ ] One-file ask stays single-agent
- [ ] Folder map uses Catalog header peek only
- [ ] Analysis allowlist blocks casual k invent
"
```

- [ ] **Step 3: Stop** — wait for user merge approval. Delete remote branch after merge.

---

## Execution notes

- Prefer **subagent-driven-development** for Tasks 1–4 if parallelizing review; Tasks are mostly sequential (2 depends on 1 IDs wording; 3 depends on 1 existing).
- Do not restore unrelated stash `wip-header-peek-refinements` into this PR unless user asks.
- After merge: single-agent recipes on `main` unchanged in behavior except optional multi-agent path.
