// This file was generated with the assistance of an AI coding tool.
//
// Backface culling toggle. Seen from inside the sample's wall every wall face
// is a back face: culled, the wall is not drawn at all; unculled, it fills the
// view. So the camera goes inside the wall and the canvas has to change.
import { test, expect } from '@playwright/test';

const shot = (page) => page.locator('#viewer-canvas').screenshot();

test('turning backface culling off draws the back faces', async ({ page }) => {
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

  // Framing the wall puts the orbit target at its centre; a 0.1 m orbit
  // around that stays inside the 0.3 m thick wall.
  await page.evaluate(async () => {
    const v = window.viewer;
    const wall = (await v.getObjects()).find((o) => o.type === 'IfcWall');
    v.setSelection([wall.objectId]);
    v.frameSelection();
  });
  await page.waitForTimeout(800);
  const enabledByDefault = await page.evaluate(() => {
    const v = window.viewer;
    v.clearSelection();
    v.setCamera({ distance: 0.1, yaw: 0, pitch: 0 });
    return v.backfaceCullingEnabled();
  });
  expect(enabledByDefault).toBe(true);
  await page.waitForTimeout(600);
  const culled = await shot(page);

  const enabledAfterOff = await page.evaluate(() => {
    window.viewer.setBackfaceCulling(false);
    return window.viewer.backfaceCullingEnabled();
  });
  expect(enabledAfterOff).toBe(false);
  await page.waitForTimeout(600);
  const unculled = await shot(page);

  expect(
    Buffer.compare(culled, unculled),
    'the culling toggle changed nothing — back faces never drew',
  ).not.toBe(0);

  await page.evaluate(() => window.viewer.setBackfaceCulling(true));
  await page.waitForTimeout(600);
  expect(Buffer.compare(culled, await shot(page)), 'culling did not come back on').toBe(0);

  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});
