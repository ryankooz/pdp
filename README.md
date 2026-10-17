# Gut Complex PDP: Shopify theme sections

A conversion-focused product page for the Gut Complex drops rebrand, built as Online Store 2.0 sections that drop into any modern Shopify theme (Dawn, Sense, Refresh, Impulse, etc.). Every section is editable in the theme editor.

Layout and content follow the current live page, with all copy reworded (same points and meaning, new wording, no old brand name):

sale bar + review ticker → gallery → rating, headline, benefit grid, stock bar, price → **Buy 1 / Buy 2 Get 1 Free / Buy 3 Get 2 Free** bundle cards (Kaching-style) → unlockable free gifts → delivery date → Subscribe & Save → Add to Cart → payments, social proof, guarantee, 7 FAQs → Why trust us → the problem (biofilm) → the Biofilm Formula → 6 ingredient flip cards + Supplement Facts → reviews → week-by-week timeline → comparison table → 90-day risk-free trial → FAQ → disclaimer.

## Files

```
sections/
  main-pdp-gut-complex.liquid   gallery + buy box + sticky add-to-cart (all blocks reorderable)
  pdp-promo-bar.liquid          sale countdown + scrolling review ticker
  pdp-why-trust.liquid          4 trust seals + "free from" checklist
  pdp-problem.liquid            dark "why your gut never resets" section
  pdp-mechanism.liquid          "The Biofilm Formula" steps + image
  pdp-ingredients.liquid        tap-to-flip ingredient cards + Supplement Facts
  pdp-reviews.liquid            UGC strip, featured reviews, reviews-app block
  pdp-timeline.liquid           "What customers notice, week by week"
  pdp-compare.liquid            us-vs-others comparison table
  pdp-risk-free.liquid          90-day risk-free trial banner
  pdp-faq.liquid                FAQ (with FAQPage structured data)
  pdp-disclaimer.liquid         FDA disclaimer
snippets/
  pdp-bundles.liquid, pdp-gallery.liquid, pdp-icon.liquid
assets/
  pdp-gut-complex.css, pdp-gut-complex.js   (no dependencies, scoped under .pdp-scope)
templates/
  product.gut-complex.json      the page, pre-filled with copy
preview/                        local preview only. Do not upload.
research/                       customer-research swipe file and hook puller (not part of the theme, see research/README.md)
```

## Install

**Option A: Shopify CLI (recommended)**

```bash
# from your theme folder (shopify theme pull first if needed)
cp -r path/to/pdp/{sections,snippets,assets,templates} .
shopify theme dev          # preview locally against your store
shopify theme push --unpublished   # push to a new draft theme to review
```

**Option B: Admin code editor.** Go to *Online Store → Themes → … → Edit code*. In each folder, click *Add a new file* and paste in the contents of the matching file above.

Then:

1. **Products → Gut Complex Drops → Theme template**: choose `gut-complex`.
2. **Online Store → Customize**, open the product page and edit copy, images and colors.

## Set up the product in Shopify

| What | How |
| --- | --- |
| Bundles (Kaching) | The product has a single variant ($43.74, compare-at $59.99), and bundles are quantity tiers. *Bundle picker → Bundle 1–3* hold the tiers copied from Kaching: Buy 1 = 1 unit at $43, Buy 2 Get 1 Free = 3 units at $67.99, Buy 3 Get 2 Free = 5 units at $98.99, rounded up to .99. Each card adds that many units to the cart; **Kaching (or an automatic discount) must apply the actual discount**. Without that, checkout charges full price × quantity. Alternatively, add Kaching's own app block to the buy box and remove the Bundle picker block. |
| Variant bundles (alternative) | For a multi-variant product, the picker shows one card per variant using its price and compare-at price. |
| Variant images | Assign each variant an image (1 bottle, 3 bottles, 6 bottles). The bundle card thumbnail and gallery switch to it. |
| Subscribe & Save | Uses the product's selling plan (currently "Subscribe and Save", 20% off, every 28 days). The toggle, savings % and subscribe prices ($34.99 / $54.99 / $79.99) are calculated from it. It is unchecked by default (*Behavior → Pre-check Subscribe & Save*); auto-renewal laws generally require shoppers to opt in themselves. |
| Star rating | Your reviews app (Judge.me, Okendo, Yotpo, Loox, Stamped) syncs `reviews.rating` / `reviews.rating_count`. Add the app's review widget as an app block inside the **Gut Complex: reviews** section. |
| Free gifts | Free Shipping (all bundles), Gut Flush & Motility Blueprint (bundle 2+), Top Priority Order + Expedited Shipping (bundle 3). The tiles only display the gifts; Kaching's progressive gifts add them to the cart. |
| Sale countdown | Set *Sale end* to a real date. When it passes, the bar hides itself. |
| After add to cart | *Behavior → After add to cart*: cart page (default), checkout, or stay on page. "Stay" fires `pdp:added` and `cart:refresh` events so a theme cart drawer can open. |

## Before launch: content to replace

- **Brand name and logo.** Copy says "our formula" / "these drops" instead of a brand name.
- **Images.** Gallery, ingredient, UGC and section images still show the old label. Upload rebranded versions (product media in Shopify admin, section images in the theme editor).
- **Reviews and ticker quotes.** Copied from the live page word for word, except the old brand name, which is replaced with "these drops". Only publish reviews from real customers, and don't present AI-generated photos as customer photos.
- **Star rating.** The rating line falls back to 4.8 until a reviews app syncs `reviews.rating`. Set *Fallback rating* to 0 to hide it until then.
- **Stock bar.** Either turn on *Calculate from real inventory* or remove the block. A fixed "93% sold" is a scarcity claim the FTC treats as deceptive if it isn't true.
- **Sale countdown.** Set *Sale end* to the real end date.
- **Label check.** The Supplement Facts panel says "NO … Preservatives", but the other ingredients list potassium sorbate, which is a preservative. Fix this on the new label.

## Compliance notes

Supplement copy is held to FDA structure/function rules: no claims to diagnose, treat, cure or prevent disease. Benefit claims are marked `*` and tied to the disclaimer section. Have someone review these before launch:

- The **Rifaximin** FAQ compares the product to a prescription antibiotic. The answer was written to avoid a drug claim, but you could also remove the question.
- "Antimicrobial", "clears bacteria & invaders" and "clear overgrowth" can be read as disease/SIBO claims. Softer alternatives: "supports a balanced gut microbiome", "helps maintain healthy gut flora".

## Local preview

```bash
cd preview && npm install && npm run build   # writes preview/index.html
```

Renders the real Liquid with mock product data (LiquidJS plus stubs for Shopify-only filters), so layout changes can be checked without a store.
