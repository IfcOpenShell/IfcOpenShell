import { test, expect } from '@playwright/test';

// Which file did this object come from? Every host page answers that by taking
// the `model` index the viewer reports and looking it up in its own list of
// models, in the order it added them — the mapping the API documents. The
// index is only worth anything if it survives federated models finishing their
// loads out of order, which is exactly what happens over a real network.
//
// The two georef fixtures carry fixed GUIDs, so an object can be attributed to
// its file here without trusting the very index under test.
const GUIDS = {
  'georef-a': ['13r0IXtWf5pf18Q1EGzHXl', '22CLYZYiz8ZhbpLaYDVIu6'],
  'georef-b': ['3DkP2KRu5AIRxhhAz$DcQH', '2ueyz_jIr2QgMKs4v0fWl2'],
};

test('model index follows add order when the first model loads last', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  await page.goto('/scripting.html');
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()), null,
    { timeout: 30_000 });

  // georef-a is added first but served slowly, so every one of its range reads
  // lands after georef-b's. Without a stable ordering the core hands out its
  // load-order slots in completion order and the two models come back swapped.
  const sourceIds = await page.evaluate(async () => {
    const a = await window.viewer.addUrl('/georef-a.ifcview?delay=120', { replace: true });
    const b = await window.viewer.addUrl('/georef-b.ifcview');
    return [a, b];
  });
  expect(sourceIds[0]).toBeLessThan(sourceIds[1]);

  await page.waitForFunction(() => window.viewer.modelCount() === 2, null, { timeout: 30_000 });

  const objects = await page.evaluate(() => window.viewer.getObjects());
  const rowFor = (guid) => objects.find((o) => o.guid === guid) || {};

  for (const guid of GUIDS['georef-a']) {
    expect(rowFor(guid).model, `${guid} belongs to georef-a, added first`).toBe(0);
    expect(rowFor(guid).sourceId, `${guid} came from georef-a's source`).toBe(sourceIds[0]);
  }
  for (const guid of GUIDS['georef-b']) {
    expect(rowFor(guid).model, `${guid} belongs to georef-b, added second`).toBe(1);
    expect(rowFor(guid).sourceId, `${guid} came from georef-b's source`).toBe(sourceIds[1]);
  }
  expect(errors, errors.join('\n')).toEqual([]);
});

test('a pick reports the source the model was added from', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  await page.goto('/scripting.html');
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()), null,
    { timeout: 30_000 });

  await page.evaluate(async () => {
    await window.viewer.addUrl('/georef-a.ifcview?delay=120', { replace: true });
    await window.viewer.addUrl('/georef-b.ifcview');
  });
  await page.waitForFunction(() => window.viewer.modelCount() === 2, null, { timeout: 30_000 });
  // The pick payload is built from the element table, so make sure it is
  // resident and take the same table to check the answer against.
  const objects = await page.evaluate(() => window.viewer.getObjects());
  await page.evaluate(() => window.viewer.viewAll());
  await page.waitForTimeout(800);

  // Whichever box the click lands on is fine — what is under test is that the
  // pick and the object table agree about which file the object came from.
  await page.evaluate(() => {
    window.__pick = new Promise((resolve) => window.viewer.onSelect(resolve));
  });
  const box = await page.locator('#viewer-canvas').boundingBox();
  // Web preset: RMB selects (LMB orbits).
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2, { button: 'right' });
  const detail = await page.evaluate(() => window.__pick);

  expect(detail.guid, 'click hit empty space').toBeTruthy();
  const row = objects.find((o) => o.guid === detail.guid);
  expect(row, 'picked a GUID that is not in the object table').toBeTruthy();
  expect(detail.sourceId, 'pick and object table disagree on the source').toBe(row.sourceId);
  expect(detail.modelIndex).toBe(row.model);
  expect(detail.sourceId).not.toBeNull();
  expect(errors, errors.join('\n')).toEqual([]);
});
