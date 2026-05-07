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

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTreeWidget>
#include <QTableWidget>
#include <QProgressBar>
#include <QLabel>
#include <QSplitter>
#include <QElapsedTimer>

#include <map>
#include <unordered_map>
#include <vector>

#include "Measurement.h"
#include "ViewportWindow.h"
#include "SceneLoader.h"

class Federation;
class SettingsWindow;
class FederationSettingsDialog;
class ModelTransformationDialog;

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget* parent = nullptr);
    ~MainWindow();

    void addFiles(const QStringList& paths);
    bool openFederation(const QString& path);
    void setPendingCamera(const QString& params);
    void setPendingBenchmark(int frames);

protected:
    void closeEvent(QCloseEvent* event) override;

private slots:
    void onFileOpen();
    void onDatabaseOpen();
    void onFederationNew();
    void onFederationOpen();
    bool onFederationSave();
    bool onFederationSaveAs();
    void onSetHomeView();
    void onGoHomeView();
    void onFileSettings();
    void onFederationSettings();
    void onModelTransformations();
    void onObjectPicked(uint32_t object_id);
    void onTreeSelectionChanged();
    void onTreeContextMenu(const QPoint& pos);

    void onLoadStarted(uint32_t mid, QString display_name);
    void onLoadProgressChanged(int percent);
    void onSidecarElementsReady(uint32_t mid,
                                std::vector<PackedElementInfo> elements,
                                std::string string_table);
    void onLoadedFromSidecar(uint32_t mid, qint64 elapsed_ms);
    void onDataSourceReady(uint32_t mid);
    void onStreamedElementsReady(uint32_t mid, std::vector<ElementInfo> elements);
    void onLoadedFromStream(uint32_t mid, qint64 elapsed_ms);
    void onLoadCancelled(uint32_t mid);
    void onLoadError(uint32_t mid, QString message);
    void onAllLoadsFinished();

private:
    void setupUi();
    void setupMenus();
    void loadModelsFromPaths(const QStringList& paths,
                             const QStringList& fed_ids);
    void clearScene();
    bool confirmDiscardIfDirty();
    void updateWindowTitle();
    void populateProperties(uint32_t object_id);
    void appendElementToTree(uint32_t model_id,
                             uint32_t object_id,
                             int ifc_id,
                             int parent_ifc_id,
                             const std::string& guid,
                             const std::string& name,
                             const std::string& type);
    void writeSidecarForModel(uint32_t mid);
    void removeModelUi(uint32_t mid);
    void removeModel(uint32_t mid);
    // Returns the model_id whose tree root is `item`, or 0 if `item` is not
    // a model root (i.e. an element row, group, or null).
    uint32_t modelIdForRoot(QTreeWidgetItem* item) const;
    // Returns the group_id whose tree item is `item`, or empty string when
    // `item` is null or is not a group item.
    QString  groupIdForItem(QTreeWidgetItem* item) const;
    // Place / reparent a model root under its group (or at top level when
    // group_id is empty / unknown).  Idempotent.  No-op if there's no tree
    // root yet for `mid`.
    void     reparentModelTreeRoot(uint32_t mid);
    // Place / reparent a group item under its parent group (or at top
    // level).  Idempotent.  No-op if there's no tree item for `group_id`.
    void     reparentGroupTreeItem(const QString& group_id);
    // Lazily create the QTreeWidgetItem for `group_id` if not already in
    // group_tree_items_.  Returns the item.  Sets text + flags but does
    // not place it under a parent — call reparentGroupTreeItem afterwards.
    QTreeWidgetItem* ensureGroupTreeItem(const QString& group_id);
    // Recompute italic/grey on a group row from current effective visibility.
    void     refreshGroupRowAppearance(const QString& group_id);
    // Walk descendants of `group_id` and re-push effective visibility to
    // the viewport for every model under it.  When `group_id` is empty,
    // re-pushes every model in the federation.
    void     applyVisibilityCascadeFromGroup(const QString& group_id);
    // Walk every group_id whose ancestor chain currently includes
    // `group_id` (inclusive).
    std::vector<QString> descendantGroupIds(const QString& group_id) const;
    // Push the federation's `visible` flag for `mid` onto the viewport.
    // No-op if `mid` is not in the federation map.  Idempotent — safe to
    // call before the model is finalised on the viewport (hideModel is a
    // lookup-and-set on models_gpu_; missing entries are skipped).
    void applyModelVisibilityToViewport(uint32_t mid);
    void applyPendingBenchmark();

    // Push a model's CoordinateOperation matrix to the viewport (or
    // identity, when the AppSettings toggle is off or the model has no
    // map conversion).  No-op if the model isn't yet known to the loader
    // or its IFC file isn't available (sidecar-hit before data-source
    // load); the call retries on onDataSourceReady.
    void applyCoordinateOperationToViewport(uint32_t mid);

    // Push a model's ModelTransformation (stage 4) matrix to the viewport,
    // composed from the federation's authoring intent + the model's units
    // + the active CoordinateOperation matrix.  Identity when the model is
    // not in the federation.
    void applyModelTransformationToViewport(uint32_t mid);

    // Push the federation-wide FederatedFalseOrigin (stage 3) matrix to
    // the viewport.  Affects every loaded model.
    void applyFederatedFalseOriginToViewport();

    // For an untitled federation whose FederatedFalseOrigin is still at
    // its default, derive a sensible origin from `mid`'s first instance
    // placement + georef and push it via Federation.  Idempotent: a
    // non-default origin (user-edited, already guessed by a sibling load
    // in the same batch, or loaded from a saved .ifcfed) is left
    // untouched, so multi-file batches naturally anchor on whichever
    // model finishes first.
    void maybeGuessFederatedFalseOrigin(uint32_t mid);
    QString formatElapsed(qint64 ms) const;

    ViewportWindow* viewport_ = nullptr;
    SceneLoader*    loader_   = nullptr;
    Federation*     federation_ = nullptr;
    SettingsWindow* settings_ = nullptr;
    FederationSettingsDialog* federation_settings_ = nullptr;
    ModelTransformationDialog* model_transformations_ = nullptr;
    QWidget* viewport_container_ = nullptr;
    QTreeWidget* element_tree_ = nullptr;
    QTableWidget* property_table_ = nullptr;
    QProgressBar* progress_bar_ = nullptr;
    QLabel* status_label_ = nullptr;
    QLabel* stats_label_ = nullptr;

    // Per-model tree roots, keyed by model_id.  May live at the top level
    // of element_tree_ or as a child of a group tree item.
    std::map<uint32_t, QTreeWidgetItem*> tree_roots_;
    // Per-group tree items, keyed by Federation group id.
    std::unordered_map<QString, QTreeWidgetItem*> group_tree_items_;

    // Bidirectional federation_id <-> model_id map.  Federation owns the
    // persistent ids; SceneLoader owns the runtime model_ids.
    std::unordered_map<QString, uint32_t> fed_id_to_model_id_;
    std::unordered_map<uint32_t, QString> model_id_to_fed_id_;

    // Display-side element registry for tree + property lookup.
    std::unordered_map<uint32_t, ElementInfo> element_map_;
    std::unordered_map<uint32_t, QTreeWidgetItem*> tree_items_;
    // Scoped (model_id, ifc_id) -> object_id
    std::unordered_map<uint64_t, uint32_t> scoped_ifc_id_to_object_id_;

    static uint64_t scopedKey(uint32_t model_id, int ifc_id) {
        return (static_cast<uint64_t>(model_id) << 32) | static_cast<uint32_t>(ifc_id);
    }

    QString pending_camera_;
    int     pending_benchmark_ = 0;

    AreaMeasurement area_measurement_;
};

#endif // MAINWINDOW_H
