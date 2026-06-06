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

// Web entry point. Wires a WebViewportHost to a ViewportCore, brings up
// wgpu through emdawnwebgpu (the spec-compatible WebGPU header set that
// shipped with Dawn), then drives a render() per requestAnimationFrame
// tick. No sidecar load yet — that lands with the emscripten_fetch
// streaming backend (#88). For this scaffold we render an empty scene
// with the configured background so init + present is verified
// end-to-end through the same ViewportCore code path the desktop build
// uses.

#include "ViewportCore.h"
#include "WebViewportHost.h"
#include "Log.h"

#include <emscripten/emscripten.h>
#include <emscripten/html5.h>

#include <cstdio>

namespace {

// Shared by the main_loop trampoline + the cleanup path. Allocated on
// the heap so Emscripten's set_main_loop callback (which is C-style)
// can recover state through a void*.
struct AppState {
    WebViewportHost host{ "#viewer-canvas" };
    ViewportCore    core{ &host };
    int             last_w = 0;
    int             last_h = 0;
};

// The main_loop is a free function (Emscripten signature em_callback_func)
// so we can hand it directly to emscripten_set_main_loop_arg.
void main_loop(void* user) {
    auto* app = static_cast<AppState*>(user);

    // Reconfigure when the canvas resizes. The first tick also lands
    // here because last_w / last_h start at 0.
    int w = 0, h = 0;
    app->host.framebufferSize(w, h);
    if (w != app->last_w || h != app->last_h) {
        app->core.configureSurface(w, h);
        app->last_w = w;
        app->last_h = h;
    }

    // Only render when something has requested a frame — saves battery
    // on the still-camera case. The initial frame request is armed by
    // WebViewportHost's ctor so the canvas always paints once at startup.
    if (app->host.consumeFrameRequest()) {
        app->core.render();
    }
}

} // namespace

int main(int /*argc*/, char** /*argv*/) {
    Log::info() << "ifcviewer-web: starting";

    auto* app = new AppState();

    // Web limits floor: requestDevice the WebGPU spec's mandatory floor
    // (maxStorageBufferBindingSize=128MB, maxBufferSize=256MB) so the
    // chunking + pool probe see the same constraints they would hit in
    // any browser. Desktop --web-limits did this opt-in; on web it's
    // the only sensible default.
    if (!app->core.initWgpu(/*web_limits=*/true)) {
        std::fprintf(stderr, "[viewer-web] initWgpu failed\n");
        delete app;
        return 1;
    }
    if (!app->core.buildPipelines()) {
        std::fprintf(stderr, "[viewer-web] buildPipelines failed\n");
        delete app;
        return 1;
    }
    // HiZ + edge + pick pipelines: built up-front to match the desktop
    // path's lifetime. shutdown() in ViewportCore expects each
    // resource to be either constructed or null, so building them all
    // here keeps teardown symmetric.
    app->core.buildHizPipeline();
    app->core.buildEdgePipeline();
    app->core.buildPickPipeline();

    // fps = 0 means "use the browser's natural rate (RAF)" — Emscripten
    // schedules the callback once per requestAnimationFrame tick.
    // simulate_infinite_loop = false because we want main() to return
    // so the runtime + JS event loop keep ticking. The AppState leaks
    // on tab close, which is fine — emscripten_force_exit (called
    // from host_->quit()) is the only formal shutdown path on web.
    emscripten_set_main_loop_arg(main_loop, app, /*fps=*/0,
                                 /*simulate_infinite_loop=*/0);
    return 0;
}
