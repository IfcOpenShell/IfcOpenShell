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

#include "ElementRegistry.h"

#include "../ifcviewer/GeometryStreamer.h"
#include "../ifcviewer/SceneLoader.h"
#include "../ifcviewer/SidecarCache.h"

namespace bonsaiviewer {

ElementRegistry::ElementRegistry(QObject* parent)
    : QObject(parent)
{
}

void ElementRegistry::bindLoader(SceneLoader* loader) {
    loader_ = loader;
    connect(loader, &SceneLoader::sidecarElementsReady,
            this, &ElementRegistry::onSidecarElementsReady);
    connect(loader, &SceneLoader::streamedElementsReady,
            this, &ElementRegistry::onStreamedElementsReady);
}

void ElementRegistry::clear() {
    elements_.clear();
}

void ElementRegistry::removeModel(uint32_t model_id) {
    for (auto it = elements_.begin(); it != elements_.end();) {
        if (it->second.model_id == model_id) {
            it = elements_.erase(it);
        } else {
            ++it;
        }
    }
}

std::vector<BasicElementInfo> ElementRegistry::basicElementInfoForModel(uint32_t model_id) const {
    std::vector<BasicElementInfo> result;
    result.reserve(elements_.size());
    for (const auto& [object_id, info] : elements_) {
        (void)object_id;
        if (info.model_id != model_id) continue;
        result.push_back(info);
    }
    return result;
}

std::optional<BasicElementInfo> ElementRegistry::findBasicElementInfo(uint32_t object_id) const {
    auto it = elements_.find(object_id);
    if (it == elements_.end()) return std::nullopt;
    return it->second;
}

std::optional<express::Base> ElementRegistry::findEntity(uint32_t object_id) const {
    if (!loader_) return std::nullopt;

    auto info = findBasicElementInfo(object_id);
    if (!info) return std::nullopt;

    auto* file = loader_->ifcFile(info->model_id);
    if (!file) return std::nullopt;

    try {
        auto instance = file->instance_by_id(info->ifc_id);
        if (!instance) return std::nullopt;
        return instance;
    } catch (...) {
        return std::nullopt;
    }
}

void ElementRegistry::onSidecarElementsReady(uint32_t /*mid*/,
                                             std::vector<PackedElementInfo> elements,
                                             std::string string_table) {
    auto str = [&](uint32_t offset, uint32_t length) -> QString {
        if (length == 0 || offset + length > string_table.size()) return {};
        return QString::fromStdString(string_table.substr(offset, length));
    };

    for (const auto& pe : elements) {
        BasicElementInfo info;
        info.object_id = pe.object_id;
        info.model_id = pe.model_id;
        info.ifc_id = pe.ifc_id;
        info.parent_id = pe.parent_id;
        info.guid = str(pe.guid_offset, pe.guid_length);
        info.name = str(pe.name_offset, pe.name_length);
        info.type = str(pe.type_offset, pe.type_length);
        elements_[info.object_id] = info;
    }
}

void ElementRegistry::onStreamedElementsReady(uint32_t /*mid*/, std::vector<ElementInfo> elements) {
    for (const auto& e : elements) {
        BasicElementInfo info;
        info.object_id = e.object_id;
        info.model_id = e.model_id;
        info.ifc_id = e.ifc_id;
        info.parent_id = e.parent_id;
        info.guid = QString::fromStdString(e.guid);
        info.name = QString::fromStdString(e.name);
        info.type = QString::fromStdString(e.type);
        elements_[info.object_id] = info;
    }
}

} // namespace bonsaiviewer
