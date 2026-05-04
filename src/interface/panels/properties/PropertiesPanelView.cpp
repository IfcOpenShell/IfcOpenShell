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

#include "PropertiesPanelView.h"

#include "PropertiesPanelWidget.h"

namespace ifcinterface::panels::properties {

PropertiesPanelView::PropertiesPanelView(PropertiesPanelWidget* widget, QObject* parent)
    : QObject(parent), widget_(widget)
{
    state_.entity = {"IfcWall", "SOLIDWALL"};
    state_.attributes = {
        {"GlobalId", "2Q$n5SLPP9Q8B7wQKjKfUQ"},
        {"Name", "Core-EXT-204"},
        {"Description", "External load-bearing wall"},
    };
    state_.relationships = {
        {"Type", "Basic Wall: Exterior - 200mm"},
        {"Container", "Level 02"},
    };
    state_.property_sets = {
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
    state_.quantity_sets = {
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

    widget_->setState(state_);
}

} // namespace ifcinterface::panels::properties
