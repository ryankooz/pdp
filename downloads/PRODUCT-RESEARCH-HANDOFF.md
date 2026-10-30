# HANDOFF: Product Research (find → validate → swipe → launch)

> **For the next chat:** this file covers the **product and competitor research** method and everything it found.
> - Customer / ICP research (pain levels, keywords, desires) is in a separate file, `ICP-RESEARCH-HANDOFF.md` (`HANDOFF.md` in the repo).
> - Repo: `ryankooz/pdp`, branch `claude/great-dijkstra-a6qa7k`.
> - Written **Oct 30, 2026**. The user launches **~Oct 31 – Nov 3, 2026**.

---

## 0. TL;DR
1. **Current product:** hemorrhoid supplement. Brand **Veltia Labs**, product **Collagen Cushion Support** ("Cacao-Powered Support").
   - It swipes the winning competitor **Venalys** (venalyslab.com / venalyn.com).
2. **Launch set:** 3 ad sets × 3 creatives = 9 creatives, 3 copies (2 natives + 1 static). Final copy is in section 7.
3. **Before launch, fix the store to match the ads** (section 8):
   - a 150-day / 5-bottle "Buy 3 Get 2 Free" offer
   - a refund guarantee
   - a formula with cacao and collagen support
   - Copy B only from a real surgeon
4. **Backup to watch:** **Rare Nutrition** (rarenutrition-us.com, saw palmetto prostate formula, first ad Oct 29). Re-check around Nov 3.
5. **Never:** invented doctors, cure claims ("gone forever", "rebuild"), fake reviews.
   - **Cirae and KrakenSupps**, two rule-clean competitors, **vanished from the Meta Ads Library** this week, most likely banned for exactly these.

---

## 1. Who the user is and how they work
- Runs supplement / health dropshipping brands on **Shopify**, sold through **Meta ads** (native and advertorial), buyers mostly **40+**. Sources from **CJ Dropshipping**.
- Already ran **Biora** (IBS/SIBO). **Don't suggest it again.**
- **Method:** the **Meta Ads Library "rabbit-hole"**. Find a *fresh* store that is visibly scaling, then **swipe it 1:1 with their own brand**: "we're not reinventing the wheel or iterating, just putting my brand instead."
- Wants short, direct answers, tables, and final copy that's ready to paste.

---

## 2. The rabbit-hole rules (how to judge a competitor)
1. **Every ad**, active or inactive, **started within the last 28 days**. **An old ad for the same product means skip.**
2. **New ads every 1–3 days.** **3+ quiet days = fail.**
3. **A high ad count is fine if the ads are fresh.**
4. **Validate** by searching the store's **domain token** with **STATUS=all** (active + inactive), keyword unordered. Read the first ad, newest ad, new ads per day, cuts, pages and landing pages.
5. **Native persona ads** (first-person posts from persona pages) are the strongest signal.
6. **A falling total ad count** means the store is cutting ads.
7. **7-row playbook score (each row out of 5), test only at 28+/35:**

   | Row | Question |
   |---|---|
   | 1 | Is there a clear pain moment? |
   | 2 | Have they tried 3+ fixes? |
   | 3 | Can the mechanism be said in 10 words? |
   | 4 | Is the margin good? |
   | 5 | Is it felt in 7–14 days? |
   | 6 | Is it a private problem for a 40+ buyer? |
   | 7 | Is there proven demand + weak competitor messaging? |

8. **The product must be solvable by a product** (supplement or similar). A different format or mechanism than competitors (powder vs pill, patch, drops) is a **bonus, not a requirement**.
9. Exclude anything on the **kill list** (`research/meta-scraper/killlist.txt`).

---

## 3. The research pipeline

| Step | Source | Question it answers | Tool |
|---|---|---|---|
| 1. Demand | Reddit | Is the pain deep, unsolved, shared, and fixable by a product? | `pain-finder/` (see the ICP handoff) |
| 2. Growth | Google Trends + autocomplete | Is it rising? How do people search for it? | `pain-finder trends` / `suggest` |
| 3. Supply | Meta Ads Library | Is a fresh store scaling on it right now? | `research/meta-scraper/scrape.js` + the rules above |
| 4. Sourcing | CJ Dropshipping | Can I get it, at what cost, and in which formats? | `pain-finder cj --formats` |
| 5. Score | 7-row playbook | Test it or skip it? | 28+/35 only |

**A winner has:** deep Reddit pain **+** rising Google interest **+** a fresh store scaling on Meta (or a clear gap) **+** a format you can source.

### 3a. Meta Ads Library scraper: `research/meta-scraper/`
- **`scrape.js`** (headless Playwright Chromium): `node scrape.js out.json "phrase1" "phrase2"`
  - `STATUS=active|all`
  - `TYPE=keyword_exact_phrase|keyword_unordered`
  - `SCROLLS=1`
  - `MEDIA=all|video|image`
  - `EXTRA=` (appended to the URL)
- **Newest-first sort:** `EXTRA='&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped'`
- **What it captures:** library ID, start date (or range start if inactive), end date, active, page, body, landing URL, versions, media type.
- **Gotchas:**
  - Logged-out view shows about 30 ads per search.
  - **"~0 results" usually means throttling.** Space searches 40–90s apart and retry with a back-off.
  - **To confirm a real zero**, run a known store as a control search in the same run.
- **Scripts:**
  - `sweep.py`: phrase discovery, then domain validation
  - `pre30.py`: comparison + discovery + validation (the latest full run)
  - `chk28.py`: competitor comparison
  - `val30.py` / `val3.py`: domain validation of a token list
  - `copycat.py`: who is swiping a competitor's distinctive phrases
  - `killlist.txt`: stores to exclude

### 3b. How to find fresh stores
1. **Exact-phrase search** on **L3–L4 customer phrases**, sorted newest first. Phrases with fewer than about 300 results find fresh stores. Phrase banks: the ICP handoff and `research/data/level4-keywords.csv`.
   - **Phrases searched so far:**
     - **Identity and life loss:** "I used to be able to", "feel like a burden", "too embarrassed to", "nobody knows", "make excuses", "play with my grandkids", "is this my life now", "for the rest of my life", "feel normal again", "travel without worrying"
     - **Doctors and tests:** "bloodwork came back normal", "brushed me off", "I begged my doctor", "my colonoscopy", "my bloodwork", "I prescribe every day", "my doctor never mentioned", "my urologist", "my gastroenterologist"
     - **Urgency and scarcity:** "sold out again", "final batch"
     - **UTI, bladder and women 40+:** "UTI", "bladder leaks", "urinary tract", "D-mannose", "leak when I laugh", "up all night to pee", "after menopause", "women over 40", "women over 50", "hot flashes", "vaginal dryness"
     - **Authority and mechanism:** "nobody told me", "root cause", "German doctor", "Japanese doctor", "as a nurse", "retired nurse", "instead of surgery"
2. **Group the ads by landing domain.** Drop the kill list, big brands and non-supplements. Dramas, novels and gadgets show up a lot.
3. **Validate** the top candidates with a STATUS=all domain search, then **apply the rules**.
4. **Score** with the playbook.

### 3c. How to swipe a winner
1. **Pull their top ads** and sort them by **ad type** (static, native, expert) and **angle**.
   - "Top" = the same copy relaunched many times, on several pages, in both video and image, and still live after 2–3 weeks. Spend isn't visible.
2. **Pick the top 3 angles** by top-10 slots + ad count + how long they've run.
3. **Keep their exact hook, lead and headline.** Rewrite only the body, keeping the structure that makes it work.
4. **3 creatives per copy**, taken from **their** winning creatives (same layout, your brand). Native creatives get **no logo, no text overlay, no product**.
5. **Mix:** 2 natives + 1 static (BOF offer), across TOF, MOF and BOF.
6. **Remove what gets accounts banned:** invented doctors and cure claims. Put **your real numbers** in.
7. **Check for copycats** (`copycat.py`) to see if others are already swiping the same store.

### 3d. CJ sourcing: `pain-finder cj`
- Searches CJ by problem, ingredient and format (capsules, gummies, powder, drops, spray, patch, drink, strips, tea, cream). It shows which formats are proven (many products and stores) and which are open.
- **Results:**
  - `pain-finder/cj-results/`: body odor and others
  - `pain-finder/cj-results/uti/`
- **Found so far:**
  - **Chlorophyll drops** $0.92 (424 stores listing). Chlorophyll powder, patch, drink and tea are **not on CJ yet** (an open format).
  - **Cranberry + vitamin C softgels** $1.74 (UTI).
- **Hemorrhoid CJ search:** a child session was set up for hemorrhoid, piles, collagen, cacao, diosmin, horse chestnut, butcher's broom, witch hazel, sitz bath and rutin, with output to `pain-finder/cj-results/hemorrhoid/`. **It was waiting for the user's "yes", so check whether it ran.**
- **Needs** a `CJ_API_KEY` set in the environment's secrets.

---

## 4. What the research found (candidates)

### Reddit × Google product fit
| Condition | Product vs Rx | Google | Meta | Read |
|---|---|---|---|---|
| **Body odor** (even with good hygiene) | **31% vs 15%, best** | ×1.17, rising "why do I smell bad even with good hygiene" | Big persimmon-soap "aging odor / 2-nonenal" market for women 40+. Fresh: **Orchard & Root** (Oct 19, 30 ads, 5 pages). Older proof: Kaori, Swarva, Kakiyu, Mirai | The user doubted it, so it's **set aside**. Scored 31/35 |
| **Hemorrhoids** | 19% vs 29% | flat overall, but **female searches +300% to +2,900%** | **Venalys**: the clearest scaling proof | **Chosen** |
| Neuropathy | **24% vs 18%** | +38%/yr; "how I cured my neuropathy" +800% | Nervalley scaling | Sleeper |
| Bloating / gut | 28% vs 30% | ×1.39 | Lydra, Biora circle it | Biora already done |
| Constipation | 30% vs 29% | ×1.14 | Golovure (~240 ads) proof | Overlaps Biora |
| Lymphatic | 18% vs 31% | ×1.57, the fastest-growing | crowded | Ride it only with standout messaging |
| UTI | — | — | **Gloa Labs** (failed cadence) | CJ cranberry softgels $1.74 |
| Endometriosis, pelvic floor, reflux, lipedema | Prescription-dominated | — | — | **Skip** |

Details: `research/reports/combined-product-research.md`.

---

## 5. Competitor status (latest: Oct 30, 2026)
| Store | Product | Total ads | First → newest | Recent days with new ads | Cut | Verdict |
|---|---|---|---|---|---|---|
| **Venalyn** (venalyn.com) | Same as Venalys (2nd domain, same operator) | 190 | Oct 10 → **Oct 30** | Oct 21, 23, 24, 26, 27, 29, 30 | 19 | ✅ Still scaling |
| **Venalys** (venalyslab.com) | Hemorrhoid cacao/collagen | 720 | Oct 10 → Oct 29 | Oct 22, 23, 24, 29 | 0 | ✅ Active; the new ads are on Venalyn. (venalys.shop ran Sep 24–Oct 9, 29 ads, all cut.) |
| **Gloa Labs** (gloalabs.com) | UTI cranberry softgels, $32.95 Buy 1 Get 1, listicle funnel | 30 | Oct 20 → Oct 29 | Oct 20, 22, 26, 28, 29 | 0 | ❌ **Final no-go**: a 3-day gap and low volume |
| **Levoria** (trylevoria.com) | Diosmin "vein" hemorrhoid (a Venalys copycat) | 64 | → Oct 29 | Oct 29 only | 57 inactive | ❌ Cutting, dying |
| **Cirae** (trycirae.com) | Gout tart cherry. Advertorial "Dr. Rachel Hayes" → $39.99 / $69.99 (3) / $99.99 (5), 90-day guarantee | **0** | — | — | everything gone | ❌ **Banned or removed** |
| **KrakenSupps** | Constipation | **0** | — | — | everything gone | ❌ **Banned or removed** |
| Bottoms Up (getbottomsup.store) | Hemorrhoids for gay men | — | Oct 18 → Oct 23 | — | — | Own angle, not a copy |

**Venalys rule check:** Venalys breaks the 28-day rule and the old-ads rule (venalys.shop goes back to Sep 24). The user accepted this, because it's the strongest proof of scaling found. Venalyn is the same operator, not a ripoff.

**Copycat check (Oct 27):** 43 searches on Venalys's distinctive phrases. **No real outside copycats.** Levoria was the only swipe, and it's dying.

### Backup candidates (discovery Oct 30, 30 phrases)
- **Rare Nutrition** (rarenutrition-us.com): **the best one to watch.**
  - Product: saw palmetto prostate formula, men 50+.
  - First ad **Oct 29**, 39 total, 26 launched Oct 30, 3 pages (American Prostate Support Group, David Hart, Dr. Paul Miller).
  - Funnel: German-doctor advertorial → product.
  - **Re-check around Nov 3:** if it's still adding ads every 1–3 days with no falling total, it passes.
- **Kaira Wellness** (kairawellness.com): transdermal **bladder patches** for women 50+ with overactive bladder (a different format, a plus). First ad Oct 14, 61 ads, 0 cut, 3 pages, a burst Oct 24–27. **Quiet since Oct 28**, so it fails today.
- **Rejected:** Dermiqua (ads since July), Lovy / trylovy (April), Her Vitality (June), Bioma (2025), Fortis Health (Sep 26, a wrap, not a supplement), Auniva (no new ads since Oct 9), Amala / Lovi Health (no data; Lovi is probably "trylovi" from the kill list).

Raw data: `research/data/oct30-comparison.json`, `oct30-discovery-candidates.json`, `oct30-backup-validation.json`.

---

## 6. Venalys teardown (what we copy, and why it works)

### Offer and funnel
- **Product:** "Collagen Cushion Support Capsules", hero ingredient **non-alkalized cacao flavanols**, 2 capsules a day.
- **Mechanism:** everyone has 3 rectal cushions held by a collagen mesh. After 40 you lose about 1% of collagen a year, so the cushions slip. Bleeding and itching are symptoms; the collapsed cushion is the cause. **Collagen, not veins.**
- **Villains:**
  - creams (hydrocortisone is only labeled for 7 days), fiber, wipes, donut cushions
  - **vein supplements (diosmin, hesperidin, horse chestnut): "tone the vessels, ignore the mesh"**
  - banding and surgery
- **Prices:**
  - $39.90 for 1 ("30-day trial")
  - $119.70 for 3 (Buy 2 Get 1)
  - **$179.50 for 5 (Buy 3 Get 2), labeled "MOST POPULAR • FREEDOM PROGRAM"** (150 days)
  - **12-month "Freedom Guarantee"**
  - "40% OFF ends at 11:59pm"
- **Funnel:** ad → product page (most ads) or a "Top 5 hemorrhoid solutions" listicle ("Dr. Matthew Hayes") → product page.
- **Pages:** 7+ personas or publishers: Venalys, Dr. Matthew Hayes, David Miller, Better Gut Living, Digestive Wellness Network, The Naked Truth on Health, The Fourth Trimester Relief (postpartum); on Venalyn: Dr. Fabian Liebscher, Gary Whitmore, Susan Rhodes.
- **Format:** Meta counts about 71 image ads vs about 31 video ads. Image + long copy dominates.

Full funnel breakdown: `research/reports/cirae-venalys-funnels.md`.

### 16 angles, by ad volume (from about 420 ads)

| # | Angle | Ads |
|---|---|---|
| 1 | Surgeon confession | ~66 |
| 2 | Collagen, not veins | ~63 |
| 3 | Finish line ("they want you buying forever") | ~52 |
| 4 | Patient vs surgeon | ~46 |
| 5 | Flare-ups mean it was never fixed | ~45 |
| 6 | Life loss (L3–4) | ~30 |
| 7 | Nurse insider | ~17 |
| 8 | Postpartum | ~16 |
| 9 | Urgency | ~14 |
| 10 | Symptom self-check | ~14 |
| 11 | Ranking / takedown | ~11 |
| 12 | Sex and intimacy | ~9 |
| 13 | "My husband is a surgeon" | ~8 |
| 14 | Shock / home fixes | ~5 |
| 15 | Foods to avoid | ~5 |
| 16 | Relief testimonial | ~3 |

About 65% of their ads are angles 1–5.

### The user's Venalys top 10 (from their screenshots)
Positions: top row 1–5, bottom row 6–10.

| # | Library ID | Page | Hook | Creative | Link headline | Type | Angle |
|---|---|---|---|---|---|---|---|
| 1 | 3859877310819123 | Dr. Matthew Hayes | "I recommended the same hemorrhoid protocol to 89 patients…" | Orange background + bottle, "doctors issue a warning?" | This will confirm your suspicions. | Expert | Surgeon confession |
| 2 | 2422274331910009 | Digestive Wellness Network | "💸 Every hemorrhoid supplement wants you to keep buying it forever" | Video, bottle in a store aisle | Hemorrhoids aren't just forever? | Brand | Finish line |
| 3 | 1087161883929270 | Better Gut Living | same as #2 | "Official 5-bottle offer, Buy 3 Get 2 Free" | 40% OFF ends at 11:59pm | Static | Finish line |
| 4 | 1088313590757998 | Dr. Matthew Hayes | same as #1 | Black, "SCAM EXPOSED", red arrow, "SCAM?" | This will confirm your suspicions. | Expert | Surgeon confession |
| 5 | 1614565426810529 | Better Gut Living | "The most dangerous sign of hemorrhoids isn't the pain…" | Doctor at a whiteboard: "The 'hemorrhoid killer' protein is called…" | Hemorrhoids Or Collagen Failure? | Expert education | Flare-ups |
| 6 | 2003014067054566 | David Miller | "So sick of people in my group swearing Collinsonia and Diosmin…" | Red grapes on a tape measure | Colorectal surgeon: hemorrhoids aren't varicose veins | Native | Competitor takedown |
| 7 | 1097904886428753 | Venalys | same as #2 | "THIRD FLARE THIS YEAR? Try Venalys", cushion icons | 40% OFF ends at 23h59 | Static | Finish line |
| 8 | 28941504235485744 | Digestive Wellness Network | "My new boyfriend… 'Babe, is this a hemorrhoid?'" | Pencil-sketch illustration | Hemorrhoids Are Collagen Failure? | Native | Sex and intimacy |
| 9 | 2105520263439478 | Venalys | same as #2 | Text-heavy "FINAL NOTICE: WE ARE CLOSING THE OFFER" | 40% OFF ends at 23h59 | Static | Finish line + urgency |
| 10 | 1655557989247292 | Better Gut Living | "Honestly thought I'd have hemorrhoids for the rest of my life" | "F*CK YOU, HEMORRHOIDS." + bottle | Finally hemorrhoids you can actually forget | Native | Relief testimonial |

**Top 3 performing angles:**
1. **Finish line**: 4 of 10, about 52 ads, 3+ pages, video and image.
2. **Surgeon confession**: the most ads, 15+ scripts, still adding.
3. **Flare-ups**: the widest page spread for one script.

### Why they work
- **Finish line:**
  - it names a villain the buyer already suspects (the business model)
  - it flips the "forever subscription" objection into the selling point
  - it justifies the 5-bottle bundle
  - one script runs under many creatives
- **Surgeon confession:**
  - an insider turns on their own industry
  - specific numbers (89 / 31)
  - the L4 fear of surgery
  - skeptic images stop the scroll
- **Flare-ups:**
  - a curiosity gap ("isn't… isn't… isn't…")
  - it reframes the buyer's own words
  - "failing 1% a year since forty" turns "managing it" into losing
- **Shared by all of them:**
  - one mechanism under every angle
  - the hook confirms frustration before selling
  - L3–4 pain
  - specific details
  - an offer built into the angle
  - many pages, one script, many creatives

Copy for the top ads: `research/reports/venalys-top10-ads.md`.

---

## 7. FINAL LAUNCH SET: Veltia Labs Collagen Cushion Support

**Brand assets:**
- **Label:** cacao pod, beans and leaves line art; "Cacao-Powered Support"; Non-GMO / Alcohol Free / GMP badges; "Herbal Dietary Supplement, 100% Plant-Based, 60 Capsules, Net Wt 35 g".
- **The 9 final creatives** are in the user's `veltia-nine-ad-creatives_1.zip` (PNG, 1122×1402).

| Ad set | Copy | Type | Funnel | Creatives (file ← Venalys source) |
|---|---|---|---|---|
| 1 | A: Finish line | Static | BOF | `1A-five-bottle-offer.png` ← #3 · `1B-third-flare.png` ← #7 · `1C-before-you-buy.png` (Final Notice) ← #9 |
| 2 | B: Expert confession | Expert native | MOF | `2A-orange-label-check.png` (doctors warning) ← #1 · `2B-scam-or-substance.png` (scam exposed) ← #4 · `2C-grapes-and-tape.png` ← #6 |
| 3 | C: Flare-ups | Customer native | TOF | `3A-collagen-whiteboard.png` ← #5 · `3B-two-am-sketch.png` ← #8 · `3C-orange-statement.png` (F*CK YOU, HEMORRHOIDS.) ← #10 |

- 6 of the 9 (1A–1C, 2A, 2B, 3A) ran under the same copy at Venalys.
- 2C, 3B and 3C are borrowed from other winning top-10 ads.
- The native images (2C, 3A, 3B) have **no logo, no text, no product**.
- **Unused option:** Venalys #2, the store-aisle video, as a 4th creative for ad set 1.

Each copy keeps **Venalys's exact hook, lead and headline**. Fill in the `[brackets]` with true numbers.

### Copy A: Finish line (static, BOF)
```
💸 Every hemorrhoid supplement wants you to keep buying it forever. Because they treat the symptom, not the collagen deficit underneath. That's the whole business model. You stop taking it, the flares come back. Every time.

🍫 Veltia Labs Collagen Cushion Support is different. You take it for [150 days] to support the collagen your rectal cushions have been losing since you turned 40.* Then you stop.

✅ If your flares come back within [12 months] of finishing, full refund. 🛡️

⭐ [2,148] people have already finished the program.

No other hemorrhoid brand puts an end date on it. There's a reason.

[Offer line, e.g. "40% OFF ends at 11:59pm"]
```
- **Headline:** 40% OFF ends at 11:59pm
- **Description:** Veltia Labs Collagen Cushion Support is a daily plant-based capsule formulated with cacao and botanical extracts, traditionally used to support collagen and comfort.*
- **Warning:** delete the "[2,148] people" line until there's a real number.

### Copy B: Expert confession (native, MOF). ONLY from a real, licensed colorectal surgeon on their own page.
```
I recommended the same hemorrhoid protocol to [89] patients last year. [31] of them still ended up on my surgery schedule. Same protocol. Same explanation. Same instructions. But more than a third of the people I was trying to keep out of my operating room walked right back into it.

I'm [Dr. Full Name, credentials]. I've been a colorectal surgeon in [city] for [X] years. I don't recommend anything I haven't watched work.

Creams calm the surface. Fiber takes pressure off. Banding removes what's already there. None of them do anything about the collagen that holds your cushions in place, and that support has been thinning since you turned 40. That's why they walk back in.

So before I recommended anything to my patients, I tried Veltia Labs Collagen Cushion Support with [12] of them first. [Six months], in my own clinic. [True observation in the doctor's own words.]* Two capsules a day. It's a [150-day] program, not a forever product.

I'm not telling you to skip your doctor. I'm telling you what I now ask my patients to try before we talk about the operating room.
```
- **Headline:** This will confirm your suspicions.
- **Description:** same as Copy A.
- **No real surgeon? Don't run ad set 2.** Launch ad sets 1 and 3 only.

### Copy C: Flare-ups (customer native, TOF)
```
The most dangerous sign of hemorrhoids isn't the pain when you sit. It isn't the itching. It isn't even the blood on the toilet paper. It's the words flare up. A flare up means it comes and it goes, and something that goes away is something you're allowed to wait out. Nothing has gone away. The thing underneath has been failing at about one percent a year since you turned forty, straight through every good week you've had. The flare ups are just the weeks you can see it.

A colorectal nurse said that in a video I watched at 2am, and I cried. Because I'd been waiting mine out for [9] years.

"It's just flaring up again." I said it to my husband when I bailed on the road trip. I said it to myself when I picked the aisle seat at every wedding. Every time it calmed down, I thought I'd won. I'd stop the cream, forget about it, and three weeks later I'd be planning my whole day around where I could sit.

Nobody told me the cream only calms the surface. The thing underneath is collagen, the support that holds your cushions in place, and it keeps thinning whether you're having a good week or a bad one.

That's what Veltia Labs Collagen Cushion Support is for. Two capsules a day, [150 days], supporting the collagen underneath instead of the surface on top.* I'm in month [4]. [Real result in her words, e.g. "I haven't said the words 'flare up' since August."]*

If you're still waiting yours out, this is for you.
```
- **Headline:** Hemorrhoids Or Collagen Failure?
- **Description:** same as Copy A.
- **Option for the sketch creative:** "A cacao capsule that supports collagen in the rectal cushion.* Two capsules a day for [150] days, then you stop."
- It must be posted by a **real** customer or creator (partnership ad) with a true story.

**Footer:**
> \*These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.

### How to run it
- **Day 1:** all 9 ads, sent to the product page with the **5-bottle bundle preselected**.
- **Pages:** brand page + real customer or creator pages (partnership ads).
- **Days 2–4:** in each ad set, kill the weakest creative and put a new image under the **same copy**.
- **Scale:** duplicate the winning creative onto another real person's page.
- **Next wave:** sex and intimacy ("Babe, is this a hemorrhoid?"), relief testimonial, postpartum (Venalys's newest page, and it matches the rising female searches).

---

## 8. PRE-LAUNCH CHECKLIST
- [ ] **Offer:** a **150-day / 5-bottle "Buy 3 Get 2 Free"** bundle as the default or most popular option.
  - Venalys charges $179.50 for 5.
  - Current template (`templates/product.cushion-support.json`): 1 month $44.99, 3 months $89.99, 5 months $129.99. Decide the price.
- [ ] **Guarantee:** a refund if flares come back within [12 months] of finishing. If you won't honor that, change the copy to your real terms.
- [ ] **Formula:** the supplier must confirm **cacao (flavanols)** and **collagen support**.
  - The template's ingredient cards currently lead with diosmin and horse chestnut, which is Venalys's villain.
  - Update the cards, and remove anything you don't actually source.
- [ ] **Discount:** use "40% OFF ends at 11:59pm" only if it's real.
- [ ] **Numbers:** every `[bracket]` must be true or deleted.
- [ ] **Copy B:** only with a real licensed surgeon.
- [ ] **Label wording:** "Cacao-Powered **Support**", not "Rebuild".
- [ ] **Product page:** FDA disclaimer, discreet shipping, the same mechanism language as the ads.
- [ ] **Reviews:** the template has placeholders. **Never fabricate reviews.**
- [ ] **CJ:** source the capsule and check the hemorrhoid CJ results (section 3d).

---

## 9. Compliance (why it matters)
| Don't | Do instead | Why |
|---|---|---|
| Invented doctors, nurses or credentials | Real people only; a customer quoting their own doctor; a real licensed expert using their real name | FTC deceptive endorsements; **Cirae and KrakenSupps vanished** |
| "Cures", "gone forever", "stay free", "rebuild" | "Supports", "program", "routine"; let the **guarantee** carry the promise | Disease claims are illegal for supplements and get accounts banned |
| Fake testimonials or review counts | Real, typical results | FTC, chargebacks |
| Claims with no disclaimer | Asterisk + FDA disclaimer | Required |

---

## 10. Files
| File | What it is |
|---|---|
| `research/meta-scraper/` | `scrape.js` + all sweep, validation and copycat scripts + `killlist.txt` |
| `research/reports/combined-product-research.md` | Reddit × Google × Meta × CJ cross-reference and playbook scores |
| `research/reports/cirae-venalys-funnels.md` | Venalys vs Cirae offers and funnels |
| `research/reports/venalys-top10-ads.md` | Venalys's top ads, with copy |
| `research/data/oct30-*.json` | The latest comparison, discovery candidates and backup validation |
| `research/data/body-odor-meta-competitors.csv`, `body-odor-google-searches.csv` | The set-aside body odor market |
| `pain-finder/cj-results/` | CJ format and product searches |
| `templates/product.cushion-support.json` | The Shopify product page (needs the updates in section 8) |
| `ads/cushion-support-natives.md` | The launch plan file (section 7 above is the latest version) |
| `ads/cushion-support-launch-ads.md` | The first draft ad pack (superseded) |

## 11. Next steps
- **~Nov 3:** re-validate **Rare Nutrition**, **Kaira Wellness** and **Venalyn** with `pre30.py` (edit its token list) or `val30.py`.
- **After launch:** run `copycat.py` on your own hooks to see who swipes you, and run a fresh discovery sweep weekly for backups.
