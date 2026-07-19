"""
Phase 1 -- convert the analyst-filled Gate A worksheet into the approved file.

Reads outputs/pairs_gateA_review_worksheet.csv (filled by the ANALYST) and writes
outputs/pairs_gateA_approved.csv. This script performs NO classification: it validates and
transcribes. The classifications are the analyst's; final_class values are preserved verbatim
apart from stripping leading/trailing whitespace (mechanical cleanup only).

Validation (hard raise -- an approved file must not be written from a defective worksheet):
  - every row has a non-empty final_class
  - row count matches the candidates file (no pair dropped or invented)
  - the (A, B) pair set is identical to the candidates file

Run from repo root:  python src/phase1_gateA_approve.py
"""
import pandas as pd

ws = pd.read_csv("outputs/pairs_gateA_review_worksheet.csv")
cand = pd.read_csv("outputs/pairs_gateA_candidates.csv")

ws['final_class'] = ws['final_class'].fillna('').str.strip()

blank = ws[ws['final_class'] == '']
if len(blank):
    raise ValueError(
        f"{len(blank)} worksheet row(s) still have an empty final_class -- the worksheet is "
        f"not finished. First: {blank.iloc[0]['A']} <-> {blank.iloc[0]['B']}")

if len(ws) != len(cand):
    raise ValueError(f"Worksheet has {len(ws)} rows; candidates file has {len(cand)}. "
                     f"A pair was dropped or added -- do not approve.")
pairs_ws = {frozenset((a, b)) for a, b in zip(ws['A'], ws['B'])}
pairs_cand = {frozenset((a, b)) for a, b in zip(cand['A'], cand['B'])}
if pairs_ws != pairs_cand:
    raise ValueError("Worksheet pair set differs from the candidates file -- do not approve.")

ws.to_csv("outputs/pairs_gateA_approved.csv", index=False)
print("Wrote outputs/pairs_gateA_approved.csv (analyst classifications, transcribed verbatim)")

print("\nFinal counts by final_class:")
print(ws['final_class'].value_counts().to_string())

inf = ws[ws['final_class'].str.startswith('INFORMATIVE')].sort_values('lift', ascending=False)
print(f"\nINFORMATIVE pairs ({len(inf)}):")
cols = ['A', 'B', 'shared', 'lift', 'P(B|A)', 'P(A|B)', 'containment_pct',
        'below_fidelity_tier', 'final_class']
with pd.option_context('display.width', 250):
    print(inf[cols].to_string(index=False))
