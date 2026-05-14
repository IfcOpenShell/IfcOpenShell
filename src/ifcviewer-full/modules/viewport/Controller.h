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
#include <memory>

namespace ifcviewerfull { class SessionState; }
class ViewportWindow;
class AreaMeasurement;
class LengthMeasurement;

namespace ifcviewerfull::modules::viewport {

class ViewportController : public QObject {
    Q_OBJECT

public:
    explicit ViewportController(ifcviewerfull::SessionState* session_state,
                                ViewportWindow* viewport,
                                QObject* parent = nullptr);
    ~ViewportController() override;

    void applyFederatedFalseOrigin();
    void setHomeView();
    void goHomeView();
    void setFlyMode();
    void toggleSectionMode();
    void clearSectionPlanes();
    void toggleDistanceMode();
    void toggleAreaMode();
    void toggleVolumeMode();
    void focusSelectedObject();
    void hideSelectedElements();
    void isolateSelectedElements();
    void showAllElements();
    void invertSelection();

private:
    void applyCoordinateOperation(uint32_t mid);
    void applyModelTransformation(uint32_t mid);
    void applyModelVisibility(uint32_t mid);
    void maybeGuessFederatedFalseOrigin(uint32_t mid);
    void updateVolumeReadout();

    ifcviewerfull::SessionState* session_state_ = nullptr;
    ViewportWindow* viewport_ = nullptr;
    std::unique_ptr<AreaMeasurement> area_measurement_;
    std::unique_ptr<LengthMeasurement> length_measurement_;
};

} // namespace ifcviewerfull::modules::viewport

#endif
