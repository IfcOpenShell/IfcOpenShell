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

#include "MainWindow.h"

#include "../ifcviewer/AppSettings.h"
#include "../ifcviewer/Federation.h"
#include "../ifcviewer/SceneLoader.h"
#include "../ifcviewer/ViewportWindow.h"
#include "ElementRegistry.h"
#include "SessionState.h"
#include "components/Buttons.h"
#include "components/Panel.h"
#include "components/Style.h"
#include "components/Tabs.h"
#include "modules/models/Controller.h"
#include "modules/todo/Panel.h"
#include "modules/models/View.h"
#include "modules/models/Panel.h"
#include "modules/project/Controller.h"
#include "modules/properties/View.h"
#include "modules/properties/Panel.h"
#include "modules/settings/Dialog.h"
#include "modules/spatial_hierarchy/View.h"
#include "modules/spatial_hierarchy/Panel.h"
#include "modules/viewport/Controller.h"
#include "modules/viewport/Panel.h"

#include <QDockWidget>
#include <QFileInfo>
#include <QHBoxLayout>
#include <QIcon>
#include <QLabel>
#include <QMessageBox>
#include <QShortcut>
#include <QSignalBlocker>
#include <QStackedWidget>
#include <QStatusBar>
#include <QProgressBar>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcviewerfull::shell {

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    federation_ = new Federation(this);
    element_registry_ = new ifcviewerfull::ElementRegistry(this);
    session_state_ = new ifcviewerfull::SessionState(this);
    session_state_->bindFederation(federation_);
    session_state_->bindElementRegistry(element_registry_);
    connect(federation_, &Federation::dirtyChanged, this, [this](bool dirty) {
        setWindowModified(dirty);
        updateWindowTitle();
    });
    connect(session_state_, &ifcviewerfull::SessionState::modelsChanged,
            this, &MainWindow::updateWindowTitle);
    connect(session_state_, &ifcviewerfull::SessionState::projectOpened,
            this, [this](const QString&) { updateWindowTitle(); });
    connect(session_state_, &ifcviewerfull::SessionState::projectSaved,
            this, [this](const QString&) { updateWindowTitle(); });
    connect(session_state_, &ifcviewerfull::SessionState::projectReset,
            this, &MainWindow::updateWindowTitle);
    setupChrome();
    setupViewport();
    setupPanels();
    setupStatus();
    setupLoader();
    setupRibbon();
    resize(1720, 980);
}

void MainWindow::setupChrome() {
    setObjectName("appWindow");
    setDockOptions(QMainWindow::AllowNestedDocks |
                   QMainWindow::AllowTabbedDocks |
                   QMainWindow::GroupedDragging);

    auto bind_shortcut = [this](const QKeySequence& sequence, auto fn) {
        auto* shortcut = new QShortcut(sequence, this);
        shortcut->setContext(Qt::WindowShortcut);
        connect(shortcut, &QShortcut::activated, this, fn);
    };
    bind_shortcut(QKeySequence("Ctrl+Shift+L"), [this]() {
        viewport_controller_->toggleDistanceMode();
    });
    bind_shortcut(QKeySequence("Ctrl+Shift+A"), [this]() {
        viewport_controller_->toggleAreaMode();
    });
    bind_shortcut(QKeySequence("Ctrl+Shift+V"), [this]() {
        viewport_controller_->toggleVolumeMode();
    });
    bind_shortcut(QKeySequence(Qt::SHIFT | Qt::Key_F), [this]() {
        viewport_controller_->setFlyMode();
    });
    bind_shortcut(QKeySequence(Qt::Key_K), [this]() {
        viewport_controller_->toggleSectionMode();
    });
    bind_shortcut(QKeySequence(Qt::SHIFT | Qt::Key_K), [this]() {
        viewport_controller_->clearSectionPlanes();
    });
    bind_shortcut(QKeySequence(Qt::Key_H), [this]() {
        viewport_controller_->hideSelectedElements();
    });
    bind_shortcut(QKeySequence(Qt::SHIFT | Qt::Key_H), [this]() {
        viewport_controller_->isolateSelectedElements();
    });
    bind_shortcut(QKeySequence(Qt::ALT | Qt::Key_H), [this]() {
        viewport_controller_->showAllElements();
    });
    updateWindowTitle();
}

QToolButton* MainWindow::makePanelToggle(const QString& text, QDockWidget* dock) {
    auto* button = components::buttons::makeButton(text, ":/icons/sidebar-expand.svg", this);
    button->setCheckable(true);
    button->setChecked(dock->isVisible());
    connect(button, &QToolButton::toggled, dock, [dock](bool checked) {
        dock->setVisible(checked);
        if (checked) dock->raise();
    });
    connect(dock, &QDockWidget::visibilityChanged, button, [button](bool visible) {
        const QSignalBlocker blocker(button);
        button->setChecked(visible);
    });
    return button;
}

QWidget* MainWindow::buildHomeRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(6, 4, 6, 4);
    row->setSpacing(0);

    auto* new_project = components::buttons::makeButton("New Project", ":/icons/plus-square.svg", this);
    connect(new_project, &QToolButton::clicked, this, [this]() {
        project_controller_->newProject();
    });
    auto* open_project = components::buttons::makeButton("Open Project", ":/icons/download-square.svg", this);
    connect(open_project, &QToolButton::clicked, this, [this]() {
        project_controller_->openProject();
    });
    auto* open_cloud = components::buttons::makeButton("Open Cloud", ":/icons/cloud-square.svg", this);
    connect(open_cloud, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Project", "Open Cloud Project coming soon");
    });
    auto* open_recent = components::buttons::makeButton("Open Recent", ":/icons/clock-rotate-right.svg", this);
    connect(open_recent, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Project", "Open Recent coming soon");
    });
    auto* save_project = components::buttons::makeButton("Save Project", ":/icons/floppy-disk.svg", this);
    connect(save_project, &QToolButton::clicked, this, [this]() {
        project_controller_->saveProject();
    });
    auto* save_project_as = components::buttons::makeButton("Save As", ":/icons/floppy-disk-arrow-in.svg", this);
    connect(save_project_as, &QToolButton::clicked, this, [this]() {
        project_controller_->saveProjectAs();
    });

    auto* add_model = components::buttons::makeButton("Add Model", ":/icons/cube.svg", this);
    connect(add_model, &QToolButton::clicked, this, [this]() {
        models_controller_->addFiles();
    });
    auto* sync_models = components::buttons::makeButton("Sync Models", ":/icons/refresh-double.svg", this);
    connect(sync_models, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Models", "Sync models coming soon");
    });

    auto* settings_button = components::buttons::makeButton("Settings", ":/icons/settings.svg", this);
    connect(settings_button, &QToolButton::clicked, this, [this]() {
        modules::settings::SettingsDialog dialog(this);
        dialog.exec();
    });

    row->addWidget(components::buttons::makeButtonGroup("PROJECT", {new_project, open_project, open_cloud, open_recent, save_project, save_project_as}, this));
    row->addWidget(components::buttons::makeButtonGroup("MODELS", {add_model, sync_models}, this));
    row->addWidget(components::buttons::makeButtonGroup("SETTINGS", {settings_button}, this));
    row->addStretch(1);
    return page;
}

QWidget* MainWindow::buildNavigateRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(2, 4, 2, 4);
    row->setSpacing(0);

    auto* set_home = components::buttons::makeButton("Set Home", ":/icons/home.svg", this);
    connect(set_home, &QToolButton::clicked, this, [this]() {
        viewport_controller_->setHomeView();
    });
    auto* go_home = components::buttons::makeButton("Go Home", ":/icons/home-alt.svg", this);
    connect(go_home, &QToolButton::clicked, this, [this]() {
        viewport_controller_->goHomeView();
    });
    auto* view_all = components::buttons::makeButton("View All", ":/icons/cube-scan.svg", this);
    connect(view_all, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->viewAll();
    });
    auto* view_selected = components::buttons::makeButton("View Selected", ":/icons/cube-scan-solid.svg", this);
    connect(view_selected, &QToolButton::clicked, this, [this]() {
        viewport_controller_->focusSelectedObject();
    });

    auto* plan_view = components::buttons::makeButton("Plan", ":/icons/planimetry.svg", this);
    connect(plan_view, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->setStandardView(90.0f, 90.0f);
    });
    auto* front_view = components::buttons::makeButton("Front", ":/icons/city.svg", this);
    connect(front_view, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->setStandardView(0.0f, 0.0f);
    });
    auto* side_view = components::buttons::makeButton("Side", ":/icons/building.svg", this);
    connect(side_view, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->setStandardView(90.0f, 0.0f);
    });
    auto* align_object = components::buttons::makeButton("Align Object", ":/icons/cellar.svg", this);
    connect(align_object, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Orientation", "Align to object coming soon");
    });
    auto* projection_button = components::buttons::makeButton("Perspective", ":/icons/perspective-view.svg", this);
    connect(projection_button, &QToolButton::clicked, this, [this, projection_button]() {
        if (!viewport_widget_) return;
        viewport_widget_->viewport()->toggleProjection();
        projection_button->setText(
            viewport_widget_->viewport()->projectionOrtho() ? "Ortho" : "Perspective");
    });

    auto* fly_mode = components::buttons::makeButton("Fly", ":/icons/drone.svg", this);
    connect(fly_mode, &QToolButton::clicked, this, [this]() {
        viewport_controller_->setFlyMode();
    });
    auto* section_mode = components::buttons::makeButton("Section", ":/icons/cube-cut-with-curve.svg", this);
    connect(section_mode, &QToolButton::clicked, this, [this]() {
        viewport_controller_->toggleSectionMode();
    });

    row->addWidget(components::buttons::makeButtonGroup("CAMERA", {set_home, go_home, view_all, view_selected}, this));
    row->addWidget(components::buttons::makeButtonGroup("ORIENTATION", {plan_view, front_view, side_view, align_object, projection_button}, this));
    row->addWidget(components::buttons::makeButtonGroup("MODE", {fly_mode, section_mode}, this));
    row->addStretch(1);
    return page;
}

QWidget* MainWindow::buildInspectRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(2, 4, 2, 4);
    row->setSpacing(0);

    auto* hide_selected = components::buttons::makeButton("Hide", ":/icons/eye-closed.svg", this);
    connect(hide_selected, &QToolButton::clicked, this, [this]() {
        viewport_controller_->hideSelectedElements();
    });
    auto* isolate_selected = components::buttons::makeButton("Isolate", ":/icons/eye-solid.svg", this);
    connect(isolate_selected, &QToolButton::clicked, this, [this]() {
        viewport_controller_->isolateSelectedElements();
    });
    auto* show_all = components::buttons::makeButton("Show All", ":/icons/eye.svg", this);
    connect(show_all, &QToolButton::clicked, this, [this]() {
        viewport_controller_->showAllElements();
    });
    auto* invert_selection = components::buttons::makeButton("Invert", ":/icons/intersect.svg", this);
    connect(invert_selection, &QToolButton::clicked, this, [this]() {
        viewport_controller_->invertSelection();
    });

    auto* distance = components::buttons::makeButton("Distance", ":/icons/select-edge3d.svg", this);
    connect(distance, &QToolButton::clicked, this, [this]() {
        viewport_controller_->toggleDistanceMode();
    });
    auto* area = components::buttons::makeButton("Area", ":/icons/select-face3d.svg", this);
    connect(area, &QToolButton::clicked, this, [this]() {
        viewport_controller_->toggleAreaMode();
    });
    auto* volume = components::buttons::makeButton("Volume", ":/icons/select-point3d.svg", this);
    connect(volume, &QToolButton::clicked, this, [this]() {
        viewport_controller_->toggleVolumeMode();
    });

    row->addWidget(components::buttons::makeButtonGroup("SELECTION", {hide_selected, isolate_selected, show_all, invert_selection}, this));
    row->addWidget(components::buttons::makeButtonGroup("MEASURE", {distance, area, volume}, this));
    row->addStretch(1);
    return page;
}

QWidget* MainWindow::buildPanelsRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(2, 4, 2, 4);
    row->setSpacing(0);

    row->addWidget(components::buttons::makeButtonGroup("DATA", {
        makePanelToggle("Models", models_panel_),
        makePanelToggle("Spatial", spatial_panel_),
        makePanelToggle("Layers", layers_panel_),
        makePanelToggle("Properties", properties_panel_)
    }, this));
    row->addWidget(components::buttons::makeButtonGroup("QUERY", {
        makePanelToggle("Views", stored_views_panel_),
        makePanelToggle("Search", search_panel_),
        makePanelToggle("Sheets", spreadsheet_panel_),
        makePanelToggle("Audit", audit_panel_)
    }, this));
    row->addWidget(components::buttons::makeButtonGroup("COLLABORATE", {
        makePanelToggle("Clash", clash_panel_),
        makePanelToggle("Issues", issues_panel_)
    }, this));
    row->addStretch(1);
    return page;
}

void MainWindow::setupRibbon() {
    auto* shell = new QFrame(this);

    auto* shell_layout = new QVBoxLayout(shell);
    shell_layout->setContentsMargins(0, 0, 0, 0);
    shell_layout->setSpacing(0);

    ribbon_tabs_ = new components::TabBar(shell);
    ribbon_tabs_->addTab("Home");
    ribbon_tabs_->addTab("Navigate");
    ribbon_tabs_->addTab("Inspect");
    ribbon_tabs_->addTab("Panels");
    ribbon_tabs_->setCurrentIndex(0);

    auto* ribbon_band = new QFrame(shell);
    ribbon_band->setObjectName("ribbonBand");
    auto* band_layout = new QVBoxLayout(ribbon_band);
    band_layout->setContentsMargins(0, 0, 0, 0);
    band_layout->setSpacing(0);

    ribbon_pages_ = new QStackedWidget(ribbon_band);
    ribbon_pages_->addWidget(buildHomeRibbonPage());
    ribbon_pages_->addWidget(buildNavigateRibbonPage());
    ribbon_pages_->addWidget(buildInspectRibbonPage());
    ribbon_pages_->addWidget(buildPanelsRibbonPage());

    band_layout->addWidget(ribbon_pages_);
    shell_layout->addWidget(ribbon_tabs_);
    shell_layout->addWidget(ribbon_band);

    connect(ribbon_tabs_, &components::TabBar::currentChanged,
            ribbon_pages_, &QStackedWidget::setCurrentIndex);

    setMenuWidget(shell);
}

void MainWindow::setupViewport() {
    viewport_widget_ = new modules::viewport::ViewportPanel(this);
    setCentralWidget(viewport_widget_);
}

void MainWindow::setupPanels() {
    models_panel_ = new modules::models::ModelsPanel(this);
    spatial_panel_ = new modules::spatial_hierarchy::SpatialHierarchyPanel(this);
    properties_panel_ = new modules::properties::PropertiesPanel(this);

    models_controller_ = new modules::models::ModelsPanelController(
        this, models_panel_, session_state_, viewport_widget_->viewport(), this);
    models_view_ = new modules::models::ModelsPanelView(models_panel_, session_state_, this);
    spatial_view_ = new modules::spatial_hierarchy::SpatialHierarchyPanelView(spatial_panel_, session_state_, this);
    properties_view_ = new modules::properties::PropertiesPanelView(properties_panel_, session_state_, this);

    layers_panel_ = new components::Panel("Layers", new modules::todo::TodoPanel("Layers", this), this);
    stored_views_panel_ = new components::Panel(
        "Stored Views", new modules::todo::TodoPanel("Stored Views", this), this);
    search_panel_ = new components::Panel(
        "Search and Query", new modules::todo::TodoPanel("Search and Query", this), this);
    spreadsheet_panel_ = new components::Panel(
        "Spreadsheet", new modules::todo::TodoPanel("Spreadsheet", this), this);
    audit_panel_ = new components::Panel("Audit", new modules::todo::TodoPanel("Audit", this), this);
    clash_panel_ = new components::Panel("Clash", new modules::todo::TodoPanel("Clash", this), this);
    issues_panel_ = new components::Panel("Issues", new modules::todo::TodoPanel("Issues", this), this);

    addDockWidget(Qt::LeftDockWidgetArea, models_panel_);
    addDockWidget(Qt::LeftDockWidgetArea, spatial_panel_);
    splitDockWidget(models_panel_, spatial_panel_, Qt::Vertical);

    addDockWidget(Qt::RightDockWidgetArea, properties_panel_);
    addDockWidget(Qt::RightDockWidgetArea, layers_panel_);
    addDockWidget(Qt::RightDockWidgetArea, stored_views_panel_);
    addDockWidget(Qt::RightDockWidgetArea, search_panel_);
    addDockWidget(Qt::RightDockWidgetArea, spreadsheet_panel_);
    addDockWidget(Qt::RightDockWidgetArea, audit_panel_);
    addDockWidget(Qt::RightDockWidgetArea, clash_panel_);
    addDockWidget(Qt::RightDockWidgetArea, issues_panel_);

    tabifyDockWidget(properties_panel_, layers_panel_);
    tabifyDockWidget(layers_panel_, stored_views_panel_);
    tabifyDockWidget(stored_views_panel_, search_panel_);
    tabifyDockWidget(search_panel_, spreadsheet_panel_);
    tabifyDockWidget(spreadsheet_panel_, audit_panel_);
    tabifyDockWidget(audit_panel_, clash_panel_);
    tabifyDockWidget(clash_panel_, issues_panel_);
    properties_panel_->raise();

    layers_panel_->hide();
    stored_views_panel_->hide();
    search_panel_->hide();
    spreadsheet_panel_->hide();
    audit_panel_->hide();
    clash_panel_->hide();
    issues_panel_->hide();

    resizeDocks({models_panel_, properties_panel_}, {290, 330}, Qt::Horizontal);
    resizeDocks({models_panel_, spatial_panel_}, {280, 240}, Qt::Vertical);
}

void MainWindow::setupStatus() {
    status_mode_label_ = new QLabel("Ready", this);
    status_selection_label_ = new QLabel("No selection", this);
    status_perf_label_ = new QLabel(this);
    status_progress_bar_ = new QProgressBar(this);
    status_perf_label_->setVisible(AppSettings::instance().showStats());
    status_progress_bar_->setMaximumWidth(200);
    status_progress_bar_->setVisible(false);

    statusBar()->setSizeGripEnabled(false);
    statusBar()->addWidget(status_mode_label_);
    statusBar()->addWidget(status_selection_label_, 1);
    statusBar()->addPermanentWidget(status_perf_label_);
    statusBar()->addPermanentWidget(status_progress_bar_);

    connect(&AppSettings::instance(), &AppSettings::showStatsChanged, this, [this](bool show) {
        status_perf_label_->setVisible(show);
        if (!show) status_perf_label_->clear();
    });
    connect(session_state_, &ifcviewerfull::SessionState::statusMessageChanged,
            this, [this](const QString& mode, const QString& detail) {
        status_mode_label_->setText(mode);
        status_selection_label_->setText(detail);
    });
    session_state_->setStatusMessage("Ready", "No selection");
}

void MainWindow::setupLoader() {
    loader_ = new SceneLoader(viewport_widget_->viewport(), this);
    element_registry_->bindLoader(loader_);
    session_state_->bindLoader(loader_);
    models_controller_->bindLoader(loader_);
    viewport_controller_ = new modules::viewport::ViewportController(
        session_state_, viewport_widget_->viewport(), this);
    project_controller_ = new modules::project::ProjectController(
        this, federation_, session_state_, element_registry_,
        viewport_widget_->viewport(), models_controller_, viewport_controller_, this);

    connect(loader_, &SceneLoader::loadStarted, this,
            [this](uint32_t /*mid*/, const QString& /*display_name*/) {
        status_progress_bar_->setValue(0);
        status_progress_bar_->setVisible(true);
    });
    connect(loader_, &SceneLoader::progressChanged, this,
            [this](int percent) {
        status_progress_bar_->setValue(percent);
    });

    auto hide_progress = [this]() {
        status_progress_bar_->setVisible(false);
    };
    connect(loader_, &SceneLoader::loadedFromSidecar, this,
            [hide_progress](uint32_t /*mid*/, qint64 /*elapsed_ms*/) {
        hide_progress();
    });
    connect(loader_, &SceneLoader::loadedFromStream, this,
            [hide_progress](uint32_t /*mid*/, qint64 /*elapsed_ms*/) {
        hide_progress();
    });
    connect(loader_, &SceneLoader::loadCancelled, this,
            [hide_progress](uint32_t /*mid*/) {
        hide_progress();
    });
    connect(loader_, &SceneLoader::loadError, this,
            [hide_progress](uint32_t /*mid*/, const QString& /*message*/) {
        hide_progress();
    });

    connect(viewport_widget_->viewport(), &ViewportWindow::frameStatsUpdated, this,
            [this](const ViewportWindow::FrameStats& s) {
        if (!status_perf_label_->isVisible()) return;
        status_perf_label_->setText(
            QString("%1 fps | %2 ms | %3/%4 obj | %5/%6 tri | %7 draws")
                .arg(s.fps, 0, 'f', 1)
                .arg(s.frame_time_ms, 0, 'f', 1)
                .arg(s.visible_objects)
                .arg(s.total_objects)
                .arg(s.visible_triangles)
                .arg(s.total_triangles)
                .arg(s.gl_draw_calls));
    });
    connect(viewport_widget_->viewport(), &ViewportWindow::objectPicked,
            this, [this](uint32_t object_id) {
        session_state_->setSelectedObjectId(object_id);
        session_state_->notifySelectionChanged();
    });
}

void MainWindow::updateWindowTitle() {
    const QString project_path = federation_ ? federation_->filePath() : QString();
    if (project_path.isEmpty() && (!federation_ || federation_->models().empty())) {
        setWindowTitle("IfcOpenShell Interface");
    } else if (project_path.isEmpty()) {
        setWindowTitle("untitled[*] - IfcOpenShell Interface");
    } else {
        setWindowTitle(QFileInfo(project_path).fileName() + "[*] - IfcOpenShell Interface");
    }
}

} // namespace ifcviewerfull::shell
