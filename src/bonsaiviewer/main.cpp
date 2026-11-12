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
#include "../ifcparse/parse.h"
#include "../plugin/plugin.h"

#include <QApplication>
#include <QCommandLineParser>
#include <QFont>
#include <QFontDatabase>
#include <QSurfaceFormat>

#include <filesystem>
#include <iostream>

namespace {

const char* pluginKindName(ifcopenshell::plugin::kind value) {
    using ifcopenshell::plugin::kind;
    switch (value) {
    case kind::parse_schema: return "parse_schema";
    case kind::mapping: return "mapping";
    case kind::kernel: return "kernel";
    case kind::tree: return "tree";
    case kind::document_serializer: return "document_serializer";
    case kind::geometry_serializer: return "geometry_serializer";
    case kind::opencascade_geometry_ifc_writer: return "opencascade_geometry_ifc_writer";
    case kind::linework_processing: return "linework_processing";
    }
    return "unknown";
}

// Try to load every ifcopenshell_* plugin next to the executable and report the result.
int listPlugins() {
    ifcopenshell::plugin::manager manager;
    std::filesystem::path pluginsDir(QCoreApplication::applicationDirPath().toStdWString());
#ifdef __APPLE__
    // Plug-ins are staged into `BonsaiViewer.app/Contents/Frameworks`.
    pluginsDir = pluginsDir.parent_path() / "Frameworks";
#endif
    manager.add_search_path(pluginsDir);

    int failures = 0;
    for (const auto& dir : manager.search_paths()) {
        std::cout << "Search path: " << dir.string() << "\n";
    }
    for (const auto& path : manager.discover("ifcopenshell_")) {
        try {
            const auto module = manager.load(path);
            const auto& meta = module.meta();
            std::cout << "OK    " << path.filename().string() << " (" << pluginKindName(meta.kind_);
            if (!meta.id.empty()) {
                std::cout << ", id=" << meta.id;
            }
            if (!meta.schema.empty()) {
                std::cout << ", schema=" << meta.schema;
            }
            if (!meta.format.empty()) {
                std::cout << ", format=" << meta.format;
            }
            std::cout << ")\n";
        } catch (const std::exception& e) {
            ++failures;
            std::cout << "FAIL  " << path.filename().string() << ": " << e.what() << "\n";
        }
    }
    return failures == 0 ? 0 : 1;
}

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
    app.setApplicationVersion(QString::fromUtf8(IFCOPENSHELL_VERSION));

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
    parser.addVersionOption();
    const QCommandLineOption listPluginsOption(
        "list-plugins", "Try to load every plugin next to the executable and report the result.");
    parser.addOption(listPluginsOption);
    parser.process(app);

    if (parser.isSet(listPluginsOption)) {
        return listPlugins();
    }

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
