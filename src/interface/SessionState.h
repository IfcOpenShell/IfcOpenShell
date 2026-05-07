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

#ifndef IFCINTERFACE_SESSIONSTATE_H
#define IFCINTERFACE_SESSIONSTATE_H

#include <QHash>
#include <QObject>
#include <QString>

class Federation;
class SceneLoader;

namespace ifcinterface {

class ElementRegistry;

class SessionState : public QObject {
    Q_OBJECT

public:
    explicit SessionState(QObject* parent = nullptr);

    void bindFederation(Federation* federation);
    void bindLoader(SceneLoader* loader);
    void bindElementRegistry(ElementRegistry* element_registry);

    Federation* federation() const { return federation_; }
    SceneLoader* loader() const { return loader_; }
    ElementRegistry* elementRegistry() const { return element_registry_; }
    QString statusMode() const { return status_mode_; }
    QString statusDetail() const { return status_detail_; }

    void setSelectedObjectId(uint32_t object_id);
    uint32_t selectedObjectId() const { return selected_object_id_; }
    void setStatusMessage(const QString& mode, const QString& detail);

    void setModelMapping(const QString& fed_id, uint32_t model_id);
    void removeModelMappingByFedId(const QString& fed_id);
    void clearModelMappings();
    uint32_t modelIdForFedId(const QString& fed_id) const;
    QString fedIdForModelId(uint32_t model_id) const;
    QList<uint32_t> modelIds() const;

    void notifySelectionChanged();
    void notifyModelsChanged();
    void notifyFederationStructureChanged();
    void notifyVisibilityChanged();
    void notifyProjectOpened(const QString& path);
    void notifyProjectReset();

signals:
    void projectOpened(const QString& path);
    void projectReset();
    void modelsChanged();
    void federationStructureChanged();
    void visibilityChanged();
    void selectionChanged(uint32_t object_id);
    void statusMessageChanged(const QString& mode, const QString& detail);

private:
    Federation* federation_ = nullptr;
    SceneLoader* loader_ = nullptr;
    ElementRegistry* element_registry_ = nullptr;
    uint32_t selected_object_id_ = 0;
    QString status_mode_;
    QString status_detail_;
    QHash<QString, uint32_t> fed_id_to_model_id_;
    QHash<uint32_t, QString> model_id_to_fed_id_;
};

} // namespace ifcinterface

#endif
