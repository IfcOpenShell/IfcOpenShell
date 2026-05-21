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

// Tier-1 coverage of VisibilityState — the per-element hidden-set tracker.
// It is a QObject (for the changed() signal) but touches no GL, so the test
// exercises the full state machine directly and asserts the hot-path
// isHidden() flag mirror stays consistent with the canonical hidden set.

#include "Visibility.h"

#include <catch2/catch_test_macros.hpp>

#include <QCoreApplication>
#include <QSignalSpy>

namespace {

// Catch2 owns main(), so QCoreApplication can't live in a TU constructor.
// Lazily construct it (intentionally leaked) the first time any test asks.
void ensureQApp() {
    if (QCoreApplication::instance()) return;
    static int argc = 1;
    static char arg0[] = "test_visibility";
    static char* argv[] = {arg0, nullptr};
    new QCoreApplication(argc, argv);
}

} // namespace

TEST_CASE("VisibilityState starts empty", "[visibility]") {
    ensureQApp();
    VisibilityState vis;
    REQUIRE(vis.empty());
    REQUIRE(vis.size() == 0);
    REQUIRE_FALSE(vis.isHidden(0));   // 0 is the "no object" sentinel
    REQUIRE_FALSE(vis.isHidden(1));
    REQUIRE_FALSE(vis.isHidden(1u << 20));
}

TEST_CASE("hideObjects unions ids, emits changed, and isHidden reflects it",
          "[visibility]") {
    ensureQApp();
    VisibilityState vis;
    QSignalSpy spy(&vis, &VisibilityState::changed);

    vis.hideObjects({1, 2, 3});
    REQUIRE(spy.count() == 1);
    REQUIRE(vis.size() == 3);
    REQUIRE(vis.isHidden(1));
    REQUIRE(vis.isHidden(2));
    REQUIRE(vis.isHidden(3));
    REQUIRE_FALSE(vis.isHidden(4));

    // Unioning in a fresh id signals once more and grows the set.
    vis.hideObjects({2, 4});  // 2 already hidden, 4 is new
    REQUIRE(spy.count() == 2);
    REQUIRE(vis.size() == 4);
    REQUIRE(vis.isHidden(4));
}

TEST_CASE("hideObjects ignores object_id 0 and is idempotent", "[visibility]") {
    ensureQApp();
    VisibilityState vis;
    QSignalSpy spy(&vis, &VisibilityState::changed);

    vis.hideObjects({0});
    REQUIRE(vis.empty());
    REQUIRE(spy.count() == 0);     // nothing changed
    REQUIRE_FALSE(vis.isHidden(0));

    vis.hideObjects({7});
    REQUIRE(spy.count() == 1);
    vis.hideObjects({7});          // already hidden — no-op
    REQUIRE(spy.count() == 1);
}

TEST_CASE("showObjects subtracts and emits only when something changes",
          "[visibility]") {
    ensureQApp();
    VisibilityState vis;
    vis.hideObjects({1, 2, 3});

    QSignalSpy spy(&vis, &VisibilityState::changed);
    vis.showObjects({2});
    REQUIRE(spy.count() == 1);
    REQUIRE_FALSE(vis.isHidden(2));
    REQUIRE(vis.isHidden(1));
    REQUIRE(vis.isHidden(3));
    REQUIRE(vis.size() == 2);

    // Showing an id that was never hidden changes nothing.
    vis.showObjects({99});
    REQUIRE(spy.count() == 1);
}

TEST_CASE("setHidden replaces the set wholesale and drops id 0", "[visibility]") {
    ensureQApp();
    VisibilityState vis;
    vis.hideObjects({1, 2});

    QSignalSpy spy(&vis, &VisibilityState::changed);
    vis.setHidden({3, 4, 0});
    REQUIRE(spy.count() == 1);
    REQUIRE(vis.size() == 2);          // id 0 was stripped
    REQUIRE_FALSE(vis.isHidden(0));
    REQUIRE_FALSE(vis.isHidden(1));    // old members cleared
    REQUIRE_FALSE(vis.isHidden(2));
    REQUIRE(vis.isHidden(3));
    REQUIRE(vis.isHidden(4));

    // Replacing with an identical set is a no-op.
    vis.setHidden({3, 4});
    REQUIRE(spy.count() == 1);
}

TEST_CASE("showAll clears the set; no-op when already empty", "[visibility]") {
    ensureQApp();
    VisibilityState vis;
    vis.hideObjects({1, 2});

    QSignalSpy spy(&vis, &VisibilityState::changed);
    vis.showAll();
    REQUIRE(spy.count() == 1);
    REQUIRE(vis.empty());
    REQUIRE_FALSE(vis.isHidden(1));
    REQUIRE_FALSE(vis.isHidden(2));

    vis.showAll();                 // already empty
    REQUIRE(spy.count() == 1);
}

TEST_CASE("reset clears state and emits only when state existed", "[visibility]") {
    ensureQApp();
    VisibilityState vis;

    QSignalSpy spy(&vis, &VisibilityState::changed);
    vis.reset();                   // nothing to clear
    REQUIRE(spy.count() == 0);

    vis.hideObjects({5});
    REQUIRE(spy.count() == 1);
    vis.reset();
    REQUIRE(spy.count() == 2);
    REQUIRE(vis.empty());
    REQUIRE_FALSE(vis.isHidden(5));
}

TEST_CASE("hideObjects grows the flag mirror for large object ids", "[visibility]") {
    ensureQApp();
    VisibilityState vis;

    // A high id forces the cpu_flags_ vector (used by the hot-path isHidden)
    // to resize.  isHidden must report it correctly without going out of
    // bounds, and neighbouring ids must stay visible.
    const uint32_t big = 1'000'000;
    vis.hideObjects({big});
    REQUIRE(vis.isHidden(big));
    REQUIRE_FALSE(vis.isHidden(big - 1));
    REQUIRE_FALSE(vis.isHidden(big + 1));
    REQUIRE(vis.hiddenIds().count(big) == 1);

    vis.noteObjectId(big * 2);     // pre-grow only — id stays visible
    REQUIRE_FALSE(vis.isHidden(big * 2));
}
