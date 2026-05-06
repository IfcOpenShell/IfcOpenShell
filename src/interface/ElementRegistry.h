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

#ifndef IFCINTERFACE_ELEMENTREGISTRY_H
#define IFCINTERFACE_ELEMENTREGISTRY_H

#include <QObject>
#include <QString>
#include <optional>
#include <unordered_map>
#include <vector>
#include <string>

class SceneLoader;
struct PackedElementInfo;
struct ElementInfo;

namespace ifcinterface {

struct BasicElementInfo {
    uint32_t object_id = 0;
    uint32_t model_id = 0;
    int ifc_id = 0;
    int parent_id = 0;
    QString guid;
    QString name;
    QString type;
};

class ElementRegistry : public QObject {
    Q_OBJECT
public:
    explicit ElementRegistry(QObject* parent = nullptr);

    void bindLoader(SceneLoader* loader);
    std::optional<BasicElementInfo> find(uint32_t object_id) const;

private:
    void onSidecarElementsReady(uint32_t mid,
                                std::vector<PackedElementInfo> elements,
                                std::string string_table);
    void onStreamedElementsReady(uint32_t mid, std::vector<ElementInfo> elements);

    std::unordered_map<uint32_t, BasicElementInfo> elements_;
};

} // namespace ifcinterface

#endif
