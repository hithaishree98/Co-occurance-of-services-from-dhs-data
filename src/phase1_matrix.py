"""
Phase 1 -- Co-occurrence analysis: conditional %, lift, ranked pairs.
Run from repo root after the Phase 0 notebook:  python src/phase1_matrix.py

Method notes (decisions carried from Phase 0 first-look):
- The dominant service's prevalence inflates naive conditional co-occurrence,
  so lift = P(B|A)/P(B) is computed alongside conditional %.
- A minimum-support threshold is applied before reporting any pair, in the
  spirit of the county's own small-cell suppression practice. It lives in
  src/config.py (MIN_SUPPORT, provisional) and is shared with the heatmaps.
  The floor gates outputs/pairs_ranked.csv only; the matrix CSVs are written
  unmasked and marked internal.
- Assertions below are MATHEMATICAL INVARIANTS only (definitions that cannot
  fail unless the code is wrong). Empirical results are printed as
  observations for interpretation, never pre-asserted.
- Gate A (structural vs informative) is PROPOSED here, never decided:
  outputs/pairs_gateA_candidates.csv carries proposed_class / reason / source.
  Classes are VERIFIED_NESTING, FAILED_NESTING_ROLE_PARTITION and REVIEW, from
  the analyst's verification of the six [UG]-indented pairs; INFORMATIVE is
  never proposed. No *_approved file is written -- that is the analyst's output,
  and is what downstream steps must read.
"""
import json, os
import pandas as pd, numpy as np
from config import MIN_SUPPORT

pl = pd.read_parquet("data/person_level.parquet")

# Service columns come from the explicit list Phase 0 wrote, not from excluding a
# hardcoded set of demographic names. Exclusion silently promotes any newly added
# column (e.g. living arrangement, if M8 resolves in favour of using it) into the
# co-occurrence matrix as though it were a service.
with open("data/service_columns.json") as f:
    svc = json.load(f)

missing = [c for c in svc if c not in pl.columns]
if missing:
    raise ValueError(
        "data/service_columns.json lists services absent from data/person_level.parquet:\n  "
        + "\n  ".join(missing)
        + "\n\nThe two artifacts have drifted -- re-run the Phase 0 pivot cell, which writes both.")

known_non_svc = {'person_id', 'age', 'gender', 'race', 'ethnicity', 'marital_status',
                 'education_level', 'total_service_months', 'distinct_services'}
unrecognized = [c for c in pl.columns if c not in svc and c not in known_non_svc]
if unrecognized:
    print(f"NOTE: parquet carries {len(unrecognized)} column(s) that are neither a listed service "
          f"nor a known demographic; they are excluded from the matrix: {unrecognized}")

B = (pl[svc] > 0).astype(np.int64)   # int64: small dtypes silently overflow on ~500k-row sums
N = len(B)

M = B.T.values @ B.values            # shared-person counts per service pair
sizes = np.diag(M).astype(float)
cond = M / sizes[:, None]            # P(col | row)
lift = cond / (sizes / N)[None, :]   # P(col|row) / P(col)

# invariants: probabilities live in [0,1]; a service co-occurs with itself fully
assert (cond >= -1e-9).all() and (cond <= 1 + 1e-9).all(), "probability outside [0,1] -> code bug"
assert (np.diag(cond) > 0.999).all(), "diagonal of conditional matrix must be 1 -> code bug"
print("Invariant checks passed.")

# containment_pct = shared / min(size_A, size_B): the share of the SMALLER service's
# population that also appears in the larger one. 1.0 means the smaller is a subset of the
# larger, which is what a genuine nesting relationship has to show.
rows = [(svc[i], svc[j], M[i,j], cond[i,j], cond[j,i], lift[i,j],
         M[i,j] / min(sizes[i], sizes[j]))
        for i in range(len(svc)) for j in range(len(svc))
        if i < j and M[i,j] >= MIN_SUPPORT]
pairs = (pd.DataFrame(rows, columns=['A','B','shared','P(B|A)','P(A|B)','lift',
                                     'containment_pct'])
           .sort_values('lift', ascending=False))

# Rare-pair fidelity tier -- input to the deferred M6 decision (findings_log, 2026-07-18).
# Documented: pairs received by <0.5% of individuals carry ~34.4% median absolute percent
# difference vs ~5.2% for pairs at/above 0.5% [GEN, "Summary of multiservice recipients"].
# Computed before the observations below so the strongest pair can carry its tier status
# inline -- ranking is by lift, which favours rare pairs, so the headline pair is exactly the
# one most likely to sit in the low-fidelity tier. The caveat must not be readable apart
# from the claim.
tier_cutoff = 0.005 * N

total_possible = len(svc)*(len(svc)-1)//2
print(f"\nObservations:")
print(f"  {len(pairs)} of {total_possible} possible pairs meet the {MIN_SUPPORT}-person support threshold;")
print(f"  the remainder are unreportable small cells.")
if pairs.empty:
    print(f"  No pair meets the {MIN_SUPPORT}-person floor. That is an observation about the data,")
    print(f"  not an error -- record it and reconsider the floor before going further.")
else:
    top = pairs.iloc[0]
    tier_note = ("BELOW the 0.5% fidelity tier -- high synthesis error, ~34.4% median [GEN]"
                 if top['shared'] < tier_cutoff else
                 "at/above the 0.5% fidelity tier -- ~5.2% median error [GEN]")
    print(f"  Strongest association: {top['A']} <-> {top['B']} "
          f"(lift={top['lift']:.1f}, shared={top['shared']:,} -- {tier_note}).")
    print("  Interpretation deferred: see the Gate A classification below. Note the [UG] indented")
    print("  outline does NOT by itself imply containment -- four of its six pairs failed")
    print("  verification (findings_log, 2026-07-19).")

# M6 DECIDED (findings_log, 2026-07-19): the rare-pair caution flag is adopted. The tier is
# carried as a below_fidelity_tier column on pairs_ranked.csv and the Gate A file so the
# ~34.4%-error tier cannot be read as equally reliable as the ~5.2% tier.
pairs['below_fidelity_tier'] = pairs['shared'] < tier_cutoff
below_tier = pairs['below_fidelity_tier'].sum()
print(f"  {below_tier} of {len(pairs)} reportable pairs fall below the 0.5%-of-individuals")
print(f"  fidelity threshold (<{tier_cutoff:,.0f} shared persons of N={N:,}). Documented error for")
print(f"  that tier is ~34.4% median vs ~5.2% at/above [GEN]. M6 DECIDED: flag adopted, carried")
print(f"  as the below_fidelity_tier column on both output files.")

os.makedirs("outputs", exist_ok=True)

# ---------------------------------------------------------------------------
# Gate A candidates -- structural vs informative pair classification.
#
# PROPOSE ONLY, and record only what the analyst has settled. The six [UG]-indented nesting
# pairs below, their verification outcomes, and the explanation for the four failures are
# ANALYST-VERIFIED against the source documents and the QuickCount program definitions
# [QC-Programs definitions, reviewed 2026-07-19]. This script RECORDS those outcomes; it
# does not re-derive, re-test, or second-guess them.
#
#   VERIFIED_NESTING               [UG]-indented AND measured ~100% containment. Accepted
#                                  as structural nesting.
#   FAILED_NESTING_ROLE_PARTITION  [UG]-indented but containment near-zero/partial. The QC
#                                  definitions establish a role/sibling partition, not a
#                                  subset. NOT accepted as nesting.
#   REVIEW                         everything else. A pair not in the [UG] list that
#                                  nonetheless behaves as containment carries a note.
#   INFORMATIVE                    never proposed.
# No *_approved file is written -- that is the analyst's output after classification, and is
# what downstream steps must read.
# ---------------------------------------------------------------------------
CONTAINMENT_NOTE_THRESHOLD = 0.95

# (child, parent, verification_outcome) -- the six indented pairs in [UG, "About the Data"],
# each carrying the analyst's verification outcome from the containment measurements.
NESTING = [
    ('Children_Receiving_Child_Welfare_Services',
     'Families_Receiving_Child_Welfare_Services', 'FAILED'),
    ('Parents_Receiving_Child_Welfare_Services',
     'Families_Receiving_Child_Welfare_Services', 'FAILED'),
    ('Children_in_Care',
     'Families_Receiving_Child_Welfare_Services', 'FAILED'),
    ('Children_Receiving_Early_Intervention_Services',
     'Children_Attending_Early_Childhood_Programs_Managed_by_DHS', 'FAILED'),
    ('Homeless_Population',
     'Individuals_Receiving_Homelessness_and_Housing_Services', 'VERIFIED'),
    ('Mental_Health_Crises',
     'Individuals_Receiving_Mental_Health_Services', 'VERIFIED'),
]

# HARD RAISE: NESTING is hand-transcribed from document prose into data literals. If a name
# does not exist in the data, the pair silently never matches and every listed pair is
# mislabelled REVIEW -- a vacuous pass, the same failure mode Check 5 guards against.
named = {s for t in NESTING for s in t[:2]}
unknown = sorted(named - set(svc))
if unknown:
    raise ValueError(
        "Gate A nesting map names services that do not exist in data/service_columns.json:\n  "
        + "\n  ".join(unknown)
        + "\n\nRe-transcribe the indented service list from [UG, 'About the Data'] against the "
          "actual data values before trusting any structural classification.")

VERIFIED_SRC = ('[UG, "About the Data"] indented list + measured containment; analyst-verified '
                'against the source documents')
FAILED_SRC = ('[UG, "About the Data"] indented list + [QC-Programs definitions, reviewed '
              '2026-07-19]; analyst-verified')
ROLE_PARTITION = (
    'The child-welfare categories partition by ROLE, not nesting: "Children Associated with a '
    'Child Welfare Case" are children/youth under 18 with an open case, and "Parents Associated '
    'with a Child Welfare Case" are the parents of such children -- different people by '
    'definition, so near-zero overlap is expected category behaviour, not an error. Early '
    'Intervention is a separate referral pipeline (AFIT), a sibling program to the '
    'early-childhood cluster, not a subset.')

outcome_of = {frozenset((c, p)): (c, p, o) for c, p, o in NESTING}
idx = {s: i for i, s in enumerate(svc)}

def gate_a(a, b, containment):
    """-> (proposed_class, reason, source). Never returns INFORMATIVE.

    For the six listed pairs the reason quotes CHILD-IN-PARENT containment
    (shared / size of the child category), which is the measure the nesting claim is
    actually about and the one the analyst verified against. The containment_pct COLUMN
    stays min-size (shared / min(size_A, size_B)) for every pair, since a general pair
    has no child and no parent. The two agree wherever the child is the smaller service;
    they diverge for Parents_CW -> Families_CW, where the child category is the larger.
    """
    key = frozenset((a, b))
    if key in outcome_of:
        child, parent, outcome = outcome_of[key]
        cip = M[idx[child], idx[parent]] / sizes[idx[child]]
        if outcome == 'VERIFIED':
            return ('VERIFIED_NESTING',
                    f'{child} is listed as a sub-category of {parent} in the [UG] indented list, '
                    f'and measured containment is ~100% ({cip:.1%} of the child category is in '
                    f'the parent) -- verified as structural nesting',
                    VERIFIED_SRC)
        return ('FAILED_NESTING_ROLE_PARTITION',
                f'{child} is listed as a sub-category of {parent} in the [UG] indented list, but '
                f'only {cip:.1%} of the child category is in the parent -- failed verification, '
                f'not accepted as nesting. ' + ROLE_PARTITION,
                FAILED_SRC)
    if containment >= CONTAINMENT_NOTE_THRESHOLD:
        return ('REVIEW',
                f'behaves as containment ({containment:.1%} of the smaller service population) '
                f'but is not in the [UG] indented list -- analyst judgment required',
                'none -- not a listed nesting pair; the note rests on measured containment only')
    return ('REVIEW',
            'no documented nesting relationship in documented_facts.md -- analyst '
            'classification required',
            'none -- classification rests on the absence of a documented nesting relationship')

# Built via concat rather than multi-column assignment: the latter raises on an empty
# frame (no pair meets the floor), which is a legitimate observation, not an error.
labels = pd.DataFrame(
    [gate_a(a, b, c) for a, b, c in zip(pairs['A'], pairs['B'], pairs['containment_pct'])],
    columns=['proposed_class', 'reason', 'source'], index=pairs.index)
gate = pd.concat([pairs, labels], axis=1)
gate.to_csv("outputs/pairs_gateA_candidates.csv", index=False)

counts = gate['proposed_class'].value_counts()
print(f"\nGate A candidates (proposed only -- INFORMATIVE is never proposed):")
for cls in ['VERIFIED_NESTING', 'FAILED_NESTING_ROLE_PARTITION', 'REVIEW']:
    print(f"  {cls:31s} {int(counts.get(cls, 0)):>4}")

review = gate[gate['proposed_class'] == 'REVIEW']
n_rev_at_tier = int((~review['below_fidelity_tier']).sum())
n_contain = int(review['reason'].str.startswith('behaves as containment').sum())
print(f"  Of {len(review)} REVIEW pairs, {n_rev_at_tier} sit AT/ABOVE the 0.5% fidelity tier")
print(f"  (>= {tier_cutoff:,.0f} shared persons); {len(review) - n_rev_at_tier} are below it.")
print(f"  {n_contain} REVIEW pair(s) behave as containment (>= {CONTAINMENT_NOTE_THRESHOLD:.0%}) "
      f"without appearing in the [UG] list.")

# The candidates file is built from `pairs`, which the support floor has already gated. A
# listed nesting pair below the floor is therefore absent from the file altogether rather than
# classified -- which would quietly understate the class counts above.
below_floor_nesting = [(c, p, o, M[idx[c], idx[p]]) for c, p, o in NESTING
                       if M[idx[c], idx[p]] < MIN_SUPPORT]
if below_floor_nesting:
    print(f"  NOTE: {len(below_floor_nesting)} of {len(NESTING)} [UG]-indented pairs do NOT clear "
          f"the {MIN_SUPPORT}-person floor and are absent from the candidates file:")
    for c, p, o, n in below_floor_nesting:
        print(f"    {c} <-> {p} (shared={n:,}, verification: {o})")
else:
    print(f"  All {len(NESTING)} [UG]-indented pairs clear the {MIN_SUPPORT}-person floor.")
print(f"  Wrote outputs/pairs_gateA_candidates.csv. No *_approved file written -- that is your output.")

HDR = ("# INTERNAL / INTERMEDIATE -- full unmasked matrix, no min-support floor applied.\n"
       "# The floor (config.MIN_SUPPORT) applies only to outputs/pairs_ranked.csv and the\n"
       "# heatmaps. Do not publish or quote cells from this file directly.\n")

def save_matrix(df, path):
    # Write via a handle: to_csv(path) would truncate the header we just wrote.
    with open(path, "w", newline="") as f:
        f.write(HDR)
        df.to_csv(f)

save_matrix(pd.DataFrame(cond, index=svc, columns=svc), "outputs/matrix_conditional.csv")
save_matrix(pd.DataFrame(lift, index=svc, columns=svc), "outputs/matrix_lift.csv")
save_matrix(pd.DataFrame(M,    index=svc, columns=svc), "outputs/matrix_shared.csv")
pairs.to_csv("outputs/pairs_ranked.csv", index=False)
print("\nSaved matrices (internal, unmasked) and outputs/pairs_ranked.csv (floor applied)")
