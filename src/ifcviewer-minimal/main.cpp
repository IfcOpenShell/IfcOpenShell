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
#include <QSurfaceFormat>
#include <QCommandLineParser>

#include "MinimalWindow.h"

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    app.setApplicationName("IfcViewerMinimal");
    app.setOrganizationName("IfcOpenShell");

    QSurfaceFormat fmt;
    fmt.setVersion(4, 5);
    fmt.setProfile(QSurfaceFormat::CoreProfile);
    fmt.setDepthBufferSize(24);
    fmt.setSwapBehavior(QSurfaceFormat::DoubleBuffer);
    fmt.setSamples(4);
    QSurfaceFormat::setDefaultFormat(fmt);

    QCommandLineParser parser;
    parser.setApplicationDescription("IfcOpenShell minimal IFC viewer — benchmarking and debugging");
    parser.addHelpOption();
    parser.addPositionalArgument("files", "IFC file(s) to open", "[files...]");
    parser.addOption({{"c", "camera"},
        "Set camera: tx,ty,tz,dist,yaw,pitch", "params"});
    parser.addOption({{"b", "benchmark"},
        "Run N frames then print stats and exit", "frames"});
    parser.process(app);

    MinimalWindow window;
    window.show();

    auto args = parser.positionalArguments();
    if (!args.isEmpty()) {
        window.addFiles(args);
    }

    if (parser.isSet("camera")) {
        window.setPendingCamera(parser.value("camera"));
    }
    if (parser.isSet("benchmark")) {
        window.setPendingBenchmark(parser.value("benchmark").toInt());
    }

    return app.exec();
}
