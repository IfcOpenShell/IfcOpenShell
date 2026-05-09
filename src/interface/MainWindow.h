// This file was generated with the assistance of an AI coding tool.
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

#ifndef IFCINTERFACE_SHELL_MAINWINDOW_H
#define IFCINTERFACE_SHELL_MAINWINDOW_H

#include <QHash>
#include <QMainWindow>
#include <QStringList>

class QLabel;
class QDockWidget;
class QStackedWidget;
class QToolButton;
class Federation;
class SceneLoader;
namespace ifcinterface { class ElementRegistry; }
namespace ifcinterface { class SessionState; }
namespace ifcinterface::components { class TabBar; }
namespace ifcinterface::modules::models { class ModelsPanelController; }
namespace ifcinterface::modules::models { class ModelsPanel; }
namespace ifcinterface::modules::models { class ModelsPanelView; }
namespace ifcinterface::modules::project { class ProjectController; }
namespace ifcinterface::modules::spatial_hierarchy { class SpatialHierarchyPanel; }
namespace ifcinterface::modules::spatial_hierarchy { class SpatialHierarchyPanelView; }
namespace ifcinterface::modules::properties { class PropertiesPanel; }
namespace ifcinterface::modules::properties { class PropertiesPanelView; }
namespace ifcinterface::modules::viewport { class ViewportController; }
namespace ifcinterface::modules::viewport { class ViewportPanel; }

namespace ifcinterface::shell {

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget* parent = nullptr);

private:
    void setupChrome();
    void setupRibbon();
    void setupViewport();
    void setupPanels();
    void setupStatus();
    void setupLoader();
    QWidget* buildHomeRibbonPage();
    QWidget* buildNavigateRibbonPage();
    QWidget* buildInspectRibbonPage();
    QWidget* buildPanelsRibbonPage();
    void updateWindowTitle();
    QToolButton* makePanelToggle(const QString& text, QDockWidget* dock);

private:
    Federation* federation_ = nullptr;
    QLabel* status_mode_label_ = nullptr;
    QLabel* status_selection_label_ = nullptr;
    QLabel* status_perf_label_ = nullptr;
    ifcinterface::components::TabBar* ribbon_tabs_ = nullptr;
    QStackedWidget* ribbon_pages_ = nullptr;
    ifcinterface::modules::viewport::ViewportPanel* viewport_widget_ = nullptr;
    ifcinterface::modules::viewport::ViewportController* viewport_controller_ = nullptr;
    SceneLoader* loader_ = nullptr;
    ifcinterface::ElementRegistry* element_registry_ = nullptr;
    ifcinterface::SessionState* session_state_ = nullptr;
    ifcinterface::modules::models::ModelsPanel* models_panel_ = nullptr;
    ifcinterface::modules::spatial_hierarchy::SpatialHierarchyPanel* spatial_panel_ = nullptr;
    QDockWidget* layers_panel_ = nullptr;
    ifcinterface::modules::properties::PropertiesPanel* properties_panel_ = nullptr;
    QDockWidget* stored_views_panel_ = nullptr;
    QDockWidget* search_panel_ = nullptr;
    QDockWidget* spreadsheet_panel_ = nullptr;
    QDockWidget* audit_panel_ = nullptr;
    QDockWidget* clash_panel_ = nullptr;
    QDockWidget* issues_panel_ = nullptr;
    ifcinterface::modules::models::ModelsPanelController* models_controller_ = nullptr;
    ifcinterface::modules::models::ModelsPanelView* models_view_ = nullptr;
    ifcinterface::modules::project::ProjectController* project_controller_ = nullptr;
    ifcinterface::modules::spatial_hierarchy::SpatialHierarchyPanelView* spatial_view_ = nullptr;
    ifcinterface::modules::properties::PropertiesPanelView* properties_view_ = nullptr;
};

} // namespace ifcinterface::shell

#endif
