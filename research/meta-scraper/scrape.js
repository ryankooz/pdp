// Meta Ads Library scraper: node scrape.js out.json "phrase1" "phrase2" ...
// Env: STATUS=active|all, TYPE=keyword_exact_phrase|keyword_unordered, SCROLLS=n
const { chromium } = require('playwright');
const fs = require('fs');
const STATUS = process.env.STATUS || 'active', TYPE = process.env.TYPE || 'keyword_exact_phrase';
const SCROLLS = +(process.env.SCROLLS || 12);
(async () => {
  const [out, ...phrases] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36', locale: 'en-US', viewport: { width: 1400, height: 1800 } });
  const all = {};
  for (const ph of phrases) {
    const q = TYPE === 'keyword_exact_phrase' ? `"${ph}"` : ph;
    const url = `https://www.facebook.com/ads/library/?active_status=${STATUS}&ad_type=all&country=US&q=${encodeURIComponent(q)}&search_type=${TYPE}&media_type=${process.env.MEDIA || "all"}${process.env.EXTRA || ""}`;
    const p = await ctx.newPage();
    try {
      await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await p.waitForTimeout(12000);
      for (let i = 0; i < SCROLLS; i++) { for (let k = 0; k < 10; k++) await p.mouse.wheel(0, 600); await p.waitForTimeout(2200); }
      const res = await p.evaluate(() => {
        const total = (document.body.innerText.match(/~?([\d,]+) results?/) || [])[1] || '0';
        const nodes = [...document.querySelectorAll('div, span')].filter(e => e.childElementCount === 0 && /^Library ID: \d+/.test(e.textContent.trim()));
        const ads = [];
        for (const n of nodes) {
          let c = n;
          for (let i = 0; i < 14 && c.parentElement; i++) {
            const par = c.parentElement;
            if ((par.innerText.match(/Library ID:/g) || []).length > 1) break;
            c = par;
          }
          const text = c.innerText;
          const id = (text.match(/Library ID: (\d+)/) || [])[1];
          const range = text.match(/([A-Z][a-z]{2} \d{1,2}, \d{4}) - ([A-Z][a-z]{2} \d{1,2}, \d{4})/);
          const started = (text.match(/Started running on ([A-Z][a-z]{2} \d{1,2}, \d{4})/) || [])[1] || (range ? range[1] : undefined);
          const ended = range ? range[2] : null;
          const active = /\bActive\b/.test(text.split('Library ID')[0]);
          const links = [...c.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.includes('l.facebook.com/l.php') || (!h.includes('facebook.com') && h.startsWith('http')));
          const dest = links.map(h => { try { const u = new URL(h); return u.hostname.includes('l.facebook.com') ? decodeURIComponent(u.searchParams.get('u') || '') : h; } catch (e) { return h; } });
          const lines = text.split('\n').map(s => s.trim()).filter(Boolean);
          const sIdx = lines.indexOf('Sponsored');
          const page = sIdx > 0 ? lines[sIdx - 1] : '';
          const body = sIdx >= 0 ? lines.slice(sIdx + 1).join(' ').slice(0, 700) : '';
          const versions = (text.match(/(\d+) ads use this creative and text/) || [])[1];
          const vids = c.querySelectorAll('video').length;
          const imgs = [...c.querySelectorAll('img')].filter(i => (i.naturalWidth || i.width) > 150).length;
          const media = vids ? 'video' : imgs > 1 ? 'carousel/multi-image' : imgs ? 'image' : 'text/unknown';
          const poster = (c.querySelector('video') || {}).poster || ([...c.querySelectorAll('img')].find(i => (i.naturalWidth || i.width) > 150) || {}).src || '';
          ads.push({ media, poster, id, started, ended, active, page, body, dest: [...new Set(dest)].slice(0, 3), versions: versions ? +versions : 1 });
        }
        return { total, ads };
      });
      all[ph] = { url, total: res.total, ads: res.ads };
      console.error(`${ph}: ~${res.total} results, ${res.ads.length} ads captured`);
    } catch (e) { console.error(`${ph}: ERROR ${e.message}`); all[ph] = { url, error: e.message, ads: [] }; }
    await p.close();
  }
  fs.writeFileSync(out, JSON.stringify(all, null, 1));
  await b.close();
})();
