import { test, expect } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import zlib from 'node:zlib';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Decode the first pixel (RGB) of a PNG buffer. For a 1x1 image the row-0
// first pixel is filter-agnostic (every PNG predictor references zero
// neighbours), so we can skip full filter handling.
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

test('sample renders without any interaction (streaming settle loop)', async ({ page }) => {
  // Regression for the blank-until-click stall: the main draw + cull precede
  // driveStreamingLoads, so a freshly-resident chunk paints a frame later. On
  // web's on-demand loop a single post-load requestFrame wasn't enough, so the
  // sample stayed blank until some input re-armed the loop. The settle burst
  // keeps frames coming until streaming converges. Here: NO mouse input at all
  // — a centred patch (the framed cube) must differ from a corner patch
  // (background). If the loop stalls blank, both patches are background.
  const gpuErrors = [];
  page.on('console', (msg) => {
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(msg.text()))
      gpuErrors.push(msg.text());
  });
  await page.goto('/IfcViewerWeb.html');
  await page.waitForFunction(
    () => !!(window.Module && window.Module._app_ptr), null, { timeout: 30_000 });

  // Settle window — strictly no pointer events.
  await page.waitForTimeout(1500);

  const box = await page.locator('#viewer-canvas').boundingBox();
  const patch = (cx, cy) => page.screenshot({
    clip: { x: Math.round(cx - 12), y: Math.round(cy - 12), width: 24, height: 24 },
  });
  const center = await patch(box.x + box.width / 2, box.y + box.height / 2);
  const corner = await patch(box.x + 16, box.y + 16);
  expect(
    Buffer.compare(center, corner),
    'centre patch matches corner — sample never rendered without interaction',
  ).not.toBe(0);
  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

test('background renders in sRGB, not crushed-dark (surface sRGB view)', async ({ page }) => {
  // Regression for the dark-colors bug: the shader pre-decodes sRGB to cancel
  // the surface's linear→sRGB write encode, which only works on an sRGB
  // target. The browser canvas is plain Unorm, so without rendering to an
  // sRGB *view* the whole image renders ~linear (≈3× too dark): the authored
  // background (0.125,0.137,0.161 → ~32,35,41) collapses to ~3,4,6.
  await page.goto('/IfcViewerWeb.html');
  await page.waitForFunction(
    () => !!(window.Module && window.Module._app_ptr), null, { timeout: 30_000 });
  await page.waitForTimeout(1200);

  const box = await page.locator('#viewer-canvas').boundingBox();
  // A 1x1 sample of a top-left corner — background, clear of the framed cube.
  const px = await page.screenshot({
    clip: { x: Math.round(box.x + 6), y: Math.round(box.y + 6), width: 1, height: 1 },
  });
  const [r, g, b] = firstPixelRGB(px);
  // Correct sRGB background is ~(32,35,41); the bug crushes it to <10.
  expect(r, `background too dark — sRGB encode missing (got ${r},${g},${b})`).toBeGreaterThan(20);
  expect(b).toBeGreaterThan(20);
});

test('loads a user-picked sidecar through the Blob.slice byte-range path', async ({ page }) => {
  // Exercises #88: the picked File is read via Blob.slice (metadata head/tail
  // + per-chunk byte ranges) WITHOUT copying the whole file into the wasm
  // heap. Distinct code path from the embedded MEMFS sample above, so it
  // needs its own coverage — a broken blob read renders blank.
  const gpuErrors = [];
  page.on('console', (msg) => {
    const t = msg.text();
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(t)) {
      gpuErrors.push(t);
    }
  });
  page.on('pageerror', (e) => gpuErrors.push('pageerror: ' + e.message));

  await page.goto('/IfcViewerWeb.html');
  await page.waitForFunction(
    () => !!(window.Module && window.Module._app_ptr),
    null,
    { timeout: 30_000 },
  );

  // Pick the sample sidecar through the hidden file input. setInputFiles
  // hands the page a real File, so the browser's Blob.slice reads it exactly
  // as it would a user's 200-500 MB sidecar — just smaller. Wait for the C
  // side to confirm the blob load landed (logged to stderr → console).
  const samplePath = resolve(__dirname, '..', 'sample.ifcview');
  const loaded = page.waitForEvent('console', {
    predicate: (m) => /loaded sidecar \(source/.test(m.text()),
    timeout: 15_000,
  });
  await page.locator('#file-input').setInputFiles(samplePath);
  await loaded;
  await page.waitForTimeout(800);  // let the chunk stream + a few frames draw

  // Orbit: the composited canvas must change, proving the blob-streamed
  // geometry rendered and input still drives it.
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
    'orbit after blob load did not change the canvas — blob read or stream failed',
  ).not.toBe(0);

  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

test('streams a remote sidecar over HTTP Range (?model= URL backend)', async ({ page }) => {
  // The remote backend: ?model=URL resolves total size (HEAD), then reads the
  // metadata + per-chunk byte ranges via HTTP Range (206) — same async-chunk
  // path as the local Blob load, different byte source. serve.mjs answers
  // Range requests, so this exercises it end-to-end (same-origin, no CORS).
  const gpuErrors = [];
  page.on('console', (msg) => {
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(msg.text()))
      gpuErrors.push(msg.text());
  });
  page.on('pageerror', (e) => gpuErrors.push('pageerror: ' + e.message));

  // Wait for the C side to confirm the URL-sourced load landed.
  const loaded = page.waitForEvent('console', {
    predicate: (m) => /loaded sidecar \(source/.test(m.text()),
    timeout: 20_000,
  });
  await page.goto('/IfcViewerWeb.html?model=/sample.ifcview');
  await page.waitForFunction(
    () => !!(window.Module && window.Module._app_ptr), null, { timeout: 30_000 });
  await loaded;
  await page.waitForTimeout(800);  // stream the chunk + a few frames

  // The remote-streamed model must render: centre patch (cube) != corner.
  const box = await page.locator('#viewer-canvas').boundingBox();
  const patch = (cx, cy) => page.screenshot({
    clip: { x: Math.round(cx - 12), y: Math.round(cy - 12), width: 24, height: 24 },
  });
  const center = await patch(box.x + box.width / 2, box.y + box.height / 2);
  const corner = await patch(box.x + 16, box.y + 16);
  expect(
    Buffer.compare(center, corner),
    'remote-streamed model did not render — HTTP Range path failed',
  ).not.toBe(0);
  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

test('click selects an object and the highlight renders (async pick)', async ({ page }) => {
  // Exercises the async object-pick readback: a click maps the pick staging
  // buffer via a spontaneous callback (no blocking spin, which would hang the
  // page), routes object_id through selection, and the next render flushes the
  // highlight. A broken async pick either hangs init/never selects (canvas
  // unchanged) or spams WebGPU errors.
  const gpuErrors = [];
  page.on('console', (msg) => {
    const t = msg.text();
    if (/Uncaptured WebGPU error|is invalid|Not enough memory left/i.test(t)) {
      gpuErrors.push(t);
    }
  });
  page.on('pageerror', (e) => gpuErrors.push('pageerror: ' + e.message));

  await page.goto('/IfcViewerWeb.html');
  await page.waitForFunction(
    () => !!(window.Module && window.Module._app_ptr),
    null,
    { timeout: 30_000 },
  );
  await page.waitForTimeout(1000);  // sample framed + a few frames drawn

  // Click dead-centre, where the framed sample geometry sits. A plain
  // down+up at one point is a pick (no drag), so it must change the canvas
  // (selection highlight). If centre happens to miss, the assertion guards it.
  const box = await page.locator('#viewer-canvas').boundingBox();
  const cx = box.x + box.width / 2;
  const cy = box.y + box.height / 2;
  const before = await shot(page);
  await page.mouse.click(cx, cy, { button: 'right' });  // Web preset: RMB selects
  await page.waitForTimeout(600);  // async pick result + flush + render
  const after = await shot(page);
  expect(
    Buffer.compare(before, after),
    'click did not change the canvas — async pick failed or hit empty space',
  ).not.toBe(0);

  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

// --- Nav / viewing features added on top of the streaming core --------------
// These drive the exported C hooks that the desktop reaches via hotkeys, so a
// break in the shared ViewportCore math (fly, visibility, x-ray) or the web
// wiring shows up here. All run against the embedded sample.

async function ready(page) {
  await page.goto('/IfcViewerWeb.html');
  await page.waitForFunction(
    () => !!(window.Module && window.Module._app_ptr), null, { timeout: 30_000 });
  await page.waitForTimeout(1000);
}

test('fly mode: enter, WASD moves the camera, exit', async ({ page }) => {
  const gpuErrors = [];
  page.on('console', (m) => { if (/Uncaptured WebGPU error|is invalid/i.test(m.text())) gpuErrors.push(m.text()); });
  await ready(page);

  await page.evaluate(() => window.Module._toggle_fly_c());
  expect(await page.evaluate(() => window.Module._fly_is_active_c())).toBe(1);

  const before = await shot(page);
  await page.keyboard.down('w');       // fly forward
  await page.waitForTimeout(500);
  await page.keyboard.up('w');
  await page.waitForTimeout(200);
  const after = await shot(page);
  expect(Buffer.compare(before, after), 'holding W did not move the fly camera').not.toBe(0);

  await page.keyboard.press('Escape');  // single Esc exits
  expect(await page.evaluate(() => window.Module._fly_is_active_c())).toBe(0);
  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

test('x-ray toggles translucency on and off', async ({ page }) => {
  const gpuErrors = [];
  page.on('console', (m) => { if (/Uncaptured WebGPU error|is invalid/i.test(m.text())) gpuErrors.push(m.text()); });
  await ready(page);

  const base = await shot(page);
  await page.evaluate(() => window.Module._toggle_xray_c());
  await page.waitForTimeout(300);
  expect(await page.evaluate(() => window.Module._xray_is_active_c())).toBe(1);
  const xray = await shot(page);
  expect(Buffer.compare(base, xray), 'x-ray on did not change the render').not.toBe(0);

  await page.evaluate(() => window.Module._toggle_xray_c());
  await page.waitForTimeout(300);
  expect(await page.evaluate(() => window.Module._xray_is_active_c())).toBe(0);
  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

test('hide selected removes geometry after a pick', async ({ page }) => {
  const gpuErrors = [];
  page.on('console', (m) => { if (/Uncaptured WebGPU error|is invalid/i.test(m.text())) gpuErrors.push(m.text()); });
  await ready(page);

  const box = await page.locator('#viewer-canvas').boundingBox();
  const before = await shot(page);
  // select whatever is under the centre (Web preset: RMB selects), then hide it
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2, { button: 'right' });
  await page.waitForTimeout(400);
  await page.evaluate(() => window.Module._hide_selected_c());
  await page.waitForTimeout(400);
  const after = await shot(page);
  expect(Buffer.compare(before, after), 'hide did not change the canvas — nothing picked or hide is a no-op').not.toBe(0);

  // show all brings it back
  await page.evaluate(() => window.Module._show_all_c());
  await page.waitForTimeout(400);
  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

test('RMB marquee drag box-selects (Web preset)', async ({ page }) => {
  const gpuErrors = [];
  page.on('console', (m) => { if (/Uncaptured WebGPU error|is invalid/i.test(m.text())) gpuErrors.push(m.text()); });
  await ready(page);

  const box = await page.locator('#viewer-canvas').boundingBox();
  const cx = box.x + box.width / 2, cy = box.y + box.height / 2;
  const before = await shot(page);
  await page.mouse.move(cx - 120, cy - 90);
  await page.mouse.down({ button: 'right' });
  await page.mouse.move(cx - 40, cy - 30, { steps: 4 });
  const midDragVisible = await page.evaluate(() => {
    const m = document.getElementById('marquee');
    return !!(m && getComputedStyle(m).display !== 'none');
  });
  await page.mouse.move(cx + 120, cy + 90, { steps: 6 });
  await page.mouse.up({ button: 'right' });
  await page.waitForTimeout(600);  // async box-pick + apply + render
  const after = await shot(page);
  const hiddenAfter = await page.evaluate(() => {
    const m = document.getElementById('marquee');
    return !!(m && getComputedStyle(m).display === 'none');
  });
  expect(midDragVisible, 'marquee rubber-band was not shown during the drag').toBe(true);
  expect(Buffer.compare(before, after), 'box-select did not change the canvas').not.toBe(0);
  expect(hiddenAfter, 'marquee was not hidden after release').toBe(true);
  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});

test('section tool: click a surface cuts geometry, clear restores', async ({ page }) => {
  const gpuErrors = [];
  page.on('console', (m) => { if (/Uncaptured WebGPU error|is invalid/i.test(m.text())) gpuErrors.push(m.text()); });
  await ready(page);

  const box = await page.locator('#viewer-canvas').boundingBox();
  const cx = box.x + box.width / 2, cy = box.y + box.height / 2;
  const before = await shot(page);
  await page.evaluate(() => window.Module._toggle_section_c());
  expect(await page.evaluate(() => window.Module._section_is_active_c())).toBe(1);
  // Section tool claims LMB: a left click on the model drops a cut.
  await page.mouse.click(cx, cy);
  await page.waitForTimeout(700);  // async surface pick + add plane + render
  const cut = await shot(page);
  expect(Buffer.compare(before, cut), 'section cut did not change the render').not.toBe(0);
  await page.evaluate(() => window.Module._clear_section_c());
  await page.waitForTimeout(400);
  const cleared = await shot(page);
  expect(Buffer.compare(cleared, cut), 'clearing cuts did not change the render').not.toBe(0);
  expect(gpuErrors, gpuErrors.join('\n')).toEqual([]);
});
