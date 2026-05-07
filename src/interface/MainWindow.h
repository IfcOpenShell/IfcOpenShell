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
namespace ifcinterface::panels::models { class ModelsPanelController; }
namespace ifcinterface::panels::models { class ModelsPanelWidget; }
namespace ifcinterface::panels::models { class ModelsPanelView; }
namespace ifcinterface::panels::spatial_hierarchy { class SpatialHierarchyPanelWidget; }
namespace ifcinterface::panels::spatial_hierarchy { class SpatialHierarchyPanelView; }
namespace ifcinterface::panels::properties { class PropertiesPanelWidget; }
namespace ifcinterface::panels::properties { class PropertiesPanelView; }
namespace ifcinterface::panels::viewport { class ViewportController; }
namespace ifcinterface::panels::viewport { class ViewportWidget; }

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
    void clearScene();
    bool confirmDiscardIfDirty();
    void loadModelsFromPaths(const QStringList& paths, const QStringList& fed_ids);
    bool openProject(const QString& path);
    bool saveProject();
    bool saveProjectAs();
    void updateWindowTitle();
    QToolButton* makeRibbonAction(const QString& text, const QString& icon_path);
    QWidget* makeRibbonGroup(const QString& title, const QList<QToolButton*>& buttons);
    QToolButton* makePanelToggle(const QString& text, QDockWidget* dock);
    void addFiles(const QStringList& paths);
    QString formatElapsed(qint64 ms) const;

private slots:
    void onAddFiles();
    void onLoadStarted(uint32_t mid, QString display_name);
    void onLoadedFromSidecar(uint32_t mid, qint64 elapsed_ms);
    void onLoadedFromStream(uint32_t mid, qint64 elapsed_ms);
    void onLoadCancelled(uint32_t mid);
    void onLoadError(uint32_t mid, QString message);
    void onAllLoadsFinished();
    void onSetHomeView();
    void onGoHomeView();
    void onNewProject();
    void onOpenProject();
    void onSaveProject();
    void onSaveProjectAs();

private:
    Federation* federation_ = nullptr;
    QLabel* status_mode_label_ = nullptr;
    QLabel* status_selection_label_ = nullptr;
    QLabel* status_perf_label_ = nullptr;
    ifcinterface::components::TabBar* ribbon_tabs_ = nullptr;
    QStackedWidget* ribbon_pages_ = nullptr;
    ifcinterface::panels::viewport::ViewportWidget* viewport_widget_ = nullptr;
    ifcinterface::panels::viewport::ViewportController* viewport_controller_ = nullptr;
    SceneLoader* loader_ = nullptr;
    ifcinterface::ElementRegistry* element_registry_ = nullptr;
    ifcinterface::SessionState* session_state_ = nullptr;
    ifcinterface::panels::models::ModelsPanelWidget* models_panel_ = nullptr;
    ifcinterface::panels::spatial_hierarchy::SpatialHierarchyPanelWidget* spatial_panel_ = nullptr;
    QDockWidget* layers_panel_ = nullptr;
    ifcinterface::panels::properties::PropertiesPanelWidget* properties_panel_ = nullptr;
    QDockWidget* stored_views_panel_ = nullptr;
    QDockWidget* search_panel_ = nullptr;
    QDockWidget* spreadsheet_panel_ = nullptr;
    QDockWidget* audit_panel_ = nullptr;
    QDockWidget* clash_panel_ = nullptr;
    QDockWidget* issues_panel_ = nullptr;
    ifcinterface::panels::models::ModelsPanelController* models_controller_ = nullptr;
    ifcinterface::panels::models::ModelsPanelView* models_view_ = nullptr;
    ifcinterface::panels::spatial_hierarchy::SpatialHierarchyPanelView* spatial_view_ = nullptr;
    ifcinterface::panels::properties::PropertiesPanelView* properties_view_ = nullptr;
};

} // namespace ifcinterface::shell

#endif
