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

#include "RecentProjects.h"

#include <QFileInfo>
#include <QSettings>

namespace bonsaiviewer::modules::project {

namespace {

constexpr const char* kRecentKey = "project/recent_projects";

// Absolute, cleaned form used both for storage and de-duplication.
QString canonicalize(const QString& path) {
    if (path.isEmpty()) return {};
    return QFileInfo(path).absoluteFilePath();
}

QStringList readRaw() {
    QSettings settings;
    return settings.value(kRecentKey).toStringList();
}

void writeRaw(const QStringList& paths) {
    QSettings settings;
    settings.setValue(kRecentKey, paths);
}

} // namespace

QStringList RecentProjects::list() {
    const QStringList stored = readRaw();
    QStringList existing;
    for (const QString& path : stored) {
        if (QFileInfo::exists(path)) existing << path;
    }
    // Persist the pruned list so vanished files don't linger forever.
    if (existing != stored) writeRaw(existing);
    return existing;
}

void RecentProjects::add(const QString& path) {
    const QString canonical = canonicalize(path);
    if (canonical.isEmpty()) return;

    QStringList paths = readRaw();
    paths.removeAll(canonical);
    paths.prepend(canonical);
    while (paths.size() > kMaxEntries) paths.removeLast();
    writeRaw(paths);
}

void RecentProjects::remove(const QString& path) {
    const QString canonical = canonicalize(path);
    if (canonical.isEmpty()) return;

    QStringList paths = readRaw();
    if (paths.removeAll(canonical) > 0) writeRaw(paths);
}

void RecentProjects::clear() {
    QSettings settings;
    settings.remove(kRecentKey);
}

} // namespace bonsaiviewer::modules::project
