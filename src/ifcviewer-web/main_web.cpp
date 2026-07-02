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

    // ---- Fly (first-person) mode ----
    // Shift+F enters (pointer-locks the canvas), Esc exits. While flying, held
    // W/A/S/D/Q/E + Shift are integrated each frame via ViewportCore::flyMove,
    // and pointer-lock mouse deltas drive flyLook. dt from fly_last_ms.
    bool   fly_mode = false;
    // True once the browser actually granted pointer lock for this fly session.
    // Distinguishes "lock lost" (Esc/click-out → exit fly) from "lock denied on
    // entry" (headless / permission) where fly stays keyboard-drivable.
    bool   fly_locked = false;
    bool   k_w = false, k_a = false, k_s = false, k_d = false, k_q = false, k_e = false, k_shift = false;
    double fly_last_ms = 0.0;
};

// Click vs drag threshold (CSS px). Below this total travel a left release is
// a pick, above it the gesture was an orbit.
constexpr float kClickDragThresholdPx = 4.0f;

// One global so the JS-side RAF loop can recover state through a
// pointer round-trip (set into Module._app_ptr from on_complete).
AppState* g_app = nullptr;

// Defined below (with the fly helpers); onMouseDown needs it to exit fly on click.
void setFlyMode(AppState* app, bool on);

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
    // In fly mode a click exits (matches the desktop app).
    if (app->fly_mode) { setFlyMode(app, false); return EM_TRUE; }
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
    if (!app->ready) return EM_FALSE;
    // Fly mode: pointer-locked mouse deltas turn the camera in place.
    if (app->fly_mode) {
        app->core.flyLook(float(e->movementX), float(e->movementY));
        return EM_TRUE;
    }
    if (!app->nav_active) return EM_FALSE;

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
    // In fly mode the wheel tunes move speed (Blender convention), not zoom.
    if (app->fly_mode) { app->core.flyAdjustSpeed(-float(dy) / 100.0f); return EM_TRUE; }
    app->core.dollyBy(-float(dy) / 100.0f);
    return EM_TRUE;  // consume so the page doesn't scroll
}

// Track a held fly movement key (W/A/S/D/Q/E/Shift). Returns true if `code` was
// one. Physical `.code` so it's keymap-independent.
bool setFlyKey(AppState* app, const char* code, bool down) {
    if      (!std::strcmp(code, "KeyW")) app->k_w = down;
    else if (!std::strcmp(code, "KeyA")) app->k_a = down;
    else if (!std::strcmp(code, "KeyS")) app->k_s = down;
    else if (!std::strcmp(code, "KeyD")) app->k_d = down;
    else if (!std::strcmp(code, "KeyQ")) app->k_q = down;
    else if (!std::strcmp(code, "KeyE")) app->k_e = down;
    else if (!std::strcmp(code, "ShiftLeft") || !std::strcmp(code, "ShiftRight"))
        app->k_shift = down;
    else return false;
    return true;
}

// Enter/leave fly mode: pointer-lock the canvas for mouse-look on enter, release
// on exit. Shared camera math is ViewportCore::flyMove/flyLook.
void setFlyMode(AppState* app, bool on) {
    if (app->fly_mode == on) return;
    app->fly_mode = on;
    if (on) {
        app->fly_last_ms = emscripten_get_now();
        emscripten_request_pointerlock(kCanvasSelector, EM_TRUE);
        Log::info() << "[fly] on — WASD/QE move, mouse looks, Shift boosts, wheel = speed, Esc exits";
    } else {
        app->k_w = app->k_a = app->k_s = app->k_d = app->k_q = app->k_e = app->k_shift = false;
        app->fly_locked = false;
        emscripten_exit_pointerlock();
        Log::info() << "[fly] off";
    }
    app->host.requestFrame();
}

// Viewport hotkeys, matching the desktop bindings (ViewportWindow):
//   Home view all · F zoom to selected · P ortho/persp · X/Y/Z (+Shift) views
//   Shift+F enter fly · Esc exit fly · while flying: W/A/S/D/Q/E held + Shift.
EM_BOOL onKeyDown(int, const EmscriptenKeyboardEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    if (!app->ready) return EM_FALSE;
    const char* code = e->code;
    const bool  shift = e->shiftKey;
    // Shift+F toggles fly; Esc leaves it.
    if (!std::strcmp(code, "KeyF") && shift && !e->repeat) { setFlyMode(app, !app->fly_mode); return EM_TRUE; }
    if (!std::strcmp(code, "Escape") && app->fly_mode)     { setFlyMode(app, false);          return EM_TRUE; }
    // While flying, WASDQE/Shift are held-movement keys, not hotkeys.
    if (app->fly_mode) { if (setFlyKey(app, code, true)) return EM_TRUE; return EM_FALSE; }
    if (e->repeat) return EM_FALSE;
    const bool alt = e->altKey;
    // Visibility + X-ray, matching desktop: H hide selected · Shift+H isolate ·
    // Alt+H show all · Alt+X x-ray.
    if (!std::strcmp(code, "KeyH")) {
        if      (alt)   app->core.showAll();
        else if (shift) app->core.isolateSelected();
        else            app->core.hideSelected();
        return EM_TRUE;
    }
    if (!std::strcmp(code, "KeyX") && alt) { app->core.toggleXray(); return EM_TRUE; }
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

EM_BOOL onKeyUp(int, const EmscriptenKeyboardEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    return setFlyKey(app, e->code, false) ? EM_TRUE : EM_FALSE;
}

// Pointer-lock is the fly-look mechanism. When it's LOST (the browser eats the
// first Esc to release it, or the user clicks out) leave fly mode — this is what
// makes a single Esc exit cleanly. `fly_locked` guards against a denied lock on
// entry (headless / permission) firing this and insta-exiting: we only treat a
// loss as an exit if we'd actually acquired the lock.
EM_BOOL onPointerLockChange(int, const EmscriptenPointerlockChangeEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    if (e->isActive) {
        app->fly_locked = true;
    } else if (app->fly_locked && app->fly_mode) {
        setFlyMode(app, false);
    }
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
    emscripten_set_keyup_callback(EMSCRIPTEN_EVENT_TARGET_WINDOW, app, EM_FALSE, onKeyUp);
    emscripten_set_pointerlockchange_callback(EMSCRIPTEN_EVENT_TARGET_DOCUMENT, app, EM_FALSE,
                                              onPointerLockChange);
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

    // Fly mode: integrate held-key movement each frame (dt from wall clock).
    // flyMove schedules a frame when it actually moves, so a still fly camera
    // costs nothing.
    if (app->fly_mode) {
        const double now = emscripten_get_now();
        const float dt = float((now - app->fly_last_ms) / 1000.0);
        app->fly_last_ms = now;
        app->core.flyMove(app->k_w, app->k_s, app->k_d, app->k_a,
                          app->k_e, app->k_q, app->k_shift, dt);
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
// Toggle fly (first-person) mode from the toolbar. The button click is a user
// gesture, so the pointer-lock request inside succeeds.
extern "C" EMSCRIPTEN_KEEPALIVE void toggle_fly_c() {
    if (g_app && g_app->ready) setFlyMode(g_app, !g_app->fly_mode);
}
extern "C" EMSCRIPTEN_KEEPALIVE int fly_is_active_c() {
    return (g_app && g_app->ready && g_app->fly_mode) ? 1 : 0;
}

// Visibility + X-ray, for the toolbar (same ops as the H/Shift+H/Alt+H/Alt+X keys).
extern "C" EMSCRIPTEN_KEEPALIVE void hide_selected_c()    { if (g_app && g_app->ready) g_app->core.hideSelected(); }
extern "C" EMSCRIPTEN_KEEPALIVE void isolate_selected_c() { if (g_app && g_app->ready) g_app->core.isolateSelected(); }
extern "C" EMSCRIPTEN_KEEPALIVE void show_all_c()         { if (g_app && g_app->ready) g_app->core.showAll(); }
extern "C" EMSCRIPTEN_KEEPALIVE void toggle_xray_c()      { if (g_app && g_app->ready) g_app->core.toggleXray(); }
extern "C" EMSCRIPTEN_KEEPALIVE int  xray_is_active_c()   { return (g_app && g_app->ready && g_app->core.xrayActive()) ? 1 : 0; }

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

// Combined byte progress for the loading bar: total geometry, bytes the current
// view needs (contribution-culled), and how much of that is loaded. Doubles so
// JS gets exact byte counts well past 2 GB.
extern "C" EMSCRIPTEN_KEEPALIVE double ifcv_bytes_total_c() {
    if (!g_app) return 0.0;
    std::uint64_t tot = 0, need = 0, load = 0;
    g_app->core.streamingByteProgress(tot, need, load); return double(tot);
}
extern "C" EMSCRIPTEN_KEEPALIVE double ifcv_bytes_needed_c() {
    if (!g_app) return 0.0;
    std::uint64_t tot = 0, need = 0, load = 0;
    g_app->core.streamingByteProgress(tot, need, load); return double(need);
}
extern "C" EMSCRIPTEN_KEEPALIVE double ifcv_bytes_loaded_c() {
    if (!g_app) return 0.0;
    std::uint64_t tot = 0, need = 0, load = 0;
    g_app->core.streamingByteProgress(tot, need, load); return double(load);
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
