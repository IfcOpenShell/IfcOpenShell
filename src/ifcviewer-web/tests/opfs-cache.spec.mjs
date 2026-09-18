import { test, expect } from '@playwright/test';

// The OPFS model cache behind addUrl(url, {cache: true}): the first load
// streams over HTTP Range and fills a local copy from those same reads; a
// reload of the page then loads the model with zero geometry traffic. One
// browser context spans both loads — OPFS is origin storage, so it survives
// page reloads within the context.

function watchRequests(page, counters) {
  page.on('request', (req) => {
    if (!req.url().includes('sample.ifcview')) return;
    if (req.method() === 'HEAD') counters.head++;
    else if (req.headers()['range']) counters.range++;
    else counters.other++;
  });
}

async function openScripting(page, errors) {
  page.on('console', (msg) => {
    const t = msg.text();
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(t)) errors.push(t);
  });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  await page.goto('/scripting.html');
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()), null,
    { timeout: 30_000 });
}

async function addCachedSampleAndSettle(page) {
  await page.evaluate(async () => {
    const v = window.viewer;
    const loaded = new Promise((resolve) => {
      const off = v.onModelLoaded((d) => { off(); resolve(d); });
    });
    await v.addUrl('/sample.ifcview', { replace: true, cache: true, name: 'cached' });
    await loaded;
  });
  await page.waitForFunction(() => {
    const v = window.viewer;
    if (!v.modelCount()) return false;
    const p = v.modelProgress(0);
    return p.total > 0 && p.resident === p.total;
  }, null, { timeout: 30_000 });
  // The element table is read through the same source — pull it so its
  // ranges land in the cache too, then let the write chain drain.
  await page.evaluate(() => window.viewer.getObjects());
  await page.waitForFunction(async () => {
    const info = await window.viewer.cacheInfo();
    const e = info.entries.find((x) => x.url.endsWith('/sample.ifcview'));
    return !!(e && e.complete);
  }, null, { timeout: 30_000 });
}

test('first load fills the cache from its own reads; a reload streams nothing', async ({ page }) => {
  const errors = [];
  const first = { head: 0, range: 0, other: 0 };
  watchRequests(page, first);
  await openScripting(page, errors);
  await page.evaluate(() => window.viewer.clearCache());

  await addCachedSampleAndSettle(page);
  expect(first.range, 'first visit must stream over HTTP Range').toBeGreaterThan(0);

  const info = await page.evaluate(() => window.viewer.cacheInfo());
  const entry = info.entries.find((x) => x.url.endsWith('/sample.ifcview'));
  expect(entry.complete).toBe(true);
  expect(entry.cachedBytes).toBe(entry.size);

  // Second visit: same context, fresh page. Only the HEAD validation may
  // touch the network — every byte of geometry and metadata comes from OPFS.
  await page.reload();
  const second = { head: 0, range: 0, other: 0 };
  watchRequests(page, second);
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()), null,
    { timeout: 30_000 });
  await addCachedSampleAndSettle(page);
  expect(second.range, 'a complete validated copy must stream zero ranges').toBe(0);
  expect(second.other, 'and never download the file whole').toBe(0);
  expect(second.head).toBeGreaterThan(0);

  // The cached model is actually usable: objects enumerate with GUIDs.
  const objects = await page.evaluate(() => window.viewer.getObjects());
  expect(objects.length).toBeGreaterThan(0);
  expect(objects.some((o) => o.guid)).toBe(true);

  expect(errors).toEqual([]);
});

test('clearCache drops the entry and the next load streams again', async ({ page }) => {
  const errors = [];
  await openScripting(page, errors);
  await addCachedSampleAndSettle(page);

  const cleared = await page.evaluate(() => window.viewer.clearCache('/sample.ifcview'));
  expect(cleared).toBe(1);
  const info = await page.evaluate(() => window.viewer.cacheInfo());
  expect(info.entries.find((x) => x.url.endsWith('/sample.ifcview'))).toBeUndefined();

  await page.reload();
  const counters = { head: 0, range: 0, other: 0 };
  watchRequests(page, counters);
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()), null,
    { timeout: 30_000 });
  await addCachedSampleAndSettle(page);
  expect(counters.range).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});
