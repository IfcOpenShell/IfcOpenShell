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

namespace ifcinterface::components::style::typography {

inline constexpr int small = 10;

} // namespace ifcinterface::components::style::typography

namespace ifcinterface::components::style::palette {

inline constexpr auto app_background = "#26292f";
inline constexpr auto border = "#3e444e";
inline constexpr auto selection_background = "#39b54a";
inline constexpr auto ribbon_shell_background = "#2d3138";
inline constexpr auto ribbon_tab_hover_text = "#ffffff";
inline constexpr auto ribbon_band_background = "#31353d";
inline constexpr auto ribbon_button_hover = "#3a3f48";
inline constexpr auto ribbon_button_pressed = "#24282f";
inline constexpr auto viewport_shell_background = "#202329";
inline constexpr auto viewport_background = "#1a1d22";
inline constexpr auto panel_title_button = "#8e97a5";
inline constexpr auto panel_title_button_hover = "#353a42";
inline constexpr auto panel_background = "#2b2f36";
inline constexpr auto control_background = "#31353d";
inline constexpr auto control_border_focus = "#5b6472";
inline constexpr auto box_background = "#26292f";
inline constexpr auto scroll_handle = "#525a67";
inline constexpr auto scroll_handle_hover = "#697385";
inline constexpr auto status_background = "#26292f";
inline constexpr auto section_header_background = "#26292f";
inline constexpr auto key_value_value_text = "#dce2eb";

inline constexpr auto primary_text = "#d0d5dd";
inline constexpr auto secondary_text = "#9aa4b3";
inline constexpr auto disabled_text = "#8f98a6";
inline constexpr auto warning_text = "#e4b35a";
inline constexpr auto selection_text = "#14161a";

} // namespace ifcinterface::components::style::palette

namespace ifcinterface::components::style {

QString buildAppStyleSheet();

} // namespace ifcinterface::components::style

#endif
