// This file was generated with the assistance of an AI coding tool.
/********************************************************************************
 *                                                                              *
 * This file is part of Bonsai.                                                 *
 *                                                                              *
 * Bonsai is free software: you can redistribute it and/or modify               *
 * it under the terms of the GNU General Public License as published by         *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * Bonsai is distributed in the hope that it will be useful,                    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * GNU General Public License for more details.                                 *
 *                                                                              *
 * You should have received a copy of the GNU General Public License            *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "SessionState.h"

#include "ElementRegistry.h"
#include "modules/connectors/Registry.h"
#include "../ifcviewer/Federation.h"
#include "../ifcviewer/SceneLoader.h"

namespace bonsaiviewer {

SessionState::SessionState(QObject* parent)
    : QObject(parent)
    , federation_(new Federation(this))
    , element_registry_(new ElementRegistry(this))
    , connector_registry_(new modules::connectors::ConnectorRegistry(this))
{
    // Relay specific Federation mutations onto the SessionState bus. Views
    // subscribe to SessionState signals only — Federation stays a back-end
    // detail. Doing the relay here (instead of having every mutation site
    // manually call notifyFederationChanged) keeps the "emit point" at one
    // hop from the data change and rules out emit-in-slot recursion bugs.
    connect(federation_, &Federation::federatedFalseOriginChanged,
            this, &SessionState::notifyFederationChanged);
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
            [this, format_elapsed](uint32_t session_model_id, qint64 elapsed_ms) {
        setStatusMessage("Loaded",
            QString("%1 from cache in %2")
                .arg(loader_->displayName(session_model_id))
                .arg(format_elapsed(elapsed_ms)));
        endProgress();
        emit modelGeometryReady(session_model_id);
    });
    connect(loader_, &SceneLoader::loadedFromStream, this,
            [this, format_elapsed](uint32_t session_model_id, qint64 elapsed_ms) {
        setStatusMessage("Loaded",
            QString("%1 streamed in %2")
                .arg(loader_->displayName(session_model_id))
                .arg(format_elapsed(elapsed_ms)));
        endProgress();
        emit modelGeometryReady(session_model_id);
    });
    connect(loader_, &SceneLoader::loadCancelled, this, [this](uint32_t session_model_id) {
        setStatusMessage("Cancelled", loader_->displayName(session_model_id));
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
    connect(loader_, &SceneLoader::dataSourceReady, this, [this](uint32_t session_model_id) {
        emit modelDataSourceReady(session_model_id);
    });
    // First model to load becomes the active model by default.
    connect(this, &SessionState::modelGeometryReady, this, [this](uint32_t session_model_id) {
        if (active_model_id_.isEmpty()) {
            setActiveModelId(modelIdForSessionModelId(session_model_id));
        }
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

void SessionState::setModelMapping(const QString& model_id, uint32_t session_model_id) {
    model_id_to_session_model_id_[model_id] = session_model_id;
    session_model_id_to_model_id_[session_model_id] = model_id;
}

void SessionState::removeModelMappingByModelId(const QString& model_id) {
    cloud_metadata_.remove(model_id);
    auto it = model_id_to_session_model_id_.find(model_id);
    if (it == model_id_to_session_model_id_.end()) return;
    session_model_id_to_model_id_.remove(it.value());
    model_id_to_session_model_id_.erase(it);
    if (model_id == active_model_id_) {
        setActiveModelId(model_id_to_session_model_id_.isEmpty()
                             ? QString()
                             : model_id_to_session_model_id_.keys().first());
    }
}

void SessionState::clearModelMappings() {
    model_id_to_session_model_id_.clear();
    session_model_id_to_model_id_.clear();
    cloud_metadata_.clear();
    setActiveModelId(QString());
}

void SessionState::setActiveModelId(const QString& model_id) {
    if (model_id == active_model_id_) return;
    active_model_id_ = model_id;
    emit activeModelChanged(active_model_id_);
}

void SessionState::setCloudMetadata(const QString& model_id, const QVariantMap& metadata) {
    if (metadata.isEmpty()) cloud_metadata_.remove(model_id);
    else cloud_metadata_.insert(model_id, metadata);
}

QVariantMap SessionState::cloudMetadata(const QString& model_id) const {
    return cloud_metadata_.value(model_id);
}

uint32_t SessionState::sessionModelIdForModelId(const QString& model_id) const {
    return model_id_to_session_model_id_.value(model_id, 0);
}

QString SessionState::modelIdForSessionModelId(uint32_t session_model_id) const {
    return session_model_id_to_model_id_.value(session_model_id);
}

QList<uint32_t> SessionState::sessionModelIds() const {
    return session_model_id_to_model_id_.keys();
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

void SessionState::notifyModelGeometryReady(uint32_t session_model_id) {
    emit modelGeometryReady(session_model_id);
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

} // namespace bonsaiviewer
