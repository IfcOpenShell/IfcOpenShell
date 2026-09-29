// This file was generated with the assistance of an AI coding tool.
//
// The RGB axis indicator, in both of its guises: the corner gizmo that sits
// in the viewport's bottom-left, and the pivot triad that appears at the
// orbit target while a navigation drag is running. Both are drawn by the
// shared AxisIndicatorRenderer from ViewportCore, so a regression here would
// most likely be a wiring one — the renderer never inited, the pivot gate
// never set, the corner pass encoded before the surface resolved — none of
// which any other test in the suite would notice.
import { test, expect } from '@playwright/test';
import zlib from 'node:zlib';

// Decode the top-left pixel (RGB) of a PNG buffer. Row 0 pixel 0 is
// filter-agnostic — every PNG predictor references zero neighbours there —
// so this can skip filter handling entirely.
function firstPixelRGB(png) {
  let off = 8;
  const idat = [];
  while (off + 8 <= png.length) {
    const len = png.readUInt32BE(off);
    const type = png.toString('ascii', off + 4, off + 8);
    const data = png.subarray(off + 8, off + 8 + len);
    if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
    off += 12 + len;
  }
  const raw = zlib.inflateSync(Buffer.concat(idat));
  return [raw[1], raw[2], raw[3]];  // skip the row filter byte
}

// Is this pixel on the +Z arm? Its colour is Bonsai's decorator blue
// (0.157, 0.565, 1.000), so blue leads red by a mile. Everything it can be
// drawn over stays well under the threshold: the background is a near-grey
// (32, 35, 41), the sample model is white, and even the dim x-ray pass —
// 0.3 alpha where the arm is behind geometry — lands around (191, 222, 255).
const isAxisBlue = ([r, , b]) => b - r > 30;

// Sample 1x1 pixels straight up from (cx, cy), which is where the +Z arm
// points at the default camera pitch. Stepping rather than picking one exact
// pixel keeps this off the anti-aliased edges of a 2.5 px line.
async function scanUp(page, cx, cy, from, to, step = 4) {
  const hits = [];
  for (let dy = from; dy <= to; dy += step) {
    const png = await page.screenshot({
      clip: { x: Math.round(cx), y: Math.round(cy - dy), width: 1, height: 1 },
    });
    hits.push(firstPixelRGB(png));
  }
  return hits;
}

async function boot(page) {
  await page.goto('/IfcViewerWeb.html');
  await page.waitForFunction(
    () => !!(window.Module && window.Module._app_ptr), null, { timeout: 30_000 });
  await page.waitForTimeout(1200);
  return page.locator('#viewer-canvas').boundingBox();
}

test('corner axis gizmo draws in the bottom-left', async ({ page }) => {
  const box = await boot(page);
  // Gizmo box: 110 CSS px square, 10 px in from the bottom-left corner. The
  // +Z arm runs up from its centre for ~39 px (arm 1.0 in a 1.4 half-extent
  // ortho, over a 55 px half-box).
  const cx = box.x + 10 + 55;
  const cy = box.y + box.height - 10 - 55;
  const hits = await scanUp(page, cx, cy, 10, 34);
  expect(
    hits.some(isAxisBlue),
    `no +Z arm above the gizmo centre — corner axis missing (sampled ${JSON.stringify(hits)})`,
  ).toBe(true);
});

test('pivot triad shows during an orbit drag and clears on release', async ({ page }) => {
  const box = await boot(page);
  // The orbit target projects to the viewport centre, and the pivot arms are
  // 30 CSS px, so the +Z arm runs up from there.
  const cx = box.x + box.width / 2;
  const cy = box.y + box.height / 2;

  const before = await scanUp(page, cx, cy, 8, 26);
  expect(before.some(isAxisBlue), 'pivot visible before any drag').toBe(false);

  await page.mouse.move(cx, cy);
  await page.mouse.down();
  await page.mouse.move(cx + 90, cy + 30, { steps: 8 });
  await page.waitForTimeout(200);
  const during = await scanUp(page, cx, cy, 8, 26);
  await page.mouse.up();
  expect(
    during.some(isAxisBlue),
    `no pivot triad mid-drag (sampled ${JSON.stringify(during)})`,
  ).toBe(true);

  // Released without afterglow — the indicator goes on the next frame.
  await page.waitForTimeout(400);
  const after = await scanUp(page, cx, cy, 8, 26);
  expect(after.some(isAxisBlue), 'pivot triad still up after mouse release').toBe(false);
});
