# Grounding-Retrieval Automation — design

STATUS: PROVISIONAL — extraction unvalidated. Early evidence (the uploaded ODS dashboard HTML rendered content via Tableau, so page data was not present in the raw HTML) suggests the full-automation fetch/extract may not work on individual dashboard pages. Listing-page text is extractable; individual dashboard content may require manual save-as. Test extraction on one page before building the pipeline; downgrade to "LLM structures a few manually-saved pages" if needed.

Automates the CLERICAL parts (fetch, extract, match). Keeps HUMAN judgment at the two points
that matter (is this a real finding? does this source truly ground it?). Build in Claude Code, where
your own network permissions apply.

## Pipeline overview

    [1. findings.csv]  <- you + matrix produce this (human judgment: real vs structural)
            |
            v
    [2. crosswalk.csv] <- maps your 22 services -> DHS topic tags (built once, reused)
            |
            v
    [3. fetch_dashboards.py]  <- clerical: pull filtered pages from analytics site
            |
            v
    [4. extract_catalog.py]   <- clerical: HTML -> structured rows (title/date/desc/tags/url)
            |
            v
    [5. match_candidates.py]  <- clerical: join findings to catalog rows sharing a tag
            |
            v
    [candidates_for_review.csv] <- you decide: aligned / gap / structural  (HUMAN judgment)
            |
            v
    [findings_grounded.md]    <- you write the so-what  (HUMAN)

## Stage 1 — findings.csv  (INPUT, human-made)
Columns: finding_id, service_A, service_B, shared_count, cond_A_to_B, cond_B_to_A, lift, verdict
`verdict` in {informative, structural, gap-candidate}. Only `informative` rows proceed.
This file is the output of the matrix lesson we still need to do together.

## Stage 2 — crosswalk.csv  (INPUT, built once)
Columns: service_name, dhs_topic_tags (pipe-separated)
e.g. Individuals_Receiving_Substance_Use_Disorder_Services | behavioral health;opioids;substance use
Built by hand from the site's own tag vocabulary. ~22 rows. Reused forever.

## Stage 3 — fetch_dashboards.py  (CLERICAL)
For each unique topic tag needed by the informative findings, hit the site's filtered URL and
save raw HTML locally. Polite scraping only: respect robots.txt, 1 request/sec, cache to disk so
you never re-fetch. If the site filters client-side (JS), fall back to saving the page manually in
the browser (File > Save) and dropping the HTML into a folder the extractor reads — same result.

## Stage 4 — extract_catalog.py  (CLERICAL)
Parse saved HTML (BeautifulSoup) into rows: title, date, description, tags[], url.
This is the ONE place an LLM may help — turning messy HTML into clean fields — and only on HTML
you actually fetched. Never let it invent entries. Validate: every row must have a real url.

## Stage 5 — match_candidates.py  (CLERICAL)
Join: for each informative finding, find catalog rows whose tags intersect the finding's services'
crosswalk tags. Output candidates_for_review.csv with finding_id, matched title/url/date/desc.
This only proposes CANDIDATES. It does not decide grounding.

## The two human gates (do NOT script these)
- Gate A (after Stage 1): is each strong pair informative or structural/definitional?
- Gate B (after Stage 5): does each candidate TRULY ground the finding, or just share a word?
  Mark each: aligned / gap / structural. Then write the implication yourself.

## Guardrails
- LLM may EXTRACT from fetched text; may never GENERATE priorities from memory.
- Every grounded citation must carry a real URL that a reviewer can click.
- Date mismatch is expected (data=2021, dashboards=2024-26): ground the STANDING relationship,
  never claim numeric confirmation across years.
