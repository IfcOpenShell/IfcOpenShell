// This file was generated with the assistance of an AI coding tool.
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

#include "View.h"

#include "Panel.h"

#include "../../ElementRegistry.h"
#include "../../SessionState.h"

namespace ifcviewerfull::modules::properties {

PropertiesPanelView::PropertiesPanelView(PropertiesPanel* widget,
                                         ifcviewerfull::SessionState* session_state,
                                         QObject* parent)
    : QObject(parent), widget_(widget), session_state_(session_state)
{
    connect(session_state_, &ifcviewerfull::SessionState::selectionChanged, this, [this](uint32_t object_id) {
        refresh(object_id);
    });
    connect(session_state_, &ifcviewerfull::SessionState::projectReset, this, [this]() {
        refresh(0);
    });
    connect(session_state_, &ifcviewerfull::SessionState::projectOpened, this, [this](const QString&) {
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

    auto entity = registry->findEntity(object_id);
    if (entity) {
        state.entity.entity_class = QString::fromStdString(entity->declaration().name());
        if (!state.property_sets.isEmpty() && !state.property_sets[1].rows.isEmpty()) {
            state.property_sets[1].rows[0].value = state.entity.entity_class;
        }
    } else {
        // No live IFC source for this object — typical when a pure-geometry
        // .ifcview sidecar was loaded without its .ifc/.rdb sibling.  Fall
        // back to the basic info cached in the element registry so the
        // panel still shows class / name / guid for visible elements.
        auto info = registry->findBasicElementInfo(object_id);
        if (info && !info->type.isEmpty()) {
            state.entity.entity_class = info->type;
            if (!state.property_sets.isEmpty() && !state.property_sets[1].rows.isEmpty()) {
                state.property_sets[1].rows[0].value = info->type;
            }
        }
        if (info && !info->name.isEmpty()) {
            state.attributes[1].value = info->name;
            if (state.property_sets.size() > 1 && state.property_sets[1].rows.size() > 1) {
                state.property_sets[1].rows[1].value = info->name;
            }
        }
        if (info && !info->guid.isEmpty()) {
            state.attributes[0].value = info->guid;
        }
    }
    widget_->render(state);
}

} // namespace ifcviewerfull::modules::properties
