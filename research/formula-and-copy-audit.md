# Formula check and PDP copy audit

Companion to [`customer-research-bootstrap.md`](customer-research-bootstrap.md). Covers bootstrap Priority 5 (verify the formula) and checks the copy in `templates/product.gut-complex.json` against the guardrails in bootstrap Part 14.

Prepared October 13, 2026. trybiora.com was not reachable from this environment, so the formula below comes from the Supplement Facts image pulled from the live page in the previous commit (`preview/img/product-9.webp`). Re-check it against the current label before using it.

## 1. The actual formula

**Serving:** 1 dropper (1 mL). **Gut Restoration Blend: 800 mg**, a proprietary blend with no per-ingredient amounts:

| # | Ingredient (as labeled) | Standardization | Upper bound per 1 mL* |
| --- | --- | --- | --- |
| 1 | Ginger root extract | 20% gingerols | ≤ 800 mg (realistically well under) |
| 2 | Artichoke leaf extract | none stated | ≤ 400 mg |
| 3 | Clove oil | "Eugenol" (no %) | ≤ 266 mg |
| 4 | Oil of oregano extract | 80% carvacrol | ≤ 200 mg |
| 5 | Black walnut hull extract | 2% juglone | ≤ 160 mg |
| 6 | Dandelion root extract | none stated | ≤ 133 mg |

\*FDA rules (21 CFR 101.36) require blend ingredients to be listed in descending order by weight. So the nth ingredient can be at most 800 ÷ n mg. These are ceilings, not actual amounts.

**Other ingredients:** purified water, vegetable glycerin, natural lemon flavor, sunflower lecithin, gum acacia, citric acid, monk fruit extract, potassium sorbate.

**Corrections to the bootstrap:**

- **No berberine.** Part 1.1 mentions berberine. It is not on the current label, so don't carry berberine evidence or messaging into this product.
- **Gingerols are real.** Ginger is listed first, so it is likely the largest component.
- **Exact doses can't be confirmed from the label.** Because it's a proprietary blend, Step 5 question 5 ("Is its dose consistent with research?") can't be answered for any ingredient without the manufacturer's formula sheet. Ask the brand for it.

## 2. Evidence snapshot by ingredient

This is a starting map, not a finished literature review. Every reference needs to be pulled and read before it supports a claim on the page.

| Ingredient | Most relevant human evidence | Studied dose vs. this product | Strength for this use |
| --- | --- | --- | --- |
| Ginger | Faster gastric emptying and more antral contractions: Hu et al., *World J Gastroenterol* 2011 (healthy volunteers) and Wu et al., *Eur J Gastroenterol Hepatol* 2008 (functional dyspepsia). | ~1.2 g ginger powder. This extract is concentrated (20% gingerols vs. low single digits in powder), so gingerol content may be comparable, but the exact amount isn't disclosed. | Moderate for **stomach** emptying. Very little human data on small-intestine MMC activity or SIBO recurrence. |
| Artichoke leaf | Functional dyspepsia RCT: Holtmann et al., *Aliment Pharmacol Ther* 2003. IBS symptom data is mostly open-label or post-hoc. | 640 mg, three times daily in the dyspepsia trial vs. ≤ 400 mg per serving here. | Moderate for dyspepsia symptoms (fullness, bloating). Weak for IBS. |
| Oregano oil | Mostly in vitro antimicrobial work. One small uncontrolled study on enteric parasites: Force et al., *Phytother Res* 2000. | 600 mg/day emulsified oil vs. ≤ 200 mg per serving here. | Weak in humans. |
| Clove oil / eugenol | In vitro antimicrobial and anti-biofilm studies. | No meaningful human GI data. | Preclinical only. |
| Black walnut hull | Traditional use. In vitro juglone activity. | No meaningful human GI data. | Preclinical / traditional only. |
| Dandelion root | Traditional bitter / choleretic use. Animal data. | No meaningful human GI data. | Traditional only. |
| Herbal antimicrobials for SIBO (category) | Chedid et al., *Glob Adv Health Med* 2014: a retrospective chart review of commercial herbal products vs. rifaximin, with similar breath-test normalization. | Different products and formulas. | Category-level signal only. Doesn't transfer to this formula. |

**Mechanism takeaway (Step 5):** The claim that holds up best is that ginger supports gastric emptying and artichoke supports post-meal comfort (fullness, bloating). That fits the bloating and fullness segments in the research (Posts 15, 23 and 25). "Clears overgrowth", "breaks down biofilm" and "restarts the MMC" depend on in vitro or extrapolated evidence and on doses that can't be confirmed.

Background for the motility story: ACG Clinical Guideline on SIBO (Pimentel et al., *Am J Gastroenterol* 2020) and Deloose et al., "The migrating motor complex", *Nat Rev Gastroenterol Hepatol* 2012.

## 3. Safety items the page should address

Research objection: "Will it make me worse?" (bootstrap Part 10).

- **Gallstones / bile-duct obstruction.** Artichoke and dandelion stimulate bile flow. Traditional monographs list bile-duct obstruction as a contraindication, and gallstones as a reason to check with a doctor first.
- **Ragweed / daisy-family (Asteraceae) allergy.** Artichoke and dandelion are in this family. This conflicts with the page's **"Allergen-Free"** badge.
- **Blood thinners / bleeding risk.** Ginger, clove (eugenol) and oregano oil have antiplatelet activity, so warn people on blood thinners.
- **Pregnancy / nursing.** Black walnut (juglone) and concentrated oregano and clove oils aren't established as safe. The disclaimer covers this generally; consider saying it explicitly.
- **Diabetes medication.** Dandelion and ginger may modestly lower blood sugar.
- **Label inconsistency (already in README).** "NO … Preservatives" vs. potassium sorbate.

## 4. Current PDP copy vs. the research

### 4a. Audience mismatch

The page is built around **urgency / diarrhea**: the ticker ("mapping bathrooms"), the FAQ that calls urgency the "number-one reason", the Imodium review, and "Less Urgency & Cramping". The research archive centers on **bloating, distension, fullness, constipation / methane, food fear and appearance**. Urgency shows up only in Post 49's replies.

A **prokinetic** (speeds transit) also fits the constipation and fullness segments better than diarrhea-predominant urgency. Consider moving the lead from urgency to bloating ("wake up bloated, go to sleep bloated", "look pregnant by dinner").

### 4b. Claims that conflict with Part 14 or can't be substantiated

| Location | Current copy | Issue |
| --- | --- | --- |
| Title intro | "botanicals that clear overgrowth" | Disease (SIBO) claim. Part 14 #1. |
| Mechanism | "Clove breaks down the shield… Oregano clears out what's left… Ginger restarts… **Sequenced.**" | All six ingredients are in the same dropper at the same time, so nothing can act "in sequence". The biofilm and MMC steps are extrapolated from in vitro data. |
| Timeline | Weeks 1–2 clove works, weeks 3–4 oregano, months 2–3 ginger | Same problem: a made-up time course for ingredients taken together from day 1. |
| Compare table | "Liposomal absorption" | The label shows sunflower lecithin as an emulsifier. That doesn't make it a liposomal product. Remove unless the brand can document a liposomal process. |
| Compare table | "Restores gut motility", "Targets the root cause", "Clears bacteria & invaders" | Part 14 #1, #3, #10. "Others: ✗" is also an unsupported comparative claim. |
| Ingredients | "Clears parasites that standard tests can miss" | Disease claim, no human evidence. Also feeds health anxiety (Posts 40, 44). |
| Ingredients heading | "Supported by 10,000+ scientific studies" | Counts studies on ingredients in general, not this use or dose. Misleading to the "Where's the proof?" skeptic. |
| Benefits | "Clearer-Looking Skin*", "Steady Daily Energy*" | No support in the formula or the research. |
| FAQ: GLP-1 | "designed specifically to counter the slowed stomach emptying… during and after GLP-1 use" | Unsubstantiated, and a safety concern: GLP-1-related delayed gastric emptying should be managed by the prescriber. |
| FAQ: thyroid | "stimulates the receptors your gut needs… even when your metabolism has slowed" | Unsupported mechanism. Part 14 #10. |
| FAQ: Rifaximin (x2) | "goes after the root cause that Rifaximin leaves untouched" | Drug comparison and disease claim. Part 14 #1, #5. Already flagged in README. |
| FAQ: drops | "absorb right through your mouth" | No sublingual absorption data for these extracts. |
| Trust | "Allergen-Free", "Backed by Clinical Research" | See Asteraceae above. No clinical research exists on this formula. |

### 4c. Where the research supports stronger, honest copy

- **Lead with the deep desire, not the mechanism.** "I just want my life back" and "stop thinking about my stomach" (Parts 2.2 and 9.10) are more powerful than biofilm, and they don't need medical claims.
- **Answer "I've tried everything" honestly.** Acknowledge the cycle (Part 3.3) and explain what is different, using only what holds up: concentrated ginger plus artichoke for post-meal fullness and bloating. Then set realistic expectations.
- **Treat safety and transparency as selling points** for the sophisticated, burned-before segment (Part 11.2). Disclose per-ingredient amounts if the brand will, add the cautions in section 3, and add a "who shouldn't take this" note.
- **Food-fear and appearance outcomes** ("finish dinner without checking your stomach", "wear what you planned to wear") are concrete, emotional and claim-safe.
- **Reviews.** The current reviews are urgency- and Rifaximin-heavy. If real reviews mention bloating or fullness, feature those. Only publish real, representative reviews.

## 5. Open questions for the brand

1. Per-ingredient amounts in the 800 mg blend, and recommended servings per day.
2. Extract ratios and plant parts for artichoke and dandelion. Eugenol percentage for the clove oil.
3. Any finished-product testing (third-party CoA) or customer survey data.
4. The basis for "liposomal", "10,000+ studies" and "100,000+ customers".
5. Whether the brand has legal review guidance on structure/function vs. disease claims.
