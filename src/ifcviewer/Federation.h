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

#include "FederationMath.h"

#include <Eigen/Dense>

#include <QJsonObject>
#include <QObject>
#include <QString>
#include <QStringList>
#include <QDateTime>

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

// Read a model's project length unit, map unit, helmert parameters, and WCS
// from `ifc_file` and reduce them to a metres-in / metres-out
// CoordinateOperation matrix.  Pure compute; safe to call repeatedly if the
// caller doesn't want to cache.
ModelGeoref computeModelGeoref(ifcopenshell::file* ifc_file);

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
        Eigen::Vector3f target  = Eigen::Vector3f::Zero();
        float distance          = 50.0f;
        float yaw               = 45.0f;     // degrees
        float pitch             = 30.0f;     // degrees
    };

    struct Model {
        QString id;                              // stable, persisted
        QString display_name;
        // "local" or a connector id (e.g. "autodesk") per CLOUD_SYNC_PROTOCOL.md.
        QString source_connector = "local";
        // Local connector: resolved absolute path. Empty for cloud sources.
        QString source_path;
        // Cloud connectors: arbitrary connector-specific keys, round-tripped
        // verbatim. Empty / unused for "local".
        QJsonObject source_data;
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
    // Serialise to `path` without touching internal state (file_path_,
    // modified_, dirty_). Used by cloud-push paths to produce a temporary
    // .ifcfed without claiming it as the project's canonical location.
    bool writeCopyTo(const QString& path, QString* err) const;
    // Repoint this project to a new on-disk location without re-loading its
    // content. Updates file_path_, re-reads adjacent .manifest, marks clean.
    // Used after push_ifcfed[_interactive] — the connector wrote a fresh
    // copy and (maybe) manifest to its cache; we already have the content
    // in memory.
    void repointTo(const QString& new_path, QStringList* warnings = nullptr);

    // Mutations
    void clear();
    // display_name is stored verbatim — callers decide the label (typically
    // QFileInfo(source_path).fileName() for local files). No implicit fallback.
    QString addModel(const QString& source_path,
                     const QString& display_name);
    // Add a model whose source is a cloud connector (anything other than
    // "local"). `source_data` holds the connector-specific keys; the
    // top-level "connector" field, if present, is overwritten with
    // `connector_id`. Returns the new fed id, or {} on empty inputs.
    QString addCloudModel(const QString& display_name,
                          const QString& connector_id,
                          const QJsonObject& source_data);
    void removeModel(const QString& model_id);
    void setHomeView(const HomeView& hv);
    void clearHomeView();

    void setConfig(const FederationConfig&);
    void setFederatedFalseOrigin(const FederatedFalseOrigin&);
    void setModelTransformation(const QString& model_id, const ModelTransformation&);
    void setModelVisible(const QString& model_id, bool visible);
    // Rename a model. No-op when model_id is unknown, name is empty, or
    // name is unchanged.
    void setModelDisplayName(const QString& model_id, const QString& display_name);
    // Replace a model's source. Used after push_model[_interactive] when
    // the connector reports a fresh source (e.g. a new version_id) or when
    // a previously-local model gets uploaded for the first time. The
    // top-level "connector" key in `source_data`, if any, is dropped —
    // it's expressed via `connector_id`.
    void setModelSource(const QString& model_id,
                        const QString& connector_id,
                        const QJsonObject& source_data);
    // Reassign a model to a group (or to root, when group_id is empty).
    // No-op when model_id is unknown or group_id is unknown-and-non-empty.
    void setModelGroup(const QString& model_id, const QString& group_id);

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
    const Model* findById(const QString& model_id) const;
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
    bool isModelEffectivelyVisible(const QString& model_id) const;
    bool isDirty() const { return dirty_; }
    void markClean();
    QString filePath() const { return file_path_; }
    QString name() const { return name_; }
    bool hasHomeView() const { return has_home_view_; }
    const HomeView& homeView() const { return home_view_; }
    const FederationConfig& config() const { return config_; }
    const FederatedFalseOrigin& federatedFalseOrigin() const { return federated_false_origin_; }

    // .ifcfed.manifest sidecar — present iff this project came from a
    // cloud connector. Read best-effort during load() (no warning if
    // absent); the connector owns writing. setManifest is called after
    // push_ifcfed[_interactive] returns a fresh manifest.
    bool hasManifest() const { return has_manifest_; }
    const QJsonObject& manifest() const { return manifest_; }
    QString manifestConnectorId() const;
    void setManifest(const QJsonObject& manifest);
    void clearManifest();

signals:
    void dirtyChanged(bool dirty);

    // Granular signals so consumers (notably the viewport-pushing layer in
    // the host app) can recompose only what's needed.  Emitted in addition
    // to dirtyChanged from the corresponding setters.
    void configChanged();
    void federatedFalseOriginChanged();
    void modelAdded(const QString& model_id);
    void modelRemoved(const QString& model_id);
    void modelTransformationChanged(const QString& model_id);
    void modelVisibilityChanged(const QString& model_id, bool visible);
    void modelGroupChanged(const QString& model_id, const QString& group_id);
    // Emitted on rename / source change — anything that affects how the
    // model is displayed but is not covered by the other granular signals.
    void modelChanged(const QString& model_id);

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

    // Pure-write helper shared by save() and writeCopyTo(). Builds the
    // JSON using the timestamps it's given (so save() can commit them to
    // member state, while writeCopyTo() can pass throwaway values), and
    // writes via QSaveFile. Never mutates `this`.
    bool writeJsonAt(const QString& abs_path,
                     const QDateTime& created_to_emit,
                     const QDateTime& modified_to_emit,
                     QString* err) const;

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
    bool has_manifest_ = false;
    QJsonObject manifest_;
    bool dirty_ = false;
};

#endif // FEDERATION_H
