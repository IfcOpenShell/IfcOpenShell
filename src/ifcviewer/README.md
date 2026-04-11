# IfcViewer

A high-performance native IFC viewer built on IfcOpenShell's C++ geometry engine with a Qt6 interface and OpenGL 4.5 rendering.

## Architecture

```
+-------------------------------------------+
|  Qt6 Application (MainWindow)             |
|  +----------+ +--------------------------+|
|  | Element  | | 3D Viewport              ||
|  | Tree     | | (QWindow + OpenGL 4.5)   ||
|  | (per-    | |                          ||
|  |  model)  | | Per-model VAO/VBO/EBO    ||
|  +----------+ | glMultiDrawElements      ||
|  | Property | | BVH frustum culling      ||
|  | Table    | | GPU pick pass            ||
|  +----------+ +--------------------------+|
|  | Status / Progress / Stats              |
+-------------------------------------------+
        ^                    ^
        |                    |
  element metadata     UploadChunks / Sidecar
        |                    |
+-------------------------------------------+
|  GeometryStreamer (one per loaded model)   |
|  IfcGeom::Iterator with N threads         |
|  (models loaded sequentially)             |
+-------------------------------------------+
```

### Key design decisions

- **QWindow viewport** embedded via `QWidget::createWindowContainer()`. This gives us a raw native surface for OpenGL, bypassing `QOpenGLWidget`'s compositor overhead.
- **Per-model GPU buffers**: each loaded model gets its own VAO/VBO/EBO. No shared buffer, no cross-model copies on growth. Removing a model frees its GPU memory immediately.
- **Interleaved vertex format**: position (3 floats) + normal (3 floats) + object ID (1 float, bitcast uint32) + color (RGBA8 packed into 1 float) = 32 bytes per vertex.
- **Progressive GPU upload**: bulk sidecar loads allocate empty GPU buffers, then stream data in 48 MB chunks per frame. VBO uploads first (no objects visible), then EBO (objects appear progressively as their index range lands). The viewport stays interactive throughout — you can orbit already-loaded models while new ones stream in.
- **Non-blocking sidecar loading**: sidecar files are read on a background thread. The heavy disk I/O (potentially gigabytes) never blocks the render loop. Only the final GPU upload and tree population happen on the main thread.
- **BVH frustum culling**: per-model BVH trees cull entire subtrees of objects in one frustum test, reducing per-frame cost from O(N) to O(log N). Falls back to linear scan during progressive upload; BVH activates once the model is fully loaded.
- **GPU object picking**: a second render pass writes object IDs to an R32UI framebuffer. Click reads back one pixel. No CPU-side raycasting.
- **Multi-model support**: multiple IFC files can be loaded simultaneously. Each model gets its own `GeometryStreamer` (owning the `ifcopenshell::file` for property lookup). Models are loaded sequentially. Per-model visibility toggle and removal are supported.
- **Multi-threaded tessellation**: `IfcGeom::Iterator` runs on a background thread and internally parallelizes geometry conversion across all CPU cores.
- **Non-blocking streaming**: the iterator emits `UploadChunk` signals via Qt's queued connection. The main thread uploads to the GPU without blocking iteration.
- **World coordinates**: geometry is emitted in world space (`use-world-coords=true`) so no per-object transform matrices are needed on the GPU.

### Files

| File | Purpose |
|------|---------|
| `main.cpp` | Application entry point, GL 4.5 surface format, CLI argument parsing |
| `MainWindow.h/cpp` | Qt main window: multi-model project management, element tree, property table, status bar |
| `ViewportWindow.h/cpp` | OpenGL 4.5 Core renderer: shaders, buffer management, camera, frustum culling, BVH traversal, picking |
| `GeometryStreamer.h/cpp` | Background geometry processing: loads IFC, runs iterator, emits chunks (one per model) |
| `BvhAccel.h/cpp` | BVH construction (median-split), per-model trees, EBO reordering |
| `SidecarCache.h/cpp` | Raw binary `.ifcview` sidecar read/write |
| `AppSettings.h/cpp` | Persisted application preferences (geometry library, show stats) |
| `SettingsWindow.h/cpp` | Settings dialog UI |
| `CMakeLists.txt` | Build configuration |

## Dependencies

- **Qt6** (Core, Gui, Widgets)
- **OpenGL 4.5** (GL_ARB_direct_state_access) - available on Windows and Linux; macOS will need a Vulkan/MoltenVK backend (not yet implemented)
- **IfcOpenShell C++ libraries** (IfcParse, IfcGeom, and their dependencies: Open CASCADE, Boost, Eigen3, optionally CGAL)

## Building

IfcViewer is built as part of the IfcOpenShell CMake project. You do not need to build everything - disable the targets you don't need.

### Minimal build (IfcViewer only)

From the repository root:

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

This builds only IfcParse, IfcGeom (with geometry kernels), and IfcViewer itself. All other targets (IfcConvert, Python bindings, serializers, etc.) are skipped.

If Qt6 is not in a standard location, pass `-DQT_DIR=/path/to/qt6`.

### Full build with IfcViewer enabled

```sh
cmake ../cmake -DBUILD_IFCVIEWER=ON
make -j$(nproc)
```

## Usage

```sh
# Open one or more files from the command line
./IfcViewer arch.ifc struct.ifc mep.ifc

# Or use File -> Add Files from the menu (supports multiselect)
./IfcViewer
```

### Controls

| Input | Action |
|-------|--------|
| Middle mouse drag | Orbit camera |
| Shift + middle mouse drag | Pan camera |
| Scroll wheel | Zoom |
| Left click | Select object (highlights in viewport and tree) |

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| Ctrl+O | Add files |
| Ctrl+Q | Quit |

## Performance Strategy

The viewer targets smooth orbiting at 60 fps on models up to 1 million IFC objects.
Rendering performance is addressed in three phases. Each phase builds on the
previous one, and the system is designed so that smaller models never pay for
optimizations they don't need.

### Phase 1: Per-Object Frustum Culling (CPU)

**Status:** Implemented.

The simplest win: don't draw what's off screen.

#### Data model

During `uploadChunk()`, the viewport records a small metadata struct for every
object that enters the GPU buffers:

```cpp
struct ObjectDrawInfo {
    uint32_t index_offset;   // byte offset into the model's EBO
    uint32_t index_count;    // number of indices (triangles * 3)
    uint32_t model_id;       // which model this object belongs to
    float    aabb_min[3];    // world-space axis-aligned bounding box
    float    aabb_max[3];    // (computed from vertex positions at upload time)
};
```

This costs 32 bytes per object. For 1M objects that's ~32 MB of CPU-side
metadata — negligible next to the vertex data.

#### Frustum extraction

Each frame, before drawing, six clip planes are extracted from the
view-projection matrix (`VP = proj * view`). The standard Griess-Hartmann
method pulls them directly from the matrix rows:

```
left   = VP[3] + VP[0]
right  = VP[3] - VP[0]
bottom = VP[3] + VP[1]
top    = VP[3] - VP[1]
near   = VP[3] + VP[2]
far    = VP[3] - VP[2]
```

Each plane is stored as (a, b, c, d) and normalized so that
`a*x + b*y + c*z + d` gives the signed distance from the plane.

#### AABB-frustum test

For each object, the AABB is tested against all six planes using the
"p-vertex / n-vertex" method:

- For each plane, find the AABB corner most in the direction of the plane
  normal (the p-vertex).
- If the p-vertex is on the negative side of the plane, the entire AABB is
  outside the frustum → cull.
- If any plane culls the object, skip it.

This test is conservative: it never culls a visible object, but may
occasionally keep an invisible one (when the AABB straddles a frustum corner).
That's fine — false positives just cost a few extra triangles.

#### Drawing visible objects

The surviving objects' `(index_count, index_offset)` pairs are passed to
`glMultiDrawElements()` in a single call. This replaces the previous single
`glDrawElements()` that drew everything. The GPU processes only the index
ranges that survived the frustum test.

Alternatively, for the pick pass (which runs less frequently), the same
visibility list is reused — objects culled from the main pass are also culled
from picking.

#### Performance characteristics

| Metric | Value |
|--------|-------|
| Per-object cost | ~6 dot products + 6 comparisons per frame |
| 50k objects | ~0.3 ms on a modern CPU core |
| 500k objects | ~3 ms (starts to matter at 60 fps) |
| 1M objects | ~6 ms (too expensive — need phase 3) |
| Memory overhead | 32 bytes/object |
| Load-time overhead | Near zero (AABB computed during existing upload) |

Phase 1 is sufficient for models up to ~100k objects. Beyond that, the CPU-side
frustum test becomes a measurable fraction of the frame budget, motivating
phase 3.

### Phase 2: BVH Acceleration (optional, for large models)

**Status:** Implemented.

For models exceeding ~100 objects, a bounding volume hierarchy (BVH) groups
nearby objects into a binary tree and culls entire subtrees in one frustum
test. This reduces the number of AABB-frustum tests from O(N_objects) to
O(log N) in the best case (camera zoomed into a corner) and gives a constant
overhead for the common case where most of the model is on screen.

A BVH was chosen over an octree because BIM data is spatially non-uniform —
dense MEP risers in one zone, sparse open atriums in another. An octree
subdivides space uniformly, wasting nodes on empty regions and creating deep
chains in dense ones. A BVH adapts its splits to the actual object
distribution, producing balanced trees regardless of density variation.

#### When the BVH activates

The BVH is **optional and non-disruptive**. Until it is built, phase 1's
linear scan handles all culling. The rendering loop checks for an active BVH
and falls back to the linear scan for any model that doesn't have one.

The BVH activates in one of two ways:

1. **Sidecar cache exists**: If a `.ifcview` file is found next to the `.ifc`
   file, the BVH is loaded from it instantly (raw memory read, no parsing).
   The model uses BVH culling from the first frame after loading.
2. **Automatic build**: After streaming finishes, a background thread builds
   the BVH from the per-object AABBs already computed in phase 1. Until it
   completes, phase 1 culling handles visibility. On completion, the render
   thread picks up the BVH on the next frame. The sidecar is written for
   future loads.

Models with fewer than 32 objects skip the BVH entirely — the overhead of tree
traversal is worse than a linear scan at that scale.

#### BVH node layout

Each node is 32 bytes, so two nodes fit in one 64-byte cache line:

```cpp
struct BvhNode {
    float    aabb_min[3];     // world-space bounding box (12 bytes)
    float    aabb_max[3];     // (12 bytes)
    uint32_t right_or_first;  // interior: right child index; leaf: first object index (4 bytes)
    uint16_t count;           // 0 = interior node; >0 = leaf with this many objects (2 bytes)
    uint16_t axis;            // split axis for interior (0=x, 1=y, 2=z); unused for leaf (2 bytes)
};
```

Interior nodes store the right child index; the left child is always the
immediately next node in the array (implicit in pre-order DFS layout, no
pointer needed). Leaf nodes reference a contiguous range in a sorted
object-index array.

The BVH is stored as a flat `std::vector<BvhNode>` in pre-order DFS layout.
This means a depth-first traversal (which is what frustum culling does) reads
memory sequentially, maximizing prefetch and cache-line utilization.

#### Build algorithm: object-median split

1. Compute the centroid of each object's AABB.
2. Find the longest axis of the current node's bounding box.
3. Use `std::nth_element` to partition objects at the median centroid on that
   axis. This is O(n) — no full sort needed.
4. Recurse on each half. Terminate when the node contains ≤ 8 objects (leaf).
5. Write nodes into the flat array in pre-order DFS.

Total build time is O(n log n). For 100k objects this is well under 100 ms on
a single core.

SAH (Surface Area Heuristic) is the gold standard for ray-tracing BVHs, but
for frustum culling — where we test 6 planes and early-out entire subtrees —
the quality difference vs. median split is negligible. Median split is simpler
and produces reliably balanced trees.

#### Frustum traversal

The traversal uses an explicit stack on the C++ stack (no heap allocation,
no recursion):

```
stack[64] = {0}   // start at root; depth 64 handles billions of objects
while stack not empty:
    node = nodes[stack.pop()]
    if node AABB outside frustum: continue   // cull entire subtree
    if leaf:
        for each object in node:
            if object AABB in frustum: emit to visible list
    else:
        push right child, push left child    // left processed first (DFS)
```

When the camera is zoomed into a corner of the model, the traversal skips
large portions of the tree after testing only a handful of interior nodes.
When zoomed out to see everything, the traversal visits all leaves but the
overhead of the interior-node tests is small relative to the leaf work.

#### Per-model BVH

Each loaded model gets its own BVH. During frustum culling, the outer loop
iterates over models (skipping hidden/removed ones); the inner loop traverses
that model's BVH. This means hiding or removing a model is free — just skip
its BVH, no tree modification needed.

```cpp
struct ModelBvh {
    uint32_t model_id;
    std::vector<BvhNode> nodes;            // flat BVH node array
    std::vector<uint32_t> object_indices;  // indices into object_draw_info_
};
```

#### EBO re-sorting

For BVH culling to maximise GPU cache performance, the EBO is re-sorted so
that objects in the same BVH leaf are contiguous. This happens via **deferred
compaction**:

1. During initial load, geometry uploads in iterator order (fast first frame,
   phase 1 culling active).
2. After the BVH build completes on the background thread:
   a. Walk the BVH leaves in DFS order.
   b. For each object in each leaf, copy its index data to a new EBO buffer,
      updating `ObjectDrawInfo::index_offset` accordingly.
   c. Package the reordered EBO + updated draw info as a `BvhBuildResult`.
3. The render thread picks up the result on the next frame: one
   `glNamedBufferSubData` call to re-upload the EBO, then swap in the new
   draw info and activate the BVH. One frame of stutter, bounded by EBO
   upload time (~5 ms for 32 MB).

#### Async build and render-thread handoff

The BVH build must not stall the render loop:

1. `buildBvhAsync()` snapshots `object_draw_info_` under the upload mutex,
   then launches a `std::thread`.
2. The thread builds the BVH and reordered EBO, then stores the result in a
   `pending_bvh_result_` pointer under a separate mutex.
3. At the top of each `render()` call, `applyBvhResult()` checks for a
   pending result. If found, it re-uploads the EBO (requires GL context),
   swaps the draw info, and activates the BVH.
4. Until the BVH is ready, phase 1's linear scan runs every frame as before.

#### Preprocessed sidecar format (`.ifcview`)

The sidecar is a raw memory dump (Blender `.blend`-style) — no serialization
format, no parsing. It stores everything needed to display the model without
re-tessellating: vertex data, index data, per-object metadata, element tree
info, and the BVH. Loading is just `fread` into vectors → GPU upload →
render. The expensive `IfcGeom::Iterator` tessellation is skipped entirely.

The IFC file is still parsed on demand (in background) for detailed property
lookup; the sidecar provides the basic properties (name, type, GUID)
immediately.

```
SidecarHeader            (16 bytes: magic, version, endian, reserved)
uint64_t                 source_file_size

uint32_t + float[]       vertex data    (interleaved, 8 floats/vertex)
uint32_t + uint32_t[]    index data     (global indices, ready for EBO)
uint32_t + ObjectDrawInfo[]   per-object draw metadata
uint32_t + PackedElementInfo[]  element tree records (fixed-size)
uint32_t + char[]        string table   (concatenated UTF-8: guid, name, type)

uint32_t                 num_bvh_models
per model:
  uint32_t model_id
  uint32_t + BvhNode[]        BVH node array
  uint32_t + uint32_t[]       object indices
```

Staleness check: `source_file_size` is compared against the actual IFC file
size. If mismatched, the sidecar is stale and is rebuilt. This is cheap and
sufficient for a local cache (no hash computation on multi-GB files).

Endianness: if the marker reads back as `0x01020304`, the file was written on
the same architecture — just `fread` the structs directly. Otherwise, reject
the sidecar and rebuild.

#### Performance characteristics

| Metric | Value |
|--------|-------|
| BVH build time (100k objects) | < 100 ms (single-threaded, background) |
| Per-frame traversal (100k objects, 50% visible) | ~0.1 ms |
| Per-frame traversal (100k objects, 5% visible) | ~0.02 ms |
| Memory overhead | 32 bytes/node + 4 bytes/object index (~1.5× object count) |
| EBO reorder (one-time) | 1–5 ms upload for 32 MB EBO |
| Sidecar file size | ~same as geometry data (vertices + indices + metadata) |
| Sidecar read time | bounded by disk I/O (~500 ms for 640 MB, ~2 s for 2.8 GB from NVMe) |
| GPU upload time | progressive: ~48 MB/frame (~1 s for 2.8 GB at 60 fps, non-blocking) |

#### Spatial coherence bonus

Beyond culling, BVH-leaf-sorted EBOs improve GPU cache performance. When the
GPU rasterizes a leaf's triangles, the vertices are close together in the VBO,
so the post-transform vertex cache hits more often. This can yield 10–20%
rasterization speedup even when nothing is culled (e.g. zoomed out to see the
whole model).

### Phase 3: GPU-Driven Indirect Draw

For models with 500k+ objects, even tile-level CPU culling is fast, but the
real bottleneck shifts to draw call submission. Phase 3 moves all per-frame
visibility decisions to the GPU via compute shaders and indirect draw commands.

#### How it works

Phase 3 builds on the BVH from phase 2. It does not replace the BVH — it
moves the per-frame traversal to the GPU.

1. **Upload phase** (once, at load time):
   - Per-leaf AABBs from the BVH are uploaded to a GPU SSBO (`leaf_aabbs`).
   - One `DrawElementsIndirectCommand` per BVH leaf is written to an indirect
     draw buffer:
     ```c
     struct DrawElementsIndirectCommand {
         uint count;          // leaf's total index count
         uint instanceCount;  // 1
         uint firstIndex;     // offset into EBO (from BVH leaf order)
         uint baseVertex;     // 0 (indices are global)
         uint baseInstance;   // leaf_id (available in shader via gl_DrawID)
     };
     ```
   - A "template" copy of the indirect buffer is kept so the compute shader
     can reset culled commands each frame without re-uploading from CPU.

2. **Cull phase** (every frame, on the GPU):
   - The CPU uploads 6 frustum plane vec4s as a uniform or small UBO.
   - A compute shader dispatches `ceil(N_leaves / 64)` workgroups:
     ```glsl
     layout(local_size_x = 64) in;

     void main() {
         uint leaf_id = gl_GlobalInvocationID.x;
         if (leaf_id >= leaf_count) return;

         // Copy from template (resets any previously zeroed commands)
         commands[leaf_id] = template_commands[leaf_id];

         // Frustum test
         if (!aabb_vs_frustum(leaf_aabbs[leaf_id], frustum_planes)) {
             commands[leaf_id].count = 0;  // culled: GPU skips zero-count draws
         }
     }
     ```
   - A memory barrier ensures the indirect buffer is visible to the draw stage.

3. **Draw phase** (every frame):
   - One call: `glMultiDrawElementsIndirect(GL_TRIANGLES, GL_UNSIGNED_INT,
     nullptr, N_leaves, 0)`.
   - The GPU reads the indirect buffer, skips tiles with `count == 0`, and
     draws the rest. Zero CPU-side per-object or per-tile work.

#### What the CPU does per frame

1. Upload 6 vec4 frustum planes (96 bytes).
2. Dispatch one compute shader.
3. Issue one `glMultiDrawElementsIndirect`.
4. Swap buffers.

That's it. The CPU frame time is essentially constant regardless of model size.

#### Future extensions (enabled by this architecture)

Once the compute-based cull pass exists, it's straightforward to add:

- **Hierarchical-Z occlusion culling**: render a coarse depth buffer from the
  previous frame, then test BVH leaf AABBs against it in the compute shader.
  Leaves fully behind closer geometry get culled. This handles interior-heavy
  BIM models well (most rooms are occluded from any given viewpoint).
- **Distance-based LOD**: the compute shader can select different index ranges
  (coarse vs. fine tessellation) per leaf based on distance to camera.
- **Contribution culling**: leaves whose screen-space projection is below a
  pixel threshold get `count = 0`. Removes distant small objects.

#### Performance characteristics

| Metric | Value |
|--------|-------|
| CPU per-frame work | ~0.01 ms (constant, independent of model size) |
| GPU compute dispatch | ~0.02 ms for 2k leaves |
| Draw call overhead | 1 indirect multi-draw call |
| GPU memory overhead | ~48 bytes/leaf (AABB SSBO) + 20 bytes/leaf (indirect commands) × 2 (template + live) |
| Total for 2k leaves | ~176 KB GPU memory |
| Implementation complexity | High (compute shaders, SSBOs, memory barriers, indirect draw) |

#### When to use

Phase 3 is worthwhile when:

- The model has 500k+ objects (CPU frustum testing > 3 ms).
- Smooth 60 fps orbiting is required during interaction.
- The GPU has compute shader support (OpenGL 4.3+, which is guaranteed since
  the viewer requires 4.5).

For models under 100k objects, phase 1 alone is sufficient. For 100k–500k,
phase 2 (BVH) keeps CPU culling well under 1 ms. Phase 3 is the final step
that makes the CPU frame time constant.

### Summary

```
Model size       Active phases     CPU cull cost     Draw calls
─────────────    ──────────────    ──────────────    ──────────
< 10k objects    Phase 1           ~0.06 ms          1 multi-draw
10k–100k         Phase 1           ~0.6 ms           1 multi-draw
100k–500k        Phase 1 + 2       ~0.01 ms          1 multi-draw
500k–1M+         Phase 1 + 2 + 3   ~0 (GPU)          1 indirect multi-draw
```

The load path:

```
open(model.ifc):
  ├─ sidecar exists (.ifcview)?
  │   ├─ yes: background thread reads sidecar file (non-blocking I/O)
  │   │       → allocate per-model VAO/VBO/EBO (empty, exact size)
  │   │       → progressive GPU upload: 48 MB/frame VBO, then EBO
  │   │       → objects appear as EBO chunks land
  │   │       → BVH activates once fully loaded
  │   │       → viewport interactive throughout
  │   └─ no:  stream from IFC via GeometryStreamer
  │           → uploadChunk() appends to per-model buffers (immediately drawable)
  │           → phase 1 linear-scan culling active from first chunk
  │           → on completion: background BVH build, re-sort EBO, save .ifcview
  └─ rendering (per model, per frame):
      ├─ phase 3 available?  → compute cull + indirect multi-draw
      ├─ BVH available?      → BVH traversal + glMultiDrawElements
      └─ else / progressive  → linear scan of active objects + glMultiDrawElements
```

## Roadmap

- [x] Material color support (per-vertex RGBA8)
- [x] Per-model GPU buffers (VAO/VBO/EBO per model, no cross-model copies)
- [x] Per-object frustum culling (phase 1)
- [x] BVH acceleration with per-model trees (phase 2)
- [x] Raw binary `.ifcview` sidecar cache (full geometry + BVH, Blender-style)
- [x] Non-blocking sidecar loading (background thread I/O)
- [x] Progressive GPU upload (48 MB/frame chunked VBO/EBO transfer)
- [ ] GPU-driven indirect draw (phase 3)
- [ ] Hierarchical-Z occlusion culling
- [ ] Distance-based LOD selection
- [ ] Vulkan/MoltenVK backend for macOS
- [ ] Embedded Python scripting console
