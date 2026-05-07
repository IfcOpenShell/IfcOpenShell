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

#include "../../../ifcviewer/AppSettings.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"

#include <Eigen/Dense>

namespace ifcinterface::panels::viewport {

ViewportController::ViewportController(Federation* federation,
                                       SceneLoader* loader,
                                       ViewportWindow* viewport,
                                       const QHash<QString, uint32_t>* fed_id_to_model_id,
                                       const QHash<uint32_t, QString>* model_id_to_fed_id,
                                       QObject* parent)
    : QObject(parent)
    , federation_(federation)
    , loader_(loader)
    , viewport_(viewport)
    , fed_id_to_model_id_(fed_id_to_model_id)
    , model_id_to_fed_id_(model_id_to_fed_id)
{
    connect(federation_, &Federation::federatedFalseOriginChanged,
            this, &ViewportController::applyFederatedFalseOrigin);
    connect(federation_, &Federation::configChanged, this, [this]() {
        applyFederatedFalseOrigin();
        for (auto it = model_id_to_fed_id_->cbegin(); it != model_id_to_fed_id_->cend(); ++it) {
            applyModelTransformation(it.key());
        }
    });
    connect(federation_, &Federation::modelTransformationChanged,
            this, [this](const QString& fed_id) {
        auto it = fed_id_to_model_id_->find(fed_id);
        if (it != fed_id_to_model_id_->end()) {
            applyModelTransformation(it.value());
        }
    });
    connect(loader_, &SceneLoader::loadedFromSidecar, this,
            [this](uint32_t mid, qint64 /*elapsed_ms*/) {
        applyCoordinateOperation(mid);
        maybeGuessFederatedFalseOrigin(mid);
    });
    connect(loader_, &SceneLoader::dataSourceReady, this,
            [this](uint32_t mid) {
        applyCoordinateOperation(mid);
    });
    connect(loader_, &SceneLoader::loadedFromStream, this,
            [this](uint32_t mid, qint64 /*elapsed_ms*/) {
        applyCoordinateOperation(mid);
        maybeGuessFederatedFalseOrigin(mid);
    });
    connect(&AppSettings::instance(),
            &AppSettings::applyCoordinateOperationChanged,
            this, [this](bool /*enabled*/) {
        for (auto it = model_id_to_fed_id_->cbegin(); it != model_id_to_fed_id_->cend(); ++it) {
            applyCoordinateOperation(it.key());
        }
    });
}

void ViewportController::applyCoordinateOperation(uint32_t mid) {
    Eigen::Matrix4d matrix = Eigen::Matrix4d::Identity();
    if (AppSettings::instance().applyCoordinateOperation()) {
        if (const ModelGeoref* georef = loader_->modelGeoref(mid)) {
            if (georef->has_coordinate_operation) {
                matrix = georef->coordinate_operation_meters;
            }
        }
    }
    viewport_->setModelCoordinateOperation(mid, matrix);
    applyModelTransformation(mid);
}

void ViewportController::applyModelTransformation(uint32_t mid) {
    Eigen::Matrix4d matrix = Eigen::Matrix4d::Identity();
    auto fed_it = model_id_to_fed_id_->find(mid);
    if (fed_it != model_id_to_fed_id_->end()) {
        if (const Federation::Model* model = federation_->findById(fed_it.value())) {
            ModelUnits units;
            Eigen::Matrix4d coordinate_operation = Eigen::Matrix4d::Identity();
            if (const ModelGeoref* georef = loader_->modelGeoref(mid)) {
                units = georef->units;
                if (AppSettings::instance().applyCoordinateOperation() &&
                    georef->has_coordinate_operation) {
                    coordinate_operation = georef->coordinate_operation_meters;
                }
            }
            matrix = composeModelTransformation(
                model->model_transformation, federation_->config(), units, coordinate_operation);
        }
    }
    viewport_->setModelTransformation(mid, matrix);
}

void ViewportController::applyFederatedFalseOrigin() {
    viewport_->setFederatedFalseOrigin(
        composeFederatedFalseOrigin(federation_->federatedFalseOrigin(), federation_->config()));
}

void ViewportController::maybeGuessFederatedFalseOrigin(uint32_t mid) {
    if (!federation_->filePath().isEmpty()) return;

    const FederatedFalseOrigin& current = federation_->federatedFalseOrigin();
    const FederatedFalseOrigin defaults;
    if (current.xyz != defaults.xyz || current.rz_deg != defaults.rz_deg) return;

    const Eigen::Matrix4d* placement = loader_->firstPlacement(mid);
    const ModelGeoref* georef = loader_->modelGeoref(mid);
    if (placement == nullptr || georef == nullptr) return;

    federation_->setFederatedFalseOrigin(guessFederatedFalseOrigin(
        *placement, *georef, federation_->config(),
        AppSettings::instance().applyCoordinateOperation()));
}

} // namespace ifcinterface::panels::viewport
