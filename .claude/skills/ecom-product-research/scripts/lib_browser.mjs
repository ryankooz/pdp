/** Shared helpers for the Meta Ads Library scripts: browser launch, paths, page harvest. */
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

/** Data root: ECOM_WIKI_ROOT, else the current working directory (run from the repo root). */
export const dataRoot = process.env.ECOM_WIKI_ROOT || process.cwd();
export const stateDir = path.join(dataRoot, 'intel', 'product-research', '_state');

function loadChromium() {
  for (const mod of ['playwright', 'playwright-core']) {
    try { return require(mod).chromium; } catch { /* try next */ }
  }
  throw new Error('Neither playwright nor playwright-core is installed. Run `npm install` in the skill folder.');
}

/** Pick a browser: EDGE_EXECUTABLE / CHROME_EXECUTABLE, else Edge if present, else Playwright's own Chromium. */
function resolveExecutable() {
  const explicit = process.env.EDGE_EXECUTABLE || process.env.CHROME_EXECUTABLE;
  if (explicit) return explicit;
  const candidates = process.platform === 'win32'
    ? ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe']
    : process.platform === 'darwin'
      ? ['/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']
      : ['/usr/bin/microsoft-edge'];
  return candidates.find(p => fs.existsSync(p)); // undefined → Playwright default Chromium
}

export async function launch() {
  const chromium = loadChromium();
  const profile = process.env.META_ADS_PROFILE || path.join(stateDir, 'browser-profile');
  fs.mkdirSync(profile, { recursive: true });
  const executablePath = resolveExecutable();
  return chromium.launchPersistentContext(profile, {
    ...(executablePath ? { executablePath } : {}),
    headless: true,
    viewport: { width: 1440, height: 1200 },
    locale: 'en-US',
    args: ['--disable-blink-features=AutomationControlled', '--no-sandbox'],
  });
}

export function libraryUrl(input, country = process.env.META_ADS_COUNTRY || 'US') {
  if (input.startsWith('http')) return input;
  return 'https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=' + encodeURIComponent(country)
    + '&q=' + encodeURIComponent(input) + '&search_type=keyword_exact_phrase&media_type=all';
}

/** Decode Meta's l.php?u= redirect so the full destination path is preserved. */
export function decodeOutbound(href) {
  try {
    const u = new URL(href);
    if (/(^|\.)facebook\.com$/.test(u.hostname) && u.pathname === '/l.php' && u.searchParams.get('u')) {
      return u.searchParams.get('u');
    }
  } catch { /* ignore */ }
  return null;
}

/** Load the page, scroll in bounded chunks, and harvest text + links. */
export async function harvest(page, input, { settleMs = 6000, scrolls = 6, scrollWaitMs = 2000 } = {}) {
  const url = libraryUrl(input);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(settleMs);
  let stable = 0, lastHeight = 0;
  for (let i = 0; i < scrolls && stable < 2; i++) {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(scrollWaitMs);
    const h = await page.evaluate(() => document.body.scrollHeight);
    stable = h === lastHeight ? stable + 1 : 0;
    lastHeight = h;
  }
  const body = await page.locator('body').innerText().catch(() => '');
  const links = (await page.locator('a[href]').evaluateAll(as => as.slice(0, 1000).map(a => ({ text: (a.innerText || '').trim(), href: a.href }))))
    .map(l => ({ ...l, destination: decodeOutbound(l.href) }));
  const libraryIds = [...new Set([...body.matchAll(/Library ID:\s*(\d+)/g)].map(m => m[1]))];
  const destinations = [...new Set(links.map(l => l.destination).filter(Boolean))];
  return {
    ok: body.length > 200,
    observed_at: new Date().toISOString(),
    query: input.startsWith('http') ? null : input,
    url,
    title: await page.title(),
    scroll_height: lastHeight,
    library_ids: libraryIds,
    destinations,
    login_wall: /log in|create new account/i.test(body.slice(0, 3000)) && libraryIds.length === 0,
    no_ads_match: body.includes('No ads match'),
    body_text: body.slice(0, 100000),
    links,
  };
}

export function writeJson(out, data) {
  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
  fs.writeFileSync(out, JSON.stringify(data, null, 2));
}
