# ifcopenshell

TypeScript/JavaScript bindings for the IfcOpenShell WASM runtime.

```ts
import * as ifcopenshell from 'ifcopenshell';
import * as ifcopenshell_geom from 'ifcopenshell/geom';

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
using model = new ifcopenshell.File('IFC4');
using wall = model.create('IfcWall', { Name: 'Example' });
console.log(wall.id(), wall.get('Name'));
wall.set('Name', 'Updated');
```

`new File(schema)` creates an empty file. `open(bytes, filename?)`
parses a `Uint8Array` or `ArrayBuffer`. Both return synchronously after runtime
initialization and explicit schema plugin loading.

`init()` initializes one shared runtime per module instance. Concurrent and later
parameterless calls reuse it. Supply configuration only on the first call; failed
initialization can be retried. Core and geometry functions share this runtime through the live `ifcopenshell` export.
Always await `init()` before accessing it or constructing native objects.

```js
import { init, ifcopenshell } from 'ifcopenshell';

await init();
const settings = ifcopenshell.geom.createSettings();
settings.dispose();
```

`File`, `EntityInstance`, `Settings` and `Iterator` are exported classes
that extend the generated binding classes. Construct them with `new`. They expose the native methods
directly and can be passed to generated functions without a `.raw` wrapper.
Call `dispose()` / `destroy()` or use `using` to release handles.

## Python API alignment

`File.create(type, attributes)` accepts any IFC attribute by its schema name,
for example `{ Name: 'Wall', Tag: 'W1', PredefinedType: 'STANDARD' }`.
Use inherited `byId`, `byGuid` and `byType` for queries. Native `byType` and
`traverse` return disposable list handles; release the list and each retrieved
entity when finished.

`EntityInstance.getInfo()` returns a flat dictionary `{ id, type, ...attributes }`.
Options use camelCase: `includeIdentifier` (default `true`), `recursive` (default
`false`), `ignore` (an array of attribute names), and `returnType` (a result
factory, applied recursively). Nonrecursive snapshots contain live entity
handles; recursive snapshots release temporary handles after conversion.

`File.getInverse(entity)` returns an IFC-identity-aware set. Pass
`{ allowDuplicate: true }` for an array, adding `withAttributeIndices: true`
for `[entity, attributeIndex]` pairs. Dispose the returned entity handles.

`File.schema()` returns the schema family, while `schemaIdentifier()` returns
its full name. Import `schemaByName` from `ifcopenshell` to retrieve a disposable
schema declaration. See [the alignment and review list](../../../docs/python-typescript-api-alignment.md).

## Geometry

```ts
await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'opencascade');
using settings = new ifcopenshell_geom.Settings();
settings.set('weld-vertices', false);
using iterator = new ifcopenshell_geom.Iterator(settings, model, {
  numThreads: 1,
  geometryLibrary: 'opencascade',
});
if (iterator.initialize()) do {
  using shape = iterator.get()!;
  // Read shape.asTriangulationElement().geometry() here.
} while (iterator.next());

// For a product with a representation:
// using shape = ifcopenshell_geom.createShape(settings, product);
```

`settings.set(name, value)` and `settings.get(name)` convert values in the native
WASM binding using `emscripten::val`. Booleans, numbers, strings and arrays map
to the setting's declared C++ type; enums use numbers and sets return arrays.
`value(name)` is an alias for `get(name)`.

The optional third argument accepts `numThreads` (default `1`),
`geometryLibrary` (default `'opencascade'`), and either `include` or `exclude`
(arrays of entity ids or IFC type names).

`initialize()` positions at the first shape; `get()` takes ownership of that
shape; `next()` advances and returns a boolean. Call `get()` once per position.
`createShape(settings, instance, representation?, geometryLibrary?)` defaults
to OpenCASCADE. Neither path loads plugins automatically.
Destroy borrowed geometry handles before their owning shape. Typed geometry
buffers are detached copies. Serializers are exported from `ifcopenshell/serializers`
and also require explicit plugin loading.

## Attribute values

`EntityInstance.get(nameOrIndex)` and the inherited `getArgument()` /
`getArgumentByName()` return `AttributeValueType`. Conversion is performed in
C++ using `emscripten::val`, not by a JS attribute wrapper. `set()` and
`setArgument()` convert JS inputs in the same native binding.

Values are null, booleans, numbers, strings, bigints, entity instances or arrays
of these (including nested arrays). Enumerations are strings; an indeterminate
IFC logical is `'UNKNOWN'`. Integers within the JS safe range are numbers;
larger signed 64-bit integers are bigints. Null, derived and empty-aggregate
markers follow the Python output typemap and become null; typed vectors become
arrays, including empty arrays. Entity references remain live `EntityInstance`
objects, including inline typed values and nested aggregates; dispose them when
finished. Passing an entity from another IFC file or runtime is rejected.

There is no `attribute()` or `AttributeValue` handle in the JS API. `entity.ts`
is now `entity_instance.ts`. Matrix conversion and disposable declaration helper
modules have been removed. The generated declarations reference `ESNext.Disposable`.

## Development

Build and stage the WASM artifacts before building the TS package:

```bash
python nix/build-all.py --native-wasm
cd src/ts/ifcopenshell-wasm
npm run stage
cd ../ifcopenshell-js
npm run build
npm test
npm run test:browser
npm run docs:check
```

The package name is `ifcopenshell`; install the local package or its `npm pack`
archive when consuming this checkout.

For the minimal Three.js viewer, serve `src/ts` with `python3 -m http.server 8766`
and open `http://localhost:8766/ifcopenshell-js/examples/threejs.html`.
Its import map uses `ifcopenshell` and `ifcopenshell/geom`. The example reads
`FILE_SCHEMA` with `instance_streamer`, manually loads that schema, its mapping
and OpenCASCADE, and uses `weld-vertices = false`. Three.js comes from a pinned
CDN URL; conversion runs on the main thread.
