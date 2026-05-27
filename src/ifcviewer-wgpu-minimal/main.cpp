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
        "IfcOpenShell minimal wgpu IFC viewer (stage 1: clear-color smoke test)");
    parser.addHelpOption();
    parser.process(app);

    auto* viewport = new WgpuViewportWindow;
    viewport->resize(1280, 800);

    QWidget* container = QWidget::createWindowContainer(viewport);
    container->setMinimumSize(320, 240);

    QMainWindow main_window;
    main_window.setWindowTitle("IfcViewer (wgpu) — stage 1");
    main_window.setCentralWidget(container);
    main_window.resize(1280, 800);
    main_window.show();

    return app.exec();
}
