import { defineConfig } from '@playwright/test';

// Smoke tests for the WebGPU/Emscripten build. They drive a real Chrome
// (channel: 'chrome' — the system google-chrome-stable, which ships a
// working WebGPU stack) rather than Playwright's bundled Chromium, so
// you don't need `npx playwright install`.
//
// WebGPU + headless on Linux is finicky, so the default is HEADED: it
// uses the machine's real GPU via the X display. For a headless CI box,
// run under xvfb-run, or flip headless:true and add a SwiftShader Vulkan
// ICD (see README).
export default defineConfig({
  testDir: '.',
  timeout: 60_000,
  reporter: [['list']],
  webServer: {
    command: 'node serve.mjs',
    url: 'http://localhost:8124/IfcViewerWeb.html',
    reuseExistingServer: true,
    timeout: 30_000,
  },
  use: {
    baseURL: 'http://localhost:8124',
    channel: 'chrome',
    headless: false,
    launchOptions: {
      // This exact combo is what makes requestAdapter return non-null on
      // a headed Linux Chrome here — --use-angle=vulkan + the blocklist
      // override are both load-bearing (probed during scaffold bring-up).
      args: [
        '--enable-unsafe-webgpu',
        '--enable-features=Vulkan',
        '--ignore-gpu-blocklist',
        '--use-angle=vulkan',
      ],
    },
  },
});
