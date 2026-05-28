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

#include <QApplication>
#include <QCommandLineParser>
#include <QMainWindow>
#include <QWidget>
#include <QVBoxLayout>

#include "WgpuViewportWindow.h"

// Stage-1 driver: opens a single window with the wgpu viewport embedded,
// clears to background colour, and exits on close. The shape mirrors
// ifcviewer-minimal so subsequent stages can grow this into a full
// benchmark-comparable binary.
int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    app.setApplicationName("IfcViewerWgpuMinimal");
    app.setOrganizationName("IfcOpenShell");

    QCommandLineParser parser;
    parser.setApplicationDescription(
        "IfcOpenShell minimal wgpu IFC viewer");
    parser.addHelpOption();
    parser.addPositionalArgument("files",
        "Sidecar (.ifcview) files to load. Stem-based: foo.ifc resolves to foo.ifcview.",
        "[files...]");
    parser.addOption({{"s", "screenshot"},
        "Render one frame, save to PATH as PNG, exit.", "path"});
    parser.addOption({{"b", "benchmark"},
        "Render N frames (yaw-sweeping the camera), print stats, exit.", "frames"});
    parser.addOption({{"c", "camera"},
        "Set camera as tx,ty,tz,dist,yaw,pitch (same format as IfcViewerMinimal).",
        "params"});
    parser.addOption({"no-hiz",
        "Disable HiZ occlusion culling for perf diagnostics."});
    parser.addOption({"web-limits",
        "Request the WebGPU mandatory floor limits (128MB max storage binding) "
        "instead of the adapter's actual max. Use to verify scenes fit through "
        "browser constraints."});
    parser.addOption({"streaming",
        "Enable streaming sidecar load. Reads metadata-only at load time; "
        "vertex chunks are deferred and loaded on demand as they become "
        "frustum-visible. Required for scenes that exceed GPU memory."});
    parser.process(app);

    auto* viewport = new WgpuViewportWindow;
    viewport->resize(1280, 800);
    if (parser.isSet("no-hiz"))     viewport->hiz_enabled_      = false;
    if (parser.isSet("web-limits")) viewport->web_limits_       = true;
    if (parser.isSet("streaming"))  viewport->streaming_enabled_ = true;

    QWidget* container = QWidget::createWindowContainer(viewport);
    container->setMinimumSize(320, 240);

    QMainWindow main_window;
    main_window.setWindowTitle("IfcViewer (wgpu) — stage 2");
    main_window.setCentralWidget(container);
    main_window.resize(1280, 800);
    main_window.show();

    // Queue sidecars; they're loaded after wgpu init completes in
    // exposeEvent. Ordering matches the command line.
    for (const QString& path : parser.positionalArguments()) {
        viewport->queueLoadSidecar(path);
    }

    if (parser.isSet("camera")) {
        const QStringList parts = parser.value("camera").split(',');
        if (parts.size() == 6) {
            bool ok = true;
            float v[6];
            for (int i = 0; i < 6 && ok; ++i) v[i] = parts[i].toFloat(&ok);
            if (ok) {
                viewport->setCamera(v[0], v[1], v[2], v[3], v[4], v[5]);
            } else {
                qWarning() << "--camera: failed to parse" << parser.value("camera");
            }
        } else {
            qWarning() << "--camera: expected 6 comma-separated floats, got"
                       << parts.size();
        }
    }

    if (parser.isSet("screenshot")) {
        viewport->captureNextFrameToPng(parser.value("screenshot"),
                                        /*quit_after=*/true);
    }
    if (parser.isSet("benchmark")) {
        viewport->setBenchmarkFrames(parser.value("benchmark").toInt());
    }

    return app.exec();
}
