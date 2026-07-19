"""
Phase 1b -- side-by-side heatmaps (conditional %, log-lift) with support mask.
Run from repo root:  python src/phase1_heatmaps.py
"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import MIN_SUPPORT

# comment='#' skips the INTERNAL/INTERMEDIATE header phase1_matrix.py writes on these.
cond = pd.read_csv("outputs/matrix_conditional.csv", index_col=0, comment='#')
lift = pd.read_csv("outputs/matrix_lift.csv", index_col=0, comment='#')
shared = pd.read_csv("outputs/matrix_shared.csv", index_col=0, comment='#')
# Explicit labels for the child-welfare / child-program cluster. The general rule below
# turned Children_Receiving_Child_Welfare_Services into "Child Child Welfare Services";
# these also keep the four child-welfare categories visibly parallel, which matters because
# they partition by role rather than nest (findings_log, 2026-07-19).
OVERRIDES = {
    'Families_Receiving_Child_Welfare_Services':      'Child Welfare: Families',
    'Children_Receiving_Child_Welfare_Services':      'Child Welfare: Children',
    'Parents_Receiving_Child_Welfare_Services':       'Child Welfare: Parents',
    'Children_in_Care':                               'Child Welfare: Children in Care',
    'Children_Receiving_Early_Intervention_Services': 'Early Intervention (children)',
    'Children_Receiving_DHS_Funded_Out_of_School_Programs': 'Out-of-School Programs (children)',
}
short = {c: OVERRIDES.get(
             c, c.replace('Individuals_Receiving_','').replace('Children_Receiving_','Child ')
                 .replace('_',' '))
         for c in cond.columns}
# Duplicate labels would silently misalign the .loc reindex below, not error out.
if len(set(short.values())) != len(short):
    dupes = sorted({v for v in short.values() if list(short.values()).count(v) > 1})
    raise ValueError(f"Short service labels collide: {dupes}. Fix OVERRIDES before plotting.")
for df in (cond, lift, shared): df.rename(index=short, columns=short, inplace=True)
order = shared.sum(axis=1).sort_values(ascending=False).index
cond, lift, shared = cond.loc[order,order], lift.loc[order,order], shared.loc[order,order]
mask = (shared < MIN_SUPPORT) | np.eye(len(cond), dtype=bool)

fig, axes = plt.subplots(1, 2, figsize=(26, 11))
for ax, mat, title, cmap, vmin, vmax in [
    (axes[0], cond*100, "Of ROW population, % also using COLUMN service", 'YlOrRd', 0, 100),
    (axes[1], np.log10(lift.clip(lower=0.1)), "log10(lift): 0=independent, +=enriched", 'RdBu_r', -1.2, 2)]:
    im = ax.imshow(mat.mask(mask).values, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(mat))); ax.set_xticklabels(mat.columns, rotation=90, fontsize=8)
    ax.set_yticks(range(len(mat))); ax.set_yticklabels(mat.index, fontsize=8)
    ax.set_title(title, fontsize=11, pad=12); plt.colorbar(im, ax=ax, shrink=0.7)
fig.suptitle("Cross-System Service Co-occurrence, ACDHS 2021 Synthetic Data "
             f"(grey = <{MIN_SUPPORT} shared or self-pair)")
plt.tight_layout(); plt.savefig("outputs/cooccurrence_heatmaps.png", dpi=130, bbox_inches='tight')
print("Saved outputs/cooccurrence_heatmaps.png")
