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

- **[2026-07-18] Rare-pair caution flag (M6, deferred).** RESOLVED 2026-07-19 — see the M6 entry
  below. Original text kept for the record: At Phase 1, add a step that counts how
  many reportable pairs (≥30 shared persons) fall BELOW the ~0.5%-of-individuals fidelity threshold
  (documented tier: ~34.4% median error below 0.5% vs ~5.2% at/above — documented_facts.md,
  service-pair fidelity [GEN]). That count is the input for the analyst's decision on whether to add
  a rare-pair caution flag. Decision is the analyst's, made from that number; log the count and the
  decision here when Phase 1 runs.

---

## [2026-07-18] — Phase 0 Check 3: are the excluded variables actually empty?

RAN: notebooks/phase0_first_look.ipynb, Check 3 (cell 60ee15c9). Full run via
nbconvert --execute --inplace, repo .venv (duckdb 1.5.4, pandas 3.0.3), kernel cwd
notebooks/.
OUTPUT: All eight excluded columns — GEO_AREA, DOB, DOD, GENDER_IDENTITY, SEX_ORIENT,
LEGAL_SEX, EMPLOYMENT_STATUS, VETERAN_FLAG — return nulls = 0 / 7,116,134,
distinct_non_null = 1, value = 'NA'. Zero true nulls in any of them.
INFER: documented_facts.md records [UG, "Excluded Variables"] as: excluded variables are
"present as columns populated with 'N/A' (null) to convey the confidential data's
structure". The file does not match that description twice over: the literal is the
two-character string 'NA' (no slash), and there are no NULLs at all — the parenthetical
"(null)" is the User Guide's prose, not a description of the bytes.
Engine split worth carrying: pandas read_csv coerces bare 'NA' to NaN by default (the
cell-1 sample preview shows NaN for these columns), while DuckDB read_csv_auto types them
VARCHAR and returns the string 'NA'. The same column therefore reads as null in one
engine and non-null in the other, so any emptiness test written against NULL will give
opposite answers depending on which engine runs it.
DECIDES: Excluded columns confirmed to carry no analysable values — no geographic analysis, no
DOB/DOD, gender identity, sexual orientation, legal sex, employment status, or veteran
flag, as designed. Any future emptiness check must be engine-aware and test contents,
not NULL-ness. NOT promoted to documented_facts.md: this is a conflict with the cited
prose, not a confirmation of it; line 135 stays as written and this entry is the
correction of record.
CHECK: Substance MATCHES [UG, "Excluded Variables"] (the columns carry nothing usable).
Wording DISCREPANCY on the same citation: '"N/A" (null)' describes neither the literal
nor the null-ness actually present.

---

## [2026-07-18] — Phase 0 Check 3b: is LIVING_ARRANGEMENT usable? (open decision M8)

RAN: notebooks/phase0_first_look.ipynb, Check 3b (cell e47ef0d0).
OUTPUT: LIVING_ARRANGEMENT: rows = 7,116,134, nulls = 0, distinct_non_null = 1, sample non-null
values = ['NA']. A constant sentinel across every row; zero real values.
INFER: The column exists but carries no information. Note the check was written content-aware
for exactly this case: a bare COUNT(DISTINCT) returns 1 here and would have been read as
"contains data", resolving M8 backwards.
DECIDES: M8's living-arrangement half is CLOSED — unavailable. The demographic lenses for this
project are firmly age, gender, race, ethnicity, marital status, education, and nothing
else. Living arrangement is NOT added to the person-level pivot. M8's other half —
minors' marital-status/education values as postprocessing artifacts [GEN,
"Postprocessing"] — remains open and is untouched by this result.
CHECK: Resolves the documented conflict, in favour of exclusion. [UG, "About the Data"] lists
living arrangement among the per-row demographics — CONTRADICTED by output. [UG,
"Excluded Variables"] lists "living situation" among the excluded columns, and [GEN,
"Variable Exclusions"] discusses it under exclusions — both MATCH output. CLAUDE.md's
instruction to treat its availability as UNCONFIRMED is now discharged.

---

## [2026-07-18] — Phase 0 Check 6: age eligibility on child-targeted services

RAN: notebooks/phase0_first_look.ipynb, Check 6 (cell a780a831).
OUTPUT: Children_Attending_Early_Childhood_Programs_Managed_by_DHS 0–5
Children_Receiving_Child_Welfare_Services 0–24
Children_Receiving_DHS_Funded_Out_of_School_Programs 0–17
Children_Receiving_Early_Intervention_Services 0–3
Children_in_Care 0–17
Child_Welfare_Services max age = 24; the other four child services stay at or below 17.
CHECK: Conflicts with documented_facts.md line 226 ([DW, Appendix #7], child welfare "covers
youth 18 or younger and their families"). Does NOT conflict with [GEN]: [GEN]'s applying-
constraints discussion confirms age caps were applied per-service from individual
eligibility rules, and names only DHS-funded out-of-school programs as its example —
which the data honours at 0–17. Child welfare's specific age cap is not stated in the
cited facts, so the "capped at age 18" phrasing in [GEN, "Stage One"] is an EXAMPLE
("e.g."), not a universal cap.
INFER: The observed max of 24 is consistent with per-service eligibility that may extend past 18
(e.g. extended foster care / independent living), but this CANNOT be confirmed from the
repo's cited facts. The published data dictionary provides no help — its age description
is erroneous boilerplate ("Age of Decedent for the morgue autopsy case"); see the
data-dictionary entry below.
DECIDES: RESOLVED 2026-07-19 (was OPEN). The observed max age of 24 is expected category
behaviour, not a discrepancy. QuickCount's Child Welfare definition explicitly
"includes services provided to transition-aged youth", with "Transition Age Youth"
defined as ages 14–24 requiring at least 30 days of child-welfare placement.
[DW #7]'s "youth 18 or younger" describes the CORE MALTREATMENT POPULATION, not the
full category, so the two are not in conflict. [QC-Programs definitions, reviewed
2026-07-19]. The shape-level caveat on age-based child-welfare analysis is lifted;
age-based child-welfare analysis may proceed on the 0–24 range.

---

## [2026-07-18] — Phase 0 Checks 1/2/4/5/7 + pivot: does the file match its documentation?

RAN: notebooks/phase0_first_look.ipynb, Checks 1, 2, 4, 5, 7 and the person-level pivot cell
(b59e9ff6). Full top-to-bottom run, exit 0.
OUTPUT: Scale/grain: 7,116,134 rows; 533,799 distinct persons; years present = [2021]; 22
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
Artifacts: data/person_level.parquet (533,799 x 29) and data/service_columns.json
(22 names) written.
[CORRECTION 2026-07-18: this line originally read "x 31". The run printed (533799, 31),
but that was the shape of the IN-MEMORY frame after the cell appended
total_service_months and distinct_services -- the COPY that wrote the parquet ran
BEFORE those two were computed, so the artifact on disk held 29 columns, not 31.
TO-DO (Phase 2): amend the pivot cell to re-save the frame after computing those two,
and re-run Phase 0 so code and stored output stay consistent. Deferred deliberately --
amending the cell without re-running would leave the committed Phase 0 artifact showing
code that contradicts its own output. Phase 1 does not need either column. Until that
re-run, the parquet on disk is 29 columns and this line reads 29.]
INFER: The file behaves as its creators described on every structural property tested, so
downstream analysis inherits their validation work. Two consequences that shape Phase 1:
(a) a per-(person, service) row count is a valid count of MONTHS RECEIVED, which the
pivot depends on; (b) with income supports at 94.1%, naive conditional co-occurrence
toward it will be inflated by prevalence alone — confirming M4's requirement to report
lift alongside conditional %.
DECIDES: Phase 1 may proceed on data/person_level.parquet. N = 533,799 is the person-level
denominator for everything downstream, which puts the documented 0.5%-of-individuals
fidelity tier at 2,669 shared persons — the cutoff the pending rare-pair decision (M6)
will be measured against.
CHECK: MATCHES [UG, "About the Data"] (22 services; service-month grain); [GEN, "Data Structure
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

RAN: Analyst inspection of the published data dictionary accompanying the release. NOT from
the Phase 0 notebook run, and not one of the four source PDFs — documented_facts.md
already notes the dictionary is a separate file.
OUTPUT: The age field is described as "Age of Decedent for the morgue autopsy case". The service
field is described as "Emergency Medical Service or Fire". Both are boilerplate carried
over from unrelated datasets and describe neither field.
INFER: The dictionary's field descriptions are unreliable for this release. The authoritative
definitions come from the source PDFs and are consistent with the Phase 0 output: age is
derived from date of birth as of the end of 2021 [GEN, "Creating the Gold Standard
Dataset"], and the service variable takes one of 22 values [UG, "About the Data"] — 22
observed. The erroneous age description is also what blocks the dictionary from settling
the child-welfare age question in the entry above.
DECIDES: Do not rely on the data dictionary's field descriptions anywhere in this project; take
definitions from the source PDFs only. No analytical impact, since that is already the
practice. Carry as a data-quality observation on the public release into the methodology
memo. TO-DO: capture the exact dictionary version/date alongside these quotes before the
memo cites them.
CHECK: Partial DISCREPANCY with documented_facts.md, which records [UG, "About the Data"] as
saying a data dictionary accompanies the dataset "with exact variable names and the
eligibility criteria for each service". Variable names are usable; the field descriptions
are not, so that expectation is only partly met.

---

## [2026-07-19] — Phase 1 Gate A: are the [UG]-indented nesting relationships real containment?

RAN: src/phase1_matrix.py (full run) over data/person_level.parquet, N = 533,799.
Containment measured as shared / min(size_A, size_B) for each of the six
[UG, "About the Data"] indented child→parent pairs.
OUTPUT: child -> parent child parent shared contained
Homeless_Population -> Homelessness_and_Housing_Services 3,415 21,823 3,415 100.0%
Mental_Health_Crises -> Mental_Health_Services 7,245 55,262 7,185 99.2%
Parents_CW -> Families_CW 7,078 3,118 2,446 34.6% (partial)
Children_CW -> Families_CW 7,306 3,118 17 0.2%
Children_in_Care -> Families_CW 2,237 3,118 4 0.2%
Early_Intervention -> Early_Childhood_Programs 6,752 349 11 0.2%

          Child-welfare cluster, shared persons (diagonal = service size):
                                Families  Children_CW  Parents_CW  Children_in_Care
            Families               3,118           17       2,446                 4
            Children_CW               17        7,306          29             2,211
            Parents_CW             2,446           29       7,078                 8
            Children_in_Care           4        2,211           8             2,237

          NOTE ON DENOMINATORS — two containment measures appear in the Phase 1 outputs and they
          are not interchangeable. The "contained" column above is CHILD-IN-PARENT
          (shared / size of the child category): the measure the nesting claim is actually
          about, and the one used in the Gate A reason strings for these six pairs. The
          containment_pct COLUMN in pairs_ranked.csv / pairs_gateA_candidates.csv is MIN-SIZE
          (shared / min(size_A, size_B)), because a general pair has no child and no parent.
          The two agree wherever the child is the smaller service — five of the six here. They
          DIVERGE for pair 2, Parents_CW -> Families_CW: child-in-parent is 34.6%
          (2,446 / 7,078) but min-size is 78.4% (2,446 / 3,118), because the child category
          (7,078) is LARGER than its documented parent (3,118). The min-size figure is not
          evidence of partial nesting; it is an artifact of the size inversion.

          Two of the six are containment; four are not. In two of the four the child category
          is LARGER than its documented parent (Children_CW 7,306 > Families 3,118; Early
          Intervention 6,752 > Early Childhood 349, a ~19x inversion), so containment is
          arithmetically impossible, not merely absent.

CHECK: Pairs 5 and 6 VERIFIED as containment and accepted as structural nesting. Pairs 1–4
FAILED verification and are NOT accepted as nesting: for these the [UG] indentation
denotes a reporting taxonomy, not set containment.

          Established explanation (analyst-verified against the source documents and the
          QuickCount program definitions): the child-welfare categories partition by ROLE, not
          nesting. "Children Associated with a Child Welfare Case" = children/youth under 18
          with an open case; "Parents Associated with a Child Welfare Case" = the parents of
          such children — different people by definition, so near-zero overlap is expected
          category behaviour rather than an error. The 29-person Children_CW ∩ Parents_CW
          overlap is PREDICTED by the QC definition's clause that parents may include under-18
          biological parents of an involved child. Early Intervention is a separate referral
          pipeline (AFIT), a sibling program to the early-childhood cluster, not a subset.
          [QC-Programs definitions, reviewed 2026-07-19]

          Rival explanation RULED OUT — synthesis error does not account for this, on three
          grounds:
          (a) the documented rare-pair error is ~34.4% median [GEN, "Summary of multiservice
              recipients"]; it cannot produce a ~99.8% collapse in overlap;
          (b) containment survived synthesis intact in pairs 5 and 6 (100.0% and 99.2%), so the
              process demonstrably preserves containment where it exists;
          (c) pair 4's size inversion would require a ~95% undercount of a SINGLE service,
              contradicting the documented single-service fidelity [GEN].

INFER: (analyst)
DECIDES: (analyst)

---

## [2026-07-19] — Addendum to the Gate A nesting entry: testing the QC teenage-parents prediction

RAN: src/phase1_check_cw_overlap.py over data/person_level.parquet. Persons with counts > 0
in BOTH Children_Receiving_Child_Welfare_Services and
Parents_Receiving_Child_Welfare_Services.
OUTPUT: Count = 29 — matches the co-occurrence matrix cell exactly.
Ages: min 15, median 16, max 21.
Full list (n=29): 15 ×11, 16 ×8, 17 ×5, 18 ×4, 21 ×1.
Gender: 19 Female (2~Female), 10 Male (1~Male).
CHECK: Against the QC Parents clause's prediction ([QC-Programs definitions, reviewed
2026-07-19]: parents may include under-18 biological parents of an involved child):
ages at-or-under ~18–20 would support the teenage-parents reading; a spread of
typical adult ages would contradict it. Observed: 24 of 29 are under 18; 28 of 29
are ≤ 18; the single exception is 21. No typical adult ages appear. Note the
documented age-eligibility context: the Children_CW category itself extends to 24
(transition-age youth — see the resolved age-24 entry), so ages 18–21 in this
overlap are within the category's documented range. Both genders present, consistent
with the clause's "biological parent" having no gender restriction.
Fidelity caveat carried: 29 shared persons is far below the 0.5% tier (2,669) and
below the 30-person reporting floor — this cell is examined as CATEGORY-SEMANTICS
EVIDENCE (what the categories mean), not as a reportable finding, and its exact
count/ages carry the documented ~34.4%-tier synthesis error.
INFER: The teenage-parents reading is supported — median age 16, 24/29 under 18, max 21 within the documented transition-age range, both genders present, no unexplained adult ages. The synthetic data preserved the dual-membership structure the QC clause permits. Caveat retained: this characterizes the synthetic pattern; the exact values carry rare-cell error.
DECIDES: Role-partition conclusion stands with composition-level support. Cell remains non-reportable (below floor and tier). Thread closed; memo-worthy as a predict-then-test methods example.

---

## [2026-07-19] — M6 decided: rare-pair caution flag

RAN: src/phase1_matrix.py, rare-pair fidelity tier count.
OUTPUT: 110 of 139 reportable pairs (>= 30 shared persons) fall below the documented
0.5%-of-individuals fidelity threshold — 2,669 shared persons of N = 533,799.
DECIDES: M6 CLOSED. The rare-pair caution flag is ADOPTED. A below_fidelity_tier column is
carried on outputs/pairs_ranked.csv and outputs/pairs_gateA_candidates.csv. The
30-person reporting floor is unchanged.
CHECK: Threshold is the documented tier from [GEN, "Summary of multiservice recipients"]
(~34.4% median error below 0.5%, ~5.2% at/above); the 2,669 cutoff follows from
N = 533,799 [OBSERVED: notebooks/phase0_first_look.ipynb, 2026-07-18].

---

## [2026-07-19] — Gate A complete: analyst classification of all 139 reportable pairs

RAN:      Analyst filled outputs/pairs_gateA_review_worksheet.csv (built by
          src/phase1_gateA_worksheet.py from the candidates file, with the dictated
          pre-applied dispositions); src/phase1_gateA_approve.py validated it (no empty
          final_class, row count and pair set identical to the candidates file) and wrote
          outputs/pairs_gateA_approved.csv. Downstream steps read the approved file only.
OUTPUT:   Final counts by final_class (139 total):
            BELOW_TIER                                  108
            NOT_A_FINDING                                20
            STRUCTURAL_BY_RECORDING_SCOPE (INFERRED)      3
            INFORMATIVE                                   3
            STRUCTURAL                                    2
            STRUCTURAL_BY_DEFINITION                      2
            INFORMATIVE (negative association)            1

          The 4 INFORMATIVE pairs (all at/above the 0.5% fidelity tier, ~5.2% median error):
            A <-> B                                      shared   lift  P(B|A)  P(A|B)  contain.
            Mental_Health_Services <-> Substance_Use      5,278   3.98   9.6%   41.2%    41.2%
            Homelessness_and_Housing <-> Mental_Health    5,004   2.21  22.9%    9.1%    22.9%
            Income_Supports <-> Intellectual_Disability   6,111   1.02   1.2%   96.1%    96.1%
            Income_Supports <-> Older_Adults (NEGATIVE)   5,311   0.34   1.1%   31.7%    31.7%

          Exclusion context for reading these counts:
          - 92 of 231 possible pairs never reached the worksheet (below the 30-person
            reporting floor), including 3 of the 6 [UG]-indented nesting pairs (shared
            17 / 4 / 11).
          - 108 reportable pairs were blanket-marked BELOW_TIER per the M6 decision
            (~34.4% median error tier), not individually adjudicated.
          - So the informative verdicts were drawn from the 31 pairs that were both
            reportable and at/above the fidelity tier (27 at-tier REVIEW + 2 verified
            nesting + 2 at-tier recording-scope, per the worksheet groupings).
CHECK:    Consistent with the project premise test (project_intent.md): the co-occurrence
          matrix yields at least some non-structural, cross-system overlaps — 4 informative
          pairs of 31 reliable candidates — rather than only structural ones. All four sit
          at/above the documented fidelity tier [GEN, "Summary of multiservice recipients"].
          The MH <-> SUD and Homelessness <-> MH pairs match overlap domains DHS itself
          publishes on (docs/dhs_priority_map.md: behavioral health crisis response;
          homelessness & housing — PROVISIONAL mapping, to be validated at grounding).
          The negative Income <-> Older_Adults association carries the documented
          undercount caveat for older adults [UG, "Limitations"], and Income_Supports
          demographic fidelity is strongest for common services [GEN] — both bear on how
          far the lift=0.34 can be trusted; noted here, not resolved.
INFER:    (analyst)
DECIDES:  (analyst)
