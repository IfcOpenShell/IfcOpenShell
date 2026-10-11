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
console.log(wall.id(), wall.get('Name'));
wall.set('Name', 'Updated');
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

## Documentation

See [IfcOpenShell JS/TS documentation](https://docs.ifcopenshell.org/ifcopenshell-js.html)
