// This file was generated with the assistance of an AI coding tool.
//
// Background colour, and specifically its alpha. The alpha only means
// anything if two separate things are right: the surface has to be
// configured with a premultiplied composite mode, or the channel is
// discarded before it reaches the compositor; and the clear value has to be
// scaled by it, or the viewport adds its background colour on top of the
// layer behind instead of vanishing. Both failures are invisible at the
// default opaque alpha, so nothing else in the suite would catch either.
import { test, expect } from '@playwright/test';
import zlib from 'node:zlib';

// Decode the top-left pixel (RGB) of a PNG buffer. Row 0 pixel 0 is
// filter-agnostic — every PNG predictor references zero neighbours there —
// so this can skip filter handling entirely.
function firstPixelRGB(png) {
  let off = 8, colorType = 6;
  const idat = [];
  while (off + 8 <= png.length) {
    const len = png.readUInt32BE(off);
    const type = png.toString('ascii', off + 4, off + 8);
    const data = png.subarray(off + 8, off + 8 + len);
    if (type === 'IHDR') colorType = data[9];
    else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
    off += 12 + len;
  }
  const raw = zlib.inflateSync(Buffer.concat(idat));
  return [raw[1], raw[2], raw[3]];  // skip the row filter byte
}

// A 1x1 sample just inside the canvas corner — background, clear of the
// framed model. Screenshotting through the browser rather than reading the
// canvas back in-page is deliberate: a WebGPU swap-chain texture isn't
// persisted for 2D copy, but the browser's own capture path composites the
// GPU layer against what is behind it, which is the whole point here.
async function cornerPixel(page) {
  const box = await page.locator('#viewer-canvas').boundingBox();
  const png = await page.screenshot({
    clip: { x: Math.round(box.x + 6), y: Math.round(box.y + 6), width: 1, height: 1 },
  });
  return firstPixelRGB(png);
}

function watchGpuErrors(page) {
  const errors = [];
  page.on('console', (msg) => {
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(msg.text()))
      errors.push(msg.text());
  });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  return errors;
}

async function bootViewer(page) {
  await page.goto('/scripting.html');
  await page.waitForFunction(() => !!(window.viewer && window.viewer.isLive()),
                             null, { timeout: 30_000 });
  await page.waitForTimeout(1200);
}

test('an opaque background colour reaches the clear', async ({ page }) => {
  const gpuErrors = watchGpuErrors(page);
  await bootViewer(page);

  await page.evaluate(() => window.viewer.setBackground('#c81e1e'));
  await page.waitForTimeout(600);

  const [r, g, b] = await cornerPixel(page);
  expect(r, `expected the red clear, got ${r},${g},${b}`).toBeGreaterThan(150);
  expect(g, `expected the red clear, got ${r},${g},${b}`).toBeLessThan(80);
  expect(b, `expected the red clear, got ${r},${g},${b}`).toBeLessThan(80);

  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

test('alpha 0 clears to nothing and the layer behind shows through', async ({ page }) => {
  const gpuErrors = watchGpuErrors(page);
  await bootViewer(page);

  // #viewer-box is the element the canvas sits in front of — where a host
  // page would stack a second view. Paint it a colour neither the scene nor
  // the palette uses, so a match can only mean the canvas showed through.
  await page.evaluate(() => {
    document.getElementById('viewer-box').style.background = '#ff00ff';
  });
  await page.waitForTimeout(300);

  const before = await cornerPixel(page);
  expect(
    Math.max(...before),
    `the corner is already bright before the alpha changed (${before}) — it is not `
      + `sampling background, so the assertion below would prove nothing`,
  ).toBeLessThan(90);

  // White at zero alpha, not transparent black: black would pass even if the
  // clear forgot to scale by alpha, since scaling black changes nothing.
  // White separates the two — premultiplied it becomes (0,0,0,0) and the
  // magenta behind survives intact, unscaled it is added on top and washes
  // the corner out to white.
  await page.evaluate(() => window.viewer.setBackground('#ffffff00'));
  await page.waitForTimeout(600);

  const [r, g, b] = await cornerPixel(page);
  const got = `got ${r},${g},${b}`;
  const why = `expected the magenta behind the canvas. Washed-out/white means the `
            + `clear was not premultiplied, or the surface fell back to an opaque `
            + `composite mode and held alpha at 1. ${got}`;
  expect(r, why).toBeGreaterThan(200);
  expect(g, why).toBeLessThan(60);
  expect(b, why).toBeGreaterThan(200);

  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});
