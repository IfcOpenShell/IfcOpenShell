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

// Phase-B-step-3 scaffold for the web target. Brings up a wgpu instance
// against a #canvas via the emdawnwebgpu port, requests adapter+device
// asynchronously, configures the surface, and renders a clear color on
// each requestAnimationFrame tick. No sidecar load, no pipelines, no
// scene state yet — the goal of this commit is "something renders in a
// browser tab" so the build + canvas + wgpu plumbing is end-to-end
// verified before we wire in IfcViewerCore.

#include <emscripten/emscripten.h>
#include <emscripten/html5.h>

#include <webgpu/webgpu.h>

#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace {

// Async-arrived handles. Populated by the requestAdapter/requestDevice
// callback chain in startup(); render() short-circuits until they're
// all set. Keeps the path single-threaded — the JS event loop drives
// progress between callbacks.
WGPUInstance g_instance       = nullptr;
WGPUAdapter  g_adapter        = nullptr;
WGPUDevice   g_device         = nullptr;
WGPUQueue    g_queue          = nullptr;
WGPUSurface  g_surface        = nullptr;
WGPUTextureFormat g_surface_format = WGPUTextureFormat_Undefined;
bool         g_main_loop_started = false;

// Canvas dimensions in CSS pixels. emscripten reports the canvas size in
// CSS pixels but the GPU surface wants device pixels; we keep things at
// 1× DPR for the scaffold and re-derive on resize once we wire input.
int g_width  = 1280;
int g_height = 800;

void frame() {
    if (!g_surface || !g_device) return;

    WGPUSurfaceTexture st = {};
    wgpuSurfaceGetCurrentTexture(g_surface, &st);
    if (st.status != WGPUSurfaceGetCurrentTextureStatus_SuccessOptimal &&
        st.status != WGPUSurfaceGetCurrentTextureStatus_SuccessSuboptimal) {
        // Lost / outdated / OOM / device-lost — log once and bail out
        // of this frame so we don't queue work against a torn surface.
        static int s_complained = 0;
        if (s_complained++ < 4) {
            std::fprintf(stderr,
                "[viewer-web] surface texture status %d; skipping frame\n",
                int(st.status));
        }
        return;
    }

    WGPUTextureView view = wgpuTextureCreateView(st.texture, nullptr);

    WGPURenderPassColorAttachment ca = {};
    ca.view       = view;
    ca.loadOp     = WGPULoadOp_Clear;
    ca.storeOp    = WGPUStoreOp_Store;
    ca.clearValue = {0.18, 0.21, 0.28, 1.0}; // BonsaiViewer slate background
    ca.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDescriptor rp_desc = {};
    rp_desc.colorAttachmentCount = 1;
    rp_desc.colorAttachments     = &ca;

    WGPUCommandEncoderDescriptor enc_desc = {};
    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(g_device, &enc_desc);
    WGPURenderPassEncoder rp = wgpuCommandEncoderBeginRenderPass(enc, &rp_desc);
    wgpuRenderPassEncoderEnd(rp);
    wgpuRenderPassEncoderRelease(rp);

    WGPUCommandBufferDescriptor cb_desc = {};
    WGPUCommandBuffer cb = wgpuCommandEncoderFinish(enc, &cb_desc);
    wgpuQueueSubmit(g_queue, 1, &cb);

    wgpuCommandBufferRelease(cb);
    wgpuCommandEncoderRelease(enc);
    wgpuTextureViewRelease(view);
    wgpuTextureRelease(st.texture);
}

void configure_surface() {
    WGPUSurfaceCapabilities caps = {};
    if (wgpuSurfaceGetCapabilities(g_surface, g_adapter, &caps) != WGPUStatus_Success
        || caps.formatCount == 0) {
        std::fprintf(stderr, "[viewer-web] surface has no formats\n");
        return;
    }
    g_surface_format = caps.formats[0];
    wgpuSurfaceCapabilitiesFreeMembers(caps);

    WGPUSurfaceConfiguration cfg = {};
    cfg.device      = g_device;
    cfg.format      = g_surface_format;
    cfg.usage       = WGPUTextureUsage_RenderAttachment;
    cfg.width       = uint32_t(g_width);
    cfg.height      = uint32_t(g_height);
    cfg.alphaMode   = WGPUCompositeAlphaMode_Auto;
    cfg.presentMode = WGPUPresentMode_Fifo;
    wgpuSurfaceConfigure(g_surface, &cfg);

    if (!g_main_loop_started) {
        emscripten_set_main_loop(frame, 0, /*simulate_infinite=*/0);
        g_main_loop_started = true;
        std::fprintf(stderr,
            "[viewer-web] surface configured (%dx%d format=%d); RAF loop started\n",
            g_width, g_height, int(g_surface_format));
    }
}

void on_device_ready(WGPURequestDeviceStatus status, WGPUDevice device,
                     WGPUStringView message, void* /*ud1*/, void* /*ud2*/) {
    if (status != WGPURequestDeviceStatus_Success || !device) {
        std::fprintf(stderr, "[viewer-web] requestDevice failed: %.*s\n",
                     int(message.length), message.data ? message.data : "");
        return;
    }
    g_device = device;
    g_queue  = wgpuDeviceGetQueue(device);

    WGPUEmscriptenSurfaceSourceCanvasHTMLSelector canvas = {};
    canvas.chain.sType = WGPUSType_EmscriptenSurfaceSourceCanvasHTMLSelector;
    static const char* kSelector = "#viewer-canvas";
    canvas.selector.data   = kSelector;
    canvas.selector.length = std::strlen(kSelector);

    WGPUSurfaceDescriptor sd = {};
    sd.nextInChain = &canvas.chain;
    g_surface = wgpuInstanceCreateSurface(g_instance, &sd);
    if (!g_surface) {
        std::fprintf(stderr,
            "[viewer-web] wgpuInstanceCreateSurface returned null "
            "(canvas '#viewer-canvas' missing?)\n");
        return;
    }
    configure_surface();
}

void on_adapter_ready(WGPURequestAdapterStatus status, WGPUAdapter adapter,
                      WGPUStringView message, void* /*ud1*/, void* /*ud2*/) {
    if (status != WGPURequestAdapterStatus_Success || !adapter) {
        std::fprintf(stderr, "[viewer-web] requestAdapter failed: %.*s\n",
                     int(message.length), message.data ? message.data : "");
        return;
    }
    g_adapter = adapter;

    WGPUDeviceDescriptor dd = {};
    WGPURequestDeviceCallbackInfo cb = {};
    cb.mode     = WGPUCallbackMode_AllowSpontaneous;
    cb.callback = on_device_ready;
    wgpuAdapterRequestDevice(adapter, &dd, cb);
}

} // namespace

int main() {
    WGPUInstanceDescriptor desc = {};
    g_instance = wgpuCreateInstance(&desc);
    if (!g_instance) {
        std::fprintf(stderr, "[viewer-web] wgpuCreateInstance returned null\n");
        return 1;
    }

    WGPURequestAdapterOptions opts = {};
    WGPURequestAdapterCallbackInfo cb = {};
    cb.mode     = WGPUCallbackMode_AllowSpontaneous;
    cb.callback = on_adapter_ready;
    wgpuInstanceRequestAdapter(g_instance, &opts, cb);

    // main() returns; the browser keeps the JS event loop running so
    // the async adapter/device callbacks above land naturally and the
    // main loop kicks off from configure_surface().
    return 0;
}
