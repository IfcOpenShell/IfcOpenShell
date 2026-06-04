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
#include <QVariantMap>

class Federation;
class SceneLoader;
class ViewportWindow;

namespace bonsaiviewer {

class ElementRegistry;

namespace modules::connectors { class ConnectorRegistry; }

class SessionState : public QObject {
    Q_OBJECT

public:
    explicit SessionState(QObject* parent = nullptr);

    // Owned by SessionState once it can be tied to a viewport. Wires
    // loader → element registry signals internally. Call exactly once.
    void createLoader(ViewportWindow* viewport);

    Federation* federation() const { return federation_; }
    SceneLoader* loader() const { return loader_; }
    ElementRegistry* elementRegistry() const { return element_registry_; }
    modules::connectors::ConnectorRegistry* connectorRegistry() const { return connector_registry_; }
    QString statusMode() const { return status_mode_; }
    QString statusDetail() const { return status_detail_; }

    void setSelectedObjectId(uint32_t object_id);
    uint32_t selectedObjectId() const { return selected_object_id_; }
    void setStatusMessage(const QString& mode, const QString& detail);

    // Generic progress reporting for any long-running operation (load,
    // convert, export, ...). Subscribers (the status bar) react to the
    // signals; they do not need to know which operation is running.
    void beginProgress(const QString& label);
    void setProgress(int percent);
    void endProgress();

    void setModelMapping(const QString& fed_id, uint32_t model_id);
    void removeModelMappingByFedId(const QString& fed_id);
    void clearModelMappings();

    // Per-session cloud metadata returned by connectors (revision/date/
    // author/...). Not persisted to the .ifcfed; display only. Lifetime
    // is tied to the fed_id — removeModelMappingByFedId and
    // clearModelMappings drop the matching entries.
    void setCloudMetadata(const QString& fed_id, const QVariantMap& metadata);
    QVariantMap cloudMetadata(const QString& fed_id) const;
    uint32_t modelIdForFedId(const QString& fed_id) const;
    QString fedIdForModelId(uint32_t model_id) const;
    QList<uint32_t> modelIds() const;

    void notifySelectionChanged();
    void notifyModelsChanged();
    void notifyFederationChanged();
    void notifyVisibilityChanged();
    void notifyModelGeometryReady(uint32_t model_id);
    void notifyProjectOpened(const QString& path);
    void notifyProjectSaved(const QString& path);
    void notifyProjectReset();

signals:
    void projectOpened(const QString& path);
    void projectSaved(const QString& path);
    void projectReset();
    void modelsChanged();
    // Fires whenever a command has mutated the federation (groups, transforms,
    // origin, config). Always implies the project is now dirty; callers do not
    // emit this on save/load/reset — projectSaved/Opened/Reset cover those.
    void federationChanged();
    void visibilityChanged();
    // Fires when a model's geometry has been pushed to the viewport. Fires
    // for both sidecar-cache and stream loads; subscribers that just need to
    // re-derive view state (e.g. ViewportView::refresh) listen to this.
    void modelGeometryReady(uint32_t model_id);
    // Fires when SceneLoader reports a load failure. SessionState turns the
    // raw loader signal into a session-level one so views (e.g. the MessageBox)
    // can subscribe without touching the loader directly.
    void loadError(const QString& message);
    void selectionChanged(uint32_t object_id);
    void statusMessageChanged(const QString& mode, const QString& detail);
    void progressBegan(const QString& label);
    void progressChanged(int percent);
    void progressEnded();

private:
    Federation* federation_ = nullptr;
    SceneLoader* loader_ = nullptr;
    ElementRegistry* element_registry_ = nullptr;
    modules::connectors::ConnectorRegistry* connector_registry_ = nullptr;
    uint32_t selected_object_id_ = 0;
    QString status_mode_;
    QString status_detail_;
    QHash<QString, uint32_t> fed_id_to_model_id_;
    QHash<uint32_t, QString> model_id_to_fed_id_;
    QHash<QString, QVariantMap> cloud_metadata_;
};

} // namespace bonsaiviewer

#endif
