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

#ifndef APPSETTINGS_H
#define APPSETTINGS_H

#include <QObject>
#include <QString>

// Application-wide preferences. Cached in memory, persisted via QSettings to
// the OS-native config location (registry on Windows, plist on macOS, INI on
// Linux). Access via AppSettings::instance().
class AppSettings : public QObject {
    Q_OBJECT
public:
    // Navigation preset.  Selects which mouse button (+ optional Shift)
    // drives orbit and pan.  Selection is unaffected and stays on LMB
    // for every preset — these three intentionally don't take LMB so
    // click + box-select remain available without modifier gymnastics.
    //
    //   Blender   — Orbit MMB,        Pan Shift+MMB   (current default)
    //   Rhino     — Orbit RMB,        Pan Shift+RMB
    //   Revit     — Orbit Shift+MMB,  Pan MMB
    //   Web       — Orbit LMB,        Pan MMB,        Select RMB
    enum class NavPreset {
        Blender = 0,
        Rhino   = 1,
        Revit   = 2,
        Web     = 3,
    };
    Q_ENUM(NavPreset)

    // Preset → the lowercase name ViewportCore::setNavPreset / applyNavPreset take.
    static const char* navPresetName(NavPreset preset);

    static AppSettings& instance();

    QString geometryLibrary() const;
    void setGeometryLibrary(const QString& value);

    bool showStats() const;
    void setShowStats(bool value);

    bool backfaceCulling() const;
    void setBackfaceCulling(bool value);

    // Skip elements with more than this many voids (HasOpenings inverse).
    // Boolean subtraction of many openings is the dominant cost in some
    // pathological exports; dropping those elements keeps load times sane.
    int voidLimit() const;
    void setVoidLimit(int value);

    // Mesher tolerances passed straight to the IfcOpenShell iterator.
    // Linear deflection bounds the chord error between a curve and its
    // triangulation, in model length units; angular deflection bounds the
    // angle (radians) between adjacent facet normals on a curved surface.
    // Smaller values mean smoother geometry at the cost of more triangles
    // and slower iteration.
    double deflectionTolerance() const;
    void setDeflectionTolerance(double value);
    double angularTolerance() const;
    void setAngularTolerance(double value);

    // Minimum projected sphere radius (in pixels) for an instance to be
    // worth drawing — below this it's contribution-culled.  Bigger value
    // = faster rendering but more pop-in on small detail; smaller =
    // more thorough but more draw cost.
    double minPixelRadius() const;
    void setMinPixelRadius(double value);

    // Aggressive contribution-cull threshold while the camera is moving.
    // 0 disables the motion boost (motion uses minPixelRadius like still
    // frames).  When >= minPixelRadius, motion frames raise the bar so
    // transient camera moves stay smooth on heavy scenes.
    double motionMinPixelRadius() const;
    void setMotionMinPixelRadius(double value);

    // Projected sphere radius (in pixels) below which an instance
    // switches to its LOD1 representation.  0 disables LOD1 entirely
    // (always draw LOD0).
    double lod1PixelThreshold() const;
    void setLod1PixelThreshold(double value);

    // Base HiZ pyramid width in texels (height tracks aspect).  Bigger
    // = tighter occlusion but more readback bandwidth.  Floored at 64.
    // Changes take effect on next viewport reinitialization.
    int hizResolution() const;
    void setHizResolution(int value);

    // Master toggle for HiZ occlusion culling.  When false, only the
    // frustum + contribution cull run; geometry hidden behind opaque
    // blockers still draws.
    bool hizEnabled() const;
    void setHizEnabled(bool value);

    // Navigation preset (see NavPreset enum above).
    NavPreset navPreset() const;
    void setNavPreset(NavPreset value);

signals:
    void geometryLibraryChanged(const QString& value);
    void showStatsChanged(bool value);
    void backfaceCullingChanged(bool value);
    void voidLimitChanged(int value);
    void deflectionToleranceChanged(double value);
    void angularToleranceChanged(double value);
    void minPixelRadiusChanged(double value);
    void motionMinPixelRadiusChanged(double value);
    void lod1PixelThresholdChanged(double value);
    void hizResolutionChanged(int value);
    void hizEnabledChanged(bool value);
    void navPresetChanged(NavPreset value);

private:
    AppSettings();
    void load();
    void persist();

    QString geometry_library_;
    bool show_stats_ = false;
    bool backface_culling_ = true;
    int void_limit_ = 30;
    double deflection_tolerance_ = 0.001;
    double angular_tolerance_ = 0.5;
    double min_pixel_radius_ = 2.0;
    double motion_min_pixel_radius_ = 10.0;
    double lod1_pixel_threshold_ = 30.0;
    int hiz_resolution_ = 256;
    bool hiz_enabled_ = true;
    NavPreset nav_preset_ = NavPreset::Blender;
};

#endif // APPSETTINGS_H
