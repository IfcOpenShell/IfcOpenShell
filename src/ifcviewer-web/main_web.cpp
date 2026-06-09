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
// wgpu via emdawnwebgpu (the spec-compatible WebGPU header set that
// shipped with Dawn), loads the embedded sample sidecar, and drives
// render() per requestAnimationFrame from JS (shell.html).
//
// The RAF loop lives in shell.html — NOT here — because any call into
// Emscripten's main-loop / RAF helpers (or even raw
// requestAnimationFrame via EM_ASM) made from inside Dawn-web's wgpu
// promise-resolution chain stalls the device callback. Having JS drive
// the tick keeps the wasm init path callback-only.

#include "ViewportCore.h"
#include "WebViewportHost.h"
#include "Log.h"

#include <emscripten/emscripten.h>

namespace {

struct AppState {
    WebViewportHost host{ "#viewer-canvas" };
    ViewportCore    core{ &host };
    int             last_w = 0;
    int             last_h = 0;
    // Set true by the init callback once the device + pipelines are up.
    // raf_tick_c skips render() until then; before that point the wgpu
    // state pointers inside core are still null and any draw would crash.
    bool            ready  = false;
};

// One global so the JS-side RAF loop can recover state through a
// pointer round-trip (set into Module._app_ptr from on_complete).
AppState* g_app = nullptr;

} // namespace

// Called from shell.html's RAF tick (via Module._raf_tick_c). Exported
// to JS by EXPORTED_FUNCTIONS in CMakeLists.txt; EMSCRIPTEN_KEEPALIVE
// also keeps the symbol alive under -O*.
extern "C" EMSCRIPTEN_KEEPALIVE void raf_tick_c(void* user) {
    auto* app = static_cast<AppState*>(user);
    if (!app->ready) return;

    int w = 0, h = 0;
    app->host.framebufferSize(w, h);
    if (w != app->last_w || h != app->last_h) {
        app->core.configureSurface(w, h);
        app->last_w = w;
        app->last_h = h;
    }

    if (app->host.consumeFrameRequest()) {
        app->core.render();
    }
}

int main(int /*argc*/, char** /*argv*/) {
    Log::info() << "ifcviewer-web: starting";
    g_app = new AppState();
    g_app->core.initWgpuAsyncWeb([](bool ok) {
        if (!ok) {
            Log::warn() << "ifcviewer-web: wgpu init failed";
            return;
        }
        if (!g_app->core.buildPipelines()) {
            Log::warn() << "ifcviewer-web: buildPipelines failed";
            return;
        }
        // HiZ + edge + pick pipelines: built up-front to match the
        // desktop path. ViewportCore::shutdown expects each resource
        // to be either constructed or null, so building them all here
        // keeps teardown symmetric.
        g_app->core.buildHizPipeline();
        g_app->core.buildEdgePipeline();
        g_app->core.buildPickPipeline();

        // Load the embedded sample sidecar (mounted into MEMFS via
        // --embed-file in CMakeLists.txt). Replaced by an
        // emscripten_fetch + Range backend in #88.
        if (!g_app->core.loadSidecarFromPath("/sample.ifcview")) {
            Log::warn() << "ifcviewer-web: sample sidecar load failed";
        }

        g_app->ready = true;

        // Hand the app pointer to the JS-side RAF loop (set up in
        // shell.html's onRuntimeInitialized). The loop polls for
        // Module._app_ptr before invoking _raf_tick_c.
        EM_ASM({ Module._app_ptr = $0; }, (void*)g_app);
    });
    return 0;
}
