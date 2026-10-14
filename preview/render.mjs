// Local preview: renders templates/product.veltia-drops.json with mock product data
// into preview/index.html using LiquidJS + stubs for Shopify-only filters/tags.
// Not part of the Shopify theme. Run: cd preview && npm install && npm run build
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Liquid, Tag } from 'liquidjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const read = (p) => readFileSync(path.join(root, p), 'utf8');

const engine = new Liquid({
  root: [path.join(root, 'sections'), path.join(root, 'snippets')],
  partials: path.join(root, 'snippets'),
  extname: '.liquid',
});

/* ---------- Shopify tag stubs ---------- */

engine.registerTag('schema', class extends Tag {
  constructor(token, remainTokens, liquid) {
    super(token, remainTokens, liquid);
    while (remainTokens.length) {
      const t = remainTokens.shift();
      if (t.name === 'endschema') return;
    }
  }
  render() { return ''; }
});

engine.registerTag('form', class extends Tag {
  constructor(token, remainTokens, liquid) {
    super(token, remainTokens, liquid);
    this.args = token.args;
    this.tpls = [];
    const stream = liquid.parser.parseStream(remainTokens)
      .on('tag:endform', () => stream.stop())
      .on('template', (tpl) => this.tpls.push(tpl))
      .on('end', () => { throw new Error('form not closed'); });
    stream.start();
  }
  * render(ctx, emitter) {
    const idExpr = (this.args.match(/id:\s*([\w.]+)/) || [])[1];
    const id = idExpr ? yield this.liquid.evalValue(idExpr, ctx) : '';
    const cls = (this.args.match(/class:\s*'([^']*)'/) || [])[1] || '';
    emitter.write(`<form method="post" action="/cart/add" id="${id}" class="${cls}" accept-charset="UTF-8" enctype="multipart/form-data" novalidate data-pdp-form><input type="hidden" name="form_type" value="product">`);
    yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter);
    emitter.write('</form>');
  }
});

/* ---------- Shopify filter stubs ---------- */

const kw = (args) => Object.fromEntries(args.filter(Array.isArray));
const attrs = (o) => Object.entries(o)
  .filter(([k, v]) => v !== '' && v != null && !['widths', 'sizes'].includes(k))
  .map(([k, v]) => `${k}="${String(v).replace(/"/g, '&quot;')}"`).join(' ');

engine.registerFilter('money', (cents) => `$${(Number(cents || 0) / 100).toFixed(2)}`);
engine.registerFilter('image_url', (img) => (img && img.src) || img || '');
engine.registerFilter('image_tag', (src, ...args) => {
  const o = kw(args);
  return `<img src="${src}" ${attrs({ alt: '', ...o })}>`;
});
engine.registerFilter('placeholder_svg_tag', (_, cls) => `<svg class="${cls || ''}" viewBox="0 0 10 10"></svg>`);
engine.registerFilter('asset_url', (name) => `ASSET:${name}`);
engine.registerFilter('stylesheet_tag', () => '');
engine.registerFilter('structured_data', () => '{}');
engine.registerFilter('media_tag', () => '');
engine.registerFilter('video_tag', () => '');
engine.registerFilter('payment_button', () => '');
engine.registerFilter('payment_type_svg_tag', (type, ...args) => {
  const label = { visa: 'VISA', master: 'MC', american_express: 'AMEX', discover: 'DISC', paypal: 'PayPal', apple_pay: 'Pay', google_pay: 'G Pay', shopify_pay: 'Shop' }[type] || type;
  return `<svg class="${kw(args).class || ''}" viewBox="0 0 38 24" role="img" aria-label="${type}"><rect x=".5" y=".5" width="37" height="23" rx="3" fill="#fff" stroke="#e2d7c9"/><text x="19" y="15.5" font-size="8" font-weight="700" font-family="Arial" text-anchor="middle" fill="#3e2617">${label}</text></svg>`;
});

/* ---------- Mock data (mirrors the live product: 1 variant at $44.99 + bundle tiers, no subscription plan yet) ---------- */

// Upload-ready images live in /images; the same file names are what to upload to Shopify.
const img = (name, alt = '') => ({ src: `../images/${name}.webp`, alt });
const media = ['veltia-bottle', 'product-lifestyle', 'product-method', 'product-flatlay', 'product-dropper', 'bundle-3', 'bundle-5'].map((name, n) => ({ id: 100 + n, media_type: 'image', alt: 'Veltia Labs Black Walnut Liquid Drops', ...img(name), preview_image: img(name) }));

const plans = [
  { id: 6644728051, name: 'Every 28 days · 20% off', price_adjustments: [{ value_type: 'percentage', value: 20 }] },
];
const variant = {
  id: 50660850827507, title: 'Default Title', price: 4499, compare_at_price: null, available: true, options: ['Default Title'],
  featured_image: null, featured_media: null, metafields: { custom: {} },
  inventory_management: 'shopify', inventory_quantity: 120,
  selling_plan_allocations: [],
};

const product = {
  id: 9812695154931, title: 'Black Walnut Liquid Drops', vendor: 'Veltia Labs',
  media, featured_image: media[0], featured_media: media[0],
  variants: [variant], options: ['Title'],
  options_with_values: [{ name: 'Title', values: ['Default Title'], selected_value: 'Default Title' }],
  has_only_default_variant: true,
  selected_variant: null,
  selected_or_first_available_variant: variant,
  selling_plan_groups: [],
  requires_selling_plan: false,
  description: '<p>Product description from Shopify admin.</p>',
  metafields: { reviews: { rating: { value: null }, rating_count: { value: null } }, custom: {} },
};

const globals = {
  product,
  shop: { money_format: '${{amount}}', enabled_payment_types: ['visa', 'master', 'american_express', 'discover', 'paypal', 'apple_pay', 'google_pay', 'shopify_pay'] },
  routes: { cart_url: '/cart', cart_add_url: '/cart/add', root_url: '/' },
};

// Images the merchant sets in the theme editor (image_picker settings), by section and block type.
// Only images that belong to the new brand. Everything else falls back to placeholders until real assets exist.
const sectionImages = {
  problem: { image: img('problem-gut') },
  mechanism: { image: img('mechanism-steps') },
  compare: { us_image: img('veltia-bottle') },
  risk: { seal: img('guarantee-seal'), image: img('product-lifestyle') },
};
const ingredientImages = ['ingr-garlic', 'ingr-oregano', 'ingr-black-walnut', 'ingr-wormwood', 'ingr-pau-darco', 'ingr-pumpkin-seed', 'ingr-soursop'];
const blockImages = {
  ingredient: (i) => ({ image: img(ingredientImages[i]) }),
  guarantee: () => ({ image: img('guarantee-seal') }),
  gifts: () => ({ gift_2_image: img('gift-bloat-guide'), gift_3_image: img('gift-priority') }),
  variant_picker: () => ({ tier_1_image: img('veltia-bottle'), tier_2_image: img('bundle-3'), tier_3_image: img('bundle-5') }),
};

/* ---------- Build sections from the JSON template ---------- */

const template = JSON.parse(read('templates/product.veltia-drops.json'));
const schemaOf = (type) => {
  const src = read(`sections/${type}.liquid`);
  return JSON.parse(src.split('{% schema %}')[1].split('{% endschema %}')[0]);
};
const defaults = (settings = []) => Object.fromEntries(settings.filter((s) => 'id' in s).map((s) => [s.id, s.default ?? '']));

let html = '';
for (const key of template.order) {
  const def = template.sections[key];
  const schema = schemaOf(def.type);
  const settings = { ...defaults(schema.settings), ...def.settings, ...(sectionImages[key] || {}) };
  const blocks = (def.block_order || []).map((id, i) => {
    const b = def.blocks[id];
    const bs = schema.blocks.find((x) => x.type === b.type) || {};
    const s = { ...defaults(bs.settings), ...b.settings, ...(blockImages[b.type] ? blockImages[b.type](i) : {}) };
    return { id, type: b.type, settings: s, shopify_attributes: '' };
  });
  const section = { id: key, settings, blocks };
  const out = await engine.renderFile(def.type, { ...globals, section });
  html += `<div id="shopify-section-${key}" class="shopify-section">${out}</div>\n`;
}

html = html.replace(/<script src="ASSET:pdp-gut-complex\.js" defer="defer"><\/script>/g, '');
const css = read('assets/pdp-gut-complex.css');
const js = read('assets/pdp-gut-complex.js');

const page = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Veltia Labs PDP</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  body { margin: 0; background: #fff; }
  .preview-header { display: flex; align-items: center; justify-content: center; height: 60px; border-bottom: 1px solid #e9dfd2; font: 600 22px/1 Fraunces, Georgia, serif; letter-spacing: .18em; color: #3e2617; background: #fff; }
  .preview-header span { font: 500 11px/1 Inter, sans-serif; letter-spacing: .1em; color: #9a8a7c; margin-left: 10px; }
  .preview-note { font: 12px/1.4 Inter, system-ui, sans-serif; text-align: center; padding: 6px 16px; background: #fff7df; color: #6b5310; }
${css}
</style>
</head>
<body>
<p class="preview-note">Preview of the theme sections with the Veltia images from /images. Reviews appear once a reviews app is connected.</p>
<header class="preview-header">VELTIA LABS</header>
${html}
<script>
// Preview only: fake cart endpoint so Add to cart can be clicked.
const _fetch = window.fetch;
window.fetch = (url, opts) => String(url).startsWith('/cart')
  ? new Promise((r) => setTimeout(() => r(new Response(JSON.stringify({ id: 1, item_count: 1 }), { status: 200 })), 600))
  : _fetch(url, opts);
document.querySelectorAll('pdp-product').forEach((el) => { el.dataset.afterAdd = 'stay'; });
</script>
<script>
${js}
</script>
</body>
</html>
`;
writeFileSync(path.join(here, 'index.html'), page);
console.log('wrote preview/index.html', page.length, 'bytes');
