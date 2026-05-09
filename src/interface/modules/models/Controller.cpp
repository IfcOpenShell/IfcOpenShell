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

#include "Controller.h"

#include "SettingsDialog.h"
#include "Panel.h"

#include "../../ElementRegistry.h"
#include "../../SessionState.h"
#include "AddModelDialog.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"

#include <QFileDialog>
#include <QListView>
#include <QMessageBox>
#include <QTreeView>

namespace ifcinterface::modules::models {

ModelsPanelController::ModelsPanelController(QWidget* host,
                                             ModelsPanel* widget,
                                             ifcinterface::SessionState* session_state,
                                             ViewportWindow* viewport,
                                             QObject* parent)
    : QObject(parent)
    , host_(host)
    , widget_(widget)
    , session_state_(session_state)
    , viewport_(viewport)
{
    connect(widget_, &ModelsPanel::visibilityToggleRequested, this,
            [this](ItemKind kind, const QString& id) {
        Federation* federation = session_state_->federation();
        if (kind == ItemKind::Group) {
            if (const Federation::Group* group = federation->findGroupById(id)) {
                federation->setGroupVisible(id, !group->visible);
                session_state_->notifyVisibilityChanged();
                session_state_->setStatusMessage("Models", group->visible ? "Group hidden" : "Group shown");
            }
        } else {
            if (const Federation::Model* model = federation->findById(id)) {
                federation->setModelVisible(id, !model->visible);
                session_state_->notifyVisibilityChanged();
                session_state_->setStatusMessage("Models", model->visible ? "Model hidden" : "Model shown");
            }
        }
    });
    connect(widget_, &ModelsPanel::addGroupRequested, this,
            [this](const QString& parent_group_id, const QString& name) {
        session_state_->federation()->addGroup(name, parent_group_id);
        session_state_->notifyFederationStructureChanged();
        session_state_->setStatusMessage("Models", "Group added");
    });
    connect(widget_, &ModelsPanel::removeGroupRequested, this,
            [this](const QString& id) {
        session_state_->federation()->removeGroup(id);
        session_state_->notifyFederationStructureChanged();
        session_state_->setStatusMessage("Models", "Group removed");
    });
    connect(widget_, &ModelsPanel::removeModelRequested, this,
            [this](const QString& id) {
        removeLoadedModel(id);
        session_state_->setStatusMessage("Models", "Model removed");
    });
    connect(widget_, &components::Panel::settingsRequested, this, [this]() {
        openSettings();
    });
}

void ModelsPanelController::bindLoader(SceneLoader* loader) {
    connect(loader, &SceneLoader::loadStarted, this,
            [this](uint32_t /*mid*/, const QString& display_name) {
        session_state_->setStatusMessage("Loading", display_name);
    });
    connect(loader, &SceneLoader::loadedFromSidecar, this,
            [this, loader](uint32_t mid, qint64 elapsed_ms) {
        session_state_->setStatusMessage(
            "Loaded",
            QString("%1 from cache in %2")
                .arg(loader->displayName(mid))
                .arg(formatElapsed(elapsed_ms)));
    });
    connect(loader, &SceneLoader::loadedFromStream, this,
            [this, loader](uint32_t mid, qint64 elapsed_ms) {
        session_state_->setStatusMessage(
            "Loaded",
            QString("%1 streamed in %2")
                .arg(loader->displayName(mid))
                .arg(formatElapsed(elapsed_ms)));
    });
    connect(loader, &SceneLoader::loadCancelled, this,
            [this, loader](uint32_t mid) {
        session_state_->setStatusMessage("Cancelled", loader->displayName(mid));
    });
    connect(loader, &SceneLoader::loadError, this,
            [this, host = host_](uint32_t /*mid*/, const QString& message) {
        session_state_->setStatusMessage("Error", message);
        QMessageBox::warning(host, "IfcInterfaceMockup", message);
    });
    connect(loader, &SceneLoader::allLoadsFinished, this,
            [this, loader]() {
        session_state_->setStatusMessage("Loaded", QString("%1 model(s)").arg(loader->modelCount()));
    });
}

void ModelsPanelController::addFiles() {
    modules::models::AddModelDialog dialog(host_);
    if (dialog.exec() != QDialog::Accepted) return;

    QStringList paths;
    switch (dialog.selectedMode()) {
    case modules::models::SourceMode::IfcFile: {
        QFileDialog file_dialog(host_, "Add IFC Files");
        file_dialog.setFileMode(QFileDialog::ExistingFiles);
        file_dialog.setNameFilter("IFC Files (*.ifc);;All Files (*)");
        file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
        if (file_dialog.exec() == QDialog::Accepted) {
            paths = file_dialog.selectedFiles();
        }
        break;
    }
    case modules::models::SourceMode::IfcDatabase: {
        QFileDialog database_dialog(host_, "Add IFC Databases");
        database_dialog.setFileMode(QFileDialog::Directory);
        database_dialog.setOption(QFileDialog::ShowDirsOnly, true);
        database_dialog.setOption(QFileDialog::DontResolveSymlinks, true);
        database_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
        if (auto* list = database_dialog.findChild<QListView*>("listView")) {
            list->setSelectionMode(QAbstractItemView::ExtendedSelection);
        }
        if (auto* tree = database_dialog.findChild<QTreeView*>()) {
            tree->setSelectionMode(QAbstractItemView::ExtendedSelection);
        }
        if (database_dialog.exec() == QDialog::Accepted) {
            paths = database_dialog.selectedFiles();
        }
        break;
    }
    case modules::models::SourceMode::GeometryOnly: {
        QFileDialog file_dialog(host_, "Add Geometry Only");
        file_dialog.setFileMode(QFileDialog::ExistingFiles);
        file_dialog.setNameFilter("IFC Viewer Cache (*.ifcview);;All Files (*)");
        file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
        if (file_dialog.exec() == QDialog::Accepted) {
            paths = file_dialog.selectedFiles();
        }
        break;
    }
    case modules::models::SourceMode::None:
        return;
    }

    addFiles(paths);
}

void ModelsPanelController::addFiles(const QStringList& paths) {
    QStringList accepted_paths;
    QStringList accepted_fed_ids;
    for (const auto& path : paths) {
        const QString fed_id = session_state_->federation()->addModel(path);
        if (fed_id.isEmpty()) continue;
        accepted_paths << path;
        accepted_fed_ids << fed_id;
    }

    loadModels(accepted_paths, accepted_fed_ids);
}

void ModelsPanelController::loadModels(const QStringList& paths, const QStringList& fed_ids) {
    if (paths.isEmpty()) return;

    const auto ids = session_state_->loader()->addFiles(paths);
    for (int i = 0; i < paths.size() && i < static_cast<int>(ids.size()) && i < fed_ids.size(); ++i) {
        session_state_->setModelMapping(fed_ids[i], ids[i]);
    }
    session_state_->notifyModelsChanged();
}

void ModelsPanelController::removeLoadedModel(const QString& fed_id) {
    const uint32_t mid = session_state_->modelIdForFedId(fed_id);
    if (mid == 0) {
        session_state_->federation()->removeModel(fed_id);
        return;
    }
    if (session_state_->loader()->isLoadingModel(mid)) return;

    viewport_->setSelectedObjectId(0);
    session_state_->setSelectedObjectId(0);
    session_state_->federation()->removeModel(fed_id);
    viewport_->removeModel(mid);
    session_state_->loader()->removeModel(mid);
    session_state_->elementRegistry()->removeModel(mid);
    session_state_->removeModelMappingByFedId(fed_id);
    session_state_->notifySelectionChanged();
    session_state_->notifyModelsChanged();
}

void ModelsPanelController::openSettings() {
    SettingsDialog dialog(session_state_->federation(), host_);
    dialog.exec();
}

QString ModelsPanelController::formatElapsed(qint64 ms) const {
    return (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
}

} // namespace ifcinterface::modules::models
