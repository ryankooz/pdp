# Gut Complex PDP: Shopify theme sections

A conversion-focused product page for the Gut Complex drops rebrand, built as Online Store 2.0 sections that drop into any modern Shopify theme (Dawn, Sense, Refresh, Impulse, etc.). Every section is editable in the theme editor.

Layout follows the current page: sale bar + review ticker → gallery with callouts → rating, headline, benefit grid, stock bar, price → **Buy 1 / Buy 2 Get 1 Free / Buy 3 Get 3 Free** bundle cards → unlockable free gifts → delivery date → Subscribe & Save → Add to Cart → payments, social proof, 90-day guarantee, FAQ → Why trust us → the problem (biofilm) → the mechanism → 6 ingredient flip cards → reviews → FDA disclaimer.

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
  pdp-disclaimer.liquid         FDA disclaimer
snippets/
  pdp-gallery.liquid, pdp-icon.liquid
assets/
  pdp-gut-complex.css, pdp-gut-complex.js   (no dependencies, scoped under .pdp-scope)
templates/
  product.gut-complex.json      the page, pre-filled with copy
preview/                        local preview only. Do not upload.
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
| Bundles | Add one option, e.g. **Bundle**, with variants `Buy 1`, `Buy 2 Get 1 Free`, `Buy 3 Get 3 Free`. Set each variant's **price** and **compare-at price** (e.g. $34.99/$59.99, $54.99/$179.97, $79.99/$359.94). Savings and "Save $X" text are calculated from these. |
| Bottles per bundle | Set *Bundle picker → Bottles per variant* to `1,3,6` (used for the per-bottle price), or add a variant metafield `custom.bottle_count` (integer). |
| Variant images | Assign each variant an image (1 bottle, 3 bottles, 6 bottles). The bundle card thumbnail and gallery switch to it. |
| Subscribe & Save | Install a subscription app (Shopify Subscriptions, Recharge, Skio, Loop…) and add a selling plan to the product. The toggle and its savings % appear automatically. |
| Star rating | Your reviews app (Judge.me, Okendo, Yotpo, Loox, Stamped) syncs `reviews.rating` / `reviews.rating_count`. Add the app's review widget as an app block inside the **Gut Complex: reviews** section. |
| Free gifts | The gift tiles are display only. Fulfill the gifts with an automatic discount or a gift-with-purchase app, and set *Gift N unlocks at variant #* to match. |
| Sale countdown | Set *Sale end* to a real date. When it passes, the bar hides itself. |
| After add to cart | *Behavior → After add to cart*: cart page (default), checkout, or stay on page. "Stay" fires `pdp:added` and `cart:refresh` events so a theme cart drawer can open. |

## Before launch: content to replace

- **Brand name.** Copy uses "us" / "our" instead of the old brand name. Update the logo and any copy once the new name is final.
- **Images.** Gallery and variant images come from the product. Upload images for the problem section, mechanism section, ingredient cards, UGC strip, avatars and the Supplement Facts panel.
- **Ingredients.** The six names were read off a small screenshot of the current page. Confirm them against the label and fill in each card's *Dose per serving*.
- **Reviews and ticker quotes.** These hold placeholders and one review transcribed from the current page. Only publish real customer reviews.
- **Trust badges.** Keep only the claims you can back up (Made in USA, third-party tested, GMP, etc.).
- **Stock bar.** Either turn on *Calculate from real inventory* or remove the block. A fixed "88% sold" is a scarcity claim the FTC treats as deceptive if it isn't true.

## Compliance notes

Supplement copy is held to FDA structure/function rules: no claims to diagnose, treat, cure or prevent disease. Benefit claims are marked `*` and tied to the disclaimer section. Have someone review these before launch:

- The **Rifaximin** FAQ compares the product to a prescription antibiotic. The answer was written to avoid a drug claim, but you could also remove the question.
- "Antimicrobial", "clears bacteria & invaders" and "clear overgrowth" can be read as disease/SIBO claims. Softer alternatives: "supports a balanced gut microbiome", "helps maintain healthy gut flora".

## Local preview

```bash
cd preview && npm install && npm run build   # writes preview/index.html
```

Renders the real Liquid with mock product data (LiquidJS plus stubs for Shopify-only filters), so layout changes can be checked without a store.
