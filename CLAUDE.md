# CLAUDE.md — binding project context

## Authority and evidence rule
- docs/documented_facts.md is the factual authority. EVERY statement there is cited to a source PDF
  (Understanding Synthetic Data, Synthetic Data User Guide, Generating a Fully Synthetic Human
  Services Dataset, Allegheny County Data Warehouse). Treat only cited facts as established.
- INFERENCES ARE NOT RECORDED AS FACTS. Anything not directly citable to a source PDF is an
  inference to be confirmed by running code against the data. Do not write inferences into the
  binding docs as if established. When code output confirms an inference, it may then be added to
  docs/documented_facts.md with the citation "[OBSERVED: <script/cell>, <date>]".
- If code output and a cited fact disagree, STOP and surface it — do not silently override either.

## Working rules (each traceable to documented_facts.md)
- Descriptive analysis only; no predictive modeling.
- Annual co-occurrence claims only; never month-sequencing/timing claims. Basis: Stage Two months
  used independent per-service lookup tables and later-month error is documented (income supports
  July–December). [GEN]
- Co-occurrence is a fence, not an arrow: never phrase as causal or directional.
- Relative/shape claims only for overrepresented populations (jail, Child Welfare families, homeless,
  homicide, suicide, overdose); never prevalence/headcount claims. Basis: [UG, Limitations] —
  overrepresentation is documented but distribution SHAPE is preserved.
- Demographic lenses: race, ethnicity, gender, marital status, education are the documented
  per-row demographics [UG]; age is used from the age variable [GEN]. Living arrangement is listed
  among row demographics in [UG] but appears in exclusion discussion in [GEN]; treat its
  availability as UNCONFIRMED until verified in the data, and do not rely on it until then.
- Two distinct documented sets, do not conflate: once-per-person = {homicides, suicides, overdoses,
  mental health crises} [GEN, Stage One]; asterisked incidents = {jail, homicides, overdoses,
  suicides} [UG, footnote].
- Min-support: no pair reported under 30 shared persons (recorded decision). Note the SEPARATE
  documented fidelity tier: pairs received by <0.5% of individuals have ~34.4% median error vs ~5.2%
  for ≥0.5% [GEN]; whether to flag pairs between these thresholds is an open decision pending output.
- Assert only mathematical invariants in code. Verify documented properties against citations.
  Everything else is an observation to interpret in writing; do not fill notebook Interpretation
  cells (analyst's authorship).
- Propose, don't decide: Gate A (structural vs informative pair classification) and Gate B
  (does a source truly ground a finding) are human decisions. Produce candidates with reason +
  source columns; over-flag to REVIEW when unsure. Downstream steps read only *_approved files.
- Never generate DHS priorities/dashboards from memory; extract only from fetched pages; every
  citation carries a real URL.

## Repo docs
- docs/documented_facts.md — cited facts from the four source PDFs (the factual AUTHORITY)
- docs/project_intent.md — what the project aims to achieve and the guardrails (no findings)
- docs/project_plan_decisions.md — method decisions M1-M9, each justified by a cited fact only
- docs/findings_log.md — observations/inferences/next-steps, written ONLY from output as work proceeds
- docs/grounding_automation_design.md, docs/dhs_priority_map.md — grounding tools, used at the grounding stage
(both PROVISIONAL — see status notes in those files; mapping and extraction unvalidated)

Note: "the four source documents" refers to the four external Urban Institute / DHS PDFs, not repo files.
Substantive content (observations, inferences, chosen population, findings, next-step order) is NOT
pre-recorded; it is produced from output and logged in findings_log.md.
