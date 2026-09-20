import { test, expect } from '@playwright/test';

// The federation half of the scripting API: false origin, per-model transform,
// and the model-loaded event.
//
// Why this exists: the web viewer used to render every model in its own local
// coordinates, because nothing applied a model's IfcCoordinateOperation. Two
// federated models whose map conversions resolve to the same real-world point
// came out misaligned. Models now resolve to global coordinates on load, and
// the first one sets a false origin so the scene stays near the origin —
// composed per-instance transforms are float32, and surveyor coordinates would
// otherwise quantise at around half a metre.
//
// Runs against the embedded sample, which carries NO IfcCoordinateOperation.
// That is deliberate here: it pins the federation plumbing (staging, applying,
// events, units) without needing a georeferenced fixture. The georef values
// themselves are covered by the sidecar round-trip tests in
// src/ifcviewer/tests/test_sidecar_cache.cpp.

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
  await page.waitForFunction(() => {
    const v = window.viewer;
    if (!v.modelCount()) return false;
    const p = v.modelProgress(0);
    return p.total > 0 && p.resident === p.total;
  }, null, { timeout: 30_000 });
  return errors;
}

// viewAll frames the union of resident chunks' world AABBs. Shifting the false
// origin moves every instance, which changes what the cull considers visible
// and can therefore change residency. Settle before each measurement, or the
// two frames being compared describe different subsets of the model.
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

async function frameAndReadTarget(page) {
  // Frame FIRST, then wait. Chunks stream on visibility, so a model sitting off
  // screen — which is exactly what happens right after the origin moves — never
  // becomes resident and a settle-then-frame order would deadlock. The initial
  // viewAll can work from the metadata AABBs, which are known before any
  // geometry has landed.
  await page.evaluate(() => window.viewer.viewAll());
  await settled(page);
  await page.evaluate(() => window.viewer.viewAll());
  return page.evaluate(() => window.viewer.getCamera().target);
}

test('false origin: guessed for the first model, and overridable', async ({ page }) => {
  const errors = await open(page);

  // The sample loads before any host code runs, so by now the automatic guess
  // has already happened. It must NOT be flagged explicit — that flag is what
  // tells the viewer a host has taken over placement.
  const guessed = await page.evaluate(() => window.viewer.getFalseOrigin());
  expect(guessed).not.toBeNull();
  expect(guessed.explicit).toBe(false);
  expect(guessed.xyz).toHaveLength(3);
  guessed.xyz.forEach((v) => expect(Number.isFinite(v)).toBe(true));
  expect(Number.isFinite(guessed.rzDeg)).toBe(true);

  // Setting one takes over: the value round-trips and the flag flips, which is
  // what suppresses the guess for any later first-model load.
  const set = await page.evaluate(() => {
    window.viewer.setFalseOrigin({ xyz: [10, 20, 30], rzDeg: 45 });
    return window.viewer.getFalseOrigin();
  });
  expect(set.xyz[0]).toBeCloseTo(10, 6);
  expect(set.xyz[1]).toBeCloseTo(20, 6);
  expect(set.xyz[2]).toBeCloseTo(30, 6);
  expect(set.rzDeg).toBeCloseTo(45, 6);
  expect(set.explicit).toBe(true);

  expect(errors).toEqual([]);
});

test('false origin shifts the scene by the negated offset', async ({ page }) => {
  const errors = await open(page);

  // A false origin nominates a point as the new origin, so geometry moves by
  // -offset. This is the assertion that would fail if the origin were stored
  // but never composed into the per-instance transforms.
  await page.evaluate(() => window.viewer.setFalseOrigin({ xyz: [0, 0, 0], rzDeg: 0 }));
  const before = await frameAndReadTarget(page);

  await page.evaluate(() => window.viewer.setFalseOrigin({ xyz: [100, 0, 0], rzDeg: 0 }));
  const after = await frameAndReadTarget(page);

  expect(after[0] - before[0]).toBeCloseTo(-100, 1);
  expect(after[1] - before[1]).toBeCloseTo(0, 1);
  expect(after[2] - before[2]).toBeCloseTo(0, 1);

  expect(errors).toEqual([]);
});

test('model transform moves one model and clears back', async ({ page }) => {
  const errors = await open(page);

  // The embedded sample bypasses the source registry, so it has no source id to
  // address. Add the same sidecar as a real source — the flow a host page
  // actually uses — and wait for the load event to hand back its ids.
  const detail = await page.evaluate(async () => {
    const v = window.viewer;
    const loaded = new Promise((resolve) => {
      const off = v.onModelLoaded((d) => { off(); resolve(d); });
    });
    const sid = await v.addUrl('/sample.ifcview', { replace: true, name: 'placed' });
    const d = await loaded;
    // Pin the origin so the automatic guess cannot move things underneath us.
    v.setFalseOrigin({ xyz: [0, 0, 0], rzDeg: 0 });
    return { ...d, sid };
  });

  // onModelLoaded must carry the source id it was asked for, and a real
  // session model id (the core numbers them from 1).
  expect(detail.sourceId).toBe(detail.sid);
  expect(detail.sessionModelId).toBeGreaterThan(0);

  const base = await frameAndReadTarget(page);

  // "Take the point a=(0,0,0) and put it at b=(50,0,0)."
  await page.evaluate((sid) => window.viewer.setModelTransform(
    sid, { a: [0, 0, 0], b: [50, 0, 0], aFrame: 'global' }), detail.sid);
  const shifted = await frameAndReadTarget(page);

  await page.evaluate((sid) => window.viewer.clearModelTransform(sid), detail.sid);
  const cleared = await frameAndReadTarget(page);

  expect(shifted[0] - base[0]).toBeCloseTo(50, 1);
  // Clearing restores the untransformed placement rather than leaving the model
  // where it was put.
  expect(cleared[0]).toBeCloseTo(base[0], 1);

  expect(errors).toEqual([]);
});

test('georef readback reports the sample carries no coordinate operation', async ({ page }) => {
  const errors = await open(page);

  const georef = await page.evaluate(async () => {
    const v = window.viewer;
    const loaded = new Promise((resolve) => {
      const off = v.onModelLoaded((d) => { off(); resolve(d); });
    });
    const sid = await v.addUrl('/sample.ifcview', { replace: true });
    await loaded;
    return v.getModelGeoref(sid);
  });

  expect(georef).not.toBeNull();
  // make_sample.py authors no IfcMapConversion, so the flag is down and the
  // matrix stays the identity placeholder.
  expect(georef.hasCoordinateOperation).toBe(false);
  expect(georef.matrix).toHaveLength(16);
  expect(georef.matrix[0]).toBeCloseTo(1, 9);
  expect(georef.matrix[5]).toBeCloseTo(1, 9);
  expect(georef.matrix[10]).toBeCloseTo(1, 9);
  expect(georef.matrix[15]).toBeCloseTo(1, 9);
  expect(georef.projectLengthToMeters).toBeGreaterThan(0);
  expect(georef.mapUnitToMeters).toBeGreaterThan(0);

  expect(errors).toEqual([]);
});

// The bug this whole path exists to fix: two models whose DIFFERENT
// IfcMapConversions resolve to the SAME real-world point must be drawn on top
// of each other.
//
// georef-a and georef-b (see make_sample.py) are 2 m boxes whose local
// positions differ by ~707 m and whose coordinate operations cancel that out
// exactly. A viewer that applies each model's operation frames one box's worth
// of scene after loading both; one that ignores it — as this viewer did before
// applyCachedModel seeded georef from the sidecar — frames ~707 m of empty
// space between them. The gap is two orders of magnitude larger than the
// geometry, so this cannot pass by accident.
test('models with different map conversions resolving to one point align', async ({ page }) => {
  const errors = await open(page);

  // Pin the origin AFTER the replacing load: replace:true clears the scene,
  // which resets federation state including an explicitly-set origin. Pinning
  // matters because the automatic guess is derived from the FIRST model, so
  // leaving it on would shift the scene between the two measurements.
  await page.evaluate(async () => {
    const v = window.viewer;
    const loaded = new Promise((resolve) => {
      const off = v.onModelLoaded(() => { off(); resolve(); });
    });
    await v.addUrl('/georef-a.ifcview', { replace: true, name: 'a' });
    await loaded;
    v.setFalseOrigin({ xyz: [0, 0, 0], rzDeg: 0 });
  });
  const alone = await frameAndReadTarget(page);
  const aloneDistance = await page.evaluate(() => window.viewer.getCamera().distance);

  // Append the second model. Aligned, it adds nothing to the scene's extent.
  await page.evaluate(async () => {
    const v = window.viewer;
    const loaded = new Promise((resolve) => {
      const off = v.onModelLoaded(() => { off(); resolve(); });
    });
    await v.addUrl('/georef-b.ifcview', { name: 'b' });
    await loaded;
  });
  const both = await frameAndReadTarget(page);
  const bothDistance = await page.evaluate(() => window.viewer.getCamera().distance);

  // Same centre: within a box's width, not hundreds of metres away.
  expect(Math.abs(both[0] - alone[0])).toBeLessThan(2);
  expect(Math.abs(both[1] - alone[1])).toBeLessThan(2);
  expect(Math.abs(both[2] - alone[2])).toBeLessThan(2);

  // And the framing does not blow out to span a 707 m gap.
  expect(bothDistance).toBeLessThan(aloneDistance * 2);

  // Both models really are in the scene — otherwise the assertions above would
  // pass trivially on a failed second load.
  expect(await page.evaluate(() => window.viewer.modelCount())).toBe(2);

  expect(errors).toEqual([]);
});
