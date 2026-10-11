.. This file was generated with the assistance of an AI coding tool.

Installation
============

Installation from npm
---------------------

TODO

Building from source
--------------------

The JavaScript wrapper depends on the ``@ifcopenshell/wasm`` package, which
contains the compiled WebAssembly modules and generated bindings. From a
repository checkout, build the native WASM artifacts, stage them into that
package, and build the JavaScript wrapper:

.. code-block:: shell

   python nix/build-all.py --native-wasm
   cd src/ts/ifcopenshell-wasm
   npm ci
   npm run stage
   cd ../ifcopenshell-js
   npm ci
   npm run build

Use Node.js 24 for this checkout. Set ``IFCOPENSHELL_WASM_DIR`` before staging
if your artifacts are outside the default ``build/Linux/wasm`` or
``build/Darwin/wasm`` layout. The repository's ``docs/README.md`` describes the
Docker documentation build, which reuses the native WASM BuildKit cache.

To use the packages from your own Node.js project, install both local package
directories using their absolute paths:

.. code-block:: shell

   npm install /path/to/IfcOpenShell/src/ts/ifcopenshell-wasm /path/to/IfcOpenShell/src/ts/ifcopenshell-js

Use ES modules, for example by giving your script a ``.mjs`` extension.
For TypeScript, include ``ES2022``, ``ESNext.Disposable``, and ``DOM`` in your
compiler's ``lib`` configuration, and use a module resolution mode that
supports package exports, such as ``bundler`` or ``NodeNext``.

Loading the runtime and plugins
-------------------------------

Initialize the runtime once, then load the schema needed by your IFC file:

.. code-block:: javascript

   import * as ifcopenshell from 'ifcopenshell';

   const runtime = await ifcopenshell.init();
   await runtime.loadPlugin('schema', 'ifc4');

Initialization and plugin loading are asynchronous. Opening files and querying
entities are synchronous after initialization. Later parameterless ``init()``
calls reuse the shared runtime. Supply custom initialization options on the
first call.

Plugin identifiers are listed in ``ifcopenshell_plugins.json`` alongside the
WASM artifacts. For the schemas in the native build, the identifiers are
``ifc2x3``, ``ifc4``, and ``ifc4x3_add2``. Geometry additionally requires the
matching ``mapping`` plugin and a ``kernel`` plugin; see
:doc:`geometry_processing`.

Using the browser
-----------------

Browser applications can import the same packages through a bundler or import
map. Deploy the WASM assets and plugin files as well as the JavaScript modules.
Keep their relative layout when using the packaged asset resolver. Serve
``.wasm`` files with the ``application/wasm`` MIME type.

The checkout includes an import-map example at
``src/ts/ifcopenshell-js/examples/threejs.html``. It reads an uploaded IFC file,
loads its schema and mapping, and displays triangulated geometry in Three.js.
Serve the ``src/ts`` directory over HTTP to use it.

If your WASM build uses shared memory, serve the application with
``Cross-Origin-Opener-Policy: same-origin`` and
``Cross-Origin-Embedder-Policy: require-corp``. The checkout's
``serve-native-wasm.ps1`` helper serves the native WASM image's browser example
with these headers.
