# Findings Log

Grows only from output. Nothing here is pre-decided. Each entry follows one shape:

    ## [date] — <what step / question>
    RAN:      <script / notebook cell / query>
    OUTPUT:   <what the numbers or visual actually showed>
    INFER:    <what I conclude from that output — labeled as inference>
    DECIDES:  <what this makes the next step; any decision it settles>
    CHECK:    <against which documented_facts.md fact, if any — match or discrepancy>

When an inference is confirmed by output, it may be promoted into documented_facts.md tagged
[OBSERVED: <source>, <date>].

---

## Pending decisions (recorded before output; not findings)

- **[2026-07-18] Rare-pair caution flag (M6, deferred).** At Phase 1, add a step that counts how
  many reportable pairs (≥30 shared persons) fall BELOW the ~0.5%-of-individuals fidelity threshold
  (documented tier: ~34.4% median error below 0.5% vs ~5.2% at/above — documented_facts.md,
  service-pair fidelity [GEN]). That count is the input for the analyst's decision on whether to add
  a rare-pair caution flag. Decision is the analyst's, made from that number; log the count and the
  decision here when Phase 1 runs.

---

## [2026-07-18] — Phase 0 Check 3: are the excluded variables actually empty?

RAN:      notebooks/phase0_first_look.ipynb, Check 3 (cell 60ee15c9). Full run via
          nbconvert --execute --inplace, repo .venv (duckdb 1.5.4, pandas 3.0.3), kernel cwd
          notebooks/.
OUTPUT:   All eight excluded columns — GEO_AREA, DOB, DOD, GENDER_IDENTITY, SEX_ORIENT,
          LEGAL_SEX, EMPLOYMENT_STATUS, VETERAN_FLAG — return nulls = 0 / 7,116,134,
          distinct_non_null = 1, value = 'NA'. Zero true nulls in any of them.
INFER:    documented_facts.md records [UG, "Excluded Variables"] as: excluded variables are
          "present as columns populated with 'N/A' (null) to convey the confidential data's
          structure". The file does not match that description twice over: the literal is the
          two-character string 'NA' (no slash), and there are no NULLs at all — the parenthetical
          "(null)" is the User Guide's prose, not a description of the bytes.
          Engine split worth carrying: pandas read_csv coerces bare 'NA' to NaN by default (the
          cell-1 sample preview shows NaN for these columns), while DuckDB read_csv_auto types them
          VARCHAR and returns the string 'NA'. The same column therefore reads as null in one
          engine and non-null in the other, so any emptiness test written against NULL will give
          opposite answers depending on which engine runs it.
DECIDES:  Excluded columns confirmed to carry no analysable values — no geographic analysis, no
          DOB/DOD, gender identity, sexual orientation, legal sex, employment status, or veteran
          flag, as designed. Any future emptiness check must be engine-aware and test contents,
          not NULL-ness. NOT promoted to documented_facts.md: this is a conflict with the cited
          prose, not a confirmation of it; line 135 stays as written and this entry is the
          correction of record.
CHECK:    Substance MATCHES [UG, "Excluded Variables"] (the columns carry nothing usable).
          Wording DISCREPANCY on the same citation: '"N/A" (null)' describes neither the literal
          nor the null-ness actually present.

---

## [2026-07-18] — Phase 0 Check 3b: is LIVING_ARRANGEMENT usable? (open decision M8)

RAN:      notebooks/phase0_first_look.ipynb, Check 3b (cell e47ef0d0).
OUTPUT:   LIVING_ARRANGEMENT: rows = 7,116,134, nulls = 0, distinct_non_null = 1, sample non-null
          values = ['NA']. A constant sentinel across every row; zero real values.
INFER:    The column exists but carries no information. Note the check was written content-aware
          for exactly this case: a bare COUNT(DISTINCT) returns 1 here and would have been read as
          "contains data", resolving M8 backwards.
DECIDES:  M8's living-arrangement half is CLOSED — unavailable. The demographic lenses for this
          project are firmly age, gender, race, ethnicity, marital status, education, and nothing
          else. Living arrangement is NOT added to the person-level pivot. M8's other half —
          minors' marital-status/education values as postprocessing artifacts [GEN,
          "Postprocessing"] — remains open and is untouched by this result.
CHECK:    Resolves the documented conflict, in favour of exclusion. [UG, "About the Data"] lists
          living arrangement among the per-row demographics — CONTRADICTED by output. [UG,
          "Excluded Variables"] lists "living situation" among the excluded columns, and [GEN,
          "Variable Exclusions"] discusses it under exclusions — both MATCH output. CLAUDE.md's
          instruction to treat its availability as UNCONFIRMED is now discharged.

---

## [2026-07-18] — Phase 0 Check 6: age eligibility on child-targeted services

RAN:      notebooks/phase0_first_look.ipynb, Check 6 (cell a780a831).
OUTPUT:   Children_Attending_Early_Childhood_Programs_Managed_by_DHS  0–5
          Children_Receiving_Child_Welfare_Services                   0–24
          Children_Receiving_DHS_Funded_Out_of_School_Programs        0–17
          Children_Receiving_Early_Intervention_Services              0–3
          Children_in_Care                                            0–17
          Child_Welfare_Services max age = 24; the other four child services stay at or below 17.
CHECK:    Conflicts with documented_facts.md line 226 ([DW, Appendix #7], child welfare "covers
          youth 18 or younger and their families"). Does NOT conflict with [GEN]: [GEN]'s applying-
          constraints discussion confirms age caps were applied per-service from individual
          eligibility rules, and names only DHS-funded out-of-school programs as its example —
          which the data honours at 0–17. Child welfare's specific age cap is not stated in the
          cited facts, so the "capped at age 18" phrasing in [GEN, "Stage One"] is an EXAMPLE
          ("e.g."), not a universal cap.
INFER:    The observed max of 24 is consistent with per-service eligibility that may extend past 18
          (e.g. extended foster care / independent living), but this CANNOT be confirmed from the
          repo's cited facts. The published data dictionary provides no help — its age description
          is erroneous boilerplate ("Age of Decedent for the morgue autopsy case"); see the
          data-dictionary entry below.
DECIDES:  OPEN discrepancy. Promote nothing age-related to documented_facts.md. TO-DO: verify child
          welfare's actual age definition against the source [DW] PDF before resolving. Until then,
          carry as a shape-level caveat on any age-based child-welfare analysis.

---

## [2026-07-18] — Phase 0 Checks 1/2/4/5/7 + pivot: does the file match its documentation?

RAN:      notebooks/phase0_first_look.ipynb, Checks 1, 2, 4, 5, 7 and the person-level pivot cell
          (b59e9ff6). Full top-to-bottom run, exit 0.
OUTPUT:   Scale/grain: 7,116,134 rows; 533,799 distinct persons; years present = [2021]; 22
            distinct service values.
          Grain uniqueness: max rows per (person, service) = 12; max distinct month-ends = 12;
            groups over 12 rows = 0; over 12 months = 0; with more rows than distinct months = 0.
          Demographics: zero persons show more than one value for any of age, GENDER, RACE,
            ETHNICITY, MARITAL_STATUS, EDUCATION_LEVEL.
          Once-per-person incidents: max 1 row per person for all four — Homicides (172 persons),
            Mental_Health_Crises (7,245), Overdoses (1,319), Suicides (1,177).
          Distribution: modal total service-months = 12, held by 328,472 persons = 61.5%. Top five
            totals: 12 (328,472), 4 (13,313), 1 (12,682), 36 (10,961), 2 (10,451).
          Prevalence: most common service = Individuals_Receiving_Income_Supports, 94.1% of persons.
          Artifacts: data/person_level.parquet (533,799 x 31) and data/service_columns.json
            (22 names) written.
INFER:    The file behaves as its creators described on every structural property tested, so
          downstream analysis inherits their validation work. Two consequences that shape Phase 1:
          (a) a per-(person, service) row count is a valid count of MONTHS RECEIVED, which the
          pivot depends on; (b) with income supports at 94.1%, naive conditional co-occurrence
          toward it will be inflated by prevalence alone — confirming M4's requirement to report
          lift alongside conditional %.
DECIDES:  Phase 1 may proceed on data/person_level.parquet. N = 533,799 is the person-level
          denominator for everything downstream, which puts the documented 0.5%-of-individuals
          fidelity tier at 2,669 shared persons — the cutoff the pending rare-pair decision (M6)
          will be measured against.
CHECK:    MATCHES [UG, "About the Data"] (22 services; service-month grain); [GEN, "Data Structure
          and Features"] (2021 only); [UG, "About the Data"] (demographics constant per person);
          [GEN, "Stage One"] (four once-per-person incidents); [UG, "Limitations"] / [GEN,
          "Individual-level service counts"] (clustering at multiples of 12, largest spike at 12);
          [GEN, "Stage One"] (income supports the most common service).
          NOT verified: [UG, "Limitations"] documents slight UNDERcounts at 24 and 36 service-
          months and overcounts above 12 at non-multiples of 12. Only the top five totals were
          printed (36 appears at 10,961; 24 does not appear in the top five), which is not enough
          to evaluate either claim. The full distribution was not examined.

---

## [2026-07-18] — Published data dictionary: erroneous field descriptions

RAN:      Analyst inspection of the published data dictionary accompanying the release. NOT from
          the Phase 0 notebook run, and not one of the four source PDFs — documented_facts.md
          already notes the dictionary is a separate file.
OUTPUT:   The age field is described as "Age of Decedent for the morgue autopsy case". The service
          field is described as "Emergency Medical Service or Fire". Both are boilerplate carried
          over from unrelated datasets and describe neither field.
INFER:    The dictionary's field descriptions are unreliable for this release. The authoritative
          definitions come from the source PDFs and are consistent with the Phase 0 output: age is
          derived from date of birth as of the end of 2021 [GEN, "Creating the Gold Standard
          Dataset"], and the service variable takes one of 22 values [UG, "About the Data"] — 22
          observed. The erroneous age description is also what blocks the dictionary from settling
          the child-welfare age question in the entry above.
DECIDES:  Do not rely on the data dictionary's field descriptions anywhere in this project; take
          definitions from the source PDFs only. No analytical impact, since that is already the
          practice. Carry as a data-quality observation on the public release into the methodology
          memo. TO-DO: capture the exact dictionary version/date alongside these quotes before the
          memo cites them.
CHECK:    Partial DISCREPANCY with documented_facts.md, which records [UG, "About the Data"] as
          saying a data dictionary accompanies the dataset "with exact variable names and the
          eligibility criteria for each service". Variable names are usable; the field descriptions
          are not, so that expectation is only partly met.
