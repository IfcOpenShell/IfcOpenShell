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
#include "../ifcviewer/SceneLoader.h"
#include "../ifcviewer/ViewportWindow.h"
#include "ElementRegistry.h"
#include "components/Panel.h"
#include "components/Style.h"
#include "components/SvgIcon.h"
#include "panels/todo/TodoPanelWidget.h"
#include "panels/models/ModelsPanelView.h"
#include "panels/models/ModelsPanelWidget.h"
#include "panels/properties/PropertiesPanelView.h"
#include "panels/properties/PropertiesPanelWidget.h"
#include "panels/spatial_hierarchy/SpatialHierarchyPanelView.h"
#include "panels/spatial_hierarchy/SpatialHierarchyPanelWidget.h"

#include <QDockWidget>
#include <QFileDialog>
#include <QFrame>
#include <QHBoxLayout>
#include <QIcon>
#include <QLabel>
#include <QMessageBox>
#include <QSignalBlocker>
#include <QStackedWidget>
#include <QStatusBar>
#include <QTabBar>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcinterface::shell {

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    element_registry_ = new ifcinterface::ElementRegistry(this);
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
    setWindowTitle("IfcOpenShell Interface");
    setDockOptions(QMainWindow::AllowNestedDocks |
                   QMainWindow::AllowTabbedDocks |
                   QMainWindow::GroupedDragging);
    setStyleSheet(components::style::buildAppStyleSheet());
}

QToolButton* MainWindow::makeRibbonAction(const QString& text, const QString& icon_path) {
    auto* button = new QToolButton(this);
    button->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    button->setIcon(icon_path.endsWith(".svg")
                        ? components::icons::makeTintedSvgIcon(icon_path)
                        : QIcon(icon_path));
    button->setIconSize(QSize(20, 20));
    button->setText(text);
    button->setMinimumSize(QSize(68, 54));
    button->setObjectName("ribbonButton");
    button->setAutoRaise(false);
    return button;
}

QWidget* MainWindow::makeRibbonGroup(const QString& title, const QList<QToolButton*>& buttons) {
    auto* group = new QFrame(this);
    group->setObjectName("ribbonGroup");
    auto* group_layout = new QVBoxLayout(group);
    group_layout->setContentsMargins(8, 6, 8, 4);
    group_layout->setSpacing(4);
    auto* button_row = new QHBoxLayout();
    button_row->setContentsMargins(0, 0, 0, 0);
    button_row->setSpacing(4);
    for (auto* button : buttons) {
        button_row->addWidget(button);
    }
    auto* label = new QLabel(title, group);
    label->setObjectName("ribbonGroupLabel");
    label->setProperty("textRole", "secondary");
    label->setAlignment(Qt::AlignCenter);
    group_layout->addLayout(button_row);
    group_layout->addWidget(label);
    return group;
}

void MainWindow::setStatusMessage(const QString& mode, const QString& detail) {
    status_mode_label_->setText(mode);
    status_selection_label_->setText(detail);
}

QToolButton* MainWindow::makePanelToggle(const QString& text, QDockWidget* dock) {
    auto* button = makeRibbonAction(text, ":/icons/sidebar-expand.svg");
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

    auto* new_project = makeRibbonAction("New Project", ":/icons/plus-square.svg");
    connect(new_project, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Project", "New Project coming soon");
    });
    auto* open_project = makeRibbonAction("Open Project", ":/icons/download-square.svg");
    connect(open_project, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Project", "Open Project coming soon");
    });
    auto* open_cloud = makeRibbonAction("Open Cloud", ":/icons/cloud-square.svg");
    connect(open_cloud, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Project", "Open Cloud Project coming soon");
    });
    auto* open_recent = makeRibbonAction("Open Recent", ":/icons/clock-rotate-right.svg");
    connect(open_recent, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Project", "Open Recent coming soon");
    });
    auto* save_project = makeRibbonAction("Save Project", ":/icons/floppy-disk.svg");
    connect(save_project, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Project", "Save Project coming soon");
    });
    auto* save_project_as = makeRibbonAction("Save As", ":/icons/floppy-disk-arrow-in.svg");
    connect(save_project_as, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Project", "Save Project As coming soon");
    });

    auto* add_model = makeRibbonAction("Add Model", ":/icons/cube.svg");
    connect(add_model, &QToolButton::clicked, this, &MainWindow::onAddFiles);
    auto* sync_models = makeRibbonAction("Sync Models", ":/icons/refresh-double.svg");
    connect(sync_models, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Models", "Sync models coming soon");
    });

    auto* settings_button = makeRibbonAction("Settings", ":/icons/settings.svg");
    connect(settings_button, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Settings", "Settings coming soon");
    });

    row->addWidget(makeRibbonGroup("PROJECT", {new_project, open_project, open_cloud, open_recent, save_project, save_project_as}));
    row->addWidget(makeRibbonGroup("MODELS", {add_model, sync_models}));
    row->addWidget(makeRibbonGroup("SETTINGS", {settings_button}));
    row->addStretch(1);
    return page;
}

QWidget* MainWindow::buildNavigateRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(2, 4, 2, 4);
    row->setSpacing(0);

    auto* set_home = makeRibbonAction("Set Home", ":/icons/home.svg");
    connect(set_home, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Camera", "Set home view coming soon");
    });
    auto* go_home = makeRibbonAction("Go Home", ":/icons/home-alt.svg");
    connect(go_home, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Camera", "Go to home view coming soon");
    });
    auto* view_all = makeRibbonAction("View All", ":/icons/cube-scan.svg");
    connect(view_all, &QToolButton::clicked, this, [this]() {
        if (viewport_) viewport_->viewAll();
    });
    auto* view_selected = makeRibbonAction("View Selected", ":/icons/cube-scan-solid.svg");
    connect(view_selected, &QToolButton::clicked, this, [this]() {
        if (viewport_) viewport_->focusOnSelectedObject();
    });

    auto* plan_view = makeRibbonAction("Plan", ":/icons/planimetry.svg");
    connect(plan_view, &QToolButton::clicked, this, [this]() {
        if (viewport_) viewport_->setStandardView(90.0f, 90.0f);
    });
    auto* front_view = makeRibbonAction("Front", ":/icons/city.svg");
    connect(front_view, &QToolButton::clicked, this, [this]() {
        if (viewport_) viewport_->setStandardView(0.0f, 0.0f);
    });
    auto* side_view = makeRibbonAction("Side", ":/icons/building.svg");
    connect(side_view, &QToolButton::clicked, this, [this]() {
        if (viewport_) viewport_->setStandardView(90.0f, 0.0f);
    });
    auto* align_object = makeRibbonAction("Align Object", ":/icons/cellar.svg");
    connect(align_object, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Orientation", "Align to object coming soon");
    });
    auto* projection_button = makeRibbonAction("Perspective", ":/icons/perspective-view.svg");
    connect(projection_button, &QToolButton::clicked, this, [this, projection_button]() {
        if (!viewport_) return;
        viewport_->toggleProjection();
        projection_button->setText(viewport_->projectionOrtho() ? "Ortho" : "Perspective");
    });

    auto* orbit_mode = makeRibbonAction("Orbit", ":/icons/rotate-camera-right.svg");
    connect(orbit_mode, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Mode", "Orbit mode active");
    });
    auto* fly_mode = makeRibbonAction("Fly", ":/icons/drone.svg");
    connect(fly_mode, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Mode", "Fly mode coming soon");
    });

    row->addWidget(makeRibbonGroup("CAMERA", {set_home, go_home, view_all, view_selected}));
    row->addWidget(makeRibbonGroup("ORIENTATION", {plan_view, front_view, side_view, align_object, projection_button}));
    row->addWidget(makeRibbonGroup("MODE", {orbit_mode, fly_mode}));
    row->addStretch(1);
    return page;
}

QWidget* MainWindow::buildInspectRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(2, 4, 2, 4);
    row->setSpacing(0);

    auto* hide_selected = makeRibbonAction("Hide", ":/icons/eye-closed.svg");
    connect(hide_selected, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Selection", "Hide selected coming soon");
    });
    auto* isolate_selected = makeRibbonAction("Isolate", ":/icons/eye-solid.svg");
    connect(isolate_selected, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Selection", "Isolate selected coming soon");
    });
    auto* show_all = makeRibbonAction("Show All", ":/icons/eye.svg");
    connect(show_all, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Selection", "Show all coming soon");
    });
    auto* invert_selection = makeRibbonAction("Invert", ":/icons/intersect.svg");
    connect(invert_selection, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Selection", "Invert selection coming soon");
    });

    auto* distance = makeRibbonAction("Distance", ":/icons/select-edge3d.svg");
    connect(distance, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Measure", "Distance coming soon");
    });
    auto* area = makeRibbonAction("Area", ":/icons/select-face3d.svg");
    connect(area, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Measure", "Area coming soon");
    });
    auto* volume = makeRibbonAction("Volume", ":/icons/select-point3d.svg");
    connect(volume, &QToolButton::clicked, this, [this]() {
        setStatusMessage("Measure", "Volume coming soon");
    });

    row->addWidget(makeRibbonGroup("SELECTION", {hide_selected, isolate_selected, show_all, invert_selection}));
    row->addWidget(makeRibbonGroup("MEASURE", {distance, area, volume}));
    row->addStretch(1);
    return page;
}

QWidget* MainWindow::buildPanelsRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(2, 4, 2, 4);
    row->setSpacing(0);

    row->addWidget(makeRibbonGroup("DATA", {
        makePanelToggle("Models", models_panel_),
        makePanelToggle("Spatial", spatial_panel_),
        makePanelToggle("Layers", layers_panel_),
        makePanelToggle("Properties", properties_panel_)
    }));
    row->addWidget(makeRibbonGroup("QUERY", {
        makePanelToggle("Views", stored_views_panel_),
        makePanelToggle("Search", search_panel_),
        makePanelToggle("Sheets", spreadsheet_panel_),
        makePanelToggle("Audit", audit_panel_)
    }));
    row->addWidget(makeRibbonGroup("COLLABORATE", {
        makePanelToggle("Clash", clash_panel_),
        makePanelToggle("Issues", issues_panel_)
    }));
    row->addStretch(1);
    return page;
}

void MainWindow::setupRibbon() {
    auto* shell = new QFrame(this);
    shell->setObjectName("ribbonShell");

    auto* shell_layout = new QVBoxLayout(shell);
    shell_layout->setContentsMargins(0, 0, 0, 0);
    shell_layout->setSpacing(0);

    ribbon_tabs_ = new QTabBar(shell);
    ribbon_tabs_->addTab("Home");
    ribbon_tabs_->addTab("Navigate");
    ribbon_tabs_->addTab("Inspect");
    ribbon_tabs_->addTab("Panels");
    ribbon_tabs_->setCurrentIndex(0);
    ribbon_tabs_->setExpanding(false);
    ribbon_tabs_->setDrawBase(false);

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

    connect(ribbon_tabs_, &QTabBar::currentChanged,
            ribbon_pages_, &QStackedWidget::setCurrentIndex);

    setMenuWidget(shell);
}

void MainWindow::setupViewport() {
    viewport_ = new ViewportWindow();
    viewport_container_ = QWidget::createWindowContainer(viewport_, this);
    viewport_container_->setMinimumSize(400, 300);
    viewport_container_->setFocusPolicy(Qt::StrongFocus);

    auto* shell = new QFrame(this);
    shell->setObjectName("viewportShell");
    auto* root = new QVBoxLayout(shell);
    root->setContentsMargins(10, 10, 10, 10);
    root->setSpacing(0);

    auto* frame = new QFrame(shell);
    frame->setObjectName("viewportFrame");
    auto* frame_layout = new QVBoxLayout(frame);
    frame_layout->setContentsMargins(0, 0, 0, 0);
    frame_layout->addWidget(viewport_container_);

    root->addWidget(frame);
    setCentralWidget(shell);
}

void MainWindow::setupPanels() {
    auto* models_widget = new panels::models::ModelsPanelWidget(this);
    auto* spatial_widget = new panels::spatial_hierarchy::SpatialHierarchyPanelWidget(this);
    auto* properties_widget = new panels::properties::PropertiesPanelWidget(this);

    models_view_ = new panels::models::ModelsPanelView(models_widget, this);
    spatial_view_ = new panels::spatial_hierarchy::SpatialHierarchyPanelView(spatial_widget, this);
    properties_view_ = new panels::properties::PropertiesPanelView(
        properties_widget, viewport_, element_registry_, this);

    connect(models_view_, &panels::models::ModelsPanelView::statusMessageRequested,
            this, &MainWindow::setStatusMessage);
    connect(spatial_view_, &panels::spatial_hierarchy::SpatialHierarchyPanelView::statusMessageRequested,
            this, &MainWindow::setStatusMessage);

    models_panel_ = new components::Panel("Models", models_widget, this, true);
    spatial_panel_ = new components::Panel("Spatial Hierarchy", spatial_widget, this);
    properties_panel_ = new components::Panel("Properties", properties_widget, this, false, true);
    layers_panel_ = new components::Panel("Layers", new panels::todo::TodoPanelWidget("Layers", this), this);
    stored_views_panel_ = new components::Panel(
        "Stored Views", new panels::todo::TodoPanelWidget("Stored Views", this), this);
    search_panel_ = new components::Panel(
        "Search and Query", new panels::todo::TodoPanelWidget("Search and Query", this), this);
    spreadsheet_panel_ = new components::Panel(
        "Spreadsheet", new panels::todo::TodoPanelWidget("Spreadsheet", this), this);
    audit_panel_ = new components::Panel("Audit", new panels::todo::TodoPanelWidget("Audit", this), this);
    clash_panel_ = new components::Panel("Clash", new panels::todo::TodoPanelWidget("Clash", this), this);
    issues_panel_ = new components::Panel("Issues", new panels::todo::TodoPanelWidget("Issues", this), this);

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
    status_perf_label_->setVisible(AppSettings::instance().showStats());

    statusBar()->setSizeGripEnabled(false);
    statusBar()->addWidget(status_mode_label_);
    statusBar()->addWidget(status_selection_label_, 1);
    statusBar()->addPermanentWidget(status_perf_label_);

    connect(&AppSettings::instance(), &AppSettings::showStatsChanged, this, [this](bool show) {
        status_perf_label_->setVisible(show);
        if (!show) status_perf_label_->clear();
    });
}

void MainWindow::setupLoader() {
    AppSettings::instance().setLoadDataSource(false);
    loader_ = new SceneLoader(viewport_, this);
    element_registry_->bindLoader(loader_);
    connect(loader_, &SceneLoader::loadStarted, this, &MainWindow::onLoadStarted);
    connect(loader_, &SceneLoader::loadedFromSidecar, this, &MainWindow::onLoadedFromSidecar);
    connect(loader_, &SceneLoader::loadedFromStream, this, &MainWindow::onLoadedFromStream);
    connect(loader_, &SceneLoader::loadCancelled, this, &MainWindow::onLoadCancelled);
    connect(loader_, &SceneLoader::loadError, this, &MainWindow::onLoadError);
    connect(loader_, &SceneLoader::allLoadsFinished, this, &MainWindow::onAllLoadsFinished);

    connect(viewport_, &ViewportWindow::frameStatsUpdated, this,
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
}

void MainWindow::addFiles(const QStringList& paths) {
    if (paths.isEmpty()) return;
    loader_->addFiles(paths);
}

QString MainWindow::formatElapsed(qint64 ms) const {
    return (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
}

void MainWindow::onAddFiles() {
    const QStringList paths = QFileDialog::getOpenFileNames(
        this, "Add IFC Files", QString(),
        "IFC Viewer Cache (*.ifcview)");
    addFiles(paths);
}

void MainWindow::onLoadStarted(uint32_t /*mid*/, QString display_name) {
    status_mode_label_->setText("Loading");
    status_selection_label_->setText(display_name);
}

void MainWindow::onLoadedFromSidecar(uint32_t mid, qint64 elapsed_ms) {
    status_mode_label_->setText("Loaded");
    status_selection_label_->setText(
        QString("%1 from cache in %2")
            .arg(loader_->displayName(mid))
            .arg(formatElapsed(elapsed_ms)));
}

void MainWindow::onLoadedFromStream(uint32_t mid, qint64 elapsed_ms) {
    status_mode_label_->setText("Loaded");
    status_selection_label_->setText(
        QString("%1 streamed in %2")
            .arg(loader_->displayName(mid))
            .arg(formatElapsed(elapsed_ms)));
}

void MainWindow::onLoadCancelled(uint32_t mid) {
    status_mode_label_->setText("Cancelled");
    status_selection_label_->setText(loader_->displayName(mid));
}

void MainWindow::onLoadError(uint32_t /*mid*/, QString message) {
    status_mode_label_->setText("Error");
    status_selection_label_->setText(message);
    QMessageBox::warning(this, "IfcInterfaceMockup", message);
}

void MainWindow::onAllLoadsFinished() {
    status_mode_label_->setText("Loaded");
    status_selection_label_->setText(QString("%1 model(s)").arg(loader_->modelCount()));
}

} // namespace ifcinterface::shell
