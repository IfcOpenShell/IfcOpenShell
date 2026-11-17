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

#include "DisplayState.h"

#include "../../ElementRegistry.h"
#include "../../SessionState.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"
#include "../../../ifcparse/express.h"
#include "../../../ifcparse/file.h"
#include "element.h"  // helpers: get_predefined_type, get_string_attribute

#include <algorithm>

namespace bonsaiviewer::modules::display {

namespace {

constexpr int kSlotCount = 3;

const char* kCategoryIfcTypes[] = {
    "IfcWall",           // Walls (includes IfcWallStandardCase)
    "IfcSlab",           // Slabs
    "IfcRoof",           // Roofs
    "IfcCovering",       // Ceilings (predefined type CEILING)
    "IfcSpace",          // Spaces
    "IfcOpeningElement", // Openings (reservations)
};

} // namespace

DisplayState::DisplayState(SessionState* session_state, QObject* parent)
    : QObject(parent), session_state_(session_state)
{
    // Spaces and Openings start DISABLED (decided): they are hidden at every
    // model load until the user enables them in the Categories menu.
    categories_[static_cast<int>(Category::Spaces)].enabled = false;
    categories_[static_cast<int>(Category::Reservations)].enabled = false;
}

// ---- Box -----------------------------------------------------------------

void DisplayState::replaceBoxWithSelection(ViewportWindow& viewport) {
    std::set<uint32_t> ids(viewport.selection().selectionIds().begin(),
                           viewport.selection().selectionIds().end());
    purgeRemovedObjects();
    box_current_ = std::move(ids);
    emit boxChanged();
}

void DisplayState::addSelectionToBox(ViewportWindow& viewport) {
    purgeRemovedObjects();
    for (uint32_t id : viewport.selection().selectionIds()) box_current_.insert(id);
    emit boxChanged();
}

void DisplayState::removeSelectionFromBox(ViewportWindow& viewport) {
    for (uint32_t id : viewport.selection().selectionIds()) box_current_.erase(id);
    emit boxChanged();
}

bool DisplayState::saveBoxToSlot(int slot) {
    if (slot < 1 || slot > kSlotCount) return false;
    purgeRemovedObjects();
    if (box_current_.empty()) return false;
    box_slots_[slot - 1] = box_current_;
    return true;
}

std::vector<uint32_t> DisplayState::boxSlotIds(int slot) const {
    if (slot < 1 || slot > kSlotCount) return {};
    return {box_slots_[slot - 1].begin(), box_slots_[slot - 1].end()};
}

bool DisplayState::boxSlotEmpty(int slot) const {
    if (slot < 1 || slot > kSlotCount) return true;
    return box_slots_[slot - 1].empty();
}

void DisplayState::purgeRemovedObjects() {
    const auto* registry = session_state_->elementRegistry();
    if (registry == nullptr) {
        box_current_.clear();
        for (auto& slot : box_slots_) slot.clear();
        appearances_.clear();
        emit boxChanged();
        return;
    }
    const auto is_known = [registry](uint32_t id) {
        return registry->findBasicElementInfo(id).has_value();
    };
    std::set<uint32_t> known;
    for (uint32_t id : box_current_) if (is_known(id)) known.insert(id);
    box_current_ = std::move(known);
    for (auto& slot : box_slots_) {
        std::set<uint32_t> slot_known;
        for (uint32_t id : slot) if (is_known(id)) slot_known.insert(id);
        slot = std::move(slot_known);
    }
    for (auto it = appearances_.begin(); it != appearances_.end();) {
        if (is_known(it->first)) ++it;
        else it = appearances_.erase(it);
    }
    emit boxChanged();
}

// ---- Category filters -------------------------------------------------------

bool DisplayState::categoryShown(Category category) const {
    return categories_[static_cast<int>(category)].shown;
}

void DisplayState::setCategoryShown(Category category, bool shown, ViewportWindow& viewport) {
    categories_[static_cast<int>(category)].shown = shown;
    // Scoped re-apply: only the affected category, so toggling walls doesn't
    // disturb an isolation the user built with another tool.
    const auto* registry = session_state_->elementRegistry();
    if (registry == nullptr) return;
    for (uint32_t session_model_id : session_state_->sessionModelIds()) {
        const std::vector<uint32_t> ids = categoryIdsForModel(session_model_id, category);
        if (ids.empty()) continue;
        const bool effective = shown && categoryEnabled(category);
        viewport.setObjectsVisible(ids, effective);
    }
    emit categoriesChanged();
}

bool DisplayState::categoryEnabled(Category category) const {
    return categories_[static_cast<int>(category)].enabled;
}

void DisplayState::setCategoryEnabled(Category category, bool enabled, ViewportWindow& viewport) {
    if (category != Category::Spaces && category != Category::Reservations) return;
    categories_[static_cast<int>(category)].enabled = enabled;
    // Scoped re-apply: only the affected category. Applying every filter
    // here would re-show elements hidden by other means (isolation, Hide
    // Selection, …) — "Enable/Disable must not re-show everything".
    const auto* registry = session_state_->elementRegistry();
    if (registry == nullptr) return;
    for (uint32_t session_model_id : session_state_->sessionModelIds()) {
        const std::vector<uint32_t> ids = categoryIdsForModel(session_model_id, category);
        if (ids.empty()) continue;
        viewport.setObjectsVisible(ids, categoryShown(category) && enabled);
    }
    emit categoriesChanged();
}

void DisplayState::applyAllCategoryFilters(ViewportWindow& viewport) {
    for (uint32_t session_model_id : session_state_->sessionModelIds()) {
        applyCategoryFiltersForModel(session_model_id, viewport);
    }
}

void DisplayState::applyCategoryFiltersForModel(uint32_t session_model_id, ViewportWindow& viewport) {
    for (int i = 0; i <= static_cast<int>(Category::Reservations); ++i) {
        const auto category = static_cast<Category>(i);
        const std::vector<uint32_t> ids = categoryIdsForModel(session_model_id, category);
        if (ids.empty()) continue;
        viewport.setObjectsVisible(ids, categoryShown(category) && categoryEnabled(category));
    }
}

std::vector<uint32_t> DisplayState::shownableIds(const std::vector<uint32_t>& object_ids) const {
    // Fast path: only Spaces / Openings carry the enable toggle.
    if (categoryEnabled(Category::Spaces) && categoryEnabled(Category::Reservations)) {
        return object_ids;
    }
    std::set<uint32_t> disabled_ids;
    for (uint32_t session_model_id : session_state_->sessionModelIds()) {
        if (!categoryEnabled(Category::Spaces)) {
            for (uint32_t id : categoryIdsForModel(session_model_id, Category::Spaces)) {
                disabled_ids.insert(id);
            }
        }
        if (!categoryEnabled(Category::Reservations)) {
            for (uint32_t id : categoryIdsForModel(session_model_id, Category::Reservations)) {
                disabled_ids.insert(id);
            }
        }
    }
    std::vector<uint32_t> result;
    result.reserve(object_ids.size());
    for (uint32_t id : object_ids) {
        if (disabled_ids.count(id) == 0) result.push_back(id);
    }
    return result;
}

std::vector<uint32_t> DisplayState::categoryIdsForModel(uint32_t session_model_id, Category category) const {
    const auto* registry = session_state_->elementRegistry();
    auto* loader = session_state_->loader();
    if (registry == nullptr || loader == nullptr) return {};
    ifcopenshell::file* file = loader->ifcFile(session_model_id);
    if (file == nullptr) return {};

    // ifc_id -> object_id for this model, from the registry's element table.
    std::map<int, uint32_t> id_map;
    for (const auto& info : registry->basicElementInfoForModel(session_model_id)) {
        id_map.emplace(info.ifc_id, info.object_id);
    }
    if (id_map.empty()) return {};

    const char* ifc_type = kCategoryIfcTypes[static_cast<int>(category)];
    std::vector<uint32_t> result;
    try {
        for (const auto& instance : file->instances_by_type(ifc_type)) {
            const auto it = id_map.find(static_cast<int>(instance.id()));
            if (it == id_map.end()) continue;
            if (category == Category::Ceilings) {
                // IfcCovering restricted to the CEILING predefined type.
                // IFC4+ stores it in PredefinedType (get_predefined_type);
                // IFC2x3 names the attribute CoveringType, so fall back to
                // it before giving up.
                auto predefined = get_predefined_type(instance);
                if (!predefined) {
                    predefined = get_string_attribute(instance, "CoveringType");
                }
                if (!predefined || *predefined != "CEILING") continue;
            }
            result.push_back(it->second);
        }
    } catch (...) {
        return {};
    }
    return result;
}

QString DisplayState::categoryIfcType(Category category) {
    return QString::fromLatin1(kCategoryIfcTypes[static_cast<int>(category)]);
}

// ---- Manual appearance -------------------------------------------------------

uint32_t DisplayState::packOverride(const std::optional<QColor>& color, std::optional<int> opacity) const {
    const int alpha = opacity.has_value()
        ? std::clamp((*opacity * 255 + 50) / 100, 0, 255)
        : 255;
    if (!color.has_value()) {
        // Alpha-only override sentinel (R=G=B=1): the shader keeps the baked
        // colour and replaces only the alpha. See MAIN_WGSL in ViewportCore.
        return (static_cast<uint32_t>(alpha) << 24) | 0x00010101u;
    }
    return (static_cast<uint32_t>(alpha) << 24)
         | (static_cast<uint32_t>(color->blue())  << 16)
         | (static_cast<uint32_t>(color->green()) << 8)
         |  static_cast<uint32_t>(color->red());
}

void DisplayState::applyColor(const std::vector<uint32_t>& object_ids, const QColor& color, ViewportWindow& viewport) {
    for (uint32_t id : object_ids) appearances_[id].color = color;
    // The colour is uniform; group by the per-object opacity so each group
    // gets one setObjectsColor call with the correct composed override.
    std::map<std::optional<int>, std::vector<uint32_t>> by_opacity;
    for (uint32_t id : object_ids) by_opacity[appearances_[id].opacity].push_back(id);
    for (const auto& [opacity, ids] : by_opacity) {
        viewport.setObjectsColor(ids, packOverride(color, opacity));
    }
}

void DisplayState::resetColor(const std::vector<uint32_t>& object_ids, ViewportWindow& viewport) {
    for (uint32_t id : object_ids) {
        auto it = appearances_.find(id);
        if (it != appearances_.end()) it->second.color = std::nullopt;
    }
    std::map<std::optional<int>, std::vector<uint32_t>> by_opacity;
    for (uint32_t id : object_ids) {
        auto it = appearances_.find(id);
        if (it == appearances_.end()) continue;
        by_opacity[it->second.opacity].push_back(id);
    }
    for (const auto& [opacity, ids] : by_opacity) {
        viewport.setObjectsColor(ids, packOverride(std::nullopt, opacity));
    }
    // Objects with no opacity left have no override at all.
    for (uint32_t id : object_ids) {
        auto it = appearances_.find(id);
        if (it != appearances_.end() && !it->second.color && !it->second.opacity) {
            appearances_.erase(it);
            viewport.setObjectsColor({id}, 0u);
        }
    }
}

void DisplayState::applyOpacity(const std::vector<uint32_t>& object_ids, int opacity_percent, ViewportWindow& viewport) {
    const std::optional<int> opacity =
        (opacity_percent >= 100) ? std::nullopt : std::optional<int>(opacity_percent);
    for (uint32_t id : object_ids) appearances_[id].opacity = opacity;
    // QColor is not orderable; group by its QRgb key instead.
    std::map<uint32_t, std::vector<uint32_t>> by_color;
    std::vector<uint32_t> without_color;
    for (uint32_t id : object_ids) {
        const auto& appearance = appearances_[id];
        if (appearance.color.has_value()) by_color[appearance.color->rgba()].push_back(id);
        else without_color.push_back(id);
    }
    for (const auto& [rgba, ids] : by_color) {
        viewport.setObjectsColor(ids, packOverride(QColor::fromRgba(rgba), opacity));
    }
    if (!without_color.empty()) {
        viewport.setObjectsColor(without_color, packOverride(std::nullopt, opacity));
    }
    // Fully-opaque objects with no colour left have no override at all.
    for (uint32_t id : object_ids) {
        auto it = appearances_.find(id);
        if (it != appearances_.end() && !it->second.color && !it->second.opacity) {
            appearances_.erase(it);
            viewport.setObjectsColor({id}, 0u);
        }
    }
}

void DisplayState::resetManualAppearances() {
    appearances_.clear();
}

} // namespace bonsaiviewer::modules::display
