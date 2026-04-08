Maintenance
===========

This page documents what needs to be updated in various maintenance scenarios.

Python Version Added or Removed
--------------------------------

When adding or removing a supported Python version, update the following:

.. list-table::
   :header-rows: 1

   * - File
     - What to update
   * - ``.github/workflows/ci-black-formatting.yaml``
     - ``MIN_IOS_PY_VERSION``
   * - ``.github/workflows/ci-ifcopenshell-python-pypi.yml``
     - ``pyver`` matrix
   * - ``.github/workflows/ci-ifcopenshell-python.yml``
     - ``pyver`` matrix
   * - ``nix/build-all.py``
     - ``PYTHON_VERSIONS`` list
   * - ``src/bsdd/pyproject.toml``
     - ``requires-python``
   * - ``src/ifcopenshell-python/docs/ifcopenshell-python/installation.rst``
     - add or remove the row in the ZIP packages table
   * - ``src/ifcopenshell-python/Makefile``
     - ``SUPPORTED_PYVERSIONS``
   * - ``src/ifcopenshell-python/pyproject.toml``
     - ``requires-python``
   * - ``src/ifcopenshell-python/test/test_package.py``
     - ``SUPPORTED_PY_VERSIONS`` tuple
   * - ``win/build-all-win.py``
     - ``PYTHON_VERSIONS`` list

Blender Version Updated
-----------------------

When a new Blender version is released and supported:

.. list-table::
   :header-rows: 1

   * - File
     - What to update
   * - ``.github/workflows/ci-bonsai-daily.yml``
     - Blender download URL

Blender's Bundled Python Version Updated
-----------------------------------------

When Blender ships with a new Python version:

.. list-table::
   :header-rows: 1

   * - File
     - What to update
   * - ``.github/workflows/ci-black-formatting.yaml``
     - ``MIN_BLENDER_PY_VERSION``
   * - ``src/bonsai/Makefile``
     - ``SUPPORTED_PYVERSIONS``
   * - ``src/bonsai/scripts/dev_environment.py``
     - ``PYTHON_VERSION`` mapping (Blender version, bundled Python version)
