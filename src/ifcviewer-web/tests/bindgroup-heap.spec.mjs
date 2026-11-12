// Regression guard for "GPURenderPassEncoder.setBindGroup: Argument 3 can't be
// an ArrayBuffer or an ArrayBufferView larger than 2 GB".
//
// Emscripten's generated WebGPU shim implements the dynamic-offset path of
// wgpuRenderPassEncoderSetBindGroup as
//
//     pass.setBindGroup(index, group, HEAPU32, ptr >>> 2, count);
//
// handing WebGPU the persistent view over the *entire* wasm linear memory.
// Browsers validate the byte length of that whole backing buffer rather than
// the (start, length) slice actually read, and reject anything past 2 GB. This
// build allows the heap to grow to 4 GB (ALLOW_MEMORY_GROWTH +
// MAXIMUM_MEMORY=4294967296, because large federations need the room), so on a
// big enough session every dynamic-offset draw throws on every frame for the
// life of the page. The axis gizmo, section gizmo and overlay lines all draw
// with dynamic offsets every frame, so the viewport dies as soon as the heap
// crosses the line. ifcviewer::setBindGroupDynamic (WgpuDynamicOffsets.h)
// copies the handful of offsets into a small Uint32Array instead.
//
// Rather than allocate 2 GB to reproduce, this asserts the invariant that
// actually matters and holds at any heap size: nothing we hand to
// setBindGroup may alias the wasm heap. Run against a build without the fix
// and it fails on the first frame — the observed buffer is the whole heap.
import { test, expect } from '@playwright/test';

// Comfortably above the 4 bytes a single dynamic offset needs, and ~5 orders
// of magnitude below INITIAL_MEMORY (256 MB), so this cannot pass by accident.
const SANE_MAX_BYTES = 4096;

test('setBindGroup is never handed the wasm heap as dynamic offsets', async ({ page }) => {
  // Must be installed before the module boots so no frame is missed.
  await page.addInitScript(() => {
    const probe = { dynamicCalls: 0, maxBufferBytes: 0, samples: [] };
    window.__bindGroupProbe = probe;
    const proto = GPURenderPassEncoder.prototype;
    const original = proto.setBindGroup;
    proto.setBindGroup = function (index, group, data, ...rest) {
      if (ArrayBuffer.isView(data)) {
        probe.dynamicCalls++;
        const bytes = data.buffer.byteLength;
        if (bytes > probe.maxBufferBytes) probe.maxBufferBytes = bytes;
        if (probe.samples.length < 5) {
          probe.samples.push({ bytes, elements: data.length, ctor: data.constructor.name });
        }
      }
      return original.call(this, index, group, data, ...rest);
    };
  });

  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));

  await page.goto('/IfcViewerWeb.html');
  await page.waitForFunction(
    () => !!(window.Module && window.Module._app_ptr), null, { timeout: 30_000 });
  await page.waitForTimeout(1200);

  // The corner gizmo draws every frame on its own; an orbit drag additionally
  // brings up the pivot triad, which is the other pair of axis call sites.
  const box = await page.locator('#viewer-canvas').boundingBox();
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width / 2 + 90, box.y + box.height / 2 + 30, { steps: 8 });
  await page.waitForTimeout(300);
  await page.mouse.up();
  await page.waitForTimeout(300);

  const result = await page.evaluate(() => ({
    ...window.__bindGroupProbe,
    heapBytes: window.Module.HEAPU32.buffer.byteLength,
  }));
  console.log('BINDGROUP ' + JSON.stringify(result));

  // Without this the assertion below would pass vacuously on a build where
  // nothing draws with dynamic offsets at all.
  expect(
    result.dynamicCalls,
    'no dynamic-offset setBindGroup calls were observed — the gizmos did not draw, ' +
    'so this test proved nothing',
  ).toBeGreaterThan(0);

  expect(
    result.maxBufferBytes,
    `setBindGroup received a ${result.maxBufferBytes}-byte backing buffer; the wasm heap ` +
    `is ${result.heapBytes} bytes. A match means the whole-heap HEAPU32 view is being ` +
    `passed straight through, which throws once the heap passes 2 GB. ` +
    `Samples: ${JSON.stringify(result.samples)}`,
  ).toBeLessThanOrEqual(SANE_MAX_BYTES);

  expect(errors, `page errors during the run: ${errors.join(' | ')}`).toHaveLength(0);
});
