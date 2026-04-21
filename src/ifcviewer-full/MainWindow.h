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
#include <QTimer>
#include <QElapsedTimer>

#include <map>
#include <deque>
#include <thread>
#include <unordered_map>

#include "ViewportWindow.h"
#include "GeometryStreamer.h"

class SettingsWindow;

using ModelId = uint32_t;

struct ModelHandle {
    ModelId id = 0;
    QString file_path;
    QString display_name;
    GeometryStreamer* streamer = nullptr;
    QTreeWidgetItem* tree_root = nullptr;
    bool visible = true;
};

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget* parent = nullptr);
    ~MainWindow();

    void addFiles(const QStringList& paths);
    void setPendingCamera(const QString& params);
    void setPendingBenchmark(int frames);

private slots:
    void onFileOpen();
    void onFileSettings();
    void onProgressChanged(int percent);
    void onMeshReady(MeshChunk chunk);
    void onInstanceReady(InstanceChunk chunk);
    void onStreamingFinished();
    void onObjectPicked(uint32_t object_id);
    void onTreeSelectionChanged();
    void pollNewElements();

private:
    void setupUi();
    void setupMenus();
    void populateProperties(uint32_t object_id);
    void startNextLoad();
    void applySidecarData(ModelId mid, SidecarData data);
    void joinSidecarThread();
    void populateTreeFromSidecar(ModelHandle& model,
                                 const std::vector<PackedElementInfo>& elements,
                                 const std::string& string_table);
    void connectStreamer(GeometryStreamer* streamer);

    ViewportWindow* viewport_ = nullptr;
    SettingsWindow* settings_ = nullptr;
    QWidget* viewport_container_ = nullptr;
    QTreeWidget* element_tree_ = nullptr;
    QTableWidget* property_table_ = nullptr;
    QProgressBar* progress_bar_ = nullptr;
    QLabel* status_label_ = nullptr;
    QLabel* stats_label_ = nullptr;
    QTimer element_poll_timer_;
    QElapsedTimer load_timer_;

    // Multi-model state
    std::map<ModelId, ModelHandle> models_;
    ModelId next_model_id_ = 1;
    uint32_t next_object_id_ = 1; // monotonically increasing across all models
    std::deque<ModelId> load_queue_;
    ModelId loading_model_id_ = 0;
    std::thread sidecar_read_thread_;

    // Map object_id -> tree item and element info
    std::unordered_map<uint32_t, ElementInfo> element_map_;
    std::unordered_map<uint32_t, QTreeWidgetItem*> tree_items_;
    // Scoped (model_id, ifc_id) -> object_id
    std::unordered_map<uint64_t, uint32_t> scoped_ifc_id_to_object_id_;

    static uint64_t scopedKey(uint32_t model_id, int ifc_id) {
        return (static_cast<uint64_t>(model_id) << 32) | static_cast<uint32_t>(ifc_id);
    }

    QString pending_camera_;
    int     pending_benchmark_ = 0;

    void applyPendingBenchmark();
};

#endif // MAINWINDOW_H
