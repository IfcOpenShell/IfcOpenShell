import { test, expect } from '@playwright/test';

// End-to-end smoke test for the WebGPU build. Every bug from the bring-up
// of camera input + file loading was exactly this shape — the page would
// load but render blank, spam uncaptured WebGPU errors, or swallow mouse
// input behind an overlay. This test would have caught all of them.

// Capture the composited canvas pixels as a PNG buffer. We use
// Playwright's element screenshot rather than an in-page drawImage/
// toDataURL: reading a WebGPU canvas back through a 2D context returns
// blank (the swap-chain texture isn't persisted for 2D copy), whereas
// the browser's own capture path includes GPU layers.
async function shot(page) {
  return page.locator('#viewer-canvas').screenshot();
}

test('renders the sample and orbits without WebGPU errors', async ({ page }) => {
  const gpuErrors = [];
  page.on('console', (msg) => {
    const t = msg.text();
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(t)) {
      gpuErrors.push(t);
    }
  });
  page.on('pageerror', (e) => gpuErrors.push('pageerror: ' + e.message));

  await page.goto('/IfcViewerWeb.html');

  // Init is complete once C publishes the app pointer (set in the wgpu
  // device callback). If WebGPU is missing or the device promise stalls,
  // this times out — a real failure, not a flake.
  await page.waitForFunction(
    () => !!(window.Module && window.Module._app_ptr),
    null,
    { timeout: 30_000 },
  );

  // Let a few frames render the embedded sample.
  await page.waitForTimeout(1000);

  // Drag across the canvas centre to orbit. The composited canvas must
  // change — a single assertion that simultaneously proves the scene
  // rendered (a blank canvas dragged stays blank), input is wired, and
  // the log overlay isn't intercepting mouse events over the viewport.
  const box = await page.locator('#viewer-canvas').boundingBox();
  const cx = box.x + box.width / 2;
  const cy = box.y + box.height / 2;
  const before = await shot(page);
  await page.mouse.move(cx, cy);
  await page.mouse.down();
  await page.mouse.move(cx + 140, cy + 50, { steps: 10 });
  await page.mouse.up();
  await page.waitForTimeout(500);
  const after = await shot(page);
  expect(
    Buffer.compare(before, after),
    'orbit drag did not change the canvas — blank render or dead input',
  ).not.toBe(0);

  // No WebGPU validation/OOM noise at any point.
  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});
