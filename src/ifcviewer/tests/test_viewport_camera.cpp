// Headless unit tests for ViewportCore's pure camera + visibility ops — the
// fly camera math (flyMove / flyLook / flyAdjustSpeed) and hide/x-ray, all of
// which are shared verbatim by the desktop and web hosts. ViewportCore is
// constructed with a mock ViewportHost; no GPU is created, and construction /
// teardown touch no wgpu (the GPU teardown lives in releaseWgpuModelGpuData,
// only reached with models loaded). So these run fast and deterministically.

#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>

#include "ViewportCore.h"
#include "ViewportHost.h"

#include <cmath>

using Catch::Matchers::WithinAbs;

struct ViewportCoreTestAccess {
    static void addObjectAabb(ViewportCore& core, uint32_t object_id,
                              const Eigen::Vector3f& mn,
                              const Eigen::Vector3f& mx) {
        InstanceInfo inst{};
        inst.object_id = object_id;
        for (int i = 0; i < 3; ++i) {
            inst.world_aabb_min[i] = mn[i];
            inst.world_aabb_max[i] = mx[i];
        }
        core.models_gpu_[1].instances.push_back(inst);
    }

    static Eigen::Vector3f orbitPivot(const ViewportCore& core) {
        return core.orbit_pivot_;
    }

    static bool hasSelectionOrbitPivot(const ViewportCore& core) {
        return core.orbit_selection_pivot_active_;
    }
};

namespace {

// Minimal host: the camera ops only ever call requestFrame().
struct MockHost : ViewportHost {
    int frames_requested = 0;
    WGPUSurface createSurface(WGPUInstance) override { return nullptr; }
    void  framebufferSize(int& w, int& h) const override { w = 800; h = 600; }
    float dpr() const override { return 1.0f; }
    void  requestFrame() override { ++frames_requested; }
    void  quit() override {}
};

// eye = orbitEye convention: target + dist * (cos p cos y, cos p sin y, sin p).
Eigen::Vector3f eyeOf(const ViewportCore& c) {
    const auto s = c.cameraState();
    const float d2r = 3.14159265358979323846f / 180.0f;
    const float y = s.yaw * d2r, p = s.pitch * d2r;
    const float cp = std::cos(p), sp = std::sin(p), cy = std::cos(y), sy = std::sin(y);
    return s.target + s.distance * Eigen::Vector3f(cp * cy, cp * sy, sp);
}

Eigen::Vector3f ndcOf(const ViewportCore& core, const Eigen::Vector3f& point) {
    Eigen::Matrix4f view, projection;
    core.buildViewProj(view, projection);
    const Eigen::Vector4f clip =
        projection * view * Eigen::Vector4f(point.x(), point.y(), point.z(), 1.0f);
    return clip.head<3>() / clip.w();
}

} // namespace

TEST_CASE("flyMove: W drives the eye toward the look direction", "[camera][fly]") {
    MockHost host; ViewportCore core(&host);
    // Look down -X: target at origin, eye at (+dist,0,0) → forward = (-1,0,0).
    core.setCamera(0, 0, 0, /*dist*/10, /*yaw*/0, /*pitch*/0);

    // dt is clamped to 0.1s inside flyMove, so use 0.1 for a predictable step:
    // move = forward*speed*dt = (-1,0,0)*5*0.1.
    core.flyMove(/*fwd*/true, false, false, false, false, false, /*boost*/false, /*dt*/0.1f);
    const auto s = core.cameraState();
    REQUIRE_THAT(s.target.x(), WithinAbs(-0.5f, 1e-4f));
    REQUIRE_THAT(s.target.y(), WithinAbs(0.0f, 1e-4f));
    REQUIRE_THAT(s.target.z(), WithinAbs(0.0f, 1e-4f));
}

TEST_CASE("flyMove: Shift boosts 5x, opposing keys cancel", "[camera][fly]") {
    MockHost host; ViewportCore core(&host);

    SECTION("boost") {
        core.setCamera(0, 0, 0, 10, 0, 0);
        core.flyMove(true, false, false, false, false, false, /*boost*/true, 0.1f);
        REQUIRE_THAT(core.cameraState().target.x(), WithinAbs(-2.5f, 1e-3f));  // 5 * 5 * 0.1
    }
    SECTION("W+S cancel → no move") {
        core.setCamera(1, 2, 3, 10, 0, 0);
        core.flyMove(/*fwd*/true, /*back*/true, false, false, false, false, false, 0.1f);
        const auto s = core.cameraState();
        REQUIRE_THAT(s.target.x(), WithinAbs(1.0f, 1e-5f));
        REQUIRE_THAT(s.target.y(), WithinAbs(2.0f, 1e-5f));
        REQUIRE_THAT(s.target.z(), WithinAbs(3.0f, 1e-5f));
    }
}

TEST_CASE("flyMove: dt is clamped so a stall can't warp the camera", "[camera][fly]") {
    MockHost host; ViewportCore core(&host);
    core.setCamera(0, 0, 0, 10, 0, 0);
    core.flyMove(true, false, false, false, false, false, false, /*dt*/10.0f);  // huge stall
    // dt clamps to 0.1 → move = 5 * 0.1 = 0.5, not 50.
    REQUIRE_THAT(core.cameraState().target.x(), WithinAbs(-0.5f, 1e-4f));
}

TEST_CASE("flyMove: QE move along world +Z; looking straight down stays finite",
          "[camera][fly]") {
    MockHost host; ViewportCore core(&host);
    SECTION("E rises along +Z") {
        core.setCamera(0, 0, 0, 10, 0, 0);
        core.flyMove(false, false, false, false, /*up*/true, false, false, 0.1f);
        const auto s = core.cameraState();
        REQUIRE_THAT(s.target.z(), WithinAbs(0.5f, 1e-4f));  // 5 * 0.1
    }
    SECTION("degenerate pitch (top view) doesn't NaN the right vector") {
        core.setStandardView(ViewportCore::StandardView::Top);  // pitch ~ +90
        core.flyMove(false, false, /*right*/true, false, false, false, false, 0.1f);
        const auto s = core.cameraState();
        REQUIRE(std::isfinite(s.target.x()));
        REQUIRE(std::isfinite(s.target.y()));
        REQUIRE(std::isfinite(s.target.z()));
    }
}

TEST_CASE("flyLook: turns in place — the eye stays pinned", "[camera][fly]") {
    MockHost host; ViewportCore core(&host);
    core.setCamera(5, -3, 2, 12, 30, 10);
    const Eigen::Vector3f eye_before = eyeOf(core);
    const float yaw_before   = core.cameraState().yaw;
    const float pitch_before = core.cameraState().pitch;

    core.flyLook(/*dx*/100.0f, /*dy*/40.0f);

    const Eigen::Vector3f eye_after = eyeOf(core);
    // Eye pinned (turn-in-place) to well within a millimetre.
    REQUIRE_THAT((eye_after - eye_before).norm(), WithinAbs(0.0f, 1e-3f));
    // Orientation actually changed: yaw -= dx*0.2, pitch += dy*0.2.
    REQUIRE_THAT(core.cameraState().yaw,   WithinAbs(yaw_before   - 20.0f, 1e-3f));
    REQUIRE_THAT(core.cameraState().pitch, WithinAbs(pitch_before +  8.0f, 1e-3f));
}

TEST_CASE("flyLook: pitch is clamped to +/-89.9", "[camera][fly]") {
    MockHost host; ViewportCore core(&host);
    core.setCamera(0, 0, 0, 10, 0, 0);
    core.flyLook(0.0f, /*dy*/100000.0f);
    REQUIRE(core.cameraState().pitch <= 89.9f);
    core.flyLook(0.0f, -100000.0f);
    REQUIRE(core.cameraState().pitch >= -89.9f);
}

TEST_CASE("flyAdjustSpeed: scales x1.25/notch, clamped to [0.05, 1000]", "[camera][fly]") {
    MockHost host; ViewportCore core(&host);
    REQUIRE_THAT(core.flySpeed(), WithinAbs(5.0f, 1e-5f));      // default
    core.flyAdjustSpeed(1.0f);
    REQUIRE_THAT(core.flySpeed(), WithinAbs(6.25f, 1e-4f));     // 5 * 1.25
    core.flyAdjustSpeed(1000.0f);                               // way up
    REQUIRE_THAT(core.flySpeed(), WithinAbs(1000.0f, 1e-2f));   // clamped high
    core.flyAdjustSpeed(-1000.0f);                              // way down
    REQUIRE_THAT(core.flySpeed(), WithinAbs(0.05f, 1e-4f));     // clamped low
}

TEST_CASE("toggleXray flips the active state", "[camera][xray]") {
    MockHost host; ViewportCore core(&host);
    REQUIRE_FALSE(core.xrayActive());
    core.toggleXray();
    REQUIRE(core.xrayActive());
    core.toggleXray();
    REQUIRE_FALSE(core.xrayActive());
}

TEST_CASE("section planes: add appends, clear drops all, capped at the max",
          "[camera][section]") {
    MockHost host; ViewportCore core(&host);
    REQUIRE(core.sectionPlaneCount() == 0);

    const Eigen::Vector3f pt(1, 2, 3), n(0, 0, 1);
    REQUIRE(core.addSectionPlaneAtSurface(pt, n, 1.0f));
    REQUIRE(core.addSectionPlaneAtSurface(pt, n, 1.0f));
    REQUIRE(core.sectionPlaneCount() == 2);

    // Fill to the cap (kMaxSectionPlanes == 6); further adds are rejected.
    while (core.sectionPlaneCount() < 6) REQUIRE(core.addSectionPlaneAtSurface(pt, n, 1.0f));
    REQUIRE_FALSE(core.addSectionPlaneAtSurface(pt, n, 1.0f));
    REQUIRE(core.sectionPlaneCount() == 6);

    core.clearSectionPlanes();
    REQUIRE(core.sectionPlaneCount() == 0);
}

TEST_CASE("setNavPreset maps names to the shared button bindings", "[camera][nav]") {
    MockHost host; ViewportCore core(&host);
    using B = ViewportCore::MouseBtn; using M = ViewportCore::NavMod;

    // Default is blender: orbit MMB, pan Shift+MMB, select LMB.
    {
        const auto& b = core.navBindings();
        REQUIRE(b.orbit == B::Middle);  REQUIRE(b.orbit_mod == M::Plain);
        REQUIRE(b.pan   == B::Middle);  REQUIRE(b.pan_mod   == M::Shift);
        REQUIRE(b.select == B::Left);   REQUIRE(b.select_mod == M::Plain);
    }
    SECTION("web: orbit LMB, pan MMB, select RMB") {
        core.setNavPreset("web");
        const auto& b = core.navBindings();
        REQUIRE(b.orbit == B::Left);    REQUIRE(b.orbit_mod == M::Plain);
        REQUIRE(b.pan   == B::Middle);  REQUIRE(b.pan_mod   == M::Plain);
        REQUIRE(b.select == B::Right);  REQUIRE(b.select_mod == M::Plain);
    }
    SECTION("rhino: orbit RMB, pan Shift+RMB") {
        core.setNavPreset("rhino");
        const auto& b = core.navBindings();
        REQUIRE(b.orbit == B::Right);   REQUIRE(b.pan == B::Right);
        REQUIRE(b.pan_mod == M::Shift); REQUIRE(b.select == B::Left);
    }
    SECTION("revit: orbit Shift+MMB, pan MMB") {
        core.setNavPreset("revit");
        const auto& b = core.navBindings();
        REQUIRE(b.orbit == B::Middle);  REQUIRE(b.orbit_mod == M::Shift);
        REQUIRE(b.pan == B::Middle);    REQUIRE(b.pan_mod == M::Plain);
    }
    SECTION("unknown name falls back to blender") {
        core.setNavPreset("web");
        core.setNavPreset("nonsense");
        const auto& b = core.navBindings();
        REQUIRE(b.orbit == B::Middle);  REQUIRE(b.select == B::Left);
    }
}

TEST_CASE("Revit orbit uses the selected objects' combined AABB centre without recentering",
          "[camera][nav]") {
    MockHost host;
    ViewportCore core(&host);
    core.setCamera(3, 4, 5, 10, 20, 15);
    const auto camera_before = core.cameraState();
    const Eigen::Vector3f eye_before = eyeOf(core);

    ViewportCoreTestAccess::addObjectAabb(
        core, 7, Eigen::Vector3f(1, 2, 3), Eigen::Vector3f(5, 8, 11));
    ViewportCoreTestAccess::addObjectAabb(
        core, 8, Eigen::Vector3f(18, 20, 22), Eigen::Vector3f(22, 24, 28));
    core.applyPickToSelection(7, /*add*/false, /*remove*/false);
    core.applyPickToSelection(8, /*add*/true, /*remove*/false);
    core.setNavPreset("revit");

    REQUIRE(core.beginOrbit());

    const Eigen::Vector3f expected_pivot(11.5f, 13.0f, 15.5f);
    REQUIRE(ViewportCoreTestAccess::hasSelectionOrbitPivot(core));
    REQUIRE_THAT(
        (ViewportCoreTestAccess::orbitPivot(core) - expected_pivot).norm(),
        WithinAbs(0.0f, 1e-5f));

    // Starting the gesture must not change the current viewport.
    const auto camera_after_begin = core.cameraState();
    REQUIRE(camera_after_begin.target == camera_before.target);
    REQUIRE(camera_after_begin.distance == camera_before.distance);
    REQUIRE(camera_after_begin.yaw == camera_before.yaw);
    REQUIRE(camera_after_begin.pitch == camera_before.pitch);
    REQUIRE_THAT((eyeOf(core) - eye_before).norm(), WithinAbs(0.0f, 1e-6f));

    // The off-axis pivot remains at the same screen position while orbiting.
    const Eigen::Vector3f pivot_ndc_before = ndcOf(core, expected_pivot);
    core.orbitBy(25.0f, -12.0f);
    const Eigen::Vector3f pivot_ndc_after = ndcOf(core, expected_pivot);
    REQUIRE_THAT(
        (pivot_ndc_after.head<2>() - pivot_ndc_before.head<2>()).norm(),
        WithinAbs(0.0f, 1e-4f));
}

TEST_CASE("Non-Revit presets keep orbit on the current camera target", "[camera][nav]") {
    const char* presets[] = {"blender", "rhino", "web"};
    for (const char* preset : presets) {
        INFO("preset: " << preset);
        MockHost host;
        ViewportCore core(&host);
        core.setCamera(4, 5, 6, 10, 0, 0);
        ViewportCoreTestAccess::addObjectAabb(
            core, 7, Eigen::Vector3f(10, 20, 30), Eigen::Vector3f(12, 22, 32));
        core.applyPickToSelection(7, /*add*/false, /*remove*/false);
        core.setNavPreset(preset);

        REQUIRE_FALSE(core.beginOrbit());
        const auto before = core.cameraState();
        core.orbitBy(25.0f, -12.0f);
        const auto after = core.cameraState();
        REQUIRE(after.target == before.target);
        REQUIRE(after.distance == before.distance);
        REQUIRE(after.yaw != before.yaw);
    }
}

TEST_CASE("hideSelected hides the selection; showAll restores", "[camera][visibility]") {
    MockHost host; ViewportCore core(&host);
    REQUIRE(core.hiddenCount() == 0);

    core.applyPickToSelection(42, /*add*/false, /*remove*/false);  // select object 42
    core.hideSelected();
    REQUIRE(core.hiddenCount() == 1);

    // Hiding deselects, so a second hide with nothing selected is a no-op.
    core.hideSelected();
    REQUIRE(core.hiddenCount() == 1);

    core.showAll();
    REQUIRE(core.hiddenCount() == 0);
}

TEST_CASE("applyMarqueeToSelection: replace / add / remove", "[camera][selection]") {
    MockHost host; ViewportCore core(&host);
    // No public selection accessor, so verify via hideSelected → hiddenCount.
    SECTION("plain marquee replaces the selection") {
        core.applyMarqueeToSelection({1, 2, 3}, /*add*/false, /*remove*/false);
        core.hideSelected();
        REQUIRE(core.hiddenCount() == 3);
    }
    SECTION("add unions, remove subtracts") {
        core.applyMarqueeToSelection({5},    false, false);  // replace → {5}
        core.applyMarqueeToSelection({6, 7}, true,  false);  // add     → {5,6,7}
        core.applyMarqueeToSelection({6},    false, true);   // remove  → {5,7}
        core.hideSelected();
        REQUIRE(core.hiddenCount() == 2);
    }
    SECTION("id 0 is ignored") {
        core.applyMarqueeToSelection({0, 9, 0}, false, false);
        core.hideSelected();
        REQUIRE(core.hiddenCount() == 1);
    }
}
