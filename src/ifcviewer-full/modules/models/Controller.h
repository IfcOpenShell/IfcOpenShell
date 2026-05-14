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

#ifndef IFCINTERFACE_PANELS_MODELSPANELCONTROLLER_H
#define IFCINTERFACE_PANELS_MODELSPANELCONTROLLER_H

#include "Types.h"

#include <QObject>
#include <QStringList>

class QWidget;
namespace ifcviewerfull { class SessionState; }
class ViewportWindow;
class SceneLoader;

namespace ifcviewerfull::modules::models {

class ModelsPanel;

class ModelsPanelController : public QObject {
    Q_OBJECT

public:
    explicit ModelsPanelController(QWidget* host,
                                   ModelsPanel* widget,
                                   ifcviewerfull::SessionState* session_state,
                                   ViewportWindow* viewport,
                                   QObject* parent = nullptr);

    void bindLoader(SceneLoader* loader);
    void addFiles();
    void addFiles(const QStringList& paths);
    void loadModels(const QStringList& paths, const QStringList& fed_ids);
    void removeLoadedModel(const QString& fed_id);
    void openSettings();

private:
    QString formatElapsed(qint64 ms) const;
    void writeSidecarForModel(SceneLoader* loader, uint32_t mid) const;

    QWidget* host_ = nullptr;
    ModelsPanel* widget_ = nullptr;
    ifcviewerfull::SessionState* session_state_ = nullptr;
    ViewportWindow* viewport_ = nullptr;
};

} // namespace ifcviewerfull::modules::models

#endif
