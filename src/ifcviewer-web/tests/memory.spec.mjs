import { test, expect } from '@playwright/test';

// GPU memory as the host page sees it: the per-frame stats (cache occupancy,
// working set) and the per-model unload/load lever. Mirrors what
// BonsaiViewer's status bar and Models panel show on desktop.

async function open(page) {
  const errors = [];
  page.on('console', (msg) => {
    const t = msg.text();
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(t)) errors.push(t);
  });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  await page.goto('/scripting.html');
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()), null,
    { timeout: 30_000 });
  return errors;
}

// Add the sample as a real source (the embedded one has no source id) and
// wait until every chunk is resident.
async function addSampleAndSettle(page) {
  const sid = await page.evaluate(async () => {
    const v = window.viewer;
    const loaded = new Promise((resolve) => {
      const off = v.onModelLoaded((d) => { off(); resolve(d); });
    });
    const sid = await v.addUrl('/sample.ifcview', { replace: true, name: 'mem' });
    await loaded;
    return sid;
  });
  await settled(page);
  return sid;
}

async function settled(page) {
  await page.waitForFunction(() => {
    const v = window.viewer;
    if (!v.modelCount()) return false;
    for (let i = 0; i < v.modelCount(); ++i) {
      const p = v.modelProgress(i);
      if (!(p.total > 0 && p.resident === p.total)) return false;
    }
    return true;
  }, null, { timeout: 30_000 });
}

test('stats() reports the frame, the cache and the working set', async ({ page }) => {
  const errors = await open(page);
  await addSampleAndSettle(page);
  await page.waitForTimeout(300);

  const s = await page.evaluate(() => window.viewer.stats());
  expect(s).not.toBeNull();
  expect(s.fps).toBeGreaterThan(0);
  expect(s.frameTimeMs).toBeGreaterThan(0);
  expect(s.objects.total).toBeGreaterThan(0);
  expect(s.triangles.total).toBeGreaterThan(0);

  // Resident geometry occupies the cache, within its capacity, and on web
  // the cache is bounded from the start (the wasm heap cap).
  expect(s.vram.usedBytes).toBeGreaterThan(0);
  expect(s.vram.usedBytes).toBeLessThanOrEqual(s.vram.capacityBytes);
  expect(s.vram.budgetBytes).toBeGreaterThan(0);

  // Everything the camera wants is resident once settled.
  expect(s.workingSet.chunks).toBeGreaterThan(0);
  expect(s.workingSet.chunksMissing).toBe(0);
  expect(s.workingSet.missingBytes).toBe(0);

  expect(errors).toEqual([]);
});

test('unloadModel frees the model\'s GPU memory and loadModel streams it back', async ({ page }) => {
  const errors = await open(page);
  const sid = await addSampleAndSettle(page);

  const before = await page.evaluate((sid) => ({
    unloaded: window.viewer.modelUnloaded(sid),
    bytes:    window.viewer.modelVramBytes(sid),
    used:     window.viewer.stats().vram.usedBytes,
  }), sid);
  expect(before.unloaded).toBe(false);
  expect(before.bytes).toBeGreaterThan(0);

  // Unload: the model's bytes go to zero immediately, and it stays listed.
  const after = await page.evaluate((sid) => {
    const v = window.viewer;
    v.unloadModel(sid);
    return {
      unloaded:   v.modelUnloaded(sid),
      bytes:      v.modelVramBytes(sid),
      modelCount: v.modelCount(),
    };
  }, sid);
  expect(after.unloaded).toBe(true);
  expect(after.bytes).toBe(0);
  expect(after.modelCount).toBe(1);

  // The cache reflects the release on the next frame.
  await page.waitForFunction((used) => {
    const s = window.viewer.stats();
    return s && s.vram.usedBytes < used;
  }, before.used, { timeout: 10_000 });

  // Load: the buffers come back and the chunks stream in again.
  const reloaded = await page.evaluate((sid) => window.viewer.loadModel(sid), sid);
  expect(reloaded).toBe(true);
  expect(await page.evaluate((sid) => window.viewer.modelUnloaded(sid), sid)).toBe(false);
  await settled(page);
  const restored = await page.evaluate((sid) => window.viewer.modelVramBytes(sid), sid);
  expect(restored).toBe(before.bytes);

  expect(errors).toEqual([]);
});
