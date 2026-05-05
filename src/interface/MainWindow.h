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

#include <QMainWindow>
#include <QStringList>

class QLabel;
class QDockWidget;
class QStackedWidget;
class QTabBar;
class QToolButton;
class ViewportWindow;
class SceneLoader;
namespace ifcinterface::panels::models { class ModelsPanelView; }
namespace ifcinterface::panels::spatial_hierarchy { class SpatialHierarchyPanelView; }
namespace ifcinterface::panels::properties { class PropertiesPanelView; }

namespace ifcinterface::shell {

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget* parent = nullptr);

private:
    void setupChrome();
    void setupRibbon();
    void setupViewport();
    void setupDocks();
    void setupStatus();
    void setupLoader();
    QWidget* buildHomeRibbonPage();
    QWidget* buildNavigateRibbonPage();
    QWidget* buildInspectRibbonPage();
    QWidget* buildPanelsRibbonPage();
    QToolButton* makeRibbonAction(const QString& text, const QString& icon_path);
    QWidget* makeRibbonGroup(const QString& title, const QList<QToolButton*>& buttons);
    QWidget* makeComingSoonPanel(const QString& title);
    QToolButton* makePanelToggle(const QString& text, QDockWidget* dock);
    void setStatusMessage(const QString& mode, const QString& detail);
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

private:
    QLabel* status_mode_label_ = nullptr;
    QLabel* status_selection_label_ = nullptr;
    QLabel* status_perf_label_ = nullptr;
    QTabBar* ribbon_tabs_ = nullptr;
    QStackedWidget* ribbon_pages_ = nullptr;
    ViewportWindow* viewport_ = nullptr;
    SceneLoader* loader_ = nullptr;
    QWidget* viewport_container_ = nullptr;
    QDockWidget* models_dock_ = nullptr;
    QDockWidget* spatial_dock_ = nullptr;
    QDockWidget* layers_dock_ = nullptr;
    QDockWidget* properties_dock_ = nullptr;
    QDockWidget* stored_views_dock_ = nullptr;
    QDockWidget* search_dock_ = nullptr;
    QDockWidget* spreadsheet_dock_ = nullptr;
    QDockWidget* clash_dock_ = nullptr;
    QDockWidget* issues_dock_ = nullptr;
    ifcinterface::panels::models::ModelsPanelView* models_panel_view_ = nullptr;
    ifcinterface::panels::spatial_hierarchy::SpatialHierarchyPanelView* spatial_panel_view_ = nullptr;
    ifcinterface::panels::properties::PropertiesPanelView* properties_panel_view_ = nullptr;
};

} // namespace ifcinterface::shell

#endif
