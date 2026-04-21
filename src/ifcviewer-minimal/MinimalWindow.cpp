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

#include "MinimalWindow.h"
#include "AppSettings.h"
#include "SidecarCache.h"

#include <QApplication>
#include <QFileInfo>
#include <QStatusBar>
#include <QTimer>
#include <QDebug>

#include <memory>
#include <optional>

MinimalWindow::MinimalWindow(QWidget* parent)
    : QMainWindow(parent)
{
    viewport_ = new ViewportWindow();
    viewport_container_ = QWidget::createWindowContainer(viewport_, this);
    viewport_container_->setMinimumSize(400, 300);
    viewport_container_->setFocusPolicy(Qt::StrongFocus);
    setCentralWidget(viewport_container_);

    status_label_ = new QLabel("Ready");
    stats_label_  = new QLabel();
    stats_label_->setVisible(AppSettings::instance().showStats());
    statusBar()->addWidget(status_label_, 1);
    statusBar()->addPermanentWidget(stats_label_);

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

    // Periodically drain the streamer's pending-elements buffer so it doesn't
    // grow unbounded on large models. We don't use the element data here —
    // this window has no tree — but the buffer must still be flushed.
    connect(&element_drain_timer_, &QTimer::timeout, this, &MinimalWindow::drainStreamerElements);
    element_drain_timer_.setInterval(250);

    setWindowTitle("IfcViewerMinimal");
    resize(1200, 800);
}

MinimalWindow::~MinimalWindow() {
    joinSidecarThread();
}

void MinimalWindow::joinSidecarThread() {
    if (sidecar_read_thread_.joinable())
        sidecar_read_thread_.join();
}

void MinimalWindow::addFiles(const QStringList& paths) {
    for (const auto& path : paths) {
        uint32_t id = next_model_id_++;
        ModelEntry entry;
        entry.id = id;
        entry.file_path = path;
        entry.display_name = QFileInfo(path).fileName();
        entry.streamer = new GeometryStreamer(this);
        models_[id] = entry;
        load_queue_.push_back(id);
    }

    if (loading_model_id_ == 0) {
        QTimer::singleShot(0, this, &MinimalWindow::startNextLoad);
    }
}

void MinimalWindow::connectStreamer(GeometryStreamer* streamer) {
    connect(streamer, &GeometryStreamer::meshReady,
            this, &MinimalWindow::onMeshReady, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::instanceReady,
            this, &MinimalWindow::onInstanceReady, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::finished,
            this, &MinimalWindow::onStreamingFinished, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::errorOccurred,
            this, &MinimalWindow::onErrorOccurred, Qt::QueuedConnection);
}

void MinimalWindow::startNextLoad() {
    if (load_queue_.empty()) {
        loading_model_id_ = 0;
        status_label_->setText(QString("Loaded %1 model(s)").arg(models_.size()));
        applyPendingBenchmark();
        return;
    }

    loading_model_id_ = load_queue_.front();
    load_queue_.pop_front();

    auto& model = models_[loading_model_id_];

    load_timer_.restart();
    status_label_->setText("Loading: " + model.display_name);

    std::string ifc_path = model.file_path.toStdString();
    uint64_t file_size = static_cast<uint64_t>(QFileInfo(model.file_path).size());
    uint32_t mid = loading_model_id_;

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
                auto it = models_.find(mid);
                if (it == models_.end()) return;
                auto& m = it->second;
                connectStreamer(m.streamer);
                element_drain_timer_.start();
                m.streamer->loadFile(
                    m.file_path.toStdString(), next_object_id_, loading_model_id_);
            }
        }, Qt::QueuedConnection);
    });
}

void MinimalWindow::applySidecarData(uint32_t mid, SidecarData data) {
    auto it = models_.find(mid);
    if (it == models_.end()) return;
    auto& model = it->second;

    qDebug("Sidecar hit: %s (%zu verts, %zu indices, %zu meshes, %zu instances, %zu elements)",
           model.file_path.toStdString().c_str(),
           data.vertices.size() / INSTANCED_VERTEX_STRIDE_BYTES,
           data.indices.size(),
           data.meshes.size(),
           data.instances.size(),
           data.elements.size());

    // Rebase object/model IDs onto the current session's ID space.  Matches
    // MainWindow::applySidecarData — two cached models both starting at
    // object_id=1 would collide otherwise.
    uint32_t min_oid = UINT32_MAX;
    for (const auto& pe : data.elements) {
        if (pe.object_id < min_oid) min_oid = pe.object_id;
    }
    uint32_t oid_offset = 0;
    if (!data.elements.empty() && min_oid < UINT32_MAX) {
        oid_offset = next_object_id_ - min_oid;
    }
    for (auto& pe : data.elements) {
        pe.object_id += oid_offset;
        pe.model_id   = mid;
        if (pe.object_id >= next_object_id_)
            next_object_id_ = pe.object_id + 1;
    }
    for (auto& inst : data.instances) {
        inst.object_id += oid_offset;
        inst.model_id   = mid;
    }

    viewport_->applyCachedModel(mid, std::move(data));

    qint64 ms = load_timer_.elapsed();
    QString elapsed = (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
    status_label_->setText(QString("%1 loaded from cache in %2")
        .arg(model.display_name).arg(elapsed));

    loading_model_id_ = 0;
    QTimer::singleShot(0, this, &MinimalWindow::startNextLoad);
}

void MinimalWindow::onMeshReady(MeshChunk chunk) {
    viewport_->uploadMeshChunk(chunk);
}

void MinimalWindow::onInstanceReady(InstanceChunk chunk) {
    viewport_->uploadInstanceChunk(chunk);
}

void MinimalWindow::drainStreamerElements() {
    if (loading_model_id_ == 0) return;
    auto it = models_.find(loading_model_id_);
    if (it == models_.end()) return;
    (void)it->second.streamer->drainElements();
}

void MinimalWindow::onStreamingFinished() {
    element_drain_timer_.stop();
    drainStreamerElements();

    if (loading_model_id_ != 0) {
        auto it = models_.find(loading_model_id_);
        if (it != models_.end()) {
            next_object_id_ = it->second.streamer->lastObjectId();
            viewport_->finalizeModel(loading_model_id_);
        }
    }

    qint64 ms = load_timer_.elapsed();
    QString elapsed = (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";

    auto it = models_.find(loading_model_id_);
    QString name = (it != models_.end()) ? it->second.display_name : QString();
    status_label_->setText(QString("%1 streamed in %2").arg(name).arg(elapsed));

    startNextLoad();
}

void MinimalWindow::onErrorOccurred(const QString& message) {
    qWarning("IfcViewerMinimal error: %s", qPrintable(message));
    status_label_->setText("Error: " + message);
}

void MinimalWindow::setPendingCamera(const QString& params) {
    pending_camera_ = params;
}

void MinimalWindow::setPendingBenchmark(int frames) {
    pending_benchmark_ = frames;
}

void MinimalWindow::applyPendingBenchmark() {
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
