.. This file was generated with the assistance of an AI coding tool.

Running tests
=============

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
