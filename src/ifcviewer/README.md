# IfcViewer

A high-performance native IFC viewer built on IfcOpenShell's C++ geometry
engine with a Qt6 interface and OpenGL 4.5 rendering.

## Architecture

```
+---------------------------------------------------+
|  Qt6 Application (MainWindow)                     |
|  +----------+ +----------------------------------+|
|  | Element  | | 3D Viewport                      ||
|  | Tree     | | (QWindow + OpenGL 4.5 Core)      ||
|  | (per-    | |                                  ||
|  |  model)  | | Per-model: VAO/VBO/EBO           ||
|  +----------+ |            instance SSBO         ||
|  | Property | |            visible SSBO          ||
|  | Table    | |            indirect buffer       ||
|  +----------+ | glMultiDrawElementsIndirect      ||
|  | Status / Progress / Stats                      |
+---------------------------------------------------+
        ^                        ^
        |                        |
  element metadata      MeshChunk / InstanceChunk / Sidecar
        |                        |
+---------------------------------------------------+
|  GeometryStreamer (one per loaded model)          |
|  IfcGeom::Iterator with N threads                 |
|  Dedups representations -> MeshChunk              |
|  Emits one InstanceChunk per placement            |
+---------------------------------------------------+
```

### Key design decisions

- **QWindow viewport** embedded via `QWidget::createWindowContainer()`. Gives
  us a raw native surface for OpenGL, bypassing `QOpenGLWidget`'s compositor
  overhead.
- **GPU instancing as the central pillar.** IFC models are dominated by
  repeated geometry — identical doors, windows, studs, pipes placed at
  different transforms. IfcOpenShell's iterator surfaces representation
  identity, so we upload each unique mesh exactly once and keep per-placement
  data (transform, object id, optional colour override) in a separate SSBO.
  For real projects this collapses tens of millions of triangles of duplicate
  vertex data into a few hundred MB of unique meshes.
- **Per-model GPU buffers**: each loaded model gets its own
  VAO/VBO/EBO/instance-SSBO/visible-SSBO/indirect-buffer. No cross-model
  growth copies. Removing a model frees its GPU memory immediately.
- **Quantized local-coordinate vertex format (16 B):** position as
  `u16x3` normalised against each mesh's local AABB, octahedral-encoded
  normal as `i16x2`, packed RGBA8 colour. Dequantisation basis is per
  mesh, uploaded once in a `MeshGpu` SSBO at binding 2. The per-instance
  transform is applied in the vertex shader. No world-baked vertex data.
  ~43 % smaller VBO and sidecar than the previous 28 B float layout.
- **Multi-draw indirect:** every frame the CPU builds a flat list of visible
  instance indices and one `DrawElementsIndirectCommand` per non-empty mesh,
  then issues a single `glMultiDrawElementsIndirect` per model. 50k visible
  instances across 8k unique meshes collapse to one driver-side command
  submission per model.
- **BVH frustum culling over instances**: per-model BVH trees cull whole
  subtrees of placements with one frustum test. Falls back to a linear scan
  during progressive upload and for very small models (< 32 instances).
- **Parallel per-model cull:** each model's CPU cull (frustum + contribution
  + HiZ + bucketing + indirect-command emit) is independent, so `render()`
  fans them out via `std::async` and joins before the serial GL-upload
  pass. On an 18-model scene this took wall-clock cull from ~25 ms to
  ~5 ms. The cull scratch buffers live on `ModelGpuData` so each worker
  owns its output storage; phase-timer counters are atomic for the same
  reason. `IFC_CULL_THREADS=0` forces single-threaded fallback.
- **Reflection-aware two-pass draw:** IFC placements can have negative-
  determinant transforms (mirrored families). These flip the screen-space
  winding of their triangles, which would make them vanish under
  `GL_CULL_FACE`. The cull pass buckets visible instances into forward
  (det ≥ 0) and reverse (det < 0) slices and the renderer issues two MDI
  calls per model with `glFrontFace` toggled between them.
- **`reorient-shells` enabled in the iterator:** makes face winding
  consistent within a shell at geometry-gen time — the only place this can
  actually be fixed. Without it, files with inside-out faces produce dark
  patches and swiss-cheese under backface culling. Costs iterator time but
  is cached in the sidecar.
- **Progressive rendering during streaming:** the viewport is drawable
  before `finalizeModel()`. Instances are pushed to the SSBO one at a time
  via `glNamedBufferSubData` as they arrive, and the linear-scan cull path
  handles them until the BVH is built. Orbit and pan remain interactive
  through load.
- **Non-blocking sidecar loading**: sidecars are read on a background
  thread; only the final GPU upload touches the main thread.
- **Event-driven rendering:** no continuous render timer. Frames are
  scheduled via `QWindow::requestUpdate()` only when something changes
  (camera move, streaming chunk, hover, settings). When the camera and
  scene are idle the cull pass and HiZ readback are skipped entirely
  and the main thread blocks in the Qt event loop — the viewer costs
  zero CPU/GPU on a static scene. FPS is still reported accurately
  because frame cost is measured *inside* `render()`, not as wall-clock
  between frames.
- **GPU object picking**: a second render pass writes object IDs into an
  R32UI framebuffer. Click reads back one pixel. No CPU-side raycasting.
- **Multi-model support**: multiple IFCs can be loaded simultaneously.
  Each gets its own `GeometryStreamer` (which owns the `ifcopenshell::file`
  for property lookup). Models load sequentially. Per-model
  hide/show/remove.

### Files

| File | Purpose |
|------|---------|
| `main.cpp` | Application entry, GL 4.5 surface format, CLI argument parsing |
| `MainWindow.h/cpp` | Qt main window: multi-model project, element tree, properties, status |
| `ViewportWindow.h/cpp` | OpenGL 4.5 Core renderer: shaders, buffers, camera, culling, MDI draw, picking |
| `GeometryStreamer.h/cpp` | Background iterator runner; emits `MeshChunk` + `InstanceChunk` |
| `InstancedGeometry.h` | Shared structs: `MeshInfo`, `InstanceCpu`, `InstanceGpu`, chunk records |
| `BvhAccel.h/cpp` | Median-split BVH builder; operates on instance world-AABBs |
| `LodBuilder.h/cpp` | Post-stream decimation of unique meshes via meshoptimizer (`simplifySloppy`) |
| `SidecarCache.h/cpp` | Raw binary `.ifcview` (v6) sidecar read/write |
| `AppSettings.h/cpp` | Persisted preferences (geometry library, stats overlay, backface culling) |
| `SettingsWindow.h/cpp` | Settings dialog |
| `CMakeLists.txt` | Build configuration |

## Dependencies

- **Qt6** (Core, Gui, Widgets, OpenGL)
- **OpenGL 4.5** with `GL_ARB_direct_state_access` and
  `GL_ARB_shader_draw_parameters` — available on Windows and Linux. macOS
  will need a Vulkan/MoltenVK backend (not yet implemented; macOS caps out
  at GL 4.1).
- **IfcOpenShell C++ libraries** (IfcParse, IfcGeom, and their
  dependencies: Open CASCADE, Boost, Eigen3, optionally CGAL).
- **[meshoptimizer](https://github.com/zeux/meshoptimizer)** — linked via
  `find_package(meshoptimizer REQUIRED)`. Used at sidecar-build time for LOD
  decimation; not needed at runtime once a sidecar exists.

## Building

IfcViewer is part of the IfcOpenShell CMake project. From the repo root:

```sh
mkdir build && cd build

cmake ../cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_IFCVIEWER=ON \
    -DBUILD_CONVERT=OFF \
    -DBUILD_IFCPYTHON=OFF \
    -DBUILD_GEOMSERVER=OFF \
    -DBUILD_DOCUMENTATION=OFF \
    -DBUILD_EXAMPLES=OFF \
    -DCOLLADA_SUPPORT=OFF \
    -DGLTF_SUPPORT=OFF \
    -DHDF5_SUPPORT=OFF

make -j$(nproc) IfcViewer
```

If Qt6 is not in a standard location, pass `-DQT_DIR=/path/to/qt6`.

## Usage

```sh
./IfcViewer arch.ifc struct.ifc mep.ifc
./IfcViewer                   # then File -> Add Files
```

### Controls

| Input | Action |
|-------|--------|
| Middle mouse drag | Orbit camera |
| Shift + middle mouse drag | Pan camera |
| Scroll wheel | Zoom |
| Left click | Select object |

### Keyboard

| Key | Action |
|-----|--------|
| Ctrl+O | Add files |
| Ctrl+Q | Quit |

### Settings

- **Geometry Library** — kernel string passed to IfcOpenShell (default
  `hybrid-cgal-simple-opencascade`).
- **Show Performance Stats** — overlay FPS / object / triangle / draw
  counts in the status bar.
- **Backface Culling** — `GL_CULL_FACE` on closed solids. Default on.
  Disable if a model uses open shells and you see missing faces.

## Performance Strategy

The viewer targets smooth orbiting at 60 fps on real-world multi-discipline
BIM projects (a "real job" being ~50 models, several million placements,
hundreds of millions of rasterised triangles when everything is in view).

Rendering performance has evolved in phases. Each builds on the previous,
and smaller models never pay for optimisations they don't need.

### Phase 1 — Per-object Frustum Culling

**Status:** implemented (and still the fallback for small models / during
streaming).

Six view-frustum planes are extracted from the view-projection matrix each
frame. Each instance's world AABB is tested with the p-vertex / n-vertex
method (one dot product + one compare per plane, 6 planes).

Surviving instance indices are written into a per-mesh bucket, then
flattened into a single `uint[]` (the "visible SSBO", binding = 1) and
accompanied by one `DrawElementsIndirectCommand` per non-empty mesh.
One `glMultiDrawElementsIndirect` call per model draws everything.

Cost: ~6 dot products per instance per frame. Fine up to ~100 k instances
per frame; above that the linear scan shows up in profiles, motivating
Phase 2.

### Phase 2 — BVH Acceleration + Sidecar Cache

**Status:** implemented.

For models exceeding ~32 instances, a bounding volume hierarchy groups
nearby placements into a binary tree and culls entire subtrees with a
single frustum test. This reduces per-frame work from O(N) to O(log N) in
the best case (camera zoomed to a corner) and remains well under 1 ms for
100 k instances in the worst case (everything on screen).

A BVH was chosen over an octree because BIM data is spatially non-uniform
— dense MEP risers in one zone, sparse open atria in another. An octree
subdivides space uniformly, wasting nodes on empty regions and creating
deep chains in dense ones. A BVH adapts its splits to the actual
placement distribution.

#### Activation

The BVH is optional and non-disruptive. Until it is built, the Phase 1
linear scan handles culling. The renderer checks for a BVH per model and
falls back to the scan for any model that doesn't have one.

It activates in one of two ways:

1. **Sidecar hit** — the `.ifcview` file next to the `.ifc` is found and
   valid; its instance data is uploaded and the BVH rebuilt on the fly
   from the restored AABBs (cheap — `< 100 ms` for 100 k placements).
2. **After streaming** — `finalizeModel()` builds the BVH synchronously
   once all chunks are in (instances already live on the GPU, so there's
   no EBO re-sort to do). The sidecar is written afterwards.

Models under 32 instances skip the BVH.

#### BVH node layout (32 B, two per cache line)

```cpp
struct BvhNode {
    float    aabb_min[3];      // 12 B
    float    aabb_max[3];      // 12 B
    uint32_t right_or_first;   // interior: right child index; leaf: first item index
    uint16_t count;            // 0 = interior, >0 = leaf
    uint16_t axis;             // 0/1/2 for interior; unused for leaf
};
```

Left child is always the next node (pre-order DFS). Leaf items are
indices into the per-model `instances` array; the parallel `bvh_items[]`
array carries the world AABBs.

#### Build: object-median split

1. Compute centroid of each item's AABB.
2. Pick the longest axis of the node's AABB.
3. `std::nth_element` partitions at the median on that axis — O(n).
4. Recurse until a leaf holds ≤ 8 items.

O(n log n) total. No SAH — for frustum culling (6-plane tests, early
subtree reject) the quality difference vs median is negligible.

#### Traversal: stack-based, no recursion

```
stack[64] = { 0 }                     // root
while stack not empty:
    node = nodes[stack.pop()]
    if node.aabb outside frustum: continue
    if leaf:
        for each item in node:
            if item.aabb in frustum: emit to visible list
    else:
        push right child, push left child   // left processed first (DFS)
```

Depth 64 is enough for billions of items on any balanced tree. The stack
is on the C++ stack, zero per-frame allocation.

#### Sidecar format (`.ifcview`, v6)

Raw memory dump, Blender-`.blend`-style — no serialisation, no parsing.
Stores everything needed to skip the `IfcGeom::Iterator` pass:

```
SidecarHeader            (magic "IFVW", version, endian, ...)
uint64_t                 source_file_size
uint32_t + uint8_t[]     vertex data    (16 B/vert quantized; per-mesh basis in MeshInfo)
uint32_t + uint32_t[]    index data     (mesh-local)
uint32_t + MeshInfo[]    per-unique-mesh metadata (56 B each, incl. LOD1 slice)
uint32_t + InstanceCpu[] per-placement records (transform + AABB + ids)
uint32_t + PackedElementInfo[]   element tree records
uint32_t + char[]        string table
```

Staleness check: `source_file_size` vs actual file size. Mismatched →
reject and rebuild. Endianness marker rejects cross-arch caches.

Sidecars store the raw `object_id` / `model_id` values from the session
that wrote them. On load they are rebased onto the current session's ID
space (`object_id += next_object_id_ - min_id_in_sidecar`, `model_id`
overwritten with the freshly-assigned handle) before the elements hit
`element_map_` or the viewport. Without this, two cached models loaded
back-to-back collide — both start at `object_id=1` and the second model's
property lookups return the first model's data.

### GPU Instancing pipeline (the central pillar)

Everything above plugs into a single data-flow, worth documenting on its
own because it's what makes the whole thing fast.

Per-model state on the GPU:

| Buffer | Contents | Lifetime |
|--------|----------|----------|
| `VBO` | Quantized local-coord vertex data (16 B/vert: u16x3 pos, oct i16x2 normal, RGBA8). One range per unique representation. | Grow-on-demand during streaming; static after finalize. |
| `MeshGpu SSBO` (binding 2) | Per-mesh dequant basis (`vec4 aabb_min`, `vec4 aabb_max`). | Grow-on-demand; static after finalize. |
| `EBO` | Mesh-local uint32 indices. One range per unique representation. | Same. |
| `SSBO` (binding 0) | `InstanceGpu[]` (80 B each: mat4 transform, object_id, color_override, pad). | Appended during streaming, static after finalize. |
| `visible SSBO` (binding 1) | `uint32[]` — flat list of visible instance indices, ordered by mesh, uploaded each frame. | Rewritten every frame. |
| Draw-indirect buffer | `DrawElementsIndirectCommand[]` — one per non-empty mesh, uploaded each frame. | Rewritten every frame. |

Draw command:

```c
struct DrawElementsIndirectCommand {
    uint32_t count;         // mesh.index_count
    uint32_t instanceCount; // visible-list length for this mesh
    uint32_t firstIndex;    // mesh.ebo_byte_offset / 4
    uint32_t baseVertex;    // mesh.vbo_byte_offset / 16
    uint32_t baseInstance;  // offset into the flat visible-index array
};
```

The vertex shader reads `visible[gl_BaseInstanceARB + gl_InstanceID]` to
get the real instance id, then indexes into the instance SSBO:

```glsl
uint slot = uint(gl_BaseInstanceARB) + uint(gl_InstanceID);
uint iid  = visible[slot];
InstanceRecord inst = instances[iid];
gl_Position = u_view_projection * inst.transform * vec4(a_position, 1.0);
```

`gl_BaseInstanceARB` requires `GL_ARB_shader_draw_parameters`, which is
available on all GL-4.6-capable drivers.

Reflection handling: at upload time we store a parallel
`instance_reflected[]` byte array (1 if the transform's upper-3×3 has
det < 0). The cull pass produces two flat visible-list slices — fwd
(non-reflected) first, rev (reflected) after — concatenated into one
buffer. The renderer issues MDI twice: fwd with `glFrontFace(GL_CCW)`,
rev with `glFrontFace(GL_CW)`. `GL_CULL_FACE` stays on and does the
right thing in both passes.

### Current bottleneck — draw-bound, not upload-bound

The original README's Phase 3 ("GPU-driven indirect draw") described
moving draw submission to the GPU via compute. In the meantime, GPU
instancing and MDI made the CPU-side draw cost essentially free (10
`glMultiDrawElementsIndirect` calls per frame for 10 models). **That
goal is met.** The real ceiling lies elsewhere, and it took a couple of
bad hypotheses to pin down.

#### Profiled scene

10 models / 379 k instances / 128 M triangles, everything in view, no
camera motion, GTX 1650 (PCIe dGPU, 4 GB VRAM):

| Metric | Value |
|--------|-------|
| FPS | 6.7 |
| Frame time | 149 ms |
| gl_draws | 10 |
| Sub-draws packed in indirect buffers | 67 037 |

`nvidia-smi` reports 95 % GPU utilisation during render — the GPU is
the thing that's pinned.

#### False lead: "the per-frame uploads are the bottleneck"

The first round of probes pointed at the two `glNamedBufferSubData`
calls per model per frame (visible list ~1.5 MB + indirect buffer
~1.3 MB):

| Probe | Result | Initial interpretation |
|-------|--------|------------------------|
| Camera off-screen (nothing visible) | 60 fps | GPU idle → CPU path cheap |
| Comment out the two `glNamedBufferSubData` | 60 fps, blank screen | Uploads are the bottleneck |

This led to an aborted Phase 3A implementation of persistent-mapped
triple-buffered rings (and then staging + VRAM-resident with
`glCopyNamedBufferSubData`). Neither moved the FPS needle — both still
sat at 6.7 fps.

The probe was wrong: **commenting out the uploads emptied the indirect
buffer, so MDI drew zero triangles. "No upload" and "no draw" were
indistinguishable in the test.**

#### What actually isolates the draw cost

Two diagnostic env vars now live in `render()`:

- `IFC_SKIP_MDI=1` — keep everything (cull, upload, binds) but skip the
  actual `glMultiDrawElementsIndirect` calls.
- `IFC_MAX_SUBDRAWS=N` — truncate each MDI's drawcount to N while still
  running the rest of the frame.

Results on the profiled scene:

| Probe | FPS | Frame time |
|-------|-----|-----------|
| baseline | 6.7 | 149 ms |
| `IFC_SKIP_MDI=1` | 62.5 | 16 ms |
| `IFC_MAX_SUBDRAWS=30000` | 6.7 | 149 ms |
| `IFC_MAX_SUBDRAWS=10000` | 7.5 | 133 ms |
| `IFC_MAX_SUBDRAWS=1000` | 20.2 | 49 ms |

Readings:

1. `SKIP_MDI` gives 62 fps with all upload/bind machinery still running
   — the non-draw path fits in ~16 ms easily. **Not upload-bound.**
2. Halving the sub-draw count (67 k → 30 k) saves 0 ms. If per-sub-draw
   command-processor overhead were material, dropping 37 k sub-draws
   would save measurable time no matter which sub-draws were dropped.
   It doesn't. **67 k sub-draws is not the bottleneck** — the long tail
   carries almost no triangles, and the heavyweights dominate.
3. Time only starts coming down once the cap is low enough to shed bulk
   triangle work (1000 sub-draws → 49 ms). The curve is consistent with
   a long-tailed distribution: a handful of very big meshes × instance
   counts do most of the rasterisation.

**Conclusion: the GTX 1650 is rasterising 128 M triangles at ~850 M
tri/s, and that eats ~133 ms of the 149 ms frame.** No CPU-side or
upload-side work will recover it. The only way forward is to draw
fewer triangles.

### Phase 3 (revised) — Shed triangles, not bytes

In order of effort/payoff for BIM workloads:

#### 3A. Screen-space contribution culling — ✅ done

Reject frustum-visible objects whose bounding-sphere projects below a
pixel-radius threshold. Applied both at BVH-node level (whole subtrees
pruned, so distant parts of the model never touch per-instance tests)
and per-instance level. Short-circuits when the camera is inside the
AABB so nothing-you're-standing-next-to is ever lost. Pick pass uses
threshold 0 so sub-pixel objects remain clickable.

Because the pick pass re-runs the cull with its own parameters (no
contribution cull, no HiZ) and writes into each model's shared
`visible_ssbo` / indirect buffer, `pickObjectAt()` must invalidate
`have_cached_cull_` on exit. Otherwise the next `render()` sees an
unchanged camera, skips the cull, and draws the pick-pass buffers —
the user sees obviously-wrong shading until they nudge the camera.

Sphere-based (centre = AABB midpoint, radius = half-diagonal,
r_px = focal_px · radius / distance). Loses a little precision on
very elongated bounds vs. 8-corner projection, but costs ~5× less per
test, and because BVH-node pre-cull handles the long tail in one shot
it doesn't matter.

Threshold defaults to 2 px radius, overridable via `IFC_MIN_PX` env
var. Measured on the 10-model / 128 M-tri test scene (GTX 1650):

| Threshold | FPS | Triangles drawn | Objects drawn |
|-----------|-----|-----------------|---------------|
| 0 px (off) | 6.7 | 128 M | 379 k |
| 2 px | 20.2 | 40 M (31 %) | 89 k (24 %) |
| 4 px | 30.3 | 15 M (12 %) | 29 k (8 %) |

At 4 px, frame time breakdown matches: ~16 ms non-draw baseline (from
`IFC_SKIP_MDI=1`) + ~18 ms of raster (15 M tris / 850 M tri/s) ≈ 34 ms
= observed 33 ms. The ceiling is now genuinely vertex/raster
throughput on the post-cull geometry — next steps (LOD, HiZ) attack
that directly.

#### 3B. Distance / contribution LOD — ✅ done

Decimate each unique representation once (at sidecar-build time), store
the reduced index slice in the same EBO, and switch to it per-instance
per-frame whenever the projected sphere radius is small enough that the
reduced silhouette is indistinguishable from the original.

##### Pipeline

1. **After streaming finishes**, `MainWindow` calls `buildLods(sd)` on
   the snapshotted `SidecarData`. Each eligible mesh's decimated index
   list is appended to `sd.indices`; the per-mesh `MeshInfo` gains two
   new fields:

   ```cpp
   uint32_t lod1_ebo_byte_offset;  // appended slice, same VBO
   uint32_t lod1_index_count;      // 0 = no LOD1 was built
   ```

   `MeshInfo` grew from 48 to 56 bytes, which also bumps the sidecar
   format to v5.

2. `viewport_->applyLodExtension(model_id, sd)` pushes the new index
   suffix onto the live EBO via `glNamedBufferSubData` and replaces the
   CPU-side `m.meshes` vector. The VBO and instance SSBO are untouched
   — LOD1 reuses the same vertices, only the indices differ.

3. The sidecar is then written with both LOD0 and LOD1 indices baked in,
   so subsequent loads of the same file pick up LOD1 for free.

##### Selection

The contribution-cull pass already computes each instance's projected
pixel radius. LOD1 is selected when that radius falls below
`IFC_LOD1_PX` (default 30 px) and the mesh has a non-empty LOD1 slice.
Camera-inside-AABB short-circuits select LOD0 (treated as "infinite
radius") so you never accidentally see the reduced mesh up close.

The visible-instance pipeline gains two more buckets (`fwd_lod1_`,
`rev_lod1_`), so the four-way split is now `{fwd, rev} × {LOD0, LOD1}`.
LOD0/LOD1 within a winding slice are contiguous — only winding requires
`glFrontFace` to flip between MDI calls, LOD does not. `firstIndex` /
`count` in the `DrawElementsIndirectCommand` pick which slice of the EBO
to walk; everything else (base vertex, base instance, SSBO bindings,
shader) is unchanged.

##### Decimator choice: `meshopt_simplifySloppy`

The first attempt used `meshopt_simplify`, which is an edge-collapse
decimator. It returned every input mesh unchanged (`err = 0.0`) for two
reasons, both inherent to BIM brep output:

1. **Per-triangle vertex duplication.** The instanced VBO stores each
   triangle's vertices separately so that hard-edge normals can differ
   across triangles. Topologically there are no shared vertices, so no
   edges exist for `meshopt_simplify` to collapse. A
   `meshopt_generateShadowIndexBuffer` welding pass (hash xyz only,
   ignore the interleaved normal/colour) fixes this half cheaply — the
   VBO isn't touched, only a per-call shadow index buffer is built.
2. **Non-manifold topology even after welding.** BIM brep output has
   T-junctions, coplanar slivers, separate solids meeting at a plane,
   and multi-material cuts. `meshopt_simplify` needs valid 2-manifold
   edge pairs to score collapses; it refuses the non-manifold ones, the
   priority queue never fires, and it returns the input untouched.

`meshopt_simplifySloppy` is a **voxel-clustering decimator** — it
quantises positions into cells and merges everything in a cell to a
single point. Topology is irrelevant, so it works directly on the
original indices (welding isn't even needed). The trade-off is that it
rounds off sharp corners and can produce slightly degenerate triangles,
so it doesn't look great at mid-screen size. For a LOD1 that only
activates below 30 px projected radius that's invisible in practice. If
you ever want LOD1 to remain active at larger sizes, the only robust
fix is to pre-process BIM meshes into manifold form (fuse coplanar
faces, split at T-junctions) — a significant project unto itself.

##### Tuning knobs (env vars)

| Var | Default | Effect |
|-----|---------|--------|
| `IFC_LOD1_PX` | `30` | Projected sphere radius (px) below which LOD1 kicks in. `0` disables LOD1 entirely. |
| `IFC_LOD_SLOPPY` | `1` | `0` falls back to edge-collapse (`meshopt_simplify`) on shadow-welded indices. Typically produces zero LOD1 output for BIM — useful only for A/B comparison. |
| `IFC_LOD_ERROR` | `0.2` | Target relative error passed to meshopt. |
| `IFC_LOD_RATIO` | `0.25` | Target triangle-count ratio (LOD1 aims for 25 % of LOD0 tris). |
| `IFC_LOD_MIN_SAVINGS` | `0.25` | Reject the LOD1 result if it doesn't shave at least this fraction of triangles. |
| `IFC_LOD_LOCK_BORDER` | `0` | `1` re-enables `meshopt_SimplifyLockBorder` (only meaningful with `IFC_LOD_SLOPPY=0`). |
| `IFC_LOD_DEBUG` | `0` | `1` prints per-mesh `tris / target / got / err` for the first 8 candidate meshes plus an accept/reject summary per model. |

##### Measured results

Same 10-model / 128 M-tri scene as Phase 3A (GTX 1650), 2 px contribution
threshold, overview camera, all models finalised with LOD1 built:

| Build | FPS | Frame time | Visible tris | Visible objs |
|-------|-----|-----------|--------------|--------------|
| Phase 3A alone (2 px) | 20.2 | 49 ms | 40 M | 89 k |
| Phase 3A + 3B (LOD1 ≤ 30 px) | **43.2** | **23 ms** | 14 M | 81 k |

Roughly half the remaining frame time, same object count (LOD is
lossless w.r.t. visibility — swapping index slice doesn't hide
anything). The triangle reduction on meshes that qualified for LOD1 is
~80 %: e.g. 4.17 M → 0.82 M tris for the 3618 eligible meshes of Model
1, 3.25 M → 0.65 M for Model 2, etc. Only about 20 % of unique meshes
qualify (the threshold is 500 tris — below that the indirect-command
overhead dominates), but those are the fat tail carrying most of the
rasterisation cost.

LOD build itself runs on the main thread inside `onStreamingFinished`;
typical cost is 100–600 ms per model, folded into the already-visible
"finalizing" step. Cached into the sidecar afterwards, so subsequent
opens skip it entirely.

#### 3C. Hierarchical-Z occlusion culling — ✅ done (v1, CPU-side)

Reject frustum-visible instances whose AABB is fully behind something
already drawn. The last drawn frame's depth buffer is the oracle — if a
region's deepest rasterised fragment is closer than an AABB's nearest
point, nothing in that AABB can win the depth test.

In dense BIM this matters most on interior views: standing inside a
building, 80–95 % of the model sits behind the walls of the current
room and contributes nothing to the frame. Phase 3A drops the
*distant-and-small* geometry, 3B drops its triangle count when kept,
and 3C drops the *close-and-big-but-hidden* bulk that neither of those
can touch. On an outdoor overview shot (nothing is occluded) 3C does
almost nothing — which is fine, 3A+3B already cover that case.

##### Pipeline (v1: CPU-side, 1-frame stale)

```
render():
  draw main scene into MSAA default fb
  axis gizmo
  buildHizPyramid():          <-- new
    glBlitFramebuffer MSAA depth → single-sample depth tex (256×128)
    glReadPixels  depth tex → CPU
    max-reduce mip chain on CPU (8–9 levels)
    store the VP that produced this frame
  swapBuffers

cullAndUploadVisible():
  per BVH node:     frustum ∧ contribution ∧ hiz  (subtree early-out)
  per instance:     frustum ∧ contribution ∧ hiz
```

The pyramid is always the *previous* frame's depth. On a newly loaded
scene or after a camera jump the cull is conservatively too permissive
for a frame or two (draws the occluded stuff by accident) and then
settles. No flicker because we never *wrongly reject* a visible
instance — the comparison is `aabb_near_depth > hiz_max`, so the
worst case is a kept instance that was actually occluded.

##### Why CPU-side?

Because the readback is cheap at this resolution (~128 KB / frame,
single glReadPixels ≈ 0.5 ms on PCIe) and the test itself is trivial
— ~100 k AABBs × 8 corners × a small mip lookup is well under a
millisecond on one thread. Phase 3D will port the cull to a compute
shader reading the pyramid as a texture, eliminating the readback; but
Phase 3C's CPU implementation was small enough to do first and
measure.

No MSAA complication on the write side: we just blit the default
framebuffer's multi-sample depth into a single-sample texture (GL
handles the resolve). No separate occluder pass either — we use the
previous completed frame's depth buffer directly, which is what a
temporal-reprojection HiZ reduces to when the "occluder set" is
"everything visible last frame".

##### The test

```cpp
project 8 AABB corners through hiz_vp  →  NDC rect + min z
if any corner has w ≤ 0:        return false  // crosses near plane
if rect is outside [-1, 1]²:    return false
pick mip level where rect ≤ 2×2 texels
hiz_max = max(pyramid[mip][covered texels])
return aabb_near_depth > hiz_max
```

Comparing the AABB's *closest* point against the pyramid's *deepest*
value is the conservative direction — it only rejects when the AABB
is strictly beyond everything we already drew in that region. We pick
the mip at which the rect covers ≲ 2 texels on each axis so the lookup
is O(1) regardless of AABB size.

##### BVH integration

The same test runs on interior BVH node AABBs before leaf expansion,
so an occluded subtree skips all its instances in one shot. This is
where most of the per-frame cost savings show up on interior shots —
rejecting a 500-instance BVH subtree costs one 8-corner projection.

##### Tuning knobs

| Var | Default | Effect |
|-----|---------|--------|
| `IFC_NO_HIZ` | unset | `1` disables HiZ entirely (forces the Phase-3B-only path). |
| `IFC_HIZ_SIZE` | `256` | Base pyramid width in texels; height tracks viewport aspect. Raise for more accurate near-silhouette occlusion, lower to shrink readback. |

The stats overlay gains one counter, `hiz_rej`, showing how many
instances per frame the HiZ test rejected. On outdoor overview shots
it hovers near zero; on indoor shots it climbs into the hundreds of
thousands and the frame time drops accordingly.

##### Known caveats

- **Disabled while the camera moves.** The pyramid is aligned to the
  VP matrix of the frame that produced it. On a moving camera the
  stored VP no longer matches the current one, and reusing it would
  pop objects in and out as the stale depth falsely claims they're
  occluded. The cull now compares `hiz_vp_ == current_vp` and drops
  HiZ rejection entirely when they differ, so HiZ only contributes on
  still frames. The honest cost: orbiting — the exact motion where
  the frame rate tends to dip — gets no HiZ help. A proper fix needs
  a same-frame depth pre-pass (draw cheap depth, build HiZ from *that*
  frame's VP, then issue the colour pass against it); deferred to the
  GPU-compute cull rewrite in Phase 3E where we're touching this code
  anyway. We also tried a 3-deep PBO ring for async readback (2-frame
  stale) which produced visible flicker on fast orbits — reverted.
- **Readback syncs the GPU.** `glGetTextureImage` is blocking.
  Measured cost is well under a millisecond at 256×128; not a
  bottleneck on the machines tested. Phase 3D's compute-shader cull
  removes it entirely.
- **Doesn't move the needle on overview shots.** Those scenes are
  CPU-bound on the cull traversal itself, not GPU-bound on drawing,
  so cutting the drawn-triangle count in half is invisible in the
  frame time. `hiz_rej` still rises modestly on overviews (the frustum
  hull contains everything behind visible walls) but saved GPU work
  is masked by CPU cost. HiZ pays off on interior views, where the
  GPU *was* the bottleneck. If a project never leaves overview,
  `IFC_NO_HIZ=1` shaves the ~1 ms of HiZ cost.
- **Transparent geometry would need special handling**, but the
  current renderer doesn't have any, so no-op for now.

#### 3D. Parallel per-model cull (CPU, done)

A cheaper intermediate step before going full-GPU: each model's cull is
independent (no shared mutable state beyond atomic timing counters), so
`render()` fans the per-model culls out to a `std::async` pool and joins
before the serial GL-upload pass. On the 18-model / 569 k-instance test
scene this took the cull from ~25 ms wall-clock to ~5 ms — roughly a 4×
speedup on an 8-core machine, tracking `std::thread::hardware_concurrency()`
up to the model count. Load balancing is static (one job per model); a
single massive model still bottlenecks to single-threaded speed and would
need intra-model partitioning, but in practice BIM projects are
multi-discipline so the coarse partition lands well.

The stats line now reports `cull[wall X | work: clr Y trv Z emt W upl U]`:
`wall` is frame-time impact, the `work` numbers are per-thread sums showing
where CPU cycles went. `IFC_CULL_THREADS=0` forces single-threaded mode
for comparison.

#### 3E. GPU-side culling via compute (longer-term)

Push the cull loop to a compute shader reading the per-instance SSBO +
frustum planes + HiZ pyramid, emitting the visible list and indirect
commands with atomic counters. Three compute dispatches per model: (1)
count survivors per `(mesh, winding, LOD)` bucket, (2) prefix-sum the
counts into `baseInstance` offsets and write the indirect command buffer,
(3) re-test and compact survivors into the dense visible list. HiZ moves
to a GPU depth texture sampled directly in the shader, eliminating the
Phase 3C readback. Lets culling scale to millions of instances and
single-model scenes where Phase 3D can't parallelise.

### Planned follow-ups (post-Phase-3)

- **Mesh shaders / meshlets.** Ceiling-raising, but overkill until the
  above are exhausted and we've hit silicon limits on vertex/raster
  throughput.

## Summary table

```
Scene size                      Bottleneck              Fix
-----------                     ----------              ---
< 100k instances                CPU cull scan           Phase 1 only
100k–500k                       CPU cull scan           BVH (Phase 2) — done
500k+ tris / overview shot      GPU vertex + raster     Phase 3A contribution cull
                                                        + Phase 3B LOD (done)
multi-million + occluders       redundant rasterisation Phase 3C HiZ (done, CPU readback)
many models, serial cull        single-thread BVH trv   Phase 3D parallel cull (done)
single giant model / <18 cores  CPU BVH trv             Phase 3E GPU cull (planned)
```

## Roadmap

- [x] Material colour support (per-vertex RGBA8)
- [x] Per-model GPU buffers (VAO/VBO/EBO per model, no cross-model copies)
- [x] Per-object frustum culling (Phase 1)
- [x] BVH acceleration with per-model trees (Phase 2)
- [x] Raw binary `.ifcview` sidecar cache
- [x] Non-blocking sidecar loading (background thread I/O)
- [x] Progressive GPU upload (VBO/EBO growth + streaming-time instance appends)
- [x] GPU instancing (unique meshes + per-placement SSBO)
- [x] `glMultiDrawElementsIndirect` draw path
- [x] Reflection-aware two-pass draw for mirrored placements
- [x] Backface culling (user-toggleable, default on)
- [x] `reorient-shells` enabled in iterator
- [x] Perf diagnostic env vars (`IFC_SKIP_MDI`, `IFC_MAX_SUBDRAWS`, `IFC_MIN_PX`, `IFC_LOD1_PX`, `IFC_NO_HIZ`, `IFC_HIZ_SIZE`, `IFC_CULL_THREADS`)
- [x] Phase 3A — screen-space contribution culling
- [x] Phase 3B — distance / contribution LOD (meshoptimizer `simplifySloppy`)
- [x] Phase 3C — Hierarchical-Z occlusion culling (v1, CPU-side readback)
- [x] Phase 3D — Parallel per-model CPU cull (`std::async` fan-out)
- [x] Quantized VBO (16 B/vert, sidecar v6)
- [x] Event-driven rendering (zero idle CPU/GPU, cull skipped on still frames)
- [ ] **Phase 3E — GPU-side compute-shader culling** (next; replaces the HiZ readback)
- [ ] Vulkan/MoltenVK backend for macOS
- [ ] Embedded Python scripting console
