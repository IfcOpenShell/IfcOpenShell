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

#ifndef WEBVIEWPORTHOST_H
#define WEBVIEWPORTHOST_H

// Web implementation of ViewportHost. ViewportCore owns the wgpu state
// + render path; this class adapts the embedder hooks to a browser
// canvas (surface creation via emdawnwebgpu's canvas-selector extension,
// framebuffer size from the canvas element, requestFrame via
// requestAnimationFrame, quit via emscripten_force_exit). All
// notifications fall through to the base class no-ops for now —
// future iterations route them to DOM events / a status bar.

#include "ViewportHost.h"

#include <string>

class WebViewportHost final : public ViewportHost {
public:
    // `canvas_selector` is the CSS selector for the host <canvas> (e.g.
    // "#viewer-canvas" — matches the host page (web/ifcviewer.js)). The string is stored;
    // it must outlive the host.
    explicit WebViewportHost(std::string canvas_selector);

    WGPUSurface createSurface(WGPUInstance instance) override;
    void  framebufferSize(int& width_px, int& height_px) const override;
    float dpr() const override;
    // Sets request_frame_pending_ so the RAF callback knows to render
    // on the next browser tick. The actual frame scheduling is done by
    // the main_web.cpp loop; this avoids spamming RAF callbacks when
    // multiple sources request a frame in the same tick.
    void  requestFrame() override;
    void  quit() override;

    // True when ViewportCore has asked for a frame since the last one
    // was rendered. The main loop clears this before invoking
    // core.render().
    bool consumeFrameRequest();

private:
    std::string canvas_selector_;
    bool        request_frame_pending_ = true;  // arm an initial frame
};

#endif  // WEBVIEWPORTHOST_H
