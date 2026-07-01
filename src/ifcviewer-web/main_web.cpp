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
#include <emscripten/html5.h>

#include <cmath>
#include <cstdint>
#include <cstring>

namespace {

// CSS selector for the host <canvas>; must match shell.html + the
// WebViewportHost selector below.
constexpr const char* kCanvasSelector = "#viewer-canvas";

struct AppState {
    WebViewportHost host{ kCanvasSelector };
    ViewportCore    core{ &host };
    int             last_w = 0;
    int             last_h = 0;
    // Set true by the init callback once the device + pipelines are up.
    // raf_tick_c skips render() until then; before that point the wgpu
    // state pointers inside core are still null and any draw would crash.
    bool            ready  = false;

    // ---- Mouse navigation state ----
    // A drag is armed on mousedown and released on mouseup. button is the
    // DOM button code (0 left, 1 middle, 2 right). Left orbits; middle or
    // right pans — matches common web 3D-viewer bindings and covers both
    // three-button mice and trackpad (right-drag) users.
    bool nav_active = false;
    int  nav_button = 0;
    // Accumulated |movement| since mousedown, in CSS px. A left release under
    // the click threshold (no real drag) is treated as a pick instead of an
    // orbit. Captures the down position (canvas-relative CSS px) for the pick.
    float nav_drag_px = 0.0f;
    long  down_x = 0;
    long  down_y = 0;
};

// Click vs drag threshold (CSS px). Below this total travel a left release is
// a pick, above it the gesture was an orbit.
constexpr float kClickDragThresholdPx = 4.0f;

// One global so the JS-side RAF loop can recover state through a
// pointer round-trip (set into Module._app_ptr from on_complete).
AppState* g_app = nullptr;

// Logical (CSS-pixel) height of the canvas. Mouse movementX/Y deltas are
// in CSS pixels, so pan's world-units-per-pixel must use CSS-pixel height
// too (not the DPR-scaled framebuffer height).
int canvasCssHeight() {
    double w = 0.0, h = 0.0;
    emscripten_get_element_css_size(kCanvasSelector, &w, &h);
    return (h > 1.0) ? int(h) : 1;
}

EM_BOOL onMouseDown(int, const EmscriptenMouseEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    if (e->button == 0 || e->button == 1 || e->button == 2) {
        app->nav_active  = true;
        app->nav_button  = e->button;
        app->nav_drag_px = 0.0f;
        app->down_x      = e->targetX;  // canvas-relative CSS px
        app->down_y      = e->targetY;
    }
    return EM_TRUE;
}

EM_BOOL onMouseMove(int, const EmscriptenMouseEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    if (!app->ready || !app->nav_active) return EM_FALSE;

    const float dx = float(e->movementX);
    const float dy = float(e->movementY);
    app->nav_drag_px += std::abs(dx) + std::abs(dy);
    if (app->nav_button == 0) {
        app->core.orbitBy(dx, dy);
    } else {
        app->core.panBy(dx, dy, canvasCssHeight());
    }
    return EM_TRUE;
}

EM_BOOL onMouseUp(int, const EmscriptenMouseEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    const bool was_active = app->nav_active;
    const int  button     = app->nav_button;
    app->nav_active = false;

    // Left release with no real drag → pick the object under the cursor and
    // route it through selection (Shift add, Ctrl remove, plain replace).
    // Async readback: the highlight appears a frame after the result lands.
    if (was_active && button == 0 && app->ready &&
        app->nav_drag_px <= kClickDragThresholdPx) {
        const double dpr = emscripten_get_device_pixel_ratio();
        const int px = int(app->down_x * dpr);
        const int py = int(app->down_y * dpr);
        const bool add    = e->shiftKey;
        const bool remove = e->ctrlKey;
        app->core.pickObjectAtAsync(px, py, [app, add, remove](std::uint32_t id) {
            app->core.applyPickToSelection(id, add, remove);
            // Demo the v15 on-demand deferred fetch: log the picked object's
            // IFC GUID (first pick fetches the property block off the network).
            if (id != 0) app->core.logSelectedObjectGuidWeb(id);
            app->host.requestFrame();
        });
    }
    return EM_TRUE;
}

EM_BOOL onWheel(int, const EmscriptenWheelEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    if (!app->ready) return EM_FALSE;

    // Normalise to "notches" like the desktop wheel (one notch ≈ 120
    // angle-units ≈ 100 px of deltaY). Line/page modes are scaled to a
    // comparable pixel magnitude. Negate so wheel-up (deltaY < 0) zooms in.
    double dy = e->deltaY;
    if (e->deltaMode == DOM_DELTA_LINE)      dy *= 16.0;
    else if (e->deltaMode == DOM_DELTA_PAGE) dy *= 800.0;
    app->core.dollyBy(-float(dy) / 100.0f);
    return EM_TRUE;  // consume so the page doesn't scroll
}

// Viewport nav hotkeys, matching the desktop bindings (ViewportWindow):
//   Home     view all        F   zoom to selected     P   ortho/persp toggle
//   X/Y/Z    front/right/top   Shift+X/Y/Z   back/left/bottom
// `.code` is layout-independent (physical key), so this works on any keymap.
EM_BOOL onKeyDown(int, const EmscriptenKeyboardEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    if (!app->ready || e->repeat) return EM_FALSE;
    const char* code = e->code;
    const bool  shift = e->shiftKey;
    using SV = ViewportCore::StandardView;
    if      (!std::strcmp(code, "Home"))            app->core.viewAll();
    else if (!std::strcmp(code, "KeyF") && !shift)  app->core.frameSelection();
    else if (!std::strcmp(code, "KeyP") && !shift)  app->core.toggleProjection();
    else if (!std::strcmp(code, "KeyX")) app->core.setStandardView(shift ? SV::Back   : SV::Front);
    else if (!std::strcmp(code, "KeyY")) app->core.setStandardView(shift ? SV::Left   : SV::Right);
    else if (!std::strcmp(code, "KeyZ")) app->core.setStandardView(shift ? SV::Bottom : SV::Top);
    else return EM_FALSE;  // let every other key through to the browser
    app->host.requestFrame();
    return EM_TRUE;
}

// Register pointer + wheel handlers once the app is live. mousedown binds
// to the canvas; mousemove/up bind to the window so a drag keeps tracking
// when the pointer leaves the canvas. A JS-side contextmenu suppressor
// lets right-drag pan without popping the browser menu.
void installInputHandlers(AppState* app) {
    emscripten_set_mousedown_callback(kCanvasSelector, app, EM_FALSE, onMouseDown);
    emscripten_set_mousemove_callback(EMSCRIPTEN_EVENT_TARGET_WINDOW, app, EM_FALSE, onMouseMove);
    emscripten_set_mouseup_callback(EMSCRIPTEN_EVENT_TARGET_WINDOW, app, EM_FALSE, onMouseUp);
    emscripten_set_wheel_callback(kCanvasSelector, app, EM_FALSE, onWheel);
    emscripten_set_keydown_callback(EMSCRIPTEN_EVENT_TARGET_WINDOW, app, EM_FALSE, onKeyDown);
    EM_ASM({
        var c = document.querySelector(UTF8ToString($0));
        if (c) c.addEventListener('contextmenu', function(ev) { ev.preventDefault(); });
    }, kCanvasSelector);
}

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

// Stream a sidecar from a registered JS byte-source and APPEND it to the scene
// (federation). shell.html registers the source first — a picked File or a
// remote URL, sized up front — into Module.__ifcvSources[source_id], then calls
// this. Byte-range: the file is never copied whole into the wasm heap; metadata
// is read via ranges and chunks stream per-chunk, so a 500 MB sidecar stays in
// the File / on the server. Asynchronous; the model frames itself from the JS
// completion callback. Call clear_scene_c first to replace instead of append.
extern "C" EMSCRIPTEN_KEEPALIVE void load_sidecar_from_source_c(int source_id) {
    if (!g_app || !g_app->ready) return;
    g_app->core.loadSidecarMetadataWeb(source_id, "source");
}

// Drop all loaded models (used by shell.html to replace the embedded sample /
// a prior federation before loading a fresh set).
extern "C" EMSCRIPTEN_KEEPALIVE void clear_scene_c() {
    if (!g_app || !g_app->ready) return;
    g_app->core.resetScene();
}

// Viewport-navigation entry points for the shell.html toolbar (buttons that
// mirror the keyboard hotkeys). Each schedules a frame.
extern "C" EMSCRIPTEN_KEEPALIVE void view_all_c() {
    if (!g_app || !g_app->ready) return;
    g_app->core.viewAll();               g_app->host.requestFrame();
}
extern "C" EMSCRIPTEN_KEEPALIVE void frame_selection_c() {
    if (!g_app || !g_app->ready) return;
    g_app->core.frameSelection();        g_app->host.requestFrame();
}
extern "C" EMSCRIPTEN_KEEPALIVE void toggle_projection_c() {
    if (!g_app || !g_app->ready) return;
    g_app->core.toggleProjection();      g_app->host.requestFrame();
}
extern "C" EMSCRIPTEN_KEEPALIVE int projection_is_ortho_c() {
    return (g_app && g_app->ready && g_app->core.projectionOrtho()) ? 1 : 0;
}
// id: 0 Front, 1 Back, 2 Left, 3 Right, 4 Top, 5 Bottom.
extern "C" EMSCRIPTEN_KEEPALIVE void standard_view_c(int id) {
    if (!g_app || !g_app->ready || id < 0 || id > 5) return;
    using SV = ViewportCore::StandardView;
    static const SV map[6] = { SV::Front, SV::Back, SV::Left, SV::Right, SV::Top, SV::Bottom };
    g_app->core.setStandardView(map[id]);
    g_app->host.requestFrame();
}

// Streaming progress for the loading bar (shell.html polls these each frame).
// total == 0 while still fetching metadata; resident climbs to total as
// geometry chunks arrive.
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_chunks_resident_c() {
    if (!g_app) return 0;
    int r = 0, t = 0; g_app->core.streamingProgress(r, t); return r;
}
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_chunks_total_c() {
    if (!g_app) return 0;
    int r = 0, t = 0; g_app->core.streamingProgress(r, t); return t;
}

// Per-model progress for the federation loading panel: how many models are in
// the scene, and the idx-th model's resident/total chunks (idx ordered by load).
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_model_count_c() {
    return g_app ? g_app->core.streamingModelCount() : 0;
}
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_model_resident_c(int idx) {
    if (!g_app) return 0;
    int r = 0, t = 0; g_app->core.streamingModelProgress(idx, r, t); return r;
}
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_model_total_c(int idx) {
    if (!g_app) return 0;
    int r = 0, t = 0; g_app->core.streamingModelProgress(idx, r, t); return t;
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
        // --embed-file in CMakeLists.txt). The sample stays on the
        // synchronous MEMFS read; user-picked files go through the
        // Blob.slice byte-range path (load_sidecar_from_blob_c) so large
        // sidecars never enter the wasm heap.
        if (!g_app->core.loadSidecarFromPath("/sample.ifcview")) {
            Log::warn() << "ifcviewer-web: sample sidecar load failed";
        }

        g_app->ready = true;

        // Now that the camera + render path are live, start listening for
        // orbit/pan/zoom input. (Pick is still deferred — it needs the
        // async buffer-readback rewrite before it's safe on web.)
        installInputHandlers(g_app);

        // Hand the app pointer to the JS-side RAF loop (set up in
        // shell.html's onRuntimeInitialized). The loop polls for
        // Module._app_ptr before invoking _raf_tick_c.
        EM_ASM({ Module._app_ptr = $0; }, (void*)g_app);
    });
    return 0;
}
