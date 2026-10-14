# Demo 0: Getting Started — "Your own copy of the workshop"

**Session:** Day 1, 8:30–9:00 (30 min) · **You build:** a Git folder with the workshop repo, and your own copy of the workshop data in `<my_schema>` · **Reference:** the shared starting state in `<catalog>.<schema>` (same data, value for value)
**Starting state:** read access to the GitHub repo `thhart-dbx/client__revantage__luxembourg-workshop__2026-10-08__tbd`; USE CATALOG on `<catalog>`, read on `<catalog>.<schema>`, and either CREATE SCHEMA on `<catalog>` or a pre-created `<my_schema>` with ALL PRIVILEGES (sandbox job)
**Where:** Settings (Linked accounts), Workspace (Git folder), notebook on serverless, Catalog Explorer, Genie Code side panel

Everything you need for the two days lives in one Git repo: one guide per module with the exact
prompts (`code/prompts/`), the handout (`assets/participant-handout.md`), the source of every reference
asset, and a notebook that builds the workshop data. In this module you clone it into Databricks as a
**Git folder**, then run the notebook to build your own copy of the data, so you can change it freely
without affecting anyone else.

## Stage 1: Link your GitHub account (5 min)
Profile (top right) → **Settings** → **Linked accounts** → **Git integration** → Git provider **GitHub** → **Link Git account** and approve the Databricks app in GitHub (or choose **Personal access token** and paste a GitHub token with read access to repos).
**Checkpoint:** Linked accounts shows **GitHub** with your GitHub user name.
**If stuck:** the repo is private: check that your GitHub user has accepted the invitation to `thhart-dbx/client__revantage__luxembourg-workshop__2026-10-08__tbd` (github.com → your notifications).

## Stage 2: Create the Git folder (5 min)
**Workspace** → **Home** → **Create** → **Git folder**. Git repository URL `https://github.com/thhart-dbx/client__revantage__luxembourg-workshop__2026-10-08__tbd`, provider **GitHub**, folder name `revantage-workshop` → **Create Git folder**.
**Checkpoint:** the folder shows the branch **main** at the top and contains `README.md`, `RUNBOOK.md`, `assets/` and `code/`.
**If stuck:** "Repository not found" or "Invalid Git credentials" means the GitHub link (Stage 1) or the repo invitation is missing: fix that and create the Git folder again.

## Stage 3: Find your way around the repo (5 min)
Open `code/prompts/`: one guide per module (`d01-…` to `d18-…`), each with the prompts to type, the expected result and an "if stuck" fallback. `code/reference/` holds the answer-key SQL, `code/setup/` the data setup.
Open `code/setup/participant_setup.py`, then the Genie Code panel (top right):
> Explain what this notebook does, step by step, and which objects it will create.

**Expected:** Genie Code describes the four widgets (catalog, shared schema, my schema, as-of date), creating your schema with the `raw` and `documents` volumes, running `setup_starting_state.py` to generate the CSVs, copy the PDFs and build bronze → silver → gold, and the PASS/FAIL checks at the end.

## Stage 4: Build your copy of the data (10 min)
In `participant_setup.py`: compute **Serverless**, fill the widgets **1. Workshop catalog** = `<catalog>` and **2. Shared workshop schema** = `<schema>` (the names shared at the start of the session); leave **3. My schema** blank (it becomes `<schema>_<your name>`) and **4.** as is → **Run all**.
**Expected:** after about 3 minutes, the last cell prints 8 **PASS** lines: gold 80 rows / 8 properties / 2024-Q1–2026-Q2, Southeast 2026-Q2 net profit ≈ €2.09M, 16 starting tables, 8 Module 17 legacy tables, 7 CSVs, 8 / 4 / 3 PDFs, and *"Done. In the module prompts, <my_schema> is …"*.
**If stuck:** `PERMISSION_DENIED` on CREATE SCHEMA: your schema hasn't been created for you yet; ask for the sandbox job to be run, then **Run all** again (the notebook is safe to re-run). Until then, every module works on the shared data in `<catalog>.<schema>`.

## Stage 5: Check your copy (5 min)
**Catalog** → `<catalog>` → `<my_schema>`: the bronze, silver and gold tables, the `legacy_*` tables, and the volumes `raw` and `documents`.
Open the Genie Code panel in a new SQL editor tab:
> Compare <my_schema>.gold_property_quarterly with <catalog>.<schema>.gold_property_quarterly: same number of rows, and how many rows differ? Run it and check the result.

**Expected:** **80** rows in each and **0** rows that differ (Genie Code writes an `EXCEPT ALL` or a full outer join). Your copy is the workshop data, value for value, so every expected result in the modules holds for it.
**If stuck:**
```sql
SELECT COUNT(*) AS differences FROM (
  SELECT * FROM <my_schema>.gold_property_quarterly
  EXCEPT ALL
  SELECT * FROM <catalog>.<schema>.gold_property_quarterly)
```

## Reset
Re-run `participant_setup.py` (**Run all**): it rebuilds your copy from scratch. Get the latest guides with the Git folder's branch button → **Pull**.

## Wrap-up
- **So what:** everyone has the material and a private copy of the data before the first module, so a broken build only ever breaks your own copy.
- **Two schemas from here on:** `<catalog>.<schema>` is the shared workshop data and holds the answer keys (`ref_*`); `<my_schema>` is your copy, where you build. You can point any module prompt at `<my_schema>` instead of `<catalog>.<schema>`.
