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

#ifndef IFCINTERFACE_MODULES_VIEWPORT_COMMANDS_H
#define IFCINTERFACE_MODULES_VIEWPORT_COMMANDS_H

class ViewportWindow;
namespace bonsaiviewer { class SessionState; }

namespace bonsaiviewer::modules::viewport::commands {

void setHome(SessionState& session, ViewportWindow& viewport);
void goHome(SessionState& session, ViewportWindow& viewport);
void viewSelected(ViewportWindow& viewport);

void fly(SessionState& session, ViewportWindow& viewport);
void toggleSection(SessionState& session, ViewportWindow& viewport);
void clearSection(SessionState& session, ViewportWindow& viewport);

void toggleDistance(ViewportWindow& viewport);
void toggleArea(ViewportWindow& viewport);
void toggleVolume(ViewportWindow& viewport);

void hideSelected(ViewportWindow& viewport);
void isolateSelected(ViewportWindow& viewport);
void showAll(ViewportWindow& viewport);
void invertVisibility(ViewportWindow& viewport);

} // namespace bonsaiviewer::modules::viewport::commands

#endif
