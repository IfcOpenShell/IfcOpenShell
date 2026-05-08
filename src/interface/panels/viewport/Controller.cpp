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

#include "../../SessionState.h"
#include "../../../ifcviewer/AppSettings.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"

#include <Eigen/Dense>

namespace ifcinterface::panels::viewport {

ViewportController::ViewportController(ifcinterface::SessionState* session_state,
                                       ViewportWindow* viewport,
                                       QObject* parent)
    : QObject(parent)
    , session_state_(session_state)
    , viewport_(viewport)
{
    Federation* federation = session_state_->federation();
    SceneLoader* loader = session_state_->loader();
    connect(federation, &Federation::federatedFalseOriginChanged,
            this, &ViewportController::applyFederatedFalseOrigin);
    connect(federation, &Federation::configChanged, this, [this]() {
        applyFederatedFalseOrigin();
        for (uint32_t mid : session_state_->modelIds()) {
            applyModelTransformation(mid);
        }
    });
    connect(federation, &Federation::modelTransformationChanged,
            this, [this](const QString& fed_id) {
        const uint32_t mid = session_state_->modelIdForFedId(fed_id);
        if (mid != 0) applyModelTransformation(mid);
    });
    connect(federation, &Federation::modelVisibilityChanged,
            this, [this](const QString& fed_id, bool /*visible*/) {
        const uint32_t mid = session_state_->modelIdForFedId(fed_id);
        if (mid != 0) applyModelVisibility(mid);
    });
    connect(federation, &Federation::modelGroupChanged,
            this, [this](const QString& fed_id, const QString& /*group_id*/) {
        const uint32_t mid = session_state_->modelIdForFedId(fed_id);
        if (mid != 0) applyModelVisibility(mid);
    });
    connect(federation, &Federation::groupVisibilityChanged,
            this, [this](const QString&, bool /*visible*/) {
        for (uint32_t mid : session_state_->modelIds()) {
            applyModelVisibility(mid);
        }
    });
    connect(loader, &SceneLoader::loadedFromSidecar, this,
            [this](uint32_t mid, qint64 /*elapsed_ms*/) {
        applyCoordinateOperation(mid);
        applyModelVisibility(mid);
        maybeGuessFederatedFalseOrigin(mid);
    });
    connect(loader, &SceneLoader::dataSourceReady, this,
            [this](uint32_t mid) {
        applyCoordinateOperation(mid);
    });
    connect(loader, &SceneLoader::loadedFromStream, this,
            [this](uint32_t mid, qint64 /*elapsed_ms*/) {
        applyCoordinateOperation(mid);
        applyModelVisibility(mid);
        maybeGuessFederatedFalseOrigin(mid);
    });
    connect(&AppSettings::instance(),
            &AppSettings::applyCoordinateOperationChanged,
            this, [this](bool /*enabled*/) {
        for (uint32_t mid : session_state_->modelIds()) {
            applyCoordinateOperation(mid);
        }
    });
}

void ViewportController::applyCoordinateOperation(uint32_t mid) {
    SceneLoader* loader = session_state_->loader();
    Eigen::Matrix4d matrix = Eigen::Matrix4d::Identity();
    if (AppSettings::instance().applyCoordinateOperation()) {
        if (const ModelGeoref* georef = loader->modelGeoref(mid)) {
            if (georef->has_coordinate_operation) {
                matrix = georef->coordinate_operation_meters;
            }
        }
    }
    viewport_->setModelCoordinateOperation(mid, matrix);
    applyModelTransformation(mid);
}

void ViewportController::applyModelTransformation(uint32_t mid) {
    Federation* federation = session_state_->federation();
    SceneLoader* loader = session_state_->loader();
    Eigen::Matrix4d matrix = Eigen::Matrix4d::Identity();
    const QString fed_id = session_state_->fedIdForModelId(mid);
    if (!fed_id.isEmpty()) {
        if (const Federation::Model* model = federation->findById(fed_id)) {
            ModelUnits units;
            Eigen::Matrix4d coordinate_operation = Eigen::Matrix4d::Identity();
            if (const ModelGeoref* georef = loader->modelGeoref(mid)) {
                units = georef->units;
                if (AppSettings::instance().applyCoordinateOperation() &&
                    georef->has_coordinate_operation) {
                    coordinate_operation = georef->coordinate_operation_meters;
                }
            }
            matrix = composeModelTransformation(
                model->model_transformation, federation->config(), units, coordinate_operation);
        }
    }
    viewport_->setModelTransformation(mid, matrix);
}

void ViewportController::applyModelVisibility(uint32_t mid) {
    Federation* federation = session_state_->federation();
    const QString fed_id = session_state_->fedIdForModelId(mid);
    if (fed_id.isEmpty()) return;

    if (federation->isModelEffectivelyVisible(fed_id)) {
        viewport_->showModel(mid);
    } else {
        viewport_->hideModel(mid);
    }
}

void ViewportController::applyFederatedFalseOrigin() {
    Federation* federation = session_state_->federation();
    viewport_->setFederatedFalseOrigin(
        composeFederatedFalseOrigin(federation->federatedFalseOrigin(), federation->config()));
}

void ViewportController::setHomeView() {
    auto camera = viewport_->cameraState();
    Federation::HomeView home_view;
    home_view.target = camera.target;
    home_view.distance = camera.distance;
    home_view.yaw = camera.yaw;
    home_view.pitch = camera.pitch;
    session_state_->federation()->setHomeView(home_view);
    session_state_->setStatusMessage("Camera", "Home view updated");
}

void ViewportController::goHomeView() {
    Federation* federation = session_state_->federation();
    if (!federation->hasHomeView()) {
        session_state_->setStatusMessage("Camera", "No home view set for this project");
        return;
    }

    const auto& home_view = federation->homeView();
    viewport_->setCamera(
        home_view.target.x(), home_view.target.y(), home_view.target.z(),
        home_view.distance, home_view.yaw, home_view.pitch);
    session_state_->setStatusMessage("Camera", "Home view restored");
}

void ViewportController::maybeGuessFederatedFalseOrigin(uint32_t mid) {
    Federation* federation = session_state_->federation();
    SceneLoader* loader = session_state_->loader();
    if (!federation->filePath().isEmpty()) return;

    const FederatedFalseOrigin& current = federation->federatedFalseOrigin();
    const FederatedFalseOrigin defaults;
    if (current.xyz != defaults.xyz || current.rz_deg != defaults.rz_deg) return;

    const Eigen::Matrix4d* placement = loader->firstPlacement(mid);
    const ModelGeoref* georef = loader->modelGeoref(mid);
    if (placement == nullptr || georef == nullptr) return;

    federation->setFederatedFalseOrigin(guessFederatedFalseOrigin(
        *placement, *georef, federation->config(),
        AppSettings::instance().applyCoordinateOperation()));
}

} // namespace ifcinterface::panels::viewport
