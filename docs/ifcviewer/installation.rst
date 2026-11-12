.. This file was generated with the assistance of an AI coding tool.

Building with IfcViewer
=======================

IfcViewer is a **library**, not an end-user application. It provides the
WebGPU rendering engine and the model loading, sidecar, streaming, selection,
visibility, and viewport-state machinery that Bonsai Viewer is built on, and
it is meant to be embedded in your own applications. This page is for
developers who want to build their own viewer on top of it.

There are two ways to consume it, from two separate CMake roots:

* a native **desktop** library (``IfcViewer`` / ``IfcViewerCore``) that you
  link into a C++ application, and
* a **web** build that compiles the same portable core to WebAssembly and
  exposes it to JavaScript, so you can drop the viewer into a web page.

If you instead want to compile the ready-made Bonsai Viewer desktop
application, see the Bonsai Viewer developer documentation (under
``src/bonsaiviewer/docs``) rather than this page.

Compiling for desktop
---------------------

The desktop side ships as two static libraries, built from
``src/ifcviewer/CMakeLists.txt``:

``IfcViewerCore``
    The portable runtime subset — Qt-free and OpenCASCADE-free. It contains
    the buffer-pool allocator, sidecar cache/layout, streaming loader,
    instance composition, selection, visibility, and viewport camera state.
    This is the same library the web build uses.

``IfcViewer``
    ``IfcViewerCore`` plus the desktop-only, Qt-coupled layer — the WebGPU
    surface creation, the ``ViewportWindow`` widget, and platform input
    handling. Link this if you are writing a Qt desktop frontend.

Prerequisites are a C++17 compiler, CMake 3.21 or newer, Ninja, and — for the
full ``IfcViewer`` target — Qt6 with OpenGL 4.5 support. ``IfcViewerCore``
additionally uses zstd (and, where enabled, Manifold/RocksDB for the sidecar
formats); these come along when you build IfcOpenShell.

Because the viewer targets live inside the IfcOpenShell source tree, the
simplest way to build against them from your own project is to add the
directory as a subproject and link the target you need:

.. code-block:: cmake

    # In your own CMakeLists.txt
    add_subdirectory(path/to/IfcOpenShell/src/ifcviewer ifcviewer)

    add_executable(my_viewer main.cpp)
    target_link_libraries(my_viewer PRIVATE IfcViewer)      # or IfcViewerCore

The targets carry their public include directory as a usage requirement, so
``#include`` paths resolve automatically once you link them.

Two reference frontends in the tree show the intended integration and are the
best starting points to copy from:

* ``IfcViewerMinimal`` — a small standalone desktop frontend built on
  ``IfcViewer``.
* ``src/ifcviewer-web/main_web.cpp`` — the web scaffold built on
  ``IfcViewerCore`` (see the next section).

Compiling for the web
---------------------

The web build compiles ``IfcViewerCore`` to WebAssembly with the `Emscripten
SDK <https://emscripten.org/docs/getting_started/downloads.html>`_ and renders
through WebGPU via Emscripten's ``emdawnwebgpu`` (Dawn) port. It uses neither
Qt nor OpenCASCADE. You will need a recent Emscripten SDK to build, and a
WebGPU-capable browser (current Chrome or Edge, or Firefox Nightly) to run the
result.

Building the module
~~~~~~~~~~~~~~~~~~~~

Activate your Emscripten environment, then configure and build the separate
web CMake root from the repository root:

.. code-block:: bash

    source /path/to/emsdk_env.sh
    emcmake cmake -S src/ifcviewer-web -B build-web -G Ninja
    ninja -C build-web

The build must be configured through ``emcmake``; the CMake root fails fast
with a clear error if invoked with a non-Emscripten toolchain.

It emits a ``MODULARIZE`` module — ``IfcViewerWeb.js`` (which defines the
global ``createIfcViewer`` factory) and ``IfcViewerWeb.wasm`` — and copies a
small integration helper (``ifcviewer.js``) and two example pages next to
them. Everything in ``build-web/`` is static; serve it over ``http://localhost``
or ``https://`` (WebGPU requires a `secure context
<https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts>`_):

.. code-block:: bash

    python3 -m http.server --directory build-web 8080
    # then open http://localhost:8080/

Embedding in your own page
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ifcviewer.js`` is a thin wrapper over the raw Emscripten module that exposes
a small ``IfcViewer`` JavaScript API. Load ``IfcViewerWeb.js`` first, then
``ifcviewer.js``, and give your canvas ``id="viewer-canvas"`` (the wasm side
hard-codes that selector for its WebGPU surface and input handlers):

.. code-block:: html

    <canvas id="viewer-canvas" width="960" height="600"></canvas>

    <script src="IfcViewerWeb.js"></script>
    <script src="ifcviewer.js"></script>
    <script>
      const canvas = document.getElementById('viewer-canvas');
      const viewer = await IfcViewer.create({ canvas });
      await viewer.ready;                     // GPU app is live

      // React to picks in the scene.
      viewer.onSelect(({ objectId, guid, modelIndex }) => {
        console.log('selected', guid, 'in model', modelIndex);
      });

      // Load a first model (drops any current scene), then federate another.
      await viewer.addUrl('/model.ifcview', { replace: true });
      await viewer.addUrl('/second.ifcview');   // appends
    </script>

The API object returned by ``IfcViewer.create`` includes:

* ``ready`` — a promise that resolves once the GPU app is initialised.
* ``onSelect(cb)`` — register a pick listener ``({ objectId, guid,
  modelIndex })``; returns an unsubscribe function. A ``ifcviewer:select``
  DOM event is also dispatched.
* ``addFile(file, { replace })`` / ``addUrl(url, { replace })`` — add a model
  from a picked ``File`` (read lazily via ``Blob.slice``) or a remote
  ``.ifcview`` URL (read lazily via HTTP range requests). Without
  ``replace: true`` the model is appended, giving a lightweight federation.
* ``clearScene()``, ``viewAll()``, ``frameSelection()`` — scene and camera
  controls.
* ``modelCount()``, ``modelProgress(i)``, ``bytes()`` — streaming/loading
  progress for building your own UI.

The bundled ``embedded.html`` is a complete, commented reference: it embeds
the viewer as a sized page element and uses plain DOM around it to add models
(by file or URL), list the loaded models with streaming progress, and display
the GlobalId of the clicked object. ``IfcViewerWeb.html`` is a fullscreen
variant. Both are good templates to start from.

For the headless-browser smoke tests that exercise this build, see
:doc:`running_tests`.
