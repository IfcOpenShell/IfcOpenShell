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

#include "Discovery.h"

#include <QCoreApplication>
#include <QDebug>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonObject>
#include <QSet>

namespace bonsaiviewer::modules::connectors {

namespace {

QString resolveExec(const QString& exec_field, const QString& folder) {
    QString resolved = QDir(folder).absoluteFilePath(exec_field);
#if defined(Q_OS_WIN)
    if (!QFileInfo::exists(resolved) && QFileInfo::exists(resolved + ".exe")) {
        resolved += ".exe";
    }
#endif
    return QDir::cleanPath(resolved);
}

bool parseManifest(const QString& folder, ConnectorManifest& out) {
    const QString manifest_path = QDir(folder).filePath("connector.json");
    QFile file(manifest_path);
    if (!file.open(QIODevice::ReadOnly)) {
        qWarning() << "ifcviewer connectors: cannot read" << manifest_path
                   << ":" << file.errorString();
        return false;
    }
    QJsonParseError err{};
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll(), &err);
    if (doc.isNull() || !doc.isObject()) {
        qWarning() << "ifcviewer connectors: malformed manifest"
                   << manifest_path << ":" << err.errorString();
        return false;
    }
    const QJsonObject obj = doc.object();
    const QString id = obj.value("id").toString();
    const QString name = obj.value("name").toString();
    const QString version = obj.value("version").toString();
    const QString exec_field = obj.value("exec").toString();
    if (id.isEmpty() || name.isEmpty() || exec_field.isEmpty()) {
        qWarning() << "ifcviewer connectors: missing required field (id/name/exec) in"
                   << manifest_path;
        return false;
    }
    out.id = id;
    out.name = name;
    out.version = version;
    out.folder = QDir::cleanPath(folder);
    out.exec_path = resolveExec(exec_field, out.folder);
    return true;
}

} // namespace

QString bundledConnectorsDir() {
    // Connectors ship alongside the executable in a "connectors" subdirectory.
    return QDir(QCoreApplication::applicationDirPath()).filePath("connectors");
}

std::vector<ConnectorManifest> discoverConnectors() {
    std::vector<ConnectorManifest> result;
    QSet<QString> seen_ids;
    QDir dir(bundledConnectorsDir());
    if (!dir.exists()) return result;
    const QFileInfoList entries = dir.entryInfoList(
        QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name);
    for (const QFileInfo& entry : entries) {
        if (!QFileInfo(QDir(entry.absoluteFilePath()).filePath("connector.json")).exists()) continue;
        ConnectorManifest m;
        if (!parseManifest(entry.absoluteFilePath(), m)) continue;
        if (seen_ids.contains(m.id)) {
            qWarning() << "ifcviewer connectors: duplicate id" << m.id
                       << "at" << entry.absoluteFilePath()
                       << "ignored (earlier match wins)";
            continue;
        }
        seen_ids.insert(m.id);
        result.push_back(std::move(m));
    }
    return result;
}

} // namespace bonsaiviewer::modules::connectors
