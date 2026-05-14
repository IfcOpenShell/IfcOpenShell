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

#include "../../ElementRegistry.h"
#include "../../SessionState.h"
#include "../models/Controller.h"
#include "../viewport/Controller.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"

#include <QFileDialog>
#include <QFileInfo>
#include <QMessageBox>

namespace ifcinterface::modules::project {

ProjectController::ProjectController(QWidget* host,
                                     Federation* federation,
                                     ifcinterface::SessionState* session_state,
                                     ifcinterface::ElementRegistry* element_registry,
                                     ViewportWindow* viewport,
                                     ifcinterface::modules::models::ModelsPanelController* models_controller,
                                     ifcinterface::modules::viewport::ViewportController* viewport_controller,
                                     QObject* parent)
    : QObject(parent)
    , host_(host)
    , federation_(federation)
    , session_state_(session_state)
    , element_registry_(element_registry)
    , viewport_(viewport)
    , models_controller_(models_controller)
    , viewport_controller_(viewport_controller)
{
}

bool ProjectController::newProject() {
    SceneLoader* loader = session_state_->loader();
    if (loader && loader->isLoading()) {
        QMessageBox::information(
            host_, "New Project",
            "Wait until the current model load finishes before creating a new project.");
        return false;
    }
    if (!confirmDiscardIfDirty()) return false;

    clearScene();
    federation_->clear();
    viewport_controller_->applyFederatedFalseOrigin();
    session_state_->setStatusMessage("Project", "Untitled");
    session_state_->notifyProjectReset();
    return true;
}

bool ProjectController::openProject() {
    QFileDialog file_dialog(host_, "Open Project");
    file_dialog.setFileMode(QFileDialog::ExistingFile);
    file_dialog.setNameFilter("IFC Federation (*.ifcfed);;All Files (*)");
    file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (file_dialog.exec() != QDialog::Accepted) return false;

    const QString path = file_dialog.selectedFiles().value(0);
    if (path.isEmpty()) return false;
    return openProject(path);
}

bool ProjectController::openProject(const QString& path) {
    SceneLoader* loader = session_state_->loader();
    if (loader && loader->isLoading()) {
        QMessageBox::information(
            host_, "Open Project",
            "Wait until the current model load finishes before opening another project.");
        return false;
    }
    if (!confirmDiscardIfDirty()) return false;

    QStringList warnings;
    QString err;
    if (!federation_->load(path, &warnings, &err)) {
        QMessageBox::warning(host_, "Open Project",
                             QString("Could not open project:\n%1").arg(err));
        return false;
    }

    clearScene();

    QStringList paths;
    QStringList fed_ids;
    for (const auto& model : federation_->models()) {
        if (model.source_kind != "local") continue;
        if (!QFileInfo::exists(model.source_path)) {
            warnings << QString("Source not found, kept in project: %1").arg(model.source_path);
            continue;
        }
        paths << model.source_path;
        fed_ids << model.id;
    }
    models_controller_->loadModels(paths, fed_ids);

    if (!warnings.isEmpty()) {
        QMessageBox::warning(host_, "Open Project",
                             "Project opened with warnings:\n\n" + warnings.join("\n"));
    }

    federation_->markClean();
    viewport_controller_->applyFederatedFalseOrigin();
    if (federation_->hasHomeView()) {
        const auto& hv = federation_->homeView();
        viewport_->setCamera(
            hv.target.x(), hv.target.y(), hv.target.z(), hv.distance, hv.yaw, hv.pitch);
    }
    session_state_->setStatusMessage("Project", QFileInfo(path).fileName());
    session_state_->notifyProjectOpened(path);
    return true;
}

bool ProjectController::saveProject() {
    if (federation_->filePath().isEmpty()) return saveProjectAs();

    QString err;
    if (!federation_->save(federation_->filePath(), &err)) {
        QMessageBox::warning(host_, "Save Project",
                             QString("Could not save project:\n%1").arg(err));
        return false;
    }
    session_state_->setStatusMessage("Project", QFileInfo(federation_->filePath()).fileName());
    session_state_->notifyProjectSaved(federation_->filePath());
    return true;
}

bool ProjectController::saveProjectAs() {
    QString suggested = federation_->filePath();
    if (suggested.isEmpty()) suggested = "project.ifcfed";

    QFileDialog file_dialog(host_, "Save Project As", suggested);
    file_dialog.setAcceptMode(QFileDialog::AcceptSave);
    file_dialog.setFileMode(QFileDialog::AnyFile);
    file_dialog.setNameFilter("IFC Federation (*.ifcfed);;All Files (*)");
    file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (file_dialog.exec() != QDialog::Accepted) return false;

    QString path = file_dialog.selectedFiles().value(0);
    if (path.isEmpty()) return false;
    if (!path.endsWith(".ifcfed", Qt::CaseInsensitive)) path += ".ifcfed";
    return saveProjectAs(path);
}

bool ProjectController::saveProjectAs(const QString& path) {
    QString err;
    if (!federation_->save(path, &err)) {
        QMessageBox::warning(host_, "Save Project",
                             QString("Could not save project:\n%1").arg(err));
        return false;
    }
    session_state_->setStatusMessage("Project", QFileInfo(path).fileName());
    session_state_->notifyProjectSaved(path);
    return true;
}

void ProjectController::clearScene() {
    viewport_->setSelectedObjectId(0);
    session_state_->setSelectedObjectId(0);
    session_state_->notifySelectionChanged();

    const auto model_ids = session_state_->modelIds();
    for (uint32_t mid : model_ids) {
        viewport_->removeModel(mid);
        session_state_->loader()->removeModel(mid);
    }

    session_state_->clearModelMappings();
    element_registry_->clear();
    session_state_->notifyModelsChanged();
}

bool ProjectController::confirmDiscardIfDirty() {
    if (!federation_->isDirty()) return true;
    const auto result = QMessageBox::question(
        host_, "Unsaved Project",
        "The current project has unsaved changes. Save before continuing?",
        QMessageBox::Save | QMessageBox::Discard | QMessageBox::Cancel,
        QMessageBox::Save);
    if (result == QMessageBox::Cancel) return false;
    if (result == QMessageBox::Save) return saveProject();
    return true;
}

} // namespace ifcinterface::modules::project
