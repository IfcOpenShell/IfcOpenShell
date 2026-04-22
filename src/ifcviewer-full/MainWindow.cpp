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
#include "SettingsWindow.h"
#include "LodBuilder.h"
#include "SidecarCache.h"

#include <QApplication>
#include <QMenuBar>
#include <QFileDialog>
#include <QFileInfo>
#include <QMessageBox>
#include <QStatusBar>
#include <QHeaderView>
#include <QVBoxLayout>
#include <QDockWidget>
#include <QDebug>

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    setupUi();
    setupMenus();

    loader_ = new SceneLoader(viewport_, this);
    connect(loader_, &SceneLoader::loadStarted,
            this, &MainWindow::onLoadStarted);
    connect(loader_, &SceneLoader::progressChanged,
            this, &MainWindow::onLoadProgressChanged);
    connect(loader_, &SceneLoader::sidecarElementsReady,
            this, &MainWindow::onSidecarElementsReady);
    connect(loader_, &SceneLoader::loadedFromSidecar,
            this, &MainWindow::onLoadedFromSidecar);
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

    setWindowTitle("IfcViewer");
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
    connect(element_tree_, &QTreeWidget::itemSelectionChanged, this, &MainWindow::onTreeSelectionChanged);
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
    auto* open_action = file_menu->addAction("&Add Files...", this, &MainWindow::onFileOpen);
    open_action->setShortcut(QKeySequence::Open);
    file_menu->addAction("&Settings...", this, &MainWindow::onFileSettings);
    file_menu->addSeparator();
    file_menu->addAction("&Quit", QKeySequence::Quit, qApp, &QApplication::quit);
}

void MainWindow::onFileOpen() {
    QStringList paths = QFileDialog::getOpenFileNames(
        this, "Add IFC Files", QString(),
        "IFC Files (*.ifc *.ifcxml *.ifczip);;All Files (*)");
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

void MainWindow::addFiles(const QStringList& paths) {
    auto ids = loader_->addFiles(paths);
    for (int i = 0; i < paths.size() && i < static_cast<int>(ids.size()); ++i) {
        uint32_t id = ids[i];
        QString display = QFileInfo(paths[i]).fileName();
        auto* root = new QTreeWidgetItem(element_tree_);
        root->setText(0, display);
        root->setText(1, "IFC Model");
        root->setData(0, Qt::UserRole, static_cast<uint32_t>(0));
        tree_roots_[id] = root;
    }
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

void MainWindow::onLoadedFromSidecar(uint32_t /*mid*/, qint64 elapsed_ms) {
    progress_bar_->setVisible(false);
    status_label_->setText(QString("%1 elements across %2 model(s) — loaded from cache in %3")
        .arg(element_map_.size())
        .arg(loader_->modelCount())
        .arg(formatElapsed(elapsed_ms)));
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
    bool ok = writeSidecar(loader_->filePath(mid).toStdString(), sd, loader_->fileSize(mid));
    qDebug("  Sidecar write: %lld ms (%s)", t.elapsed(), ok ? "ok" : "FAILED");
}

void MainWindow::removeModelUi(uint32_t mid) {
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
