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
constexpr const char* kVoidLimitKey = "loading/void_limit";
constexpr int kVoidLimitDefault = 30;
constexpr const char* kDeflectionToleranceKey = "loading/deflection_tolerance";
constexpr double kDeflectionToleranceDefault = 0.001;
constexpr const char* kAngularToleranceKey = "loading/angular_tolerance";
constexpr double kAngularToleranceDefault = 0.5;
constexpr const char* kMinPixelRadiusKey = "viewport/min_pixel_radius";
constexpr double kMinPixelRadiusDefault = 2.0;
constexpr const char* kMotionMinPixelRadiusKey = "viewport/motion_min_pixel_radius";
constexpr double kMotionMinPixelRadiusDefault = 10.0;
constexpr const char* kLod1PixelThresholdKey = "viewport/lod1_pixel_threshold";
constexpr double kLod1PixelThresholdDefault = 30.0;
constexpr const char* kHizResolutionKey = "viewport/hiz_resolution";
constexpr int kHizResolutionDefault = 256;
constexpr int kHizResolutionFloor = 64;
constexpr const char* kHizEnabledKey = "viewport/hiz_enabled";
constexpr const char* kNavPresetKey = "viewport/nav_preset";
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

double AppSettings::minPixelRadius() const {
    return min_pixel_radius_;
}

void AppSettings::setMinPixelRadius(double value) {
    if (value < 0.0) value = 0.0;
    if (min_pixel_radius_ == value) return;
    min_pixel_radius_ = value;
    persist();
    emit minPixelRadiusChanged(value);
}

double AppSettings::motionMinPixelRadius() const {
    return motion_min_pixel_radius_;
}

void AppSettings::setMotionMinPixelRadius(double value) {
    if (value < 0.0) value = 0.0;
    if (motion_min_pixel_radius_ == value) return;
    motion_min_pixel_radius_ = value;
    persist();
    emit motionMinPixelRadiusChanged(value);
}

double AppSettings::lod1PixelThreshold() const {
    return lod1_pixel_threshold_;
}

void AppSettings::setLod1PixelThreshold(double value) {
    if (value < 0.0) value = 0.0;
    if (lod1_pixel_threshold_ == value) return;
    lod1_pixel_threshold_ = value;
    persist();
    emit lod1PixelThresholdChanged(value);
}

int AppSettings::hizResolution() const {
    return hiz_resolution_;
}

void AppSettings::setHizResolution(int value) {
    if (value < kHizResolutionFloor) value = kHizResolutionFloor;
    if (hiz_resolution_ == value) return;
    hiz_resolution_ = value;
    persist();
    emit hizResolutionChanged(value);
}

bool AppSettings::hizEnabled() const {
    return hiz_enabled_;
}

void AppSettings::setHizEnabled(bool value) {
    if (hiz_enabled_ == value) return;
    hiz_enabled_ = value;
    persist();
    emit hizEnabledChanged(value);
}

AppSettings::NavPreset AppSettings::navPreset() const {
    return nav_preset_;
}

const char* AppSettings::navPresetName(NavPreset preset) {
    switch (preset) {
        case NavPreset::Rhino:   return "rhino";
        case NavPreset::Revit:   return "revit";
        case NavPreset::Web:     return "web";
        case NavPreset::Blender: break;
    }
    return "blender";
}

void AppSettings::setNavPreset(NavPreset value) {
    if (nav_preset_ == value) return;
    nav_preset_ = value;
    persist();
    emit navPresetChanged(value);
}

void AppSettings::load() {
    QSettings settings;
    geometry_library_ = settings.value(kGeometryLibraryKey, kGeometryLibraryDefault).toString();
    show_stats_ = settings.value(kShowStatsKey, false).toBool();
    backface_culling_ = settings.value(kBackfaceCullingKey, true).toBool();
    void_limit_ = settings.value(kVoidLimitKey, kVoidLimitDefault).toInt();
    if (void_limit_ < 0) void_limit_ = 0;
    deflection_tolerance_ = settings.value(kDeflectionToleranceKey, kDeflectionToleranceDefault).toDouble();
    if (deflection_tolerance_ <= 0.0) deflection_tolerance_ = kDeflectionToleranceDefault;
    angular_tolerance_ = settings.value(kAngularToleranceKey, kAngularToleranceDefault).toDouble();
    if (angular_tolerance_ <= 0.0) angular_tolerance_ = kAngularToleranceDefault;
    min_pixel_radius_ = settings.value(kMinPixelRadiusKey, kMinPixelRadiusDefault).toDouble();
    if (min_pixel_radius_ < 0.0) min_pixel_radius_ = 0.0;
    motion_min_pixel_radius_ =
        settings.value(kMotionMinPixelRadiusKey, kMotionMinPixelRadiusDefault).toDouble();
    if (motion_min_pixel_radius_ < 0.0) motion_min_pixel_radius_ = 0.0;
    lod1_pixel_threshold_ =
        settings.value(kLod1PixelThresholdKey, kLod1PixelThresholdDefault).toDouble();
    if (lod1_pixel_threshold_ < 0.0) lod1_pixel_threshold_ = 0.0;
    hiz_resolution_ = settings.value(kHizResolutionKey, kHizResolutionDefault).toInt();
    if (hiz_resolution_ < kHizResolutionFloor) hiz_resolution_ = kHizResolutionFloor;
    hiz_enabled_ = settings.value(kHizEnabledKey, true).toBool();
    {
        const int raw = settings.value(kNavPresetKey,
                                       static_cast<int>(NavPreset::Blender)).toInt();
        // Clamp to known values so a stale config doesn't drop us into
        // an undefined preset slot.
        if (raw < 0 || raw > static_cast<int>(NavPreset::Web)) {
            nav_preset_ = NavPreset::Blender;
        } else {
            nav_preset_ = static_cast<NavPreset>(raw);
        }
    }
}

void AppSettings::persist() {
    QSettings settings;
    settings.setValue(kGeometryLibraryKey, geometry_library_);
    settings.setValue(kShowStatsKey, show_stats_);
    settings.setValue(kBackfaceCullingKey, backface_culling_);
    settings.setValue(kVoidLimitKey, void_limit_);
    settings.setValue(kDeflectionToleranceKey, deflection_tolerance_);
    settings.setValue(kAngularToleranceKey, angular_tolerance_);
    settings.setValue(kMinPixelRadiusKey, min_pixel_radius_);
    settings.setValue(kMotionMinPixelRadiusKey, motion_min_pixel_radius_);
    settings.setValue(kLod1PixelThresholdKey, lod1_pixel_threshold_);
    settings.setValue(kHizResolutionKey, hiz_resolution_);
    settings.setValue(kHizEnabledKey, hiz_enabled_);
    settings.setValue(kNavPresetKey, static_cast<int>(nav_preset_));
}
