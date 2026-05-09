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

#ifndef IFCVIEWER_SELECTION_H
#define IFCVIEWER_SELECTION_H

#include <QObject>
#include <QtOpenGL/QOpenGLFunctions_4_5_Core>

#include <cstdint>
#include <unordered_set>
#include <vector>

// Multi-selection state for the viewport, owned by ViewportWindow.
//
// Tracks the *set* of currently selected object_ids plus a single "active"
// id — the last single-clicked one.  The active id is what the properties
// panel and tree mirror; the full set is what the viewport highlights.
//
// Selection state is published to the main shader through a per-object_id
// flags SSBO bound at a caller-chosen index (binding=3 today).  The buffer
// is sized to max(object_id) + 1 and grown on demand via noteObjectId,
// which the viewport calls for every appended instance.
//
// On every mutation the selection emits `changed(active_id)`.  Consumers
// (MainWindow, the viewport itself for requestUpdate) connect to it.
class SelectionState : public QObject {
    Q_OBJECT
public:
    explicit SelectionState(QObject* parent = nullptr);
    ~SelectionState() override;

    // Wire up the GL context.  Must be called once the viewport's GL
    // context is current.  release() drops GL resources before context
    // teardown.
    void initializeGl(QOpenGLFunctions_4_5_Core* gl);
    void releaseGl();

    // Tell the manager about a newly added object_id so the flag buffer
    // can grow ahead of the next render.  Cheap when the id fits in the
    // already-allocated CPU vector; otherwise resizes (and marks dirty).
    void noteObjectId(uint32_t id);

    // Clear everything — both the selection set and the per-object flags.
    // Called from clearScene.
    void reset();

    // ---- Mutation API ----
    //
    // Plain LMB click → setSelectedObjectId(id) (or clearSelection() for 0).
    // Modifier+click  → toggleInSelection(id).
    // Box-select on release → setSelection / addToSelection / removeFromSelection
    // depending on the modifier held when the drag started.
    //
    // setSelection's `active` should be in `ids` or 0; if it isn't, the
    // active is silently coerced to 0.

    void setSelectedObjectId(uint32_t id);
    void setSelection(const std::unordered_set<uint32_t>& ids, uint32_t active);
    void addToSelection(const std::unordered_set<uint32_t>& ids);
    void removeFromSelection(const std::unordered_set<uint32_t>& ids);
    void toggleInSelection(uint32_t id);
    void clearSelection();

    // ---- Accessors ----

    bool isSelected(uint32_t id) const { return selected_ids_.count(id) > 0; }
    bool empty() const { return selected_ids_.empty(); }
    size_t size() const { return selected_ids_.size(); }
    const std::unordered_set<uint32_t>& selectionIds() const { return selected_ids_; }
    uint32_t activeObjectId() const { return active_id_; }

    // ---- GL binding ----
    //
    // Bind the selection-flags SSBO at the given binding index for the
    // upcoming draw.  Lazily uploads any pending flag changes.  Caller
    // must have GL context current.
    void bindForRender(GLuint binding_index);

signals:
    // Emitted on any mutation that changes either the set or the active.
    // Carries the new active id for convenience (consumers usually only
    // care about the active for properties/tree sync).
    void changed(uint32_t active_id);

private:
    // Mark the SSBO dirty so the next bindForRender() re-uploads it.
    void markDirty();
    // Resize the CPU flag vector + GL buffer to hold up to capacity_ids
    // entries.  Called when noteObjectId outgrows the current capacity.
    void growTo(uint32_t capacity_ids);
    // Fully overwrite cpu_flags_ from selected_ids_, then upload to GL.
    void uploadFlags();

    QOpenGLFunctions_4_5_Core* gl_ = nullptr;

    std::unordered_set<uint32_t> selected_ids_;
    uint32_t active_id_ = 0;

    // Per-object_id flag, indexed by id directly (slot 0 unused — object_id 0
    // means "no object").  Bit 0 = selected.  Stored as uint32 per slot for
    // std430 alignment simplicity; the byte cost (~4 MB at 1M objects) is
    // negligible compared to the instance SSBO.
    std::vector<uint32_t> cpu_flags_;
    GLuint ssbo_                = 0;
    size_t ssbo_capacity_slots_ = 0;
    bool   dirty_               = true;
};

#endif // IFCVIEWER_SELECTION_H
