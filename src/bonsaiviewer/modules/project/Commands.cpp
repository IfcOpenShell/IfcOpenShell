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

#include "Commands.h"

#include "SaveProjectDialog.h"

#include "../../ElementRegistry.h"
#include "../../SessionState.h"
#include "../connectors/PickerDialog.h"
#include "../connectors/Process.h"
#include "../connectors/Registry.h"
#include "../models/Commands.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"

#include <QDebug>
#include <QDir>
#include <QFileDialog>
#include <QFileInfo>
#include <QHash>
#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>
#include <QMessageBox>
#include <QPointer>
#include <QTemporaryDir>

#include <memory>

namespace bonsaiviewer::modules::project::commands {

namespace {

// Pure helper — clears the loaded scene without emitting any signals. The
// caller (newProject / openProject) emits projectReset / projectOpened once
// the whole flow finishes.
void clearScene(SessionState& session, ViewportWindow& viewport) {
    viewport.setSelectedObjectId(0);
    session.setSelectedObjectId(0);
    for (uint32_t model_id : session.modelIds()) {
        viewport.removeModel(model_id);
        session.loader()->removeModel(model_id);
    }
    session.clearModelMappings();
    session.elementRegistry()->clear();
}

// Returns false if the user cancelled (i.e. don't proceed with the destructive
// op). Handles the Save → Discard → Cancel branch including a follow-on save.
bool confirmDiscardIfDirty(SessionState& session, QWidget& host) {
    if (!session.federation()->isDirty()) return true;
    const auto result = QMessageBox::question(
        &host, "Unsaved Project",
        "The current project has unsaved changes. Save before continuing?",
        QMessageBox::Save | QMessageBox::Discard | QMessageBox::Cancel,
        QMessageBox::Save);
    if (result == QMessageBox::Cancel) return false;
    if (result == QMessageBox::Save) return saveProject(session, host);
    return true;
}

// Fire-and-forget async resolution of any non-local models in the
// federation. Groups by source_connector and issues one pull_models per
// group. For each returned entry:
//   - if the fed_id already has a scene entry pointed at the same path,
//     just refresh cloud metadata (no reload, preserves view state);
//   - if the path differs, tear down the stale scene entry and queue a
//     fresh load (federation entry is preserved either way);
//   - if no scene entry exists yet (initial open), queue a load.
// Per spec, connector errors are not surfaced to the user; the connector
// has already shown its own UI.
void resolveCloudModels(SessionState& session, ViewportWindow& viewport) {
    auto* federation = session.federation();
    QHash<QString, QStringList> connector_to_fed_ids;
    for (const auto& model : federation->models()) {
        if (model.source_connector == "local") continue;
        connector_to_fed_ids[model.source_connector].push_back(model.id);
    }
    if (connector_to_fed_ids.isEmpty()) return;

    auto* registry = session.connectorRegistry();
    QPointer<SessionState> sguard(&session);
    QPointer<ViewportWindow> vguard(&viewport);

    for (auto it = connector_to_fed_ids.constBegin();
              it != connector_to_fed_ids.constEnd(); ++it) {
        const QString connector_id = it.key();
        const QStringList fed_ids = it.value();

        auto* proc = registry->get(connector_id);
        if (!proc) {
            qWarning() << "resolveCloudModels: cannot launch connector"
                       << connector_id << ":" << registry->lastError();
            continue;
        }

        QJsonArray params;
        for (const QString& fed_id : fed_ids) {
            const Federation::Model* model = federation->findById(fed_id);
            if (!model) continue;
            QJsonObject source = model->source_data;
            source["connector"] = model->source_connector;
            QJsonObject entry;
            entry["display_name"] = model->display_name;
            entry["id"] = model->id;
            entry["source"] = source;
            params.append(entry);
        }

        proc->call("pull_models", params,
            [sguard, vguard, fed_ids](const QJsonValue& result) {
                if (!sguard) return;
                const QJsonArray arr = result.toArray();
                QStringList paths_to_load;
                QStringList fed_ids_to_load;
                bool any_detached = false;
                for (int i = 0; i < arr.size() && i < fed_ids.size(); ++i) {
                    if (arr[i].isNull()) continue;
                    const QJsonObject obj = arr[i].toObject();
                    const QString new_path = obj.value("path").toString();
                    if (new_path.isEmpty()) continue;
                    const QString fed_id = fed_ids[i];
                    const QJsonObject meta = obj.value("metadata").toObject();

                    const uint32_t existing_mid = sguard->modelIdForFedId(fed_id);
                    if (existing_mid != 0 && sguard->loader()) {
                        const QString existing_path = sguard->loader()->filePath(existing_mid);
                        if (QDir::cleanPath(existing_path) == QDir::cleanPath(new_path)) {
                            sguard->setCloudMetadata(fed_id, meta.toVariantMap());
                            continue;
                        }
                        // Path changed (new revision lives in a fresh cache dir).
                        // Detach the stale scene entry; federation entry stays.
                        if (vguard) vguard->removeModel(existing_mid);
                        sguard->loader()->removeModel(existing_mid);
                        sguard->elementRegistry()->removeModel(existing_mid);
                        sguard->removeModelMappingByFedId(fed_id);
                        any_detached = true;
                    }

                    sguard->setCloudMetadata(fed_id, meta.toVariantMap());
                    paths_to_load << new_path;
                    fed_ids_to_load << fed_id;
                }
                if (any_detached) {
                    if (vguard) vguard->setSelectedObjectId(0);
                    sguard->setSelectedObjectId(0);
                    sguard->notifySelectionChanged();
                }
                if (!paths_to_load.isEmpty()) {
                    modules::models::commands::detail::loadModels(
                        *sguard, paths_to_load, fed_ids_to_load);
                    sguard->notifyModelsChanged();
                }
            },
            [sguard, connector_id](int code, const QString& message) {
                qWarning() << "pull_models from" << connector_id
                           << "failed:" << code << message;
                if (sguard) {
                    sguard->setStatusMessage("Cloud",
                        QString("%1 reported an error (see connector UI)").arg(connector_id));
                }
            });
    }

    int total = 0;
    for (auto it = connector_to_fed_ids.constBegin();
              it != connector_to_fed_ids.constEnd(); ++it) {
        total += it.value().size();
    }
    session.setStatusMessage("Cloud", QString("Resolving %1 model(s)...").arg(total));
}

// Byte-equality check for "is this .ifcfed the same as what we have loaded?"
// — used by Sync From Cloud to skip the full reload when the connector
// served an unchanged revision.
bool isIfcfedUnchanged(const QString& current_path, const QString& candidate_path) {
    if (current_path.isEmpty() || candidate_path.isEmpty()) return false;
    if (QDir::cleanPath(current_path) == QDir::cleanPath(candidate_path)) return true;
    QFile a(current_path);
    QFile b(candidate_path);
    if (!a.open(QIODevice::ReadOnly) || !b.open(QIODevice::ReadOnly)) return false;
    if (a.size() != b.size()) return false;
    return a.readAll() == b.readAll();
}

bool openProjectAt(SessionState& session, QWidget& host, ViewportWindow& viewport, const QString& path) {
    SceneLoader* loader = session.loader();
    if (loader && loader->isLoading()) {
        QMessageBox::information(
            &host, "Open Project",
            "Wait until the current model load finishes before opening another project.");
        return false;
    }
    if (!confirmDiscardIfDirty(session, host)) return false;

    QStringList warnings;
    QString err;
    if (!session.federation()->load(path, &warnings, &err)) {
        QMessageBox::warning(&host, "Open Project",
                             QString("Could not open project:\n%1").arg(err));
        return false;
    }

    clearScene(session, viewport);

    QStringList paths;
    QStringList fed_ids;
    for (const auto& model : session.federation()->models()) {
        if (model.source_connector != "local") continue;
        if (!QFileInfo::exists(model.source_path)) {
            warnings << QString("Source not found, kept in project: %1").arg(model.source_path);
            continue;
        }
        paths << model.source_path;
        fed_ids << model.id;
    }
    modules::models::commands::detail::loadModels(session, paths, fed_ids);

    if (!warnings.isEmpty()) {
        QMessageBox::warning(&host, "Open Project",
                             "Project opened with warnings:\n\n" + warnings.join("\n"));
    }

    session.federation()->markClean();
    if (session.federation()->hasHomeView()) {
        const auto& home_view = session.federation()->homeView();
        viewport.setCamera(home_view.target.x(), home_view.target.y(), home_view.target.z(),
                     home_view.distance, home_view.yaw, home_view.pitch);
    }
    session.setStatusMessage("Project", QFileInfo(path).fileName());
    session.notifyProjectOpened(path);

    resolveCloudModels(session, viewport);
    return true;
}

bool saveProjectTo(SessionState& session, QWidget& host, const QString& path) {
    QString err;
    if (!session.federation()->save(path, &err)) {
        QMessageBox::warning(&host, "Save Project",
                             QString("Could not save project:\n%1").arg(err));
        return false;
    }
    session.setStatusMessage("Project", QFileInfo(path).fileName());
    session.notifyProjectSaved(path);
    return true;
}

} // namespace

bool newProject(SessionState& session, QWidget& host, ViewportWindow& viewport) {
    SceneLoader* loader = session.loader();
    if (loader && loader->isLoading()) {
        QMessageBox::information(
            &host, "New Project",
            "Wait until the current model load finishes before creating a new project.");
        return false;
    }
    if (!confirmDiscardIfDirty(session, host)) return false;

    clearScene(session, viewport);
    session.federation()->clear();
    session.setStatusMessage("Project", "Untitled");
    session.notifyProjectReset();
    return true;
}

bool openProject(SessionState& session, QWidget& host, ViewportWindow& viewport) {
    QFileDialog file_dialog(&host, "Open Project");
    file_dialog.setFileMode(QFileDialog::ExistingFile);
    file_dialog.setNameFilter("IFC Federation (*.ifcfed);;All Files (*)");
    file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (file_dialog.exec() != QDialog::Accepted) return false;

    const QString path = file_dialog.selectedFiles().value(0);
    if (path.isEmpty()) return false;
    return openProjectAt(session, host, viewport, path);
}

bool openProjectPath(SessionState& session, QWidget& host, ViewportWindow& viewport, const QString& path) {
    if (path.isEmpty()) return false;
    return openProjectAt(session, host, viewport, path);
}

bool openCloudProject(SessionState& session, QWidget& host, ViewportWindow& viewport) {
    SceneLoader* loader = session.loader();
    if (loader && loader->isLoading()) {
        QMessageBox::information(
            &host, "Open from Cloud",
            "Wait until the current model load finishes before opening another project.");
        return false;
    }
    if (!confirmDiscardIfDirty(session, host)) return false;

    auto* registry = session.connectorRegistry();
    const auto& manifests = registry->available();
    if (manifests.empty()) {
        QMessageBox::information(&host, "Open from Cloud",
            "No connectors are installed. Install one under your user connectors "
            "directory.");
        return false;
    }

    modules::connectors::ConnectorPickerDialog picker(
        manifests, "Open from Cloud",
        "Pick a connector to browse a project on.", &host);
    if (picker.exec() != QDialog::Accepted) return false;
    const QString connector_id = picker.selectedId();
    if (connector_id.isEmpty()) return false;

    auto* proc = registry->get(connector_id);
    if (!proc) {
        QMessageBox::warning(&host, "Open from Cloud",
            QString("Could not launch connector '%1':\n%2")
                .arg(connector_id, registry->lastError()));
        return false;
    }

    session.beginProgress(QString("Opening project from %1...").arg(connector_id));
    session.setStatusMessage("Cloud", QString("Browsing %1...").arg(connector_id));

    QPointer<SessionState> sguard(&session);
    QPointer<QWidget> hguard(&host);
    QPointer<ViewportWindow> vguard(&viewport);

    proc->call("pull_ifcfed_interactive", QJsonValue(),
        [sguard, hguard, vguard, connector_id](const QJsonValue& result) {
            if (!sguard) return;
            sguard->endProgress();
            const QString path = result.toObject().value("path").toString();
            if (path.isEmpty()) {
                if (hguard) {
                    QMessageBox::warning(hguard, "Open from Cloud",
                        QString("Connector '%1' returned no path.").arg(connector_id));
                }
                return;
            }
            if (hguard && vguard) {
                openProjectAt(*sguard, *hguard, *vguard, path);
            }
        },
        [sguard, connector_id](int code, const QString& message) {
            qWarning() << "pull_ifcfed_interactive from" << connector_id
                       << "failed:" << code << message;
            if (sguard) {
                sguard->endProgress();
                sguard->setStatusMessage("Cloud",
                    QString("%1 reported an error (see connector UI)").arg(connector_id));
            }
        });
    return true;
}

bool syncCloudProject(SessionState& session, QWidget& host, ViewportWindow& viewport) {
    auto* federation = session.federation();

    // Per spec, sync has two independent phases — refreshing the .ifcfed
    // (requires manifest) and refreshing cloud models (requires any
    // non-local source). Either is sufficient.
    const bool has_manifest = federation->hasManifest();
    bool has_cloud_models = false;
    for (const auto& model : federation->models()) {
        if (model.source_connector != "local") { has_cloud_models = true; break; }
    }
    if (!has_manifest && !has_cloud_models) {
        QMessageBox::information(&host, "Sync From Cloud",
            "Nothing to sync — this project has no cloud resources.");
        return false;
    }

    SceneLoader* loader = session.loader();
    if (loader && loader->isLoading()) {
        QMessageBox::information(&host, "Sync From Cloud",
            "Wait until the current model load finishes before syncing.");
        return false;
    }

    // No manifest: skip the pull_ifcfed phase entirely (spec step 2-4
    // skipped). Just refresh cloud-sourced models against the .ifcfed
    // already on disk. Federation state is preserved, so no dirty prompt.
    if (!has_manifest) {
        session.setStatusMessage("Cloud", "Refreshing cloud models...");
        resolveCloudModels(session, viewport);
        return true;
    }

    // Manifest path: the .ifcfed itself may be replaced. Confirm dirty —
    // even though we'll attempt to preserve the session if the returned
    // .ifcfed is byte-equal, that's not known until after the round-trip.
    if (!confirmDiscardIfDirty(session, host)) return false;

    const QString connector_id = federation->manifestConnectorId();
    if (connector_id.isEmpty()) {
        QMessageBox::warning(&host, "Sync From Cloud",
            "The project's manifest does not name a connector.");
        return false;
    }
    auto* registry = session.connectorRegistry();
    auto* proc = registry->get(connector_id);
    if (!proc) {
        QMessageBox::warning(&host, "Sync From Cloud",
            QString("Could not launch connector '%1':\n%2")
                .arg(connector_id, registry->lastError()));
        return false;
    }

    session.beginProgress(QString("Syncing from %1...").arg(connector_id));
    session.setStatusMessage("Cloud", QString("Syncing from %1...").arg(connector_id));

    QPointer<SessionState> sguard(&session);
    QPointer<QWidget> hguard(&host);
    QPointer<ViewportWindow> vguard(&viewport);
    const QString current_path = federation->filePath();

    proc->call("pull_ifcfed", federation->manifest(),
        [sguard, hguard, vguard, connector_id, current_path](const QJsonValue& result) {
            if (!sguard) return;
            sguard->endProgress();
            const QString new_path = result.toObject().value("path").toString();
            if (new_path.isEmpty()) {
                if (hguard) {
                    QMessageBox::warning(hguard, "Sync From Cloud",
                        QString("Connector '%1' returned no path.").arg(connector_id));
                }
                return;
            }
            // Per spec: if the returned .ifcfed is unchanged from the one
            // already loaded, preserve the current session — just repoint
            // if the cache path moved and resync models.
            if (isIfcfedUnchanged(current_path, new_path)) {
                if (QDir::cleanPath(current_path) != QDir::cleanPath(new_path)) {
                    sguard->federation()->repointTo(new_path);
                }
                sguard->setStatusMessage("Cloud",
                    "Project up to date; refreshing cloud models...");
                if (vguard) resolveCloudModels(*sguard, *vguard);
                return;
            }
            // Content differs — fall through to the standard open path,
            // which clears the scene and triggers resolveCloudModels for
            // any cloud-sourced models in the freshly loaded federation.
            if (hguard && vguard) {
                openProjectAt(*sguard, *hguard, *vguard, new_path);
            }
        },
        [sguard, connector_id](int code, const QString& message) {
            qWarning() << "pull_ifcfed from" << connector_id
                       << "failed:" << code << message;
            if (sguard) {
                sguard->endProgress();
                sguard->setStatusMessage("Cloud",
                    QString("%1 reported an error (see connector UI)").arg(connector_id));
            }
        });
    return true;
}

bool saveProject(SessionState& session, QWidget& host) {
    if (session.federation()->filePath().isEmpty()) return saveProjectAs(session, host);
    return saveProjectTo(session, host, session.federation()->filePath());
}

bool saveProjectAs(SessionState& session, QWidget& host) {
    QString suggested = session.federation()->filePath();
    if (suggested.isEmpty()) suggested = "project.ifcfed";

    QFileDialog file_dialog(&host, "Save Project As", suggested);
    file_dialog.setAcceptMode(QFileDialog::AcceptSave);
    file_dialog.setFileMode(QFileDialog::AnyFile);
    file_dialog.setNameFilter("IFC Federation (*.ifcfed);;All Files (*)");
    file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (file_dialog.exec() != QDialog::Accepted) return false;

    QString path = file_dialog.selectedFiles().value(0);
    if (path.isEmpty()) return false;
    if (!path.endsWith(".ifcfed", Qt::CaseInsensitive)) path += ".ifcfed";
    return saveProjectTo(session, host, path);
}

namespace {

// Writes the current federation to a fresh QTemporaryDir as a `.ifcfed`
// without touching Federation's state, returning the temp dir (so callers
// can keep it alive through the async RPC) and the resolved file path.
struct TempProjectFile {
    std::shared_ptr<QTemporaryDir> dir;
    QString path;
};

TempProjectFile writeProjectToTemp(SessionState& session, QWidget& host, const QString& op_title) {
    TempProjectFile out;
    out.dir = std::make_shared<QTemporaryDir>();
    if (!out.dir->isValid()) {
        QMessageBox::warning(&host, op_title,
            QString("Could not create a temporary directory:\n%1")
                .arg(out.dir->errorString()));
        out.dir.reset();
        return out;
    }
    const QString name = session.federation()->filePath().isEmpty()
        ? "project.ifcfed"
        : QFileInfo(session.federation()->filePath()).fileName();
    const QString tmp_path = QDir(out.dir->path()).filePath(name);
    QString err;
    if (!session.federation()->writeCopyTo(tmp_path, &err)) {
        QMessageBox::warning(&host, op_title,
            QString("Failed to write temporary project:\n%1").arg(err));
        out.dir.reset();
        return out;
    }
    out.path = tmp_path;
    return out;
}

// Shared continuation for push_ifcfed[_interactive]: on success, repoint
// Federation to the returned path and notify; on error, log + status.
void onPushIfcfedResult(SessionState& session,
                        QWidget& host,
                        const QString& op_title,
                        const QString& connector_id,
                        const QJsonValue& result) {
    session.endProgress();
    const QString new_path = result.toObject().value("path").toString();
    if (new_path.isEmpty()) {
        QMessageBox::warning(&host, op_title,
            QString("Connector '%1' returned no path.").arg(connector_id));
        return;
    }
    QStringList warnings;
    session.federation()->repointTo(new_path, &warnings);
    session.setStatusMessage("Cloud",
        QString("Saved to %1 via %2")
            .arg(QFileInfo(new_path).fileName(), connector_id));
    session.notifyProjectSaved(new_path);
}

} // namespace

bool saveCloudProject(SessionState& session, QWidget& host) {
    auto* federation = session.federation();
    if (!federation->hasManifest()) {
        QMessageBox::information(&host, "Save To Cloud",
            "This project has no cloud target. Use \"Save As To Cloud\" first.");
        return false;
    }
    const QString connector_id = federation->manifestConnectorId();
    auto* registry = session.connectorRegistry();
    auto* proc = registry->get(connector_id);
    if (!proc) {
        QMessageBox::warning(&host, "Save To Cloud",
            QString("Could not launch connector '%1':\n%2")
                .arg(connector_id, registry->lastError()));
        return false;
    }

    auto temporary_project = writeProjectToTemp(session, host, "Save To Cloud");
    if (!temporary_project.dir) return false;

    QJsonObject params;
    params["path"] = temporary_project.path;
    params["manifest"] = federation->manifest();

    session.beginProgress(QString("Saving to %1...").arg(connector_id));
    session.setStatusMessage("Cloud", QString("Saving to %1...").arg(connector_id));

    QPointer<SessionState> sguard(&session);
    QPointer<QWidget> hguard(&host);

    proc->call("push_ifcfed", params,
        [sguard, hguard, connector_id, tmp_keepalive = temporary_project.dir](const QJsonValue& result) {
            (void)tmp_keepalive;
            if (!sguard || !hguard) return;
            onPushIfcfedResult(*sguard, *hguard, "Save To Cloud", connector_id, result);
        },
        [sguard, connector_id, tmp_keepalive = temporary_project.dir](int code, const QString& message) {
            (void)tmp_keepalive;
            qWarning() << "push_ifcfed to" << connector_id
                       << "failed:" << code << message;
            if (sguard) {
                sguard->endProgress();
                sguard->setStatusMessage("Cloud",
                    QString("%1 reported an error (see connector UI)").arg(connector_id));
            }
        });
    return true;
}

bool saveAsCloudProject(SessionState& session, QWidget& host) {
    auto* registry = session.connectorRegistry();
    const auto& manifests = registry->available();
    if (manifests.empty()) {
        QMessageBox::information(&host, "Save As To Cloud",
            "No connectors are installed.");
        return false;
    }

    modules::connectors::ConnectorPickerDialog picker(
        manifests, "Save As To Cloud",
        "Pick a connector to push this project to.", &host);
    if (picker.exec() != QDialog::Accepted) return false;
    const QString connector_id = picker.selectedId();
    if (connector_id.isEmpty()) return false;

    auto* proc = registry->get(connector_id);
    if (!proc) {
        QMessageBox::warning(&host, "Save As To Cloud",
            QString("Could not launch connector '%1':\n%2")
                .arg(connector_id, registry->lastError()));
        return false;
    }

    auto temporary_project = writeProjectToTemp(session, host, "Save As To Cloud");
    if (!temporary_project.dir) return false;

    QJsonObject params;
    params["path"] = temporary_project.path;

    session.beginProgress(QString("Pushing to %1...").arg(connector_id));
    session.setStatusMessage("Cloud", QString("Pushing to %1...").arg(connector_id));

    QPointer<SessionState> sguard(&session);
    QPointer<QWidget> hguard(&host);

    proc->call("push_ifcfed_interactive", params,
        [sguard, hguard, connector_id, tmp_keepalive = temporary_project.dir](const QJsonValue& result) {
            (void)tmp_keepalive;
            if (!sguard || !hguard) return;
            onPushIfcfedResult(*sguard, *hguard, "Save As To Cloud", connector_id, result);
        },
        [sguard, connector_id, tmp_keepalive = temporary_project.dir](int code, const QString& message) {
            (void)tmp_keepalive;
            qWarning() << "push_ifcfed_interactive to" << connector_id
                       << "failed:" << code << message;
            if (sguard) {
                sguard->endProgress();
                sguard->setStatusMessage("Cloud",
                    QString("%1 reported an error (see connector UI)").arg(connector_id));
            }
        });
    return true;
}

bool saveProjectDialog(SessionState& session, QWidget& host) {
    SaveProjectDialog dialog(session.federation()->hasManifest(), &host);
    if (dialog.exec() != QDialog::Accepted) return false;
    switch (dialog.selectedTarget()) {
    case SaveTarget::Local:   return saveProject(session, host);
    case SaveTarget::LocalAs: return saveProjectAs(session, host);
    case SaveTarget::Cloud:   return saveCloudProject(session, host);
    case SaveTarget::CloudAs: return saveAsCloudProject(session, host);
    case SaveTarget::None:    return false;
    }
    return false;
}

} // namespace bonsaiviewer::modules::project::commands
