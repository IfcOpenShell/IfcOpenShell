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

## Roadmap

- [ ] Material color support (currently renders default grey per batch)
- [ ] Buffer growth (reallocate when 64 MB VBO fills up)
- [ ] `glMultiDrawElementsIndirect` for fewer draw calls
- [ ] Vulkan/MoltenVK backend for macOS
- [ ] Spatial tree (BVH) for frustum culling
- [ ] LOD: coarse tessellation during streaming, refine in background
- [ ] Embedded Python scripting console
- [ ] CJK text input support (Qt6 handles this natively)
