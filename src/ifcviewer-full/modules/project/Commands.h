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

#ifndef IFCINTERFACE_MODULES_PROJECT_COMMANDS_H
#define IFCINTERFACE_MODULES_PROJECT_COMMANDS_H

#include <QString>

class QWidget;
class ViewportWindow;
namespace ifcviewerfull { class SessionState; }

namespace ifcviewerfull::modules::project::commands {

// User-facing commands. Each owns its own dialogs and confirmations; each
// emits exactly one notify() at the end (projectReset / projectOpened /
// projectSaved) so views refresh once per command.
bool newProject(SessionState& s, QWidget& host, ViewportWindow& vp);
bool openProject(SessionState& s, QWidget& host, ViewportWindow& vp);
bool saveProject(SessionState& s, QWidget& host);
bool saveProjectAs(SessionState& s, QWidget& host);

} // namespace ifcviewerfull::modules::project::commands

#endif
