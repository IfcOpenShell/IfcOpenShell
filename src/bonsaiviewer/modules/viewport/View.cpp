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

#include "View.h"

#include "../../ViewerSettings.h"
#include "../../SessionState.h"
#include "../models/Commands.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"
#include "../../../ifcviewer/OverlayRenderer.h"
#include "../../Measurement.h"

#include <Eigen/Dense>

#include <vector>

namespace bonsaiviewer::modules::viewport {

ViewportView::ViewportView(bonsaiviewer::SessionState* session_state,
                           ViewportWindow* viewport,
                           QObject* parent)
    : QObject(parent)
    , session_state_(session_state)
    , viewport_(viewport)
    , area_measurement_(std::make_unique<AreaMeasurement>())
    , length_measurement_(std::make_unique<LengthMeasurement>())
{
    auto& settings = bonsaiviewer::ViewerSettings::instance();
    connect(&settings, &bonsaiviewer::ViewerSettings::themeChanged, this, [this]() {
        viewport_->setBackgroundColor(
            QColor(bonsaiviewer::ViewerSettings::instance().color("viewport_background")));
    });
    viewport_->setBackgroundColor(QColor(settings.color("viewport_background")));

    connect(session_state_, &SessionState::projectReset,           this, &ViewportView::refresh);
    connect(session_state_, &SessionState::projectOpened,          this, [this](const QString&) { refresh(); });
    connect(session_state_, &SessionState::modelsChanged,          this, &ViewportView::refresh);
    connect(session_state_, &SessionState::federationChanged,      this, &ViewportView::refresh);
    connect(session_state_, &SessionState::visibilityChanged,      this, &ViewportView::refresh);
    // modelGeometryReady is the right hook for "a model finished loading"
    // — by this point the loader has populated firstPlacement/modelGeoref,
    // so the guess has the data it needs. Whether to actually guess is
    // gated by the arm-flag set by the add-model commands when they're
    // adding into an empty session (so batch-adds work too: arm once,
    // first geometry-ready consumes the arm). refresh() stays terminal —
    // any federation mutation from the guess propagates through
    // SessionState's federatedFalseOriginChanged relay.
    connect(session_state_, &SessionState::modelGeometryReady,     this, [this](uint32_t mid) {
        if (modules::models::consumeFederatedFalseOriginGuess()) {
            guessFederatedFalseOriginFromFirstModel(mid);
        }
        refresh();
    });

    // Measurement tools — input-driven, share the View's lifetime.
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
        case ViewportWindow::ToolMode::NoTool:
        case ViewportWindow::ToolMode::Volume:
            break;
        }
    });
    connect(viewport_, &ViewportWindow::toolModeChanged, this,
            [this](ViewportWindow::ToolMode mode) {
        area_measurement_->clear(*viewport_);
        length_measurement_->clear(*viewport_);
        switch (mode) {
        case ViewportWindow::ToolMode::NoTool:
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

    refresh();
}

ViewportView::~ViewportView() = default;

void ViewportView::refresh() {
    Federation* federation = session_state_->federation();
    viewport_->setFederatedFalseOrigin(
        composeFederatedFalseOrigin(federation->federatedFalseOrigin(), federation->config()));

    for (uint32_t mid : session_state_->modelIds()) {
        applyCoordinateOperation(mid);
        applyModelVisibility(mid);
    }
}

void ViewportView::applyCoordinateOperation(uint32_t mid) {
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

void ViewportView::applyModelTransformation(uint32_t mid) {
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

void ViewportView::applyModelVisibility(uint32_t mid) {
    Federation* federation = session_state_->federation();
    const QString fed_id = session_state_->fedIdForModelId(mid);
    if (fed_id.isEmpty()) return;

    if (federation->isModelEffectivelyVisible(fed_id)) {
        viewport_->showModel(mid);
    } else {
        viewport_->hideModel(mid);
    }
}

// Apply the federation false-origin guess from this model's first
// placement. Called only when the add-model command armed the guess
// (i.e. it was adding into an empty session); see the modelGeometryReady
// connection above and modules::models::armFederatedFalseOriginGuess().
//
// The internal guards (filePath, default origin, placement/georef
// presence) are defense-in-depth, not the primary gate — that's the arm.
// Order of checks matters: filePath skip protects project files
// (federation owns origin); current==defaults skip protects a user who
// previously set the origin manually and only later removed the model;
// nullptr placement/georef skip handles loads where the loader hasn't
// surfaced data yet (rare given the modelGeometryReady contract).
//
// Lives off the refresh() fan-in deliberately. refresh() is connected to
// half a dozen signals; calling a federation mutator from inside it
// stack-overflowed BonsaiViewer once the guess returned defaults because
// the mutation re-emitted through SessionState → re-entered refresh().
// Guessing only on the modelGeometryReady edge means a Federation
// mutation here propagates through SessionState's federation relay
// (federatedFalseOriginChanged → notifyFederationChanged) without
// re-entering this function.
void ViewportView::guessFederatedFalseOriginFromFirstModel(uint32_t mid) {
    Federation* federation = session_state_->federation();
    if (!federation->filePath().isEmpty()) return;

    const FederatedFalseOrigin& current = federation->federatedFalseOrigin();
    const FederatedFalseOrigin defaults;
    if (current.xyz != defaults.xyz || current.rz_deg != defaults.rz_deg) return;

    Eigen::Vector3d first_geometry_point_m;
    if (!viewport_->firstGeometryPointWorldM(mid, first_geometry_point_m)) return;

    SceneLoader* loader = session_state_->loader();
    const ModelGeoref* georef = loader->modelGeoref(mid);
    if (georef == nullptr) return;

    federation->setFederatedFalseOrigin(::guessFederatedFalseOrigin(
        first_geometry_point_m, *georef, federation->config()));

    // applyCachedModel's auto-viewAll already framed the camera against
    // the pre-shift (surveyor) coordinates. The setFederatedFalseOrigin
    // call above propagated through SessionState's federation relay →
    // refresh() → viewport->setFederatedFalseOrigin → recomposeAndUpload
    // (all synchronous Qt direct connections), which rewrote every
    // instance's world AABB to its post-shift position. Re-target on
    // (0,0,0) — the federated false origin in render space — capped at
    // 100 m so a model with crazy-coord geometry can't pull the camera
    // back into nothing.
    viewport_->frameOnFederatedOrigin(mid, 100.0f);
}

void ViewportView::updateVolumeReadout() {
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
        Eigen::Vector3f mn, mx;
        if (!viewport_->computeObjectAabb(oid, mn, mx)) continue;
        OverlayRenderer::Label lbl;
        const Eigen::Vector3f c = (mn + mx) * 0.5f;
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

} // namespace bonsaiviewer::modules::viewport
