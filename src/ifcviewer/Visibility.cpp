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

#include "Visibility.h"

#include <algorithm>

VisibilityState::VisibilityState(QObject* parent) : QObject(parent) {
    // Slot 0 is the "no object" sentinel; keep it present so isHidden(0)
    // is well-defined (returns false).
    cpu_flags_.assign(1, 0u);
}

void VisibilityState::noteObjectId(uint32_t id) {
    if (id == 0) return;
    if (uint32_t(cpu_flags_.size()) <= id) {
        cpu_flags_.resize(size_t(id) + 1, 0u);
    }
}

void VisibilityState::reset() {
    const bool had_state = !hidden_ids_.empty();
    hidden_ids_.clear();
    std::fill(cpu_flags_.begin(), cpu_flags_.end(), 0u);
    if (had_state) emit changed();
}

void VisibilityState::hideObjects(const std::unordered_set<uint32_t>& ids) {
    bool any = false;
    for (uint32_t id : ids) {
        if (id == 0) continue;
        if (hidden_ids_.insert(id).second) {
            if (uint32_t(cpu_flags_.size()) <= id) {
                cpu_flags_.resize(size_t(id) + 1, 0u);
            }
            cpu_flags_[id] = 1u;
            any = true;
        }
    }
    if (any) emit changed();
}

void VisibilityState::showObjects(const std::unordered_set<uint32_t>& ids) {
    bool any = false;
    for (uint32_t id : ids) {
        if (hidden_ids_.erase(id) > 0) {
            if (id < cpu_flags_.size()) cpu_flags_[id] = 0u;
            any = true;
        }
    }
    if (any) emit changed();
}

void VisibilityState::setHidden(const std::unordered_set<uint32_t>& ids) {
    if (ids == hidden_ids_) return;
    hidden_ids_ = ids;
    hidden_ids_.erase(0);
    rebuildFlags();
    emit changed();
}

void VisibilityState::showAll() {
    if (hidden_ids_.empty()) return;
    hidden_ids_.clear();
    std::fill(cpu_flags_.begin(), cpu_flags_.end(), 0u);
    emit changed();
}

void VisibilityState::rebuildFlags() {
    std::fill(cpu_flags_.begin(), cpu_flags_.end(), 0u);
    for (uint32_t id : hidden_ids_) {
        if (uint32_t(cpu_flags_.size()) <= id) {
            cpu_flags_.resize(size_t(id) + 1, 0u);
        }
        cpu_flags_[id] = 1u;
    }
}
