# Cross-System Service Involvement — ACDHS 2021 Synthetic Integrated Services Data

Descriptive co-occurrence analysis of the public synthetic release of Allegheny County DHS's
2021 Integrated Services data (Urban Institute / ACDHS): among 533,799 synthetic individuals
across 22 service categories, which services touch the same people within the year? The
project verifies the file against its own documentation before analyzing it, measures every
claimed category relationship instead of assuming it (four of the six documented "nesting"
relationships turned out not to be containment), pushes every pair through explicit
reliability floors and a human classification gate, and ends with four defensible findings —
a benefits-coverage channel, two quantified coordination overlaps, and one open question —
each carrying its caveats inline. The discipline is the deliverable: every fact is cited to a
source document or to logged output, every judgment is recorded, and nothing below the
reliability floor is reported as a finding.

## The funnel

| Stage | Pairs | Gate |
|---|---|---|
| All possible service pairs | 231 | — |
| Reportable | 139 | ≥ 30 shared persons (small-cell floor, M6) |
| Reliable | 31 | at/above the documented 0.5% fidelity tier (~5.2% vs ~34.4% median error) |
| **Findings** | **4** | analyst classification (Gate A) — structural and artifact pairs removed |

The classification record is [outputs/pairs_gateA_approved.csv](outputs/pairs_gateA_approved.csv)
(one row per reportable pair: stats, proposed class, analyst's final class). The reasoning
trail — every observation, inference, and decision, in order — is
[docs/findings_log.md](docs/findings_log.md). The findings brief (draft) is
[docs/brief_draft.md](docs/brief_draft.md).

## What this dataset cannot support

Claims deliberately **not** made anywhere in this project:

- **Causal or directional claims** — co-occurrence is a fence, not an arrow.
- **Within-year timing or sequencing** — months were synthesized independently per service;
  only annual co-occurrence is defensible.
- **Geography** — excluded from the release by design.
- **Rare-pair findings** — pairs below the 0.5%-of-individuals tier carry ~34.4% median
  synthesis error and are flagged `below_fidelity_tier`, never featured.
- **Prevalence/headcount claims for documented over/under-represented groups** (jail, child
  welfare families, homeless, homicide/suicide/overdose, older adults) — shape and relative
  claims only.
- **Multi-variable demographic cross-tabs** — documented fidelity degrades beyond
  single-variable breakdowns.

## Repo map

| Stage | Where | What |
|---|---|---|
| Verification | [notebooks/phase0_first_look.ipynb](notebooks/phase0_first_look.ipynb) | file vs. documentation: grain, 22 services, demographics, once-per-person incidents; builds `data/person_level.parquet` |
| Matrix | [src/phase1_matrix.py](src/phase1_matrix.py), [src/phase1_heatmaps.py](src/phase1_heatmaps.py) | co-occurrence (conditional %, lift, containment), floors and tier flags, Gate A candidates, heatmaps |
| Human gates | [src/phase1_gateA_worksheet.py](src/phase1_gateA_worksheet.py) → analyst → [src/phase1_gateA_approve.py](src/phase1_gateA_approve.py) | worksheet with pre-applied dispositions; analyst classifies; validated into the approved file |
| Findings record | [docs/findings_log.md](docs/findings_log.md) | RAN / OUTPUT / INFER / DECIDES / CHECK entries; corrections kept visible |
| Exports | [src/phase1_tableau_export.py](src/phase1_tableau_export.py) | tidy per-direction findings + population sizes for visualization |

Binding context: [CLAUDE.md](CLAUDE.md) (working rules),
[docs/documented_facts.md](docs/documented_facts.md) (cited facts — the factual authority),
[docs/project_intent.md](docs/project_intent.md) (aim and guardrails),
[docs/project_plan_decisions.md](docs/project_plan_decisions.md) (method decisions M1–M9).
Grounding tools ([docs/dhs_priority_map.md](docs/dhs_priority_map.md),
[docs/grounding_automation_design.md](docs/grounding_automation_design.md)) are provisional,
for the later grounding stage.

## Setup

    python -m venv .venv && source .venv/bin/activate
    pip install duckdb pandas pyarrow matplotlib jupyter

Place the dataset CSV (from WPRDC) at `data/dhs_service_records_synthesized_final.csv`.
`data/` stays in `.gitignore` — the file is ~1.4 GB and must not be committed. `outputs/` IS
committed: the approved file and filled worksheet carry analyst judgment and are not
regenerable.

## Run order

1. `notebooks/phase0_first_look.ipynb` — structural verification against the documentation,
   base-table build, first-look conclusions.
2. `python src/phase1_matrix.py` — matrices, ranked pairs, Gate A candidates.
3. `python src/phase1_heatmaps.py` — conditional and lift heatmaps.
4. `python src/phase1_gateA_worksheet.py` — builds the review worksheet; the analyst fills
   `final_class` for every row (the human gate — not scripted).
5. `python src/phase1_gateA_approve.py` — validates the filled worksheet and writes
   `outputs/pairs_gateA_approved.csv`; downstream reads only approved files.
6. `python src/phase1_tableau_export.py` — tidy exports for the four approved findings.

## Future work

- **Demographic deep-dive on the ID population** (single-variable lenses only, per the
  documented fidelity limits) behind the CHANNEL finding.
- **Phase 0 persistence re-run** — persist `total_service_months` / `distinct_services` into
  the parquet and re-execute the notebook (the 29-vs-31 correction in the findings log).
- **Confidential-data follow-up on the older-adults question** — artifact, federal benefit
  substitution, or genuine enrollment shortfall is not answerable in the synthetic file.
- **Grounding stage** — tie each finding to published DHS priorities with real URLs
  (Gate B), per the provisional design docs.
