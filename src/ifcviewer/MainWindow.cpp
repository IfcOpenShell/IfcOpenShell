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
#include "SettingsWindow.h"

#include <QApplication>
#include <QMenuBar>
#include <QFileDialog>
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

    streamer_ = new GeometryStreamer(this);
    connect(streamer_, &GeometryStreamer::progressChanged, this, &MainWindow::onProgressChanged, Qt::QueuedConnection);
    connect(streamer_, &GeometryStreamer::elementReady, this, &MainWindow::onElementReady, Qt::QueuedConnection);
    connect(streamer_, &GeometryStreamer::finished, this, &MainWindow::onStreamingFinished, Qt::QueuedConnection);
    connect(streamer_, &GeometryStreamer::errorOccurred, this, [this](const QString& msg) {
        QMessageBox::warning(this, "Error", msg);
    }, Qt::QueuedConnection);

    connect(&element_poll_timer_, &QTimer::timeout, this, &MainWindow::pollNewElements);
    element_poll_timer_.setInterval(100);

    setWindowTitle("IfcViewer");
    resize(1400, 900);
}

MainWindow::~MainWindow() {}

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
    statusBar()->addWidget(status_label_, 1);
    statusBar()->addPermanentWidget(progress_bar_);
}

void MainWindow::setupMenus() {
    auto* file_menu = menuBar()->addMenu("&File");
    auto* open_action = file_menu->addAction("&Open...", this, &MainWindow::onFileOpen);
    open_action->setShortcut(QKeySequence::Open);
    file_menu->addAction("&Settings...", this, &MainWindow::onFileSettings);
    file_menu->addSeparator();
    file_menu->addAction("&Quit", QKeySequence::Quit, qApp, &QApplication::quit);
}

void MainWindow::onFileOpen() {
    QString path = QFileDialog::getOpenFileName(this, "Open IFC File", QString(), "IFC Files (*.ifc *.ifcxml *.ifczip);;All Files (*)");
    if (!path.isEmpty()) {
        openFile(path);
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

void MainWindow::openFile(const QString& path) {
    viewport_->resetScene();
    element_tree_->clear();
    property_table_->setRowCount(0);
    element_map_.clear();
    tree_items_.clear();
    ifc_id_to_object_id_.clear();

    progress_bar_->setValue(0);
    progress_bar_->setVisible(true);
    status_label_->setText("Loading: " + path);

    load_timer_.restart();
    element_poll_timer_.start();
    streamer_->loadFile(path.toStdString());
}

void MainWindow::onProgressChanged(int percent) {
    progress_bar_->setValue(percent);
}

void MainWindow::onElementReady(UploadChunk chunk) {
    viewport_->uploadChunk(chunk);
}

void MainWindow::onStreamingFinished() {
    element_poll_timer_.stop();
    pollNewElements(); // drain remaining

    progress_bar_->setVisible(false);

    qint64 ms = load_timer_.elapsed();
    QString elapsed = (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
    status_label_->setText(QString("Loaded %1 elements in %2")
        .arg(element_map_.size())
        .arg(elapsed));
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
    auto elements = streamer_->drainElements();
    for (auto& info : elements) {
        element_map_[info.object_id] = info;
        ifc_id_to_object_id_[info.ifc_id] = info.object_id;

        // Find parent tree item
        QTreeWidgetItem* parent_item = nullptr;
        auto parent_obj_it = ifc_id_to_object_id_.find(info.parent_id);
        if (parent_obj_it != ifc_id_to_object_id_.end()) {
            auto tree_it = tree_items_.find(parent_obj_it->second);
            if (tree_it != tree_items_.end()) {
                parent_item = tree_it->second;
            }
        }

        QString display_name = QString::fromStdString(info.name);
        if (display_name.isEmpty()) {
            display_name = QString::fromStdString(info.type) + " #" + QString::number(info.ifc_id);
        }

        QTreeWidgetItem* item;
        if (parent_item) {
            item = new QTreeWidgetItem(parent_item);
        } else {
            item = new QTreeWidgetItem(element_tree_);
        }
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

    // If the file is loaded, try to get property sets
    auto* file = streamer_->ifcFile();
    if (!file) return;

    auto* product = file->instance_by_id(info.ifc_id);
    if (!product) return;

    // Show all direct attributes
    auto& decl = product->declaration();
    if (auto* entity = decl.as_entity()) {
        for (size_t i = 0; i < entity->attribute_count(); ++i) {
            auto* attr = entity->attribute_by_index(i);
            try {
                auto val = product->get_attribute_value(i);
                if (!val.isNull()) {
                    std::string str_val;
                    try {
                        str_val = static_cast<std::string>(val);
                    } catch (...) {
                        // Not a string-convertible attribute (entity ref, aggregate, etc.)
                        str_val = "<" + std::string(IfcUtil::ArgumentTypeToString(val.type())) + ">";
                    }
                    addRow(QString::fromStdString(attr->name()), QString::fromStdString(str_val));
                }
            } catch (...) {}
        }
    }
}
