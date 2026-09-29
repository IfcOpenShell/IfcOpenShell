/**
 * Objective-C++ bridge between ViewportWindow (pure C++) and Cocoa /
 * QuartzCore (Objective-C). Compiled only on macOS — see CMakeLists.txt.
 *
 * Qt's QWindow::winId() returns the backing NSView* (as a WId) on macOS;
 * we need a CAMetalLayer attached to that view to hand to wgpu-native
 * via WGPUSurfaceSourceMetalLayer. Doing that requires Objective-C, so
 * the actual layer attach lives in MetalSurface_mac.mm.
 */

#ifndef WGPU_METAL_SURFACE_MAC_H
#define WGPU_METAL_SURFACE_MAC_H

#if defined(__APPLE__)

#ifdef __cplusplus
extern "C" {
#endif

/// Ensures the given NSView has a CAMetalLayer as its backing layer.
/// Returns the CAMetalLayer pointer (`void*` so callers don't need to
/// pull QuartzCore into their TU); the layer is owned by the NSView.
/// Returns nullptr if `nsview_ptr` is null.
void* wgpu_macos_attach_metal_layer(void* nsview_ptr);

#ifdef __cplusplus
}
#endif

#endif // __APPLE__

#endif // WGPU_METAL_SURFACE_MAC_H
