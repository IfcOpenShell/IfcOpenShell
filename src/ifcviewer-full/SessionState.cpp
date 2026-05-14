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

#include "../ifcviewer/Federation.h"

namespace ifcinterface {

SessionState::SessionState(QObject* parent)
    : QObject(parent)
{
}

void SessionState::bindFederation(Federation* federation) {
    federation_ = federation;
}

void SessionState::bindLoader(SceneLoader* loader) {
    loader_ = loader;
}

void SessionState::bindElementRegistry(ElementRegistry* element_registry) {
    element_registry_ = element_registry;
}

void SessionState::setSelectedObjectId(uint32_t object_id) {
    selected_object_id_ = object_id;
}

void SessionState::setStatusMessage(const QString& mode, const QString& detail) {
    status_mode_ = mode;
    status_detail_ = detail;
    emit statusMessageChanged(status_mode_, status_detail_);
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

void SessionState::notifyFederationStructureChanged() {
    emit federationStructureChanged();
}

void SessionState::notifyVisibilityChanged() {
    emit visibilityChanged();
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

} // namespace ifcinterface
