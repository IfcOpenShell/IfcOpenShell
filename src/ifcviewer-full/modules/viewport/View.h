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

#ifndef IFCINTERFACE_MODULES_VIEWPORT_VIEW_H
#define IFCINTERFACE_MODULES_VIEWPORT_VIEW_H

#include <QObject>
#include <memory>

namespace ifcviewerfull { class SessionState; }
class ViewportWindow;
class AreaMeasurement;
class LengthMeasurement;

namespace ifcviewerfull::modules::viewport {

// Renders SessionState into the OpenGL viewport. Subscribes to session-level
// signals only; on each one it calls refresh() to re-derive viewport state
// (false origin, per-model coord op + transformation + visibility) from
// SessionState idempotently.
//
// Also owns the stateful measurement tools and subscribes to viewport input
// events for them. That's a distinct concern from the state-render side but
// kept here to avoid a second tiny QObject.
class ViewportView : public QObject {
    Q_OBJECT

public:
    explicit ViewportView(ifcviewerfull::SessionState* session_state,
                          ViewportWindow* viewport,
                          QObject* parent = nullptr);
    ~ViewportView() override;

private:
    void refresh();
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
