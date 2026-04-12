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
constexpr const char* kShowStatsKey = "viewport/show_stats";
constexpr const char* kBackfaceCullingKey = "viewport/backface_culling";
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

bool AppSettings::showStats() const {
    return show_stats_;
}

void AppSettings::setShowStats(bool value) {
    if (show_stats_ == value) return;
    show_stats_ = value;
    persist();
    emit showStatsChanged(value);
}

bool AppSettings::backfaceCulling() const {
    return backface_culling_;
}

void AppSettings::setBackfaceCulling(bool value) {
    if (backface_culling_ == value) return;
    backface_culling_ = value;
    persist();
    emit backfaceCullingChanged(value);
}

void AppSettings::load() {
    QSettings settings;
    geometry_library_ = settings.value(kGeometryLibraryKey, kGeometryLibraryDefault).toString();
    show_stats_ = settings.value(kShowStatsKey, false).toBool();
    backface_culling_ = settings.value(kBackfaceCullingKey, true).toBool();
}

void AppSettings::persist() {
    QSettings settings;
    settings.setValue(kGeometryLibraryKey, geometry_library_);
    settings.setValue(kShowStatsKey, show_stats_);
    settings.setValue(kBackfaceCullingKey, backface_culling_);
}
