# Method Decisions (document-derived only)

These are the only decisions made in advance, because each is justified purely by a cited fact in
documented_facts.md — not by any result. Everything substantive (which population, which findings,
groundings, next-step order) is produced from output and lives in findings_log.md.

| # | Decision | Justifying documented fact |
|---|----------|----------------------------|
| M1 | Descriptive analysis only; no predictive modeling. | Aim is cross-service description; the dataset's strength is annual co-occurrence structure (Stage One). |
| M2 | Annual co-occurrence claims only; no month-sequencing claims. | Stage Two assigned months via independent per-service lookup tables; later-month error is documented (income supports Jul–Dec). |
| M3 | Co-occurrence is a fence, not an arrow (never causal/directional). | Data records only that two services occurred for one person in 2021; nothing about order or cause. |
| M4 | Compute lift alongside conditional %. | Services vary greatly in prevalence; a common service would inflate raw conditional co-occurrence. (Prevalence spread is documented; exact dominance to be confirmed from output.) |
| M5 | Relative/shape claims only for overrepresented populations; no prevalence claims. | Overrepresentation of jail, CW families, homeless, homicide, suicide, overdose is documented; distribution SHAPE is preserved but counts are not. |
| M6 | Small-cell reporting floor (min shared persons before a pair is reported). | County suppresses public counts under 6; rarer pairs also carry much higher synthesis error (~34% vs ~5%). Exact threshold is a recorded choice; whether to add a rare-pair caution flag is DEFERRED to output. |
| M7 | Single-variable demographic breakdowns preferred over multi-variable cross-tabs. | Demographic fidelity degrades from one-way to all-way joint frequencies (documented). |
| M8 | Treat marital-status/education for minors, and living-arrangement availability, as suspect until verified. | Postprocessing forced under-18 marital/education values to "unknown"; living arrangement is listed as a row demographic in UG but in the exclusion discussion in GEN. Confirm from output. |
| M9 | Every finding ends in a practical implication grounded in DHS's own published work. | DHS authorizes action research (analysis + strategies developed from it). |

Note: "documented most-common service = income supports" is a documented fact; its actual prevalence
in this synthetic file is an OBSERVATION to confirm from output, not assumed here.
