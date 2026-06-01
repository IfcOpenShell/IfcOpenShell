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

#include "../../SessionState.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer-wgpu/WgpuViewportWindow.h"

namespace bonsaiviewer::modules::viewport::commands {

void setHome(SessionState& session, WgpuViewportWindow& vp) {
    auto camera = vp.cameraState();
    Federation::HomeView home_view;
    home_view.target = camera.target;
    home_view.distance = camera.distance;
    home_view.yaw = camera.yaw;
    home_view.pitch = camera.pitch;
    session.federation()->setHomeView(home_view);
    session.setStatusMessage("Camera", "Home view updated");
}

void goHome(SessionState& session, WgpuViewportWindow& vp) {
    Federation* federation = session.federation();
    if (!federation->hasHomeView()) {
        session.setStatusMessage("Camera", "No home view set for this project");
        return;
    }
    const auto& home_view = federation->homeView();
    vp.setCamera(
        home_view.target.x(), home_view.target.y(), home_view.target.z(),
        home_view.distance, home_view.yaw, home_view.pitch);
    session.setStatusMessage("Camera", "Home view restored");
}

void viewSelected(WgpuViewportWindow& vp) {
    vp.focusOnSelectedObject();
}

void fly(SessionState& session, WgpuViewportWindow& vp) {
    vp.requestActivate();
    vp.enterFpsMode();
    session.setStatusMessage("Mode", "Fly mode active");
}

void toggleSection(SessionState& session, WgpuViewportWindow& vp) {
    vp.toggleSectionTool();
    session.setStatusMessage("Section",
        vp.sectionToolActive() ? "Section tool active" : "Section tool off");
}

void clearSection(SessionState& session, WgpuViewportWindow& vp) {
    vp.clearSectionPlanes();
    session.setStatusMessage("Section", "Section planes cleared");
}

void toggleDistance(WgpuViewportWindow& vp) {
    vp.toggleLengthTool();
}

void toggleArea(WgpuViewportWindow& vp) {
    vp.toggleAreaTool();
}

void toggleVolume(WgpuViewportWindow& vp) {
    vp.toggleVolumeTool();
}

void hideSelected(WgpuViewportWindow& vp) {
    vp.hideSelectedElements();
}

void isolateSelected(WgpuViewportWindow& vp) {
    vp.isolateSelectedElements();
}

void showAll(WgpuViewportWindow& vp) {
    vp.showAllElements();
}

void invertVisibility(WgpuViewportWindow& vp) {
    vp.invertElementVisibility();
}

} // namespace bonsaiviewer::modules::viewport::commands
