// Local preview: renders templates/product.gut-complex.json with mock product data
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
  const label = { visa: 'VISA', master: 'MC', american_express: 'AMEX', paypal: 'PayPal', apple_pay: 'Pay', google_pay: 'G Pay', shopify_pay: 'Shop' }[type] || type;
  return `<svg class="${kw(args).class || ''}" viewBox="0 0 38 24" role="img" aria-label="${type}"><rect x=".5" y=".5" width="37" height="23" rx="3" fill="#fff" stroke="#d7dbd6"/><text x="19" y="15.5" font-size="8" font-weight="700" font-family="Arial" text-anchor="middle" fill="#1d3a28">${label}</text></svg>`;
});

/* ---------- Mock data ---------- */

const image = (n, dir = 'bottle') => ({ id: 100 + n, src: `img/${dir}-${n}.svg`, alt: '', media_type: 'image', preview_image: { src: `img/${dir}-${n}.svg` } });
const media = [1, 2, 3, 4].map((n) => image(n));
media.forEach((m) => { m.preview_image = { src: m.src }; });

const plans = [
  { id: 501, name: 'Every 30 days', price_adjustments: [{ value_type: 'percentage', value: 15 }] },
  { id: 502, name: 'Every 60 days', price_adjustments: [{ value_type: 'percentage', value: 15 }] },
];
const mkVariant = (id, title, price, compare, img) => ({
  id, title, price, compare_at_price: compare, available: true, options: [title],
  featured_image: img, featured_media: { id: img.id }, metafields: { custom: {} },
  inventory_management: 'shopify', inventory_quantity: 120,
  selling_plan_allocations: plans.map((p) => ({ selling_plan: p, price: Math.round(price * 0.85) })),
});
const variants = [
  mkVariant(1001, 'Buy 1', 3499, 5999, media[0]),
  mkVariant(1002, 'Buy 2 Get 1 Free', 5499, 17997, media[1]),
  mkVariant(1003, 'Buy 3 Get 3 Free', 7999, 35994, media[2]),
];

const product = {
  id: 1, title: 'Gut Complex Drops', vendor: 'Brand',
  media, featured_image: media[0], featured_media: media[0],
  variants, options: ['Bundle'],
  options_with_values: [{ name: 'Bundle', values: variants.map((v) => v.title), selected_value: variants[0].title }],
  has_only_default_variant: false,
  selected_variant: null,
  selected_or_first_available_variant: variants[0],
  selling_plan_groups: [{ selling_plans: plans }],
  requires_selling_plan: false,
  description: '<p>Product description from Shopify admin.</p>',
  metafields: { reviews: { rating: { value: { rating: 4.8, scale_max: 5 } }, rating_count: { value: null } }, custom: {} },
};

const globals = {
  product,
  shop: { money_format: '${{amount}}', enabled_payment_types: ['visa', 'master', 'american_express', 'paypal', 'apple_pay', 'google_pay'] },
  routes: { cart_url: '/cart', cart_add_url: '/cart/add', root_url: '/' },
};

// Preview-only images for image_picker settings (the merchant uploads real ones in the theme editor)
const previewImages = {
  problem: { image: { src: 'img/gut.svg', alt: '' } },
  mechanism: { image: { src: 'img/bottle-3.svg', alt: '' } },
};

/* ---------- Build sections from the JSON template ---------- */

const template = JSON.parse(read('templates/product.gut-complex.json'));
const schemaOf = (type) => {
  const src = read(`sections/${type}.liquid`);
  return JSON.parse(src.split('{% schema %}')[1].split('{% endschema %}')[0]);
};
const defaults = (settings = []) => Object.fromEntries(settings.filter((s) => 'id' in s).map((s) => [s.id, s.default ?? '']));

let html = '';
for (const key of template.order) {
  const def = template.sections[key];
  const schema = schemaOf(def.type);
  const settings = { ...defaults(schema.settings), ...def.settings, ...(previewImages[key] || {}) };
  const blocks = (def.block_order || []).map((id, i) => {
    const b = def.blocks[id];
    const bs = schema.blocks.find((x) => x.type === b.type) || {};
    const s = { ...defaults(bs.settings), ...b.settings };
    if (b.type === 'ingredient') s.image = { src: `img/ingredient-${i + 1}.svg` };
    if (b.type === 'ugc') s.image = { src: `img/bottle-${(i % 4) + 1}.svg`, alt: '' };
    if (b.type === 'social_proof') ['avatar_1', 'avatar_2', 'avatar_3', 'avatar_4'].forEach((a) => { s[a] = { src: 'img/avatar.svg' }; });
    if (b.type === 'review') s.avatar = { src: 'img/avatar.svg' };
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
<title>Gut Complex PDP</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  body { margin: 0; background: #fff; }
  .preview-header { display: flex; align-items: center; justify-content: center; height: 60px; border-bottom: 1px solid #e3e6e1; font: 600 22px/1 Fraunces, Georgia, serif; letter-spacing: .18em; color: #1d3a28; background: #fff; }
  .preview-note { font: 12px/1.4 Inter, system-ui, sans-serif; text-align: center; padding: 6px 16px; background: #fff7df; color: #6b5310; }
${css}
</style>
</head>
<body>
<p class="preview-note">Preview with mock product data. In Shopify, images, prices, bundles and subscriptions come from your product.</p>
<header class="preview-header">BRAND</header>
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
