# Cross-System Service Involvement -- ACDHS 2021 Synthetic Integrated Services Data

Descriptive co-occurrence analysis of the public synthetic version of Allegheny County DHS's
2021 Integrated Services data, built to mirror the analytical tradition of the county's own
integrated Data Warehouse reporting.

## Analytical discipline used throughout

- **Mathematical invariants** are asserted (violations = code bugs).
- **Documented properties** (from the Urban Institute User Guide and technical report) are
  verified and cited -- see the Phase 0 notebook's expectations table.
- **Empirical results** are observed and interpreted in writing after each step -- never
  assumed in advance.

## Setup

    python -m venv .venv && source .venv/bin/activate
    pip install duckdb pandas pyarrow matplotlib jupyter

Place the dataset CSV (from WPRDC) at data/dhs_service_records_synthesized_final.csv
and keep data/ in .gitignore -- the file is ~1.4 GB and must not be committed.

## Run order

1. notebooks/phase0_first_look.ipynb -- structural verification against the documentation,
   base-table build, first-look conclusions (fill in the reasoning cells as you go).
2. python src/phase1_matrix.py -- co-occurrence matrices + ranked pairs.
3. python src/phase1_heatmaps.py -- conditional and lift heatmaps.
4. Manual gate: classify the top pairs in outputs/pairs_ranked.csv as
   STRUCTURAL / INFORMATIVE / REVIEW with one-line reasons before any finding is written.

# Cross-System Service Involvement -- ACDHS 2021 Synthetic Integrated Services Data

Descriptive co-occurrence analysis of the public synthetic version of Allegheny County DHS's
2021 Integrated Services data. The analysis follows the county's own cross-system reporting
tradition; its value depends on the co-occurrence matrix yielding genuinely informative
(non-definitional) overlaps, which is confirmed only at Phase 1.

## Analytical discipline used throughout

- **Mathematical invariants** are asserted (violations = code bugs).
- **Documented properties** are verified against docs/documented_facts.md, where every fact is
  cited to a source PDF -- see the Phase 0 notebook's checks.
- **Empirical results** are observed and interpreted in writing after each step -- never
  assumed in advance.
- **Substantive content** (observations, chosen focus, findings, next steps) is produced from
  output and recorded in docs/findings_log.md -- never pre-decided.

## Where the thinking lives

Before running, read docs/project_intent.md (the aim and guardrails) and
docs/documented_facts.md (what the source documents establish, with citations). Method decisions
justified purely by those documents are in docs/project_plan_decisions.md. Grounding tools
(docs/dhs_priority_map.md, docs/grounding_automation_design.md) are provisional and used only at
the later grounding stage.

## Setup

    python -m venv .venv && source .venv/bin/activate
    pip install duckdb pandas pyarrow matplotlib jupyter

Place the dataset CSV (from WPRDC) at data/dhs_service_records_synthesized_final.csv
and keep data/ in .gitignore -- the file is ~1.4 GB and must not be committed.

## Run order

1. notebooks/phase0_first_look.ipynb -- structural verification against the documentation,
   base-table build, first-look conclusions (fill in the reasoning cells as you go).
2. python src/phase1_matrix.py -- co-occurrence matrices + ranked pairs.
3. python src/phase1_heatmaps.py -- conditional and lift heatmaps.
4. Manual gate: classify the top pairs in outputs/pairs_ranked.csv as
   STRUCTURAL / INFORMATIVE / REVIEW with one-line reasons before any finding is written.

Everything after step 4 is driven by what the output shows, not by a fixed plan. Record each
step's observations, inferences, and resulting decisions in docs/findings_log.md as you go.
