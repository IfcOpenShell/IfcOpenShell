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

#include "SessionState.h"

#include "ElementRegistry.h"
#include "../ifcviewer/Federation.h"
#include "../ifcviewer/SceneLoader.h"

namespace ifcviewerfull {

SessionState::SessionState(QObject* parent)
    : QObject(parent)
    , federation_(new Federation(this))
    , element_registry_(new ElementRegistry(this))
{
}

void SessionState::createLoader(ViewportWindow* viewport) {
    Q_ASSERT(!loader_);
    loader_ = new SceneLoader(viewport, this);
    loader_->setShouldReadSidecar(true);
    loader_->setShouldWriteSidecar(true);
    element_registry_->bindLoader(loader_);

    auto format_elapsed = [](qint64 ms) {
        return (ms >= 1000)
            ? QString::number(ms / 1000.0, 'f', 2) + " s"
            : QString::number(ms) + " ms";
    };

    // Translate low-level loader events into session-level signals, status
    // text, and progress so views don't need to subscribe to the loader.
    connect(loader_, &SceneLoader::loadStarted, this,
            [this](uint32_t, const QString& display_name) {
        setStatusMessage("Loading", display_name);
        beginProgress(display_name);
    });
    connect(loader_, &SceneLoader::progressChanged, this, &SessionState::setProgress);
    connect(loader_, &SceneLoader::loadedFromSidecar, this,
            [this, format_elapsed](uint32_t mid, qint64 elapsed_ms) {
        setStatusMessage("Loaded",
            QString("%1 from cache in %2")
                .arg(loader_->displayName(mid))
                .arg(format_elapsed(elapsed_ms)));
        endProgress();
        emit modelGeometryReady(mid);
    });
    connect(loader_, &SceneLoader::loadedFromStream, this,
            [this, format_elapsed](uint32_t mid, qint64 elapsed_ms) {
        setStatusMessage("Loaded",
            QString("%1 streamed in %2")
                .arg(loader_->displayName(mid))
                .arg(format_elapsed(elapsed_ms)));
        endProgress();
        emit modelGeometryReady(mid);
    });
    connect(loader_, &SceneLoader::loadCancelled, this, [this](uint32_t mid) {
        setStatusMessage("Cancelled", loader_->displayName(mid));
        endProgress();
    });
    connect(loader_, &SceneLoader::loadError, this,
            [this](uint32_t, const QString& message) {
        setStatusMessage("Error", message);
        endProgress();
        emit loadError(message);
    });
    connect(loader_, &SceneLoader::allLoadsFinished, this, [this]() {
        setStatusMessage("Loaded", QString("%1 model(s)").arg(loader_->modelCount()));
    });
}

void SessionState::setSelectedObjectId(uint32_t object_id) {
    selected_object_id_ = object_id;
}

void SessionState::setStatusMessage(const QString& mode, const QString& detail) {
    status_mode_ = mode;
    status_detail_ = detail;
    emit statusMessageChanged(status_mode_, status_detail_);
}

void SessionState::beginProgress(const QString& label) {
    emit progressBegan(label);
}

void SessionState::setProgress(int percent) {
    emit progressChanged(percent);
}

void SessionState::endProgress() {
    emit progressEnded();
}

void SessionState::setModelMapping(const QString& fed_id, uint32_t model_id) {
    fed_id_to_model_id_[fed_id] = model_id;
    model_id_to_fed_id_[model_id] = fed_id;
}

void SessionState::removeModelMappingByFedId(const QString& fed_id) {
    auto it = fed_id_to_model_id_.find(fed_id);
    if (it == fed_id_to_model_id_.end()) return;
    model_id_to_fed_id_.remove(it.value());
    fed_id_to_model_id_.erase(it);
}

void SessionState::clearModelMappings() {
    fed_id_to_model_id_.clear();
    model_id_to_fed_id_.clear();
}

uint32_t SessionState::modelIdForFedId(const QString& fed_id) const {
    return fed_id_to_model_id_.value(fed_id, 0);
}

QString SessionState::fedIdForModelId(uint32_t model_id) const {
    return model_id_to_fed_id_.value(model_id);
}

QList<uint32_t> SessionState::modelIds() const {
    return model_id_to_fed_id_.keys();
}

void SessionState::notifySelectionChanged() {
    emit selectionChanged(selected_object_id_);
}

void SessionState::notifyModelsChanged() {
    emit modelsChanged();
}

void SessionState::notifyFederationChanged() {
    emit federationChanged();
}

void SessionState::notifyVisibilityChanged() {
    emit visibilityChanged();
}

void SessionState::notifyModelGeometryReady(uint32_t model_id) {
    emit modelGeometryReady(model_id);
}

void SessionState::notifyProjectOpened(const QString& path) {
    emit projectOpened(path);
}

void SessionState::notifyProjectSaved(const QString& path) {
    emit projectSaved(path);
}

void SessionState::notifyProjectReset() {
    emit projectReset();
}

} // namespace ifcviewerfull
