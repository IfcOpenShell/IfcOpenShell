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

#include "View.h"

#include "Panel.h"

#include "../../ElementRegistry.h"
#include "../../SessionState.h"

#include "element.h"  // helpers: get_predefined_type

namespace bonsaiviewer::modules::properties {

PropertiesPanelView::PropertiesPanelView(PropertiesPanel* widget,
                                         bonsaiviewer::SessionState* session_state,
                                         QObject* parent)
    : QObject(parent), widget_(widget), session_state_(session_state)
{
    connect(session_state_, &bonsaiviewer::SessionState::selectionChanged, this, [this](uint32_t object_id) {
        // A deselect (click on empty space → object_id 0) leaves the panel
        // showing the last active object rather than resetting to the empty
        // placeholder. Project reset/open below still clear it explicitly.
        if (object_id == 0) return;
        refresh(object_id);
    });
    connect(session_state_, &bonsaiviewer::SessionState::projectReset, this, [this]() {
        refresh(0);
    });
    connect(session_state_, &bonsaiviewer::SessionState::projectOpened, this, [this](const QString&) {
        refresh(0);
    });
    refresh(0);
}

void PropertiesPanelView::refresh(uint32_t object_id) {
    auto* registry = session_state_->elementRegistry();
    PropertiesPanelState state;
    state.entity = {"IfcWall", "SOLIDWALL"};
    state.attributes = {
        {"GlobalId", "2Q$n5SLPP9Q8B7wQKjKfUQ"},
        {"Name", "Core-EXT-204"},
        {"Description", "External load-bearing wall"},
    };
    state.relationships = {
        {"Type", "Basic Wall: Exterior - 200mm"},
        {"Container", "Level 02"},
    };
    state.property_sets = {
        {"Pset_WallCommon",
         {{"Reference", "Core-EXT-204"},
          {"Status", "Reviewed"},
          {"Fire Rating", "120 min"},
          {"LoadBearing", "True"}}},
        {"Identity Data",
         {{"Type", "IfcWall"},
          {"Name", "Core-EXT-204"},
          {"Owner", "Architecture"},
          {"Phase", "Construction"}}},
        {"BIM Collaboration",
         {{"Issue Count", "2 open"},
          {"Last Review", "2026-04-30"},
          {"Assigned To", "Design Coordination"}}},
    };
    state.quantity_sets = {
        {"BaseQuantities",
         {{"Length", "6.20 m"},
          {"Height", "3.45 m"},
          {"Width", "0.30 m"},
          {"Volume", "6.42 m3"}}},
        {"Finish Quantities",
         {{"NetSideArea", "21.39 m2"},
          {"GrossArea", "22.10 m2"},
          {"Paint Coverage", "42.78 m2"}}},
    };

    if (!registry) {
        widget_->render(state);
        return;
    }

    // A real project is loaded — don't leak the placeholder attributes /
    // relationships / predefined type. They're populated below from live IFC
    // data, or from the cached basics for geometry-only elements.
    state.entity.predefined_type.clear();
    state.attributes.clear();
    state.relationships.clear();

    auto entity = registry->findEntity(object_id);
    if (entity) {
        state.entity.entity_class = QString::fromStdString(entity->declaration().name());
        if (auto predefined_type = get_predefined_type(*entity)) {
            state.entity.predefined_type = QString::fromStdString(*predefined_type);
        }
        // Direct EXPRESS attributes, primitives only — lists / entity refs omitted.
        for (const auto& [name, value] : get_scalar_attributes(*entity)) {
            state.attributes.append({QString::fromStdString(name), QString::fromStdString(value)});
        }
        // Relationships: the construction type and the spatial container, shown
        // by name (falling back to the entity class when unnamed).
        auto display_name = [](const express::Base& related) -> QString {
            if (auto name = get_string_attribute(related, "Name"); name && !name->empty()) {
                return QString::fromStdString(*name);
            }
            return QString::fromStdString(related.declaration().name());
        };
        if (express::Base type = get_type(*entity)) {
            state.relationships.append({"Type", display_name(type)});
        }
        if (express::Base container = get_container(*entity)) {
            state.relationships.append({"Container", display_name(container)});
        }
        if (!state.property_sets.isEmpty() && !state.property_sets[1].rows.isEmpty()) {
            state.property_sets[1].rows[0].value = state.entity.entity_class;
        }
    } else {
        // No live IFC source for this object — typical when a pure-geometry
        // .ifcview sidecar was loaded without its .ifc/.rdb sibling.  Fall back
        // to the basic info cached in the element registry so the panel still
        // shows class / GlobalId / Name for visible elements.
        auto info = registry->findBasicElementInfo(object_id);
        if (info && !info->type.isEmpty()) {
            state.entity.entity_class = info->type;
            // Geometry only — no live IFC entity to read a predefined type from.
            state.entity.predefined_type = "N/A";
            if (!state.property_sets.isEmpty() && !state.property_sets[1].rows.isEmpty()) {
                state.property_sets[1].rows[0].value = info->type;
            }
        }
        if (info && !info->guid.isEmpty()) {
            state.attributes.append({"GlobalId", info->guid});
        }
        if (info && !info->name.isEmpty()) {
            state.attributes.append({"Name", info->name});
        }
    }
    widget_->render(state);
}

} // namespace bonsaiviewer::modules::properties
