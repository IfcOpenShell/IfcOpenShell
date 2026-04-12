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

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    setupUi();
    setupMenus();

    connect(viewport_, &ViewportWindow::frameStatsUpdated, this, [this](const ViewportWindow::FrameStats& s) {
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

    connect(&element_poll_timer_, &QTimer::timeout, this, &MainWindow::pollNewElements);
    element_poll_timer_.setInterval(100);

    setWindowTitle("IfcViewer");
    resize(1400, 900);
}

MainWindow::~MainWindow() {
    joinSidecarThread();
}

void MainWindow::joinSidecarThread() {
    if (sidecar_read_thread_.joinable())
        sidecar_read_thread_.join();
}

void MainWindow::setupUi() {
    // 3D Viewport as central widget
    viewport_ = new ViewportWindow();
    viewport_container_ = QWidget::createWindowContainer(viewport_, this);
    viewport_container_->setMinimumSize(400, 300);
    viewport_container_->setFocusPolicy(Qt::StrongFocus);
    setCentralWidget(viewport_container_);

    connect(viewport_, &ViewportWindow::objectPicked, this, &MainWindow::onObjectPicked);

    // Element tree dock
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

    // Properties dock
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

    // Status bar with progress
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
    for (const auto& path : paths) {
        ModelId id = next_model_id_++;

        ModelHandle handle;
        handle.id = id;
        handle.file_path = path;
        handle.display_name = QFileInfo(path).fileName();
        handle.streamer = new GeometryStreamer(this);

        // Create top-level tree item for this model
        auto* root = new QTreeWidgetItem(element_tree_);
        root->setText(0, handle.display_name);
        root->setText(1, "IFC Model");
        root->setData(0, Qt::UserRole, static_cast<uint32_t>(0)); // 0 = not a pickable object
        handle.tree_root = root;

        models_[id] = handle;
        load_queue_.push_back(id);
    }

    if (loading_model_id_ == 0) {
        QTimer::singleShot(0, this, &MainWindow::startNextLoad);
    }
}

void MainWindow::connectStreamer(GeometryStreamer* streamer) {
    connect(streamer, &GeometryStreamer::progressChanged,
            this, &MainWindow::onProgressChanged, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::meshReady,
            this, &MainWindow::onMeshReady, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::instanceReady,
            this, &MainWindow::onInstanceReady, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::finished,
            this, &MainWindow::onStreamingFinished, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::errorOccurred, this, [this](const QString& msg) {
        QMessageBox::warning(this, "Error", msg);
    }, Qt::QueuedConnection);
}

void MainWindow::startNextLoad() {
    if (load_queue_.empty()) {
        loading_model_id_ = 0;
        return;
    }

    loading_model_id_ = load_queue_.front();
    load_queue_.pop_front();

    auto& model = models_[loading_model_id_];

    load_timer_.restart();
    status_label_->setText("Loading: " + model.display_name);

    // Try sidecar on a background thread so the UI stays responsive.
    std::string ifc_path = model.file_path.toStdString();
    uint64_t file_size = static_cast<uint64_t>(QFileInfo(model.file_path).size());
    ModelId mid = loading_model_id_;

    joinSidecarThread();
    sidecar_read_thread_ = std::thread([this, ifc_path, file_size, mid]() {
        QElapsedTimer rt; rt.start();
        auto cached = readSidecar(ifc_path, file_size);
        qDebug("  Sidecar read: %lld ms (%s)", rt.elapsed(), ifc_path.c_str());
        auto result = std::make_shared<std::optional<SidecarData>>(std::move(cached));
        QMetaObject::invokeMethod(this, [this, mid, result]() {
            if (*result && !(*result)->instances.empty()) {
                applySidecarData(mid, std::move(**result));
            } else {
                // No sidecar — fall back to streaming from IFC.
                auto it = models_.find(mid);
                if (it == models_.end()) return;
                auto& m = it->second;
                connectStreamer(m.streamer);
                progress_bar_->setValue(0);
                progress_bar_->setVisible(true);
                status_label_->setText("Loading: " + m.display_name);
                element_poll_timer_.start();
                m.streamer->loadFile(
                    m.file_path.toStdString(), next_object_id_, loading_model_id_);
            }
        }, Qt::QueuedConnection);
    });
}

void MainWindow::applySidecarData(ModelId mid, SidecarData data) {
    auto it = models_.find(mid);
    if (it == models_.end()) return;
    auto& model = it->second;

    qDebug("Sidecar hit: %s (%zu verts, %zu indices, %zu meshes, %zu instances, %zu elements)",
           model.file_path.toStdString().c_str(),
           data.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS,
           data.indices.size(),
           data.meshes.size(),
           data.instances.size(),
           data.elements.size());

    QElapsedTimer t;
    t.start();

    // Update next_object_id_ past all objects in this model before the
    // extracted `elements` is moved out of `data`.
    for (const auto& elem : data.elements) {
        if (elem.object_id >= next_object_id_)
            next_object_id_ = elem.object_id + 1;
    }

    // Hand off geometry to GPU in a single call.
    std::vector<PackedElementInfo> elements = std::move(data.elements);
    std::string stbl                        = std::move(data.string_table);
    viewport_->applyCachedModel(mid, std::move(data));
    qDebug("  GL upload: %lld ms", t.elapsed());

    t.restart();
    element_tree_->setUpdatesEnabled(false);
    populateTreeFromSidecar(model, elements, stbl);
    element_tree_->setUpdatesEnabled(true);
    qDebug("  Tree build: %lld ms (%zu elements)", t.elapsed(), elements.size());

    progress_bar_->setVisible(false);

    qint64 ms = load_timer_.elapsed();
    QString elapsed = (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
    status_label_->setText(QString("%1 elements across %2 model(s) — loaded from cache in %3")
        .arg(element_map_.size())
        .arg(models_.size())
        .arg(elapsed));

    loading_model_id_ = 0;
    QTimer::singleShot(0, this, &MainWindow::startNextLoad);
}

void MainWindow::populateTreeFromSidecar(ModelHandle& model,
                                          const std::vector<PackedElementInfo>& elements,
                                          const std::string& stbl) {
    auto str = [&](uint32_t offset, uint32_t length) -> std::string {
        if (length == 0 || offset + length > stbl.size()) return {};
        return stbl.substr(offset, length);
    };

    for (const auto& pe : elements) {
        ElementInfo info;
        info.object_id = pe.object_id;
        info.model_id = pe.model_id;
        info.ifc_id = pe.ifc_id;
        info.parent_id = pe.parent_id;
        info.guid = str(pe.guid_offset, pe.guid_length);
        info.name = str(pe.name_offset, pe.name_length);
        info.type = str(pe.type_offset, pe.type_length);

        element_map_[info.object_id] = info;
        scoped_ifc_id_to_object_id_[scopedKey(info.model_id, info.ifc_id)] = info.object_id;

        // Find parent tree item.
        QTreeWidgetItem* parent_item = model.tree_root;
        auto parent_obj_it = scoped_ifc_id_to_object_id_.find(
            scopedKey(info.model_id, info.parent_id));
        if (parent_obj_it != scoped_ifc_id_to_object_id_.end()) {
            auto tree_it = tree_items_.find(parent_obj_it->second);
            if (tree_it != tree_items_.end()) {
                parent_item = tree_it->second;
            }
        }

        QString display_name = QString::fromStdString(info.name);
        if (display_name.isEmpty()) {
            display_name = QString::fromStdString(info.type) + " #" + QString::number(info.ifc_id);
        }

        auto* item = new QTreeWidgetItem(parent_item);
        item->setText(0, display_name);
        item->setText(1, QString::fromStdString(info.type));
        item->setText(2, QString::fromStdString(info.guid));
        item->setData(0, Qt::UserRole, info.object_id);

        tree_items_[info.object_id] = item;
    }
}

void MainWindow::onProgressChanged(int percent) {
    progress_bar_->setValue(percent);
}

void MainWindow::onMeshReady(MeshChunk chunk) {
    viewport_->uploadMeshChunk(chunk);
}

void MainWindow::onInstanceReady(InstanceChunk chunk) {
    viewport_->uploadInstanceChunk(chunk);
}

void MainWindow::onStreamingFinished() {
    element_poll_timer_.stop();
    pollNewElements(); // drain remaining

    // Update next_object_id_ from the streamer that just finished.
    if (loading_model_id_ != 0) {
        auto it = models_.find(loading_model_id_);
        if (it != models_.end()) {
            next_object_id_ = it->second.streamer->lastObjectId();
        }
    }

    progress_bar_->setVisible(false);

    qint64 ms = load_timer_.elapsed();
    QString elapsed = (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";

    size_t total_elements = element_map_.size();
    size_t num_models = models_.size();
    status_label_->setText(QString("%1 elements across %2 model(s) — last loaded in %3")
        .arg(total_elements)
        .arg(num_models)
        .arg(elapsed));

    // Sort instances by mesh, upload the per-model instance SSBO, and
    // persist a v4 sidecar for next load.
    if (loading_model_id_ != 0) {
        viewport_->finalizeModel(loading_model_id_);

        auto it = models_.find(loading_model_id_);
        if (it != models_.end()) {
            SidecarData sd;
            if (viewport_->snapshotModel(loading_model_id_, sd)) {
                // Pack this model's element metadata + string table.
                for (const auto& [oid, info] : element_map_) {
                    if (info.model_id != loading_model_id_) continue;
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

                std::string ifc_path = it->second.file_path.toStdString();
                uint64_t file_size = static_cast<uint64_t>(
                    QFileInfo(it->second.file_path).size());
                QElapsedTimer t; t.start();
                bool ok = writeSidecar(ifc_path, sd, file_size);
                qDebug("  Sidecar write: %lld ms (%s)",
                       t.elapsed(), ok ? "ok" : "FAILED");
            }
        }
    }

    // Start next model if queued.
    startNextLoad();
}

void MainWindow::onObjectPicked(uint32_t object_id) {
    viewport_->setSelectedObjectId(object_id);

    // Select in tree
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

void MainWindow::pollNewElements() {
    if (loading_model_id_ == 0) return;

    auto it = models_.find(loading_model_id_);
    if (it == models_.end()) return;

    auto& model = it->second;
    auto elements = model.streamer->drainElements();

    for (auto& info : elements) {
        element_map_[info.object_id] = info;
        scoped_ifc_id_to_object_id_[scopedKey(info.model_id, info.ifc_id)] = info.object_id;

        // Find parent tree item (scoped to this model)
        QTreeWidgetItem* parent_item = model.tree_root;
        auto parent_obj_it = scoped_ifc_id_to_object_id_.find(
            scopedKey(info.model_id, info.parent_id));
        if (parent_obj_it != scoped_ifc_id_to_object_id_.end()) {
            auto tree_it = tree_items_.find(parent_obj_it->second);
            if (tree_it != tree_items_.end()) {
                parent_item = tree_it->second;
            }
        }

        QString display_name = QString::fromStdString(info.name);
        if (display_name.isEmpty()) {
            display_name = QString::fromStdString(info.type) + " #" + QString::number(info.ifc_id);
        }

        auto* item = new QTreeWidgetItem(parent_item);
        item->setText(0, display_name);
        item->setText(1, QString::fromStdString(info.type));
        item->setText(2, QString::fromStdString(info.guid));
        item->setData(0, Qt::UserRole, info.object_id);

        tree_items_[info.object_id] = item;
    }
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

    // Find the correct model's file for property lookup
    auto model_it = models_.find(info.model_id);
    if (model_it == models_.end()) return;

    auto* file = model_it->second.streamer->ifcFile();
    if (!file) return;

    auto product = file->instance_by_id(info.ifc_id);
    if (!product) return;

    // Show all direct attributes
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
