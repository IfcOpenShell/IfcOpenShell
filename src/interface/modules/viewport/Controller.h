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

#ifndef IFCINTERFACE_PANELS_VIEWPORT_CONTROLLER_H
#define IFCINTERFACE_PANELS_VIEWPORT_CONTROLLER_H

#include <QObject>

namespace ifcinterface { class SessionState; }
class ViewportWindow;

namespace ifcinterface::modules::viewport {

class ViewportController : public QObject {
    Q_OBJECT

public:
    explicit ViewportController(ifcinterface::SessionState* session_state,
                                ViewportWindow* viewport,
                                QObject* parent = nullptr);

    void applyFederatedFalseOrigin();
    void setHomeView();
    void goHomeView();

private:
    void applyCoordinateOperation(uint32_t mid);
    void applyModelTransformation(uint32_t mid);
    void applyModelVisibility(uint32_t mid);
    void maybeGuessFederatedFalseOrigin(uint32_t mid);

    ifcinterface::SessionState* session_state_ = nullptr;
    ViewportWindow* viewport_ = nullptr;
};

} // namespace ifcinterface::modules::viewport

#endif
