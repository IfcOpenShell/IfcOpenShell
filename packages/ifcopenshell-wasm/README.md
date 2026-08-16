# @ifcopenshell-js/wasm

WASM binaries and generated API glue for [`@ifcopenshell-js/web`](../ifcopenshell-js/).

## Staging assets

This package does not commit multi-megabyte WASM artifacts. Stage them from a local build:

```bash
python nix/wasm_native.py build
cd packages/ifcopenshell-wasm && npm run stage

# Or point at an existing build directory
IFCOPENSHELL_WASM_DIR=/path/to/ifcwrap/wasm npm run stage
```

## Default usage

```js
import { init } from '@ifcopenshell-js/web';

const shell = await init();
```

`@ifcopenshell-js/web` depends on this package and uses `resolveWasmAssets()` by
default. Browser bundlers copy and rewrite the packaged WASM assets
from static `new URL(..., import.meta.url)` references generated into
`asset-manifest.js`.

Vite handles these static asset references without app-specific copy config.
Plain Rollup, esbuild, and webpack 5 are not exercised by this package's
browser test; use a copy/static-assets plugin or serve the packaged `wasm/`
directory and pass `resolveUrls(baseUrl)` when your bundler does not emit the
referenced assets.

## Node usage

Use the default `init()` shown above. The Node export loads
`ifcopenshell_wasm.node.mjs`, reads the packaged WASM binary from disk, and
passes it as `wasmBinary`. Browser exports load the browser-only
`ifcopenshell_wasm.mjs`, so browser bundles never need to parse Node builtin
imports.

## Manual browser asset serving

Most browser apps should use `init()` and let the bundler copy assets. If you
need to serve a custom full `wasm/` directory yourself, pass explicit URLs:

```js
import { init } from '@ifcopenshell-js/web';
import { resolveUrls } from '@ifcopenshell-js/wasm';

const shell = await init({ wasmAssets: await resolveUrls('/wasm/') });
```

The package root is browser-safe: browser bundlers resolve the browser entry,
while Node resolves the filesystem-backed entry.
