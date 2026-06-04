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

#ifndef IFCINTERFACE_MODULES_MODELS_COMMANDS_H
#define IFCINTERFACE_MODULES_MODELS_COMMANDS_H

#include "Types.h"

#include <QString>
#include <QStringList>
#include <cstdint>

class QWidget;
class WgpuViewportWindow;
namespace bonsaiviewer { class SessionState; }

namespace bonsaiviewer::modules::models {

// Arm/consume pair for "the next model load should auto-guess the
// federation's false origin." Add-model commands arm this when they're
// about to add into an empty session; ViewportView consumes it on the
// next modelGeometryReady. The flag has consume-on-read semantics so
// the API is functions, not a raw bool (a peek-without-clear would
// silently break the one-shot guarantee).
//
// Module-scoped (not on SessionState) because it's add-command intent —
// SessionState shouldn't grow a field for every module's per-command
// state. Lives next to the commands that arm it.
void armFederatedFalseOriginGuess();
bool consumeFederatedFalseOriginGuess();

} // namespace bonsaiviewer::modules::models

namespace bonsaiviewer::modules::models::commands {

// User-facing commands. Each one is responsible for emitting any notify()
// signals exactly once, at the end of its execution.
void toggleVisibility(SessionState& s, ItemKind kind, const QString& id);
void addGroup(SessionState& s, QWidget& host, const QString& parent_group_id);
void renameGroup(SessionState& s, QWidget& host, const QString& group_id);
void moveGroup(SessionState& s, const QString& id, const QString& parent_group_id);
void moveModels(SessionState& s, const QStringList& ids, const QString& parent_group_id);
void removeGroup(SessionState& s, QWidget& host, const QString& group_id);
void removeModel(SessionState& s, WgpuViewportWindow& vp, QWidget& host, const QString& fed_id);
void addModel(SessionState& s, QWidget& host);
// Connector picker → pull_models_interactive → addCloudModel + load.
// Reachable from AddModelDialog's CloudModel button; the underlying call
// is async, so addModelFromCloud returns immediately after kicking it off.
void addModelFromCloud(SessionState& s, QWidget& host);
// push_model: push a cloud-sourced model back to its existing target.
// Only valid when model.source_connector != "local". Async.
void saveModelToCloud(SessionState& s, QWidget& host, const QString& fed_id);
// push_model_interactive: pick a connector and push to a fresh cloud
// target. Valid for any model (local or already cloud-sourced). Async.
void saveModelAsToCloud(SessionState& s, QWidget& host, const QString& fed_id);
void convertIfcToDatabase(SessionState& s, QWidget& host);
void exportGeometryDatabase(SessionState& s, QWidget& host);
void openSettings(SessionState& s, QWidget& host);

// Internal building blocks shared by commands here and by ProjectController.
// These NEVER call notify*() — the caller is responsible for emitting once
// at the end of its execution.
namespace detail {

// Queues already-federated models on the loader and maps their fed-ids to mids.
void loadModels(SessionState& s, const QStringList& paths, const QStringList& fed_ids);

} // namespace detail

} // namespace bonsaiviewer::modules::models::commands

#endif
