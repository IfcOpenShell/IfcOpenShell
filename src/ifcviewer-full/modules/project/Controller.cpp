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
#include "../models/Commands.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"

#include <QFileDialog>
#include <QFileInfo>
#include <QMessageBox>

namespace ifcviewerfull::modules::project {

ProjectController::ProjectController(QWidget* host,
                                     ifcviewerfull::SessionState* session_state,
                                     ViewportWindow* viewport,
                                     QObject* parent)
    : QObject(parent)
    , host_(host)
    , session_state_(session_state)
    , viewport_(viewport)
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
    session_state_->federation()->clear();
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
    if (!session_state_->federation()->load(path, &warnings, &err)) {
        QMessageBox::warning(host_, "Open Project",
                             QString("Could not open project:\n%1").arg(err));
        return false;
    }

    clearScene();

    QStringList paths;
    QStringList fed_ids;
    for (const auto& model : session_state_->federation()->models()) {
        if (model.source_kind != "local") continue;
        if (!QFileInfo::exists(model.source_path)) {
            warnings << QString("Source not found, kept in project: %1").arg(model.source_path);
            continue;
        }
        paths << model.source_path;
        fed_ids << model.id;
    }
    ifcviewerfull::modules::models::commands::detail::loadModels(*session_state_, paths, fed_ids);

    if (!warnings.isEmpty()) {
        QMessageBox::warning(host_, "Open Project",
                             "Project opened with warnings:\n\n" + warnings.join("\n"));
    }

    session_state_->federation()->markClean();
    if (session_state_->federation()->hasHomeView()) {
        const auto& hv = session_state_->federation()->homeView();
        viewport_->setCamera(
            hv.target.x(), hv.target.y(), hv.target.z(), hv.distance, hv.yaw, hv.pitch);
    }
    session_state_->setStatusMessage("Project", QFileInfo(path).fileName());
    session_state_->notifyProjectOpened(path);
    return true;
}

bool ProjectController::saveProject() {
    if (session_state_->federation()->filePath().isEmpty()) return saveProjectAs();

    QString err;
    if (!session_state_->federation()->save(session_state_->federation()->filePath(), &err)) {
        QMessageBox::warning(host_, "Save Project",
                             QString("Could not save project:\n%1").arg(err));
        return false;
    }
    session_state_->setStatusMessage("Project", QFileInfo(session_state_->federation()->filePath()).fileName());
    session_state_->notifyProjectSaved(session_state_->federation()->filePath());
    return true;
}

bool ProjectController::saveProjectAs() {
    QString suggested = session_state_->federation()->filePath();
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
    if (!session_state_->federation()->save(path, &err)) {
        QMessageBox::warning(host_, "Save Project",
                             QString("Could not save project:\n%1").arg(err));
        return false;
    }
    session_state_->setStatusMessage("Project", QFileInfo(path).fileName());
    session_state_->notifyProjectSaved(path);
    return true;
}

void ProjectController::clearScene() {
    // Helper for newProject / openProject. Does not emit any notifies; the
    // caller emits projectReset / projectOpened once at the end of its flow.
    viewport_->setSelectedObjectId(0);
    session_state_->setSelectedObjectId(0);
    for (uint32_t mid : session_state_->modelIds()) {
        viewport_->removeModel(mid);
        session_state_->loader()->removeModel(mid);
    }
    session_state_->clearModelMappings();
    session_state_->elementRegistry()->clear();
}

bool ProjectController::confirmDiscardIfDirty() {
    if (!session_state_->federation()->isDirty()) return true;
    const auto result = QMessageBox::question(
        host_, "Unsaved Project",
        "The current project has unsaved changes. Save before continuing?",
        QMessageBox::Save | QMessageBox::Discard | QMessageBox::Cancel,
        QMessageBox::Save);
    if (result == QMessageBox::Cancel) return false;
    if (result == QMessageBox::Save) return saveProject();
    return true;
}

} // namespace ifcviewerfull::modules::project
