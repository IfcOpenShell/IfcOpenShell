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
   * - ``.github/workflows/ci-lint.yaml``
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
   * - ``.github/workflows/ci-bonsai.yml``
     - ``pyver`` matrix
   * - ``.github/workflows/ci-bonsai-daily.yml``
     - Blender download URL

Blender's Bundled Python Version Updated
-----------------------------------------

When Blender ships with a new Python version:

.. list-table::
   :header-rows: 1

   * - File
     - What to update
   * - ``.github/workflows/ci-lint.yaml``
     - ``MIN_BLENDER_PY_VERSION``
   * - ``.github/scripts/publish-bonsai-releases.py``
     - ``CURRENT_PYTHON_VERSION``
   * - ``src/bonsai/Makefile``
     - ``SUPPORTED_PYVERSIONS``
   * - ``src/bonsai/scripts/dev_environment.py``
     - ``PYTHON_VERSION`` mapping (Blender version, bundled Python version)

Release
-------

Notes:

- Typically all packages are released at once using the same version schema
- The ``README.md`` badges can serve as a visual reference for what versions have been released
- Corrective Release (if needed after a standard release):

  - Create a new branch from the release tag (e.g., from the ``ifcopenshell-0.8.5`` tag)
  - Update ``VERSION`` with the ``-post1`` suffix (e.g., ``0.8.5-post1``, **not** ``.post1``)
  - The hyphen is required for semantic versioning compliance; Blender will not process ``.post1`` suffixes correctly
  - Follow the standard release process for the corrective version

- Multiple Blender Python Versions:

  - Blender does not allow multiple builds for the same platform with different Python versions (e.g., cannot have both ``bonsai_py311-0.8.5-windows-x64.zip`` and ``bonsai_py313-0.8.5-windows-x64.zip``)
  - Workaround: publish different Python versions as different extension versions (e.g., py313 as ``0.8.5`` and py311 as ``0.8.5-post1``)
  - Set the maximum Blender version on the Blender extensions platform UI to prevent conflicts (e.g., set max version ``5.1.0`` for ``0.8.5-post1``, which restricts it to versions below 5.1.0)

Things to update:

- ``.github/workflows/ci-bcf-pypi.yml`` - release `bcf-client <https://pypi.org/project/bcf-client/>`_ to PyPI
- ``.github/workflows/ci-bonsai.yml`` - release bonsai in GitHub releases
- ``.github/workflows/ci-bsdd-pypi.yaml`` - release `bsdd <https://pypi.org/project/bsdd/>`_ to PyPI
- ``.github/workflows/ci-ifc4d-pypi.yaml`` - release `ifc4d <https://pypi.org/project/ifc4d/>`_ to PyPI
- ``.github/workflows/ci-ifc5d-pypi.yaml`` - release `ifc5d <https://pypi.org/project/ifc5d/>`_ to PyPI
- ``.github/workflows/ci-ifcclash-pypi.yaml`` - release `ifcclash <https://pypi.org/project/ifcclash/>`_ to PyPI
- ``.github/workflows/ci-ifcconvert.yml`` - release ifcconvert binaries in GitHub releases
- ``.github/workflows/ci-ifccsv-pypi.yaml`` - release `ifccsv <https://pypi.org/project/ifccsv/>`_ to PyPI
- ``.github/workflows/ci-ifcdiff-pypi.yaml`` - release `ifcdiff <https://pypi.org/project/ifcdiff/>`_ to PyPI
- ``.github/workflows/ci-ifcedit-pypi.yaml`` - release `ifcedit <https://pypi.org/project/ifcedit/>`_ to PyPI
- ``.github/workflows/ci-ifcfm-pypi.yaml`` - release `ifcfm <https://pypi.org/project/ifcfm/>`_ to PyPI
- ``.github/workflows/ci-ifccityjson-pypi.yaml`` - release `ifccityjson <https://pypi.org/project/ifccityjson/>`_ to PyPI
- ``.github/workflows/ci-ifcmcp-pypi.yaml`` - release `ifcopenshell-mcp <https://pypi.org/project/ifcopenshell-mcp/>`_ to PyPI
- ``.github/workflows/ci-ifcopenshell-python.yml`` - release ifcopenshell-python binaries in GitHub releases
- ``.github/workflows/ci-ifcopenshell-python-pypi.yml`` - release `ifcopenshell <https://pypi.org/project/ifcopenshell/>`_ wheels to PyPI
- ``.github/workflows/ci-ifcpatch-pypi.yaml`` - release `ifcpatch <https://pypi.org/project/ifcpatch/>`_ to PyPI
- ``.github/workflows/ci-ifcquery-pypi.yaml`` - release `ifcquery <https://pypi.org/project/ifcquery/>`_ to PyPI
- ``.github/workflows/ci-ifcsverchok.yml`` - release ifcsverchok Blender add-on in GitHub releases
- ``.github/workflows/ci-ifctester-pypi.yml`` - release `ifctester <https://pypi.org/project/ifctester/>`_ to PyPI
- ``.github/workflows/ci-pyodide-wasm-release.yml`` - release pyodide wasm wheel to `wasm-wheels <https://github.com/IfcOpenShell/wasm-wheels>`_
- ``.github/workflows/publish-bonsai-releases.yml`` - publish Bonsai Blender extension to `Blender extensions platform <https://extensions.blender.org/add-ons/bonsai/>`_

  - ❗ Requires ``BLENDER_EXTENSIONS_TOKEN`` secret to be set - ❗ not yet configured

- Publishing documentation and websites (see `website <https://github.com/IfcOpenShell/website>`_ repository):

  - `ifcopenshell-docs.yml` - builds and publishes IfcOpenShell documentation to `docs.ifcopenshell.org <https://docs.ifcopenshell.org>`_ (`ifcopenshell_org_docs <https://github.com/IfcOpenShell/ifcopenshell_org_docs>`_ repo)
  - `bonsai-docs.yml` - builds and publishes Bonsai documentation to `docs.bonsaibim.org <https://docs.bonsaibim.org>`_ (`bonsaibim_org_docs <https://github.com/IfcOpenShell/bonsaibim_org_docs>`_ repo)
  - `publish-websites.yml` - publishes `bonsaibim.org <https://bonsaibim.org>`_ (`bonsaibim_org_static_html <https://github.com/IfcOpenShell/bonsaibim_org_static_html>`_ repo) and `ifcopenshell.org <https://ifcopenshell.org>`_ (`ifcopenshell_org_static_html <https://github.com/IfcOpenShell/ifcopenshell_org_static_html>`_ repo)
- ``VERSION`` to the release version - **UPDATE THIS LAST** as all workflows above typically depend on it to set the version correctly
