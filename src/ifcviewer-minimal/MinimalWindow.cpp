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

#include <QStatusBar>
#include <QDebug>

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

    loader_ = new SceneLoader(viewport_, this);
    connect(loader_, &SceneLoader::loadStarted,
            this, &MinimalWindow::onLoadStarted);
    connect(loader_, &SceneLoader::loadedFromSidecar,
            this, &MinimalWindow::onLoadedFromSidecar);
    connect(loader_, &SceneLoader::loadedFromStream,
            this, &MinimalWindow::onLoadedFromStream);
    connect(loader_, &SceneLoader::loadCancelled,
            this, &MinimalWindow::onLoadCancelled);
    connect(loader_, &SceneLoader::loadError,
            this, &MinimalWindow::onLoadError);
    connect(loader_, &SceneLoader::allLoadsFinished,
            this, &MinimalWindow::onAllLoadsFinished);

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

    setWindowTitle("IfcViewerMinimal");
    resize(1200, 800);
}

void MinimalWindow::addFiles(const QStringList& paths) {
    loader_->addFiles(paths);
}

static QString formatElapsed(qint64 ms) {
    return (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
}

void MinimalWindow::onLoadStarted(uint32_t /*mid*/, QString display_name) {
    status_label_->setText("Loading: " + display_name);
}

void MinimalWindow::onLoadedFromSidecar(uint32_t mid, qint64 elapsed_ms) {
    status_label_->setText(QString("%1 loaded from cache in %2")
        .arg(loader_->displayName(mid))
        .arg(formatElapsed(elapsed_ms)));
}

void MinimalWindow::onLoadedFromStream(uint32_t mid, qint64 elapsed_ms) {
    status_label_->setText(QString("%1 streamed in %2")
        .arg(loader_->displayName(mid))
        .arg(formatElapsed(elapsed_ms)));
}

void MinimalWindow::onLoadCancelled(uint32_t mid) {
    status_label_->setText(QString("%1 load cancelled")
        .arg(loader_->displayName(mid)));
}

void MinimalWindow::onLoadError(uint32_t /*mid*/, QString message) {
    qWarning("IfcViewerMinimal error: %s", qPrintable(message));
    status_label_->setText("Error: " + message);
}

void MinimalWindow::onAllLoadsFinished() {
    status_label_->setText(QString("Loaded %1 model(s)").arg(loader_->modelCount()));
    applyPendingBenchmark();
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
