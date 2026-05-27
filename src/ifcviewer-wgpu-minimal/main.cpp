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
    parser.process(app);

    auto* viewport = new WgpuViewportWindow;
    viewport->resize(1280, 800);

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

    if (parser.isSet("screenshot")) {
        viewport->captureNextFrameToPng(parser.value("screenshot"),
                                        /*quit_after=*/true);
    }
    if (parser.isSet("benchmark")) {
        viewport->setBenchmarkFrames(parser.value("benchmark").toInt());
    }

    return app.exec();
}
