# Documented Facts — Cited to Source PDFs Only

**Rule for this file:** every statement is a direct citation to one of the four Urban Institute / DHS
source documents. No inferences, no derived numbers, no "consequences." Anything not citable to a
source PDF does not belong here — it is an inference to be confirmed by running code, and is kept out
of the binding docs until confirmed.

Source abbreviations:
- **[USD]** Understanding Synthetic Data
- **[UG]** Synthetic Data User Guide
- **[GEN]** Generating a Fully Synthetic Human Services Dataset
- **[DW]** Allegheny County Data Warehouse (July 2018)

---

## Dataset structure

- The synthetic dataset is structured on the service-month level: each row is associated with one
  synthetic individual, one service received by that individual, and the month in 2021 that the
  individual received the service. [UG, "About the Data"]
- If an individual received multiple services, one service in multiple months, or a combination,
  they are represented by more than one row. [UG, "About the Data"]
- An ID variable uniquely identifies service recipients; it has no association with the confidential
  ID but can tie repeat service usage to one synthetic individual. [UG, "About the Data"]
- Allegheny County tracks service usage monthly as a binary variable indicating whether a recipient
  did or did not receive a service at least once in a given month; "date of event" took the value of
  the last day of each month. [GEN, "Data Structure and Features"]
- "Year of event" exclusively took the value 2021 because all data were from 2021. [GEN, "Data
  Structure and Features"]
- Grain uniqueness verified in the released file: across 7,116,134 rows / 533,799 persons, no
  (person, service) group exceeds 12 rows or 12 distinct month-end dates, and no group has more
  rows than distinct months (zero duplicates). A per-(person, service) row count is therefore a
  valid count of MONTHS RECEIVED. [OBSERVED: notebooks/phase0_first_look.ipynb Check 2, 2026-07-18]

## Services

- The service variable takes one of 22 possible values. [UG, "About the Data"]
- The released file contains exactly 22 distinct service values, matching the documented count.
  [OBSERVED: notebooks/phase0_first_look.ipynb Check 1, 2026-07-18]
- The 22 services, with nesting shown by indentation in the source, are:
  Individuals receiving DHS services; Families receiving Child Welfare services
  (→ Children receiving Child Welfare services; → Parents receiving Child Welfare services;
  → Children in care); Children receiving DHS funded out-of-school programs; Children attending
  early childhood programs managed by DHS (→ Children receiving early intervention services);
  Individuals receiving family strengthening programs; Individuals receiving homelessness and
  housing services (→ Individuals identified as homeless); Individuals receiving intellectual
  disability services; Individuals receiving mental health services (→ Individuals receiving
  services for a mental health crisis); Individuals with an involuntary commitment; Individuals
  receiving substance use disorder services; Individuals receiving income supports; Individuals in
  the Allegheny County jail*; Older adults receiving services; Homicides*; Overdoses*; Suicides*.
  [UG, "About the Data"]
- The asterisk (*) marks variables that "denote incidents to which Allegheny County DHS responded,"
  not services received; "services" is used for brevity. Asterisked items: jail, homicides,
  overdoses, suicides. [UG, footnote]
- Homicides, suicides, overdoses, AND mental health crises only appear in the confidential data once
  per individual, and this constraint was reflected in the synthetic service counts. [GEN, "Stage
  One"]  (NOTE: this once-per-person set of FOUR is distinct from the asterisked incident set; mental
  health crises is once-per-person but is NOT asterisked, and jail IS asterisked but is not in the
  once-per-person set.)
- The once-per-person constraint holds in the released file: Homicides, Suicides, Overdoses and
  Mental_Health_Crises each show a maximum of one row per person (172 / 1,177 / 1,319 / 7,245
  persons respectively). [OBSERVED: notebooks/phase0_first_look.ipynb Check 5, 2026-07-18]

## Demographics

- Demographic variables included in each row are race, ethnicity, gender, marital status,
  educational status, and living arrangement. [UG, "About the Data"]
- Demographic values remain the same across every record associated with one synthetic individual,
  and represent the most recent information as of June 2022, when the data were pulled. [UG, "About
  the Data"]
- Verified in the released file: all six per-row demographics (age, gender, race, ethnicity,
  marital status, education) are constant within person — zero persons show more than one value
  for any of them. [OBSERVED: notebooks/phase0_first_look.ipynb Check 4, 2026-07-18]
- Stage One aimed to match service usage distributions by demographic, "particularly age, gender,
  race, and ethnicity." [GEN, "Stage One"]
- Excluded variables (chosen for exclusion due to sparsity / disclosure risk): gender identity,
  sexual orientation, and additional sparse fields. [GEN, "Variable Exclusions"; UG, "Excluded
  Variables"]  (The county-tracked confidential fields also included geographic area, date of birth,
  date of death, gender identity, sexual orientation, legal sex, employment status, veteran flag —
  [GEN, dataset variable list].)

## Synthesis method (governs what claims are supported)

- Fully synthetic: all variables synthesized; no one-to-one mapping between confidential and
  synthetic records; identity and attribute disclosure risks considered low. [USD; UG; GEN]
- 77 synthetic datasets were generated; the released one best balanced quality and privacy, chosen
  with county partners. [GEN, "Evaluating and Selecting a Synthetic Dataset"]
- Stage One synthesized annual service-month counts sequentially, using previously synthesized
  variables as predictors; "variables synthesized earlier in the sequence are subjected to less
  propagated modeling error." [GEN, "Stage One"]
- Synthesis order: income supports first (as "the most common service"), then race, ethnicity,
  gender, age, every other service most- to least-received, then living arrangement, marital status,
  education level. [GEN, "Stage One"]
- Age eligibility constraints were applied (e.g., services targeted to children capped at age 18).
  [GEN, "Stage One"]
- Stage Two assigned months to counts using per-service, per-count, per-month probability lookup
  tables, with must/cannot logic; it was not jointly modeled across services (264-column full
  imputation was not computationally feasible). [GEN, "Stage Two"]

## Documented quality findings and limitations

- Service-month count distributions show clustering around multiples of 12, because many individuals
  receive a service at least once every month of the year. [UG, "Limitations"; GEN, "Individual-
  level service counts"]
- The synthetic data slightly undercount individuals at 24 and 36 service-months, and slightly
  overcount individuals above 12 service-months that are not multiples of 12. [UG, "Limitations"]
- The largest spike is at 12 service-months, reflecting the most common pattern: income supports for
  12 months and no other services. [GEN, "Individual-level service counts"]
- January–March tended to overcount service receipt; December undercounted it. [UG, "Limitations"]
- Overrepresented populations: jailed population, families receiving Child Welfare services,
  homeless population, those who experienced homicide and suicide, and those who overdosed. [UG,
  "Limitations"]
- Older adults receiving services are undercounted. [UG, "Limitations"]
- Younger individuals are slightly undercounted, EXCEPT the homeless population and those who
  experienced suicide, which are overcounted for individuals under 18. [UG, "Limitations"]
- Despite over/undercounts, the SHAPE of the distribution remains similar between synthetic and
  confidential data (e.g., a June-to-July drop is reflected even if both months are overcounted).
  [UG, "Limitations"]
- Specific service-demographic combinations exceed a 20% difference from the confidential data for
  gender, race, and ethnicity (see UG Tables 1–3 for the enumerated combinations). [UG,
  "Limitations"]
- Discriminant-model variable importance was highest for age, education, and marital status
  (a postprocessing side effect), and for income supports in months July–December (reflecting error
  propagated to later months by the two-stage process). [GEN, "Evaluating Synthetic Data Quality"]
- Service-pair fidelity: median absolute percent difference ~5.2% for pairs received by ≥0.5% of
  individuals, ~34.4% for pairs received by fewer than 0.5%; differences are smaller for more common
  combinations and larger for rarer ones. [GEN, "Summary of multiservice recipients"]
- Demographic relative-frequency fidelity DEGRADES as variables are combined: differences are
  smallest for one-way (single-variable) frequencies and grow larger for three-way and all-way joint
  combinations. Implication for analysis: single-variable demographic breakdowns are more reliable
  than multi-variable cross-tabs. [GEN, "Utility Metrics — Categorical relative frequencies"]
- Age fidelity is service-dependent: it aligns very closely for the common income-supports service,
  but for less common services synthesized later (e.g., child welfare) the synthetic age distribution
  only mimics the general SHAPE, not each point. [GEN, "Age summary statistics" / Figures 5A, 5B]
- Postprocessing converted unrealistic marital-status and education values for certain under-18s to
  "unknown" (e.g., children <16 with above-high-school education; children <18 with a marital status
  other than "single never married" or "unknown"). Implication: marital-status/education patterns for
  minors are partly cleanup artifacts, not observed values. [GEN, "Postprocessing"]

## Derivation and formatting facts (affect how the data is read)

- Age was derived by converting date of birth to age as of the end of 2021. [GEN, "Creating the Gold
  Standard Dataset"]
- "Date of event" took the value of the last day of each month; "year of event" is always 2021.
  [GEN, "Data Structure and Features"]
- Many records have missing values for some variables. [GEN, "Data Structure and Features"]
- Excluded variables are present as columns populated with "N/A" (null) to convey the confidential
  data's structure. Full excluded list: geographic area, date of birth (replaced with age), date of
  death, gender identity, sexual orientation, legal sex, employment status, living situation, veteran
  status. [UG, "Excluded Variables"]
- Geographic area is excluded specifically because many municipalities had very few individuals
  (would require suppression) and would be hard to replicate without sacrificing the prioritized
  service-relationship quality. Users wanting geography are directed to the published aggregate
  statistics or a confidential-data request. [UG, "Excluded Variables"]
- Date of birth and date of death are omitted for privacy; a synthetic age variable stands in for age
  in 2021. [UG, "Excluded Variables"]

## Why the dataset exists / access context

- DHS's public WPRDC data is aggregated to municipality level, and counts under 6 individuals are
  suppressed. [GEN, "Current Data Access Options and Limitations"]
- Aggregated public data cannot capture interactions between services or the repeated nature of
  service use; e.g., a municipality total cannot distinguish many residents each receiving one
  service from a few residents receiving many. [GEN; UG]
- Stated use cases: explore interactions between services, trends over time, and demographics by
  service; understand data structure to make confidential-data requests specific; train/debug
  analysis code before confidential access is granted. [UG; GEN]
- DHS collects this administrative data for care coordination, case management, and quality
  improvement. [GEN, "Allegheny County Human Services Data"]

## Institutional frame

- The Data Warehouse links data stored separately per service by a common ID per individual, to
  support a whole-person view across programs. [GEN; DW]
- QuickCount is a public tool that shows client counts for services and the overlap between two
  services (e.g., mental health clients vs. child-welfare-associated parents, and their overlap).
  [DW]
- DHS's data-sharing agreements authorize action research: producing analysis and creating,
  implementing, and evaluating strategies developed from it. [DW]

---

## Enumerated demographic deviation tables (>20% difference from confidential data) [UG, Tables 1–3]

These are the SPECIFIC service×demographic combinations the User Guide flags as exceeding a 20%
difference. Before featuring any demographic breakdown on these exact service+group cells, treat the
number as unreliable. The User Guide notes these "primarily affected services with a small sample
size, making the differences more pronounced when represented as a percentage."

GENDER (Table 1):
- Overdoses — Male underrepresented ≥20%; Female overrepresented ≥20%
- Suicides — Male underrepresented ≥20%; Female overrepresented ≥20%

RACE (Table 2):
- Children Attending Early Childhood Programs Managed by DHS — White over ≥20%; Black/African American under ≥20%
- Children Receiving Early Intervention Services — Unknown under ≥20%
- Individuals Receiving Family Strengthening Programs — White over ≥20%; Black/African American under ≥20%

ETHNICITY (Table 3):
- Children Attending Early Childhood Programs Managed by DHS — Not Hispanic/Latinx under ≥60%
- Children Receiving DHS Funded Out of School Programs — Unknown over ≥40%
- Children Receiving Early Intervention Services — Not Hispanic/Latinx over ≥20%; Unknown under ≥30%
- Homicides — Not Hispanic/Latinx under ≥20%; Unknown over ≥20%
- Overdoses — Not Hispanic/Latinx under ≥20%; Unknown over ≥20%
- Suicides — Not Hispanic/Latinx under ≥40%; Unknown over ≥50%

Exact deviation magnitudes are not published (privacy). [UG, Tables 1–3 notes]

## Additional cited specifics that can influence analysis

- Three-way demographic frequencies (gender×race×ethnicity) are overall very similar between
  synthetic and confidential, but Black non-Hispanic residents (male or female) are slightly
  UNDERrepresented and White non-Hispanic slightly OVERrepresented. [GEN, Figure 3 discussion]
- Worked pair-fidelity examples: mental health services + income supports co-occur for ~10% of
  individuals in the confidential data, with only ~2% absolute difference in the synthetic data
  (common pair = high fidelity). Parents receiving BOTH child welfare and family strengthening
  co-occur for <0.1% of individuals, with ~35% absolute difference (rare pair = low fidelity).
  [GEN, "Summary of multiservice recipients"]
- Definitions of the two count concepts: a SERVICE-MONTH is one month in which one service was
  received (one service for 12 months + a different service for 8 months = 20 service-months). A
  DISTINCT SERVICE count is how many different services a person received for any number of months
  (the same example = 2 distinct services). [GEN, "Individual-level service counts"]
- Monthly trend SHAPES are generally preserved even for less common services (e.g., a July drop in
  early childhood programs appears in both confidential and synthetic). [GEN]
- "date of event" was set to the last day of each month; the county records service use as a monthly
  binary (received at least once that month), NOT a count of visits within the month. [GEN, "Data
  Structure and Features"; UG, "About the Data"]  → a service-month count measures DURATION (months
  present), not intensity (visits).
- The synthetic ID can tie repeat service usage to one synthetic individual but has NO association
  with the confidential ID. [UG, "About the Data"]
- A published data dictionary accompanies the dataset with exact variable names and the eligibility
  criteria for each service; consult it for service definitions. [UG, "About the Data"]  (Note: the
  data dictionary is a separate file, not among the four analyzed PDFs.)
- Postprocessing reshaped the Stage-Two output back to the service-month (one row per person-service-
  month) format of the gold standard dataset. [GEN, "Postprocessing"]
- DHS Data Warehouse source-system eligibility definitions that clarify category scope, e.g.:
  Intellectual Disability services are for individuals OVER age 18 [DW, Appendix #15]; Older
  Adults / Aging services are for individuals age 60 and above [DW, Appendix #1]; Child Welfare
  covers youth 18 or younger and their families [DW, Appendix #7]; the incident/autopsy source
  covers Medical Examiner cases of homicide, suicide, overdose and other sudden deaths [DW,
  Appendix #18]. (These are 2018 warehouse-source definitions; use as context for interpreting
  category scope, not as synthetic-file guarantees.)
