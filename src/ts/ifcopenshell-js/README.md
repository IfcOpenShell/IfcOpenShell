# ifcopenshell

TypeScript/JavaScript bindings for the IfcOpenShell WASM runtime.

IFC (Industry Foundation Classes) is the main open standard to encode our built environment in multi-faceted information models. A discipline called BIM (Building Information Modelling) that enables many novel use cases such as 3D coordination, scheduling, define handover information requirements and advanced spatial and programmatic analysis.

IfcOpenShell is the oldest and most mature open source IFC library available. It’s developed since 2011 by a community of hundreds of developers and trusted to deliver many AEC technologies that power our industry. IfcOpenShell is also taught in numerous universities and cited in hundreds of academic publications.

```ts
import * as ifcopenshell from 'ifcopenshell';
import * as ifcopenshell_geom from 'ifcopenshell/geom';

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
using model = new ifcopenshell.File('IFC4');
const wall = model.create('IfcWall', { Name: 'Example' });
console.log(wall.id(), wall.Name);
wall.Name = 'Updated';
```

## Geometry

```ts
await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'manifold');
const settings = new ifcopenshell_geom.Settings();
settings.set('weld-vertices', false);
using iterator = new ifcopenshell_geom.Iterator(settings, model, {
  geometryLibrary: 'manifold',
});
if (iterator.initialize()) do {
  const shape = iterator.get()!;
  // Read shape.asTriangulationElement().geometry() here.
} while (iterator.next());
```

## ifcopenshell.util and ifcopenshell.api (experimental)

`ifcopenshell/util/<module>` and `ifcopenshell/api/<package>` are transpiled from the
Python `ifcopenshell.util` and `ifcopenshell.api` by `src/transpiler`, when the package
is built after `npm run generate`. Names are camelCase, and optional Python parameters go
into a trailing options object:

```ts
import { getProjectUnit } from 'ifcopenshell/util/unit';
import { createEntity } from 'ifcopenshell/api/root';

const unit = getProjectUnit(file, 'LENGTHUNIT');
const wall = createEntity(file, { ifcClass: 'IfcWall', name: 'Wall' });
```

`src/python` holds the generated code (not committed) and its hand-written runtime.
See `src/transpiler/README.md` for how it is generated and tested.

## Examples

[`examples/threejs.html`](./examples/threejs.html) and [`examples/babylon.html`](./examples/babylon.html) load `ifcopenshell` and `@ifcopenshell/wasm` from the jsDelivr CDN. Serve `src/ts` over HTTP and open either page.

## Documentation

See [IfcOpenShell JS/TS documentation](https://docs.ifcopenshell.org/ifcopenshell-js.html)
