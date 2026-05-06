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

#ifndef IFCINTERFACE_COMPONENTS_STYLE_H
#define IFCINTERFACE_COMPONENTS_STYLE_H

#include <QString>

namespace ifcinterface::components::style::metrics {

inline constexpr int padding = 6;
inline constexpr int section_body_padding = 10;
inline constexpr int section_header_padding = 2;
inline constexpr int panel_radius = 3;

} // namespace ifcinterface::components::style::metrics

namespace ifcinterface::components::style::palette {

inline constexpr auto primary_text = "#d0d5dd";
inline constexpr auto secondary_text = "#9aa4b3";
inline constexpr auto disabled_text = "#8f98a6";
inline constexpr auto warning_text = "#e4b35a";

} // namespace ifcinterface::components::style::palette

namespace ifcinterface::components::style {

QString buildAppStyleSheet();

} // namespace ifcinterface::components::style

#endif
