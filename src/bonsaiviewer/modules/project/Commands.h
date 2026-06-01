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
class WgpuViewportWindow;
namespace bonsaiviewer { class SessionState; }

namespace bonsaiviewer::modules::project::commands {

// User-facing commands. Each owns its own dialogs and confirmations; each
// emits exactly one notify() at the end (projectReset / projectOpened /
// projectSaved) so views refresh once per command.
bool newProject(SessionState& s, QWidget& host, WgpuViewportWindow& vp);
bool openProject(SessionState& s, QWidget& host, WgpuViewportWindow& vp);
// Open a specific .ifcfed by path, bypassing the file dialog. Used by the
// "Open Recent" menu. Same dirty-check / load / cloud-resolve flow as
// openProject; returns false if the load failed or was cancelled.
bool openProjectPath(SessionState& s, QWidget& host, WgpuViewportWindow& vp, const QString& path);
// Pick a connector, then call pull_ifcfed_interactive and open the resulting
// .ifcfed as a fresh project. Non-local models in the loaded federation are
// resolved asynchronously via pull_models.
bool openCloudProject(SessionState& s, QWidget& host, WgpuViewportWindow& vp);
// pull_ifcfed using the current project's .ifcfed.manifest. Re-downloads
// the .ifcfed from the same cloud target it came from (typically without
// user interaction), then opens it like a fresh project — discarding any
// local edits after the usual dirty-check prompt.
bool syncCloudProject(SessionState& s, QWidget& host, WgpuViewportWindow& vp);
bool saveProject(SessionState& s, QWidget& host);
bool saveProjectAs(SessionState& s, QWidget& host);
// Push the current federation to the cloud target named in its manifest
// (push_ifcfed). No user prompt for destination. Caller is responsible for
// gating this on Federation::hasManifest.
bool saveCloudProject(SessionState& s, QWidget& host);
// Pick a connector and push the current federation to a fresh cloud target
// (push_ifcfed_interactive). The connector returns a new path + manifest;
// Federation repoints to that location.
bool saveAsCloudProject(SessionState& s, QWidget& host);
// Show the four-way Save dialog (Local / Save As Local / To Cloud / Save
// As To Cloud) and dispatch to one of the above. This is what the "Save
// Project" ribbon button is wired to.
bool saveProjectDialog(SessionState& s, QWidget& host);

} // namespace bonsaiviewer::modules::project::commands

#endif
