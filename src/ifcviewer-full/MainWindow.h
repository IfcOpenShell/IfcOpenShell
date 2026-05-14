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
class QProgressBar;
class QStackedWidget;
class QToolButton;
class Federation;
class SceneLoader;
namespace ifcviewerfull { class ElementRegistry; }
namespace ifcviewerfull { class SessionState; }
namespace ifcviewerfull::components { class TabBar; }
namespace ifcviewerfull::modules::models { class ModelsPanelController; }
namespace ifcviewerfull::modules::models { class ModelsPanel; }
namespace ifcviewerfull::modules::models { class ModelsPanelView; }
namespace ifcviewerfull::modules::project { class ProjectController; }
namespace ifcviewerfull::modules::spatial_hierarchy { class SpatialHierarchyPanel; }
namespace ifcviewerfull::modules::spatial_hierarchy { class SpatialHierarchyPanelView; }
namespace ifcviewerfull::modules::properties { class PropertiesPanel; }
namespace ifcviewerfull::modules::properties { class PropertiesPanelView; }
namespace ifcviewerfull::modules::viewport { class ViewportController; }
namespace ifcviewerfull::modules::viewport { class ViewportPanel; }

namespace ifcviewerfull::shell {

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
    QProgressBar* status_progress_bar_ = nullptr;
    ifcviewerfull::components::TabBar* ribbon_tabs_ = nullptr;
    QStackedWidget* ribbon_pages_ = nullptr;
    ifcviewerfull::modules::viewport::ViewportPanel* viewport_widget_ = nullptr;
    ifcviewerfull::modules::viewport::ViewportController* viewport_controller_ = nullptr;
    SceneLoader* loader_ = nullptr;
    ifcviewerfull::ElementRegistry* element_registry_ = nullptr;
    ifcviewerfull::SessionState* session_state_ = nullptr;
    ifcviewerfull::modules::models::ModelsPanel* models_panel_ = nullptr;
    ifcviewerfull::modules::spatial_hierarchy::SpatialHierarchyPanel* spatial_panel_ = nullptr;
    QDockWidget* layers_panel_ = nullptr;
    ifcviewerfull::modules::properties::PropertiesPanel* properties_panel_ = nullptr;
    QDockWidget* stored_views_panel_ = nullptr;
    QDockWidget* search_panel_ = nullptr;
    QDockWidget* spreadsheet_panel_ = nullptr;
    QDockWidget* audit_panel_ = nullptr;
    QDockWidget* clash_panel_ = nullptr;
    QDockWidget* issues_panel_ = nullptr;
    ifcviewerfull::modules::models::ModelsPanelController* models_controller_ = nullptr;
    ifcviewerfull::modules::models::ModelsPanelView* models_view_ = nullptr;
    ifcviewerfull::modules::project::ProjectController* project_controller_ = nullptr;
    ifcviewerfull::modules::spatial_hierarchy::SpatialHierarchyPanelView* spatial_view_ = nullptr;
    ifcviewerfull::modules::properties::PropertiesPanelView* properties_view_ = nullptr;
};

} // namespace ifcviewerfull::shell

#endif
