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

#ifndef WGPUVISIBILITYSTATE_H
#define WGPUVISIBILITYSTATE_H

#include <cstdint>
#include <unordered_set>

// CPU-side per-element visibility. Mirrors src/ifcviewer/Visibility.h shape
// but pure stdlib so it can move into ifcviewer-core later.
//
// Consulted in cullModelCpuCompute: instances whose object_id is in
// hidden_ids_ are dropped from the visible-draws list entirely (no GPU
// work, no triangle in the depth buffer, no pick hit). Concurrent reads
// from multiple cull worker threads are safe as long as no mutations
// happen during render — which is the case here (input handlers
// requestUpdate after mutating, render then reads).
class VisibilityState {
public:
    bool isHidden(uint32_t object_id) const {
        return hidden_ids_.count(object_id) > 0;
    }

    void hide(uint32_t object_id) {
        if (object_id == 0) return;
        hidden_ids_.insert(object_id);
    }

    void show(uint32_t object_id) {
        hidden_ids_.erase(object_id);
    }

    void clear() { hidden_ids_.clear(); }

    size_t hiddenCount() const { return hidden_ids_.size(); }
    const std::unordered_set<uint32_t>& hiddenIds() const { return hidden_ids_; }

private:
    std::unordered_set<uint32_t> hidden_ids_;
};

#endif // WGPUVISIBILITYSTATE_H
