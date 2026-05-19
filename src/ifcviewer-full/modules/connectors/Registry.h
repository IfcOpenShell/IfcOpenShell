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

#ifndef IFCINTERFACE_MODULES_CONNECTORS_REGISTRY_H
#define IFCINTERFACE_MODULES_CONNECTORS_REGISTRY_H

#include "Discovery.h"

#include <QHash>
#include <QObject>
#include <QString>
#include <vector>

namespace ifcviewerfull::modules::connectors {

class ConnectorProcess;

// Per-session catalog of available connectors plus their lazily-launched
// subprocesses. One instance lives on SessionState; processes are launched
// on first get() and shut down on ~Registry / shutdownAll().
class ConnectorRegistry : public QObject {
    Q_OBJECT
public:
    explicit ConnectorRegistry(QObject* parent = nullptr);
    ~ConnectorRegistry() override;

    // Discovered connectors in discovery order. First call triggers a scan;
    // call refresh() to force a rescan.
    const std::vector<ConnectorManifest>& available();

    // Re-scans the filesystem. Live processes for ids that have disappeared
    // (or whose exec changed) are shut down; surviving connectors keep their
    // running process.
    void refresh();

    // Returns the manifest for `id`, or nullptr.
    const ConnectorManifest* manifestFor(const QString& id) const;

    // Lazily-launched process. Returns nullptr if `id` is unknown or launch
    // failed; the reason is in lastError().
    ConnectorProcess* get(const QString& id);

    QString lastError() const { return last_error_; }

    // Close stdin on every live connector. Idempotent.
    void shutdownAll();

private:
    bool discovered_ = false;
    std::vector<ConnectorManifest> manifests_;
    QHash<QString, ConnectorProcess*> processes_;
    QString last_error_;
};

} // namespace ifcviewerfull::modules::connectors

#endif
