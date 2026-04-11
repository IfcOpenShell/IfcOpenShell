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

#include "AppSettings.h"

#include <QSettings>

namespace {
constexpr const char* kGeometryLibraryKey = "geometry/library";
constexpr const char* kGeometryLibraryDefault = "hybrid-cgal-simple-opencascade";
}

AppSettings& AppSettings::instance() {
    static AppSettings inst;
    return inst;
}

AppSettings::AppSettings() {
    load();
}

QString AppSettings::geometryLibrary() const {
    return geometry_library_;
}

void AppSettings::setGeometryLibrary(const QString& value) {
    if (geometry_library_ == value) return;
    geometry_library_ = value;
    persist();
    emit geometryLibraryChanged(value);
}

void AppSettings::load() {
    QSettings settings;
    geometry_library_ = settings.value(kGeometryLibraryKey, kGeometryLibraryDefault).toString();
}

void AppSettings::persist() {
    QSettings settings;
    settings.setValue(kGeometryLibraryKey, geometry_library_);
}
