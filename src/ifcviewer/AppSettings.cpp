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
constexpr const char* kLoadDataSourceKey = "loading/load_data_source";
constexpr const char* kVoidLimitKey = "loading/void_limit";
constexpr int kVoidLimitDefault = 30;
constexpr const char* kDeflectionToleranceKey = "loading/deflection_tolerance";
constexpr double kDeflectionToleranceDefault = 0.001;
constexpr const char* kAngularToleranceKey = "loading/angular_tolerance";
constexpr double kAngularToleranceDefault = 0.5;
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

bool AppSettings::loadDataSource() const {
    return load_data_source_;
}

void AppSettings::setLoadDataSource(bool value) {
    if (load_data_source_ == value) return;
    load_data_source_ = value;
    persist();
    emit loadDataSourceChanged(value);
}

int AppSettings::voidLimit() const {
    return void_limit_;
}

void AppSettings::setVoidLimit(int value) {
    if (value < 0) value = 0;
    if (void_limit_ == value) return;
    void_limit_ = value;
    persist();
    emit voidLimitChanged(value);
}

double AppSettings::deflectionTolerance() const {
    return deflection_tolerance_;
}

void AppSettings::setDeflectionTolerance(double value) {
    if (value <= 0.0) value = kDeflectionToleranceDefault;
    if (deflection_tolerance_ == value) return;
    deflection_tolerance_ = value;
    persist();
    emit deflectionToleranceChanged(value);
}

double AppSettings::angularTolerance() const {
    return angular_tolerance_;
}

void AppSettings::setAngularTolerance(double value) {
    if (value <= 0.0) value = kAngularToleranceDefault;
    if (angular_tolerance_ == value) return;
    angular_tolerance_ = value;
    persist();
    emit angularToleranceChanged(value);
}

void AppSettings::load() {
    QSettings settings;
    geometry_library_ = settings.value(kGeometryLibraryKey, kGeometryLibraryDefault).toString();
    show_stats_ = settings.value(kShowStatsKey, false).toBool();
    backface_culling_ = settings.value(kBackfaceCullingKey, true).toBool();
    load_data_source_ = settings.value(kLoadDataSourceKey, true).toBool();
    void_limit_ = settings.value(kVoidLimitKey, kVoidLimitDefault).toInt();
    if (void_limit_ < 0) void_limit_ = 0;
    deflection_tolerance_ = settings.value(kDeflectionToleranceKey, kDeflectionToleranceDefault).toDouble();
    if (deflection_tolerance_ <= 0.0) deflection_tolerance_ = kDeflectionToleranceDefault;
    angular_tolerance_ = settings.value(kAngularToleranceKey, kAngularToleranceDefault).toDouble();
    if (angular_tolerance_ <= 0.0) angular_tolerance_ = kAngularToleranceDefault;
}

void AppSettings::persist() {
    QSettings settings;
    settings.setValue(kGeometryLibraryKey, geometry_library_);
    settings.setValue(kShowStatsKey, show_stats_);
    settings.setValue(kBackfaceCullingKey, backface_culling_);
    settings.setValue(kLoadDataSourceKey, load_data_source_);
    settings.setValue(kVoidLimitKey, void_limit_);
    settings.setValue(kDeflectionToleranceKey, deflection_tolerance_);
    settings.setValue(kAngularToleranceKey, angular_tolerance_);
}
