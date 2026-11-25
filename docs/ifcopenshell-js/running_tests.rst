.. This file was generated with the assistance of an AI coding tool.

Running tests
=============

From the repository root, stage the native WASM artifacts and run the
JavaScript/TypeScript package's tests:

.. code-block:: shell

   cd src/ts/ifcopenshell-wasm
   npm ci
   npm run stage
   cd ../ifcopenshell-js
   npm ci
   npm run build
   npm test

Set ``IFCOPENSHELL_WASM_DIR`` to the directory containing
``ifcopenshell_api.mjs``, ``ifcopenshell_wasm.node.mjs``,
``ifcopenshell_wasm.wasm``, and ``ifcopenshell_plugins.json`` before running
the tests. Tests requiring native WASM artifacts are skipped when this
variable is unset or the required files are absent.

To run a particular group, pass its filename to Vitest:

.. code-block:: shell

   npm test -- tests/io.test.ts
   npm test -- tests/geom/shape.test.ts

The browser suite uses Playwright and runs separately:

.. code-block:: shell

   npx playwright install chromium
   npm run test:browser

Check the TypeScript API documentation and generate its Sphinx source pages:

.. code-block:: shell

   npm run docs:check
   npm run docs:sphinx

See the repository's ``docs/README.md`` for building and serving the combined
C++, Python, and TypeScript documentation site.
