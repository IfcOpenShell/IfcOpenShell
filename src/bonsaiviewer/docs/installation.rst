Developer installation
======================

This page is for developers who want to compile Bonsai Viewer from source.
End users should install a packaged release rather than building it themselves.

Bonsai Viewer is a native C++ application (Qt6 + WebGPU) built together with
the rest of IfcOpenShell. It is not a Blender add-on, so — unlike Bonsai —
there is no "live development" symlink workflow: you rebuild the binary after
changing the code.

System requirements
-------------------

- A 64-bit Linux, macOS, or Windows host.
- A C++17 compiler, CMake 3.21 or newer, and Ninja.
- Qt6 with OpenGL 4.5 support (``BUILD_BONSAIVIEWER`` requires it).
- The IfcOpenShell geometry dependencies (Boost, OpenCASCADE, Eigen, CGAL,
  GMP/MPFR) and the viewer's sidecar/kernel dependencies (RocksDB, zstd,
  Manifold).

The viewer is built on the IfcViewer library. If you want to build your own
application on that library instead of the ready-made Bonsai Viewer, see
"Building with IfcViewer" in the IfcOpenShell documentation (under
``src/ifcopenshell-python/docs/ifcviewer``).

Batteries-included build
------------------------

The simplest way to get a working build — and the one continuous integration
uses — is ``nix/build-all.py``. It downloads and compiles every dependency
(including Qt6) and then Bonsai Viewer itself. From the repository root:

.. code-block:: bash

    python3 ./nix/build-all.py

By default, the script pulls in the ``BonsaiViewer`` and ``qt6``
targets along with their dependencies. This is self-contained but slow on a
cold checkout, because it builds the whole dependency stack from source. The
finished executable lands under the platform build tree, e.g.
``build/<system>/<arch>/install/ifcopenshell/bin/BonsaiViewer``.

Direct CMake build
------------------

If you already have Qt6 and the geometry dependencies available (for example
from a previous ``build-all.py`` run), you can configure and build the app
directly against them. ``BUILD_BONSAIVIEWER`` implies
``BUILD_BONSAIVIEWER_WGPU``, so the WebGPU backend is built automatically:

.. code-block:: bash

    cmake -S cmake -B build-viewer \
        -G Ninja \
        -DCMAKE_BUILD_TYPE=Debug \
        -DBUILD_BONSAIVIEWER=ON \
        -DCMAKE_PREFIX_PATH="/path/to/deps"

    cmake --build build-viewer --target BonsaiViewer

Set ``-DCMAKE_PREFIX_PATH`` to a ``;``-separated list of your dependency
install prefixes (Boost, OpenCASCADE, CGAL, Eigen, GMP/MPFR, Manifold,
RocksDB, zstd) so CMake can find them. Other useful targets are ``IfcViewer``
(the shared engine library) and ``IfcViewerMinimal`` (a small standalone
frontend).

To also build the C++ unit tests for the viewer core, add
``-DBUILD_BONSAIVIEWER_TESTS=ON`` and run them with CTest.

Running from source
-------------------

Run the built binary directly:

.. code-block:: bash

    ./build-viewer/bonsaiviewer/BonsaiViewer

Runtime behaviour can be tuned with environment variables (logging, geometry
kernel selection, and other diagnostics) — see :doc:`env-vars` and
:doc:`debug-output`. For an overview of how the rendering and viewport code is
organised, see :doc:`viewport_architecture`.

The Autodesk connector
----------------------

Bonsai Viewer discovers connectors at ``<BonsaiViewer dir>/connectors``. The
Autodesk connector is a separate Rust crate under ``src/bonsaiviewer-autodesk``
and is built with ``cargo`` (its packaging step is run by
``src/bonsaiviewer-autodesk/packaging/build.py``). For a local debug build,
symlink the built connector into the viewer's ``connectors`` directory so the
running app can find it. See :doc:`connectors/index` for details.
