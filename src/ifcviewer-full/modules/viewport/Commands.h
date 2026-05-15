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
namespace ifcviewerfull { class SessionState; }

namespace ifcviewerfull::modules::viewport::commands {

void setHome(SessionState& session, ViewportWindow& vp);
void goHome(SessionState& session, ViewportWindow& vp);
void viewSelected(ViewportWindow& vp);

void fly(SessionState& session, ViewportWindow& vp);
void toggleSection(SessionState& session, ViewportWindow& vp);
void clearSection(SessionState& session, ViewportWindow& vp);

void toggleDistance(ViewportWindow& vp);
void toggleArea(ViewportWindow& vp);
void toggleVolume(ViewportWindow& vp);

void hideSelected(ViewportWindow& vp);
void isolateSelected(ViewportWindow& vp);
void showAll(ViewportWindow& vp);
void invertVisibility(ViewportWindow& vp);

} // namespace ifcviewerfull::modules::viewport::commands

#endif
