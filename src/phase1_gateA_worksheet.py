"""
Phase 1 -- Gate A review worksheet.

Builds outputs/pairs_gateA_review_worksheet.csv from outputs/pairs_gateA_candidates.csv with
the analyst's PRE-APPLIED dispositions (dictated 2026-07-19) and the remaining at-tier REVIEW
pairs left blank for the analyst's classification. This is still not an *_approved file --
downstream reads only what the analyst saves after finishing the blank set.

Disposition rules, applied in order (first match wins):
  1. VERIFIED_NESTING pairs            -> STRUCTURAL
  2. FAILED_NESTING_ROLE_PARTITION     -> STRUCTURAL_BY_DEFINITION
  3. Children_CW <-> Children_in_Care  -> STRUCTURAL_BY_DEFINITION (QC Placement Services)
  4. DHS_Services pairs >=95% contain. -> STRUCTURAL_BY_RECORDING_SCOPE (INFERRED)
  5. below-tier REVIEW pairs           -> BELOW_TIER (blanket, not individually adjudicated)
  6. remaining at-tier REVIEW pairs    -> BLANK final_class / my_reason, for the analyst

Run from repo root:  python src/phase1_gateA_worksheet.py
"""
import pandas as pd

g = pd.read_csv("outputs/pairs_gateA_candidates.csv")

DHS = 'Individuals_Receiving_DHS_Services'
CW_CHILDREN = 'Children_Receiving_Child_Welfare_Services'
CIC = 'Children_in_Care'

g['final_class'] = ''
g['my_reason'] = ''
g['note'] = ''

def pair_is(row, x, y):
    return {row['A'], row['B']} == {x, y}

# 1. Verified nesting -> STRUCTURAL
m = g['proposed_class'] == 'VERIFIED_NESTING'
g.loc[m, 'final_class'] = 'STRUCTURAL'
g.loc[m, 'my_reason'] = 'documented nesting verified by containment; definitional, not a finding.'

# 2. Failed-nesting role partition -> STRUCTURAL_BY_DEFINITION
m = g['proposed_class'] == 'FAILED_NESTING_ROLE_PARTITION'
g.loc[m, 'final_class'] = 'STRUCTURAL_BY_DEFINITION'
g.loc[m, 'my_reason'] = 'role partition per [QC]; not a finding.'

# 3. Children_CW <-> Children_in_Care -> STRUCTURAL_BY_DEFINITION
m = g.apply(lambda r: pair_is(r, CW_CHILDREN, CIC), axis=1) & (g['final_class'] == '')
g.loc[m, 'final_class'] = 'STRUCTURAL_BY_DEFINITION'
g.loc[m, 'my_reason'] = ('Placement Services defined as subset of children-with-open-case [QC]; '
                         'below tier regardless.')

# 4. DHS_Services >=95%-containment pairs -> STRUCTURAL_BY_RECORDING_SCOPE (INFERRED)
m = (((g['A'] == DHS) | (g['B'] == DHS)) & (g['containment_pct'] >= 0.95)
     & (g['final_class'] == ''))
n_dhs = int(m.sum())
g.loc[m, 'final_class'] = 'STRUCTURAL_BY_RECORDING_SCOPE (INFERRED)'
g.loc[m, 'my_reason'] = ('DHS_Services measures as complete container for the MH cluster but not '
                         'income supports, consistent with direct-DHS-delivered recording scope; '
                         'analyst inference -- no [UG] arrow, no [QC] definition for this '
                         'category.')

# 5. Below-tier REVIEW pairs -> BELOW_TIER blanket
m = (g['final_class'] == '') & g['below_fidelity_tier']
g.loc[m, 'final_class'] = 'BELOW_TIER'
g.loc[m, 'my_reason'] = 'ineligible as findings per M6; not individually adjudicated.'

# 6. Remaining at-tier REVIEW pairs stay blank; note the flagged near-containment candidate
m = g.apply(lambda r: pair_is(r, 'Individuals_Receiving_Income_Supports',
                              'Individuals_Receiving_Intellectual_Disability_Services'), axis=1)
g.loc[m, 'note'] = ('candidate real-world near-containment: 96.1% of ID clients receive income '
                    'supports; above tier.')

blank = g[g['final_class'] == ''].sort_values('lift', ascending=False)

# Worksheet order: the analyst's blank set first (lift desc), then pre-applied dispositions,
# then the BELOW_TIER block.
order = ['', 'STRUCTURAL', 'STRUCTURAL_BY_DEFINITION',
         'STRUCTURAL_BY_RECORDING_SCOPE (INFERRED)', 'BELOW_TIER']
ws = pd.concat([g[g['final_class'] == c].sort_values('lift', ascending=False) for c in order])
ws.to_csv("outputs/pairs_gateA_review_worksheet.csv", index=False)

print("Worksheet: outputs/pairs_gateA_review_worksheet.csv "
      "(NOT an *_approved file; downstream still reads only *_approved)")
print("\nDisposition counts:")
vc = ws['final_class'].replace('', 'BLANK (analyst)').value_counts()
print(vc.to_string())
print(f"  Total rows: {len(ws)} (candidates file had {len(g)})")
if n_dhs != 3:
    print(f"  NOTE: DHS >=95%-containment rule matched {n_dhs} pairs.")

print(f"\nBLANK SET -- {len(blank)} at-tier REVIEW pairs for analyst classification "
      f"(lift descending):")
cols = ['A', 'B', 'shared', 'lift', 'P(B|A)', 'P(A|B)', 'containment_pct']
with pd.option_context('display.width', 220, 'display.max_rows', None):
    print(blank[cols].to_string(index=False))
for _, r in blank[blank['note'] != ''].iterrows():
    print(f"\n  NOTE on {r['A']} <-> {r['B']}: {r['note']}")
