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

#ifndef IFCINTERFACE_MODULES_PROJECT_RECENTPROJECTS_H
#define IFCINTERFACE_MODULES_PROJECT_RECENTPROJECTS_H

#include <QString>
#include <QStringList>

namespace bonsaiviewer::modules::project {

// Persistent most-recently-used list of project (.ifcfed) paths, backed by
// QSettings so it survives across sessions. All entries are stored as
// absolute, cleaned paths; the list is capped and de-duplicated.
class RecentProjects {
public:
    // Hard cap on how many entries are kept / shown.
    static constexpr int kMaxEntries = 10;

    // Recent project paths, most-recent first. Entries whose file no longer
    // exists on disk are pruned (and the pruned list is persisted) so callers
    // never need to filter the result themselves.
    static QStringList list();

    // Promote `path` to the front of the list. De-duplicates against any
    // existing entry for the same file and trims the list to kMaxEntries.
    // A no-op for empty paths.
    static void add(const QString& path);

    // Drop a single entry, e.g. after a failed open. No-op if absent.
    static void remove(const QString& path);

    // Forget every entry.
    static void clear();
};

} // namespace bonsaiviewer::modules::project

#endif
