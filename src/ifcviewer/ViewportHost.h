/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#ifndef VIEWPORTHOST_H
#define VIEWPORTHOST_H

// Abstraction layer between the platform-agnostic ViewportCore (wgpu
// state, scene state, render path, cull, input) and whichever host owns
// the native window / canvas / event loop. On desktop the host is a
// QWindow-derived ViewportWindow; on web it'll be a small canvas-bound
// shell in src/ifcviewer-web. The host implements this interface so
// ViewportCore can call back into it for:
//
//   - surface creation (only the host knows its native handle)
//   - framebuffer geometry (size, DPR)
//   - scheduling the next render tick (QWindow::requestUpdate vs RAF)
//   - quitting the process
//   - bubbling user-facing notifications (selection changed, picked
//     object, tool mode, frame stats) up to whatever signal/callback
//     mechanism the host uses
//
// All host-side notifications have default empty implementations so
// hosts only override the ones they care about — minimal-boilerplate
// hosts (a screenshot CI runner, the web spike before UI lands) can
// ignore the rest. Inverting control this way keeps ViewportCore from
// having to know whether it's running inside Qt's event loop or
// Emscripten's main-loop.

#include <webgpu/webgpu.h>

#include <cstdint>
#include <string>

class ViewportHost {
public:
    virtual ~ViewportHost() = default;

    // Surface creation. The host wraps its native window/canvas in the
    // appropriate WGPUSurfaceDescriptor extension struct (Xlib, HWND,
    // CAMetalLayer, EmscriptenCanvas) and returns the resulting surface.
    // Returns nullptr if the surface can't be created — caller logs and
    // aborts init.
    virtual WGPUSurface createSurface(WGPUInstance instance) = 0;

    // Framebuffer geometry. width/height are in device pixels (post-
    // multiplied by devicePixelRatio); the depth attachment and surface
    // configuration both consume these.
    virtual void framebufferSize(int& width_px, int& height_px) const = 0;
    // Device pixel ratio (CSS-px → device-px). Renamed from
    // `devicePixelRatio` because QWindow already exposes that name; an
    // override conflict between qreal (QWindow) and float (a hypothetical
    // ViewportHost::devicePixelRatio) would surprise readers. `dpr` is
    // unambiguous.
    virtual float dpr() const = 0;

    // Ask the host to schedule another render tick. On Qt this is
    // QWindow::requestUpdate (coalesced + DPR-aware); on web this is a
    // requestAnimationFrame schedule. Idempotent within a tick.
    virtual void requestFrame() = 0;

    // Ask the host to terminate the process / close the tab. Used by
    // the --screenshot / --benchmark exits, and by the future
    // window-close path.
    virtual void quit() = 0;

    // ---- Notifications ----------------------------------------------------
    //
    // Each callback corresponds to something ViewportWindow currently
    // exposes as a Q_SIGNAL. Default empty body so non-Qt hosts can
    // selectively implement; the desktop ViewportWindow override
    // forwards each to emit objectPicked() / emit toolModeChanged() etc.

    virtual void onObjectPicked(uint32_t /*object_id*/) {}
    virtual void onSurfacePickedInTool(int /*x_px*/, int /*y_px*/,
                                       int /*modifiers*/) {}
    virtual void onToolModeChanged(int /*tool_mode*/) {}
    virtual void onToolBackspacePressed() {}
    // FrameStats is a Qt-using struct declared inside ViewportWindow
    // today; once the move to ViewportCore happens it'll come back here
    // as a plain POD. For B4 the desktop ViewportWindow keeps the
    // existing typed signal and this is just the placeholder.
    virtual void onFrameStats(double /*frame_ms*/, double /*cull_ms*/,
                              uint32_t /*draws*/, uint32_t /*tris*/) {}

    // Encode + save the screenshot. Called from the render path after
    // wgpu has mapped the surface-copy staging buffer back to host
    // memory; the host gets tightly-packed RGBA8 (BGRA→RGBA already
    // swapped in core) at `w × h` and writes a PNG to `path`. Default
    // body is a no-op so headless / web hosts can selectively ignore
    // it — the QtViewportHost override calls QImage::save.
    virtual void saveScreenshotRgba8(const std::string& /*path*/,
                                     const std::uint8_t* /*rgba*/,
                                     int /*w*/, int /*h*/) {}
};

#endif  // VIEWPORTHOST_H
