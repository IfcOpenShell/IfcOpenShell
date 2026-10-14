# IfcOpenShell JS/WASM — tutorial chapters

Each chapter is a folder of static files under [`examples/`](./). Serve `src/ts`
and open the hub at `/ifcopenshell-js/examples/`.

| Chapter | Folder | What you learn |
|---------|--------|----------------|
| **0** | [`00-installation/`](./00-installation/) | Confirm the CDN packages, then `init()` |
| **1** | [`parse/`](./parse/) | Schema plugin, `open`, `byType` |
| **1b** | [`stream/`](./stream/) | Read `FILE_SCHEMA` before loading a schema plugin |
| **2** | [`geom/`](./geom/) | `geom.Settings` and `geom.Iterator` |
| **3** | [`create/`](./create/) | `new File` and `createEntity` |
| **4** | [`full/`](./full/) | Edit an attribute, then tessellate |
| **5** | [`viewer-threejs/`](./viewer-threejs/) | Three.js |
| **6** | [`viewer-babylon/`](./viewer-babylon/) | Babylon.js |
| **7** | [`stream-viewer/`](./stream-viewer/) | Schema, product list, tessellation, click to inspect |
| — | [`smoke/`](./smoke/) | Create a wall or open a local file |

## Prerequisites

`ifcopenshell` and WASM are loaded from jsDelivr (`ifcopenshell@latest` and
`@ifcopenshell/wasm@latest`). From `src/ts`:

```bash
python -m http.server 4173
```

Open http://127.0.0.1:4173/ifcopenshell-js/examples/

## API contract

`init()` takes no asset URL when the page import map points `ifcopenshell` and
`@ifcopenshell/wasm` at the CDN packages.
Plugins are loaded by id before they are used. `open` and
`new File` are synchronous and require the matching schema plugin. Geometry
requires the mapping plugin and a kernel plugin.

```js
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');

const model = ifcopenshell.open(bytes, 'model.ifc');
const walls = model.byType('IfcWall');
console.log(walls[0].id(), walls[0].isA(), walls[0].Name);

await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'manifold');
const settings = new geom.Settings();
settings.set('weld-vertices', false);
const iterator = new geom.Iterator(settings, model, { geometryLibrary: 'manifold' });
if (iterator.initialize()) do {
  const shape = iterator.get();
  const tri = shape.asTriangulationElement();
  const nativeGeometry = tri.geometry();
  let data;
  try {
    data = {
      vertices: nativeGeometry.vertsBuffer(Float32Array),
      faces: nativeGeometry.facesBuffer(Uint32Array),
      transform: shape.transformationBuffer(Float64Array),
    };
  } finally {
    nativeGeometry.destroy();
    tri.destroy();
    shape.destroy();
  }
  if (!data.faces.length) continue;
} while (iterator.next());
iterator.dispose();
model.dispose();
```

`FILE_SCHEMA` can be read with `runtime.raw.parse.streamFromString` before any
schema plugin is loaded. Plugin ids in the staged manifest are `ifc2x3`, `ifc4`,
and `ifc4x3_add2`. These chapters lowercase the schema identifier from the file.

This package does not export an IFC GUID helper. The create and smoke chapters
compress `crypto.randomUUID()` into a 22-character GlobalId locally.

Dispose files and iterators with `dispose()`. Entity instances and settings are
left to garbage collection. Copy triangulation buffers inside `try`, then
`destroy()` the geometry, the triangulation element, and the shape in
`finally`. Empty face buffers are skipped.

Geometry chapters use the `manifold` kernel with `weld-vertices` set to
`false`, matching `threejs.html`. The shared `sample.ifc` contains swept solids
and mapped representations.
