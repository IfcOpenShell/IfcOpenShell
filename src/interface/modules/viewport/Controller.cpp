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

#include "../../InterfaceSettings.h"
#include "../../SessionState.h"
#include "../../../ifcviewer/AppSettings.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"
#include "../../../ifcviewer/OverlayRenderer.h"
#include "../../../ifcviewer-full/Measurement.h"

#include <Eigen/Dense>
#include <QVector3D>

#include <vector>

namespace ifcinterface::modules::viewport {

ViewportController::ViewportController(ifcinterface::SessionState* session_state,
                                       ViewportWindow* viewport,
                                       QObject* parent)
    : QObject(parent)
    , session_state_(session_state)
    , viewport_(viewport)
    , area_measurement_(std::make_unique<AreaMeasurement>())
    , length_measurement_(std::make_unique<LengthMeasurement>())
{
    Federation* federation = session_state_->federation();
    SceneLoader* loader = session_state_->loader();
    connect(&ifcinterface::InterfaceSettings::instance(),
            &ifcinterface::InterfaceSettings::themeChanged,
            this, [this]() {
        viewport_->setBackgroundColor(QColor(ifcinterface::InterfaceSettings::instance().color("viewport_background")));
    });
    viewport_->setBackgroundColor(QColor(ifcinterface::InterfaceSettings::instance().color("viewport_background")));
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
    connect(viewport_, &ViewportWindow::surfacePickedInTool, this,
            [this](int x, int y, int modifiers) {
        const bool alt = (modifiers & Qt::AltModifier) != 0;
        switch (viewport_->toolMode()) {
        case ViewportWindow::ToolMode::Area:
            area_measurement_->onPick(*viewport_, x, y, alt);
            viewport_->setHudText(QString("Area: %1 m²  (%2 tris)")
                .arg(area_measurement_->totalArea(), 0, 'f', 4)
                .arg(area_measurement_->triangleCount()));
            break;
        case ViewportWindow::ToolMode::Length:
            length_measurement_->onPick(*viewport_, x, y, alt);
            break;
        case ViewportWindow::ToolMode::None:
        case ViewportWindow::ToolMode::Volume:
            break;
        }
    });
    connect(viewport_, &ViewportWindow::toolModeChanged, this,
            [this](ViewportWindow::ToolMode mode) {
        area_measurement_->clear(*viewport_);
        length_measurement_->clear(*viewport_);
        switch (mode) {
        case ViewportWindow::ToolMode::None:
            viewport_->setHudText(QString());
            viewport_->setOverlayLabels({});
            session_state_->setStatusMessage("Measure", "Measurement tool off");
            break;
        case ViewportWindow::ToolMode::Length:
            viewport_->setHudText("Length tool: click first point");
            session_state_->setStatusMessage("Measure", "Length tool: LMB add point, Backspace remove last, Esc exits");
            break;
        case ViewportWindow::ToolMode::Area:
            viewport_->setHudText("Area: 0.0000 m²  (0 tris)");
            session_state_->setStatusMessage("Measure", "Area tool: LMB add, Alt+LMB single tri, click again to remove, Esc exits");
            break;
        case ViewportWindow::ToolMode::Volume:
            session_state_->setStatusMessage("Measure", "Volume tool: click / box-select objects, Esc exits");
            updateVolumeReadout();
            break;
        }
    });
    connect(viewport_, &ViewportWindow::toolBackspacePressed, this, [this]() {
        if (viewport_->toolMode() == ViewportWindow::ToolMode::Length) {
            length_measurement_->removeLastPoint(*viewport_);
        }
    });
    connect(viewport_, &ViewportWindow::objectPicked, this, [this](uint32_t) {
        updateVolumeReadout();
    });
}

ViewportController::~ViewportController() = default;

void ViewportController::applyCoordinateOperation(uint32_t mid) {
    SceneLoader* loader = session_state_->loader();
    Eigen::Matrix4d matrix = Eigen::Matrix4d::Identity();
    if (const ModelGeoref* georef = loader->modelGeoref(mid)) {
        if (georef->has_coordinate_operation) {
            matrix = georef->coordinate_operation_meters;
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
                if (georef->has_coordinate_operation) {
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

void ViewportController::setFlyMode() {
    viewport_->requestActivate();
    viewport_->enterFpsMode();
    session_state_->setStatusMessage("Mode", "Fly mode active");
}

void ViewportController::toggleSectionMode() {
    viewport_->toggleSectionTool();
    if (viewport_->sectionToolActive()) {
        session_state_->setStatusMessage("Section", "Section tool active");
    } else {
        session_state_->setStatusMessage("Section", "Section tool off");
    }
}

void ViewportController::clearSectionPlanes() {
    viewport_->clearSectionPlanes();
    session_state_->setStatusMessage("Section", "Section planes cleared");
}

void ViewportController::toggleDistanceMode() {
    viewport_->toggleLengthTool();
}

void ViewportController::toggleAreaMode() {
    viewport_->toggleAreaTool();
}

void ViewportController::toggleVolumeMode() {
    viewport_->toggleVolumeTool();
}

void ViewportController::focusSelectedObject() {
    viewport_->focusOnSelectedObject();
}

void ViewportController::hideSelectedElements() {
    viewport_->hideSelectedElements();
}

void ViewportController::isolateSelectedElements() {
    viewport_->isolateSelectedElements();
}

void ViewportController::showAllElements() {
    viewport_->showAllElements();
}

void ViewportController::invertSelection() {
    viewport_->invertElementVisibility();
}

void ViewportController::updateVolumeReadout() {
    if (viewport_->toolMode() != ViewportWindow::ToolMode::Volume) return;

    const auto& sel = viewport_->selection().selectionIds();
    if (sel.empty()) {
        viewport_->setHudText(QString());
        viewport_->setOverlayLabels({});
        return;
    }

    std::vector<uint32_t> ids(sel.begin(), sel.end());
    const auto per_obj = volumesPerObject(*viewport_, ids);

    double total = 0.0;
    std::vector<OverlayRenderer::Label> labels;
    labels.reserve(per_obj.size());
    for (const auto& [oid, v] : per_obj) {
        total += v;
        QVector3D mn, mx;
        if (!viewport_->computeObjectAabb(oid, mn, mx)) continue;
        OverlayRenderer::Label lbl;
        const QVector3D c = (mn + mx) * 0.5f;
        lbl.world_pos[0] = c.x();
        lbl.world_pos[1] = c.y();
        lbl.world_pos[2] = c.z();
        lbl.text = QString::number(v, 'f', 4) + " m³";
        labels.push_back(std::move(lbl));
    }

    viewport_->setHudText(QString("Volume: %1 m³  (%2 object%3)")
        .arg(total, 0, 'f', 4)
        .arg(per_obj.size())
        .arg(per_obj.size() == 1 ? "" : "s"));
    viewport_->setOverlayLabels(labels);
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
        *placement, *georef, federation->config()));
}

} // namespace ifcinterface::modules::viewport
