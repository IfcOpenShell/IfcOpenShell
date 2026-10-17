.. This file was generated with the assistance of an AI coding tool.

Installation
============

Install the published ``ifcopenshell`` package, or build both packages from a
checkout. Either way the application imports ``ifcopenshell``. npm places the
WebAssembly build in ``node_modules/@ifcopenshell/wasm``, and ``init()`` loads
it from there. The application passes no file path and no URL unless a later
section tells it to.

Installation from npm
---------------------

``ifcopenshell`` depends on ``@ifcopenshell/wasm``. That second package
contains the compiled WebAssembly modules, the generated bindings, and the
plugins. Installing the wrapper installs it too:

.. code-block:: shell

   npm install ifcopenshell

Node.js 18 or newer is required. The packages publish ES modules only.

From an empty directory, the same install looks like this:

.. code-block:: shell

   npm init -y
   npm pkg set type=module
   npm install ifcopenshell

``npm pkg set type=module`` writes ``"type": "module"`` into ``package.json``.
A script with a ``.mjs`` extension is the other way to turn on ES modules.

Save this as ``create.js`` in that same directory, the one that contains
``node_modules``, and run ``node create.js``:

.. code-block:: javascript

   import * as ifcopenshell from 'ifcopenshell';

   const runtime = await ifcopenshell.init();
   await runtime.loadPlugin('schema', 'ifc4');
   const model = new ifcopenshell.File('IFC4');
   try {
     const wall = model.create('IfcWall', { Name: 'Example' });
     console.log(wall.id(), wall.Name);
   } finally {
     model.dispose();
   }

The import is the package name ``ifcopenshell``. Node starts at ``create.js``
and walks up until it finds ``node_modules/ifcopenshell``. That package then
imports ``@ifcopenshell/wasm``, which resolves to
``node_modules/@ifcopenshell/wasm``.

``init()`` loads the runtime from that installed package. Call it before
creating a ``File``, calling ``open()``, or loading a plugin. Geometry is a
separate import, ``ifcopenshell/geom``.

For TypeScript, include ``ES2022``, ``ESNext.Disposable``, and ``DOM`` in the
compiler ``lib`` list. ``moduleResolution`` has to read the package
``exports`` map, so use ``bundler`` or ``NodeNext``:

.. code-block:: json

   {
     "compilerOptions": {
       "target": "ES2022",
       "module": "NodeNext",
       "moduleResolution": "NodeNext",
       "lib": ["ES2022", "ESNext.Disposable", "DOM"]
     }
   }

``ESNext.Disposable`` is what enables ``using`` on ``File``. ``DOM`` is what
the WebAssembly types refer to.

Building from source
--------------------

The JavaScript wrapper depends on the ``@ifcopenshell/wasm`` package, which
contains the compiled WebAssembly modules and generated bindings. From a
repository checkout, build the native WASM artifacts, stage them into that
package, and build the JavaScript wrapper. Use Node.js 24 for this checkout.

.. code-block:: shell

   python nix/build-all.py --native-wasm
   cd src/ts/ifcopenshell-wasm
   npm ci
   npm run stage
   cd ../ifcopenshell-js
   npm ci
   npm run build

Set ``IFCOPENSHELL_WASM_DIR`` before staging if your artifacts are outside the
default ``build/Linux/wasm`` or ``build/Darwin/wasm`` layout. The repository's
``docs/README.md`` describes the Docker documentation build, which reuses the
native WASM BuildKit cache.

``npm run stage`` is what fills ``src/ts/ifcopenshell-wasm/wasm``. Until that
directory contains ``ifcopenshell_api.mjs``, ``ifcopenshell_wasm.node.mjs``,
``ifcopenshell_wasm.wasm``, and ``ifcopenshell_plugins.json``, ``init()``
reports that the WASM artifacts are missing.

Inside this checkout, ``src/ts/ifcopenshell-js/node_modules/@ifcopenshell/wasm``
is a link to ``../ifcopenshell-wasm``. That relative link is valid only while
commands run from ``src/ts/ifcopenshell-js``.

To use the packages from your own Node.js project, install both local package
directories. The wrapper depends on the package name ``@ifcopenshell/wasm``,
so both directories go in one command. Installing only ``ifcopenshell-js``
makes npm fetch ``@ifcopenshell/wasm`` from the registry, which is a different
build from the directory you staged.

Absolute paths:

.. code-block:: shell

   npm install /path/to/IfcOpenShell/src/ts/ifcopenshell-wasm /path/to/IfcOpenShell/src/ts/ifcopenshell-js

On Windows, pass the same directories as ``file:`` URLs with forward slashes:

.. code-block:: shell

   npm install file:///C:/path/to/IfcOpenShell/src/ts/ifcopenshell-wasm file:///C:/path/to/IfcOpenShell/src/ts/ifcopenshell-js

On macOS and Linux the URLs start with ``file:///home/you/IfcOpenShell/...``.
The project still imports ``ifcopenshell``, and it uses the same
``"type": "module"`` setting (or ``.mjs`` scripts) and the same TypeScript
``lib`` and ``moduleResolution`` settings as an install from npm.

Loading the runtime and plugins
-------------------------------

Initialize the runtime once, then load the schema needed by your IFC file.
Initialization and plugin loading are asynchronous. Opening files and querying
entities are synchronous after initialization. Later parameterless ``init()``
calls reuse the shared runtime. Supply custom initialization options on the
first call.

.. code-block:: javascript

   import { readFile } from 'node:fs/promises';
   import * as ifcopenshell from 'ifcopenshell';

   const name = process.argv[2];
   const bytes = await readFile(name);
   const runtime = await ifcopenshell.init();
   await runtime.loadPlugin('schema', 'ifc4');
   const model = ifcopenshell.open(bytes, name);
   try {
     console.log(model.schema(), model.entityCount);
   } finally {
     model.dispose();
   }

Run it with ``node open.js model.ifc``. The script stays inside the project
directory so the ``ifcopenshell`` import resolves.

Plugin identifiers are listed in ``ifcopenshell_plugins.json`` alongside the
WASM artifacts. For the schemas in the native build, the identifiers are
``ifc2x3``, ``ifc4``, and ``ifc4x3_add2``. Geometry additionally requires the
matching ``mapping`` plugin and a ``kernel`` plugin; see
:doc:`../ifcopenshell/geometry_processing`.

.. code-block:: javascript

   await runtime.loadPlugin('schema', 'ifc4');
   await runtime.loadPlugin('mapping', 'ifc4');
   await runtime.loadPlugin('kernel', 'manifold');

``FILE_SCHEMA`` can be read before any schema plugin is loaded. The plugin id
is that identifier in lower case. ``schema()`` then returns the general schema
name, such as ``IFC4``. ``schemaIdentifier()`` keeps addendum and technical
corrigendum suffixes. Release the header, the schema declaration, and the
stream with ``destroy()``. ``bytes`` and ``name`` are the same values as in
the program above:

.. code-block:: javascript

   const preview = new TextDecoder().decode(bytes.slice(0, 4096));
   const stream = runtime.raw.parse.streamFromString(preview);
   let header;
   let declaration;
   let pluginId;
   try {
     header = stream.header();
     declaration = header.fileSchema();
     pluginId = declaration.schemaIdentifiers()[0].toLowerCase();
   } finally {
     declaration?.destroy();
     header?.destroy();
     stream.destroy();
   }
   await runtime.loadPlugin('schema', pluginId);
   const model = ifcopenshell.open(bytes, name);

Using the browser
-----------------

Browser applications can import the same packages through a bundler or an
import map. Deploy the WASM assets and plugin files as well as the JavaScript
modules. Keep their relative layout when using the packaged asset resolver.
Serve ``.wasm`` files with the ``application/wasm`` MIME type.

With a bundler
~~~~~~~~~~~~~~

After ``npm install ifcopenshell``, a bundler resolves ``ifcopenshell`` and
``@ifcopenshell/wasm`` the same way Node.js does. The script is the same
``import * as ifcopenshell from 'ifcopenshell'``.

A bundler that rewrites ``new URL(..., import.meta.url)`` copies the WASM
files and plugins out of ``@ifcopenshell/wasm``. Vite does this, so a Vite
app passes no asset path:

.. code-block:: shell

   npm create vite@latest my-app -- --template vanilla
   cd my-app
   npm install
   npm install ifcopenshell
   npm run dev

Put ``init()`` and ``loadPlugin()`` in ``src/main.js``.

With an import map
~~~~~~~~~~~~~~~~~~

An import map does not read ``package.json`` ``exports``, so each specifier
the packages import has to be a file URL. Use the same version on every URL.
``@ifcopenshell/wasm`` points at ``browser.js``. The Node entry ``index.js``
imports ``node:fs`` and will not load in a browser. ``browser.js`` then loads
``asset-manifest.js`` and the ``wasm`` directory relative to its own URL, so
the map targets ``browser.js`` itself. ``@ifcopenshell/wasm/api`` is a second
specifier.

.. code-block:: html

   <script type="importmap">
   {
     "imports": {
       "ifcopenshell": "https://cdn.jsdelivr.net/npm/ifcopenshell@latest/dist/index.js",
       "ifcopenshell/geom": "https://cdn.jsdelivr.net/npm/ifcopenshell@latest/dist/geom/index.js",
       "@ifcopenshell/wasm": "https://cdn.jsdelivr.net/npm/@ifcopenshell/wasm@latest/browser.js",
       "@ifcopenshell/wasm/api": "https://cdn.jsdelivr.net/npm/@ifcopenshell/wasm@latest/wasm/ifcopenshell_api.mjs"
     }
   }
   </script>

The checkout includes import-map examples at
``src/ts/ifcopenshell-js/examples/threejs.html`` and
``src/ts/ifcopenshell-js/examples/babylon.html``. Each page reads an uploaded
IFC file, loads its schema and mapping, and displays triangulated geometry.
Serve the ``src/ts`` directory over HTTP to use them.

Copying the WebAssembly files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the bundler leaves the asset URLs unresolved, copy the ``wasm`` directory
from ``@ifcopenshell/wasm`` onto your server and pass it to the first
``init()`` call. The directory to copy is
``node_modules/@ifcopenshell/wasm/wasm``. Keep the files in that relative
layout. Served at ``/wasm/``, these URLs exist:

- ``/wasm/ifcopenshell_plugins.json``
- ``/wasm/ifcopenshell_wasm.wasm``
- ``/wasm/ifcopenshell_wasm.mjs``
- ``/wasm/ifcopenshell_api.mjs``
- ``/wasm/plugins/`` (one ``.wasm`` file per plugin)

The argument to ``resolveUrls`` is that URL, including the trailing slash.
``/wasm/wasm/`` is one directory too deep. The package root, which contains
``browser.js``, is one directory too high.

.. code-block:: javascript

   import { init } from 'ifcopenshell';
   import { resolveUrls } from '@ifcopenshell/wasm';

   const runtime = await init({
     wasmAssets: await resolveUrls('/wasm/'),
   });

Shared memory
~~~~~~~~~~~~~

If your WASM build uses shared memory, serve the application with
``Cross-Origin-Opener-Policy: same-origin`` and
``Cross-Origin-Embedder-Policy: require-corp``. The checkout's
``serve-native-wasm.ps1`` helper serves the native WASM image's browser example
with these headers.

When Node cannot find the package
---------------------------------

``Cannot find module 'ifcopenshell'`` means Node looked upward from the script
and never found ``node_modules``. Put the script in the project directory, or
in a subdirectory of it.

``Cannot find module '@ifcopenshell/wasm'`` means the wrapper loaded, and its
own import did not. A relative import such as
``./node_modules/ifcopenshell/dist/index.js`` resolves the wrapper file and
then stops using the project's ``node_modules``. The import that resolves is
the package name ``ifcopenshell``. Installing the wrapper from a checkout
without also installing ``@ifcopenshell/wasm`` leaves that dependency for npm
to fetch from the registry. The source section installs both directories
together.

``IfcOpenShell WASM artifacts are missing`` means the ``@ifcopenshell/wasm``
package is installed and its ``wasm`` directory is empty. Stage the artifacts
before ``init()``.
