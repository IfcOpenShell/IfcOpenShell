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

#include "../../ElementRegistry.h"
#include "../../SessionState.h"
#include "../models/Commands.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"

#include <QFileDialog>
#include <QFileInfo>
#include <QMessageBox>

namespace ifcviewerfull::modules::project::commands {

namespace {

// Pure helper — clears the loaded scene without emitting any signals. The
// caller (newProject / openProject) emits projectReset / projectOpened once
// the whole flow finishes.
void clearScene(SessionState& s, ViewportWindow& vp) {
    vp.setSelectedObjectId(0);
    s.setSelectedObjectId(0);
    for (uint32_t mid : s.modelIds()) {
        vp.removeModel(mid);
        s.loader()->removeModel(mid);
    }
    s.clearModelMappings();
    s.elementRegistry()->clear();
}

// Returns false if the user cancelled (i.e. don't proceed with the destructive
// op). Handles the Save → Discard → Cancel branch including a follow-on save.
bool confirmDiscardIfDirty(SessionState& s, QWidget& host) {
    if (!s.federation()->isDirty()) return true;
    const auto result = QMessageBox::question(
        &host, "Unsaved Project",
        "The current project has unsaved changes. Save before continuing?",
        QMessageBox::Save | QMessageBox::Discard | QMessageBox::Cancel,
        QMessageBox::Save);
    if (result == QMessageBox::Cancel) return false;
    if (result == QMessageBox::Save) return saveProject(s, host);
    return true;
}

bool openProjectAt(SessionState& s, QWidget& host, ViewportWindow& vp, const QString& path) {
    SceneLoader* loader = s.loader();
    if (loader && loader->isLoading()) {
        QMessageBox::information(
            &host, "Open Project",
            "Wait until the current model load finishes before opening another project.");
        return false;
    }
    if (!confirmDiscardIfDirty(s, host)) return false;

    QStringList warnings;
    QString err;
    if (!s.federation()->load(path, &warnings, &err)) {
        QMessageBox::warning(&host, "Open Project",
                             QString("Could not open project:\n%1").arg(err));
        return false;
    }

    clearScene(s, vp);

    QStringList paths;
    QStringList fed_ids;
    for (const auto& model : s.federation()->models()) {
        if (model.source_kind != "local") continue;
        if (!QFileInfo::exists(model.source_path)) {
            warnings << QString("Source not found, kept in project: %1").arg(model.source_path);
            continue;
        }
        paths << model.source_path;
        fed_ids << model.id;
    }
    modules::models::commands::detail::loadModels(s, paths, fed_ids);

    if (!warnings.isEmpty()) {
        QMessageBox::warning(&host, "Open Project",
                             "Project opened with warnings:\n\n" + warnings.join("\n"));
    }

    s.federation()->markClean();
    if (s.federation()->hasHomeView()) {
        const auto& hv = s.federation()->homeView();
        vp.setCamera(hv.target.x(), hv.target.y(), hv.target.z(),
                     hv.distance, hv.yaw, hv.pitch);
    }
    s.setStatusMessage("Project", QFileInfo(path).fileName());
    s.notifyProjectOpened(path);
    return true;
}

bool saveProjectTo(SessionState& s, QWidget& host, const QString& path) {
    QString err;
    if (!s.federation()->save(path, &err)) {
        QMessageBox::warning(&host, "Save Project",
                             QString("Could not save project:\n%1").arg(err));
        return false;
    }
    s.setStatusMessage("Project", QFileInfo(path).fileName());
    s.notifyProjectSaved(path);
    return true;
}

} // namespace

bool newProject(SessionState& s, QWidget& host, ViewportWindow& vp) {
    SceneLoader* loader = s.loader();
    if (loader && loader->isLoading()) {
        QMessageBox::information(
            &host, "New Project",
            "Wait until the current model load finishes before creating a new project.");
        return false;
    }
    if (!confirmDiscardIfDirty(s, host)) return false;

    clearScene(s, vp);
    s.federation()->clear();
    s.setStatusMessage("Project", "Untitled");
    s.notifyProjectReset();
    return true;
}

bool openProject(SessionState& s, QWidget& host, ViewportWindow& vp) {
    QFileDialog file_dialog(&host, "Open Project");
    file_dialog.setFileMode(QFileDialog::ExistingFile);
    file_dialog.setNameFilter("IFC Federation (*.ifcfed);;All Files (*)");
    file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (file_dialog.exec() != QDialog::Accepted) return false;

    const QString path = file_dialog.selectedFiles().value(0);
    if (path.isEmpty()) return false;
    return openProjectAt(s, host, vp, path);
}

bool saveProject(SessionState& s, QWidget& host) {
    if (s.federation()->filePath().isEmpty()) return saveProjectAs(s, host);
    return saveProjectTo(s, host, s.federation()->filePath());
}

bool saveProjectAs(SessionState& s, QWidget& host) {
    QString suggested = s.federation()->filePath();
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
    return saveProjectTo(s, host, path);
}

} // namespace ifcviewerfull::modules::project::commands
