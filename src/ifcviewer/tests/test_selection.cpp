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

// Tier-1 coverage of SelectionState — the viewport's multi-selection state
// machine.  The class also owns a GL flags SSBO, but every GL path guards on
// a context that initializeGl() has wired up; the test never calls
// initializeGl(), so the CPU-side selection set / active-id logic runs in
// full isolation (gl_ stays null and bindForRender is simply not exercised).

#include "Selection.h"

#include <catch2/catch_test_macros.hpp>

#include <QCoreApplication>
#include <QSignalSpy>

namespace {

// Catch2 owns main(), so QCoreApplication can't live in a TU constructor.
// Lazily construct it (intentionally leaked) the first time any test asks.
void ensureQApp() {
    if (QCoreApplication::instance()) return;
    static int argc = 1;
    static char arg0[] = "test_selection";
    static char* argv[] = {arg0, nullptr};
    new QCoreApplication(argc, argv);
}

// First arg of the most recent changed(active_id) signal.
uint32_t lastActive(QSignalSpy& spy) {
    REQUIRE(spy.count() > 0);
    return spy.takeLast().at(0).toUInt();
}

} // namespace

TEST_CASE("SelectionState starts empty with no active id", "[selection]") {
    ensureQApp();
    SelectionState sel;
    REQUIRE(sel.empty());
    REQUIRE(sel.size() == 0);
    REQUIRE(sel.activeObjectId() == 0);
    REQUIRE_FALSE(sel.isSelected(1));
}

TEST_CASE("setSelectedObjectId selects a single id and makes it active",
          "[selection]") {
    ensureQApp();
    SelectionState sel;
    QSignalSpy spy(&sel, &SelectionState::changed);

    sel.setSelectedObjectId(5);
    REQUIRE(spy.count() == 1);
    REQUIRE(sel.size() == 1);
    REQUIRE(sel.isSelected(5));
    REQUIRE(sel.activeObjectId() == 5);
    REQUIRE(lastActive(spy) == 5);
}

TEST_CASE("setSelectedObjectId(0) clears the selection", "[selection]") {
    ensureQApp();
    SelectionState sel;
    sel.setSelectedObjectId(5);

    QSignalSpy spy(&sel, &SelectionState::changed);
    sel.setSelectedObjectId(0);
    REQUIRE(spy.count() == 1);
    REQUIRE(sel.empty());
    REQUIRE(sel.activeObjectId() == 0);
    REQUIRE(lastActive(spy) == 0);
}

TEST_CASE("setSelection coerces active to 0 when it is not in the set",
          "[selection]") {
    ensureQApp();
    SelectionState sel;

    sel.setSelection({1, 2, 3}, /*active=*/9);  // 9 not in the set
    REQUIRE(sel.size() == 3);
    REQUIRE(sel.activeObjectId() == 0);

    sel.setSelection({1, 2, 3}, /*active=*/2);  // 2 is in the set
    REQUIRE(sel.activeObjectId() == 2);
}

TEST_CASE("setSelection drops object_id 0 and no-ops on identical state",
          "[selection]") {
    ensureQApp();
    SelectionState sel;
    QSignalSpy spy(&sel, &SelectionState::changed);

    sel.setSelection({0, 1, 2}, /*active=*/1);
    REQUIRE(spy.count() == 1);
    REQUIRE(sel.size() == 2);            // id 0 stripped
    REQUIRE_FALSE(sel.isSelected(0));
    REQUIRE(sel.activeObjectId() == 1);

    // Same set + same active — no churn.
    sel.setSelection({1, 2}, /*active=*/1);
    REQUIRE(spy.count() == 1);
}

TEST_CASE("addToSelection adds ids, keeps active, ignores 0 and no-ops",
          "[selection]") {
    ensureQApp();
    SelectionState sel;
    sel.setSelectedObjectId(1);

    QSignalSpy spy(&sel, &SelectionState::changed);
    sel.addToSelection({2, 3});
    REQUIRE(spy.count() == 1);
    REQUIRE(sel.size() == 3);
    REQUIRE(sel.activeObjectId() == 1);  // active unchanged by add
    REQUIRE(lastActive(spy) == 1);

    // Nothing new -> no signal.
    sel.addToSelection({2});
    REQUIRE(spy.count() == 0);

    // id 0 is never added.
    sel.addToSelection({0});
    REQUIRE(spy.count() == 0);
    REQUIRE_FALSE(sel.isSelected(0));
    REQUIRE(sel.size() == 3);
}

TEST_CASE("removeFromSelection clears active when the active id is removed",
          "[selection]") {
    ensureQApp();
    SelectionState sel;
    sel.setSelection({1, 2, 3}, /*active=*/2);

    QSignalSpy spy(&sel, &SelectionState::changed);

    // Removing a non-active id keeps the active id.
    sel.removeFromSelection({1});
    REQUIRE(spy.count() == 1);
    REQUIRE(sel.size() == 2);
    REQUIRE(sel.activeObjectId() == 2);

    // Removing the active id drops the active.
    sel.removeFromSelection({2});
    REQUIRE(spy.count() == 2);
    REQUIRE(sel.activeObjectId() == 0);
    REQUIRE(sel.isSelected(3));

    // Removing something absent -> no signal.
    sel.removeFromSelection({99});
    REQUIRE(spy.count() == 2);
}

TEST_CASE("toggleInSelection adds-as-active then removes-and-clears-active",
          "[selection]") {
    ensureQApp();
    SelectionState sel;
    QSignalSpy spy(&sel, &SelectionState::changed);

    sel.toggleInSelection(5);            // add
    REQUIRE(sel.isSelected(5));
    REQUIRE(sel.activeObjectId() == 5);  // last-toggled becomes active

    sel.toggleInSelection(6);            // add — active follows the click
    REQUIRE(sel.isSelected(6));
    REQUIRE(sel.activeObjectId() == 6);

    sel.toggleInSelection(5);            // remove non-active — active unchanged
    REQUIRE_FALSE(sel.isSelected(5));
    REQUIRE(sel.activeObjectId() == 6);

    sel.toggleInSelection(6);            // remove the active — active cleared
    REQUIRE(sel.empty());
    REQUIRE(sel.activeObjectId() == 0);

    REQUIRE(spy.count() == 4);

    // id 0 is never toggled.
    spy.clear();
    sel.toggleInSelection(0);
    REQUIRE(spy.count() == 0);
    REQUIRE(sel.empty());
}

TEST_CASE("clearSelection empties the set; no-op when already empty",
          "[selection]") {
    ensureQApp();
    SelectionState sel;
    QSignalSpy spy(&sel, &SelectionState::changed);

    sel.clearSelection();                // already empty
    REQUIRE(spy.count() == 0);

    sel.setSelectedObjectId(1);
    REQUIRE(spy.count() == 1);
    sel.clearSelection();
    REQUIRE(spy.count() == 2);
    REQUIRE(sel.empty());
    REQUIRE(sel.activeObjectId() == 0);
}

TEST_CASE("reset clears state and emits only when state existed", "[selection]") {
    ensureQApp();
    SelectionState sel;
    QSignalSpy spy(&sel, &SelectionState::changed);

    sel.reset();                         // nothing to clear
    REQUIRE(spy.count() == 0);

    sel.setSelectedObjectId(7);
    REQUIRE(spy.count() == 1);
    sel.reset();
    REQUIRE(spy.count() == 2);
    REQUIRE(sel.empty());
    REQUIRE(sel.activeObjectId() == 0);
}
