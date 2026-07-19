"""
Targeted check -- the 29-person Children_CW / Parents_CW overlap (findings_log, 2026-07-19
nesting entry addendum).

The QC Parents clause predicts this overlap consists of under-18 biological parents of an
involved child, which makes a testable prediction: ages should skew young. This script prints
the raw values only. REPORT-ONLY: no assertions, no interpretation -- the reading is the
analyst's (CLAUDE.md: do not fill Interpretation; observations are interpreted in writing).

Run from repo root:  python src/phase1_check_cw_overlap.py
"""
import pandas as pd

A = 'Children_Receiving_Child_Welfare_Services'
B = 'Parents_Receiving_Child_Welfare_Services'

pl = pd.read_parquet("data/person_level.parquet")
both = pl[(pl[A] > 0) & (pl[B] > 0)]

# Cross-reference, stated not asserted: the co-occurrence matrix cell for this pair was 29.
print(f"Persons with counts > 0 in BOTH:\n  {A}\n  {B}")
print(f"Count: {len(both)}  (co-occurrence matrix cell: 29 -- "
      f"{'match' if len(both) == 29 else 'MISMATCH, investigate'})")
print()
print(f"Age: min={both['age'].min()}  median={both['age'].median()}  max={both['age'].max()}")
print(f"All ages (n={len(both)}): {sorted(both['age'].tolist())}")
print()
print("Gender breakdown:")
print(both['gender'].value_counts().to_string())
print()
print("Report-only. Interpretation is the analyst's -- see the findings_log addendum "
      "(2026-07-19). This 29-person cell is below the 30-person reporting floor and far below "
      "the 0.5% fidelity tier; it is examined as category-semantics evidence, not a finding.")
