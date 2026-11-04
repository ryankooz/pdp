---
name: ecom-product-research
description: "Find and validate early-stage winning ecommerce/DTC products with the Rabbit-Hole Meta Ads Library method: keyword chaining from real ad copy, free pre-spend screens, and five validation gates (ad recency, live volume, cadence, delivery, store/SKU age). Use when the user asks for product research, winning-product discovery, store hunting, keyword chaining, hourly research runs, or to validate a pasted product, store, Shopify URL, or Meta ad."
---

# Ecommerce Product Research

## When to Use

Use for winning-product discovery, store hunting, hourly research, keyword chaining, and validating a pasted product/store/ad. This workflow implements the current Rabbit-Hole method; it is not the old advertising-only three-gate version.

## Paths and setup (Claude Code)

All commands run from the **repository root**. Durable state lives in `intel/product-research/` (override the root with `ECOM_WIKI_ROOT`):

- `intel/product-research/_state/research.sqlite` - keyword queue, candidates, runs, observations
- `intel/product-research/_state/evidence/` - wave/probe JSON from Meta Ads Library (git-ignored)
- `intel/product-research/runs/` - human-readable run summaries and verdict blocks (Markdown)
- `intel/product-research/ledger.md` - product ledger, do-not-spend register, struck-keyword index

Cloud sessions are ephemeral: **commit and push** the state DB, ledger and run summaries at the end of every session or they are lost.

First run in a fresh checkout:
1. `python3 .claude/skills/ecom-product-research/scripts/rabbit_hole_state.py init`
2. Browser: the scripts use the installed `playwright` package if available, else `playwright-core` (`npm install` in the skill folder). They use Edge if found, otherwise Playwright's Chromium; override with `EDGE_EXECUTABLE` / `CHROME_EXECUTABLE`. `META_ADS_COUNTRY` (default `US`) sets the library geography.
3. If a read returns `login_wall: true`, or zero `library_ids` on a query that should be busy, report it as a **tool blocker** (Meta may gate datacenter IPs), not a research result.

## Source hierarchy

1. Optional local doctrine, if present: `doctrine/sources/rabbit-hole-method/accumulated-method/` and `doctrine/sources/rabbit-hole-method/transcripts/`. These are not shipped with this skill; if absent, rely on this file plus the reference.
2. For exact screen definitions, gate caveats, and keyword shapes, read `references/rabbit-hole-method.md` (in this skill folder).

## Governing rules

- **Keywords are the supply engine.** Mine them from real ad copy, URLs, mechanisms, complaints, avatars, competitor/enemy brand or drug names, and validated operators' secondary products. Never invent a keyword to pad a run.
- **Cheapest evidence first.** Reject by durable history, exclusions, persona identity, store catalogue, and structural screens before spending a Meta Ads Library navigation.
- **Disqualifiers outrank attractive metrics and all five gates.** Reject established brands, catalogue/general stores, relay/clone networks, persona fleets, service-led offers, retail-held products, affiliates/creator layers, info products, B2B/OEM suppliers, and DME/insurance lead generation.
- **A null run is valid.** Report no screened keyword or no validated product plainly; never manufacture activity.
- **A host is disposable; a persona is durable.** Search the host, product noun/path, and every advertiser page/persona name before validating.
- **The product must be early, not merely the ads.** Gates (a)-(d) measure advertising; gate (e) is mandatory when available because it measures store/SKU age.

## Procedure

### 1. Load durable state before choosing a keyword

Read the product ledger, keyword queue, keyword history, do-not-spend register, struck-keyword index, candidate queue, and the previous run summary. Dedupe against hosts, unique brand stems, product nouns, page/persona names, and destination paths—not hostname alone.

Inspect grep hits structurally rather than trusting counts. Small counts often consist of the original dig plus carry-forward lines. Match product/path phrases hyphen-flexibly because URLs and prose spell the same phrase differently.

### 2. Choose 3–5 starter roots from Ads-Library-derived supply

The Rabbit-Hole research instrument is **Meta Ads Library**. TrendTrack is not required and must never pause, block, replenish, or control this workflow. It may be used elsewhere for swipe discovery, but not as the dependency for Rabbit-Hole product research.

Starter priority:
1. Other products/mechanism words from a newly validated operator.
2. Customer-spoken complaint or mirror language from live copy.
3. Seller-created category coinage or differentiated product noun.
4. Specific mechanism, avatar, feature, or benefit phrase.
5. Enemy **brand/drug** name that sufferers recognize.
6. Broad generic offer terms are doctrine examples only. **Owner rule: do not start scheduled research with `shop now`, `free shipping`, or `50% off`.** Scheduled runs begin with specific, verbatim product/problem/mechanism/benefit phrases already harvested in the Rabbit-Hole sources or later live ads.

If the queued frontier is empty, replenish it without TrendTrack by mining unsearched verbatim phrases from the Rabbit-Hole source bundle, prior Ads Library evidence, current candidate/product pages originally discovered through Ads Library, and secondary products or mechanisms from productive operators. Apply free screens, select 3–5 roots, and restart Ads Library branching. An empty SQLite queue is not a reason to stop while these Ads-Library-derived reservoirs remain.

Avoid diagnoses, broad category nouns, enemy generic nouns, ambiguous homographs, high-frequency verb/adjective pairs, phrases one edit from common words, and phrases already covered by a measured dead aisle.

A keyword bank is not a queue merely because its exact tokens grep clean. Grade its aisle by neighboring nouns, known hosts, operator/persona identities, and exclusion classes before spending it.

### 3. Run free pre-spend screens

Run, in order:
1. Register + struck-keyword exclusions; measured exclusions are terminal, assumed exclusions may receive one measured test.
2. Carry-line inspection of every history grep.
3. Dealer/local-producer channel.
4. Secondhand-market dominance.
5. Verb/adjective, gerund, broad-head-noun, and homograph collisions.
6. Edit-distance coinage fuzz.
7. Service layer: ask who gets paid when the sufferer acts.
8. Retail-held commodity and roughly sub-$10 price floor.
9. Catalogue/path census.
10. Volume-window sanity: very broad surfaces expose only canopy; very thin surfaces usually lack an operator layer.
11. Field-view age prohibition: field dates can kill but cannot pass.
12. Product coinage vs enemy generic noun.
13. Persona/page-name grep, with distinctive titled identities weighted more than common names.
14. Host count before young-card ratio.
15. B2B/OEM manufacturer collision.

If these screens reject the keyword or candidate, log the exact reason and do not navigate Meta.

### 4. Load the field and harvest before judging

**Meta Ads Library is the canonical and sufficient research instrument.** Use `node .claude/skills/ecom-product-research/scripts/meta_ads_library_probe.mjs "<keyword-or-full-URL>" "intel/product-research/_state/evidence/<name>.json"`. It launches an isolated headless browser profile (never the owner's own profile). Parse `body_text`, `links`, `library_ids`, decoded `destinations` (from `l.php?u=`), `login_wall`, `no_ads_match` and the result counter from the JSON. Use a full page/domain URL for candidate history views. Do not require TrendTrack credits, launch radar, product records, or attribution to run Rabbit-Hole research.

Search Meta Ads Library in the target geography with `search_type=keyword_exact_phrase`; do not put quotes inside `q`. Load in bounded scroll chunks, deduplicate by Library ID, and do not assume a fixed card cap.

For each card, decode outbound `l.php?u=` links and preserve the full destination path. Judge composition only after harvesting links: does this surface contain independent DTC operators shipping a product, rather than services, clinics, courses, apps, affiliates, retailers, catalogues, or manufacturers?

Harvest aggressively from every useful card, destination page, operator catalogue, product path and persona—even when the candidate fails. **The 3–5 count applies only to starter roots; it does not limit branch searches or branches harvested.** Search qualified children, grandchildren and deeper descendants during the same session through repeated waves. There is no small harvest quota: queue every distinct, high-quality verbatim branch that survives the free screens. Prioritize product nouns, secondary products, seller coinage, mechanisms, customer mirror language, avatars, specific enemies and concrete feature/benefit phrases. Preserve `parent_keyword_id`, root and branch depth so later runs can keep following the strongest limbs several generations deep. A failed or old operator can validate demand and supply many keywords for fresh operators.

### 5. Pre-validate each candidate for free

Before page-level Meta navigation:
- Grep host, brand stem, product noun/path, and all card page/persona names.
- Fetch `https://<host>/products.json?limit=250` when Shopify is indicated.
- Record SKU count, oldest/newest `created_at`, creation-date spread, products/prices, catalogue shape, bundles/refills, and whether the advertised product still exists.
- Treat near-zero age with many same-day SKUs as a rebuild/import, not a clean launch.
- Treat a 404 plus non-`/products/` paths as non-Shopify: gate (e) is unavailable, not passed.

### 6. Apply all five validation gates

- **(a) Ad recency:** oldest same-product ad is within 28 days. Use the host-pure domain/page history, never a keyword field view. A field-view date may kill but never pass.
- **(b) Live volume:** at least 5 live, own-host ads after token-fuzz filtering.
- **(c) Cadence:** new ads every 1–3 days; weekly is weak; a gap over roughly 10 days kills when the read is not capped.
- **(d) Delivery:** evaluate `Low impression count` share only for cohorts at least 5 days old. Rough pass band 2–43%; rough fail band 65–81%.
- **(e) Store/SKU age:** gap from oldest SKU creation to that candidate's first ad is under about 60 days. Measure against first-ad date, never today. Treat 60–180 days as borderline and 180+ as established.

Capped-read asymmetry: when the counter exceeds the rendered-card ceiling, trust a cadence **pass** and delivery **fail**; distrust a cadence **kill** and delivery **pass**. Never force certainty from a capped read.

Partition pitfall: `start_date[max]` renders a date chip one day earlier. To test for anything older than a 28-day cutoff, pass the cutoff date itself and verify the chip reads the preceding day. `start_date[min]` may be ignored. Pair a partition zero with an unfiltered count; only literal “No ads match” is conclusively empty.

### 7. Save evidence and continue the chain

For each candidate save:
- product, host, page/persona names, full destination path, source keyword, and keyword trail;
- Ad Library URL/page ID, counters, rendered-card count, own-host count, oldest/newest dates, cadence map, delivery cohorts;
- products.json status, SKU ages/count/shape, price, advertised-product presence;
- pass/fail/unknown for every gate, disqualifier checks, and confidence;
- exact kill reason or validation rationale;
- newly harvested keywords with their source phrase/card.

Separate outcomes: `VALIDATED`, `WATCH/RECHECK`, `KILLED`, `UNMEASURABLE`, and `SWIPE-ONLY`. Do not convert missing evidence into a pass.

### 8. Hourly automation discipline

Each hourly session selects **3–5 starter/root keywords**, then recursively searches through their branches **multiple times during that same session**. The 3–5 count is only the number of starting trees; it is not the total number of keyword searches.

Run in waves:
1. Search the 3–5 starters together.
2. Harvest and screen every strong child branch.
3. Search the strongest qualified children in another batch during the same session.
4. Harvest their children and search the strongest grandchildren.
5. Keep repeating branch waves while the frontier contains qualified terms and the session still has operating time. A productive root should receive multiple search generations; do not merely queue all children for the next hour.

Use breadth plus depth: pursue several independent limbs per starter instead of following only one chain. Queue overflow branches for later hours, but search a meaningful subset of children and grandchildren now. Stop an individual limb only when it is struck, dead, excluded, exhausted, duplicate, or structurally weak. Preserve parent/root/depth lineage on every child.

Batch commands: begin with `python3 .claude/skills/ecom-product-research/scripts/rabbit_hole_state.py next-keywords --limit 5`, then call `node .claude/skills/ecom-product-research/scripts/meta_ads_library_batch.mjs "intel/product-research/_state/evidence/<wave>.json" "<kw1>" ...` (max 5 keywords) once per wave. Record each harvested child with `rabbit_hole_state.py add-keyword "<text>" --source-type ad_copy --quote "<verbatim>" --url "<card/destination URL>" --shape <class> --parent-id <id>`, mark searched keywords with `mark-keyword <id> <status> --attempt`, and close the session with `log-run`. `status` prints queue and run counts. The first call covers the starters; later calls in the same hourly session cover qualified children, grandchildren and deeper branches.

**Keep the hourly researcher running continuously.** In Claude Code, set it up as a recurring scheduled task (every 60 minutes, no finite repeat limit) only when the user asks for one. Never pause the job because an optional discovery source, enrichment service, or unrelated integration is unavailable; Meta Ads Library plus the durable keyword reservoirs are sufficient. A failed run may end honestly, but the next hourly tick must remain scheduled.

When asked for status, verify all of: enabled/paused state, schedule, current execution state, last completed run, next scheduled run, latest durable run record, and newest evidence timestamp. `enabled` or a future `next_run_at` alone does not prove that hourly work has been completing. If a gap exists, state its exact boundaries plainly, resume/reset the schedule, trigger one recovery run, and never describe the gap as continuous operation.

Keep collection and deep validation separable so a rate wall or time limit preserves harvested links and keywords. Use continuity only as convenience; files are the source of truth. Notify on new validated products, meaningful watch changes, or a blocker needing login—not on ordinary null runs unless the user requests every-run reports.

Before enabling a recurring job, define the target geography, exclusions/legal boundaries, delivery channel, output ledger path, and whether uncertain non-Shopify candidates may enter WATCH. The default validation thresholds are US-calibrated; non-US libraries may be used for vocabulary but require separately calibrated live-volume and cadence gates.

## Output style

Lead with validated products, then watch/recheck candidates, exact kills, keyword trail, harvested unsearched keywords, and source links. Keep verdict blocks compact and evidence-heavy. Label limitations and unknowns plainly.
