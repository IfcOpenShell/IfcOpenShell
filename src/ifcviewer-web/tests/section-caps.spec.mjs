// This file was generated with the assistance of an AI coding tool.
//
// Section caps. A section plane is dropped on the end of the sample's beam and
// dragged inwards, so it cuts through the beam and the slab; the cut faces are
// then either capped or left hollow.
import { test, expect } from '@playwright/test';

const shot = (page) => page.locator('#viewer-canvas').screenshot();
const settle = (page) => page.waitForTimeout(600);

test('section cuts are capped, and the caps can be turned off and restyled', async ({ page }) => {
  const gpuErrors = [];
  page.on('console', (msg) => {
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(msg.text()))
      gpuErrors.push(msg.text());
  });
  page.on('pageerror', (e) => gpuErrors.push('pageerror: ' + e.message));

  await page.goto('/scripting.html');
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()),
                             null, { timeout: 30_000 });
  await page.waitForTimeout(1500);

  // The beam's end face in the default view, and a point halfway along it.
  const box = await page.locator('#viewer-canvas').boundingBox();
  const at = (fx, fy) => [box.x + box.width * fx, box.y + box.height * fy];
  const beamEnd = at(0.525, 0.535);
  const beamMiddle = at(0.385, 0.435);

  await page.evaluate(() => window.viewer.module._toggle_section_c());
  await page.mouse.click(...beamEnd);
  await page.waitForTimeout(900);  // async surface pick + add plane
  await page.mouse.move(...beamEnd);
  await page.mouse.down();
  await page.mouse.move(...beamMiddle, { steps: 8 });
  await page.mouse.up();
  await settle(page);

  expect(await page.evaluate(() => window.viewer.sectionCapsEnabled())).toBe(true);
  const capped = await shot(page);

  await page.evaluate(() => window.viewer.setSectionCaps(false));
  await settle(page);
  const hollow = await shot(page);
  expect(Buffer.compare(capped, hollow), 'turning the caps off changed nothing').not.toBe(0);

  await page.evaluate(() => window.viewer.setSectionCaps(true));
  await settle(page);
  expect(Buffer.compare(capped, await shot(page)), 'the caps did not come back').toBe(0);

  await page.evaluate(() => window.viewer.setSectionCapStyle({ outlineWidth: 0 }));
  await settle(page);
  const unoutlined = await shot(page);
  expect(Buffer.compare(capped, unoutlined), 'removing the cut outline changed nothing').not.toBe(0);

  await page.evaluate(() => window.viewer.setSectionCapStyle({ hatch: 'none' }));
  await settle(page);
  const unhatched = await shot(page);
  expect(Buffer.compare(unoutlined, unhatched), 'removing the hatch changed nothing').not.toBe(0);
  expect(Buffer.compare(hollow, unhatched), 'an unhatched cap should still be filled').not.toBe(0);

  // X-ray is for seeing through, so it draws no caps whatever the setting.
  await page.evaluate(() => window.viewer.toggleXray());
  await settle(page);
  const xray = await shot(page);
  await page.evaluate(() => window.viewer.setSectionCaps(false));
  await settle(page);
  expect(Buffer.compare(xray, await shot(page)), 'x-ray drew caps').toBe(0);

  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

test('clicking a cap selects the object it cuts through', async ({ page }) => {
  await page.goto('/scripting.html');
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()),
                             null, { timeout: 30_000 });
  await page.waitForTimeout(1500);

  const box = await page.locator('#viewer-canvas').boundingBox();
  const at = (fx, fy) => [box.x + box.width * fx, box.y + box.height * fy];
  const beamEnd = at(0.525, 0.535);
  const beamMiddle = at(0.385, 0.435);

  await page.evaluate(() => window.viewer.module._toggle_section_c());
  await page.mouse.click(...beamEnd);
  await page.waitForTimeout(900);
  await page.mouse.move(...beamEnd);
  await page.mouse.down();
  await page.mouse.move(...beamMiddle, { steps: 8 });
  await page.mouse.up();
  // Leave the section tool, which claims the left button, so a click selects.
  await page.evaluate(() => window.viewer.module._toggle_section_c());
  await settle(page);

  // The beam's cut face now sits where the middle of the beam was. The right
  // button selects in the default nav preset.
  await page.mouse.click(...at(0.41, 0.452), { button: 'right' });
  await settle(page);

  const picked = await page.evaluate(async () => {
    const v = window.viewer;
    const byId = new Map((await v.getObjects()).map((o) => [o.objectId, o.type]));
    return v.getSelection().map((id) => byId.get(id));
  });
  expect(picked).toEqual(['IfcBeam']);
});
