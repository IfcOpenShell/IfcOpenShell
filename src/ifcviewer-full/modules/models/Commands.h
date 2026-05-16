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
class ViewportWindow;
namespace ifcviewerfull { class SessionState; }

namespace ifcviewerfull::modules::models::commands {

// User-facing commands. Each one is responsible for emitting any notify()
// signals exactly once, at the end of its execution.
void toggleVisibility(SessionState& s, ItemKind kind, const QString& id);
void addGroup(SessionState& s, QWidget& host, const QString& parent_group_id);
void renameGroup(SessionState& s, QWidget& host, const QString& group_id);
void moveGroup(SessionState& s, const QString& id, const QString& parent_group_id);
void moveModels(SessionState& s, const QStringList& ids, const QString& parent_group_id);
void removeGroup(SessionState& s, QWidget& host, const QString& group_id);
void removeModel(SessionState& s, ViewportWindow& vp, QWidget& host, const QString& fed_id);
void addModel(SessionState& s, QWidget& host);
void convertIfcToDatabase(SessionState& s, QWidget& host);
void exportGeometryDatabase(SessionState& s, QWidget& host);
void openSettings(SessionState& s, QWidget& host);

// Snapshots the in-memory geometry + element registry for a freshly streamed
// model and persists it as a sidecar next to the source IFC. Called after
// SceneLoader::loadedFromStream so subsequent loads can skip the stream phase.
void writeSidecarForLoadedModel(SessionState& s, ViewportWindow& vp, uint32_t mid);

// Persistent post-load handler. Call once at app startup. Whenever the
// session reports a model was streamed (not loaded from cache), persists a
// sidecar so the next load skips the stream phase. Connection lifetime is
// tied to `context`.
void addHandlers(SessionState& s, ViewportWindow& vp, QObject& context);

// Internal building blocks shared by commands here and by ProjectController.
// These NEVER call notify*() — the caller is responsible for emitting once
// at the end of its execution.
namespace detail {

// Queues already-federated models on the loader and maps their fed-ids to mids.
void loadModels(SessionState& s, const QStringList& paths, const QStringList& fed_ids);

} // namespace detail

} // namespace ifcviewerfull::modules::models::commands

#endif
