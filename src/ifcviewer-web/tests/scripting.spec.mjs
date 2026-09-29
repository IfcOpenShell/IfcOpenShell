import { test, expect } from '@playwright/test';

// The JavaScript scripting API (web/ifcviewer.js + the _ifcv_* wasm exports),
// driven against the real GPU through /scripting.html — the demo page whose
// buttons ARE the API. Everything runs against the embedded sample sidecar
// (a slab, a wall and a beam), so no fixture file is needed.
//
// Each assertion pins a capability a host page depends on: read/set camera,
// read/set multi-selection, enumerate objects by GlobalId, per-object
// visibility, show/hide all, and colour override. Colour and visibility are
// checked at the PIXELS, not just at the API — the whole point of those two is
// that the GPU state actually changed.

// Boot the scripting page and wait until the API can answer for the sample.
async function open(page) {
  const errors = [];
  page.on('console', (msg) => {
    const t = msg.text();
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(t)) errors.push(t);
  });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));

  await page.goto('/scripting.html');
  // The page publishes the API as window.viewer; isLive() flips once the GPU
  // device is up and the RAF loop is ticking. Timing out here means WebGPU
  // never came up — a real failure, not a flake.
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()), null,
    { timeout: 30_000 });
  // The object table fills once the (async) element-metadata fetch lands.
  await page.waitForFunction(
    () => document.querySelectorAll('#object-table tr[data-id]').length > 0,
    null, { timeout: 30_000 });
  // Geometry streams in a few frames AFTER the model's metadata is up. The
  // pixel assertions below all compare against a baseline shot, so wait until
  // every chunk is resident — otherwise the baseline is an empty scene and, say,
  // hideAll() "changes nothing" because it was already blank.
  await page.waitForFunction(() => {
    const v = window.viewer;
    const p = v.modelProgress(0);
    return v.modelCount() > 0 && p.total > 0 && p.resident === p.total;
  }, null, { timeout: 30_000 });
  await page.waitForTimeout(500);   // let the settle burst paint
  return errors;
}

const shot = (page) => page.locator('#viewer-canvas').screenshot();

test('enumerates every object with its GlobalId, name, type and model', async ({ page }) => {
  const errors = await open(page);

  const objects = await page.evaluate(() => window.viewer.getObjects());
  expect(objects.length).toBe(3);   // the sample: slab + wall + beam
  expect(objects.map((o) => o.type).sort()).toEqual(['IfcBeam', 'IfcSlab', 'IfcWall']);
  for (const o of objects) {
    expect(o.guid, 'every object carries an IFC GlobalId').toMatch(/^[0-9A-Za-z_$]{22}$/);
    expect(o.objectId).toBeGreaterThan(0);
    expect(o.model, 'single model → load index 0').toBe(0);
  }
  // The table rendered from that same array.
  await expect(page.locator('#object-table tr[data-id]')).toHaveCount(3);
  expect(errors, errors.join('\n')).toEqual([]);
});

test('reads the camera and sets it back, round-tripping a saved view', async ({ page }) => {
  const errors = await open(page);

  const start = await page.evaluate(() => window.viewer.getCamera());
  expect(start.yaw).toBeCloseTo(45, 1);
  expect(start.pitch).toBeCloseTo(30, 1);
  expect(start.distance).toBeGreaterThan(0);
  expect(start.eye, 'eye is derived from target/distance/yaw/pitch').toHaveLength(3);
  expect(start.ortho).toBe(false);

  // Set it somewhere else and read it back.
  const moved = await page.evaluate(() => {
    window.viewer.setCamera({ yaw: 120, pitch: -15, distance: 30, ortho: true });
    return window.viewer.getCamera();
  });
  expect(moved.yaw).toBeCloseTo(120, 1);
  expect(moved.pitch).toBeCloseTo(-15, 1);
  expect(moved.distance).toBeCloseTo(30, 1);
  expect(moved.ortho).toBe(true);

  // A whole getCamera() result must be valid input to setCamera — this is what
  // makes "save view / restore view" a two-liner for a host page.
  const restored = await page.evaluate((v) => {
    window.viewer.setCamera(v);
    return window.viewer.getCamera();
  }, start);
  expect(restored.yaw).toBeCloseTo(start.yaw, 1);
  expect(restored.pitch).toBeCloseTo(start.pitch, 1);
  expect(restored.distance).toBeCloseTo(start.distance, 1);
  expect(restored.ortho).toBe(false);

  expect(errors, errors.join('\n')).toEqual([]);
});

test('sets, adds to, and clears a multi-object selection (by id and by GlobalId)', async ({ page }) => {
  const errors = await open(page);

  const result = await page.evaluate(async () => {
    const v = window.viewer;
    const objects = await v.getObjects();
    const wall = objects.find((o) => o.type === 'IfcWall');
    const beam = objects.find((o) => o.type === 'IfcBeam');

    // Every id-taking call accepts an objectId, a GlobalId string, or a whole
    // element object. Exercise all three shapes.
    const events = [];
    v.onSelectionChange((ids) => events.push(ids.length));

    v.setSelection(wall.objectId);                    // by objectId
    const afterSingle = v.getSelection();
    v.addToSelection(beam.guid);                      // by GlobalId
    const afterAdd = v.getSelection();
    const active = v.getActiveObject();
    const named = v.getSelectedObjects().map((o) => o.type).sort();

    v.setSelection(objects);                          // by element objects
    const afterAll = v.getSelection();
    v.removeFromSelection(wall);
    const afterRemove = v.getSelection();
    v.clearSelection();
    const afterClear = v.getSelection();

    return { wallId: wall.objectId, beamId: beam.objectId, afterSingle, afterAdd, active,
             named, afterAll, afterRemove, afterClear, events };
  });

  expect(result.afterSingle).toEqual([result.wallId]);
  expect(result.afterAdd.sort()).toEqual([result.wallId, result.beamId].sort());
  expect(result.active, 'the last-added object is the active one').toBe(result.beamId);
  expect(result.named, 'selected objects carry their IFC identity').toEqual(['IfcBeam', 'IfcWall']);
  expect(result.afterAll).toHaveLength(3);
  expect(result.afterRemove).toHaveLength(2);
  expect(result.afterRemove).not.toContain(result.wallId);
  expect(result.afterClear).toEqual([]);
  // onSelectionChange fired once per mutation, including the programmatic ones.
  expect(result.events).toEqual([1, 2, 3, 2, 0]);

  expect(errors, errors.join('\n')).toEqual([]);
});

test('hides one object, hides all, and shows all again — visibly', async ({ page }) => {
  const errors = await open(page);

  const full = await shot(page);

  // Hide every object: the scene must empty out to background.
  await page.evaluate(() => window.viewer.hideAll());
  await page.waitForTimeout(400);
  const empty = await shot(page);
  expect(Buffer.compare(full, empty), 'hideAll() did not change the render').not.toBe(0);
  expect(await page.evaluate(() => window.viewer.getHidden().length)).toBe(3);

  // Show all: back to the original pixels.
  await page.evaluate(() => window.viewer.showAll());
  await page.waitForTimeout(400);
  expect(await page.evaluate(() => window.viewer.getHidden().length)).toBe(0);
  const restored = await shot(page);
  expect(Buffer.compare(full, restored), 'showAll() did not restore the render').toBe(0);

  // Hide a single object by GlobalId: different from both full and empty.
  await page.evaluate(async () => {
    const v = window.viewer;
    const slab = (await v.getObjects()).find((o) => o.type === 'IfcSlab');
    v.hide(slab.guid);
  });
  await page.waitForTimeout(400);
  const oneHidden = await shot(page);
  expect(await page.evaluate(() => window.viewer.getHidden().length)).toBe(1);
  expect(Buffer.compare(oneHidden, full), 'hiding one object changed nothing').not.toBe(0);
  expect(Buffer.compare(oneHidden, empty), 'hiding one object emptied the scene').not.toBe(0);

  expect(errors, errors.join('\n')).toEqual([]);
});

test('overrides object colour, and clears back to the baked colour', async ({ page }) => {
  const errors = await open(page);

  const before = await shot(page);

  // Paint every object magenta. Nothing else about the scene changes, so any
  // pixel difference is the override landing on the GPU.
  await page.evaluate(async () => {
    const v = window.viewer;
    v.setColor(await v.getObjects(), '#ff00ff');
  });
  await page.waitForTimeout(400);
  const painted = await shot(page);
  expect(Buffer.compare(before, painted), 'setColor() did not change the render').not.toBe(0);

  // A translucent override reclassifies the instance into the transparent pass —
  // a different render again, and the one that would silently do nothing if the
  // cull classifier ignored the override's alpha byte.
  await page.evaluate(async () => {
    const v = window.viewer;
    v.setColor(await v.getObjects(), { r: 255, g: 0, b: 255, a: 80 });
  });
  await page.waitForTimeout(400);
  const translucent = await shot(page);
  expect(Buffer.compare(painted, translucent), 'alpha in a colour override had no effect').not.toBe(0);

  // Clearing restores the model's own colours exactly.
  await page.evaluate(() => window.viewer.clearColors());
  await page.waitForTimeout(400);
  const cleared = await shot(page);
  expect(Buffer.compare(before, cleared), 'clearColors() did not restore the baked colours').toBe(0);

  expect(errors, errors.join('\n')).toEqual([]);
});

test('the demo page buttons drive the same API', async ({ page }) => {
  const errors = await open(page);

  // Select walls → the readout and the table highlight both follow.
  await page.click('#sel-walls');
  await expect(page.locator('#selection-readout')).toContainText('IfcWall');
  await expect(page.locator('#object-table tr.selected')).toHaveCount(1);

  await page.click('#sel-add-beams');
  await expect(page.locator('#object-table tr.selected')).toHaveCount(2);
  expect(await page.evaluate(() => window.viewer.getSelection().length)).toBe(2);

  // Hide the selection through the button, then show all again.
  await page.click('#vis-hide-sel');
  await expect(page.locator('#vis-hint')).toContainText('2 object(s) hidden');
  await page.click('#vis-show-all');
  await expect(page.locator('#vis-hint')).toContainText('Nothing hidden');

  // Colour-by-type paints all three, then reset drops every override.
  const before = await shot(page);
  await page.click('#colour-by-type');
  await page.waitForTimeout(400);
  expect(Buffer.compare(before, await shot(page))).not.toBe(0);
  await page.click('#colour-clear');
  await page.waitForTimeout(400);
  expect(Buffer.compare(before, await shot(page))).toBe(0);

  // Camera buttons move the camera and the readout tracks it.
  await page.click('#cam-top');
  await page.waitForTimeout(300);
  expect(await page.evaluate(() => window.viewer.getCamera().pitch)).toBeCloseTo(90, 0);
  await expect(page.locator('#camera-readout')).toContainText('perspective');
  await page.click('#cam-ortho');
  await page.waitForTimeout(300);
  await expect(page.locator('#camera-readout')).toContainText('orthographic');

  expect(errors, errors.join('\n')).toEqual([]);
});
