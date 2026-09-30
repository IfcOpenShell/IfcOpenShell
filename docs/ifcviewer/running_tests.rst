.. This file was generated with the assistance of an AI coding tool.

Running tests
=============

IfcViewer has two test layers:

1. **Desktop tests**: C++ unit tests for the shared viewer core and desktop
   support code.
2. **Web tests**: headless-browser smoke tests for the Emscripten/WebGPU
   frontend.

The desktop tests are in ``src/ifcviewer/tests``. The web tests are in
``src/ifcviewer-web/tests``.

Desktop tests
-------------

The desktop tests are Catch2 executables registered with CTest. They cover
pure viewer logic such as sidecar layout, streaming loaders, selection,
visibility, instance composition, buffer-pool allocation, and viewport camera
state.

Configure a desktop build with viewer tests enabled:

.. code-block:: bash

    cmake -S cmake -B build-viewer-wgpu \
        -G Ninja \
        -DBUILD_BONSAIVIEWER=ON \
        -DBUILD_BONSAIVIEWER_TESTS=ON

Build and run all registered tests:

.. code-block:: bash

    cmake --build build-viewer-wgpu
    ctest --test-dir build-viewer-wgpu --output-on-failure

To run only the IfcViewer tests, filter by test name:

.. code-block:: bash

    ctest --test-dir build-viewer-wgpu -R "test_(sidecar|streaming|selection|visibility|buffer|viewport|federation|instance|chunk|lod)" --output-on-failure

You can also build or run a single test executable directly:

.. code-block:: bash

    cmake --build build-viewer-wgpu --target test_sidecar_cache
    ./build-viewer-wgpu/ifcviewer/tests/test_sidecar_cache

Common test targets include:

* ``test_sidecar_compress``
* ``test_sidecar_cache``
* ``test_streaming_loader``
* ``test_instanced_geometry``
* ``test_chunk_planner``
* ``test_sidecar_layout``
* ``test_instance_compose``
* ``test_selection``
* ``test_visibility``
* ``test_buffer_pool``
* ``test_viewport_camera``
* ``test_federation``

Web tests
---------

The web tests are Playwright smoke tests for the WebGPU/Emscripten build. They
load the built page in Chrome, wait for WebGPU initialisation, and assert that
the embedded sample renders non-blank, interactions change the framebuffer,
and no uncaptured WebGPU errors are logged.

First build the web viewer from the repository root. This requires an
Emscripten environment:

.. code-block:: bash

    source /path/to/emsdk_env.sh
    emcmake cmake -S src/ifcviewer-web -B build-web
    ninja -C build-web IfcViewerWeb

Install the web test dependencies once:

.. code-block:: bash

    cd src/ifcviewer-web/tests
    npm install

Run the web smoke tests:

.. code-block:: bash

    npm test

The Playwright configuration starts ``serve.mjs`` automatically. The server
serves ``build-web`` on ``http://localhost:8124``. Override the build directory
or port with environment variables:

.. code-block:: bash

    WEB_BUILD_DIR=/path/to/build-web PORT=9000 npm test

Chrome requirements
~~~~~~~~~~~~~~~~~~~

The test configuration uses the system Chrome channel, so a system Chrome such
as ``google-chrome-stable`` must be installed. You do not need to run
``npx playwright install`` unless you change the Playwright browser channel.

Headless and CI runs
~~~~~~~~~~~~~~~~~~~~

WebGPU in headless Linux environments can be sensitive to the GPU and browser
configuration. The default configuration runs headed against the machine's real
GPU. On a headless machine, use Xvfb:

.. code-block:: bash

    xvfb-run -a npm test

For a GPU-less runner, change ``headless`` to ``true`` in
``playwright.config.mjs`` and provide a SwiftShader Vulkan ICD, for example via
``VK_ICD_FILENAMES=/path/to/vk_swiftshader_icd.json`` together with a Chrome
``--use-angle=swiftshader`` argument. This is slower than a real GPU but is
enough for render-non-blank smoke checks.
