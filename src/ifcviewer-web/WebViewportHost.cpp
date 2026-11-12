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

#include "WebViewportHost.h"

#include <emscripten/emscripten.h>
#include <emscripten/html5.h>

#include <cstring>
#include <utility>

WebViewportHost::WebViewportHost(std::string canvas_selector)
    : canvas_selector_(std::move(canvas_selector)) {}

WGPUSurface WebViewportHost::createSurface(WGPUInstance instance) {
    // Emdawnwebgpu canvas-selector surface source. Same shape as
    // WGPUSurfaceSourceCanvasHTMLSelector_Emscripten in Dawn's headers.
    WGPUEmscriptenSurfaceSourceCanvasHTMLSelector canvas_desc = {};
    canvas_desc.chain.sType =
        WGPUSType_EmscriptenSurfaceSourceCanvasHTMLSelector;
    canvas_desc.selector.data   = canvas_selector_.c_str();
    canvas_desc.selector.length = canvas_selector_.size();

    WGPUSurfaceDescriptor surface_desc = {};
    surface_desc.nextInChain = &canvas_desc.chain;
    return wgpuInstanceCreateSurface(instance, &surface_desc);
}

void WebViewportHost::framebufferSize(int& width_px, int& height_px) const {
    double w_css = 0.0, h_css = 0.0;
    // Pull the element's logical (CSS-pixel) size, then multiply by DPR
    // — matches the QWindow desktop host's framebufferSize semantics.
    emscripten_get_element_css_size(canvas_selector_.c_str(), &w_css, &h_css);
    const float ratio = dpr();
    width_px  = int(w_css * double(ratio));
    height_px = int(h_css * double(ratio));
    if (width_px  < 1) width_px  = 1;
    if (height_px < 1) height_px = 1;
}

float WebViewportHost::dpr() const {
    return float(emscripten_get_device_pixel_ratio());
}

void WebViewportHost::requestFrame() {
    request_frame_pending_ = true;
}

void WebViewportHost::quit() {
    // emscripten_force_exit honours -sEXIT_RUNTIME=1; without that flag
    // the runtime swallows the call and keeps the page interactive.
    emscripten_force_exit(0);
}

bool WebViewportHost::consumeFrameRequest() {
    const bool pending = request_frame_pending_;
    request_frame_pending_ = false;
    return pending;
}
