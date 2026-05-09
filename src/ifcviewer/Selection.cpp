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

#include "Selection.h"

#include <algorithm>

SelectionState::SelectionState(QObject* parent) : QObject(parent) {
    // Reserve slot 0 — object_id 0 is the "no object" sentinel and the
    // shader still indexes the buffer with v_object_id, so the slot must
    // exist (and be zero) to avoid OOB reads.
    cpu_flags_.assign(1, 0u);
}

SelectionState::~SelectionState() = default;

void SelectionState::initializeGl(QOpenGLFunctions_4_5_Core* gl) {
    gl_ = gl;
    if (ssbo_ == 0) {
        gl_->glCreateBuffers(1, &ssbo_);
    }
    // Force a fresh upload against the new context.
    dirty_ = true;
}

void SelectionState::releaseGl() {
    if (gl_ && ssbo_) {
        gl_->glDeleteBuffers(1, &ssbo_);
    }
    ssbo_ = 0;
    ssbo_capacity_slots_ = 0;
    gl_ = nullptr;
    dirty_ = true;
}

void SelectionState::reset() {
    const bool had_state = !selected_ids_.empty() || active_id_ != 0;
    selected_ids_.clear();
    active_id_ = 0;
    std::fill(cpu_flags_.begin(), cpu_flags_.end(), 0u);
    markDirty();
    if (had_state) emit changed(active_id_);
}

void SelectionState::noteObjectId(uint32_t id) {
    if (id == 0) return;
    if (uint32_t(cpu_flags_.size()) <= id) {
        // Grow CPU side; the SSBO is sized lazily inside uploadFlags so
        // we don't realloc GL on every streamed instance.
        cpu_flags_.resize(size_t(id) + 1, 0u);
        markDirty();
    }
}

void SelectionState::setSelectedObjectId(uint32_t id) {
    if (id == 0) {
        clearSelection();
        return;
    }
    setSelection({id}, id);
}

void SelectionState::setSelection(const std::unordered_set<uint32_t>& ids,
                                  uint32_t active) {
    // Avoid emitting churn when the call is a no-op.
    if (ids == selected_ids_ && active == active_id_) return;
    selected_ids_ = ids;
    selected_ids_.erase(0);
    active_id_ = (active != 0 && selected_ids_.count(active)) ? active : 0u;
    markDirty();
    emit changed(active_id_);
}

void SelectionState::addToSelection(const std::unordered_set<uint32_t>& ids) {
    bool any_added = false;
    for (uint32_t id : ids) {
        if (id == 0) continue;
        if (selected_ids_.insert(id).second) any_added = true;
    }
    if (!any_added) return;
    markDirty();
    emit changed(active_id_);
}

void SelectionState::removeFromSelection(const std::unordered_set<uint32_t>& ids) {
    bool any_removed = false;
    bool active_removed = false;
    for (uint32_t id : ids) {
        if (selected_ids_.erase(id) > 0) {
            any_removed = true;
            if (id == active_id_) active_removed = true;
        }
    }
    if (!any_removed) return;
    if (active_removed) active_id_ = 0;
    markDirty();
    emit changed(active_id_);
}

void SelectionState::toggleInSelection(uint32_t id) {
    if (id == 0) return;
    if (selected_ids_.erase(id) > 0) {
        // Removed.  If it was active, drop active.
        if (active_id_ == id) active_id_ = 0;
    } else {
        // Added.  Last-toggled becomes active so the properties panel
        // tracks the most recent click — matches the user's "last single
        // clicked is active" expectation.
        selected_ids_.insert(id);
        active_id_ = id;
    }
    markDirty();
    emit changed(active_id_);
}

void SelectionState::clearSelection() {
    if (selected_ids_.empty() && active_id_ == 0) return;
    selected_ids_.clear();
    active_id_ = 0;
    markDirty();
    emit changed(active_id_);
}

void SelectionState::markDirty() {
    dirty_ = true;
}

void SelectionState::growTo(uint32_t capacity_ids) {
    if (!gl_ || ssbo_ == 0) return;
    if (capacity_ids <= ssbo_capacity_slots_) return;
    // Round up to a power-of-two-ish step so streamed scenes don't realloc
    // every few instances.  Floor at 1024 slots = 4 KB.
    size_t new_cap = std::max<size_t>(1024, ssbo_capacity_slots_ * 2);
    while (new_cap < capacity_ids) new_cap *= 2;
    gl_->glNamedBufferData(ssbo_,
                           GLsizeiptr(new_cap * sizeof(uint32_t)),
                           nullptr, GL_DYNAMIC_DRAW);
    ssbo_capacity_slots_ = new_cap;
}

void SelectionState::uploadFlags() {
    if (!gl_ || ssbo_ == 0) return;

    // Rebuild the CPU flag vector from the canonical selected_ids_.  The
    // overhead is O(|cpu_flags_|), which scales with max object_id rather
    // than with selection size — acceptable: object_ids are dense so this
    // is just a memset + a handful of writes for the selected set.
    std::fill(cpu_flags_.begin(), cpu_flags_.end(), 0u);
    for (uint32_t id : selected_ids_) {
        if (id < cpu_flags_.size()) cpu_flags_[id] = 1u;
    }

    growTo(static_cast<uint32_t>(cpu_flags_.size()));
    if (ssbo_capacity_slots_ == 0) return;

    const GLsizeiptr bytes =
        GLsizeiptr(cpu_flags_.size() * sizeof(uint32_t));
    if (bytes > 0) {
        gl_->glNamedBufferSubData(ssbo_, 0, bytes, cpu_flags_.data());
    }
    dirty_ = false;
}

void SelectionState::bindForRender(GLuint binding_index) {
    if (!gl_ || ssbo_ == 0) return;
    if (dirty_) uploadFlags();
    gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding_index, ssbo_);
}
