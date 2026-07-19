"""
Phase 1 -- tidy Tableau exports for the four approved INFORMATIVE findings.

Reads outputs/pairs_gateA_approved.csv (analyst classifications; the four INFORMATIVE rows
are the project's findings set per the Gate A DECIDES entry, findings_log 2026-07-19) and
outputs/matrix_shared.csv (diagonal = service population sizes). Writes:

  outputs/findings_for_tableau.csv  -- one row per finding per direction (8 rows)
  outputs/sizes_for_tableau.csv     -- the six involved services and their sizes

Mechanism and caveat text are the ANALYST'S labels (dictated 2026-07-19), transcribed:
  Coordination -> the two association findings (MH<->SUD, HH<->MH)
  Channel      -> the coverage finding (Income<->ID)
  Question     -> the negative association (Income<->Older_Adults)
No interpretation is added here; this is a tidy-data reshape.

Run from repo root:  python src/phase1_tableau_export.py
"""
import numpy as np
import pandas as pd

N = 533_799   # person denominator [OBSERVED: phase0_first_look.ipynb, 2026-07-18]

approved = pd.read_csv("outputs/pairs_gateA_approved.csv")
shared_m = pd.read_csv("outputs/matrix_shared.csv", index_col=0, comment='#')
sizes = pd.Series(np.diag(shared_m.values), index=shared_m.index)

SHORT = {
    'Individuals_Receiving_Mental_Health_Services':          'Mental Health',
    'Individuals_Receiving_Substance_Use_Disorder_Services': 'SUD',
    'Individuals_Receiving_Homelessness_and_Housing_Services': 'Homelessness & Housing',
    'Individuals_Receiving_Income_Supports':                 'Income Supports',
    'Individuals_Receiving_Intellectual_Disability_Services': 'Intellectual Disability',
    'Older_Adults_Receiving_Services':                       'Older Adults Services',
}

TIER_CAVEAT = ('at/above the 0.5% fidelity tier (~5.2% median error) [GEN]; annual '
               'co-occurrence only; not causal/directional')
OA_CAVEAT = ('population documented as undercounted [UG]; magnitude not load-bearing; '
             'plausible federal benefit substitution')

# (finding_id, A, B, mechanism, claim_type, caveat) -- analyst-approved set, lift-descending
# order as in the Gate A findings_log entry.
FINDINGS = [
    ('F1', 'Individuals_Receiving_Mental_Health_Services',
           'Individuals_Receiving_Substance_Use_Disorder_Services',
           'Coordination', 'association', TIER_CAVEAT),
    ('F2', 'Individuals_Receiving_Homelessness_and_Housing_Services',
           'Individuals_Receiving_Mental_Health_Services',
           'Coordination', 'association', TIER_CAVEAT),
    ('F3', 'Individuals_Receiving_Income_Supports',
           'Individuals_Receiving_Intellectual_Disability_Services',
           'Channel', 'coverage', TIER_CAVEAT),
    ('F4', 'Individuals_Receiving_Income_Supports',
           'Older_Adults_Receiving_Services',
           'Question', 'negative', OA_CAVEAT),
]

# HARD RAISE: the findings list is hand-transcribed from the approved file. If it drifts
# from the INFORMATIVE rows there, the export would misstate the approved findings set.
inf_rows = approved[approved['final_class'].str.startswith('INFORMATIVE')]
approved_pairs = {frozenset((a, b)) for a, b in zip(inf_rows['A'], inf_rows['B'])}
listed_pairs = {frozenset((a, b)) for _, a, b, *_ in FINDINGS}
if approved_pairs != listed_pairs:
    raise ValueError(
        "FINDINGS does not match the INFORMATIVE rows of pairs_gateA_approved.csv -- "
        f"approved-only: {approved_pairs - listed_pairs}; listed-only: {listed_pairs - approved_pairs}")

rows = []
for fid, a, b, mech, ctype, caveat in FINDINGS:
    row = approved[((approved['A'] == a) & (approved['B'] == b)) |
                   ((approved['A'] == b) & (approved['B'] == a))].iloc[0]
    shared, lift = int(row['shared']), float(row['lift'])
    for src, tgt in [(a, b), (b, a)]:
        rows.append({
            'finding_id': fid,
            'mechanism': mech,
            'pair_label': f"{SHORT[a]} <-> {SHORT[b]}",
            'direction_label': f"of {SHORT[src]} clients, % also in {SHORT[tgt]}",
            'rate': shared / sizes[src],
            'baseline_rate': sizes[tgt] / N,
            'lift': lift,
            'shared': shared,
            'claim_type': ctype,
            'caveat': caveat,
        })

out = pd.DataFrame(rows)
# invariant: rate / baseline must reproduce the matrix lift in both directions
assert np.allclose(out['rate'] / out['baseline_rate'], out['lift'], rtol=1e-6), \
    "rate/baseline does not reproduce lift -> code bug"
out.to_csv("outputs/findings_for_tableau.csv", index=False)

svc_involved = sorted({s for _, a, b, *_ in FINDINGS for s in (a, b)})
pd.DataFrame({
    'service': svc_involved,
    'service_label': [SHORT[s] for s in svc_involved],
    'population_size': [int(sizes[s]) for s in svc_involved],
    'share_of_persons': [sizes[s] / N for s in svc_involved],
}).to_csv("outputs/sizes_for_tableau.csv", index=False)

print("Wrote outputs/findings_for_tableau.csv:")
with pd.option_context('display.width', 250, 'display.max_colwidth', 46):
    print(out.drop(columns='caveat').to_string(index=False))
print("\nWrote outputs/sizes_for_tableau.csv:")
print(pd.read_csv("outputs/sizes_for_tableau.csv").to_string(index=False))
