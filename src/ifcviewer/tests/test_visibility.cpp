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

// Tier-1 coverage of VisibilityState — the per-element hidden-id set
// consulted in cull. The class is pure stdlib; this test exercises its
// primitives directly. Bulk hide/isolate/show-all semantics live in
// ViewportWindow (which composes VisibilityState + the model
// instance lists) and would need an integration test, not a Tier-1 unit.

#include "VisibilityState.h"

#include <catch2/catch_test_macros.hpp>

TEST_CASE("VisibilityState starts empty", "[wgpu-visibility]") {
    VisibilityState vis;
    REQUIRE(vis.hiddenCount() == 0);
    REQUIRE_FALSE(vis.isHidden(0));        // 0 is the "no object" sentinel
    REQUIRE_FALSE(vis.isHidden(1));
    REQUIRE_FALSE(vis.isHidden(1u << 20));
}

TEST_CASE("hide(id) records the id; isHidden reflects it",
          "[wgpu-visibility]") {
    VisibilityState vis;

    vis.hide(1);
    vis.hide(2);
    vis.hide(3);

    REQUIRE(vis.hiddenCount() == 3);
    REQUIRE(vis.isHidden(1));
    REQUIRE(vis.isHidden(2));
    REQUIRE(vis.isHidden(3));
    REQUIRE_FALSE(vis.isHidden(4));
}

TEST_CASE("hide is idempotent", "[wgpu-visibility]") {
    VisibilityState vis;

    vis.hide(5);
    vis.hide(5);
    vis.hide(5);

    REQUIRE(vis.hiddenCount() == 1);
    REQUIRE(vis.isHidden(5));
}

TEST_CASE("hide(0) is ignored", "[wgpu-visibility]") {
    VisibilityState vis;

    vis.hide(0);
    REQUIRE(vis.hiddenCount() == 0);
    REQUIRE_FALSE(vis.isHidden(0));
}

TEST_CASE("show(id) removes a previously hidden id",
          "[wgpu-visibility]") {
    VisibilityState vis;
    vis.hide(1);
    vis.hide(2);

    vis.show(1);
    REQUIRE(vis.hiddenCount() == 1);
    REQUIRE_FALSE(vis.isHidden(1));
    REQUIRE(vis.isHidden(2));
}

TEST_CASE("show(non-hidden) is a no-op", "[wgpu-visibility]") {
    VisibilityState vis;
    vis.hide(1);

    vis.show(99);                 // never hidden
    REQUIRE(vis.hiddenCount() == 1);
    REQUIRE(vis.isHidden(1));
}

TEST_CASE("clear() drops every hidden id", "[wgpu-visibility]") {
    VisibilityState vis;
    vis.hide(1);
    vis.hide(2);
    vis.hide(3);

    vis.clear();
    REQUIRE(vis.hiddenCount() == 0);
    REQUIRE_FALSE(vis.isHidden(1));
    REQUIRE_FALSE(vis.isHidden(2));
    REQUIRE_FALSE(vis.isHidden(3));
}

TEST_CASE("hiddenIds returns the live set", "[wgpu-visibility]") {
    VisibilityState vis;
    vis.hide(10);
    vis.hide(20);
    vis.hide(30);

    const auto& ids = vis.hiddenIds();
    REQUIRE(ids.size() == 3);
    REQUIRE(ids.count(10) == 1);
    REQUIRE(ids.count(20) == 1);
    REQUIRE(ids.count(30) == 1);
    REQUIRE(ids.count(40) == 0);
}
