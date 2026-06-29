# Web smoke tests

Headless-browser smoke tests for the WebGPU/Emscripten ifcviewer build.
They load the built page in a real Chrome, wait for wgpu init, and assert
the embedded sample **renders non-blank**, an **orbit drag changes the
framebuffer**, and **no uncaptured WebGPU errors** are logged. Every web
bring-up bug so far (blank render, error-buffer cascade, an overlay
swallowing mouse input) is this shape.

## Prerequisites

- The web build must exist at `build-web/` (repo root):
  ```sh
  source /path/to/emsdk_env.sh
  emcmake cmake -S src/ifcviewer-web -B build-web
  ninja -C build-web IfcViewerWeb
  ```
- Node + a system Chrome (`google-chrome-stable`). The config uses
  `channel: 'chrome'`, so you do **not** need `npx playwright install`.

## Run

```sh
cd src/ifcviewer-web/tests
npm install          # one-time: pulls @playwright/test
npm test
```

`serve.mjs` statically serves `build-web` on :8124 (override with
`WEB_BUILD_DIR=/path PORT=...`). Playwright starts it automatically.

## Headless / CI

WebGPU + headless on Linux is finicky, so the default config runs
**headed** against the machine's real GPU. On a headless box:

```sh
xvfb-run -a npm test
```

For a GPU-less runner, flip `headless: true` in
`playwright.config.mjs` and provide a SwiftShader Vulkan ICD
(`VK_ICD_FILENAMES=.../vk_swiftshader_icd.json`) plus
`--use-angle=swiftshader`. Browser WebGPU over SwiftShader is slow but
adequate for a render-non-blank assertion.
