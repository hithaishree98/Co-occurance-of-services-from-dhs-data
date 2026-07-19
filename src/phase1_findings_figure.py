"""
Phase 1 -- single presentation figure for the four approved findings.

Reads outputs/findings_for_tableau.csv and outputs/sizes_for_tableau.csv (the extracts are
the single source -- nothing is hardcoded here; titles and big numbers are formatted from the
CSV values) and renders a 2x2 figure:

  Panel 1  CHANNEL (F3)      big-number treatment, no bars
  Panel 2  COORDINATION (F1) paired horizontal bars, both directions, rate vs baseline
  Panel 3  COORDINATION (F2) same treatment
  Panel 4  QUESTION (F4)     one bar pair + inline caveat (italic)

Styled consistently with phase1_heatmaps.py (Agg backend, plain matplotlib, same title
sizes). Saves outputs/findings_figure.png at dpi=150.

Run from repo root:  python src/phase1_findings_figure.py
"""
import numpy as np
import pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

f = pd.read_csv("outputs/findings_for_tableau.csv")
sizes = pd.read_csv("outputs/sizes_for_tableau.csv").set_index('service_label')

# invariant: rate / baseline must reproduce lift (same check as the export script)
assert np.allclose(f['rate'] / f['baseline_rate'], f['lift'], rtol=1e-6), \
    "rate/baseline does not reproduce lift -> stale or inconsistent extract"

RATE_COLOR = '#d73027'      # solid -- observed rate (YlOrRd family, matches heatmap palette)
BASE_COLOR = '#fdae61'      # lighter -- base rate, hatched
TEXT = '#333333'

def x_of(fid, label_contains):
    """Row of finding `fid` whose direction_label contains the phrase."""
    rows = f[(f['finding_id'] == fid) & f['direction_label'].str.contains(label_contains)]
    if len(rows) != 1:
        raise ValueError(f"expected exactly 1 row for {fid} / {label_contains!r}, got {len(rows)}")
    return rows.iloc[0]

def fmt_lift(lift):
    return f"~{lift:.0f}×" if lift >= 3 else f"{lift:.1f}×"

def paired_bars(ax, rows, title, legend_loc='lower right'):
    """Horizontal rate-vs-baseline pairs, one pair per direction row."""
    ypos, labels = [], []
    for i, (_, r) in enumerate(rows.iterrows()):
        base = i * 2.4
        ax.barh(base + 0.45, r['rate'] * 100, height=0.75, color=RATE_COLOR,
                label='observed' if i == 0 else None)
        ax.barh(base - 0.45, r['baseline_rate'] * 100, height=0.75, color=BASE_COLOR,
                hatch='///', edgecolor='white', label='base rate' if i == 0 else None)
        ax.text(r['rate'] * 100 + 0.6, base + 0.45, f"{r['rate']*100:.1f}%",
                va='center', fontsize=9, color=TEXT)
        ax.text(r['baseline_rate'] * 100 + 0.6, base - 0.45, f"{r['baseline_rate']*100:.1f}%",
                va='center', fontsize=9, color='#777777')
        ypos.append(base); labels.append(r['direction_label'].replace(' % also in ', '\n% also in '))
    # headroom so the value label on the longest bar never clips at the axis edge
    ax.set_xlim(0, max(rows['rate'].max(), rows['baseline_rate'].max()) * 100 * 1.14)
    ax.set_yticks(ypos); ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('% of clients', fontsize=9)
    ax.set_title(title, fontsize=11, pad=10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(fontsize=8, loc=legend_loc, frameon=False)
    ax.invert_yaxis()

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
ax1, ax2, ax3, ax4 = axes.flat

# ---- Panel 1: CHANNEL (F3), big number, no bars -------------------------------------------
r3 = x_of('F3', 'of Intellectual Disability clients')
id_pop = int(sizes.loc['Intellectual Disability', 'population_size'])
ax1.axis('off')
ax1.text(0.5, 0.93, 'CHANNEL', ha='center', fontsize=12, fontweight='bold', color=RATE_COLOR,
         transform=ax1.transAxes)
ax1.text(0.5, 0.52, f"{r3['rate']*100:.1f}%", ha='center', va='center', fontsize=72,
         fontweight='bold', color=TEXT, transform=ax1.transAxes)
ax1.text(0.5, 0.24, f"of Intellectual Disability service clients\n"
                    f"({int(r3['shared']):,} of {id_pop:,}) are enrolled in Income Supports",
         ha='center', fontsize=12, color=TEXT, transform=ax1.transAxes)
ax1.text(0.5, 0.07, f"Coverage, not association — base rate "
                    f"{r3['baseline_rate']*100:.1f}%",
         ha='center', fontsize=10, style='italic', color='#666666', transform=ax1.transAxes)

# ---- Panels 2-3: COORDINATION (F1, F2), paired bars both directions -----------------------
f1 = f[f['finding_id'] == 'F1']
# upper-right legend: the bottom direction's 41% bar spans the lower right of this panel
paired_bars(ax2, f1, f"COORDINATION — {int(f1.iloc[0]['shared']):,} shared clients "
                     f"— {fmt_lift(f1.iloc[0]['lift'])} base rate", legend_loc='upper right')
f2 = f[f['finding_id'] == 'F2']
paired_bars(ax3, f2, f"COORDINATION — {int(f2.iloc[0]['shared']):,} shared "
                     f"— {fmt_lift(f2.iloc[0]['lift'])} base rate")

# ---- Panel 4: QUESTION (F4), one bar pair + caveat ----------------------------------------
r4 = x_of('F4', 'of Older Adults Services clients')
paired_bars(ax4, r4.to_frame().T,
            "QUESTION — Older-adult service clients are markedly\n"
            "under-connected to county income supports")
# caveat sits below the axis, clear of both bars; bbox_inches='tight' keeps it in frame
ax4.text(0.5, -0.30, "Direction only — population documented as undercounted [UG]; "
                     "plausible federal benefit substitution;\n"
                     "flagged for confidential-data follow-up.",
         ha='center', fontsize=9, style='italic', color='#666666', transform=ax4.transAxes)

fig.suptitle("Reaching Allegheny's High-Need Clients: Channels, Overlaps, and a Gap Question "
             "— 2021 Synthetic Services Data", fontsize=15, y=0.985)
fig.text(0.5, 0.945, 'Public synthetic release · annual co-occurrence · '
                     'descriptive only', ha='center', fontsize=10, color='#666666')

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig("outputs/findings_figure.png", dpi=150, bbox_inches='tight')
print("Saved outputs/findings_figure.png")
