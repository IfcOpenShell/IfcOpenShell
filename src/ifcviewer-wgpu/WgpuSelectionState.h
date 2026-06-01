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

#ifndef WGPUSELECTIONSTATE_H
#define WGPUSELECTIONSTATE_H

#include <cstdint>
#include <unordered_set>
#include <vector>

// CPU-side selection tracking. Mirrors src/ifcviewer/Selection.h shape but
// without Qt deps (kept pure stdlib so it can move into ifcviewer-core
// later without dragging Qt along).
//
// Two flavours of "selected":
//   - the multi-set (ids()): every object the user has Shift-added.
//   - active (activeId()): the *last* single-clicked object. UIs typically
//     use this to drive the properties panel; the renderer tints it
//     slightly more strongly than the rest of the multi-set.
//
// The GPU consumes a flat u32 array indexed by object_id: bit 0 = selected,
// bit 1 = active. Sized to (max_object_id + 1) by the caller.
class WgpuSelectionState {
public:
    void clear() {
        if (ids_.empty() && active_ == 0) return;
        ids_.clear();
        active_ = 0;
        dirty_ = true;
    }

    // Replace the selection with a single object. id == 0 clears.
    void replace(uint32_t id) {
        ids_.clear();
        if (id != 0) ids_.insert(id);
        active_ = id;
        dirty_ = true;
    }

    void add(uint32_t id) {
        if (id == 0) return;
        ids_.insert(id);
        active_ = id;
        dirty_ = true;
    }

    void remove(uint32_t id) {
        if (id == 0) return;
        if (ids_.erase(id) == 0) return;
        if (active_ == id) {
            active_ = ids_.empty() ? 0 : *ids_.begin();
        }
        dirty_ = true;
    }

    void toggle(uint32_t id) {
        if (id == 0) return;
        if (ids_.count(id)) remove(id);
        else                add(id);
    }

    bool contains(uint32_t id) const { return ids_.count(id) > 0; }
    uint32_t activeId() const         { return active_; }
    // Named selectionIds() rather than ids() so bonsai's
    // `viewport_->selection().selectionIds()` compiles unchanged.
    const std::unordered_set<uint32_t>& selectionIds() const { return ids_; }
    size_t count() const              { return ids_.size(); }

    bool dirty() const { return dirty_; }
    void markClean()   { dirty_ = false; }

    // Fill `out` (sized to entries u32s) with bit-packed flags:
    //   bit 0 = selected (in ids_), bit 1 = active. out[0] is always 0
    //   because object_id 0 is the "miss" sentinel.
    void fillFlagsArray(std::vector<uint32_t>& out, uint32_t entries) const {
        out.assign(entries, 0);
        for (uint32_t id : ids_) {
            if (id < entries) out[id] |= 1u;
        }
        if (active_ != 0 && active_ < entries) out[active_] |= 2u;
    }

private:
    std::unordered_set<uint32_t> ids_;
    uint32_t                     active_ = 0;
    bool                         dirty_  = false;
};

#endif // WGPUSELECTIONSTATE_H
