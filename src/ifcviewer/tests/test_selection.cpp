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

// Tier-1 coverage of SelectionState — the CPU-side selection set + active
// id used by the wgpu viewport. The class is pure stdlib (no Qt, no QObject),
// so the test exercises the state machine directly. The GPU-side flags SSBO
// is filled via fillFlagsArray; that pure-function path is also covered.

#include "SelectionState.h"

#include <catch2/catch_test_macros.hpp>

#include <vector>

TEST_CASE("SelectionState starts empty with no active id", "[wgpu-selection]") {
    SelectionState sel;
    REQUIRE(sel.count() == 0);
    REQUIRE(sel.activeId() == 0);
    REQUIRE_FALSE(sel.contains(1));
    REQUIRE_FALSE(sel.dirty());
}

TEST_CASE("replace(id) selects a single id and makes it active",
          "[wgpu-selection]") {
    SelectionState sel;

    sel.replace(5);
    REQUIRE(sel.count() == 1);
    REQUIRE(sel.contains(5));
    REQUIRE(sel.activeId() == 5);
    REQUIRE(sel.dirty());
}

TEST_CASE("replace(0) clears the selection", "[wgpu-selection]") {
    SelectionState sel;
    sel.replace(5);
    sel.markClean();

    sel.replace(0);
    REQUIRE(sel.count() == 0);
    REQUIRE(sel.activeId() == 0);
    REQUIRE(sel.dirty());
}

TEST_CASE("add(id) appends to the set and steals active", "[wgpu-selection]") {
    SelectionState sel;
    sel.replace(1);
    sel.markClean();

    sel.add(2);
    REQUIRE(sel.count() == 2);
    REQUIRE(sel.contains(1));
    REQUIRE(sel.contains(2));
    // Each click should drive the properties panel to the most recently
    // touched object, so active follows the last add — distinct from GL's
    // addToSelection (which kept the prior active).
    REQUIRE(sel.activeId() == 2);
    REQUIRE(sel.dirty());
}

TEST_CASE("add(0) is ignored", "[wgpu-selection]") {
    SelectionState sel;
    sel.replace(1);
    sel.markClean();

    sel.add(0);
    REQUIRE(sel.count() == 1);
    REQUIRE(sel.activeId() == 1);
    REQUIRE_FALSE(sel.dirty());   // no-op didn't flip the flag
}

TEST_CASE("remove(non-active) keeps active", "[wgpu-selection]") {
    SelectionState sel;
    sel.replace(1);
    sel.add(2);
    sel.add(3);
    REQUIRE(sel.activeId() == 3);
    sel.markClean();

    sel.remove(1);
    REQUIRE(sel.count() == 2);
    REQUIRE_FALSE(sel.contains(1));
    REQUIRE(sel.activeId() == 3);  // still the most recently touched
    REQUIRE(sel.dirty());
}

TEST_CASE("remove(active) falls back to some remaining id", "[wgpu-selection]") {
    SelectionState sel;
    sel.replace(1);
    sel.add(2);
    sel.add(3);
    REQUIRE(sel.activeId() == 3);

    sel.remove(3);
    REQUIRE(sel.count() == 2);
    REQUIRE_FALSE(sel.contains(3));
    // Active falls back to *some* remaining id (implementation picks the
    // unordered_set's first element; documenting non-determinism rather
    // than the specific choice).
    const uint32_t a = sel.activeId();
    REQUIRE((a == 1 || a == 2));
    REQUIRE(sel.contains(a));
}

TEST_CASE("remove(last id) clears active", "[wgpu-selection]") {
    SelectionState sel;
    sel.replace(7);
    REQUIRE(sel.activeId() == 7);

    sel.remove(7);
    REQUIRE(sel.count() == 0);
    REQUIRE(sel.activeId() == 0);
}

TEST_CASE("remove(non-existent) is a no-op for state, no dirty flag",
          "[wgpu-selection]") {
    SelectionState sel;
    sel.replace(1);
    sel.markClean();

    sel.remove(99);
    REQUIRE(sel.count() == 1);
    REQUIRE(sel.activeId() == 1);
    REQUIRE_FALSE(sel.dirty());
}

TEST_CASE("remove(0) is ignored", "[wgpu-selection]") {
    SelectionState sel;
    sel.replace(1);
    sel.markClean();

    sel.remove(0);
    REQUIRE(sel.count() == 1);
    REQUIRE_FALSE(sel.dirty());
}

TEST_CASE("toggle adds when absent, removes when present", "[wgpu-selection]") {
    SelectionState sel;

    sel.toggle(5);
    REQUIRE(sel.contains(5));
    REQUIRE(sel.activeId() == 5);

    sel.toggle(6);
    REQUIRE(sel.contains(6));
    REQUIRE(sel.activeId() == 6);   // last add steals active

    sel.toggle(5);                  // remove non-active — active unchanged
    REQUIRE_FALSE(sel.contains(5));
    REQUIRE(sel.activeId() == 6);

    sel.toggle(6);                  // remove active — fallback (set empty → 0)
    REQUIRE(sel.count() == 0);
    REQUIRE(sel.activeId() == 0);
}

TEST_CASE("toggle(0) is ignored", "[wgpu-selection]") {
    SelectionState sel;
    sel.markClean();

    sel.toggle(0);
    REQUIRE(sel.count() == 0);
    REQUIRE_FALSE(sel.dirty());
}

TEST_CASE("clear empties; no-op when already empty", "[wgpu-selection]") {
    SelectionState sel;

    sel.clear();                    // already empty
    REQUIRE_FALSE(sel.dirty());

    sel.replace(1);
    sel.markClean();
    sel.clear();
    REQUIRE(sel.count() == 0);
    REQUIRE(sel.activeId() == 0);
    REQUIRE(sel.dirty());
}

TEST_CASE("markClean clears the dirty flag", "[wgpu-selection]") {
    SelectionState sel;
    sel.replace(5);
    REQUIRE(sel.dirty());

    sel.markClean();
    REQUIRE_FALSE(sel.dirty());

    // Subsequent mutation re-arms the flag.
    sel.add(6);
    REQUIRE(sel.dirty());
}

TEST_CASE("selectionIds returns the live set", "[wgpu-selection]") {
    SelectionState sel;
    sel.add(1);
    sel.add(2);
    sel.add(3);

    const auto& ids = sel.selectionIds();
    REQUIRE(ids.size() == 3);
    REQUIRE(ids.count(1) == 1);
    REQUIRE(ids.count(2) == 1);
    REQUIRE(ids.count(3) == 1);
}

TEST_CASE("fillFlagsArray packs selected/active bits per object_id",
          "[wgpu-selection]") {
    SelectionState sel;
    sel.add(1);
    sel.add(3);   // active is now 3

    std::vector<uint32_t> flags;
    sel.fillFlagsArray(flags, 8);

    REQUIRE(flags.size() == 8);
    REQUIRE(flags[0] == 0u);          // sentinel
    REQUIRE(flags[1] == 1u);          // selected, not active
    REQUIRE(flags[2] == 0u);
    REQUIRE(flags[3] == (1u | 2u));   // selected + active
    REQUIRE(flags[4] == 0u);
    REQUIRE(flags[5] == 0u);
    REQUIRE(flags[6] == 0u);
    REQUIRE(flags[7] == 0u);
}

TEST_CASE("fillFlagsArray drops ids past the entries cap",
          "[wgpu-selection]") {
    SelectionState sel;
    sel.add(1);
    sel.add(100);   // active is 100

    std::vector<uint32_t> flags;
    sel.fillFlagsArray(flags, 4);

    REQUIRE(flags.size() == 4);
    REQUIRE(flags[1] == 1u);
    // id 100 is out of range — should not write to flags[2]/[3]/etc.
    REQUIRE(flags[2] == 0u);
    REQUIRE(flags[3] == 0u);
}
