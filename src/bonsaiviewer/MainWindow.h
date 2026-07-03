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

#ifndef IFCINTERFACE_SHELL_MAINWINDOW_H
#define IFCINTERFACE_SHELL_MAINWINDOW_H

#include <QHash>
#include <QMainWindow>
#include <QStringList>

class QLabel;
class QDockWidget;
class QMenu;
class QProgressBar;
class QStackedWidget;
class QToolButton;
namespace bonsaiviewer { class SessionState; }
namespace bonsaiviewer::components { class TabBar; }
namespace bonsaiviewer::modules::models { class ModelsPanel; }
namespace bonsaiviewer::modules::models { class ModelsPanelView; }
namespace bonsaiviewer::modules::spatial_hierarchy { class SpatialHierarchyPanel; }
namespace bonsaiviewer::modules::spatial_hierarchy { class SpatialHierarchyPanelView; }
namespace bonsaiviewer::modules::properties { class PropertiesPanel; }
namespace bonsaiviewer::modules::properties { class PropertiesPanelView; }
namespace bonsaiviewer::modules::viewport { class ViewportView; }
namespace bonsaiviewer::modules::viewport { class ViewportPanel; }

namespace bonsaiviewer::shell {

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
    // Rebuilds `menu` from the persisted recent-projects list. Wired to the
    // menu's aboutToShow so it always reflects the current MRU state.
    void populateRecentMenu(QMenu* menu);

private:
    QLabel* status_mode_label_ = nullptr;
    QLabel* status_selection_label_ = nullptr;
    QLabel* status_perf_label_ = nullptr;
    QProgressBar* status_progress_bar_ = nullptr;
    bonsaiviewer::components::TabBar* ribbon_tabs_ = nullptr;
    QStackedWidget* ribbon_pages_ = nullptr;
    bonsaiviewer::modules::viewport::ViewportPanel* viewport_widget_ = nullptr;
    bonsaiviewer::modules::viewport::ViewportView* viewport_view_ = nullptr;
    bonsaiviewer::SessionState* session_state_ = nullptr;
    bonsaiviewer::modules::models::ModelsPanel* models_panel_ = nullptr;
    bonsaiviewer::modules::spatial_hierarchy::SpatialHierarchyPanel* spatial_panel_ = nullptr;
    QDockWidget* layers_panel_ = nullptr;
    bonsaiviewer::modules::properties::PropertiesPanel* properties_panel_ = nullptr;
    QDockWidget* stored_views_panel_ = nullptr;
    QDockWidget* search_panel_ = nullptr;
    QDockWidget* spreadsheet_panel_ = nullptr;
    QDockWidget* audit_panel_ = nullptr;
    QDockWidget* clash_panel_ = nullptr;
    QDockWidget* issues_panel_ = nullptr;
    bonsaiviewer::modules::models::ModelsPanelView* models_view_ = nullptr;
    bonsaiviewer::modules::spatial_hierarchy::SpatialHierarchyPanelView* spatial_view_ = nullptr;
    bonsaiviewer::modules::properties::PropertiesPanelView* properties_view_ = nullptr;
};

} // namespace bonsaiviewer::shell

#endif
