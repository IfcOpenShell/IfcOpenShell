// This file was generated with the assistance of an AI coding tool.
//
// Selection silhouette outline. The renderer's blue selection tint says
// nothing about an object that is already blue, so the halo is the cue that
// has to survive that case: this paints the whole sample the exact palette
// blue that collides, selects one element, and checks the canvas changes.
import { test, expect } from '@playwright/test';

const shot = (page) => page.locator('#viewer-canvas').screenshot();

test('halo reads on an object painted the selection tint colour', async ({ page }) => {
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

  const n = await page.evaluate(async () => {
    const v = window.viewer;
    const objs = await v.getObjects();
    v.setColor(objs, '#3987e5');
    v.setSelection([objs[0].objectId]);
    return objs.length;
  });
  expect(n).toBeGreaterThan(0);
  await page.waitForTimeout(600);
  const withOutline = await shot(page);

  await page.evaluate(() => window.viewer.setSelectionOutline(false));
  await page.waitForTimeout(600);
  const withoutOutline = await shot(page);

  expect(
    Buffer.compare(withOutline, withoutOutline),
    'the outline toggle changed nothing — halo never drew',
  ).not.toBe(0);

  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});
