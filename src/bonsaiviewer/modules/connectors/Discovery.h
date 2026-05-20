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

#ifndef IFCINTERFACE_MODULES_CONNECTORS_DISCOVERY_H
#define IFCINTERFACE_MODULES_CONNECTORS_DISCOVERY_H

#include <QString>
#include <vector>

namespace bonsaiviewer::modules::connectors {

struct ConnectorManifest {
    QString id;          // from connector.json; stable identifier
    QString name;        // human-readable label
    QString version;     // informational
    QString folder;      // directory containing connector.json
    QString exec_path;   // resolved executable; absolute when possible,
                         // otherwise a bare name for PATH lookup at launch
};

// Scans the connectors directory bundled alongside the executable.
// First match wins for any given id; duplicates and malformed manifests
// are skipped with a qWarning. Returned in discovery order so first-wins
// is observable to callers.
std::vector<ConnectorManifest> discoverConnectors();

// Connectors directory bundled next to the executable
// (<applicationDirPath>/connectors). Exposed for tests and for
// "open connectors dir" affordances.
QString bundledConnectorsDir();

} // namespace bonsaiviewer::modules::connectors

#endif
