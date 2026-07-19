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

rows = [(svc[i], svc[j], M[i,j], cond[i,j], cond[j,i], lift[i,j])
        for i in range(len(svc)) for j in range(len(svc))
        if i < j and M[i,j] >= MIN_SUPPORT]
pairs = (pd.DataFrame(rows, columns=['A','B','shared','P(B|A)','P(A|B)','lift'])
           .sort_values('lift', ascending=False))

total_possible = len(svc)*(len(svc)-1)//2
print(f"\nObservations:")
print(f"  {len(pairs)} of {total_possible} possible pairs meet the {MIN_SUPPORT}-person support threshold;")
print(f"  the remainder are unreportable small cells.")
if pairs.empty:
    print(f"  No pair meets the {MIN_SUPPORT}-person floor. That is an observation about the data,")
    print(f"  not an error -- record it and reconsider the floor before going further.")
else:
    print(f"  Strongest association: {pairs.iloc[0]['A']} <-> {pairs.iloc[0]['B']} "
          f"(lift={pairs.iloc[0]['lift']:.1f}, shared={pairs.iloc[0]['shared']:,}).")
    print("  Interpretation deferred: strong pairs must first be classified as structural")
    print("  (definitional nesting per the User Guide's category outline) vs informative.")

# Rare-pair fidelity tier -- input to the deferred M6 decision (findings_log, 2026-07-18).
# Documented: pairs received by <0.5% of individuals carry ~34.4% median absolute percent
# difference vs ~5.2% for pairs at/above 0.5% [GEN, "Summary of multiservice recipients"].
# Count only. Whether to add a rare-pair caution flag is the analyst's call, not this script's.
tier_cutoff = 0.005 * N
below_tier = (pairs['shared'] < tier_cutoff).sum()
print(f"  {below_tier} of {len(pairs)} reportable pairs fall below the 0.5%-of-individuals")
print(f"  fidelity threshold (<{tier_cutoff:,.0f} shared persons of N={N:,}). Documented error for")
print(f"  that tier is ~34.4% median vs ~5.2% at/above [GEN]. No flag applied -- analyst decision.")

os.makedirs("outputs", exist_ok=True)

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
