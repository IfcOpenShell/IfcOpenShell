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

#ifndef IFCVIEWER_VISIBILITY_H
#define IFCVIEWER_VISIBILITY_H

#include <QObject>

#include <cstdint>
#include <unordered_set>
#include <vector>

// Per-element visibility state, owned by ViewportWindow.  Independent of
// the per-model `hidden` flag — model-level hiding still wins (a hidden
// model never draws regardless of its elements' visibility).  This class
// only tracks element-level overrides on top.
//
// Lookup is hot — the CPU cull queries `isHidden(object_id)` for every
// surviving instance — so the canonical set is mirrored into a flat
// per-id byte vector indexed directly by object_id.  Ownership is purely
// CPU: nothing on the GPU reads visibility, the cull just skips hidden
// instances before they reach the visible[] SSBO.
class VisibilityState : public QObject {
    Q_OBJECT
public:
    explicit VisibilityState(QObject* parent = nullptr);

    // Tell the manager about a newly added object_id so the flag vector
    // can grow ahead of the next cull.  Cheap when the id fits already.
    void noteObjectId(uint32_t id);

    // Drop everything — clears the hidden set.  Called from clearScene.
    void reset();

    // ---- Mutation ----
    //
    // hideObjects: union into the hidden set.
    // showObjects: subtract from the hidden set.
    // setHidden:   replace the hidden set wholesale (used by isolate).
    // showAll:     equivalent to setHidden({}).
    void hideObjects(const std::unordered_set<uint32_t>& ids);
    void showObjects(const std::unordered_set<uint32_t>& ids);
    void setHidden(const std::unordered_set<uint32_t>& ids);
    void showAll();

    // ---- Hot-path query ----
    //
    // Inline so the cull's `if (visibility_.isHidden(...)) return;`
    // compiles to a bounds check + a byte load + a compare.
    bool isHidden(uint32_t id) const {
        return id < cpu_flags_.size() && cpu_flags_[id] != 0;
    }

    // ---- Accessors ----
    bool empty() const { return hidden_ids_.empty(); }
    size_t size() const { return hidden_ids_.size(); }
    const std::unordered_set<uint32_t>& hiddenIds() const { return hidden_ids_; }

signals:
    // Emitted on any mutation that changes the hidden set.  Consumers
    // (the viewport) connect to invalidate cached cull state and
    // requestUpdate.
    void changed();

private:
    // Recompute cpu_flags_ from hidden_ids_.  Cheap: O(|cpu_flags_|).
    void rebuildFlags();

    std::unordered_set<uint32_t> hidden_ids_;
    std::vector<uint8_t>         cpu_flags_;
};

#endif // IFCVIEWER_VISIBILITY_H
