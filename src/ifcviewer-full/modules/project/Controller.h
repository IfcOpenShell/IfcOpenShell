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

#ifndef IFCINTERFACE_PANELS_PROJECT_CONTROLLER_H
#define IFCINTERFACE_PANELS_PROJECT_CONTROLLER_H

#include <QObject>

class QWidget;
class ViewportWindow;
namespace ifcviewerfull { class SessionState; }

namespace ifcviewerfull::modules::project {

class ProjectController : public QObject {
    Q_OBJECT

public:
    explicit ProjectController(QWidget* host,
                               ifcviewerfull::SessionState* session_state,
                               ViewportWindow* viewport,
                               QObject* parent = nullptr);

    bool newProject();
    bool openProject();
    bool saveProject();
    bool saveProjectAs();

private:
    bool openProject(const QString& path);
    bool saveProjectAs(const QString& path);
    void clearScene();
    bool confirmDiscardIfDirty();

    QWidget* host_ = nullptr;
    ifcviewerfull::SessionState* session_state_ = nullptr;
    ViewportWindow* viewport_ = nullptr;
};

} // namespace ifcviewerfull::modules::project

#endif
