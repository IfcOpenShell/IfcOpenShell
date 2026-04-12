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
- **Local-coordinate vertex format (28 B):** position (3 floats) + normal
  (3 floats) + packed RGBA8 colour (1 uint). The per-instance transform is
  applied in the vertex shader via an SSBO lookup. No world-baked vertex data.
- **Multi-draw indirect:** every frame the CPU builds a flat list of visible
  instance indices and one `DrawElementsIndirectCommand` per non-empty mesh,
  then issues a single `glMultiDrawElementsIndirect` per model. 50k visible
  instances across 8k unique meshes collapse to one driver-side command
  submission per model.
- **BVH frustum culling over instances**: per-model BVH trees cull whole
  subtrees of placements with one frustum test. Falls back to a linear scan
  during progressive upload and for very small models (< 32 instances).
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
| `SidecarCache.h/cpp` | Raw binary `.ifcview` (v4) sidecar read/write |
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

#### Sidecar format (`.ifcview`, v4)

Raw memory dump, Blender-`.blend`-style — no serialisation, no parsing.
Stores everything needed to skip the `IfcGeom::Iterator` pass:

```
SidecarHeader            (magic "IFVW", version, endian, ...)
uint64_t                 source_file_size
uint32_t + float[]       vertex data    (7 floats × N_verts, local coords)
uint32_t + uint32_t[]    index data     (mesh-local)
uint32_t + MeshInfo[]    per-unique-mesh metadata (48 B each)
uint32_t + InstanceCpu[] per-placement records (transform + AABB + ids)
uint32_t + PackedElementInfo[]   element tree records
uint32_t + char[]        string table
```

Staleness check: `source_file_size` vs actual file size. Mismatched →
reject and rebuild. Endianness marker rejects cross-arch caches.

### GPU Instancing pipeline (the central pillar)

Everything above plugs into a single data-flow, worth documenting on its
own because it's what makes the whole thing fast.

Per-model state on the GPU:

| Buffer | Contents | Lifetime |
|--------|----------|----------|
| `VBO` | Interleaved local-coord vertex data (28 B/vert). One range per unique representation. | Grow-on-demand during streaming; static after finalize. |
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
    uint32_t baseVertex;    // mesh.vbo_byte_offset / 28
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

### Current bottleneck — Phase 3 as designed is already obsolete

The original README's Phase 3 ("GPU-driven indirect draw") described
moving draw submission to the GPU via compute. In the meantime, GPU
instancing and MDI made the CPU-side draw cost essentially free (10
`glMultiDrawElementsIndirect` calls per frame for 10 models). **That
goal is met.** The real Phase 3 problem is different.

#### Diagnosed on a 10-model / 379 k-instance / 128 M-triangle scene

Observed numbers (everything in view, no movement):

| Metric | Value |
|--------|-------|
| FPS | 10 |
| Frame time | ~100 ms |
| gl_draws | 10 |
| Sub-draws packed in indirect buffers | 67 037 |

Elimination experiments:

| Probe | Result | Interpretation |
|-------|--------|----------------|
| Camera off-screen (nothing visible) | → 60 fps | GPU is idle; CPU path is cheap |
| Resize window to 1/4 area | no change | Not fragment/raster bound |
| `setSamples(4)` → `setSamples(1)` | no change | Not MSAA/resolve bound |
| Comment out the two `glNamedBufferSubData` in `cullAndUploadVisible` | → 60 fps (screen blank) | **The per-frame uploads are the bottleneck.** |

So the bottleneck is two `glNamedBufferSubData` calls per model per
frame uploading ~1.5 MB (visible list) + ~1.3 MB (indirect buffer).
3 MB/frame / 60 fps = 180 MB/s — trivial for the bus, but `glNamedBufferSubData`
against a buffer the GPU is still reading forces the driver to stall
the CPU or orphan/reallocate the backing store, and we're hitting that
on 20 buffers per frame.

### Phase 3 (proposed) — Eliminate per-frame upload stalls

Two ways to attack it, in ascending order of effort:

#### 3A. Persistent mapped ring buffers (near-term)

Allocate each of the per-frame-written buffers with
`glBufferStorage(GL_MAP_PERSISTENT_BIT | GL_MAP_COHERENT_BIT | GL_MAP_WRITE_BIT)`
at 3× the needed size. Keep one `void*` from `glMapBufferRange` forever.
Each frame, write the CPU-side data into slice `frame % 3` and bind
that slice via `glBindBufferRange`. The GPU reads slice N−1 while the
CPU writes slice N — no driver sync, no orphan, no stall.

Scope: ~80 lines across `ModelGpuData` + `cullAndUploadVisible` +
binding in `render()` / `renderPickPass()`. No algorithmic change, no
shader change. Expected result on the stats scene: 10 fps → ~60 fps
(the measured ceiling once uploads are removed).

#### 3B. GPU-side culling (longer-term)

Push culling itself to the GPU. A compute shader reads the
`InstanceCpu`-equivalent SSBO + frustum planes, builds the visible list
and indirect commands in-place via atomics. Zero CPU→GPU per-frame
bytes. Also lays the foundation for occlusion and contribution culling
(both want to run on the GPU anyway, with access to the depth buffer
or screen-space projection).

Scope: compute shader + atomic counter + BVH-traversal-on-GPU (or a
linear compute scan — simpler and still gains most of the win since
traversal isn't the bottleneck once upload is gone). Bigger change;
worth doing after 3A is measured, because 3A may be enough for a long
while.

### Planned follow-ups (post-Phase-3)

- **Screen-space contribution cull.** Reject instances whose projected
  screen-space AABB is below a pixel threshold. Cheap CPU-side filter
  that eliminates distant MEP detail. Big win on unfiltered plant-room
  scenes.
- **Hierarchical-Z occlusion culling.** Render large occluders, build a
  depth pyramid, test BVH / instance AABBs against it. In dense BIM,
  most geometry is behind other geometry from any given viewpoint; this
  is historically a 3–10× reduction in drawn instances.
- **Distance / contribution LOD.** Unique meshes pre-simplified at load
  time; compute shader selects an LOD per instance per frame based on
  screen-space size. Same visible-SSBO plumbing, different `firstIndex`.
- **Mesh shaders / meshlets.** Ceiling-raising but overkill until the
  above are exhausted.

## Summary table

```
Scene size                      Bottleneck           Fix
-----------                     ----------           ---
< 100k instances                CPU cull scan        Phase 1 only (current)
100k–500k                       CPU cull scan        BVH (Phase 2) — done
500k+ across many models        visible/indirect     Phase 3A mapped rings
                                buffer uploads       (next)
---                             ---                  ---
multi-million + occlusion-heavy fragment / overdraw  HiZ occlusion + LOD
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
- [ ] **Phase 3A — persistent-mapped ring buffers for visible + indirect** (next)
- [ ] Phase 3B — GPU-side compute-shader culling
- [ ] Screen-space contribution culling
- [ ] Hierarchical-Z occlusion culling
- [ ] Distance-based LOD selection
- [ ] Vulkan/MoltenVK backend for macOS
- [ ] Embedded Python scripting console
