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

#include "Registry.h"

#include "Process.h"

#include <QDebug>

namespace bonsaiviewer::modules::connectors {

ConnectorRegistry::ConnectorRegistry(QObject* parent)
    : QObject(parent)
{
}

ConnectorRegistry::~ConnectorRegistry() {
    shutdownAll();
}

const std::vector<ConnectorManifest>& ConnectorRegistry::available() {
    if (!discovered_) refresh();
    return manifests_;
}

void ConnectorRegistry::refresh() {
    manifests_ = discoverConnectors();
    discovered_ = true;

    // Cull processes whose connector is no longer discoverable, or whose
    // exec changed under us. Surviving entries keep their running process.
    for (auto it = processes_.begin(); it != processes_.end();) {
        const QString id = it.key();
        ConnectorProcess* p = it.value();
        const ConnectorManifest* now = manifestFor(id);
        const bool stale = !now || !p ||
                           p->manifest().exec_path != now->exec_path;
        if (stale) {
            if (p) {
                p->shutdown();
                p->deleteLater();
            }
            it = processes_.erase(it);
        } else {
            ++it;
        }
    }
}

const ConnectorManifest* ConnectorRegistry::manifestFor(const QString& id) const {
    for (const auto& m : manifests_) {
        if (m.id == id) return &m;
    }
    return nullptr;
}

ConnectorProcess* ConnectorRegistry::get(const QString& id) {
    if (!discovered_) refresh();
    if (auto* existing = processes_.value(id, nullptr)) return existing;

    const ConnectorManifest* manifest = manifestFor(id);
    if (!manifest) {
        last_error_ = QString("Unknown connector '%1'.").arg(id);
        return nullptr;
    }
    auto* proc = new ConnectorProcess(*manifest, this);
    if (!proc->ensureStarted()) {
        last_error_ = proc->lastError();
        delete proc;
        return nullptr;
    }
    last_error_.clear();
    processes_.insert(id, proc);
    connect(proc, &ConnectorProcess::crashed, this, [this, id](const QString& message) {
        qWarning() << "ifcviewer connectors:" << message;
        if (auto* p = processes_.take(id)) p->deleteLater();
    });
    return proc;
}

void ConnectorRegistry::shutdownAll() {
    const auto procs = processes_;
    processes_.clear();
    for (auto it = procs.begin(); it != procs.end(); ++it) {
        if (auto* p = it.value()) {
            p->shutdown();
            p->deleteLater();
        }
    }
}

} // namespace bonsaiviewer::modules::connectors
