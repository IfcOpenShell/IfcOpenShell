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

#include "ViewportWindow.h"
#include "SceneLoader.h"

class SettingsWindow;

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
    void onDatabaseOpen();
    void onFileSettings();
    void onObjectPicked(uint32_t object_id);
    void onTreeSelectionChanged();

    void onLoadStarted(uint32_t mid, QString display_name);
    void onLoadProgressChanged(int percent);
    void onSidecarElementsReady(uint32_t mid,
                                std::vector<PackedElementInfo> elements,
                                std::string string_table);
    void onLoadedFromSidecar(uint32_t mid, qint64 elapsed_ms);
    void onStreamedElementsReady(uint32_t mid, std::vector<ElementInfo> elements);
    void onLoadedFromStream(uint32_t mid, qint64 elapsed_ms);
    void onLoadCancelled(uint32_t mid);
    void onLoadError(uint32_t mid, QString message);
    void onAllLoadsFinished();

private:
    void setupUi();
    void setupMenus();
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
    void applyPendingBenchmark();
    QString formatElapsed(qint64 ms) const;

    ViewportWindow* viewport_ = nullptr;
    SceneLoader*    loader_   = nullptr;
    SettingsWindow* settings_ = nullptr;
    QWidget* viewport_container_ = nullptr;
    QTreeWidget* element_tree_ = nullptr;
    QTableWidget* property_table_ = nullptr;
    QProgressBar* progress_bar_ = nullptr;
    QLabel* status_label_ = nullptr;
    QLabel* stats_label_ = nullptr;

    // Per-model tree roots, keyed by model_id.
    std::map<uint32_t, QTreeWidgetItem*> tree_roots_;

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
};

#endif // MAINWINDOW_H
