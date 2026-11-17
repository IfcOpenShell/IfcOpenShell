// This file was generated with the assistance of an AI coding tool.
/********************************************************************************
 *                                                                              *
 * This file is part of Bonsai.                                                 *
 *                                                                              *
 * Bonsai is free software: you can redistribute it and/or modify               *
 * it under the terms of the GNU General Public License as published by         *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * Bonsai is distributed in the hope that it will be useful,                    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * GNU General Public License for more details.                                 *
 *                                                                              *
 * You should have received a copy of the GNU General Public License            *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCINTERFACE_MODULES_DISPLAY_DISPLAYSTATE_H
#define IFCINTERFACE_MODULES_DISPLAY_DISPLAYSTATE_H

#include <QColor>
#include <QObject>
#include <QString>

#include <cstdint>
#include <map>
#include <optional>
#include <set>
#include <vector>

class ViewportWindow;

namespace bonsaiviewer {
class SessionState;

namespace modules::display {

// Session state for the "Display" ribbon tab: the Box (temporary object
// set + 3 save slots), per-category visibility filters, and manual
// colour/transparency overrides. Everything here is session-only — nothing is
// persisted. See SPEC_Viewer.md.
class DisplayState : public QObject {
    Q_OBJECT

public:
    explicit DisplayState(SessionState* session_state, QObject* parent = nullptr);

    // ---- Box ------------------------------------------------------------
    // The current box is a temporary set of object ids. Slots 1..3 copy it.
    void replaceBoxWithSelection(ViewportWindow& viewport);
    void addSelectionToBox(ViewportWindow& viewport);
    void removeSelectionFromBox(ViewportWindow& viewport);
    const std::set<uint32_t>& currentBox() const { return box_current_; }
    bool saveBoxToSlot(int slot);          // slot 1..3; false when the box is empty
    std::vector<uint32_t> boxSlotIds(int slot) const;   // slot 1..3
    bool boxSlotEmpty(int slot) const;
    // Drops ids the ElementRegistry no longer knows (model closed / project
    // reset) from the current box, the slots, and the appearance map.
    void purgeRemovedObjects();

    // ---- Category filters --------------------------------------------------
    enum class Category { Walls, Slabs, Roofs, Ceilings, Spaces, Reservations };

    // "Show/Hide <category>": immediate, temporary visual effect.
    bool categoryShown(Category category) const;
    void setCategoryShown(Category category, bool shown, ViewportWindow& viewport);
    // "Enable/Disable": durable session toggle applied at each model load.
    // Only meaningful for Spaces and Reservations; other categories report
    // true and ignore writes.
    bool categoryEnabled(Category category) const;
    void setCategoryEnabled(Category category, bool enabled, ViewportWindow& viewport);
    // Re-applies every category filter (all loaded models).
    void applyAllCategoryFilters(ViewportWindow& viewport);
    // Re-applies the filters for one model — call on model load.
    void applyCategoryFiltersForModel(uint32_t session_model_id, ViewportWindow& viewport);
    // Elements of a disabled category can NEVER be shown, whatever the path
    // (show selection, box/search isolation, …) while the deactivation is
    // active. Every show/isolate path filters its ids through this.
    std::vector<uint32_t> shownableIds(const std::vector<uint32_t>& object_ids) const;

    static QString categoryIfcType(Category category);

    // ---- Manual appearance --------------------------------------------------
    // Colour and opacity are independent: the app remembers both per object
    // and composes them into the single per-instance GPU override.
    void applyColor(const std::vector<uint32_t>& object_ids, const QColor& color, ViewportWindow& viewport);
    // Back to the colour baked at load ("Remove Color"); opacity stays.
    void resetColor(const std::vector<uint32_t>& object_ids, ViewportWindow& viewport);
    // opacity_percent: 100 = opaque (restores original), 75/50/25.
    void applyOpacity(const std::vector<uint32_t>& object_ids, int opacity_percent, ViewportWindow& viewport);
    // Model reload/close: fresh instance records carry no overrides.
    void resetManualAppearances();

signals:
    void boxChanged();
    void categoriesChanged();

private:
    struct CategoryConfig {
        bool shown   = true;
        bool enabled = true;
    };

    std::vector<uint32_t> categoryIdsForModel(uint32_t session_model_id, Category category) const;
    uint32_t packOverride(const std::optional<QColor>& color, std::optional<int> opacity) const;

    SessionState* session_state_ = nullptr;
    std::set<uint32_t> box_current_;
    std::set<uint32_t> box_slots_[3];
    CategoryConfig categories_[6];
    // object_id -> manual appearance. Colour nullopt = baked colour; opacity
    // nullopt = baked alpha.
    struct Appearance {
        std::optional<QColor> color;
        std::optional<int> opacity;
    };
    std::map<uint32_t, Appearance> appearances_;
};

} // namespace bonsaiviewer::modules::display

} // namespace bonsaiviewer

#endif
