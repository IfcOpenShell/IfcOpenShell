Viewport architecture
=====================

This page documents the WebGPU IFC viewer renderer in ``src/ifcviewer``. The
same renderer is used by BonsaiViewer, IfcViewerMinimal, and the web build. It
explains the path from an IFC model or ``.ifcview`` cache to rendered triangles,
including the optimisation stages that decide what is loaded, what is resident
in GPU memory, and what is drawn.

Overview
--------

The renderer is built around a small number of data transformations:

.. code-block:: text

   IFC / .ifcview input
       -> SceneLoader
       -> GeometryStreamer or sidecar metadata reader
       -> SidecarData-shaped model metadata
       -> ViewportCore::applyCachedModel()
       -> per-model chunks, mesh table, instance table
       -> cullModelCpuCompute()
       -> visible_draws + prefix_sums
       -> driveStreamingLoads()
       -> applyStreamedChunk()
       -> WebGPU draw() calls
       -> WGSL expands visible draws into indexed triangles

The important split is between **metadata** and **geometry bytes**. Metadata
describes meshes, instances, bounds, transforms, element ids, and chunk layout.
Geometry bytes are the quantised vertices and indices. A sidecar load reads
metadata first and leaves geometry chunks non-resident until the camera needs
them. A direct IFC load builds the same structures from the geometry iterator,
then uploads all chunks at finalisation.

Main components
---------------

``SceneLoader``
    Orchestrates model loading. It first tries to read ``.ifcview`` metadata
    when sidecar reads are enabled. If that fails, it starts the geometry
    streamer. It also keeps the ``ifcopenshell::file`` used by property and UI
    code.

``GeometryStreamer``
    Runs ``IfcGeom::Iterator`` on a worker thread for raw IFC loads. It emits a
    ``StreamedMesh`` once for each unique representation mesh and a
    ``StreamedInstance`` for each placed occurrence.

``SidecarBuilder``
    Optionally mirrors the streamer's output while a raw IFC is loading. It
    writes a new ``.ifcview`` cache after the stream finishes, so the next open
    can use the sidecar fast path.

``ViewportWindow``
    The Qt-facing window wrapper. It owns UI/window integration and forwards
    renderer work to ``ViewportCore``.

``ViewportCore``
    The renderer core. It owns the WebGPU device-facing model state, pipelines,
    chunk residency, culling, streaming, picking, screenshot capture, and render
    loop.

``ModelGpuData``
    Per-model runtime state: mesh metadata, instances, chunks, GPU buffers,
    per-chunk visibility scratch, object lookup maps, and CPU-side caches used
    by tools.

``BufferPool``
    Sub-allocates chunk vertex and index bytes from one or more WebGPU buffers.
    Chunks enter and leave this pool as the streaming system pages geometry in
    and out.

``StreamingThread`` and web range loading
    Desktop sidecar streaming uses a background worker to read and decompress
    chunk frames. The web build uses asynchronous byte-range reads from a
    registered file or URL source.

Load path 1: sidecar hit
------------------------

The fast path starts when ``SceneLoader`` finds a readable ``.ifcview`` cache.
The reader validates the sidecar header, skips the compressed geometry section,
and reads the metadata blocks.

For desktop loading, ``readSidecarMetadata()`` returns a
``StreamingSidecar`` containing:

- the sidecar file path
- the geometry section offset
- mesh records
- instance records
- georeferencing state
- the baked chunk table of contents
- element metadata

For web loading, ``ViewportCore::loadSidecarMetadataWeb()`` reads only the
header and critical metadata before creating the model. It records the location
of the deferred element metadata block and fetches that later only when UI code
needs it.

``ViewportCore::applyCachedModel()`` then converts sidecar metadata into
runtime model state:

1. It creates the chunk list. If the sidecar contains a baked
   ``SidecarChunk`` table, that table is authoritative. Each chunk is a
   consecutive mesh range with compressed vertex and index frame locations. If
   the model came from a direct in-memory load and has no table, the chunk plan
   is derived from mesh centroids with Morton sorting and greedy packing.
2. It creates per-chunk scratch buffers: ``visible_draws``, ``prefix_sums``,
   and a small uniform with draw counts.
3. It uploads the per-mesh quantisation table, ``MeshGpu``.
4. It uploads the per-instance GPU table, ``InstanceGpu``.
5. It builds CPU lookup tables: object id to instance, instance to chunk,
   mesh-local offsets inside each chunk, chunk AABBs, and chunk instance lists.
6. It leaves the actual chunk vertex and index bytes non-resident. They are
   fetched later by ``driveStreamingLoads()``.

At this point the viewer knows the model's structure and bounds, but a sidecar
model has not necessarily uploaded any triangles yet.

Load path 2: direct IFC stream
------------------------------

When no usable sidecar exists, ``SceneLoader`` starts ``GeometryStreamer``.
Streamer signals are queued from the worker thread into the UI/render thread:

``StreamedMesh``
    A unique mesh in transfer form. Vertices are seven floats per vertex:
    position, normal, and packed colour.

``StreamedInstance``
    One placed occurrence of a mesh, with object id, colour override,
    placement transform, and world AABB.

During the stream, ``ViewportCore::uploadStreamedMesh()`` and
``ViewportCore::uploadStreamedInstance()`` stage the data in a ``SidecarData``
shape. Mesh vertices are converted to the renderer's packed 12-byte format,
indices are stored, and instance records are accumulated. The viewport does not
incrementally draw these raw streamed mesh records one by one.

When the streamer finishes, ``SceneLoader::onStreamerFinished()`` calls
``ViewportCore::finalizeModel()``. Finalisation wraps the staged data in a
``StreamingSidecar`` object and calls the same ``applyCachedModel()`` path used
by sidecar loads. It then gathers the already-staged vertex and index bytes per
chunk and calls ``applyStreamedChunk()`` for each chunk. Direct IFC loads
therefore become resident after finalisation rather than streaming from disk.

If sidecar writes are enabled, ``SidecarBuilder`` finalises its mirrored copy,
builds LOD1 where available, reorders geometry into streaming chunk order, and
writes the ``.ifcview`` file for the next open.

Mesh and vertex representation
------------------------------

IFC geometry is represented as unique meshes plus instances. Repeated IFC
representations are uploaded once, and every placement becomes an instance that
references a mesh.

The GPU vertex format is 12 bytes per vertex:

.. code-block:: text

   offset 0   position  uint16[3]  quantised against the mesh local AABB
   offset 6   normal    int8[2]    octahedral encoded
   offset 8   colour    uint8[4]   RGBA

The mesh's ``MeshGpu`` record stores ``aabb_min`` and ``aabb_max``. The vertex
shader reconstructs local positions by mapping the three 16-bit coordinates
back into that local AABB. The instance transform then moves the vertex to
world space.

Indices are ``uint32``. Each mesh has an LOD0 index range and may have an LOD1
index range. LOD1 reuses the same vertices with a smaller index list generated
at sidecar-build time.

Chunk layout and residency
--------------------------

Chunks are the unit of streaming, residency, culling priority, and rendering
bind groups. A chunk owns:

- a list of mesh ids
- a list of instance ids
- a world AABB
- compressed sidecar frame locations, for sidecar-backed models
- local vertex and index offsets for meshes inside the chunk
- GPU pool slices when resident
- cull output buffers

For sidecar-backed models, chunks start non-resident. They have metadata and
small cull buffers, but no vertex/index pool slices. A chunk becomes resident
when ``applyStreamedChunk()`` receives its decompressed vertex and index bytes.

``applyStreamedChunk()``:

1. Allocates vertex and index slices from ``BufferPool``.
2. Uploads chunk bytes with ``wgpuQueueWriteBuffer``.
3. Builds the chunk bind group.
4. Marks the chunk resident.
5. Scans alpha bytes so culling can route transparent meshes to the transparent
   pass.
6. Computes mesh-local volumes and triangle CPU shadows used by measurement
   tools.

``unloadChunk()`` releases the chunk's bind group and returns its pool slices
to ``BufferPool``. Metadata and cull scratch remain allocated so the chunk can
be loaded again later.

Per-frame render pipeline
-------------------------

Each frame in ``ViewportCore::render()`` follows this order:

.. code-block:: text

   render():
     drain completed HiZ readbacks
     upload selection flags if dirty
     acquire surface texture
     update frame uniforms
     cull visible instances and upload visible draw tables
     drive chunk streaming and eviction
     encode opaque main pass
     encode transparent main pass
     encode in-pass overlays
     encode edge silhouette pass
     encode HiZ resolve if enabled
     encode post-main overlays
     submit command buffer
     present surface

Streaming runs after culling. That means a chunk that becomes resident during
``driveStreamingLoads()`` is usually first visible on a later frame. The
renderer requests a short burst of follow-up frames while streaming work is
settling so an event-driven render loop does not stop before newly resident
chunks are drawn.

Culling
-------

Culling is CPU-side and model-parallel on desktop. The web build currently uses
the serial path because the WebAssembly build is not wired for pthread-backed
``std::async``.

``cullModelCpuCompute()`` is chunk-driven:

1. Reset each chunk's per-frame scratch and counters.
2. Frustum-test the chunk AABB. If the chunk is outside the frustum, every
   instance inside it is skipped.
3. For frustum-passing chunks, process each instance in the chunk.
4. Skip hidden object ids.
5. Frustum-test the instance AABB.
6. Estimate projected pixel radius and projected AABB area.
7. Accumulate projected AABB area into the chunk's streaming priority.
8. Apply contribution culling. Instances below the current pixel-radius
   threshold are dropped.
9. Mark the chunk contribution-visible. This is the signal that
   ``driveStreamingLoads()`` uses to decide whether a non-resident chunk is
   worth fetching.
10. Optionally apply HiZ occlusion using the previous frame's depth pyramid.
11. Choose LOD0 or LOD1 based on projected size and LOD1 availability.
12. Classify the draw as opaque or transparent.
13. Append a ``VisibleDrawGpu`` record and extend the chunk prefix sum.

The contribution threshold is higher while the camera is moving when
``viewport/motion_min_pixel_radius`` exceeds the still threshold. This drops
more sub-pixel work during navigation and reduces cull and streaming pressure.

HiZ occlusion is optional. When enabled, the renderer uses a depth pyramid from
a previous compatible view-projection matrix. Contribution culling runs before
HiZ because it is much cheaper and reduces the number of HiZ tests.

Visible draw tables
-------------------

Culling does not issue draw calls directly. It writes compact per-chunk tables:

``visible_draws``
    One record per visible instance draw. It stores mesh id, instance index,
    first index, and base vertex.

``prefix_sums``
    A monotonic array that maps a flat vertex id inside one chunk draw call to
    a visible draw record.

``per_chunk_uniform``
    Four counters: total visible draws, total visible vertices, opaque visible
    vertices, and opaque visible draws.

After culling, ``cullModelCpuUpload()`` uploads those arrays to the chunk's GPU
buffers. Chunks with zero visible draws have their uniform zeroed and are
skipped by the render pass.

Triangle rendering
------------------

The main render uses one WebGPU ``draw()`` per resident visible chunk, not one
draw per IFC element. The CPU has already compacted the visible instances into
the chunk's ``visible_draws`` table.

The vertex shader receives a flat ``vertex_index`` from the draw call. It:

1. Binary-searches ``prefix_sums`` to find the visible draw record.
2. Computes the local vertex within that draw.
3. Reads the mesh-local index from the chunk index buffer.
4. Adds the draw's base vertex to get the packed vertex record.
5. Decodes quantised position, octahedral normal, and colour.
6. Reads the instance transform and object id.
7. Transforms the local vertex to world and clip space.

The fragment shader applies lighting, selection/active-object highlighting,
x-ray alpha cap, section clipping, and transparency output. Section clipping is
also used by picking so selected section planes match what the user sees.

Opaque and transparent passes
-----------------------------

Culling partitions visible draws into opaque and transparent halves. Opaque
draws are written first in each chunk's arrays; transparent draws are appended
after them.

The main pass then renders:

1. Opaque pipeline with depth writes and no blending, drawing
   ``opaque_visible_vertices``.
2. Transparent pipeline with blending, drawing the remaining vertices starting
   at ``opaque_visible_vertices``.

Transparency is chosen from the baked mesh alpha flag, an instance colour
override alpha, or forced x-ray mode. The transparent pass uses the same chunk
bind group and buffers as the opaque pass.

Streaming and eviction
----------------------

``driveStreamingLoads()`` decides which non-resident sidecar chunks should be
loaded and which resident chunks may be evicted.

Each frame it:

1. Drains completed desktop worker reads and applies successful chunks.
2. Updates resident chunk visibility history.
3. Builds candidates from non-resident chunks that passed contribution
   visibility in the current cull.
4. Sorts candidates by current projected-area priority.
5. Loads up to a fixed number of chunks per frame.
6. Ensures the buffer pool can fit the chunk before issuing the load.
7. Evicts lower-value resident chunks when the pool is full.

The first eviction pass drops the least-recently-visible resident chunk that
was not visible this frame. If every resident chunk is currently visible, a
second pass may evict the lowest-priority resident chunk, but only when the
candidate has meaningfully higher priority. This hysteresis prevents simple
swap loops while still allowing a saturated pool to follow the camera.

Desktop sidecar chunks are read by ``StreamingThread``. Each request contains
the sidecar path, geometry section offset, compressed vertex frame location,
and compressed index frame location. The worker reads and decompresses those
frames, then ``driveStreamingLoads()`` applies the result on the render thread.

Web sidecar chunks are fetched asynchronously by byte range. Vertex and index
frames are requested separately and joined before decompression and upload.
The web path caps concurrent chunk downloads so the highest-priority chunks can
arrive and render progressively instead of sharing bandwidth across the entire
visible set.

Sidecar format relationship
---------------------------

The ``.ifcview`` file exists to feed this renderer. Its critical metadata block
contains enough data to build ``ModelGpuData`` without reading geometry:

- mesh table
- instance table
- georeferencing cache
- chunk table of contents

The geometry section contains one compressed vertex frame and one compressed
index frame per chunk. The chunk table lets the streaming system jump directly
to the frames for a visible chunk without scanning the file or reading
unrelated geometry.

The sidecar version documented by the current code is version 16.

Picking, overlays, and tools
----------------------------

Picking is a GPU pass, not CPU raycasting. The pick pipeline uses the same
``visible_draws`` and chunk buffers as the main pass and writes object ids to
an integer texture. A click reads back the selected pixel. The section tool also
uses a normal and world-position pick target so it can create planes from the
actual rendered surface.

Overlay rendering is host-provided. ``ViewportCore`` encodes the shared section
gizmo and calls host hooks for in-pass and post-main overlays. The Qt host
forwards those hooks to the desktop overlay renderer; the web host can no-op or
provide its own implementation.

Edges are drawn after the main pass using the depth buffer. HiZ resolve, when
enabled, also happens after the main pass so a later frame can use the captured
depth pyramid for occlusion culling.

Federation and transforms
-------------------------

Federated models compose several transforms before upload:

.. code-block:: text

   federated_false_origin
       * model_transformation
       * coordinate_operation
       * placement_transformation

The sidecar stores double-precision placement transforms so large IFC
coordinates can be combined with coordinate operation and false-origin matrices
before being narrowed to the float transform used by the GPU. This protects
rendering precision for survey-coordinate models.

What to remember
----------------

- Raw IFC streaming produces mesh and instance chunks, but the WebGPU viewport
  does not draw each emitted mesh immediately. It stages them, finalises a model,
  then uses the same chunk path as sidecar loads.
- Sidecar loads create a renderable model from metadata first. Geometry becomes
  visible only as chunks become resident.
- Culling produces compact visible draw tables per chunk.
- The renderer draws one flat vertex stream per visible chunk. The shader
  expands that stream back into indexed, instanced triangles using
  ``visible_draws`` and ``prefix_sums``.
- Streaming priority comes from the current view. Chunks are fetched only when
  their instances are large enough on screen to be worth drawing.
- The buffer pool is finite, so residency is dynamic. The renderer keeps the
  chunks that matter most for the current view and evicts lower-value chunks
  under memory pressure.
