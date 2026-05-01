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

#ifndef FEDERATION_H
#define FEDERATION_H

#include <Eigen/Dense>

#include <QObject>
#include <QString>
#include <QStringList>
#include <QDateTime>
#include <QVector3D>

#include <string>
#include <vector>

namespace ifcopenshell { class file; }

// === Stage-3/4 data model ===
//
// A federation places one or more IFC models in a shared scene.  Each model's
// final per-instance transform is composed as
//
//     stage3 · stage4 · stage2 · placement_stage1
//
// where:
//   - stage1 is per-mesh vertex rebasing (load-time, immutable)
//   - stage2 is the per-model georef matrix from IfcMapConversion etc.
//     (load-time, immutable; can be toggled off)
//   - stage3 is the federation-wide false origin (mutable, federation-scope)
//   - stage4 is the per-model placement within the federation (mutable, per-model)
//
// All composed matrices are in metres.  User-authored numbers are stored in
// their source units (model project unit / model map unit / federation unit)
// to round-trip without precision loss; conversion happens in the compose
// helpers.

// Federation-wide unit; the value space for FederationOrigin.xyz and
// ModelTransform::{b, pivot}.
struct FederationConfig {
    // IfcSIUnit name ("METRE") or IfcConversionBasedUnit name ("foot", "inch").
    std::string unit_name   = "METRE";
    // SI prefix ("MILLI", "KILO", ...) — empty for unprefixed or for
    // conversion-based units.
    std::string unit_prefix = "";
};

// Stage 3 — the federation false origin.  Authoring intent is "nominate this
// XYZ as the new origin, with optional Z-axis heading rotation".  Composed
// as stage3 = R_z(rz_deg) · T(-xyz_in_metres).
struct FederationOrigin {
    Eigen::Vector3d xyz    = Eigen::Vector3d::Zero();   // federation unit
    double          rz_deg = 0.0;
};

// Frame in which ModelTransform.a is expressed.
//   ModelLocal  — pre-stage2 model coordinates, in the model's project length unit
//   ModelGlobal — post-stage2 model coordinates, in the model's map unit
enum class AFrame { ModelLocal, ModelGlobal };

// Stage 4 — the per-model placement within the federation.  Authoring intent
// is "rotate the model around `pivot`, then translate so that point `a` lands
// at point `b`".  Composed as
//     R_local    = R_z(rz) · R_y(ry) · R_x(rx)            [intrinsic XYZ]
//     R_at_pivot = T(pivot_m) · R_local · T(-pivot_m)
//     stage4     = T(b_m - R_at_pivot · a_m) · R_at_pivot
struct ModelTransform {
    AFrame          a_frame  = AFrame::ModelGlobal;
    Eigen::Vector3d a        = Eigen::Vector3d::Zero();   // model project / map unit
    Eigen::Vector3d b        = Eigen::Vector3d::Zero();   // federation unit
    Eigen::Vector3d rxyz_deg = Eigen::Vector3d::Zero();   // degrees, intrinsic XYZ
    Eigen::Vector3d pivot    = Eigen::Vector3d::Zero();   // federation unit
};

// Per-model unit scales captured at load time.  project_length_to_meters
// comes from calculateUnitScale(file, "LENGTHUNIT"); map_unit_to_meters from
// siScaleFromNamedUnit(getMapUnit(file)) and falls back to the project length
// scale when the model has no MapUnit.
struct ModelUnits {
    double project_length_to_meters = 1.0;
    double map_unit_to_meters       = 1.0;
};

// Per-model georeferencing data derived from the IFC.  `stage2_meters` is
// the helmert · inv(wcs) georef matrix in metres; consumers compose it
// before stage 3 / stage 4 at upload time.  When the model has no map
// conversion, `has_stage2 == false` and `stage2_meters` is identity.
struct ModelGeoref {
    ModelUnits      units;
    Eigen::Matrix4d stage2_meters = Eigen::Matrix4d::Identity();
    bool            has_stage2    = false;
};

// Read a model's project length unit, map unit, helmert parameters, and WCS
// from `ifc_file` and reduce them to a metres-in / metres-out georef matrix.
// Pure compute; safe to call repeatedly if the caller doesn't want to cache.
ModelGeoref computeModelGeoref(ifcopenshell::file* ifc_file);

// 1 federation_unit -> N metres.
double federationUnitToMeters(const FederationConfig&);

// Compose stage 3 (federation false origin) into a 4x4 matrix in metres.
Eigen::Matrix4d composeFederationOrigin(const FederationOrigin&,
                                        const FederationConfig&);

// Compose stage 4 (per-model placement within the federation) into a 4x4
// matrix in metres.  `stage2_meters` is the model's georef matrix (e.g.
// helmertMetersFromParameters · inv(wcs_meters)) — needed to lift `a` into
// metres when a_frame == ModelLocal.  Pass identity when stage 2 is disabled
// or absent.
Eigen::Matrix4d composeModelTransform(const ModelTransform&,
                                      const FederationConfig& fed_cfg,
                                      const ModelUnits& model_units,
                                      const Eigen::Matrix4d& stage2_meters);

// === Federation persistence (.ifcfed) ===
//
// In-memory representation of an .ifcfed file (IFC federation).
//
// A federation is a named, ordered list of model sources plus an optional
// "home view" camera state, a federation-wide unit + false origin, and per
// model an optional transform intent.  Source paths can be relative
// (resolved against the .ifcfed's directory) or absolute.  Save() reserialises
// paths relative when they live under the federation file's directory tree,
// absolute otherwise — Save As recomputes against the new location.
class Federation : public QObject {
    Q_OBJECT
public:
    struct HomeView {
        QVector3D target;
        float distance = 50.0f;
        float yaw = 45.0f;     // degrees
        float pitch = 30.0f;   // degrees
    };

    struct Model {
        QString id;                          // stable, persisted
        QString display_name;
        QString source_kind = "local";       // future: "http", "speckle", ...
        QString source_path;                 // resolved absolute when kind == "local"
        ModelTransform transform_intent;     // stage 4
        bool visible = true;
    };

    explicit Federation(QObject* parent = nullptr);

    // Round-trip
    bool load(const QString& path, QStringList* warnings, QString* err);
    bool save(const QString& path, QString* err);

    // Mutations
    void clear();
    QString addModel(const QString& source_path,
                     const QString& display_name = QString());
    void removeModel(const QString& fed_id);
    void setHomeView(const HomeView& hv);
    void clearHomeView();

    void setConfig(const FederationConfig&);
    void setOrigin(const FederationOrigin&);
    void setModelTransform(const QString& fed_id, const ModelTransform&);

    // Accessors
    const std::vector<Model>& models() const { return models_; }
    const Model* findById(const QString& fed_id) const;
    bool isDirty() const { return dirty_; }
    void markClean();
    QString filePath() const { return file_path_; }
    QString name() const { return name_; }
    bool hasHomeView() const { return has_home_view_; }
    const HomeView& homeView() const { return home_view_; }
    const FederationConfig& config() const { return config_; }
    const FederationOrigin& origin() const { return origin_; }

signals:
    void dirtyChanged(bool dirty);

private:
    void setDirty(bool d);
    static QString generateId();
    static bool isFederationPath(const QString& path);

    QString file_path_;
    QString name_;
    QDateTime created_;
    QDateTime modified_;
    std::vector<Model> models_;
    FederationConfig config_;
    FederationOrigin origin_;
    bool has_home_view_ = false;
    HomeView home_view_;
    bool dirty_ = false;
};

#endif // FEDERATION_H
