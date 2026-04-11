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

#include <unordered_map>

#include "ViewportWindow.h"
#include "GeometryStreamer.h"

class SettingsWindow;

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget* parent = nullptr);
    ~MainWindow();

    void openFile(const QString& path);

private slots:
    void onFileOpen();
    void onFileSettings();
    void onProgressChanged(int percent);
    void onElementReady(UploadChunk chunk);
    void onStreamingFinished();
    void onObjectPicked(uint32_t object_id);
    void onTreeSelectionChanged();
    void pollNewElements();

private:
    void setupUi();
    void setupMenus();
    void populateProperties(uint32_t object_id);

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

    GeometryStreamer* streamer_ = nullptr;

    // Map object_id -> tree item and element info
    std::unordered_map<uint32_t, ElementInfo> element_map_;
    std::unordered_map<uint32_t, QTreeWidgetItem*> tree_items_;
    std::unordered_map<int, uint32_t> ifc_id_to_object_id_;
};

#endif // MAINWINDOW_H
