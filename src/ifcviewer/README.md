# IfcViewer

A high-performance native IFC viewer built on IfcOpenShell's C++ geometry engine with a Qt6 interface and OpenGL 4.5 rendering.

## Architecture

```
+-------------------------------------------+
|  Qt6 Application (MainWindow)             |
|  +----------+ +--------------------------+|
|  | Element  | | 3D Viewport              ||
|  | Tree     | | (QWindow + OpenGL 4.5)   ||
|  |          | |                          ||
|  +----------+ | Single VBO/EBO           ||
|  | Property | | DrawElementsBaseVertex   ||
|  | Table    | | GPU pick pass            ||
|  +----------+ +--------------------------+|
|  | Status / Progress                      |
+-------------------------------------------+
        ^                    ^
        |                    |
  element metadata     UploadChunks
        |                    |
+-------------------------------------------+
|  GeometryStreamer (background QThread)     |
|  IfcGeom::Iterator with N threads         |
|  (one per CPU core by default)            |
+-------------------------------------------+
```

### Key design decisions

- **QWindow viewport** embedded via `QWidget::createWindowContainer()`. This gives us a raw native surface for OpenGL, bypassing `QOpenGLWidget`'s compositor overhead.
- **One big vertex buffer + index buffer** (64 MB + 32 MB initial). Geometry is appended as it streams in. No per-object VBOs, no rebinding.
- **Interleaved vertex format**: position (3 floats) + normal (3 floats) + object ID (1 float, bitcast uint32) = 28 bytes per vertex.
- **GPU object picking**: a second render pass writes object IDs to an R32UI framebuffer. Click reads back one pixel. No CPU-side raycasting.
- **Multi-threaded tessellation**: `IfcGeom::Iterator` runs on a background thread and internally parallelizes geometry conversion across all CPU cores.
- **Non-blocking streaming**: the iterator emits `UploadChunk` signals via Qt's queued connection. The main thread uploads to the GPU without blocking iteration.
- **World coordinates**: geometry is emitted in world space (`use-world-coords=true`) so no per-object transform matrices are needed on the GPU.

### Files

| File | Purpose |
|------|---------|
| `main.cpp` | Application entry point, GL 4.5 surface format, CLI argument parsing |
| `MainWindow.h/cpp` | Qt main window: dockable element tree, property table, status bar, menus |
| `ViewportWindow.h/cpp` | OpenGL 4.5 Core renderer: shaders, buffer management, camera, picking |
| `GeometryStreamer.h/cpp` | Background geometry processing: loads IFC, runs iterator, emits chunks |
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
# Open a file directly
./IfcViewer model.ifc

# Or use File -> Open from the menu
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
| Ctrl+O | Open file |
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
    uint32_t index_offset;   // byte offset into the shared EBO
    uint32_t index_count;    // number of indices (triangles * 3)
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

### Phase 2: Spatial Tiling (optional, for large models)

For models exceeding ~10k objects, spatial tiling groups nearby objects into
tiles and culls at the tile level rather than per-object. This reduces the
number of frustum tests from N_objects to N_tiles (typically hundreds to low
thousands).

#### When tiling activates

Tiling is **optional and non-disruptive**. The system treats a non-tiled model
as the degenerate case of "one tile containing everything" — the rendering loop
always iterates tiles, so no separate code path is needed.

Tiling activates in one of three ways:

1. **Preprocessed cache exists**: If a `.ifcview` sidecar file is found next to
   the `.ifc` file, the tile structure is loaded from it instantly. The model
   uploads geometry in tile order.
2. **Automatic by size**: If the model has more than a configurable threshold of
   objects (default 10k), a background task builds the spatial tree after
   initial loading completes. Until it finishes, phase 1 culling handles
   visibility.
3. **Explicit user action**: A "preprocess for performance" option builds the
   spatial tree and saves the sidecar for future loads.

#### Spatial subdivision

The world-space bounding box of the entire model is subdivided using a
**loose octree**:

- The root node covers the scene AABB.
- Each node is split when it contains more than a threshold number of objects
  (e.g. 256).
- Objects are assigned to the smallest node that fully contains their AABB.
- "Loose" bounds (inflated by 1.5x) reduce the number of objects that span
  multiple nodes.
- Leaf nodes become tiles.

An octree adapts to non-uniform object density (common in buildings — lots of
detail in MEP risers, sparse in open atriums) better than a uniform grid.

#### EBO re-sorting

For tile-level culling to translate into contiguous index ranges, the EBO must
be sorted so that all indices for objects in the same tile are adjacent.

This happens via **deferred compaction**:

1. During initial load, geometry uploads in iterator order (fast first frame,
   phase 1 culling active).
2. After loading completes, a background thread:
   a. Builds the octree from the per-object AABBs (already computed in phase 1).
   b. Determines the tile for each object.
   c. Computes the new index order (sorted by tile, then by object within tile).
   d. Builds a new EBO on the CPU.
3. The main thread uploads the new EBO in one `glNamedBufferSubData` call and
   swaps in the tile metadata. One frame of stutter, bounded by EBO upload
   time.

The per-tile metadata:

```cpp
struct TileInfo {
    float    aabb_min[3];    // tile bounding box (union of contained AABBs)
    float    aabb_max[3];
    uint32_t index_offset;   // into the re-sorted EBO
    uint32_t index_count;    // sum of all contained objects' indices
    uint32_t object_count;   // for stats / debugging
};
```

#### Preprocessed sidecar format

The `.ifcview` file stores:

- Octree structure (node hierarchy, split planes).
- Per-object tile assignment (object_id → tile_id mapping).
- Per-tile index order (so the EBO can be built in tile order directly during
  upload, skipping the compaction pass entirely).
- File hash of the source `.ifc` (invalidation check).

This makes second-and-subsequent loads of the same model significantly faster:
the spatial tree doesn't need to be rebuilt, and geometry uploads in tile order
from the start.

#### Performance characteristics

| Metric | Value |
|--------|-------|
| Tile count (typical) | 500–5,000 for a large building |
| Per-frame frustum tests | N_tiles instead of N_objects |
| 500k objects, ~2k tiles | ~0.01 ms frustum testing |
| Memory overhead | ~64 bytes/tile + 32 bytes/object (phase 1 metadata retained) |
| Background compaction | 1–5 seconds for 1M objects (single-threaded) |
| Sidecar file size | ~10–50 KB (indices + tree, no geometry) |

#### Spatial coherence bonus

Beyond culling, tile-sorted EBOs improve GPU cache performance. When the GPU
rasterizes a tile's triangles, the vertices are contiguous in the VBO, so the
post-transform vertex cache hits more often. This can yield 10–20% rasterization
speedup even when nothing is culled (e.g. zoomed out to see the whole model).

### Phase 3: GPU-Driven Indirect Draw

For models with 500k+ objects, even tile-level CPU culling is fast, but the
real bottleneck shifts to draw call submission. Phase 3 moves all per-frame
visibility decisions to the GPU via compute shaders and indirect draw commands.

#### How it works

Phase 3 is **approach 2 layered on top of approach 3**. It does not replace
tiling — it accelerates it.

1. **Upload phase** (once, at load time):
   - Per-tile AABBs are uploaded to a GPU SSBO (`tile_aabbs`).
   - One `DrawElementsIndirectCommand` per tile is written to an indirect draw
     buffer:
     ```c
     struct DrawElementsIndirectCommand {
         uint count;          // tile's total index count
         uint instanceCount;  // 1
         uint firstIndex;     // offset into EBO
         uint baseVertex;     // 0 (indices are global)
         uint baseInstance;   // tile_id (available in shader via gl_DrawID)
     };
     ```
   - A "template" copy of the indirect buffer is kept so the compute shader
     can reset culled commands each frame without re-uploading from CPU.

2. **Cull phase** (every frame, on the GPU):
   - The CPU uploads 6 frustum plane vec4s as a uniform or small UBO.
   - A compute shader dispatches `ceil(N_tiles / 64)` workgroups:
     ```glsl
     layout(local_size_x = 64) in;

     void main() {
         uint tile_id = gl_GlobalInvocationID.x;
         if (tile_id >= tile_count) return;

         // Copy from template (resets any previously zeroed commands)
         commands[tile_id] = template_commands[tile_id];

         // Frustum test
         if (!aabb_vs_frustum(tile_aabbs[tile_id], frustum_planes)) {
             commands[tile_id].count = 0;  // culled: GPU skips zero-count draws
         }
     }
     ```
   - A memory barrier ensures the indirect buffer is visible to the draw stage.

3. **Draw phase** (every frame):
   - One call: `glMultiDrawElementsIndirect(GL_TRIANGLES, GL_UNSIGNED_INT,
     nullptr, N_tiles, 0)`.
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
  previous frame, then test tile AABBs against it in the compute shader. Tiles
  fully behind closer geometry get culled. This handles interior-heavy BIM
  models well (most rooms are occluded from any given viewpoint).
- **Distance-based LOD**: the compute shader can select different index ranges
  (coarse vs. fine tessellation) per tile based on distance to camera.
- **Contribution culling**: tiles whose screen-space projection is below a
  pixel threshold get `count = 0`. Removes distant small objects.

#### Performance characteristics

| Metric | Value |
|--------|-------|
| CPU per-frame work | ~0.01 ms (constant, independent of model size) |
| GPU compute dispatch | ~0.02 ms for 2k tiles |
| Draw call overhead | 1 indirect multi-draw call |
| GPU memory overhead | ~48 bytes/tile (AABB SSBO) + 20 bytes/tile (indirect commands) × 2 (template + live) |
| Total for 2k tiles | ~176 KB GPU memory |
| Implementation complexity | High (compute shaders, SSBOs, memory barriers, indirect draw) |

#### When to use

Phase 3 is worthwhile when:

- The model has 500k+ objects (CPU frustum testing > 3 ms).
- Smooth 60 fps orbiting is required during interaction.
- The GPU has compute shader support (OpenGL 4.3+, which is guaranteed since
  the viewer requires 4.5).

For models under 100k objects, phase 1 alone is sufficient. For 100k–500k,
phase 2 (tiling) keeps CPU culling under 1 ms. Phase 3 is the final step that
makes the CPU frame time constant.

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
  ├─ sidecar exists?
  │   ├─ yes: load tile tree from .ifcview
  │   │       upload geometry in tile order
  │   │       (skip background compaction)
  │   └─ no:  upload geometry in iterator order (fast first frame)
  │           phase 1 culling active immediately
  │           if object_count > threshold:
  │               background: build octree, re-sort EBO, save .ifcview
  │               on completion: swap in tile structure
  └─ rendering:
      ├─ phase 3 available? → compute cull + indirect multi-draw
      └─ else               → CPU frustum test + glMultiDrawElements
```

## Roadmap

- [x] Material color support (per-vertex RGBA8)
- [x] Buffer growth (dynamic VBO/EBO resizing up to 4 GB)
- [x] Per-object frustum culling (phase 1)
- [ ] Spatial tiling with octree (phase 2)
- [ ] GPU-driven indirect draw (phase 3)
- [ ] Preprocessed `.ifcview` sidecar for fast re-loads
- [ ] Hierarchical-Z occlusion culling
- [ ] Distance-based LOD selection
- [ ] Vulkan/MoltenVK backend for macOS
- [ ] Embedded Python scripting console
