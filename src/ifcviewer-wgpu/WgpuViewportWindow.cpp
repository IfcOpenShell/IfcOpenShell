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

#include "WgpuViewportWindow.h"

#include <QGuiApplication>
#include <QResizeEvent>
#include <QDebug>

#include <webgpu/wgpu.h>  // wgpu-native extensions (logging, MULTI_DRAW_INDIRECT, …)

#include <cstring>

// -----------------------------------------------------------------------------
// Small helpers
// -----------------------------------------------------------------------------

static QString sv(WGPUStringView s) {
    if (!s.data) return QString();
    // WGPU_STRLEN sentinel == SIZE_MAX -> nul-terminated.
    const int len = (s.length == WGPU_STRLEN)
                        ? int(std::strlen(s.data))
                        : int(s.length);
    return QString::fromUtf8(s.data, len);
}

static void onWgpuLog(WGPULogLevel level, WGPUStringView message, void* /*userdata*/) {
    const QString m = sv(message);
    switch (level) {
        case WGPULogLevel_Error: qWarning().noquote() << "[wgpu err]"   << m; break;
        case WGPULogLevel_Warn:  qWarning().noquote() << "[wgpu warn]"  << m; break;
        case WGPULogLevel_Info:  qInfo   ().noquote() << "[wgpu info]"  << m; break;
        case WGPULogLevel_Debug: qDebug  ().noquote() << "[wgpu dbg]"   << m; break;
        case WGPULogLevel_Trace: qDebug  ().noquote() << "[wgpu trace]" << m; break;
        default: break;
    }
}

static void onUncapturedError(WGPUDevice const* /*device*/,
                              WGPUErrorType type, WGPUStringView message,
                              void* /*ud1*/, void* /*ud2*/) {
    qWarning().noquote() << "[wgpu device error" << int(type) << "]" << sv(message);
}

// -----------------------------------------------------------------------------
// Construction / destruction
// -----------------------------------------------------------------------------

WgpuViewportWindow::WgpuViewportWindow(QWindow* parent)
    : QWindow(parent) {
    // wgpu doesn't need a GL context; we just need a real native window that
    // the platform window manager has actually created. OpenGLSurface is the
    // most portable way to ask Qt for a hardware-rendering-ready native
    // window — we never bind a GL context on top of it.
    setSurfaceType(QSurface::OpenGLSurface);
}

WgpuViewportWindow::~WgpuViewportWindow() {
    shutdown();
}

void WgpuViewportWindow::setBackgroundColor(const QColor& color) {
    background_color_ = color;
    if (isExposed()) requestUpdate();
}

// -----------------------------------------------------------------------------
// Lifecycle
// -----------------------------------------------------------------------------

void WgpuViewportWindow::exposeEvent(QExposeEvent* /*event*/) {
    if (!isExposed()) return;

    if (!wgpu_initialized_) {
        if (!initWgpu()) {
            qWarning() << "wgpu init failed; viewport will not render";
            return;
        }
        wgpu_initialized_ = true;
    }

    const int w = int(width()  * devicePixelRatio());
    const int h = int(height() * devicePixelRatio());
    if (w > 0 && h > 0 && (w != configured_w_ || h != configured_h_)) {
        configureSurface(w, h);
    }
    requestUpdate();
}

void WgpuViewportWindow::resizeEvent(QResizeEvent* /*event*/) {
    if (!wgpu_initialized_ || !isExposed()) return;
    const int w = int(width()  * devicePixelRatio());
    const int h = int(height() * devicePixelRatio());
    if (w > 0 && h > 0) {
        configureSurface(w, h);
        requestUpdate();
    }
}

bool WgpuViewportWindow::event(QEvent* event) {
    if (event->type() == QEvent::UpdateRequest) {
        if (wgpu_initialized_ && surface_configured_) {
            render();
        }
        return true;
    }
    return QWindow::event(event);
}

// -----------------------------------------------------------------------------
// wgpu init: instance, surface, adapter, device, queue
// -----------------------------------------------------------------------------

bool WgpuViewportWindow::initWgpu() {
    // Optional: log everything wgpu-native says at warn+ so backend init
    // problems surface in the console rather than being swallowed.
    wgpuSetLogCallback(onWgpuLog, nullptr);
    wgpuSetLogLevel(WGPULogLevel_Warn);

    instance_ = wgpuCreateInstance(nullptr);
    if (!instance_) {
        qWarning() << "wgpuCreateInstance returned null";
        return false;
    }

    if (!createSurface()) return false;

    // ---- Async request adapter -------------------------------------------
    struct AdapterReq { WGPUAdapter adapter = nullptr; bool done = false; bool ok = false; };
    AdapterReq areq;

    WGPURequestAdapterOptions adapter_opts = {};
    adapter_opts.compatibleSurface = surface_;
    adapter_opts.powerPreference   = WGPUPowerPreference_HighPerformance;

    WGPURequestAdapterCallbackInfo acb = {};
    acb.mode      = WGPUCallbackMode_AllowProcessEvents;
    acb.callback  = [](WGPURequestAdapterStatus status, WGPUAdapter adapter,
                       WGPUStringView message, void* ud1, void* /*ud2*/) {
        auto* r = static_cast<AdapterReq*>(ud1);
        r->done = true;
        if (status == WGPURequestAdapterStatus_Success) {
            r->adapter = adapter;
            r->ok = true;
        } else {
            qWarning().noquote() << "RequestAdapter failed:" << sv(message);
        }
    };
    acb.userdata1 = &areq;

    wgpuInstanceRequestAdapter(instance_, &adapter_opts, acb);
    while (!areq.done) wgpuInstanceProcessEvents(instance_);
    if (!areq.ok) return false;
    adapter_ = areq.adapter;

    // ---- Async request device --------------------------------------------
    struct DeviceReq { WGPUDevice device = nullptr; bool done = false; bool ok = false; };
    DeviceReq dreq;

    WGPUDeviceDescriptor dev_desc = {};
    // Surface uncaptured errors (validation failures etc.) into qWarning so
    // they're attributable rather than silently swallowed.
    dev_desc.uncapturedErrorCallbackInfo.callback = onUncapturedError;

    WGPURequestDeviceCallbackInfo dcb = {};
    dcb.mode     = WGPUCallbackMode_AllowProcessEvents;
    dcb.callback = [](WGPURequestDeviceStatus status, WGPUDevice device,
                      WGPUStringView message, void* ud1, void* /*ud2*/) {
        auto* r = static_cast<DeviceReq*>(ud1);
        r->done = true;
        if (status == WGPURequestDeviceStatus_Success) {
            r->device = device;
            r->ok = true;
        } else {
            qWarning().noquote() << "RequestDevice failed:" << sv(message);
        }
    };
    dcb.userdata1 = &dreq;

    wgpuAdapterRequestDevice(adapter_, &dev_desc, dcb);
    while (!dreq.done) wgpuInstanceProcessEvents(instance_);
    if (!dreq.ok) return false;
    device_ = dreq.device;
    queue_  = wgpuDeviceGetQueue(device_);

    // ---- Pick a surface format -------------------------------------------
    WGPUSurfaceCapabilities caps = {};
    if (wgpuSurfaceGetCapabilities(surface_, adapter_, &caps) != WGPUStatus_Success
        || caps.formatCount == 0) {
        qWarning() << "wgpuSurfaceGetCapabilities returned no formats";
        return false;
    }
    surface_format_ = caps.formats[0];  // preferred format per wgpu docs
    wgpuSurfaceCapabilitiesFreeMembers(caps);

    qInfo() << "wgpu init OK; surface format =" << int(surface_format_);
    return true;
}

// -----------------------------------------------------------------------------
// Surface creation — platform-specific native handle plumbing.
// -----------------------------------------------------------------------------

#if defined(Q_OS_LINUX)
// QNativeInterface::QX11Application::display() returns Display*; pulling
// Xlib.h is fine on any system that has Qt6Gui built with xcb support
// (which already depends on libX11). We never look inside Display* — we
// only forward the pointer to wgpu as opaque.
#  if __has_include(<X11/Xlib.h>)
#    include <X11/Xlib.h>
#  endif
// QWaylandApplication::display() and ::surface() return wl_display* and
// wl_surface* (wayland-client-core.h). Same story.
#  if __has_include(<wayland-client-core.h>)
#    include <wayland-client-core.h>
#  endif
#endif

bool WgpuViewportWindow::createSurface() {
    WGPUSurfaceDescriptor surface_desc = {};

#if defined(Q_OS_LINUX)
    const QString platform = QGuiApplication::platformName();
    if (platform == "xcb") {
#  if __has_include(<X11/Xlib.h>)
        auto* x11 = qApp->nativeInterface<QNativeInterface::QX11Application>();
        if (!x11 || !x11->display()) {
            qWarning() << "Could not get X11 Display* from Qt";
            return false;
        }
        WGPUSurfaceSourceXlibWindow xlib = {};
        xlib.chain.sType = WGPUSType_SurfaceSourceXlibWindow;
        xlib.display = x11->display();
        xlib.window  = static_cast<uint64_t>(winId());
        surface_desc.nextInChain = &xlib.chain;
        surface_ = wgpuInstanceCreateSurface(instance_, &surface_desc);
#  else
        qWarning() << "Built without Xlib headers; cannot create X11 surface";
        return false;
#  endif
    } else if (platform == "wayland") {
#  if __has_include(<wayland-client-core.h>)
        auto* wl = qApp->nativeInterface<QNativeInterface::QWaylandApplication>();
        if (!wl || !wl->display()) {
            qWarning() << "Could not get Wayland wl_display* from Qt";
            return false;
        }
        // The wl_surface for a window is exposed via the QPA window-handle
        // accessor on the native interface (not the application-wide one).
        // For stage 1 we fail loud; stage-1.5 fills this in.
        qWarning() << "Wayland wgpu surface creation not yet wired (stage 1.5)";
        return false;
#  else
        qWarning() << "Built without Wayland headers; cannot create Wayland surface";
        return false;
#  endif
    } else {
        qWarning().noquote() << "Unsupported Qt platform for wgpu surface:" << platform;
        return false;
    }
#else
    // macOS / Windows native-handle wiring lands when those targets become
    // active. Stage-1 development happens on Linux.
    qWarning() << "wgpu surface creation not yet wired for this platform";
    return false;
#endif

    if (!surface_) {
        qWarning() << "wgpuInstanceCreateSurface returned null";
        return false;
    }
    return true;
}

// -----------------------------------------------------------------------------
// Surface (re)configure + render
// -----------------------------------------------------------------------------

void WgpuViewportWindow::configureSurface(int width_px, int height_px) {
    WGPUSurfaceConfiguration cfg = {};
    cfg.device      = device_;
    cfg.format      = surface_format_;
    cfg.usage       = WGPUTextureUsage_RenderAttachment;
    cfg.width       = uint32_t(width_px);
    cfg.height      = uint32_t(height_px);
    cfg.presentMode = WGPUPresentMode_Fifo;
    cfg.alphaMode   = WGPUCompositeAlphaMode_Auto;

    wgpuSurfaceConfigure(surface_, &cfg);
    configured_w_       = width_px;
    configured_h_       = height_px;
    surface_configured_ = true;
}

void WgpuViewportWindow::render() {
    WGPUSurfaceTexture surf_tex = {};
    wgpuSurfaceGetCurrentTexture(surface_, &surf_tex);

    switch (surf_tex.status) {
        case WGPUSurfaceGetCurrentTextureStatus_SuccessOptimal:
        case WGPUSurfaceGetCurrentTextureStatus_SuccessSuboptimal:
            break;  // proceed
        case WGPUSurfaceGetCurrentTextureStatus_Timeout:
        case WGPUSurfaceGetCurrentTextureStatus_Outdated:
        case WGPUSurfaceGetCurrentTextureStatus_Lost: {
            // Reconfigure and try again next frame.
            const int w = int(width()  * devicePixelRatio());
            const int h = int(height() * devicePixelRatio());
            if (w > 0 && h > 0) configureSurface(w, h);
            requestUpdate();
            return;
        }
        default:
            qWarning() << "GetCurrentTexture status" << int(surf_tex.status);
            return;
    }

    WGPUTextureView view = wgpuTextureCreateView(surf_tex.texture, nullptr);

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    WGPURenderPassColorAttachment color = {};
    color.view       = view;
    color.loadOp     = WGPULoadOp_Clear;
    color.storeOp    = WGPUStoreOp_Store;
    color.clearValue = {
        background_color_.redF(),
        background_color_.greenF(),
        background_color_.blueF(),
        1.0,
    };
    color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount = 1;
    pass_desc.colorAttachments     = &color;

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    WGPUCommandBuffer cmd = wgpuCommandEncoderFinish(enc, nullptr);
    wgpuQueueSubmit(queue_, 1, &cmd);

    wgpuCommandBufferRelease(cmd);
    wgpuCommandEncoderRelease(enc);
    wgpuTextureViewRelease(view);

    wgpuSurfacePresent(surface_);
    wgpuTextureRelease(surf_tex.texture);
}

void WgpuViewportWindow::shutdown() {
    if (queue_)    { wgpuQueueRelease(queue_);       queue_    = nullptr; }
    if (device_)   { wgpuDeviceRelease(device_);     device_   = nullptr; }
    if (adapter_)  { wgpuAdapterRelease(adapter_);   adapter_  = nullptr; }
    if (surface_)  { wgpuSurfaceRelease(surface_);   surface_  = nullptr; }
    if (instance_) { wgpuInstanceRelease(instance_); instance_ = nullptr; }
    wgpu_initialized_   = false;
    surface_configured_ = false;
}
