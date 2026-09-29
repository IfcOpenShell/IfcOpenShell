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

#include "WebFederation.h"

#include "Log.h"
#include "ViewportCore.h"

void WebFederation::setConfig(const FederationConfig& cfg) {
    config_ = cfg;
    // The unit is the value space for the false origin and every model
    // transform, so changing it re-scales both.
    applyFalseOrigin();
    for (const auto& [source_id, state] : models_) {
        if (state.has_transformation) applyModelTransformation(source_id);
    }
}

void WebFederation::setFalseOrigin(const FederatedFalseOrigin& origin) {
    false_origin_          = origin;
    false_origin_explicit_ = true;
    applyFalseOrigin();
}

void WebFederation::setModelTransformation(int source_id, const ModelTransformation& xf) {
    ModelState& state       = models_[source_id];
    state.transformation     = xf;
    state.has_transformation = true;
    applyModelTransformation(source_id);
}

void WebFederation::clearModelTransformation(int source_id) {
    auto it = models_.find(source_id);
    if (it == models_.end() || !it->second.has_transformation) return;
    it->second.has_transformation = false;
    it->second.transformation     = ModelTransformation{};
    if (it->second.session_model_id != 0) {
        core_.setModelTransformation(it->second.session_model_id,
                                     Eigen::Matrix4d::Identity());
    }
}

void WebFederation::setModelName(int source_id, std::string name) {
    models_[source_id].name = std::move(name);
}

std::string WebFederation::modelName(int source_id) const {
    auto it = models_.find(source_id);
    return it == models_.end() ? std::string() : it->second.name;
}

std::uint32_t WebFederation::sessionModelId(int source_id) const {
    auto it = models_.find(source_id);
    return it == models_.end() ? 0u : it->second.session_model_id;
}

void WebFederation::onModelLoaded(int source_id, std::uint32_t session_model_id) {
    ModelState& state     = models_[source_id];
    state.session_model_id = session_model_id;

    // Guess before applying the transform: the guess reads the model's raw
    // geometry position, and the transform is composed against the origin the
    // guess produces. Doing it the other way round would compose against the
    // identity origin and then need a second recompose.
    if (!false_origin_explicit_ && !guessed_false_origin_) {
        guessFalseOriginFrom(session_model_id);
    }
    if (state.has_transformation) applyModelTransformation(source_id);
}

void WebFederation::onModelLoadedWithoutSource(std::uint32_t session_model_id) {
    if (!false_origin_explicit_ && !guessed_false_origin_) {
        guessFalseOriginFrom(session_model_id);
    }
}

void WebFederation::clear() {
    models_.clear();
    config_                = FederationConfig{};
    false_origin_          = FederatedFalseOrigin{};
    false_origin_explicit_ = false;
    guessed_false_origin_  = false;
    core_.setFederatedFalseOrigin(Eigen::Matrix4d::Identity());
}

void WebFederation::applyFalseOrigin() {
    core_.setFederatedFalseOrigin(composeFederatedFalseOrigin(false_origin_, config_));
}

void WebFederation::applyModelTransformation(int source_id) {
    auto it = models_.find(source_id);
    if (it == models_.end() || !it->second.has_transformation) return;
    const std::uint32_t session_model_id = it->second.session_model_id;
    if (session_model_id == 0) return;   // staged; applied from onModelLoaded

    // ModelTransformation::a may be authored in the model's pre-CoordinateOperation
    // frame, so composing needs the model's units and CoordinateOperation. Both
    // come from the sidecar, which is what makes this work with no IFC present.
    ModelGeoref georef;
    if (!core_.modelGeoref(session_model_id, georef)) return;

    core_.setModelTransformation(
        session_model_id,
        composeModelTransformation(it->second.transformation, config_,
                                   georef.units,
                                   georef.coordinate_operation_meters));
}

void WebFederation::guessFalseOriginFrom(std::uint32_t session_model_id) {
    Eigen::Vector3d first_geometry_point_m;
    if (!core_.firstGeometryPointWorldM(session_model_id, first_geometry_point_m)) return;

    ModelGeoref georef;
    if (!core_.modelGeoref(session_model_id, georef)) return;

    // Why this is on by default rather than opt-in: the composed per-instance
    // transform is float32 (InstanceInfo::transform). Now that applyCachedModel
    // seeds the CoordinateOperation, an un-shifted georeferenced model renders
    // at its surveyor coordinates, where float precision is ~0.5 m per ULP
    // around 6e6 m — visibly worse than the local-coordinates behaviour this
    // replaced. Resolving to global coordinates only makes sense together with
    // an origin shift.
    false_origin_ = guessFederatedFalseOrigin(first_geometry_point_m, georef, config_);
    guessed_false_origin_ = true;
    applyFalseOrigin();

    // applyCachedModel's auto-viewAll framed the camera against the pre-shift
    // position; the recompose above moved every instance, so re-frame.
    core_.viewAll();

    Log::info().nospace()
        << "web federation: guessed false origin ("
        << false_origin_.xyz.x() << ", " << false_origin_.xyz.y() << ", "
        << false_origin_.xyz.z() << ") rz=" << false_origin_.rz_deg << "deg";
}
