Viewport architecture
=====================

This page documents the IFC viewer renderer that lives at
``src/ifcviewer/`` and underpins both BonsaiViewer and the standalone
``IfcViewerMinimal`` testbed.

Consumers
---------

``src/ifcviewer/`` is a static library (``IfcViewer``) — it does not
ship as an executable on its own. Two consumers link against it:

* **BonsaiViewer** (``src/bonsaiviewer/``) — full project shell with
  side panels, federation tree, settings dialog, connector picker,
  ribbon. The end-user product.
* **IfcViewerMinimal** (``src/ifcviewer-minimal/``) — single-file
  testbed that opens an IFC, a ``.ifcview`` sidecar, or a federation
  ``.ifcfed`` and shows just the viewport. Used for screenshot
  regression tests, benchmarks, and isolating renderer-only issues
  from the Bonsai Viewer shell.

Stack
-----

* **wgpu-native v29** for rendering, fetched as a pre-built binary in
  ``src/ifcviewer/CMakeLists.txt``. WebGPU API on top of Vulkan
  (Linux/Windows) or Metal (macOS, via the ``MetalSurface_mac``
  Cocoa bridge).
* **Qt6** for windowing (a raw ``QWindow``, not ``QOpenGLWidget``)
  and the surface integration with the OS. Qt is also the source of
  ``QSettings`` for persisted user preferences (``AppSettings``),
  the event loop driving render scheduling, and the timer/elapsed
  primitives used in instrumentation.
* **IfcOpenShell C++ libs** (IfcParse / IfcGeom) for IFC parsing and
  geometry generation, plus **helpers** for the schema-agnostic
  helpers (``unit``, ``geolocation``, ``placement``).
* **Eigen3** for 4×4 matrices and small linear algebra.
* **meshoptimizer** at sidecar-build time only — decimates each
  unique mesh into an LOD1 slice. Not pulled at runtime.

Five core ideas
---------------

The renderer is built around five decisions worth knowing about
before reading the code:

**1. Unique-mesh GPU instancing.** IFC scenes are dominated by
repeated geometry (identical doors, windows, studs, pipes, …). The
``IfcGeom::Iterator`` surfaces representation identity, so each
unique mesh is uploaded once into a per-model vertex buffer slice
and every placement becomes a tiny ``InstanceCpu`` record
(transform + ``object_id`` + optional colour override). On a 1 M-
placement BIM scene this collapses tens of millions of duplicate
vertices into a few hundred MB of unique meshes.

**2. Quantized 12-byte vertex format.** Each vertex is exactly 12
bytes:

.. code-block:: text

   offset 0   pos     3 × uint16   normalised → mix(mesh.aabb_min, mesh.aabb_max, t)
   offset 6   normal  2 × int8     normalised → [-1,1]; octahedral-decoded
   offset 8   color   4 × uint8    normalised → [0,1]; alpha is real (see "Transparency")

The dequantisation basis is per-mesh, uploaded once in a
``MeshGpu`` SSBO at binding 2; the vertex shader reads it via the
mesh index that comes through the visible-draws table. ``int8``
normals carry ~1.4° worst-case angular error, invisible for the
overwhelmingly axis-aligned faces (walls, floors, slabs) BIM models
produce.

**3. Streaming chunked storage backed by a probed VRAM pool.** Per-
model state isn't loaded all at once. The sidecar's vertex/index
data is split into spatially-coherent chunks (Morton-sorted at bake
time, packed greedily); ``ViewportWindow`` keeps each chunk's bytes
resident in a single GPU buffer pool whose size is determined at
startup by ``wgpuDevicePushErrorScope(OutOfMemory)`` probing. As
the camera moves, chunks page in and out via the
``StreamingThread`` background worker; the render thread never
issues a blocking disk read.

**4. Sidecar cache as the fast path.** Loading an IFC the first
time runs the ``IfcGeom::Iterator`` (expensive); the result is
serialised to a ``.ifcview`` file (``SIDECAR_VERSION = 13``) next
to the source. Subsequent opens go straight from disk to GPU
buffers — no iteration, no geometry-engine cost. The sidecar
format embeds chunked vertex sections with a byte-range table of
contents so the streaming thread can fetch any chunk by ``pread``
without scanning the file.

**5. Event-driven rendering.** No render timer. Frames are
scheduled only via ``QWindow::requestUpdate()`` when something
actually changes — camera motion, streaming chunk arrival, hover,
selection, settings edits. When the camera is idle, the cull pass
short-circuits and the main thread blocks in the Qt event loop;
the viewer costs zero CPU/GPU on a static scene.

Per-frame pipeline
------------------

Each call to ``ViewportWindow::render()`` runs the same six phases:

.. code-block:: text

   render():
     1. fpsIntegrate()            ← advance fly-mode camera by wall-clock dt
     2. drainHizReadbacks()       ← absorb HiZ readback completions
     3. uploadSelectionFlagsIfDirty()
     4. cullModelCpuCompute()     ← parallel per-model frustum+contrib+HiZ+LOD
        cullModelCpuUpload()      ← writeBuffer visible-draws + prefix-sums
     5. driveStreamingLoads()     ← enqueue chunk fetches, apply completions
     6. encode passes:
          opaque main      (depthWriteEnabled=True, no blend)
          transparent main (depthWriteEnabled=True, SrcAlpha/InvSrcAlpha blend)
          edge silhouette  (samples depth buffer)
          overlay (HUD, labels, gizmos, measurements, marquee)
        wgpuSurfacePresent()

The two-pass alpha split (#6) routes each visible instance into
either the opaque half or the transparent half of the per-chunk
``visible_draws_scratch`` based on a per-mesh ``has_alpha`` flag +
the instance's ``color_override_rgba8`` alpha byte. The transparent
pass uses the same buffers, just with ``firstVertex`` offset to the
opaque half's end. ``Alt+X`` forces every instance through the
transparent pass via the ``xray_alpha_cap`` frame uniform, giving a
free X-ray mode.

Cull
~~~~

CPU-side, runs parallel per model via ``std::async``. The cascade
per instance is:

1. **Chunk-level frustum cull** — each chunk's AABB is tested first;
   off-frustum chunks skip every instance inside them in one shot.
2. **Per-instance frustum cull** — for chunks that pass.
3. **Contribution cull** — instances whose sphere projects below
   ``viewport/min_pixel_radius`` (stationary) or
   ``viewport/motion_min_pixel_radius`` (during motion) get dropped.
4. **HiZ occlusion** — projected AABB tested against the previous
   frame's depth pyramid, when the VP matches. The pyramid is
   captured at end-of-frame, downsampled, read back to CPU, and
   queried with conservative all-fine-texels-agree semantics. Off
   by default; ``WGPU_HIZ=1`` re-enables.
5. **LOD selection** — instances with sub-``viewport/lod1_pixel_threshold``
   projected size and an available LOD1 slice route through the
   LOD1 index range. Same vertex buffer, different ``firstIndex``.

Survivors are appended to the chunk's ``visible_draws_scratch`` and
cumulative ``prefix_sums_scratch`` — the vertex shader uses a
binary search on prefix_sums to translate ``vertex_index`` into a
``(draw_index, vertex_in_draw)`` pair.

Streaming
~~~~~~~~~

The buffer pool (``BufferPool``) is a free-list sub-allocator over
one or more wgpu buffers, sized at startup by probing for
``WGPUErrorType_OutOfMemory`` on a series of growing allocations.
``StreamingThread`` is one worker thread that owns disk I/O:
``driveStreamingLoads()`` posts requests for the highest-priority
non-resident chunks and drains completions. The pool's eviction
policy is "evict the lowest-priority resident chunk whose priority
is below ``candidate_priority / EVICT_PRIORITY_RATIO``" — strict
enough to prevent thrash, lax enough that a single panning frame
doesn't refuse the move.

Priorities come from a per-chunk screen-space score computed during
cull (chunk AABB projected to a screen-rect area). Spatial sort at
bake time means screen-adjacent chunks are byte-adjacent on disk,
so the typical fetch is a single ``pread`` range, not scatter-
gather.

Overlay / picking / section cuts
--------------------------------

* ``OverlayRenderer`` runs after the main passes. Bundles the HUD
  text, world-anchored labels (measurement readouts), the
  marquee-select rect, the corner axis gizmo, the orbit pivot
  indicator, and section-plane outline rendering. Has its own
  pipelines with the usual ``SrcAlpha/OneMinusSrcAlpha`` blend.
* **Picking** is a second render pass with a dedicated pipeline
  writing object IDs into an ``R32UInt`` framebuffer. Clicking
  triggers a ``wgpuQueueOnSubmittedWorkDone`` + ``mapAsync``
  readback of one pixel. No CPU-side raycasting.
* **Section cuts** (the ``K`` tool) push up to six clipping planes
  into the frame uniform; ``is_section_clipped()`` in WGSL discards
  fragments on the positive side. The plane gizmo and visible
  cross-section outline come from OverlayRenderer.

Federation
----------

``Federation`` (in ``IfcViewer``, not Bonsai) is the multi-model
data model. Each model in a federation has a fed_id, optional
group membership, an explicit ``ModelTransformation``, a
``CoordinateOperation`` (from the IFC's IfcMapConversion), and a
visibility flag. The viewport composes a single
``transform_meters`` per instance as:

.. code-block:: text

   federated_false_origin · model_transformation · coord_op · placement

``federated_false_origin`` is shared across all models in the
session and cancels the bulk of the big surveyor coordinates BIM
files carry, so float32 vertex math stays well within precision.
The first-added model's first geometry point auto-seeds the false
origin via ``ViewportView::guessFederatedFalseOriginFromFirstModel``
when the add-model command arms the guess; see that function for
why the arm/consume mechanism exists (it replaced a stack-
overflowing slot-emit-in-slot recursion).

Files map
---------

Render core (the wgpu side):

* ``ViewportWindow.{h,cpp}`` — the main render window. Owns the
  wgpu surface, device, queue, all pipelines, the per-model
  ``ModelGpuData``, the cull pass, the frame uniforms. ~7500 lines;
  the bulk of the renderer.
* ``ModelGpuData.h`` — per-model GPU state (chunks, instances,
  meshes, pool slices, alpha flags, scratch buffers used by cull).
* ``InstancedGeometry.h`` — wire structs shared by the streamer
  and the viewport (``MeshInfo``, ``InstanceCpu``, ``InstanceGpu``,
  ``MeshChunk``, ``InstanceChunk``, vertex layout constants).
* ``VertexQuantization.h`` — pack/unpack helpers for the 12-byte
  vertex format.
* ``BufferPool.{h,cpp}`` — VRAM sub-allocator with multi-sub-buffer
  growth.
* ``StreamingThread.{h,cpp}`` — background ``pread`` worker.
* ``StreamingLoader.{h,cpp}`` — chunk-priority planner driving the
  thread; owns the eviction policy and the residency map.
* ``OverlayRenderer.{h,cpp}`` — HUD / labels / gizmos / section-cut
  outline / marquee. Separate pipelines + WGSL shader strings.
* ``MetalSurface_mac.{h,mm}`` — Cocoa bridge for the CAMetalLayer
  surface attach on macOS. Compiled only on Apple via the
  ``OBJCXX`` language CMake enables.
* ``SelectionState.h``, ``VisibilityState.h`` — pure CPU state
  machines for the selection set and the hidden-objects set;
  header-only; covered by ``ifcviewer/tests/test_selection.cpp``
  and ``test_visibility.cpp``.
* ``AreaMeasurement.{h,cpp}``, ``LengthMeasurement.{h,cpp}`` — the
  measurement tools (triangle-area accumulation; world-space
  polyline distance).

IFC ingestion and on-disk format:

* ``GeometryStreamer.{h,cpp}`` — wraps ``IfcGeom::Iterator`` on a
  background thread; emits ``MeshChunk`` (unique geometry) and
  ``InstanceChunk`` (one per placement) to ``SceneLoader``.
* ``SceneLoader.{h,cpp}`` — orchestrates load. Owns the per-model
  ``ifcopenshell::file`` for property lookup; detects sidecar
  presence; serialises queue of pending loads.
* ``SidecarCache.{h,cpp}`` — binary read/write of ``.ifcview``
  files. Magic ``IFVW``, version 13 (see the per-version comment
  block at the top of the header for the schema evolution).
* ``SidecarBuilder.{h,cpp}`` — live-load sidecar writer. Accumulates
  the data as the streamer emits it, writes the sidecar after
  ``finalizeModel``.
* ``LodBuilder.{h,cpp}`` — meshoptimizer wrapper that builds each
  mesh's LOD1 index slice at sidecar-bake time. Gated behind
  ``WITH_MESH_OPTIMIZER``; otherwise the LOD1 slot is left empty
  and the renderer always uses LOD0.

Federation + settings:

* ``Federation.{h,cpp}`` — multi-model session: groups, model
  transforms, coordinate operations, the federated false origin.
  Persisted as ``.ifcfed``. Covered by
  ``ifcviewer/tests/test_federation.cpp``.
* ``AppSettings.{h,cpp}`` — ``QSettings``-backed preferences:
  ``viewport/min_pixel_radius``, ``viewport/lod1_pixel_threshold``,
  ``viewport/hiz_enabled``, ``viewport/nav_preset``, etc. See
  :doc:`env-vars` for the full key list.
