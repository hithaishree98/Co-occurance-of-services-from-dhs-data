# DRAFT — analyst edits before any use. Not for circulation.

# Reaching High-Need Clients Through Existing Channels: Cross-System Service Overlap in the 2021 Integrated Services Data (Public Synthetic Release)

The 2021 public synthetic release of Allegheny County's Integrated Services data shows that
the county's highest-coverage benefit already reaches nearly all of one high-need population,
quantifies two service overlaps where coordinated case management is operating at scale, and
raises one question about a population that appears under-connected.

All figures describe the synthetic file (533,799 synthetic individuals; service receipt in
2021). Each reported overlap sits at or above the release's documented reliability threshold
(pairs received by ≥0.5% of individuals, ~5.2% median error) unless noted. Overlap means two
services touched the same person within the year — it carries no timing, no direction, and no
cause.

## CHANNEL — Income supports already reach the intellectual-disability service population

Of the 6,360 individuals receiving intellectual disability services, 6,111 — **96.1%** — also
received income supports in 2021. This is a coverage claim, not an association claim: income
supports reach 94.1% of everyone in the file, so ID clients are not disproportionately
enrolled; they are simply almost fully enrolled. The practical reading is infrastructural — an
existing enrollment relationship already connects nearly the entire ID service population to
the county, and that channel is available when new supports for this population need a
delivery path.

## COORDINATION — Two overlaps confirm, with numbers, what integrated care assumes

Where the county's behavioral-health and housing work already assumes overlapping populations,
the file quantifies the overlap:

- **Mental health and substance use disorder services:** 5,278 shared clients — individuals
  receiving SUD services appear in mental health services at about **4× chance** (41.2% of
  SUD clients, against a 10.4% base rate).
- **Homelessness/housing services and mental health services:** 5,004 shared clients, at
  **2.2× chance** (22.9% of housing-services clients, against the same 10.4% base rate).

Both figures are annual co-occurrence in a synthetic file: they support planning-scale
statements about caseload overlap, not client-level claims and not statements about which
service came first.

## QUESTION — Older adults appear markedly under-connected to county income supports

Individuals in older-adult services appear in county income supports at roughly **one-third
of chance** (31.7% of the 16,759 older-adult service population, against the 94.1% base
rate). Direction only, for two reasons stated with the claim: the release documentation
records the older-adult population as undercounted in the synthetic data, so the magnitude is
not load-bearing; and a benign explanation is plausible — older adults' income may flow
through federal programs (Social Security, SSI, Medicare) that this county-tracked category
does not capture. Whether the gap is a data artifact, federal substitution, or a genuine
enrollment shortfall is answerable only in the confidential data, and is flagged for that
follow-up.

---

Identifying eligible-but-unserved individuals requires confidential data; this analysis maps
reach and coordination for those already visible to the system.

*Source: public synthetic 2021 Integrated Services release (Urban Institute / ACDHS). Figures
from this project's approved co-occurrence analysis (outputs/pairs_gateA_approved.csv);
methods and caveats in docs/findings_log.md.*
