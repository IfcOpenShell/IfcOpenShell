.. This file was generated with the assistance of an AI coding tool.

Running the tests
=================

Each language has its own test suite for the library, and every code block in
these guides is cut from a program which is run by a test suite as well.

Documentation examples
----------------------

The example programs live in ``docs/ifcopenshell/examples``, with one directory
per guide and the three languages side by side. Each program takes the path of
an IFC model as its first argument, and exits with a non-zero code when a check
fails. The models are in ``docs/ifcopenshell/examples/models``.

Python
~~~~~~

The Python programs run against the installed ``ifcopenshell``:

.. code-block:: shell

    cd docs/ifcopenshell/examples
    python -m pytest

A program whose header says ``Requires IfcOpenShell 0.9`` is skipped on older
versions.

.. _building-and-running-the-examples:

C++
~~~

The C++ programs are a standalone CMake project which consumes an installed
IfcOpenShell through ``find_package(IfcOpenShell CONFIG)``, the same way any
other third party consumer would. Every program is registered as a CTest test:

.. code-block:: shell

    cd docs/ifcopenshell/examples
    cmake -S . -B build -DCMAKE_PREFIX_PATH=/path/to/ifcopenshell
    cmake --build build --config RelWithDebInfo
    ctest --test-dir build -C RelWithDebInfo --output-on-failure

There is also a single custom command which builds and runs all of them at
once, and which fails if any of the examples reports a failure:

.. code-block:: shell

    cmake --build build --config RelWithDebInfo --target run_examples

JavaScript
~~~~~~~~~~

The JavaScript programs are run by ``tests/doc-examples.test.ts`` of the
``ifcopenshell`` package, after staging the WebAssembly files as described
below, and are linted with their own ESLint configuration:

.. code-block:: shell

    cd src/ts/ifcopenshell-js
    npm test -- tests/doc-examples.test.ts
    npm run lint:docs

IfcOpenShell-Python
-------------------

IfcOpenShell-Python tests live in ``src/ifcopenshell-python/test`` and use
``pytest``. From the repository root, enter the Python package directory before
running the test suite:

.. code-block:: bash

    cd src/ifcopenshell-python

Install the test runner in the Python environment you are using for
development:

.. code-block:: bash

    pip install pytest

Full test suite
---------------

Use the Makefile target for the default test suite:

.. code-block:: bash

    make test

This runs:

.. code-block:: bash

    pytest -p no:pytest-blender test

The ``pytest-blender`` plugin is disabled because these are IfcOpenShell-Python
tests, not Bonsai Blender tests.

Parallel tests
--------------

For a faster local run, install ``pytest-xdist`` and use the parallel target:

.. code-block:: bash

    pip install pytest-xdist
    make test-parallel

This automatically uses the available CPU count and runs the same tests as
``make test``.

Shape builder tests
-------------------

Most of ``ifcopenshell.util.shape_builder`` is covered here, but the tests
that check its ``mathutils``-compatible helpers live in the Bonsai test suite instead,
since they need Blender's ``mathutils`` package. See ``src/bonsai/test/tool/test_shape_builder.py``.

Running individual tests
------------------------

You can run an individual file or test directly with ``pytest``:

.. code-block:: bash

    pytest -p no:pytest-blender test/test_file.py
    pytest -p no:pytest-blender test/util/test_unit.py
    pytest -p no:pytest-blender test/test_file.py::TestFile::test_creating_a_new_file

Coverage
--------

To generate an HTML coverage report, install ``coverage`` and run:

.. code-block:: bash

    pip install coverage
    make coverage

The report is written to ``htmlcov``.

IfcOpenShell JS/TS
------------------

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
