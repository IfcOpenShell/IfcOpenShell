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

#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace ifcopenshell { class file; }

// === Federation transformation pipeline ===
//
// A federation places one or more IFC models in a shared scene.  Each model's
// final per-instance transform is the composition of four named stages:
//
//     FederatedFalseOrigin · ModelTransformation · CoordinateOperation
//                                                · PlacementTransformation
//
// where:
//   - PlacementTransformation: per-instance, derived from the IFC's
//     IfcObjectPlacement chain (load-time, immutable).  This is the
//     iterator's per-shape transform.
//   - CoordinateOperation: per-model, derived from the IFC's
//     IfcCoordinateOperation (e.g. IfcMapConversion + IfcProjectedCRS).
//     Load-time, immutable; can be toggled on/off.
//   - FederatedFalseOrigin: federation-wide.  Mutable, persisted in
//     `.ifcfed`.  Re-applied to every model.
//   - ModelTransformation: per-model, user-authored within the federation.
//     Mutable, persisted in `.ifcfed`.
//
// All composed matrices are in metres.  User-authored numbers are stored in
// their source units (model project unit / model map unit / federation unit)
// to round-trip without precision loss; conversion happens in the compose
// helpers.

// Federation-wide unit; the value space for FederatedFalseOrigin.xyz and
// ModelTransformation::{b, pivot}.
struct FederationConfig {
    // IfcSIUnit name ("METRE") or IfcConversionBasedUnit name ("foot", "inch").
    std::string unit_name   = "METRE";
    // SI prefix ("MILLI", "KILO", ...) — empty for unprefixed or for
    // conversion-based units.
    std::string unit_prefix = "";
};

// FederatedFalseOrigin — the user-nominated federation origin.  Authoring
// intent is "nominate this XYZ as the new origin, with optional Z-axis
// heading rotation".  Composed as R_z(rz_deg) · T(-xyz_in_metres).
struct FederatedFalseOrigin {
    Eigen::Vector3d xyz    = Eigen::Vector3d::Zero();   // federation unit
    double          rz_deg = 0.0;
};

// Frame in which ModelTransformation.a is expressed.
//   ModelLocal  — pre-CoordinateOperation model coordinates, in the model's
//                 project length unit
//   ModelGlobal — post-CoordinateOperation model coordinates, in the model's
//                 map unit
enum class AFrame { ModelLocal, ModelGlobal };

// ModelTransformation — the per-model placement within the federation.
// Authoring intent is "rotate the model around `pivot`, then translate so
// that point `a` lands at point `b`".  Composed as
//
//     R_local    = R_z(rz) · R_y(ry) · R_x(rx)            [intrinsic XYZ]
//     R_at_pivot = T(pivot_m) · R_local · T(-pivot_m)
//     result     = T(b_m - R_at_pivot · a_m) · R_at_pivot
struct ModelTransformation {
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

// Per-model georeferencing data derived from the IFC.
// `coordinate_operation_meters` is the helmert · inv(wcs) matrix in metres
// representing the IfcCoordinateOperation; consumers compose it before
// FederatedFalseOrigin / ModelTransformation at upload time.  When the
// model has no map conversion, `has_coordinate_operation == false` and the
// matrix is identity.
struct ModelGeoref {
    ModelUnits      units;
    Eigen::Matrix4d coordinate_operation_meters = Eigen::Matrix4d::Identity();
    bool            has_coordinate_operation    = false;
};

// Read a model's project length unit, map unit, helmert parameters, and WCS
// from `ifc_file` and reduce them to a metres-in / metres-out
// CoordinateOperation matrix.  Pure compute; safe to call repeatedly if the
// caller doesn't want to cache.
ModelGeoref computeModelGeoref(ifcopenshell::file* ifc_file);

// Build a FederatedFalseOrigin guess so that a model lands near the
// federation origin instead of out at its surveyor coordinates.  Designed
// to work without an open IFC file so it's usable from sidecar-only loads
// (the inputs are all derivable from the InstanceCpu cache + ModelGeoref).
//
// Position: `first_placement_meters` is the model's "anchor" placement —
// typically the first instance's `placement_transformation`, which the
// iterator already produces in metres (its `convert-back-units` default
// is false).  The translation is optionally lifted through
// `georef.coordinate_operation_meters` (controlled by
// `apply_coordinate_operation`), then expressed in the federation unit.
//
// Rotation: read directly from `georef.coordinate_operation_meters` when
// `apply_coordinate_operation && has_coordinate_operation` (this is the
// helmert grid-north angle).  Otherwise zero.  Anticlockwise positive.
FederatedFalseOrigin
guessFederatedFalseOrigin(const Eigen::Matrix4d& first_placement_meters,
                          const ModelGeoref& georef,
                          const FederationConfig& fed_cfg,
                          bool apply_coordinate_operation);

// 1 federation_unit -> N metres.
double federationUnitToMeters(const FederationConfig&);

// Compose FederatedFalseOrigin into a 4x4 matrix in metres.
Eigen::Matrix4d composeFederatedFalseOrigin(const FederatedFalseOrigin&,
                                            const FederationConfig&);

// Compose ModelTransformation into a 4x4 matrix in metres.
// `coordinate_operation_meters` is the model's CoordinateOperation matrix
// (e.g. helmertMetersFromParameters · inv(wcs_meters)) — needed to lift
// `a` into metres when a_frame == ModelLocal.  Pass identity when the
// CoordinateOperation is disabled or absent.
Eigen::Matrix4d composeModelTransformation(const ModelTransformation&,
                                           const FederationConfig& fed_cfg,
                                           const ModelUnits& model_units,
                                           const Eigen::Matrix4d& coordinate_operation_meters);

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
        QString id;                              // stable, persisted
        QString display_name;
        QString source_kind = "local";           // future: "http", "speckle", ...
        QString source_path;                     // resolved absolute when kind == "local"
        ModelTransformation model_transformation;
        bool visible = true;
        QString group_id;                        // empty = root level
    };

    // Group — a named container for sub-groups and models.  Models are
    // assigned via Model::group_id (one-to-one); sub-groups live in
    // `children` (owning).  Visibility is per-group and cascades: a
    // model is effectively visible only when its `visible` is true and
    // every ancestor group's `visible` is true.
    //
    // `parent` is a non-owning back pointer, kept in sync by Federation
    // mutations.  Group ownership tree is rooted at Federation::root_groups_.
    struct Group {
        QString id;                              // stable, persisted
        QString display_name;
        bool    visible = true;
        std::vector<std::unique_ptr<Group>> children;
        Group*  parent = nullptr;                // not owned; nullptr at root

        Group() = default;
        Group(const Group&) = delete;
        Group& operator=(const Group&) = delete;
        Group(Group&&) = default;
        Group& operator=(Group&&) = default;
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
    void setFederatedFalseOrigin(const FederatedFalseOrigin&);
    void setModelTransformation(const QString& fed_id, const ModelTransformation&);
    void setModelVisible(const QString& fed_id, bool visible);
    // Reassign a model to a group (or to root, when group_id is empty).
    // No-op when fed_id is unknown or group_id is unknown-and-non-empty.
    void setModelGroup(const QString& fed_id, const QString& group_id);

    // Group mutations.  All return / accept stable group ids.
    QString addGroup(const QString& display_name = QString(),
                     const QString& parent_id = QString());
    // Removes the group; child sub-groups + child models are reparented
    // to the removed group's parent (i.e. up one level).  No-op when
    // group_id is unknown.
    void removeGroup(const QString& group_id);
    void setGroupName(const QString& group_id, const QString& display_name);
    // Reparents a group.  No-op if the move would create a cycle (new
    // parent is the group itself or one of its descendants) or if either
    // id is unknown.
    void setGroupParent(const QString& group_id, const QString& parent_id);
    void setGroupVisible(const QString& group_id, bool visible);

    // Accessors
    const std::vector<Model>& models() const { return models_; }
    const Model* findById(const QString& fed_id) const;
    // Top-level groups in insertion order; descend via Group::children.
    const std::vector<std::unique_ptr<Group>>& rootGroups() const { return root_groups_; }
    const Group* findGroupById(const QString& group_id) const;
    // Depth-first flatten: every group in the tree, parents before
    // children.  Cheap, intended for UI iteration.
    std::vector<const Group*> allGroups() const;
    // True iff every ancestor of `group_id` (inclusive of `group_id`
    // itself) has visible == true.  Returns true for empty group_id (root).
    bool isGroupChainVisible(const QString& group_id) const;
    // True iff the model exists, its own `visible` is true, and every
    // ancestor group is visible.
    bool isModelEffectivelyVisible(const QString& fed_id) const;
    bool isDirty() const { return dirty_; }
    void markClean();
    QString filePath() const { return file_path_; }
    QString name() const { return name_; }
    bool hasHomeView() const { return has_home_view_; }
    const HomeView& homeView() const { return home_view_; }
    const FederationConfig& config() const { return config_; }
    const FederatedFalseOrigin& federatedFalseOrigin() const { return federated_false_origin_; }

signals:
    void dirtyChanged(bool dirty);

    // Granular signals so consumers (notably the viewport-pushing layer in
    // the host app) can recompose only what's needed.  Emitted in addition
    // to dirtyChanged from the corresponding setters.
    void configChanged();
    void federatedFalseOriginChanged();
    void modelTransformationChanged(const QString& fed_id);
    void modelVisibilityChanged(const QString& fed_id, bool visible);
    void modelGroupChanged(const QString& fed_id, const QString& group_id);

    void groupAdded(const QString& group_id);
    void groupRemoved(const QString& group_id);
    // Emitted on rename or reparent.
    void groupChanged(const QString& group_id);
    // Visibility flip on this group only.  Effective visibility of
    // descendant models also changes; consumers that care should walk
    // descendants themselves.
    void groupVisibilityChanged(const QString& group_id, bool visible);

private:
    void setDirty(bool d);
    static QString generateId();
    static bool isFederationPath(const QString& path);

    Group* findGroupByIdMutable(const QString& group_id);
    // Detach a group from its current parent's children vector, returning
    // ownership.  group->parent is left set to its former parent — the
    // caller must update it before reattachment.  Returns nullptr if the
    // group can't be found in the expected parent.
    std::unique_ptr<Group> detachGroup(Group* group);
    // True iff `candidate_descendant` is `group` itself or any descendant.
    static bool isDescendantOrSelf(const Group* group,
                                    const Group* candidate_descendant);
    // DFS append for allGroups() and similar walks.
    static void appendDfs(const Group* g, std::vector<const Group*>& out);

    QString file_path_;
    QString name_;
    QDateTime created_;
    QDateTime modified_;
    std::vector<Model> models_;
    std::vector<std::unique_ptr<Group>> root_groups_;
    FederationConfig     config_;
    FederatedFalseOrigin federated_false_origin_;
    bool has_home_view_ = false;
    HomeView home_view_;
    bool dirty_ = false;
};

#endif // FEDERATION_H
