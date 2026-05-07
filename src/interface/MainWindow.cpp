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
#include "panels/add_model/Dialog.h"
#include "panels/models/Controller.h"
#include "panels/todo/Widget.h"
#include "panels/models/View.h"
#include "panels/models/Widget.h"
#include "panels/properties/View.h"
#include "panels/properties/Widget.h"
#include "panels/settings/Dialog.h"
#include "panels/spatial_hierarchy/View.h"
#include "panels/spatial_hierarchy/Widget.h"
#include "panels/viewport/Controller.h"
#include "panels/viewport/Widget.h"

#include <QDockWidget>
#include <QFileDialog>
#include <QFileInfo>
#include <QHBoxLayout>
#include <QIcon>
#include <QLabel>
#include <QListView>
#include <QMessageBox>
#include <QSignalBlocker>
#include <QStackedWidget>
#include <QStatusBar>
#include <QTreeView>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcinterface::shell {

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    federation_ = new Federation(this);
    element_registry_ = new ifcinterface::ElementRegistry(this);
    session_state_ = new ifcinterface::SessionState(this);
    session_state_->bindFederation(federation_);
    session_state_->bindElementRegistry(element_registry_);
    connect(federation_, &Federation::dirtyChanged, this, [this](bool dirty) {
        setWindowModified(dirty);
        updateWindowTitle();
    });
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
    updateWindowTitle();
}

QToolButton* MainWindow::makeRibbonAction(const QString& text, const QString& icon_path) {
    return components::buttons::makeButton(text, icon_path, this, QSize(90, 54));
}

QWidget* MainWindow::makeRibbonGroup(const QString& title, const QList<QToolButton*>& buttons) {
    return components::buttons::makeButtonGroup(title, buttons, this);
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
    connect(new_project, &QToolButton::clicked, this, &MainWindow::onNewProject);
    auto* open_project = makeRibbonAction("Open Project", ":/icons/download-square.svg");
    connect(open_project, &QToolButton::clicked, this, &MainWindow::onOpenProject);
    auto* open_cloud = makeRibbonAction("Open Cloud", ":/icons/cloud-square.svg");
    connect(open_cloud, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Project", "Open Cloud Project coming soon");
    });
    auto* open_recent = makeRibbonAction("Open Recent", ":/icons/clock-rotate-right.svg");
    connect(open_recent, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Project", "Open Recent coming soon");
    });
    auto* save_project = makeRibbonAction("Save Project", ":/icons/floppy-disk.svg");
    connect(save_project, &QToolButton::clicked, this, &MainWindow::onSaveProject);
    auto* save_project_as = makeRibbonAction("Save As", ":/icons/floppy-disk-arrow-in.svg");
    connect(save_project_as, &QToolButton::clicked, this, &MainWindow::onSaveProjectAs);

    auto* add_model = makeRibbonAction("Add Model", ":/icons/cube.svg");
    connect(add_model, &QToolButton::clicked, this, &MainWindow::onAddFiles);
    auto* sync_models = makeRibbonAction("Sync Models", ":/icons/refresh-double.svg");
    connect(sync_models, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Models", "Sync models coming soon");
    });

    auto* settings_button = makeRibbonAction("Settings", ":/icons/settings.svg");
    connect(settings_button, &QToolButton::clicked, this, [this]() {
        panels::settings::SettingsDialog dialog(this);
        dialog.exec();
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
    connect(set_home, &QToolButton::clicked, this, &MainWindow::onSetHomeView);
    auto* go_home = makeRibbonAction("Go Home", ":/icons/home-alt.svg");
    connect(go_home, &QToolButton::clicked, this, &MainWindow::onGoHomeView);
    auto* view_all = makeRibbonAction("View All", ":/icons/cube-scan.svg");
    connect(view_all, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->viewAll();
    });
    auto* view_selected = makeRibbonAction("View Selected", ":/icons/cube-scan-solid.svg");
    connect(view_selected, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->focusOnSelectedObject();
    });

    auto* plan_view = makeRibbonAction("Plan", ":/icons/planimetry.svg");
    connect(plan_view, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->setStandardView(90.0f, 90.0f);
    });
    auto* front_view = makeRibbonAction("Front", ":/icons/city.svg");
    connect(front_view, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->setStandardView(0.0f, 0.0f);
    });
    auto* side_view = makeRibbonAction("Side", ":/icons/building.svg");
    connect(side_view, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->setStandardView(90.0f, 0.0f);
    });
    auto* align_object = makeRibbonAction("Align Object", ":/icons/cellar.svg");
    connect(align_object, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Orientation", "Align to object coming soon");
    });
    auto* projection_button = makeRibbonAction("Perspective", ":/icons/perspective-view.svg");
    connect(projection_button, &QToolButton::clicked, this, [this, projection_button]() {
        if (!viewport_widget_) return;
        viewport_widget_->viewport()->toggleProjection();
        projection_button->setText(
            viewport_widget_->viewport()->projectionOrtho() ? "Ortho" : "Perspective");
    });

    auto* orbit_mode = makeRibbonAction("Orbit", ":/icons/rotate-camera-right.svg");
    connect(orbit_mode, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Mode", "Orbit mode active");
    });
    auto* fly_mode = makeRibbonAction("Fly", ":/icons/drone.svg");
    connect(fly_mode, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Mode", "Fly mode coming soon");
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
        session_state_->setStatusMessage("Selection", "Hide selected coming soon");
    });
    auto* isolate_selected = makeRibbonAction("Isolate", ":/icons/eye-solid.svg");
    connect(isolate_selected, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Selection", "Isolate selected coming soon");
    });
    auto* show_all = makeRibbonAction("Show All", ":/icons/eye.svg");
    connect(show_all, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Selection", "Show all coming soon");
    });
    auto* invert_selection = makeRibbonAction("Invert", ":/icons/intersect.svg");
    connect(invert_selection, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Selection", "Invert selection coming soon");
    });

    auto* distance = makeRibbonAction("Distance", ":/icons/select-edge3d.svg");
    connect(distance, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Measure", "Distance coming soon");
    });
    auto* area = makeRibbonAction("Area", ":/icons/select-face3d.svg");
    connect(area, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Measure", "Area coming soon");
    });
    auto* volume = makeRibbonAction("Volume", ":/icons/select-point3d.svg");
    connect(volume, &QToolButton::clicked, this, [this]() {
        session_state_->setStatusMessage("Measure", "Volume coming soon");
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
    viewport_widget_ = new panels::viewport::ViewportWidget(this);
    setCentralWidget(viewport_widget_);
}

void MainWindow::setupPanels() {
    models_panel_ = new panels::models::ModelsPanelWidget(this);
    spatial_panel_ = new panels::spatial_hierarchy::SpatialHierarchyPanelWidget(this);
    properties_panel_ = new panels::properties::PropertiesPanelWidget(this);

    models_controller_ = new panels::models::ModelsPanelController(
        models_panel_, session_state_, viewport_widget_->viewport(), element_registry_, this);
    models_view_ = new panels::models::ModelsPanelView(models_panel_, session_state_, this);
    spatial_view_ = new panels::spatial_hierarchy::SpatialHierarchyPanelView(spatial_panel_, session_state_, this);
    properties_view_ = new panels::properties::PropertiesPanelView(properties_panel_, session_state_, this);

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
    connect(session_state_, &ifcinterface::SessionState::statusMessageChanged,
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
    viewport_controller_ = new panels::viewport::ViewportController(
        session_state_, viewport_widget_->viewport(), this);
    connect(loader_, &SceneLoader::loadStarted, this, &MainWindow::onLoadStarted);
    connect(loader_, &SceneLoader::loadedFromSidecar, this, &MainWindow::onLoadedFromSidecar);
    connect(loader_, &SceneLoader::loadedFromStream, this, &MainWindow::onLoadedFromStream);
    connect(loader_, &SceneLoader::loadCancelled, this, &MainWindow::onLoadCancelled);
    connect(loader_, &SceneLoader::loadError, this, &MainWindow::onLoadError);
    connect(loader_, &SceneLoader::allLoadsFinished, this, &MainWindow::onAllLoadsFinished);

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

void MainWindow::addFiles(const QStringList& paths) {
    QStringList accepted_paths;
    QStringList accepted_fed_ids;
    for (const auto& path : paths) {
        const QString fed_id = federation_->addModel(path);
        if (fed_id.isEmpty()) continue;
        accepted_paths << path;
        accepted_fed_ids << fed_id;
    }
    loadModelsFromPaths(accepted_paths, accepted_fed_ids);
    updateWindowTitle();
}

QString MainWindow::formatElapsed(qint64 ms) const {
    return (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
}

void MainWindow::onAddFiles() {
    panels::add_model::AddModelDialog dialog(this);
    if (dialog.exec() != QDialog::Accepted) return;

    QStringList paths;
    switch (dialog.selectedMode()) {
    case panels::add_model::SourceMode::IfcFile: {
        QFileDialog file_dialog(this, "Add IFC Files");
        file_dialog.setFileMode(QFileDialog::ExistingFiles);
        file_dialog.setNameFilter("IFC Files (*.ifc);;All Files (*)");
        file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
        if (file_dialog.exec() == QDialog::Accepted) {
            paths = file_dialog.selectedFiles();
        }
        break;
    }
    case panels::add_model::SourceMode::IfcDatabase: {
        QFileDialog database_dialog(this, "Add IFC Databases");
        database_dialog.setFileMode(QFileDialog::Directory);
        database_dialog.setOption(QFileDialog::ShowDirsOnly, true);
        database_dialog.setOption(QFileDialog::DontResolveSymlinks, true);
        database_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
        if (auto* list = database_dialog.findChild<QListView*>("listView")) {
            list->setSelectionMode(QAbstractItemView::ExtendedSelection);
        }
        if (auto* tree = database_dialog.findChild<QTreeView*>()) {
            tree->setSelectionMode(QAbstractItemView::ExtendedSelection);
        }
        if (database_dialog.exec() == QDialog::Accepted) {
            paths = database_dialog.selectedFiles();
        }
        break;
    }
    case panels::add_model::SourceMode::GeometryOnly: {
        QFileDialog file_dialog(this, "Add Geometry Only");
        file_dialog.setFileMode(QFileDialog::ExistingFiles);
        file_dialog.setNameFilter("IFC Viewer Cache (*.ifcview);;All Files (*)");
        file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
        if (file_dialog.exec() == QDialog::Accepted) {
            paths = file_dialog.selectedFiles();
        }
        break;
    }
    case panels::add_model::SourceMode::None:
        return;
    }
    addFiles(paths);
}

void MainWindow::clearScene() {
    if (viewport_widget_) viewport_widget_->viewport()->setSelectedObjectId(0);
    session_state_->setSelectedObjectId(0);
    session_state_->notifySelectionChanged();

    const auto model_ids = session_state_->modelIds();
    for (uint32_t mid : model_ids) {
        viewport_widget_->viewport()->removeModel(mid);
        loader_->removeModel(mid);
    }

    session_state_->clearModelMappings();
    element_registry_->clear();
    session_state_->notifyModelsChanged();
}

bool MainWindow::confirmDiscardIfDirty() {
    if (!federation_->isDirty()) return true;
    const auto result = QMessageBox::question(
        this, "Unsaved Project",
        "The current project has unsaved changes. Save before continuing?",
        QMessageBox::Save | QMessageBox::Discard | QMessageBox::Cancel,
        QMessageBox::Save);
    if (result == QMessageBox::Cancel) return false;
    if (result == QMessageBox::Save) return saveProject();
    return true;
}

void MainWindow::loadModelsFromPaths(const QStringList& paths, const QStringList& fed_ids) {
    if (paths.isEmpty()) return;
    const auto ids = loader_->addFiles(paths);
    for (int i = 0; i < paths.size() && i < static_cast<int>(ids.size()) && i < fed_ids.size(); ++i) {
        session_state_->setModelMapping(fed_ids[i], ids[i]);
    }
    session_state_->notifyModelsChanged();
}

bool MainWindow::openProject(const QString& path) {
    if (loader_ && loader_->isLoading()) {
        QMessageBox::information(
            this, "Open Project",
            "Wait until the current model load finishes before opening another project.");
        return false;
    }
    if (!confirmDiscardIfDirty()) return false;

    QStringList warnings;
    QString err;
    if (!federation_->load(path, &warnings, &err)) {
        QMessageBox::warning(this, "Open Project",
                             QString("Could not open project:\n%1").arg(err));
        return false;
    }

    clearScene();

    QStringList paths;
    QStringList fed_ids;
    QStringList missing;
    for (const auto& model : federation_->models()) {
        if (model.source_kind != "local") continue;
        if (!QFileInfo::exists(model.source_path)) {
            missing << model.source_path;
            continue;
        }
        paths << model.source_path;
        fed_ids << model.id;
    }
    loadModelsFromPaths(paths, fed_ids);

    for (const auto& msg : missing) {
        warnings << QString("Source not found, kept in project: %1").arg(msg);
    }
    if (!warnings.isEmpty()) {
        QMessageBox::warning(this, "Open Project",
                             "Project opened with warnings:\n\n" + warnings.join("\n"));
    }

    federation_->markClean();
    viewport_controller_->applyFederatedFalseOrigin();
    if (federation_->hasHomeView()) {
        const auto& hv = federation_->homeView();
        viewport_widget_->viewport()->setCamera(
            hv.target.x(), hv.target.y(), hv.target.z(), hv.distance, hv.yaw, hv.pitch);
    }
    updateWindowTitle();
    session_state_->setStatusMessage("Project", QFileInfo(path).fileName());
    session_state_->notifyProjectOpened(path);
    return true;
}

bool MainWindow::saveProject() {
    if (federation_->filePath().isEmpty()) return saveProjectAs();

    QString err;
    if (!federation_->save(federation_->filePath(), &err)) {
        QMessageBox::warning(this, "Save Project",
                             QString("Could not save project:\n%1").arg(err));
        return false;
    }
    updateWindowTitle();
    session_state_->setStatusMessage("Project", QFileInfo(federation_->filePath()).fileName());
    return true;
}

bool MainWindow::saveProjectAs() {
    QString suggested = federation_->filePath();
    if (suggested.isEmpty()) suggested = "project.ifcfed";

    QFileDialog file_dialog(this, "Save Project As", suggested);
    file_dialog.setAcceptMode(QFileDialog::AcceptSave);
    file_dialog.setFileMode(QFileDialog::AnyFile);
    file_dialog.setNameFilter("IFC Federation (*.ifcfed);;All Files (*)");
    file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (file_dialog.exec() != QDialog::Accepted) return false;
    QString path = file_dialog.selectedFiles().value(0);
    if (path.isEmpty()) return false;
    if (!path.endsWith(".ifcfed", Qt::CaseInsensitive)) path += ".ifcfed";

    QString err;
    if (!federation_->save(path, &err)) {
        QMessageBox::warning(this, "Save Project",
                             QString("Could not save project:\n%1").arg(err));
        return false;
    }
    updateWindowTitle();
    session_state_->setStatusMessage("Project", QFileInfo(path).fileName());
    return true;
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

void MainWindow::onNewProject() {
    if (loader_ && loader_->isLoading()) {
        QMessageBox::information(
            this, "New Project",
            "Wait until the current model load finishes before creating a new project.");
        return;
    }
    if (!confirmDiscardIfDirty()) return;
    clearScene();
    federation_->clear();
    viewport_controller_->applyFederatedFalseOrigin();
    updateWindowTitle();
    session_state_->setStatusMessage("Project", "Untitled");
    session_state_->notifyProjectReset();
}

void MainWindow::onOpenProject() {
    QFileDialog file_dialog(this, "Open Project");
    file_dialog.setFileMode(QFileDialog::ExistingFile);
    file_dialog.setNameFilter("IFC Federation (*.ifcfed);;All Files (*)");
    file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (file_dialog.exec() != QDialog::Accepted) return;
    const QString path = file_dialog.selectedFiles().value(0);
    if (path.isEmpty()) return;
    openProject(path);
}

void MainWindow::onSaveProject() {
    saveProject();
}

void MainWindow::onSaveProjectAs() {
    saveProjectAs();
}

void MainWindow::onSetHomeView() {
    auto camera = viewport_widget_->viewport()->cameraState();
    Federation::HomeView home_view;
    home_view.target = camera.target;
    home_view.distance = camera.distance;
    home_view.yaw = camera.yaw;
    home_view.pitch = camera.pitch;
    federation_->setHomeView(home_view);
    updateWindowTitle();
    session_state_->setStatusMessage("Camera", "Home view updated");
}

void MainWindow::onGoHomeView() {
    if (!federation_->hasHomeView()) {
        session_state_->setStatusMessage("Camera", "No home view set for this project");
        return;
    }

    const auto& home_view = federation_->homeView();
    viewport_widget_->viewport()->setCamera(
        home_view.target.x(), home_view.target.y(), home_view.target.z(),
        home_view.distance, home_view.yaw, home_view.pitch);
    session_state_->setStatusMessage("Camera", "Home view restored");
}

void MainWindow::onLoadStarted(uint32_t /*mid*/, QString display_name) {
    session_state_->setStatusMessage("Loading", display_name);
}

void MainWindow::onLoadedFromSidecar(uint32_t mid, qint64 elapsed_ms) {
    session_state_->setStatusMessage(
        "Loaded",
        QString("%1 from cache in %2")
            .arg(loader_->displayName(mid))
            .arg(formatElapsed(elapsed_ms)));
}

void MainWindow::onLoadedFromStream(uint32_t mid, qint64 elapsed_ms) {
    session_state_->setStatusMessage(
        "Loaded",
        QString("%1 streamed in %2")
            .arg(loader_->displayName(mid))
            .arg(formatElapsed(elapsed_ms)));
}

void MainWindow::onLoadCancelled(uint32_t mid) {
    session_state_->setStatusMessage("Cancelled", loader_->displayName(mid));
}

void MainWindow::onLoadError(uint32_t /*mid*/, QString message) {
    session_state_->setStatusMessage("Error", message);
    QMessageBox::warning(this, "IfcInterfaceMockup", message);
}

void MainWindow::onAllLoadsFinished() {
    session_state_->setStatusMessage("Loaded", QString("%1 model(s)").arg(loader_->modelCount()));
}

} // namespace ifcinterface::shell
