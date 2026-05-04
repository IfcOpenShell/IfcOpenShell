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

#include "MainWindow.h"
#include "AppSettings.h"
#include "Federation.h"
#include "FederationSettingsDialog.h"
#include "ModelTransformationDialog.h"
#include "SettingsWindow.h"
#include "LodBuilder.h"
#include "SidecarCache.h"

#include <QApplication>
#include <QCloseEvent>

#include <algorithm>
#include <QMenu>
#include <QMenuBar>
#include <QFileDialog>
#include <QFileInfo>
#include <QFont>
#include <QInputDialog>
#include <QMessageBox>
#include <QStatusBar>
#include <QHeaderView>
#include <QVBoxLayout>
#include <QDockWidget>
#include <QListView>
#include <QTreeView>
#include <QAbstractItemView>
#include <QDebug>

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    setupUi();
    setupMenus();

    federation_ = new Federation(this);

    // Federation -> viewport: granular signals so we recompose only what's
    // affected.  Each handler reads the current federation state, composes
    // the matrix, and pushes to the viewport.
    connect(federation_, &Federation::federatedFalseOriginChanged,
            this, &MainWindow::applyFederatedFalseOriginToViewport);
    connect(federation_, &Federation::configChanged, this, [this]() {
        // Federation unit changed — both stage 3 (uses fed unit) and every
        // model's stage 4 (b/pivot are in fed units) need recomposing.
        applyFederatedFalseOriginToViewport();
        for (const auto& kv : fed_id_to_model_id_) {
            applyModelTransformationToViewport(kv.second);
        }
    });
    connect(federation_, &Federation::modelTransformationChanged,
            this, [this](const QString& fed_id) {
        auto it = fed_id_to_model_id_.find(fed_id);
        if (it != fed_id_to_model_id_.end()) {
            applyModelTransformationToViewport(it->second);
        }
    });
    connect(federation_, &Federation::modelVisibilityChanged,
            this, [this](const QString& fed_id, bool /*visible*/) {
        auto it = fed_id_to_model_id_.find(fed_id);
        if (it != fed_id_to_model_id_.end()) {
            applyModelVisibilityToViewport(it->second);
        }
    });

    connect(federation_, &Federation::modelGroupChanged,
            this, [this](const QString& fed_id, const QString& /*group_id*/) {
        auto it = fed_id_to_model_id_.find(fed_id);
        if (it == fed_id_to_model_id_.end()) return;
        reparentModelTreeRoot(it->second);
        // Effective visibility may have flipped because the new group's
        // chain visibility differs from the old one.
        applyModelVisibilityToViewport(it->second);
    });

    connect(federation_, &Federation::groupAdded,
            this, [this](const QString& group_id) {
        ensureGroupTreeItem(group_id);
        reparentGroupTreeItem(group_id);
        refreshGroupRowAppearance(group_id);
    });

    connect(federation_, &Federation::groupChanged,
            this, [this](const QString& group_id) {
        const Federation::Group* g = federation_->findGroupById(group_id);
        if (!g) return;
        auto it = group_tree_items_.find(group_id);
        if (it == group_tree_items_.end()) return;
        it->second->setText(0, g->display_name);
        reparentGroupTreeItem(group_id);
        // Reparenting a group changes the chain visibility for the moved
        // group + its descendants — refresh both rows and viewport.
        for (const QString& gid : descendantGroupIds(group_id)) {
            refreshGroupRowAppearance(gid);
        }
        applyVisibilityCascadeFromGroup(group_id);
    });

    connect(federation_, &Federation::groupVisibilityChanged,
            this, [this](const QString& group_id, bool /*visible*/) {
        for (const QString& gid : descendantGroupIds(group_id)) {
            refreshGroupRowAppearance(gid);
        }
        applyVisibilityCascadeFromGroup(group_id);
    });

    connect(federation_, &Federation::groupRemoved,
            this, [this](const QString& group_id) {
        auto it = group_tree_items_.find(group_id);
        if (it == group_tree_items_.end()) return;
        // By now, the federation has fired groupChanged / modelGroupChanged
        // for every direct child, and our slots have moved them out from
        // under this item, so deleting it just removes the (now empty)
        // group row.
        delete it->second;
        group_tree_items_.erase(it);
    });

    connect(federation_, &Federation::dirtyChanged, this, [this](bool dirty) {
        setWindowModified(dirty);
    });

    loader_ = new SceneLoader(viewport_, this);
    connect(loader_, &SceneLoader::loadStarted,
            this, &MainWindow::onLoadStarted);
    connect(loader_, &SceneLoader::progressChanged,
            this, &MainWindow::onLoadProgressChanged);
    connect(loader_, &SceneLoader::sidecarElementsReady,
            this, &MainWindow::onSidecarElementsReady);
    connect(loader_, &SceneLoader::loadedFromSidecar,
            this, &MainWindow::onLoadedFromSidecar);
    connect(loader_, &SceneLoader::dataSourceReady,
            this, &MainWindow::onDataSourceReady);
    connect(loader_, &SceneLoader::streamedElementsReady,
            this, &MainWindow::onStreamedElementsReady);
    connect(loader_, &SceneLoader::loadedFromStream,
            this, &MainWindow::onLoadedFromStream);
    connect(loader_, &SceneLoader::loadCancelled,
            this, &MainWindow::onLoadCancelled);
    connect(loader_, &SceneLoader::loadError,
            this, &MainWindow::onLoadError);
    connect(loader_, &SceneLoader::allLoadsFinished,
            this, &MainWindow::onAllLoadsFinished);

    connect(viewport_, &ViewportWindow::frameStatsUpdated, this,
            [this](const ViewportWindow::FrameStats& s) {
        if (!stats_label_->isVisible()) return;
        stats_label_->setText(
            QString("%1 fps | %2 ms | %3/%4 obj | %5/%6 tri | %7 gl_draws (%8 sub)")
                .arg(s.fps, 0, 'f', 1)
                .arg(s.frame_time_ms, 0, 'f', 1)
                .arg(s.visible_objects)
                .arg(s.total_objects)
                .arg(s.visible_triangles)
                .arg(s.total_triangles)
                .arg(s.gl_draw_calls)
                .arg(s.indirect_sub_draws));
    });

    connect(&AppSettings::instance(), &AppSettings::showStatsChanged, this, [this](bool show) {
        stats_label_->setVisible(show);
        if (!show) stats_label_->clear();
    });

    // Toggling the CoordinateOperation setting walks every loaded model
    // and pushes either its georef matrix or identity to the viewport.
    connect(&AppSettings::instance(),
            &AppSettings::applyCoordinateOperationChanged,
            this, [this](bool /*enabled*/) {
        for (const auto& kv : fed_id_to_model_id_) {
            applyCoordinateOperationToViewport(kv.second);
        }
    });

    updateWindowTitle();
    resize(1400, 900);
}

MainWindow::~MainWindow() = default;

void MainWindow::setupUi() {
    viewport_ = new ViewportWindow();
    viewport_container_ = QWidget::createWindowContainer(viewport_, this);
    viewport_container_->setMinimumSize(400, 300);
    viewport_container_->setFocusPolicy(Qt::StrongFocus);
    setCentralWidget(viewport_container_);

    connect(viewport_, &ViewportWindow::objectPicked, this, &MainWindow::onObjectPicked);

    auto* tree_dock = new QDockWidget("Elements", this);
    tree_dock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    element_tree_ = new QTreeWidget();
    element_tree_->setHeaderLabels({"Name", "Type", "GUID"});
    element_tree_->setColumnWidth(0, 200);
    element_tree_->setColumnWidth(1, 120);
    element_tree_->setSelectionMode(QAbstractItemView::SingleSelection);
    element_tree_->setContextMenuPolicy(Qt::CustomContextMenu);
    connect(element_tree_, &QTreeWidget::itemSelectionChanged, this, &MainWindow::onTreeSelectionChanged);
    connect(element_tree_, &QTreeWidget::customContextMenuRequested,
            this, &MainWindow::onTreeContextMenu);
    tree_dock->setWidget(element_tree_);
    addDockWidget(Qt::LeftDockWidgetArea, tree_dock);

    auto* prop_dock = new QDockWidget("Properties", this);
    prop_dock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    property_table_ = new QTableWidget();
    property_table_->setColumnCount(2);
    property_table_->setHorizontalHeaderLabels({"Property", "Value"});
    property_table_->horizontalHeader()->setStretchLastSection(true);
    property_table_->setEditTriggers(QAbstractItemView::NoEditTriggers);
    property_table_->setSelectionBehavior(QAbstractItemView::SelectRows);
    prop_dock->setWidget(property_table_);
    addDockWidget(Qt::RightDockWidgetArea, prop_dock);

    progress_bar_ = new QProgressBar();
    progress_bar_->setMaximumWidth(200);
    progress_bar_->setVisible(false);
    status_label_ = new QLabel("Ready");
    stats_label_ = new QLabel();
    stats_label_->setVisible(AppSettings::instance().showStats());
    statusBar()->addWidget(status_label_, 1);
    statusBar()->addPermanentWidget(stats_label_);
    statusBar()->addPermanentWidget(progress_bar_);
}

void MainWindow::setupMenus() {
    auto* file_menu = menuBar()->addMenu("&File");
    file_menu->addAction("&New Federation",
                         this, &MainWindow::onFederationNew,
                         QKeySequence::New);
    file_menu->addAction("&Open Federation...",
                         this, &MainWindow::onFederationOpen,
                         QKeySequence::Open);
    file_menu->addSeparator();
    file_menu->addAction("&Add Files...",
                         this, &MainWindow::onFileOpen,
                         QKeySequence("Ctrl+Shift+O"));
    file_menu->addAction("Add &Database...", this, &MainWindow::onDatabaseOpen);
    file_menu->addSeparator();
    file_menu->addAction("&Save Federation",
                         this, &MainWindow::onFederationSave,
                         QKeySequence::Save);
    file_menu->addAction("Save Federation &As...",
                         this, &MainWindow::onFederationSaveAs,
                         QKeySequence::SaveAs);
    file_menu->addAction("Federation Se&ttings...",
                         this, &MainWindow::onFederationSettings);
    file_menu->addAction("&Model Transformations...",
                         this, &MainWindow::onModelTransformations);
    file_menu->addSeparator();
    file_menu->addAction("&Settings...", this, &MainWindow::onFileSettings);
    file_menu->addSeparator();
    file_menu->addAction("&Quit", QKeySequence::Quit, qApp, &QApplication::quit);

    auto* view_menu = menuBar()->addMenu("&View");
    // F frames the current selection.  The viewport already binds F in its
    // own keyPressEvent for the case where it has focus; this duplicate at
    // window level is so the shortcut still fires when the tree, property
    // table, or any other child widget has keyboard focus.
    view_menu->addAction("&Frame Selected", this, [this]() {
        viewport_->focusOnSelectedObject();
    }, QKeySequence(Qt::Key_F));
    view_menu->addAction("Print Selected &Coords", this, [this]() {
        viewport_->printSelectedObjectCoords();
    }, QKeySequence("Ctrl+Shift+P"));
    view_menu->addSeparator();
    view_menu->addAction("Set &Home View", this, &MainWindow::onSetHomeView);
    view_menu->addAction("&Go to Home View", this, &MainWindow::onGoHomeView);
}

void MainWindow::onFileOpen() {
    QStringList paths = QFileDialog::getOpenFileNames(
        this, "Add IFC Files", QString(),
        "IFC Files (*.ifc *.ifcxml *.ifczip);;"
        "IFC Viewer Cache (*.ifcview);;"
        "All Files (*)");
    if (!paths.isEmpty()) {
        addFiles(paths);
    }
}

void MainWindow::onDatabaseOpen() {
    QFileDialog dialog(this, "Add IFC Databases");
    dialog.setFileMode(QFileDialog::Directory);
    dialog.setOption(QFileDialog::ShowDirsOnly, true);
    dialog.setOption(QFileDialog::DontResolveSymlinks, true);
    // Native dialogs only support single-directory selection — use Qt's
    // dialog so we can flip the inner views into ExtendedSelection.
    dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (auto* list = dialog.findChild<QListView*>("listView")) {
        list->setSelectionMode(QAbstractItemView::ExtendedSelection);
    }
    if (auto* tree = dialog.findChild<QTreeView*>()) {
        tree->setSelectionMode(QAbstractItemView::ExtendedSelection);
    }
    if (dialog.exec() != QDialog::Accepted) return;
    QStringList paths = dialog.selectedFiles();
    if (!paths.isEmpty()) {
        addFiles(paths);
    }
}

void MainWindow::onFileSettings() {
    if (settings_ == nullptr) {
        settings_ = new SettingsWindow(this);
    }
    settings_->open();
    settings_->activateWindow();
    settings_->raise();
}

void MainWindow::onFederationSettings() {
    if (federation_settings_ == nullptr) {
        federation_settings_ = new FederationSettingsDialog(federation_, this);
    }
    federation_settings_->open();
    federation_settings_->activateWindow();
    federation_settings_->raise();
}

void MainWindow::onModelTransformations() {
    if (model_transformations_ == nullptr) {
        model_transformations_ = new ModelTransformationDialog(federation_, this);
    }
    model_transformations_->open();
    model_transformations_->activateWindow();
    model_transformations_->raise();
}

void MainWindow::addFiles(const QStringList& paths) {
    QStringList accepted_paths;
    QStringList accepted_fed_ids;
    for (const auto& p : paths) {
        QString fed_id = federation_->addModel(p);
        if (fed_id.isEmpty()) continue;  // .ifcfed or empty path — silently skipped
        accepted_paths << p;
        accepted_fed_ids << fed_id;
    }
    loadModelsFromPaths(accepted_paths, accepted_fed_ids);
    updateWindowTitle();
}

void MainWindow::loadModelsFromPaths(const QStringList& paths,
                                      const QStringList& fed_ids) {
    if (paths.isEmpty()) return;
    auto ids = loader_->addFiles(paths);
    for (int i = 0; i < paths.size() && i < static_cast<int>(ids.size()); ++i) {
        uint32_t mid = ids[i];
        const QString& fed_id = fed_ids[i];
        fed_id_to_model_id_[fed_id] = mid;
        model_id_to_fed_id_[mid] = fed_id;

        QString display = QFileInfo(paths[i]).fileName();
        auto* root = new QTreeWidgetItem();
        root->setText(0, display);
        root->setText(1, "IFC Model");
        root->setData(0, Qt::UserRole, static_cast<uint32_t>(0));
        tree_roots_[mid] = root;
        reparentModelTreeRoot(mid);
    }
}

bool MainWindow::openFederation(const QString& path) {
    if (!confirmDiscardIfDirty()) return false;

    QStringList warnings;
    QString err;
    if (!federation_->load(path, &warnings, &err)) {
        QMessageBox::warning(this, "Open Federation",
                              QString("Could not open federation:\n%1").arg(err));
        return false;
    }

    clearScene();

    // Materialise group tree items.  allGroups() walks parents-before-
    // children, so reparenting in the same pass always finds the parent's
    // tree item ready.
    for (const Federation::Group* g : federation_->allGroups()) {
        ensureGroupTreeItem(g->id);
        reparentGroupTreeItem(g->id);
        refreshGroupRowAppearance(g->id);
    }

    QStringList paths;
    QStringList fed_ids;
    QStringList missing;
    for (const auto& m : federation_->models()) {
        if (m.source_kind != "local") continue;  // already warned by load()
        if (!QFileInfo::exists(m.source_path)) {
            missing << m.source_path;
            continue;
        }
        paths << m.source_path;
        fed_ids << m.id;
    }
    loadModelsFromPaths(paths, fed_ids);

    for (const auto& msg : missing) {
        warnings << QString("Source not found, kept in federation: %1").arg(msg);
    }
    if (!warnings.isEmpty()) {
        QMessageBox::warning(this, "Open Federation",
                              "Federation opened with warnings:\n\n" + warnings.join("\n"));
    }

    federation_->markClean();
    updateWindowTitle();

    // Push the federation's loaded FederatedFalseOrigin to the viewport.
    // Per-model ModelTransformations get pushed as each model finishes
    // loading, via applyCoordinateOperationToViewport.
    applyFederatedFalseOriginToViewport();

    if (federation_->hasHomeView()) {
        const auto& hv = federation_->homeView();
        viewport_->setCamera(hv.target.x(), hv.target.y(), hv.target.z(),
                             hv.distance, hv.yaw, hv.pitch);
    }
    return true;
}

void MainWindow::onFederationNew() {
    if (!confirmDiscardIfDirty()) return;
    clearScene();
    federation_->clear();
    updateWindowTitle();
}

void MainWindow::onFederationOpen() {
    QString path = QFileDialog::getOpenFileName(
        this, "Open Federation", QString(),
        "IFC Federation (*.ifcfed);;All Files (*)");
    if (path.isEmpty()) return;
    openFederation(path);
}

bool MainWindow::onFederationSave() {
    if (federation_->filePath().isEmpty()) return onFederationSaveAs();
    QString err;
    if (!federation_->save(federation_->filePath(), &err)) {
        QMessageBox::warning(this, "Save Federation",
                              QString("Could not save federation:\n%1").arg(err));
        return false;
    }
    updateWindowTitle();
    return true;
}

bool MainWindow::onFederationSaveAs() {
    QString suggested = federation_->filePath();
    if (suggested.isEmpty()) suggested = "federation.ifcfed";
    QString path = QFileDialog::getSaveFileName(
        this, "Save Federation As", suggested,
        "IFC Federation (*.ifcfed);;All Files (*)");
    if (path.isEmpty()) return false;
    if (!path.endsWith(".ifcfed", Qt::CaseInsensitive)) path += ".ifcfed";

    QString err;
    if (!federation_->save(path, &err)) {
        QMessageBox::warning(this, "Save Federation",
                              QString("Could not save federation:\n%1").arg(err));
        return false;
    }
    updateWindowTitle();
    return true;
}

void MainWindow::onSetHomeView() {
    auto cs = viewport_->cameraState();
    Federation::HomeView hv;
    hv.target   = cs.target;
    hv.distance = cs.distance;
    hv.yaw      = cs.yaw;
    hv.pitch    = cs.pitch;
    federation_->setHomeView(hv);
    updateWindowTitle();
}

void MainWindow::onGoHomeView() {
    if (!federation_->hasHomeView()) {
        status_label_->setText("No home view set for this federation.");
        return;
    }
    const auto& hv = federation_->homeView();
    viewport_->setCamera(hv.target.x(), hv.target.y(), hv.target.z(),
                         hv.distance, hv.yaw, hv.pitch);
}

void MainWindow::clearScene() {
    while (!tree_roots_.empty()) {
        uint32_t mid = tree_roots_.begin()->first;
        viewport_->removeModel(mid);
        loader_->removeModel(mid);
        removeModelUi(mid);
    }
    fed_id_to_model_id_.clear();
    model_id_to_fed_id_.clear();
    for (auto& kv : group_tree_items_) delete kv.second;
    group_tree_items_.clear();
}

bool MainWindow::confirmDiscardIfDirty() {
    if (!federation_->isDirty()) return true;
    auto ret = QMessageBox::question(
        this, "Unsaved Federation",
        "The current federation has unsaved changes. Save before continuing?",
        QMessageBox::Save | QMessageBox::Discard | QMessageBox::Cancel,
        QMessageBox::Save);
    if (ret == QMessageBox::Cancel) return false;
    if (ret == QMessageBox::Save) return onFederationSave();
    return true;  // Discard
}

void MainWindow::updateWindowTitle() {
    QString fed_path = federation_->filePath();
    if (fed_path.isEmpty() && federation_->models().empty()) {
        setWindowTitle("IfcViewer");
    } else if (fed_path.isEmpty()) {
        setWindowTitle("untitled[*] — IfcViewer");
    } else {
        setWindowTitle(QFileInfo(fed_path).fileName() + "[*] — IfcViewer");
    }
    setWindowModified(federation_->isDirty());
}

void MainWindow::closeEvent(QCloseEvent* event) {
    if (confirmDiscardIfDirty()) event->accept();
    else                          event->ignore();
}

void MainWindow::onLoadStarted(uint32_t /*mid*/, QString display_name) {
    progress_bar_->setValue(0);
    progress_bar_->setVisible(true);
    status_label_->setText("Loading: " + display_name);
}

void MainWindow::onLoadProgressChanged(int percent) {
    progress_bar_->setValue(percent);
}

void MainWindow::appendElementToTree(uint32_t model_id,
                                      uint32_t object_id,
                                      int ifc_id,
                                      int parent_ifc_id,
                                      const std::string& guid,
                                      const std::string& name,
                                      const std::string& type) {
    auto root_it = tree_roots_.find(model_id);
    QTreeWidgetItem* parent_item = (root_it != tree_roots_.end()) ? root_it->second : nullptr;

    auto parent_obj_it = scoped_ifc_id_to_object_id_.find(
        scopedKey(model_id, parent_ifc_id));
    if (parent_obj_it != scoped_ifc_id_to_object_id_.end()) {
        auto tree_it = tree_items_.find(parent_obj_it->second);
        if (tree_it != tree_items_.end()) {
            parent_item = tree_it->second;
        }
    }

    QString display_name = QString::fromStdString(name);
    if (display_name.isEmpty()) {
        display_name = QString::fromStdString(type) + " #" + QString::number(ifc_id);
    }

    auto* item = new QTreeWidgetItem(parent_item);
    item->setText(0, display_name);
    item->setText(1, QString::fromStdString(type));
    item->setText(2, QString::fromStdString(guid));
    item->setData(0, Qt::UserRole, object_id);

    tree_items_[object_id] = item;
}

void MainWindow::onSidecarElementsReady(uint32_t mid,
                                         std::vector<PackedElementInfo> elements,
                                         std::string string_table) {
    auto str = [&](uint32_t offset, uint32_t length) -> std::string {
        if (length == 0 || offset + length > string_table.size()) return {};
        return string_table.substr(offset, length);
    };

    QElapsedTimer t;
    t.start();
    element_tree_->setUpdatesEnabled(false);

    for (const auto& pe : elements) {
        ElementInfo info;
        info.object_id = pe.object_id;
        info.model_id  = pe.model_id;
        info.ifc_id    = pe.ifc_id;
        info.parent_id = pe.parent_id;
        info.guid = str(pe.guid_offset, pe.guid_length);
        info.name = str(pe.name_offset, pe.name_length);
        info.type = str(pe.type_offset, pe.type_length);

        element_map_[info.object_id] = info;
        scoped_ifc_id_to_object_id_[scopedKey(info.model_id, info.ifc_id)] = info.object_id;

        appendElementToTree(info.model_id, info.object_id, info.ifc_id,
                            info.parent_id, info.guid, info.name, info.type);
    }

    element_tree_->setUpdatesEnabled(true);
    qDebug("  Tree build: %lld ms (%zu elements)", t.elapsed(), elements.size());
}

void MainWindow::onDataSourceReady(uint32_t mid) {
    // The IFC file is now available — push the model's CoordinateOperation
    // (or identity) to the viewport.  Sidecar-hit models get here for the
    // first time; stream-loaded models also pass through here when a
    // separate data source opens, but applyCoordinateOperationToViewport
    // is idempotent so double-applying is harmless.
    applyCoordinateOperationToViewport(mid);

    // Re-populate if the current selection belongs to this model, since
    // populateProperties() now has an ifcFile() to query.
    auto items = element_tree_->selectedItems();
    if (items.isEmpty()) return;
    uint32_t object_id = items.first()->data(0, Qt::UserRole).toUInt();
    auto it = element_map_.find(object_id);
    if (it != element_map_.end() && it->second.model_id == mid) {
        populateProperties(object_id);
    }
}

void MainWindow::applyCoordinateOperationToViewport(uint32_t mid) {
    Eigen::Matrix4d M = Eigen::Matrix4d::Identity();
    if (AppSettings::instance().applyCoordinateOperation()) {
        if (const ModelGeoref* gr = loader_->modelGeoref(mid)) {
            if (gr->has_coordinate_operation) {
                M = gr->coordinate_operation_meters;
            }
        }
    }
    viewport_->setModelCoordinateOperation(mid, M);
    // ModelTransformation's compose can depend on the active
    // CoordinateOperation (when ModelTransformation.a_frame == ModelLocal,
    // a is lifted through stage 2), so re-push it whenever stage 2 changes.
    applyModelTransformationToViewport(mid);
}

void MainWindow::applyModelTransformationToViewport(uint32_t mid) {
    Eigen::Matrix4d M = Eigen::Matrix4d::Identity();
    auto fed_it = model_id_to_fed_id_.find(mid);
    if (fed_it != model_id_to_fed_id_.end()) {
        if (const Federation::Model* m = federation_->findById(fed_it->second)) {
            // ModelUnits + the active CoordinateOperation come from the
            // ModelGeoref cache; defaults are safe (1.0, 1.0, identity)
            // when the IFC file isn't yet available.
            ModelUnits      units;
            Eigen::Matrix4d coord_op = Eigen::Matrix4d::Identity();
            if (const ModelGeoref* gr = loader_->modelGeoref(mid)) {
                units = gr->units;
                if (AppSettings::instance().applyCoordinateOperation() &&
                    gr->has_coordinate_operation) {
                    coord_op = gr->coordinate_operation_meters;
                }
            }
            M = composeModelTransformation(
                    m->model_transformation, federation_->config(),
                    units, coord_op);
        }
    }
    viewport_->setModelTransformation(mid, M);
}

void MainWindow::applyFederatedFalseOriginToViewport() {
    const Eigen::Matrix4d M = composeFederatedFalseOrigin(
        federation_->federatedFalseOrigin(), federation_->config());
    viewport_->setFederatedFalseOrigin(M);
}

void MainWindow::maybeGuessFederatedFalseOrigin(uint32_t mid) {
    // Only auto-guess for untitled federations.  A saved .ifcfed carries its
    // authoritative origin (even if that happens to be the default), so we
    // never silently overwrite it when the user re-adds a model.
    if (!federation_->filePath().isEmpty()) return;

    // Skip once the origin is non-default — either the user edited it, a
    // previous batch already guessed, or a load-from-file populated it.
    // For a multi-file batch this means whichever model finishes first
    // anchors the federation; the rest see a non-default origin and skip.
    const FederatedFalseOrigin& cur = federation_->federatedFalseOrigin();
    const FederatedFalseOrigin def;
    if (cur.xyz != def.xyz || cur.rz_deg != def.rz_deg) return;

    const Eigen::Matrix4d* placement = loader_->firstPlacement(mid);
    const ModelGeoref*     gr        = loader_->modelGeoref(mid);
    if (placement == nullptr || gr == nullptr) return;

    const FederatedFalseOrigin guess = guessFederatedFalseOrigin(
        *placement, *gr, federation_->config(),
        AppSettings::instance().applyCoordinateOperation());
    federation_->setFederatedFalseOrigin(guess);
}

void MainWindow::onLoadedFromSidecar(uint32_t mid, qint64 elapsed_ms) {
    progress_bar_->setVisible(false);
    status_label_->setText(QString("%1 elements across %2 model(s) — loaded from cache in %3")
        .arg(element_map_.size())
        .arg(loader_->modelCount())
        .arg(formatElapsed(elapsed_ms)));

    // Sidecar v11+ caches the CoordinateOperation, so SceneLoader has
    // already populated modelGeoref by now — push CoordinateOperation +
    // ModelTransformation immediately rather than waiting for the
    // (possibly never-arriving) data-source load.
    applyCoordinateOperationToViewport(mid);
    applyModelVisibilityToViewport(mid);
    maybeGuessFederatedFalseOrigin(mid);
}

void MainWindow::onStreamedElementsReady(uint32_t /*mid*/, std::vector<ElementInfo> elements) {
    for (const auto& info : elements) {
        element_map_[info.object_id] = info;
        scoped_ifc_id_to_object_id_[scopedKey(info.model_id, info.ifc_id)] = info.object_id;
        appendElementToTree(info.model_id, info.object_id, info.ifc_id,
                            info.parent_id, info.guid, info.name, info.type);
    }
}

void MainWindow::writeSidecarForModel(uint32_t mid) {
    SidecarData sd;
    if (!viewport_->snapshotModel(mid, sd)) return;

    // Cache the model's CoordinateOperation alongside the geometry so a
    // sidecar load doesn't need the IFC source just to apply georef.
    if (const ModelGeoref* gr = loader_->modelGeoref(mid)) {
        sd.has_coordinate_operation = gr->has_coordinate_operation ? 1 : 0;
        Eigen::Map<Eigen::Matrix<double, 4, 4, Eigen::ColMajor>>(
            sd.coordinate_operation_meters) = gr->coordinate_operation_meters;
        sd.project_length_to_meters = gr->units.project_length_to_meters;
        sd.map_unit_to_meters       = gr->units.map_unit_to_meters;
    }

    for (const auto& [oid, info] : element_map_) {
        if (info.model_id != mid) continue;
        PackedElementInfo pe;
        pe.object_id = info.object_id;
        pe.model_id  = info.model_id;
        pe.ifc_id    = info.ifc_id;
        pe.parent_id = info.parent_id;
        pe.guid_offset = static_cast<uint32_t>(sd.string_table.size());
        pe.guid_length = static_cast<uint32_t>(info.guid.size());
        sd.string_table += info.guid;
        pe.name_offset = static_cast<uint32_t>(sd.string_table.size());
        pe.name_length = static_cast<uint32_t>(info.name.size());
        sd.string_table += info.name;
        pe.type_offset = static_cast<uint32_t>(sd.string_table.size());
        pe.type_length = static_cast<uint32_t>(info.type.size());
        sd.string_table += info.type;
        sd.elements.push_back(pe);
    }

    QElapsedTimer t_lod; t_lod.start();
    buildLods(sd);
    LodStats ls = summariseLods(sd);
    qDebug("  LOD build: %lld ms — %u/%u meshes got LOD1 "
           "(%u tris -> %u tris for those meshes)",
           t_lod.elapsed(),
           ls.meshes_with_lod1, ls.meshes_total,
           ls.tris_lod0_for_lod1, ls.tris_lod1);
    viewport_->applyLodExtension(mid, sd);

    QElapsedTimer t; t.start();
    bool ok = writeSidecar(loader_->filePath(mid).toStdString(), sd);
    qDebug("  Sidecar write: %lld ms (%s)", t.elapsed(), ok ? "ok" : "FAILED");
}

void MainWindow::removeModelUi(uint32_t mid) {
    auto fed_it = model_id_to_fed_id_.find(mid);
    if (fed_it != model_id_to_fed_id_.end()) {
        fed_id_to_model_id_.erase(fed_it->second);
        model_id_to_fed_id_.erase(fed_it);
    }

    auto root_it = tree_roots_.find(mid);
    if (root_it != tree_roots_.end()) {
        delete root_it->second;
        tree_roots_.erase(root_it);
    }

    for (auto it = tree_items_.begin(); it != tree_items_.end();) {
        auto info_it = element_map_.find(it->first);
        if (info_it != element_map_.end() && info_it->second.model_id == mid) {
            it = tree_items_.erase(it);
        } else {
            ++it;
        }
    }

    for (auto it = element_map_.begin(); it != element_map_.end();) {
        if (it->second.model_id == mid) {
            it = element_map_.erase(it);
        } else {
            ++it;
        }
    }

    for (auto it = scoped_ifc_id_to_object_id_.begin(); it != scoped_ifc_id_to_object_id_.end();) {
        if (static_cast<uint32_t>(it->first >> 32) == mid) {
            it = scoped_ifc_id_to_object_id_.erase(it);
        } else {
            ++it;
        }
    }

    viewport_->setSelectedObjectId(0);
    property_table_->setRowCount(0);
}

void MainWindow::onLoadedFromStream(uint32_t mid, qint64 elapsed_ms) {
    progress_bar_->setVisible(false);
    status_label_->setText(QString("%1 elements across %2 model(s) — last loaded in %3")
        .arg(element_map_.size())
        .arg(loader_->modelCount())
        .arg(formatElapsed(elapsed_ms)));

    applyCoordinateOperationToViewport(mid);
    applyModelVisibilityToViewport(mid);
    maybeGuessFederatedFalseOrigin(mid);

    writeSidecarForModel(mid);
}

void MainWindow::onLoadCancelled(uint32_t mid) {
    progress_bar_->setVisible(false);
    removeModelUi(mid);
    status_label_->setText(QString("%1 load cancelled").arg(loader_->displayName(mid)));
}

void MainWindow::onLoadError(uint32_t mid, QString message) {
    progress_bar_->setVisible(false);
    removeModelUi(mid);
    status_label_->setText("Error: " + message);
    QMessageBox::warning(this, "Error", message);
}

void MainWindow::onAllLoadsFinished() {
    applyPendingBenchmark();
}

void MainWindow::onObjectPicked(uint32_t object_id) {
    viewport_->setSelectedObjectId(object_id);

    auto it = tree_items_.find(object_id);
    if (it != tree_items_.end()) {
        element_tree_->blockSignals(true);
        element_tree_->setCurrentItem(it->second);
        element_tree_->blockSignals(false);
    }

    populateProperties(object_id);
}

void MainWindow::onTreeSelectionChanged() {
    auto items = element_tree_->selectedItems();
    if (items.isEmpty()) return;

    uint32_t object_id = items.first()->data(0, Qt::UserRole).toUInt();
    viewport_->setSelectedObjectId(object_id);
    populateProperties(object_id);
}

void MainWindow::populateProperties(uint32_t object_id) {
    property_table_->setRowCount(0);
    if (object_id == 0) return;

    auto it = element_map_.find(object_id);
    if (it == element_map_.end()) return;

    const auto& info = it->second;

    auto addRow = [this](const QString& key, const QString& value) {
        int row = property_table_->rowCount();
        property_table_->insertRow(row);
        property_table_->setItem(row, 0, new QTableWidgetItem(key));
        property_table_->setItem(row, 1, new QTableWidgetItem(value));
    };

    addRow("IFC ID", QString::number(info.ifc_id));
    addRow("GUID", QString::fromStdString(info.guid));
    addRow("Name", QString::fromStdString(info.name));
    addRow("Type", QString::fromStdString(info.type));

    auto* file = loader_->ifcFile(info.model_id);
    if (!file) return;

    auto product = file->instance_by_id(info.ifc_id);
    if (!product) return;

    auto& decl = product.declaration();
    if (auto* entity = decl.as_entity()) {
        for (size_t i = 0; i < entity->attribute_count(); ++i) {
            auto* attr = entity->attribute_by_index(i);
            try {
                auto val = product.get_attribute_value(i);
                if (!val.isNull()) {
                    std::string str_val;
                    try {
                        str_val = static_cast<std::string>(val);
                    } catch (...) {
                        str_val = "<" + std::string(ifcopenshell::argument_type_to_string(val.type())) + ">";
                    }
                    addRow(QString::fromStdString(attr->name()), QString::fromStdString(str_val));
                }
            } catch (...) {}
        }
    }
}

void MainWindow::setPendingCamera(const QString& params) {
    pending_camera_ = params;
}

void MainWindow::setPendingBenchmark(int frames) {
    pending_benchmark_ = frames;
}

void MainWindow::applyPendingBenchmark() {
    if (pending_camera_.isEmpty() && pending_benchmark_ <= 0) return;

    if (!pending_camera_.isEmpty()) {
        QStringList parts = pending_camera_.split(',');
        if (parts.size() == 6) {
            viewport_->setCamera(
                parts[0].toFloat(), parts[1].toFloat(), parts[2].toFloat(),
                parts[3].toFloat(), parts[4].toFloat(), parts[5].toFloat());
            qDebug("Camera set: %s", qPrintable(pending_camera_));
        } else {
            qWarning("--camera expects 6 comma-separated values: tx,ty,tz,dist,yaw,pitch");
        }
        pending_camera_.clear();
    }

    if (pending_benchmark_ > 0) {
        qDebug("Starting benchmark: %d frames", pending_benchmark_);
        viewport_->setBenchmarkFrames(pending_benchmark_);
        pending_benchmark_ = 0;
    }
}

QString MainWindow::formatElapsed(qint64 ms) const {
    return (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
}

uint32_t MainWindow::modelIdForRoot(QTreeWidgetItem* item) const {
    if (!item) return 0;
    for (const auto& kv : tree_roots_) {
        if (kv.second == item) return kv.first;
    }
    return 0;
}

void MainWindow::applyModelVisibilityToViewport(uint32_t mid) {
    auto fed_it = model_id_to_fed_id_.find(mid);
    if (fed_it == model_id_to_fed_id_.end()) return;
    const QString& fed_id = fed_it->second;
    const bool effective = federation_->isModelEffectivelyVisible(fed_id);
    if (effective) viewport_->showModel(mid);
    else           viewport_->hideModel(mid);

    // Tree-side cue: italicise + grey out the model root when not
    // effectively visible (own toggle off, or any ancestor group hidden).
    auto root_it = tree_roots_.find(mid);
    if (root_it != tree_roots_.end()) {
        QFont f = root_it->second->font(0);
        f.setItalic(!effective);
        for (int col = 0; col < element_tree_->columnCount(); ++col) {
            root_it->second->setFont(col, f);
            root_it->second->setForeground(
                col,
                effective ? element_tree_->palette().color(QPalette::Text)
                          : element_tree_->palette().color(QPalette::Disabled,
                                                           QPalette::Text));
        }
    }
}

void MainWindow::onTreeContextMenu(const QPoint& pos) {
    QTreeWidgetItem* item = element_tree_->itemAt(pos);
    const uint32_t mid = modelIdForRoot(item);
    const QString  group_id = groupIdForItem(item);
    // Element rows (children of a model root) are excluded — only model
    // roots, group rows, and the empty area get a menu.
    const bool is_element_row =
        item != nullptr && mid == 0 && group_id.isEmpty();
    if (is_element_row) return;

    QMenu menu(this);

    if (mid != 0) {
        // === Model row ===
        auto fed_it = model_id_to_fed_id_.find(mid);
        if (fed_it == model_id_to_fed_id_.end()) return;
        const Federation::Model* m = federation_->findById(fed_it->second);
        if (!m) return;

        const bool currently_loading = loader_->isLoadingModel(mid);

        QAction* hide_show = menu.addAction(m->visible ? "Hide" : "Show");

        QMenu* move_menu = menu.addMenu("Move to Group");
        QAction* move_to_root = move_menu->addAction("(Root)");
        move_to_root->setEnabled(!m->group_id.isEmpty());
        move_menu->addSeparator();
        std::vector<std::pair<QAction*, QString>> move_targets;
        for (const Federation::Group* g : federation_->allGroups()) {
            QAction* a = move_menu->addAction(g->display_name);
            a->setEnabled(g->id != m->group_id);
            move_targets.emplace_back(a, g->id);
        }
        if (federation_->allGroups().empty()) {
            QAction* none = move_menu->addAction("(no groups)");
            none->setEnabled(false);
        }

        QAction* remove = menu.addAction("Remove");
        remove->setEnabled(!currently_loading);

        QAction* chosen = menu.exec(element_tree_->viewport()->mapToGlobal(pos));
        if (!chosen) return;
        if (chosen == hide_show) {
            federation_->setModelVisible(fed_it->second, !m->visible);
        } else if (chosen == move_to_root) {
            federation_->setModelGroup(fed_it->second, QString());
        } else if (chosen == remove) {
            removeModel(mid);
        } else {
            for (const auto& [a, gid] : move_targets) {
                if (chosen == a) {
                    federation_->setModelGroup(fed_it->second, gid);
                    break;
                }
            }
        }
        return;
    }

    if (!group_id.isEmpty()) {
        // === Group row ===
        const Federation::Group* g = federation_->findGroupById(group_id);
        if (!g) return;

        QAction* hide_show = menu.addAction(g->visible ? "Hide" : "Show");
        QAction* rename    = menu.addAction("Rename...");
        QAction* new_sub   = menu.addAction("New Subgroup");

        QMenu* move_menu = menu.addMenu("Move to Parent");
        QAction* move_to_root = move_menu->addAction("(Root)");
        move_to_root->setEnabled(g->parent != nullptr);
        move_menu->addSeparator();
        std::vector<std::pair<QAction*, QString>> move_targets;
        for (const Federation::Group* og : federation_->allGroups()) {
            QAction* a = move_menu->addAction(og->display_name);
            // Disable self, current parent, and any descendant of g (the
            // latter would create a cycle).  Walk og's ancestor chain to
            // detect descendants.
            bool would_cycle = false;
            for (const Federation::Group* cur = og; cur; cur = cur->parent) {
                if (cur == g) { would_cycle = true; break; }
            }
            const bool is_current_parent =
                g->parent != nullptr && og == g->parent;
            a->setEnabled(!would_cycle && !is_current_parent);
            move_targets.emplace_back(a, og->id);
        }

        QAction* remove = menu.addAction("Remove Group");

        QAction* chosen = menu.exec(element_tree_->viewport()->mapToGlobal(pos));
        if (!chosen) return;
        if (chosen == hide_show) {
            federation_->setGroupVisible(group_id, !g->visible);
        } else if (chosen == rename) {
            bool ok = false;
            QString name = QInputDialog::getText(
                this, "Rename Group", "Group name:", QLineEdit::Normal,
                g->display_name, &ok);
            if (ok && !name.isEmpty()) federation_->setGroupName(group_id, name);
        } else if (chosen == new_sub) {
            bool ok = false;
            QString name = QInputDialog::getText(
                this, "New Subgroup", "Group name:", QLineEdit::Normal,
                "Group", &ok);
            if (ok && !name.isEmpty()) federation_->addGroup(name, group_id);
        } else if (chosen == move_to_root) {
            federation_->setGroupParent(group_id, QString());
        } else if (chosen == remove) {
            federation_->removeGroup(group_id);
        } else {
            for (const auto& [a, gid] : move_targets) {
                if (chosen == a) {
                    federation_->setGroupParent(group_id, gid);
                    break;
                }
            }
        }
        return;
    }

    // === Empty area ===
    QAction* new_group = menu.addAction("New Group");
    QAction* chosen = menu.exec(element_tree_->viewport()->mapToGlobal(pos));
    if (!chosen) return;
    if (chosen == new_group) {
        bool ok = false;
        QString name = QInputDialog::getText(
            this, "New Group", "Group name:", QLineEdit::Normal,
            "Group", &ok);
        if (ok && !name.isEmpty()) federation_->addGroup(name, QString());
    }
}

void MainWindow::removeModel(uint32_t mid) {
    if (loader_->isLoadingModel(mid)) return;

    QString fed_id;
    auto fed_it = model_id_to_fed_id_.find(mid);
    if (fed_it != model_id_to_fed_id_.end()) fed_id = fed_it->second;

    viewport_->removeModel(mid);
    loader_->removeModel(mid);
    removeModelUi(mid);
    if (!fed_id.isEmpty()) federation_->removeModel(fed_id);
    updateWindowTitle();
}

QString MainWindow::groupIdForItem(QTreeWidgetItem* item) const {
    if (!item) return {};
    for (const auto& kv : group_tree_items_) {
        if (kv.second == item) return kv.first;
    }
    return {};
}

QTreeWidgetItem* MainWindow::ensureGroupTreeItem(const QString& group_id) {
    if (group_id.isEmpty()) return nullptr;
    auto it = group_tree_items_.find(group_id);
    if (it != group_tree_items_.end()) return it->second;
    const Federation::Group* g = federation_->findGroupById(group_id);
    if (!g) return nullptr;

    auto* item = new QTreeWidgetItem();
    item->setText(0, g->display_name);
    item->setText(1, "Group");
    group_tree_items_[group_id] = item;
    return item;
}

void MainWindow::reparentGroupTreeItem(const QString& group_id) {
    auto it = group_tree_items_.find(group_id);
    if (it == group_tree_items_.end()) return;
    QTreeWidgetItem* item = it->second;
    const Federation::Group* g = federation_->findGroupById(group_id);
    if (!g) return;

    QTreeWidgetItem* desired_parent = nullptr;
    if (g->parent != nullptr) {
        auto pit = group_tree_items_.find(g->parent->id);
        if (pit != group_tree_items_.end()) desired_parent = pit->second;
    }

    QTreeWidgetItem* current_parent = item->parent();
    if (current_parent == desired_parent &&
        (current_parent != nullptr ||
         element_tree_->indexOfTopLevelItem(item) >= 0)) {
        return;
    }

    // Detach from current location.
    if (current_parent) {
        current_parent->removeChild(item);
    } else {
        int idx = element_tree_->indexOfTopLevelItem(item);
        if (idx >= 0) element_tree_->takeTopLevelItem(idx);
    }
    // Attach to desired location.
    if (desired_parent) desired_parent->addChild(item);
    else                element_tree_->addTopLevelItem(item);
}

void MainWindow::reparentModelTreeRoot(uint32_t mid) {
    auto root_it = tree_roots_.find(mid);
    if (root_it == tree_roots_.end()) return;
    QTreeWidgetItem* item = root_it->second;

    auto fed_it = model_id_to_fed_id_.find(mid);
    QString group_id;
    if (fed_it != model_id_to_fed_id_.end()) {
        if (const Federation::Model* m = federation_->findById(fed_it->second)) {
            group_id = m->group_id;
        }
    }

    QTreeWidgetItem* desired_parent = nullptr;
    if (!group_id.isEmpty()) {
        auto pit = group_tree_items_.find(group_id);
        if (pit != group_tree_items_.end()) desired_parent = pit->second;
    }

    QTreeWidgetItem* current_parent = item->parent();
    if (current_parent == desired_parent &&
        (current_parent != nullptr ||
         element_tree_->indexOfTopLevelItem(item) >= 0)) {
        return;
    }

    if (current_parent) {
        current_parent->removeChild(item);
    } else {
        int idx = element_tree_->indexOfTopLevelItem(item);
        if (idx >= 0) element_tree_->takeTopLevelItem(idx);
    }
    if (desired_parent) desired_parent->addChild(item);
    else                element_tree_->addTopLevelItem(item);
}

void MainWindow::refreshGroupRowAppearance(const QString& group_id) {
    auto it = group_tree_items_.find(group_id);
    if (it == group_tree_items_.end()) return;
    QTreeWidgetItem* item = it->second;
    const bool effective = federation_->isGroupChainVisible(group_id);

    QFont f = item->font(0);
    f.setItalic(!effective);
    f.setBold(true);
    for (int col = 0; col < element_tree_->columnCount(); ++col) {
        item->setFont(col, f);
        item->setForeground(
            col,
            effective ? element_tree_->palette().color(QPalette::Text)
                      : element_tree_->palette().color(QPalette::Disabled,
                                                       QPalette::Text));
    }
}

std::vector<QString> MainWindow::descendantGroupIds(const QString& group_id) const {
    std::vector<QString> out;
    auto walk = [&](auto&& self,
                    const std::vector<std::unique_ptr<Federation::Group>>& src) -> void {
        for (const auto& g : src) {
            out.push_back(g->id);
            self(self, g->children);
        }
    };
    if (group_id.isEmpty()) {
        walk(walk, federation_->rootGroups());
    } else {
        const Federation::Group* g = federation_->findGroupById(group_id);
        if (!g) return out;
        out.push_back(g->id);
        walk(walk, g->children);
    }
    return out;
}

void MainWindow::applyVisibilityCascadeFromGroup(const QString& group_id) {
    const std::vector<QString> gids = descendantGroupIds(group_id);
    // Models directly assigned to one of these groups need their viewport
    // visibility re-pushed because chain visibility may have flipped.
    for (const auto& m : federation_->models()) {
        const bool affected =
            (group_id.isEmpty()) ||
            std::find(gids.begin(), gids.end(), m.group_id) != gids.end();
        if (!affected) continue;
        auto it = fed_id_to_model_id_.find(m.id);
        if (it != fed_id_to_model_id_.end()) {
            applyModelVisibilityToViewport(it->second);
        }
    }
}
