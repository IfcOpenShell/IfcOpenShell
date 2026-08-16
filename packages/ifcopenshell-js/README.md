# @ifcopenshell-js/web

Ergonomic TypeScript and JavaScript wrappers for the generated low-level
IfcOpenShell WASM API. The package uses the same contract in browsers and Node.

## Install

```bash
npm install @ifcopenshell-js/web
```

## Usage

```ts
import { IfcFile, init } from '@ifcopenshell-js/web';

const shell = await init();
await shell.loadPlugin('schema', 'ifc4');

const response = await fetch('/model.ifc');
const file = await IfcFile.open(
  shell,
  new Uint8Array(await response.arrayBuffer()),
  'model.ifc',
);

console.log(file.schema, file.entityCount);
const walls = file.all('IfcWall');
console.log(walls.map((wall) => wall.get('Name')));
```

The `raw` property exposes the generated C/WASM surface when a wrapper is not
appropriate. Files, entities, geometry objects, and settings own native handles;
call `dispose()` or use explicit resource management (`using`).

Geometry iteration helpers are exported from `@ifcopenshell-js/web/geom`, serializers from
`@ifcopenshell-js/web/serializers`, and inspection helpers from
`@ifcopenshell-js/web/util`.

## Development

Build and stage WASM before compiling or testing:

```bash
python nix/wasm_native.py build
python nix/wasm_native.py package
cd packages/ifcopenshell-wasm
IFCOPENSHELL_WASM_DIR=/path/to/dist npm run stage
cd ../ifcopenshell-js
npm run build
npm test
```

Use `npm run test:browser` for the browser runtime smoke test and
`npm run docs:check` to validate the public API documentation.
