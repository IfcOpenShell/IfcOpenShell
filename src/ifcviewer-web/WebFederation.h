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

#ifndef WEBFEDERATION_H
#define WEBFEDERATION_H

#include "FederationMath.h"

#include <cstdint>
#include <string>
#include <unordered_map>

class ViewportCore;

// Federation state for the web viewer: the concepts a host page needs to place
// several models in one scene — a federation unit, a false origin, and a
// per-model transform and display name.
//
// Deliberately NOT an .ifcfed reader. The desktop Federation class is a
// document model (QObject, JSON persistence, groups, cloud manifests) and its
// model sources are local filesystem paths, which mean nothing in a browser.
// What the web needs is the underlying concepts, exposed so JS can drive them;
// a host page that wants .ifcfed can parse the JSON itself and call these.
//
// Models are keyed by the JS-side source id, NOT the session model id. The
// source id exists synchronously the moment a File or URL is registered,
// whereas the session model id is minted deep inside the async range-read
// chain. Keying on the source id is what lets a caller set a transform BEFORE
// the load finishes, so the model appears already in place instead of jumping
// once its state is applied afterwards.
class WebFederation {
public:
    explicit WebFederation(ViewportCore& core) : core_(core) {}

    // ---- Federation-wide -----------------------------------------------

    void setConfig(const FederationConfig& cfg);
    const FederationConfig& config() const { return config_; }

    // Marks the origin as explicitly authored, which suppresses the automatic
    // guess in onModelLoaded. A host that sets an origin means it.
    void setFalseOrigin(const FederatedFalseOrigin& origin);
    const FederatedFalseOrigin& falseOrigin() const { return false_origin_; }
    bool falseOriginIsExplicit() const { return false_origin_explicit_; }

    // ---- Per-model -------------------------------------------------------

    void setModelTransformation(int source_id, const ModelTransformation& xf);
    void clearModelTransformation(int source_id);
    void setModelName(int source_id, std::string name);
    std::string modelName(int source_id) const;

    // Session model id for a source, or 0 when that source has not finished
    // loading. Session ids start at 1, so 0 is unambiguous.
    std::uint32_t sessionModelId(int source_id) const;

    // ---- Lifecycle -------------------------------------------------------

    // Call when a sidecar load completes. Binds the source to its session model
    // id, applies whatever state was staged against the source id, and — for
    // the first model only, and only when no origin was set explicitly — runs
    // the false-origin guess.
    void onModelLoaded(int source_id, std::uint32_t session_model_id);

    // A model that did not come from a JS source — the embedded sample, read
    // synchronously from MEMFS. It has no source id and so cannot carry a
    // per-model transform (a host that wants to place a model adds it as a
    // source), but it must still take part in the false-origin guess.
    // Otherwise a page showing the sample renders it unshifted, which for a
    // georeferenced model means out at its surveyor coordinates.
    void onModelLoadedWithoutSource(std::uint32_t session_model_id);

    // Drop all state. Pairs with ViewportCore::resetScene so a fresh
    // federation does not inherit the previous one's origin or transforms.
    void clear();

private:
    // Push the composed false-origin matrix; every model recomposes against it.
    void applyFalseOrigin();
    // Push one model's composed transform. No-op until the model has loaded,
    // since composing needs its georef.
    void applyModelTransformation(int source_id);
    // Position + grid-north heading that puts the first model near the origin
    // instead of out at its surveyor coordinates.
    void guessFalseOriginFrom(std::uint32_t session_model_id);

    struct ModelState {
        std::uint32_t       session_model_id = 0;  // 0 until loaded
        std::string         name;
        ModelTransformation transformation;
        bool                has_transformation = false;
    };

    ViewportCore&                      core_;
    FederationConfig                   config_;
    FederatedFalseOrigin               false_origin_;
    bool                               false_origin_explicit_ = false;
    bool                               guessed_false_origin_  = false;
    std::unordered_map<int, ModelState> models_;
};

#endif // WEBFEDERATION_H
