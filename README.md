# Veltia Labs PDP: Shopify theme sections

The product page for **Veltia Labs Black Walnut Liquid Drops**: an herbal digestive supplement with black walnut, wormwood, soursop, pumpkin seed, pau d'arco, garlic and oregano in a 60 mL dropper bottle. It's built as Online Store 2.0 sections that drop into any modern Shopify theme (Dawn, Sense, Refresh, Impulse, etc.), and every section is editable in the theme editor.

The layout follows the competitor page it was modeled on, with the copy rewritten around this product's own mechanism, **the Shield Breaker**: garlic helps break down the protective biofilm layer gut bacteria hide behind, so oregano, wormwood and black walnut can reach what's underneath. The research behind it is in `research/unique-mechanisms.md`.

Page order:

sale bar → gallery → headline, benefit grid, price → **Buy 1 / Buy 2 Get 1 Free / Buy 3 Get 2 Free** bundle cards (Kaching-style) → unlockable free gifts → delivery date → Subscribe & Save → Add to Cart → payments, guarantee, 7 FAQs → Why trust us → the problem (the biofilm shield) → the Shield Breaker Method → 7 ingredient flip cards + Supplement Facts → reviews → what to expect, week by week → comparison table → 90-day risk-free trial → FAQ (incl. who shouldn't take it) → disclaimer.

Colors come from the bottle: banner brown `#7A4A2A`, espresso `#3E2617`, amber `#C8873A`, label cream `#F6EEE2`.

## Files

```
sections/
  main-pdp-gut-complex.liquid   gallery + buy box + sticky add-to-cart (all blocks reorderable)
  pdp-promo-bar.liquid          sale countdown + optional review ticker
  pdp-why-trust.liquid          4 trust seals + optional "free from" checklist
  pdp-problem.liquid            dark "why your bloating keeps coming back" section
  pdp-mechanism.liquid          "The Shield Breaker Method" steps + image
  pdp-ingredients.liquid        tap-to-flip ingredient cards + Supplement Facts
  pdp-reviews.liquid            UGC strip, featured reviews, reviews-app block
  pdp-timeline.liquid           "What to expect, week by week"
  pdp-compare.liquid            us-vs-typical-supplements comparison table
  pdp-risk-free.liquid          90-day risk-free trial banner
  pdp-faq.liquid                FAQ (with FAQPage structured data)
  pdp-disclaimer.liquid         FDA disclaimer
snippets/
  pdp-bundles.liquid, pdp-gallery.liquid, pdp-icon.liquid
assets/
  pdp-gut-complex.css, pdp-gut-complex.js   (no dependencies, scoped under .pdp-scope)
templates/
  product.veltia-drops.json     the page, pre-filled with copy
images/                         upload-ready product + section images (see "Images" below)
preview/                        local preview only. Do not upload.
research/                       customer research, mechanism work, competitor copies. Do not upload.
```

File names still say `gut-complex` because they're internal. Section names in the theme editor read "Veltia: …".

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

1. **Products → Black Walnut Liquid Drops → Theme template**: choose `veltia-drops`.
2. **Online Store → Customize**, open the product page and add images, logo and reviews.

## Set up the product in Shopify

| What | How |
| --- | --- |
| Bundles (Kaching) | The bundle cards are quantity tiers on a single variant: Buy 1 = 1 unit at $44.99, Buy 2 Get 1 Free = 3 units at $69.99, Buy 3 Get 2 Free = 5 units at $99.99 (product price $44.99). If you change them, update *Bundle picker → Bundle 1–3*, the product price and the bundle discount together, and keep the sale bar's "up to X%" true. Each card adds that many units to the cart; **Kaching (or an automatic discount) must apply the actual discount**. Without that, checkout charges full price × quantity. Alternatively, add Kaching's own app block and remove the Bundle picker block. |
| Variant bundles (alternative) | For a multi-variant product, the picker shows one card per variant using its price and compare-at price. |
| Variant images | Assign each variant an image (1 bottle, 3 bottles, 5 bottles). The bundle card thumbnail and gallery switch to it. |
| Subscribe & Save | Uses the product's selling plan (e.g. 20% off every 28 days). The toggle, savings % and subscribe prices are calculated from it. It's unchecked by default (*Behavior → Pre-check Subscribe & Save*); auto-renewal laws generally require shoppers to opt in themselves. |
| Star rating | Hidden until a reviews app (Judge.me, Okendo, Yotpo, Loox, Stamped) syncs `reviews.rating` / `reviews.rating_count`. Add the app's review widget as an app block inside the **Veltia: reviews** section. |
| Free gifts | Free Shipping (all bundles), Bloat Reset Guide (Digital) (bundle 2+), Top Priority Order + Expedited Shipping (bundle 3). The tiles only display the gifts; Kaching's progressive gifts add them to the cart. **The guide has to exist before you advertise it.** |
| Sale countdown | Set *Sale end* to a real date. When it passes, the bar hides itself. |
| After add to cart | *Behavior → After add to cart*: cart page (default), checkout, or stay on page. "Stay" fires `pdp:added` and `cart:refresh` events so a theme cart drawer can open. |

## Before launch

**Confirm with the supplier** (the copy depends on these):

- [ ] Full Supplement Facts panel: amount of each botanical per serving, serving size, liquid base (glycerin, alcohol or oil). Upload it as *Ingredients → Supplement Facts panel image*.
- [x] Garlic form and allicin: supplier confirmed **stabilized allicin, 10+ mg per serving, stable in the bottle**. The page now says "at least 10 mg" ("Why garlic?" FAQ, garlic card, comparison table). Keep the supplier's COA on file, and make sure the label's serving size matches "one full dropper" and its allicin figure is 10 mg or more.
- [ ] Oregano carvacrol %, black walnut juglone %. Update the "Key compound" field on each ingredient card to match the label.
- [ ] Taste and directions. The FAQ says "earthy and bitter" and "start with a few drops, work up to a full dropper". Match the label's directions.
- [ ] Allergen and free-from facts (gluten-free, vegan, sugar-free, etc.). The "free from" checklist was removed until these are confirmed; re-add them as *Why trust → Free-from item* blocks.
- [ ] Any third-party testing, GMP or made-in claims. Only add those trust badges with paperwork to back them.

**Content to add:**

- [ ] **Images.** Upload the files in `images/` and set them as listed under "Images" below. The only slot still empty is the Supplement Facts panel, which must be the real label, not a generated one.
- [ ] **Logo** in the theme header.
- [ ] **Reviews.** The page ships with **no testimonials**, no ticker quotes and no customer counts. Connect a reviews app and only publish real customer reviews; don't present AI-generated photos as customer photos. Once you have real quotes, add them to the sale bar ticker as *Quote* blocks.
- [ ] **Guarantee terms.** The page promises a 90-day money-back guarantee in several places. Make sure your refund policy says the same.
- [ ] **Prices and bundles** (see above).
- [ ] **Sale end date.**

## Images

Everything in `images/` except `veltia-bottle.webp` (your original photo) was generated with GPT Image 2 on Higgsfield. The bottle shots used your photo as the reference so the label stays accurate. They're WebP, max 1600 px; the two badges have transparent backgrounds.

| File | Where it goes |
| --- | --- |
| `carousel-1-hero.webp` … `carousel-8-guarantee.webp` | Product media, in number order (hero, benefits, Shield Breaker method, how to take it, timeline, vs. others, testimonial, guarantee), followed by `bundle-3.webp` and `bundle-5.webp`. Made with GPT Image 2.5 on Higgsfield from `veltia-bottle.webp`; the testimonial quote is Rachel T.'s own words. |
| `veltia-bottle.webp`, `product-lifestyle.webp`, `product-method.webp`, `product-flatlay.webp`, `product-dropper.webp`, `bundle-3.webp`, `bundle-5.webp` | Product media in Shopify admin, in that order |
| `veltia-bottle.webp` / `bundle-3.webp` / `bundle-5.webp` | *Bundle picker → Bundle 1 / 2 / 3 image* |
| `gift-bloat-guide.webp`, `gift-priority.webp` | *Free gifts → Gift 2 / Gift 3 image* |
| `guarantee-seal.webp` | *Guarantee → Seal image* and *Risk-free → Seal* |
| `problem-gut.webp` (alternate: `problem-gut-alt.webp`) | *Problem → Image* |
| `mechanism-steps.webp` (3-panel: hidden, opened, cleared) | *Mechanism → Image* |
| `ingr-garlic.webp`, `ingr-oregano.webp`, `ingr-black-walnut.webp`, `ingr-wormwood.webp`, `ingr-pau-darco.webp`, `ingr-pumpkin-seed.webp`, `ingr-soursop.webp` | *Ingredients → each card's image*, in that order |
| `veltia-bottle.webp` | *Comparison → Our column image* |
| `product-lifestyle.webp` | *Risk-free → Image* |

Before running ads, check each image's label text at full size: AI can garble small print. The `product-method.webp` infographic shows mechanism wording; keep it consistent with the page's `*` claims.

## Compliance notes

Supplement copy must stay within FDA structure/function rules: no claims to diagnose, treat, cure or prevent disease. Benefit claims are marked `*` and tied to the disclaimer. Notes for whoever reviews it:

- **Biofilm claims are lab-based.** The page says "lab studies show" for garlic and doesn't call anything clinically proven. Keep it that way.
- **No SIBO, parasite or drug claims.** Black walnut, wormwood and pumpkin seed are classic "parasite cleanse" herbs, but the copy deliberately describes them only by traditional use. Don't add "kills parasites" language.
- **Safety.** Wormwood (thujone), pau d'arco, garlic and soursop all carry cautions. The bottom FAQ "Who should not take these drops?" covers pregnancy, nursing, under 18, blood thinners and medication, seizure disorders, liver, kidney and gallbladder conditions, and daisy/ragweed allergy. The timeline tells people to talk to their provider about how long to continue. Match the label's warnings.
- **No relapse-prevention promise.** There's no ingredient that restores gut motility, so the copy doesn't promise the bloating won't come back.

## Local preview

```bash
cd preview && npm install && npm run build   # writes preview/index.html
```

Renders the real Liquid with mock product data (LiquidJS plus stubs for Shopify-only filters), so layout changes can be checked without a store. Grey boxes are image slots.
