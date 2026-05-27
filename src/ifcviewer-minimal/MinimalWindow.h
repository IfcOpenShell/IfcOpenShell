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

#include "ViewportWindow.h"
#include "SceneLoader.h"

class MinimalWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MinimalWindow(QWidget* parent = nullptr);
    ~MinimalWindow() = default;

    void addFiles(const QStringList& paths);
    void setPendingCamera(const QString& params);
    void setPendingBenchmark(int frames);
    // One-shot framebuffer capture queued for the next render. Forwarded
    // to ViewportWindow::captureNextFrameToPng; the viewport handles the
    // glReadPixels + PNG save + optional QCoreApplication::quit.
    void setPendingScreenshot(const QString& path);

private slots:
    void onLoadStarted(uint32_t mid, QString display_name);
    void onLoadedFromSidecar(uint32_t mid, qint64 elapsed_ms);
    void onLoadedFromStream(uint32_t mid, qint64 elapsed_ms);
    void onLoadCancelled(uint32_t mid);
    void onLoadError(uint32_t mid, QString message);
    void onAllLoadsFinished();

private:
    void applyPendingBenchmark();

    ViewportWindow* viewport_ = nullptr;
    SceneLoader*    loader_   = nullptr;
    QWidget* viewport_container_ = nullptr;
    QLabel* status_label_ = nullptr;
    QLabel* stats_label_ = nullptr;

    QString pending_camera_;
    int     pending_benchmark_ = 0;
    QString pending_screenshot_;
};

#endif // MINIMALWINDOW_H
