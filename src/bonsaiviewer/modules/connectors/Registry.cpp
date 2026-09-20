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
        ConnectorProcess* process = it.value();
        const ConnectorManifest* current_manifest = manifestFor(id);
        const bool stale = !current_manifest || !process ||
                           process->manifest().exec_path != current_manifest->exec_path;
        if (stale) {
            if (process) {
                process->shutdown();
                process->deleteLater();
            }
            it = processes_.erase(it);
        } else {
            ++it;
        }
    }
}

const ConnectorManifest* ConnectorRegistry::manifestFor(const QString& id) const {
    for (const auto& manifest : manifests_) {
        if (manifest.id == id) return &manifest;
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
        if (auto* process = processes_.take(id)) process->deleteLater();
    });
    return proc;
}

void ConnectorRegistry::shutdownAll() {
    const auto procs = processes_;
    processes_.clear();
    for (auto it = procs.begin(); it != procs.end(); ++it) {
        if (auto* process = it.value()) {
            process->shutdown();
            process->deleteLater();
        }
    }
}

} // namespace bonsaiviewer::modules::connectors
