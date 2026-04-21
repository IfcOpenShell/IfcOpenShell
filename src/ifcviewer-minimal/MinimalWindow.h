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

#ifndef MINIMALWINDOW_H
#define MINIMALWINDOW_H

#include <QMainWindow>
#include <QLabel>
#include <QTimer>
#include <QElapsedTimer>

#include <map>
#include <deque>
#include <thread>

#include "ViewportWindow.h"
#include "GeometryStreamer.h"

class MinimalWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MinimalWindow(QWidget* parent = nullptr);
    ~MinimalWindow();

    void addFiles(const QStringList& paths);
    void setPendingCamera(const QString& params);
    void setPendingBenchmark(int frames);

private slots:
    void onMeshReady(MeshChunk chunk);
    void onInstanceReady(InstanceChunk chunk);
    void onStreamingFinished();
    void onErrorOccurred(const QString& message);
    void drainStreamerElements();

private:
    struct ModelEntry {
        uint32_t id = 0;
        QString file_path;
        QString display_name;
        GeometryStreamer* streamer = nullptr;
    };

    void startNextLoad();
    void connectStreamer(GeometryStreamer* streamer);
    void joinSidecarThread();
    void applySidecarData(uint32_t mid, SidecarData data);
    void applyPendingBenchmark();

    ViewportWindow* viewport_ = nullptr;
    QWidget* viewport_container_ = nullptr;
    QLabel* status_label_ = nullptr;
    QLabel* stats_label_ = nullptr;

    std::map<uint32_t, ModelEntry> models_;
    std::deque<uint32_t> load_queue_;
    uint32_t next_model_id_ = 1;
    uint32_t next_object_id_ = 1;
    uint32_t loading_model_id_ = 0;
    std::thread sidecar_read_thread_;

    QTimer element_drain_timer_;
    QElapsedTimer load_timer_;

    QString pending_camera_;
    int     pending_benchmark_ = 0;
};

#endif // MINIMALWINDOW_H
