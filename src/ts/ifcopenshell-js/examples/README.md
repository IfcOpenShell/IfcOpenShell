# Examples — `ifcopenshell`

Browser chapters for the TypeScript bindings in this package. Each folder is a static
`index.html` plus `app.js` page. Import maps load this package's `dist/` and
`@ifcopenshell/wasm` from the jsDelivr CDN, so serve `src/ts` over HTTP.

## Quick start

From the repository, with this package built:

```bash
cd src/ts
python -m http.server 4173
```

Or, from this folder:

```bash
node serve.mjs
```

Open http://127.0.0.1:4173/ifcopenshell-js/examples/

`threejs.html` in this folder loads the published JavaScript and WASM from a CDN.
The numbered chapters keep the local `dist/` and load only WASM from that CDN.

## Layout

| Path | Role |
|------|------|
| `index.html` | Chapter hub |
| `sample.ifc` | One model shared by the chapters that open a file |
| `TUTORIAL.md` | API notes for each chapter |
| `00-installation/` … `stream-viewer/` | Runnable chapters |
| `smoke/` | Create a wall, or open a local file |
| `serve.mjs` | Static server rooted at `src/ts` |

## API used here

```js
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(bytes, 'model.ifc');
const walls = model.byType('IfcWall');
```

Call `dispose()` on files and geometry iterators when you are finished with them.
Copy triangulation buffers out of a shape, then `destroy()` that shape.
