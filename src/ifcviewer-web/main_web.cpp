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
// render() per requestAnimationFrame from JS (the host page (web/ifcviewer.js)).
//
// The RAF loop lives in the host page (web/ifcviewer.js) — NOT here — because any call into
// Emscripten's main-loop / RAF helpers (or even raw
// requestAnimationFrame via EM_ASM) made from inside Dawn-web's wgpu
// promise-resolution chain stalls the device callback. Having JS drive
// the tick keeps the wasm init path callback-only.

#include "ViewportCore.h"
#include "WebViewportHost.h"
#include "WebFederation.h"
#include "Log.h"

#include <emscripten/emscripten.h>
#include <emscripten/html5.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <unordered_set>
#include <vector>

namespace {

// CSS selector for the host <canvas>; must match the host page (web/ifcviewer.js) + the
// WebViewportHost selector below.
constexpr const char* kCanvasSelector = "#viewer-canvas";

// What a mouse drag drives, decided against the active nav preset's bindings.
enum class NavKind { None, Orbit, Pan, Select };

struct AppState {
    WebViewportHost host{ kCanvasSelector };
    ViewportCore    core{ &host };
    // Federation concepts (unit, false origin, per-model transforms) that the
    // host page drives via the ifcv_federation_* exports below.
    WebFederation   federation{ core };
    int             last_w = 0;
    int             last_h = 0;
    // Set true by the init callback once the device + pipelines are up.
    // raf_tick_c skips render() until then; before that point the wgpu
    // state pointers inside core are still null and any draw would crash.
    bool            ready  = false;

    // ---- Mouse navigation state ----
    // A drag is armed on mousedown and released on mouseup. What the press
    // drives (orbit / pan / select) is decided against the active nav preset's
    // bindings (ViewportCore::navBindings), so any preset works on web too.
    bool    nav_active = false;
    NavKind nav_kind   = NavKind::None;
    // Section-cut tool: while active, a select-button click drops a clip plane
    // at the picked surface (K toggles, Shift+K clears — matches desktop).
    bool    section_tool_active = false;
    // True while dragging a section-plane gizmo (LMB down on the arrow → slide).
    bool    section_dragging    = false;
    // Accumulated |movement| since mousedown, in CSS px. A select-button release
    // under the click threshold (no real drag) is treated as a pick; a drag will
    // become a marquee. Captures the down position (canvas-relative CSS px).
    float nav_drag_px = 0.0f;
    long  down_x = 0;
    long  down_y = 0;
    // The canvas's top-left in window coords, captured on mousedown. The
    // mousemove/mouseup handlers are window-targeted (so a drag can leave the
    // canvas), so their coords are window-relative; subtracting this maps them
    // back to canvas-relative — the space down_x/down_y and the picker use.
    // Zero for a fullscreen canvas pinned at (0,0); nonzero when embedded.
    double canvas_origin_x = 0.0;
    double canvas_origin_y = 0.0;

    // ---- Fly (first-person) mode ----
    // Shift+F enters (pointer-locks the canvas), Esc exits. While flying, held
    // W/A/S/D/Q/E + Shift are integrated each frame via ViewportCore::flyMove,
    // and pointer-lock mouse deltas drive flyLook. dt from fly_last_ms.
    bool   fly_mode = false;
    // True once the browser actually granted pointer lock for this fly session.
    // Distinguishes "lock lost" (Esc/click-out → exit fly) from "lock denied on
    // entry" (headless / permission) where fly stays keyboard-drivable.
    bool   fly_locked = false;
    bool   key_w_pressed = false;
    bool   key_a_pressed = false;
    bool   key_s_pressed = false;
    bool   key_d_pressed = false;
    bool   key_q_pressed = false;
    bool   key_e_pressed = false;
    bool   key_shift_pressed = false;
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

// Marquee rectangle overlay. The rubber-band is a plain DOM <div> (the host page (web/ifcviewer.js))
// positioned in CSS px — the canvas fills the viewport, so canvas-relative
// coords are viewport coords. Cheaper + pixel-perfect vs a GPU overlay pass
// (which the web lib doesn't have anyway).
void showMarquee(int x, int y, int w, int h) {
    EM_ASM({
        var m = document.getElementById('marquee');
        if (m) {
            m.style.display = 'block';
            m.style.left = $0 + 'px'; m.style.top    = $1 + 'px';
            m.style.width = $2 + 'px'; m.style.height = $3 + 'px';
        }
    }, x, y, w, h);
}
void hideMarquee() {
    EM_ASM({ var m = document.getElementById('marquee'); if (m) m.style.display = 'none'; });
}

// The canvas's top-left in window (client) coords. Window-targeted mouse events
// are window-relative; subtract this to convert them to canvas-relative.
void canvasClientOrigin(double& left, double& top) {
    left = EM_ASM_DOUBLE({
        var c = document.getElementById('viewer-canvas');
        return c ? c.getBoundingClientRect().left : 0;
    });
    top = EM_ASM_DOUBLE({
        var c = document.getElementById('viewer-canvas');
        return c ? c.getBoundingClientRect().top : 0;
    });
}

// Tell the page the selection changed; it pulls the new id set back through
// ifcv_get_selection_c. Every wasm-side mutation (single pick, marquee, hide-
// selected) fires this, so a host UI tracking multi-selection never has to poll.
// The JS API layer (web/ifcviewer.js) also fires it after its own programmatic
// mutations, so listeners see one event stream regardless of the source.
void notifySelectionChanged() {
    EM_ASM({ if (Module.__ifcvOnSelectionChange) Module.__ifcvOnSelectionChange(); });
}

// The (pointer, count) id array the JS side marshals into the wasm heap. A null
// pointer with a zero count is a legitimate empty list — "clear the selection"
// arrives that way — so it must not be turned into pointer arithmetic on null.
std::vector<std::uint32_t> idsFrom(const std::uint32_t* ids, int n) {
    if (!ids || n <= 0) return {};
    return std::vector<std::uint32_t>(ids, ids + n);
}

// The reading half of the same convention: write `ids` ascending into `out`
// (at most `max` of them) and return the TOTAL, so a caller that passed a
// too-small buffer — or none at all — knows what to allocate and can ask again.
int fillIdsAscending(const std::unordered_set<std::uint32_t>& ids,
                     std::uint32_t* out, int max) {
    std::vector<std::uint32_t> sorted(ids.begin(), ids.end());
    std::sort(sorted.begin(), sorted.end());
    const int n = std::min(int(sorted.size()), std::max(0, max));
    if (out && n > 0) std::copy_n(sorted.begin(), n, out);
    return int(sorted.size());
}

// Quote `s` as a JSON string literal. IFC names come straight from the model
// and can hold quotes, backslashes and control characters; UTF-8 continuation
// bytes are already legal JSON and pass through untouched.
std::string jsonString(const std::string& s) {
    std::string out = "\"";
    for (unsigned char c : s) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\b': out += "\\b";  break;
            case '\f': out += "\\f";  break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:
                if (c < 0x20) {
                    char esc[7];
                    std::snprintf(esc, sizeof(esc), "\\u%04x", c);
                    out += esc;
                } else {
                    out += char(c);
                }
        }
    }
    return out + '"';
}

NavKind classifyPress(const ViewportCore::NavBindings& b, int em_button,
                      bool shift, bool ctrl, bool alt) {
    using MB = ViewportCore::MouseBtn; using M = ViewportCore::NavMod;
    const MB btn = (em_button == 0) ? MB::Left : (em_button == 1) ? MB::Middle : MB::Right;
    const M  mod = shift ? M::Shift : ctrl ? M::Ctrl : alt ? M::Alt : M::Plain;
    if (btn == b.orbit && mod == b.orbit_mod) return NavKind::Orbit;
    if (btn == b.pan   && mod == b.pan_mod)   return NavKind::Pan;
    if (btn == b.select)                      return NavKind::Select;  // Shift/Ctrl = add/remove
    return NavKind::None;
}

EM_BOOL onMouseDown(int, const EmscriptenMouseEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    // In fly mode a click exits (matches the desktop app).
    if (app->fly_mode) { setFlyMode(app, false); return EM_TRUE; }
    // Snapshot the canvas origin for this gesture so the window-targeted
    // move/up handlers can map their coords back into canvas space.
    canvasClientOrigin(app->canvas_origin_x, app->canvas_origin_y);
    // Section tool: LMB on a plane's gizmo arrow grabs it to slide (logical px).
    if (app->section_tool_active && e->button == 0) {
        const int hit = app->core.hitTestSectionGizmo(int(e->targetX), int(e->targetY));
        if (hit >= 0 && app->core.beginSectionDrag(hit, int(e->targetX), int(e->targetY))) {
            app->section_dragging = true;
            return EM_TRUE;  // claim the press — don't orbit
        }
    }
    const NavKind kind = classifyPress(app->core.navBindings(), e->button,
                                       e->shiftKey, e->ctrlKey, e->altKey);
    if (kind != NavKind::None) {
        app->nav_active  = true;
        app->nav_kind    = kind;
        app->nav_drag_px = 0.0f;
        app->down_x      = e->targetX;  // canvas-relative CSS px
        app->down_y      = e->targetY;
        // Show the pivot triad for the duration of an orbit / pan drag, so
        // it's visible what the camera turns around (matches the desktop).
        if (kind == NavKind::Orbit || kind == NavKind::Pan)
            app->core.setPivotIndicatorVisible(true);
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
    // Section gizmo drag: slide the grabbed plane along its normal (logical px).
    if (app->section_dragging) {
        app->core.updateSectionDrag(int(e->targetX - app->canvas_origin_x),
                                    int(e->targetY - app->canvas_origin_y));
        return EM_TRUE;
    }
    if (!app->nav_active) return EM_FALSE;

    const float dx = float(e->movementX);
    const float dy = float(e->movementY);
    app->nav_drag_px += std::abs(dx) + std::abs(dy);
    if (app->nav_kind == NavKind::Orbit)     app->core.orbitBy(dx, dy);
    else if (app->nav_kind == NavKind::Pan)  app->core.panBy(dx, dy, canvasCssHeight());
    else if (app->nav_kind == NavKind::Select && app->nav_drag_px > kClickDragThresholdPx) {
        // Select-button drag → draw the marquee rubber-band (canvas-relative CSS px).
        const long mx = long(e->targetX - app->canvas_origin_x);
        const long my = long(e->targetY - app->canvas_origin_y);
        const long x0 = std::min<long>(app->down_x, mx);
        const long y0 = std::min<long>(app->down_y, my);
        showMarquee(int(x0), int(y0),
                    int(std::labs(mx - app->down_x)),
                    int(std::labs(my - app->down_y)));
    }
    return EM_TRUE;
}

EM_BOOL onMouseUp(int, const EmscriptenMouseEvent* e, void* user) {
    auto* app = static_cast<AppState*>(user);
    const bool    was_active = app->nav_active;
    const NavKind kind       = app->nav_kind;
    app->nav_active = false;
    app->nav_kind   = NavKind::None;
    // Drag is over — hide the pivot indicator without afterglow. Only for the
    // gesture that raised it; a stray mouseup must not cut a wheel afterglow.
    if (was_active && (kind == NavKind::Orbit || kind == NavKind::Pan))
        app->core.setPivotIndicatorVisible(false);

    // End a section-gizmo drag (took over the press; no pick/orbit on release).
    if (app->section_dragging) {
        app->core.endSectionDrag();
        app->section_dragging = false;
        return EM_TRUE;
    }

    if (!was_active || !app->ready) return EM_TRUE;
    const double dpr     = emscripten_get_device_pixel_ratio();
    const bool   no_drag = app->nav_drag_px <= kClickDragThresholdPx;

    // Section tool claims a LEFT-button click ("click a surface to cut"); LMB
    // drag still orbits. Takes priority over nav while the tool is active.
    if (app->section_tool_active && e->button == 0 && no_drag) {
        const int px = int(app->down_x * dpr), py = int(app->down_y * dpr);
        app->core.pickSurfaceAtAsync(px, py, [app](ViewportCore::SurfaceHit hit) {
            if (hit.found)  // pad past the AABB so the cut reads as a cap
                app->core.addSectionPlaneAtSurface(hit.world_pos, hit.world_normal,
                                                   hit.aabb_radius * 1.5f);
            app->host.requestFrame();
        });
        return EM_TRUE;
    }

    if (kind == NavKind::Select) {
        const bool add = e->shiftKey, remove = e->ctrlKey;
        if (!no_drag) {
            // Marquee drag → box-pick the rect (device px) and apply to selection.
            hideMarquee();
            const long mx = long(e->targetX - app->canvas_origin_x);
            const long my = long(e->targetY - app->canvas_origin_y);
            const long x0 = std::min<long>(app->down_x, mx);
            const long y0 = std::min<long>(app->down_y, my);
            const int  rx = int(x0 * dpr), ry = int(y0 * dpr);
            const int  rw = int(std::labs(mx - app->down_x) * dpr);
            const int  rh = int(std::labs(my - app->down_y) * dpr);
            app->core.picksInRectAsync(rx, ry, rw, rh,
                [app, add, remove](std::vector<std::uint32_t> ids) {
                    app->core.applyMarqueeToSelection(ids, add, remove);
                    notifySelectionChanged();
                    app->host.requestFrame();
                });
        } else {
            // Single pick under the cursor (Shift add, Ctrl remove, plain replace).
            const int px = int(app->down_x * dpr), py = int(app->down_y * dpr);
            app->core.pickObjectAtAsync(px, py, [app, add, remove](std::uint32_t id) {
                app->core.applyPickToSelection(id, add, remove);
                notifySelectionChanged();
                // Surface the pick to JS: resolve + emit the GUID for a real hit;
                // emit an empty selection when a plain click deselects (id 0).
                if (id != 0) {
                    app->core.logSelectedObjectGuidWeb(id);
                } else if (!add && !remove) {
                    EM_ASM({ if (Module.__ifcvOnSelect) Module.__ifcvOnSelect(0, '', -1, -1); });
                }
                app->host.requestFrame();
            });
        }
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
    // Pivot afterglow on wheel — visible for 600 ms so the user can see what
    // they're zooming around without holding a drag.
    app->core.setPivotIndicatorVisible(true, 600);
    return EM_TRUE;  // consume so the page doesn't scroll
}

// Track a held fly movement key (W/A/S/D/Q/E/Shift). Returns true if `code` was
// one. Physical `.code` so it's keymap-independent.
bool setFlyKey(AppState* app, const char* code, bool down) {
    if      (!std::strcmp(code, "KeyW")) app->key_w_pressed = down;
    else if (!std::strcmp(code, "KeyA")) app->key_a_pressed = down;
    else if (!std::strcmp(code, "KeyS")) app->key_s_pressed = down;
    else if (!std::strcmp(code, "KeyD")) app->key_d_pressed = down;
    else if (!std::strcmp(code, "KeyQ")) app->key_q_pressed = down;
    else if (!std::strcmp(code, "KeyE")) app->key_e_pressed = down;
    else if (!std::strcmp(code, "ShiftLeft") || !std::strcmp(code, "ShiftRight"))
        app->key_shift_pressed = down;
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
        app->key_w_pressed = app->key_a_pressed = app->key_s_pressed = false;
        app->key_d_pressed = app->key_q_pressed = app->key_e_pressed = false;
        app->key_shift_pressed = false;
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
    // Section tool: K toggles drop-a-plane mode, Shift+K clears all cuts.
    if (!std::strcmp(code, "KeyK")) {
        if (shift) app->core.clearSectionPlanes();
        else {
            app->section_tool_active = !app->section_tool_active;
            Log::info() << "[section] tool "
                        << (app->section_tool_active ? "active — click a surface" : "off");
        }
        app->host.requestFrame();
        return EM_TRUE;
    }
    // Del/Backspace removes the most recent cut while the tool is active.
    if (app->section_tool_active &&
        (!std::strcmp(code, "Delete") || !std::strcmp(code, "Backspace"))) {
        const int n = app->core.sectionPlaneCount();
        if (n > 0) app->core.removeSectionPlane(n - 1);
        app->host.requestFrame();
        return EM_TRUE;
    }
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

// Called from the host page (web/ifcviewer.js)'s RAF tick (via Module._raf_tick_c). Exported
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
        app->core.flyMove(app->key_w_pressed, app->key_s_pressed,
                          app->key_d_pressed, app->key_a_pressed,
                          app->key_e_pressed, app->key_q_pressed,
                          app->key_shift_pressed, dt);
    }

    if (app->host.consumeFrameRequest()) {
        app->core.render();
    }
}

// Stream a sidecar from a registered JS byte-source and APPEND it to the scene
// (federation). the host page (web/ifcviewer.js) registers the source first — a picked File or a
// remote URL, sized up front — into Module.__ifcvSources[source_id], then calls
// this. Byte-range: the file is never copied whole into the wasm heap; metadata
// is read via ranges and chunks stream per-chunk, so a 500 MB sidecar stays in
// the File / on the server. Asynchronous; the model frames itself from the JS
// completion callback. Call clear_scene_c first to replace instead of append.
extern "C" EMSCRIPTEN_KEEPALIVE void load_sidecar_from_source_c(int source_id) {
    if (!g_app || !g_app->ready) return;
    // Label the model with whatever name the host page set for this source, so
    // logs identify it rather than saying "source" five times over.
    std::string label = g_app->federation.modelName(source_id);
    if (label.empty()) label = "source " + std::to_string(source_id);

    g_app->core.loadSidecarMetadataWeb(source_id, std::move(label),
        [source_id](std::uint32_t session_model_id) {
            if (!g_app) return;
            // Binds source -> session model, applies any transform staged
            // before the load finished, and guesses the false origin off the
            // first model. Only then tell JS, so a handler that reacts sees a
            // fully placed model.
            g_app->federation.onModelLoaded(source_id, session_model_id);
            EM_ASM({
                if (Module.__ifcvOnModelLoaded) Module.__ifcvOnModelLoaded($0, $1);
            }, source_id, int(session_model_id));
        });
}

// Drop all loaded models (used by the host page (web/ifcviewer.js) to replace the embedded sample /
// a prior federation before loading a fresh set).
extern "C" EMSCRIPTEN_KEEPALIVE void clear_scene_c() {
    if (!g_app || !g_app->ready) return;
    g_app->core.resetScene();
    // Source ids are re-minted from zero by the host page's next registration
    // pass, so stale per-source transforms would land on the wrong models.
    g_app->federation.clear();
}

// Viewport-navigation entry points for the the host page (web/ifcviewer.js) toolbar (buttons that
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
extern "C" EMSCRIPTEN_KEEPALIVE void hide_selected_c() {
    if (!g_app || !g_app->ready) return;
    g_app->core.hideSelected();   // hiding deselects
    notifySelectionChanged();
}
extern "C" EMSCRIPTEN_KEEPALIVE void isolate_selected_c() { if (g_app && g_app->ready) g_app->core.isolateSelected(); }
extern "C" EMSCRIPTEN_KEEPALIVE void show_all_c()         { if (g_app && g_app->ready) g_app->core.showAll(); }
extern "C" EMSCRIPTEN_KEEPALIVE void hide_all_c()         { if (g_app && g_app->ready) g_app->core.hideAll(); }
extern "C" EMSCRIPTEN_KEEPALIVE void toggle_xray_c()      { if (g_app && g_app->ready) g_app->core.toggleXray(); }
extern "C" EMSCRIPTEN_KEEPALIVE int  xray_is_active_c()   { return (g_app && g_app->ready && g_app->core.xrayActive()) ? 1 : 0; }
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_selection_outline_c(int on) {
    if (!g_app || !g_app->ready) return;
    g_app->core.setSelectionOutlineEnabled(on != 0);
    g_app->host.requestFrame();
}
extern "C" EMSCRIPTEN_KEEPALIVE int  ifcv_selection_outline_is_on_c() {
    return (g_app && g_app->ready && g_app->core.selectionOutlineEnabled()) ? 1 : 0;
}

// ===========================================================================
// Scripting API (web/ifcviewer.js wraps these into the IfcViewer object)
// ===========================================================================
//
// Arrays cross the boundary as (pointer, count) into the wasm heap; JS
// allocates with _malloc, fills HEAPU32, calls, frees. The getters follow the
// "ask twice" convention: they always return the TOTAL count and fill at most
// `max` entries, so a caller can size a buffer with (null, 0) and call again.
// Ids are object_ids — globally unique across federated models. The JS layer
// maps IFC GUIDs onto them from the element table (ifcv_request_objects_c).

// Camera state, as 9 floats: target xyz, distance, yaw°, pitch°, eye xyz. Eye
// comes from the core rather than being re-derived in JS, so the orbit
// convention has exactly one definition.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_get_camera_c(float* out) {
    if (!g_app || !g_app->ready || !out) return;
    const ViewportCore::CameraState s = g_app->core.cameraState();
    const Eigen::Vector3f eye = g_app->core.cameraEye();
    out[0] = s.target.x(); out[1] = s.target.y(); out[2] = s.target.z();
    out[3] = s.distance;   out[4] = s.yaw;        out[5] = s.pitch;
    out[6] = eye.x();      out[7] = eye.y();      out[8] = eye.z();
}
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_camera_c(float tx, float ty, float tz,
                                                       float dist, float yaw, float pitch) {
    if (!g_app || !g_app->ready) return;
    g_app->core.setCamera(tx, ty, tz, dist, yaw, pitch);
}
// toggleProjection is the only projection mutator in the core; drive it to the
// requested state so JS doesn't have to read-then-toggle.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_ortho_c(int on) {
    if (!g_app || !g_app->ready) return;
    if (bool(on) != g_app->core.projectionOrtho()) g_app->core.toggleProjection();
}

// Background colour, RGBA in [0..1]. Alpha 0 clears the canvas to nothing, so
// whatever the host page has stacked behind it shows through. See
// ViewportCore::setBackgroundColor.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_background_c(float r, float g,
                                                           float b, float a) {
    if (!g_app || !g_app->ready) return;
    g_app->core.setBackgroundColor(r, g, b, a);
}

// Mouse navigation scheme: "blender" | "rhino" | "revit" | "web". The preset
// only rewrites the button/modifier table classifyPress reads, so unlike the
// rest of the scripting API it does not need the GPU app to be live — a host
// page can pick its scheme the moment the module resolves. Unknown names fall
// back to blender inside the core; web/ifcviewer.js rejects them before they
// get here so a typo is an error rather than a silent scheme change.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_nav_preset_c(const char* name) {
    if (!g_app || !name) return;
    g_app->core.setNavPreset(name);
}

// Selection.
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_get_selection_c(std::uint32_t* out, int max) {
    if (!g_app || !g_app->ready) return 0;
    return fillIdsAscending(g_app->core.selection().selectionIds(), out, max);
}
extern "C" EMSCRIPTEN_KEEPALIVE std::uint32_t ifcv_get_active_object_c() {
    return (g_app && g_app->ready) ? g_app->core.selection().activeId() : 0u;
}
// mode: 0 replace (n == 0 clears), 1 add, 2 remove. applyMarqueeToSelection is
// the core's selection primitive and already means exactly this.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_apply_selection_c(const std::uint32_t* ids,
                                                            int n, int mode) {
    if (!g_app || !g_app->ready) return;
    g_app->core.applyMarqueeToSelection(idsFrom(ids, n), mode == 1, mode == 2);
}

// Per-object visibility. show_all_c / hide_all_c above cover the bulk cases.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_visible_c(const std::uint32_t* ids,
                                                        int n, int visible) {
    if (!g_app || !g_app->ready) return;
    g_app->core.setObjectsVisible(idsFrom(ids, n), visible != 0);
}
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_get_hidden_c(std::uint32_t* out, int max) {
    if (!g_app || !g_app->ready) return 0;
    return fillIdsAscending(g_app->core.hiddenIds(), out, max);
}

// Colour override. rgba8 is packed 0xAABBGGRR; 0 restores the baked colour.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_color_c(const std::uint32_t* ids, int n,
                                                      std::uint32_t rgba8) {
    if (!g_app || !g_app->ready) return;
    g_app->core.setObjectsColor(idsFrom(ids, n), rgba8);
}
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_clear_colors_c() {
    if (g_app && g_app->ready) g_app->core.clearObjectColors();
}

// ---- Federation ---------------------------------------------------------
//
// The concepts an .ifcfed carries, minus the file format: a federation unit, a
// false origin, and a per-model transform + display name. A host page that
// wants to read .ifcfed JSON (or a cloud manifest) parses it in JS and drives
// these. Models are addressed by the JS source id — the value registered
// before loading — so a transform can be set before the model has streamed.
//
// Angles are degrees, xyz/b/pivot are in the federation unit and `a` is in the
// model's project or map unit depending on a_frame, matching the desktop
// authoring model exactly (see FederationMath.h).

// Federation unit, e.g. ("METRE","") or ("foot",""), or ("METRE","MILLI").
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_federation_unit_c(const char* name,
                                                                const char* prefix) {
    if (!g_app || !name) return;
    FederationConfig cfg;
    cfg.unit_name   = name;
    cfg.unit_prefix = prefix ? prefix : "";
    g_app->federation.setConfig(cfg);
}

// Nominate xyz (federation unit) as the origin, with an optional grid-north
// heading. Setting this suppresses the automatic first-model guess.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_false_origin_c(double x, double y, double z,
                                                             double rz_deg) {
    if (!g_app) return;
    FederatedFalseOrigin origin;
    origin.xyz    = Eigen::Vector3d(x, y, z);
    origin.rz_deg = rz_deg;
    g_app->federation.setFalseOrigin(origin);
}

// Reads back the active origin — including one the guess produced — as
// [x, y, z, rz_deg, explicit]. `explicit` is 1 when a host set it.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_get_false_origin_c(double* out) {
    if (!g_app || !out) return;
    const FederatedFalseOrigin& o = g_app->federation.falseOrigin();
    out[0] = o.xyz.x(); out[1] = o.xyz.y(); out[2] = o.xyz.z();
    out[3] = o.rz_deg;
    out[4] = g_app->federation.falseOriginIsExplicit() ? 1.0 : 0.0;
}

// "Rotate about pivot, then translate so point a lands on point b."
// a_frame: 0 = ModelLocal (a is pre-CoordinateOperation, project units),
//          1 = ModelGlobal (a is post-CoordinateOperation, map units).
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_model_transform_c(
        int source_id, int a_frame,
        double ax, double ay, double az,
        double bx, double by, double bz,
        double rx, double ry, double rz,
        double px, double py, double pz) {
    if (!g_app) return;
    ModelTransformation xf;
    xf.a_frame  = (a_frame == 0) ? AFrame::ModelLocal : AFrame::ModelGlobal;
    xf.a        = Eigen::Vector3d(ax, ay, az);
    xf.b        = Eigen::Vector3d(bx, by, bz);
    xf.rxyz_deg = Eigen::Vector3d(rx, ry, rz);
    xf.pivot    = Eigen::Vector3d(px, py, pz);
    g_app->federation.setModelTransformation(source_id, xf);
}

extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_clear_model_transform_c(int source_id) {
    if (g_app) g_app->federation.clearModelTransformation(source_id);
}

extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_set_model_name_c(int source_id, const char* name) {
    if (g_app && name) g_app->federation.setModelName(source_id, name);
}

// The model's CoordinateOperation as baked into its sidecar, so a host can see
// what georeferencing a model actually carries: out[0] is 1 when the model has
// one, out[1..16] the 4x4 in metres (column-major), out[17] the project length
// unit scale and out[18] the map unit scale. Returns 0 when the source has not
// finished loading.
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_get_model_georef_c(int source_id, double* out) {
    if (!g_app || !out) return 0;
    const std::uint32_t session_model_id = g_app->federation.sessionModelId(source_id);
    if (session_model_id == 0) return 0;
    ModelGeoref georef;
    if (!g_app->core.modelGeoref(session_model_id, georef)) return 0;
    out[0] = georef.has_coordinate_operation ? 1.0 : 0.0;
    const Eigen::Matrix4d& m = georef.coordinate_operation_meters;
    for (int i = 0; i < 16; ++i) out[1 + i] = m.data()[i];
    out[17] = georef.units.project_length_to_meters;
    out[18] = georef.units.map_unit_to_meters;
    return 1;
}

// Every object in the scene, as JSON. Asynchronous: the element tables are
// fetched lazily per model on web (first paint must not wait on them), so this
// makes sure they are all resident and only then hands the page its array via
// Module.__ifcvOnObjects(token, json). `token` correlates the reply with the
// Promise the JS layer is holding.
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_request_objects_c(int token) {
    if (!g_app || !g_app->ready) {
        EM_ASM({ if (Module.__ifcvOnObjects) Module.__ifcvOnObjects($0, '[]'); }, token);
        return;
    }
    g_app->core.loadAllElementMetadataWeb([token](bool) {
        // Partial failures are not fatal: a model whose element block failed to
        // fetch simply contributes no rows, and the rest still resolve.
        std::string json = "[";
        bool first = true;
        for (const ViewportCore::ElementRef& e : g_app->core.elements()) {
            if (!first) json += ',';
            first = false;
            json += "{\"objectId\":" + std::to_string(e.object_id)
                  + ",\"model\":"    + std::to_string(e.model_index)
                  + ",\"sourceId\":" + std::to_string(e.source_id)
                  + ",\"guid\":"     + jsonString(e.guid)
                  + ",\"name\":"     + jsonString(e.name)
                  + ",\"type\":"     + jsonString(e.type) + '}';
        }
        json += ']';
        EM_ASM({ if (Module.__ifcvOnObjects) Module.__ifcvOnObjects($0, UTF8ToString($1)); },
               token, json.c_str());
    });
}

// Section-cut tool: toggle the drop-a-plane mode, clear all planes, query state.
extern "C" EMSCRIPTEN_KEEPALIVE void toggle_section_c() {
    if (!g_app || !g_app->ready) return;
    g_app->section_tool_active = !g_app->section_tool_active;
    Log::info() << "[section] tool "
                << (g_app->section_tool_active ? "active — click a surface to cut" : "off");
    g_app->host.requestFrame();
}
extern "C" EMSCRIPTEN_KEEPALIVE void clear_section_c() {
    if (g_app && g_app->ready) { g_app->core.clearSectionPlanes(); g_app->host.requestFrame(); }
}
extern "C" EMSCRIPTEN_KEEPALIVE int section_is_active_c() {
    return (g_app && g_app->ready && g_app->section_tool_active) ? 1 : 0;
}

// id: 0 Front, 1 Back, 2 Left, 3 Right, 4 Top, 5 Bottom.
extern "C" EMSCRIPTEN_KEEPALIVE void standard_view_c(int id) {
    if (!g_app || !g_app->ready || id < 0 || id > 5) return;
    using SV = ViewportCore::StandardView;
    static const SV map[6] = { SV::Front, SV::Back, SV::Left, SV::Right, SV::Top, SV::Bottom };
    g_app->core.setStandardView(map[id]);
    g_app->host.requestFrame();
}

// Streaming progress for the loading bar (the host page (web/ifcviewer.js) polls these each frame).
// total == 0 while still fetching metadata; resident climbs to total as
// geometry chunks arrive.
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_chunks_resident_c() {
    if (!g_app) return 0;
    int resident_chunks = 0, total_chunks = 0;
    g_app->core.streamingProgress(resident_chunks, total_chunks);
    return resident_chunks;
}
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_chunks_total_c() {
    if (!g_app) return 0;
    int resident_chunks = 0, total_chunks = 0;
    g_app->core.streamingProgress(resident_chunks, total_chunks);
    return total_chunks;
}

// Per-model progress for the federation loading panel: how many models are in
// the scene, and the idx-th model's resident/total chunks (idx ordered by load).
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_model_count_c() {
    return g_app ? g_app->core.streamingModelCount() : 0;
}
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_model_resident_c(int idx) {
    if (!g_app) return 0;
    int resident_chunks = 0, total_chunks = 0;
    g_app->core.streamingModelProgress(idx, resident_chunks, total_chunks);
    return resident_chunks;
}
extern "C" EMSCRIPTEN_KEEPALIVE int ifcv_model_total_c(int idx) {
    if (!g_app) return 0;
    int resident_chunks = 0, total_chunks = 0;
    g_app->core.streamingModelProgress(idx, resident_chunks, total_chunks);
    return total_chunks;
}

// Combined byte progress for the loading bar: total geometry, bytes the current
// view needs (contribution-culled), and how much of that is loaded. Doubles so
// JS gets exact byte counts well past 2 GB.
extern "C" EMSCRIPTEN_KEEPALIVE double ifcv_bytes_total_c() {
    if (!g_app) return 0.0;
    std::uint64_t total_bytes = 0, needed_bytes = 0, loaded_bytes = 0;
    g_app->core.streamingByteProgress(total_bytes, needed_bytes, loaded_bytes);
    return double(total_bytes);
}
extern "C" EMSCRIPTEN_KEEPALIVE double ifcv_bytes_needed_c() {
    if (!g_app) return 0.0;
    std::uint64_t total_bytes = 0, needed_bytes = 0, loaded_bytes = 0;
    g_app->core.streamingByteProgress(total_bytes, needed_bytes, loaded_bytes);
    return double(needed_bytes);
}
extern "C" EMSCRIPTEN_KEEPALIVE double ifcv_bytes_loaded_c() {
    if (!g_app) return 0.0;
    std::uint64_t total_bytes = 0, needed_bytes = 0, loaded_bytes = 0;
    g_app->core.streamingByteProgress(total_bytes, needed_bytes, loaded_bytes);
    return double(loaded_bytes);
}

int main(int /*argc*/, char** /*argv*/) {
    Log::info() << "ifcviewer-web: starting";
    g_app = new AppState();
    // Default to the web mouse scheme: LMB orbit, MMB pan, RMB select/marquee.
    // Host pages override it with ifcv_set_nav_preset_c (IfcViewer.create's
    // `navPreset` option) — e.g. "blender" for MMB-orbit.
    g_app->core.setNavPreset("web");
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
        g_app->core.buildSelectionOutlinePipelines();

        // Load the embedded sample sidecar (mounted into MEMFS via
        // --embed-file in CMakeLists.txt). The sample stays on the
        // synchronous MEMFS read; user-picked files go through the
        // Blob.slice byte-range path (load_sidecar_from_blob_c) so large
        // sidecars never enter the wasm heap.
        if (const std::uint32_t sample_id = g_app->core.loadSidecarFromPath("/sample.ifcview")) {
            // Bypasses the source registry, so tell the federation directly —
            // otherwise the first-model false-origin guess never runs for a
            // page that only ever shows the sample.
            g_app->federation.onModelLoadedWithoutSource(sample_id);
        } else {
            Log::warn() << "ifcviewer-web: sample sidecar load failed";
        }

        g_app->ready = true;

        // Now that the camera + render path are live, start listening for
        // orbit/pan/zoom input. (Pick is still deferred — it needs the
        // async buffer-readback rewrite before it's safe on web.)
        installInputHandlers(g_app);

        // Hand the app pointer to the JS-side RAF loop (set up in
        // the host page (web/ifcviewer.js)'s onRuntimeInitialized). The loop polls for
        // Module._app_ptr before invoking _raf_tick_c.
        EM_ASM({ Module._app_ptr = $0; }, (void*)g_app);
    });
    return 0;
}
