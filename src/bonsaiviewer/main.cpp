// This file was generated with the assistance of an AI coding tool.
/********************************************************************************
 *                                                                              *
 * This file is part of Bonsai.                                                 *
 *                                                                              *
 * Bonsai is free software: you can redistribute it and/or modify               *
 * it under the terms of the GNU General Public License as published by         *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * Bonsai is distributed in the hope that it will be useful,                    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * GNU General Public License for more details.                                 *
 *                                                                              *
 * You should have received a copy of the GNU General Public License            *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "MainWindow.h"
#include "ViewerSettings.h"
#include "components/Style.h"
#include "modules/models/Commands.h"

#include <QApplication>
#include <QCommandLineParser>
#include <QFont>
#include <QFontDatabase>
#include <QSurfaceFormat>

namespace {

void installUiFont() {
    const int font_id = QFontDatabase::addApplicationFont(
        ":/fonts/DMSans-VariableFont_opsz,wght.ttf");
    QString family;
    if (font_id >= 0) {
        const QStringList families = QFontDatabase::applicationFontFamilies(font_id);
        if (!families.isEmpty()) {
            family = families.front();
        }
    }
    if (!family.isEmpty()) {
        // Slightly smaller base font to fit more data. Panel titles keep their
        // own explicit size (QLabel#panelTitleText in Style.cpp), so they're
        // unaffected by this.
        QApplication::setFont(QFont(family, 9));
    }
}

} // namespace

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    app.setApplicationName("Bonsai Viewer");
    app.setOrganizationName("IfcOpenShell");

    // Clear any .rdbview extractions left in temp by a previous session.
    bonsaiviewer::modules::models::commands::cleanupRdbviewCache();

    QSurfaceFormat fmt;
    fmt.setVersion(4, 5);
    fmt.setProfile(QSurfaceFormat::CoreProfile);
    fmt.setDepthBufferSize(24);
    fmt.setSwapBehavior(QSurfaceFormat::DoubleBuffer);
    fmt.setSamples(4);
    QSurfaceFormat::setDefaultFormat(fmt);

    QCommandLineParser parser;
    parser.setApplicationDescription("Bonsai Viewer — IfcOpenShell IFC viewer");
    parser.addHelpOption();
    parser.process(app);

    installUiFont();
    const auto applyStyle = [&app]() {
        app.setStyleSheet(bonsaiviewer::components::style::buildAppStyleSheet());
    };
    applyStyle();
    QObject::connect(&bonsaiviewer::ViewerSettings::instance(),
                     &bonsaiviewer::ViewerSettings::themeChanged,
                     &app,
                     applyStyle);

    bonsaiviewer::shell::MainWindow window;
    window.show();
    return app.exec();
}
