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

#include "../ifcviewer/AppSettings.h"
#include "../ifcviewer/Federation.h"
#include "../ifcviewer/ViewportWindow.h"
#include "SessionState.h"
#include "components/Buttons.h"
#include "components/Panel.h"
#include "components/Style.h"
#include "components/Tabs.h"
#include "modules/models/Commands.h"
#include "modules/todo/Panel.h"
#include "modules/models/View.h"
#include "modules/models/Panel.h"
#include "modules/project/Commands.h"
#include "modules/project/RecentProjects.h"
#include "modules/properties/View.h"
#include "modules/properties/Panel.h"
#include "modules/settings/Dialog.h"
#include "modules/spatial_hierarchy/View.h"
#include "modules/spatial_hierarchy/Panel.h"
#include "modules/viewport/Commands.h"
#include "modules/viewport/Panel.h"
#include "modules/viewport/View.h"

#include <QAction>
#include <QDockWidget>
#include <QFileInfo>
#include <QHBoxLayout>
#include <QIcon>
#include <QLabel>
#include <QMenu>
#include <QMessageBox>
#include <QShortcut>
#include <QSignalBlocker>
#include <QStackedWidget>
#include <QStatusBar>
#include <QProgressBar>
#include <QToolButton>
#include <QVBoxLayout>

namespace bonsaiviewer::shell {

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    session_state_ = new bonsaiviewer::SessionState(this);
    auto on_mutated = [this]() {
        setWindowModified(true);
        updateWindowTitle();
    };
    auto on_clean_state = [this]() {
        setWindowModified(false);
        updateWindowTitle();
    };
    connect(session_state_, &bonsaiviewer::SessionState::federationChanged, this, on_mutated);
    connect(session_state_, &bonsaiviewer::SessionState::modelsChanged,     this, on_mutated);
    connect(session_state_, &bonsaiviewer::SessionState::projectReset,      this, on_clean_state);
    connect(session_state_, &bonsaiviewer::SessionState::projectOpened,     this, on_clean_state);
    connect(session_state_, &bonsaiviewer::SessionState::projectSaved,      this, on_clean_state);

    // Every successful open/save (local or cloud) feeds the recent list.
    auto remember_recent = [](const QString& path) {
        modules::project::RecentProjects::add(path);
    };
    connect(session_state_, &bonsaiviewer::SessionState::projectOpened, this, remember_recent);
    connect(session_state_, &bonsaiviewer::SessionState::projectSaved,  this, remember_recent);
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

    auto bind_shortcut = [this](const QKeySequence& sequence, auto handler) {
        auto* shortcut = new QShortcut(sequence, this);
        shortcut->setContext(Qt::WindowShortcut);
        connect(shortcut, &QShortcut::activated, this, handler);
    };
    bind_shortcut(QKeySequence("Ctrl+Shift+L"), [this]() {
        modules::viewport::commands::toggleDistance(*viewport_widget_->viewport());
    });
    bind_shortcut(QKeySequence("Ctrl+Shift+A"), [this]() {
        modules::viewport::commands::toggleArea(*viewport_widget_->viewport());
    });
    bind_shortcut(QKeySequence("Ctrl+Shift+V"), [this]() {
        modules::viewport::commands::toggleVolume(*viewport_widget_->viewport());
    });
    bind_shortcut(QKeySequence(Qt::SHIFT | Qt::Key_F), [this]() {
        modules::viewport::commands::fly(*session_state_, *viewport_widget_->viewport());
    });
    bind_shortcut(QKeySequence(Qt::Key_K), [this]() {
        modules::viewport::commands::toggleSection(*session_state_, *viewport_widget_->viewport());
    });
    bind_shortcut(QKeySequence(Qt::SHIFT | Qt::Key_K), [this]() {
        modules::viewport::commands::clearSection(*session_state_, *viewport_widget_->viewport());
    });
    bind_shortcut(QKeySequence(Qt::Key_H), [this]() {
        modules::viewport::commands::hideSelected(*viewport_widget_->viewport());
    });
    bind_shortcut(QKeySequence(Qt::SHIFT | Qt::Key_H), [this]() {
        modules::viewport::commands::isolateSelected(*viewport_widget_->viewport());
    });
    bind_shortcut(QKeySequence(Qt::ALT | Qt::Key_H), [this]() {
        modules::viewport::commands::showAll(*viewport_widget_->viewport());
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

void MainWindow::populateRecentMenu(QMenu* menu) {
    menu->clear();

    const QStringList recent = modules::project::RecentProjects::list();
    if (recent.isEmpty()) {
        QAction* empty = menu->addAction("No Recent Projects");
        empty->setEnabled(false);
        return;
    }

    for (const QString& path : recent) {
        QAction* action = menu->addAction(QFileInfo(path).fileName());
        action->setToolTip(path);
        connect(action, &QAction::triggered, this, [this, path]() {
            const bool opened = modules::project::commands::openProjectPath(
                *session_state_, *this, *viewport_widget_->viewport(), path);
            // A recent entry that no longer loads is dropped so it stops
            // cluttering the menu (e.g. moved/deleted file).
            if (!opened && !QFileInfo::exists(path)) {
                modules::project::RecentProjects::remove(path);
            }
        });
    }

    menu->addSeparator();
    QAction* clear = menu->addAction("Clear Recent Projects");
    connect(clear, &QAction::triggered, this, []() {
        modules::project::RecentProjects::clear();
    });
}

QWidget* MainWindow::buildHomeRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(6, 4, 6, 4);
    row->setSpacing(0);

    auto* new_project = components::buttons::makeButton("New Project", ":/icons/plus-square.svg", this);
    connect(new_project, &QToolButton::clicked, this, [this]() {
        modules::project::commands::newProject(
            *session_state_, *this, *viewport_widget_->viewport());
    });
    auto* open_project = components::buttons::makeButton("Open Project", ":/icons/download-square.svg", this);
    connect(open_project, &QToolButton::clicked, this, [this]() {
        modules::project::commands::openProject(
            *session_state_, *this, *viewport_widget_->viewport());
    });
    auto* open_cloud = components::buttons::makeButton("Open Cloud", ":/icons/cloud-square.svg", this);
    connect(open_cloud, &QToolButton::clicked, this, [this]() {
        modules::project::commands::openCloudProject(
            *session_state_, *this, *viewport_widget_->viewport());
    });
    auto* open_recent = components::buttons::makeButton("Open Recent", ":/icons/clock-rotate-right.svg", this);
    auto* recent_menu = new QMenu(open_recent);
    recent_menu->setToolTipsVisible(true);
    open_recent->setMenu(recent_menu);
    open_recent->setPopupMode(QToolButton::InstantPopup);
    connect(recent_menu, &QMenu::aboutToShow, this, [this, recent_menu]() {
        populateRecentMenu(recent_menu);
    });
    auto* save_project = components::buttons::makeButton("Save Project", ":/icons/floppy-disk.svg", this);
    connect(save_project, &QToolButton::clicked, this, [this]() {
        modules::project::commands::saveProjectDialog(*session_state_, *this);
    });

    auto* add_model = components::buttons::makeButton("Add Model", ":/icons/cube.svg", this);
    connect(add_model, &QToolButton::clicked, this, [this]() {
        modules::models::commands::addModel(*session_state_, *this);
    });
    auto* sync_from_cloud = components::buttons::makeButton("Sync From Cloud", ":/icons/refresh-double.svg", this);
    connect(sync_from_cloud, &QToolButton::clicked, this, [this]() {
        modules::project::commands::syncCloudProject(
            *session_state_, *this, *viewport_widget_->viewport());
    });

    auto* settings_button = components::buttons::makeButton("Settings", ":/icons/settings.svg", this);
    connect(settings_button, &QToolButton::clicked, this, [this]() {
        modules::settings::SettingsDialog dialog(session_state_, this);
        dialog.exec();
    });

    components::buttons::addButtonGroups(row, {
        components::buttons::makeButtonGroup("PROJECT", {new_project, open_project, open_cloud, open_recent, save_project}, this),
        components::buttons::makeButtonGroup("MODELS", {add_model, sync_from_cloud}, this),
        components::buttons::makeButtonGroup("SETTINGS", {settings_button}, this),
    });
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
        modules::viewport::commands::setHome(*session_state_, *viewport_widget_->viewport());
    });
    auto* go_home = components::buttons::makeButton("Go Home", ":/icons/home-alt.svg", this);
    connect(go_home, &QToolButton::clicked, this, [this]() {
        modules::viewport::commands::goHome(*session_state_, *viewport_widget_->viewport());
    });
    auto* view_all = components::buttons::makeButton("View All", ":/icons/cube-scan.svg", this);
    connect(view_all, &QToolButton::clicked, this, [this]() {
        if (viewport_widget_) viewport_widget_->viewport()->viewAll();
    });
    auto* view_selected = components::buttons::makeButton("View Selected", ":/icons/cube-scan-solid.svg", this);
    connect(view_selected, &QToolButton::clicked, this, [this]() {
        modules::viewport::commands::viewSelected(*viewport_widget_->viewport());
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
        modules::viewport::commands::fly(*session_state_, *viewport_widget_->viewport());
    });
    auto* section_mode = components::buttons::makeButton("Section", ":/icons/cube-cut-with-curve.svg", this);
    connect(section_mode, &QToolButton::clicked, this, [this]() {
        modules::viewport::commands::toggleSection(*session_state_, *viewport_widget_->viewport());
    });

    components::buttons::addButtonGroups(row, {
        components::buttons::makeButtonGroup("CAMERA", {set_home, go_home, view_all, view_selected}, this),
        components::buttons::makeButtonGroup("ORIENTATION", {plan_view, front_view, side_view, align_object, projection_button}, this),
        components::buttons::makeButtonGroup("MODE", {fly_mode, section_mode}, this),
    });
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
        modules::viewport::commands::hideSelected(*viewport_widget_->viewport());
    });
    auto* isolate_selected = components::buttons::makeButton("Isolate", ":/icons/eye-solid.svg", this);
    connect(isolate_selected, &QToolButton::clicked, this, [this]() {
        modules::viewport::commands::isolateSelected(*viewport_widget_->viewport());
    });
    auto* show_all = components::buttons::makeButton("Show All", ":/icons/eye.svg", this);
    connect(show_all, &QToolButton::clicked, this, [this]() {
        modules::viewport::commands::showAll(*viewport_widget_->viewport());
    });
    auto* invert_selection = components::buttons::makeButton("Invert", ":/icons/intersect.svg", this);
    connect(invert_selection, &QToolButton::clicked, this, [this]() {
        modules::viewport::commands::invertVisibility(*viewport_widget_->viewport());
    });

    auto* distance = components::buttons::makeButton("Distance", ":/icons/select-edge3d.svg", this);
    connect(distance, &QToolButton::clicked, this, [this]() {
        modules::viewport::commands::toggleDistance(*viewport_widget_->viewport());
    });
    auto* area = components::buttons::makeButton("Area", ":/icons/select-face3d.svg", this);
    connect(area, &QToolButton::clicked, this, [this]() {
        modules::viewport::commands::toggleArea(*viewport_widget_->viewport());
    });
    auto* volume = components::buttons::makeButton("Volume", ":/icons/select-point3d.svg", this);
    connect(volume, &QToolButton::clicked, this, [this]() {
        modules::viewport::commands::toggleVolume(*viewport_widget_->viewport());
    });

    components::buttons::addButtonGroups(row, {
        components::buttons::makeButtonGroup("SELECTION", {hide_selected, isolate_selected, show_all, invert_selection}, this),
        components::buttons::makeButtonGroup("MEASURE", {distance, area, volume}, this),
    });
    row->addStretch(1);
    return page;
}

QWidget* MainWindow::buildPanelsRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(2, 4, 2, 4);
    row->setSpacing(0);

    components::buttons::addButtonGroups(row, {
        components::buttons::makeButtonGroup("DATA", {
            makePanelToggle("Models", models_panel_),
            makePanelToggle("Spatial", spatial_panel_),
            makePanelToggle("Layers", layers_panel_),
            makePanelToggle("Properties", properties_panel_)
        }, this),
        components::buttons::makeButtonGroup("QUERY", {
            makePanelToggle("Views", stored_views_panel_),
            makePanelToggle("Search", search_panel_),
            makePanelToggle("Sheets", spreadsheet_panel_),
            makePanelToggle("Audit", audit_panel_)
        }, this),
        components::buttons::makeButtonGroup("COLLABORATE", {
            makePanelToggle("Clash", clash_panel_),
            makePanelToggle("Issues", issues_panel_)
        }, this),
    });
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
    models_panel_ = new modules::models::ModelsPanel(
        session_state_, viewport_widget_->viewport(), this);
    spatial_panel_ = new modules::spatial_hierarchy::SpatialHierarchyPanel(this);
    properties_panel_ = new modules::properties::PropertiesPanel(this);

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

    // Nav mouse preset. The WGPU_NAV_PRESET env var is a dev override applied at
    // ViewportWindow construction; otherwise apply the persisted Settings choice
    // here, and re-apply live whenever the user changes it in the dialog.
    if (!std::getenv("WGPU_NAV_PRESET")) {
        if (auto* vp = viewport_widget_->viewport())
            vp->applyNavPreset(AppSettings::navPresetName(AppSettings::instance().navPreset()));
    }
    connect(&AppSettings::instance(), &AppSettings::navPresetChanged, this,
            [this](AppSettings::NavPreset preset) {
                if (auto* vp = viewport_widget_->viewport())
                    vp->applyNavPreset(AppSettings::navPresetName(preset));
            });

    // Backface culling: apply the persisted choice and re-apply live on change.
    if (auto* vp = viewport_widget_->viewport())
        vp->setBackfaceCulling(AppSettings::instance().backfaceCulling());
    connect(&AppSettings::instance(), &AppSettings::backfaceCullingChanged, this,
            [this](bool enabled) {
                if (auto* vp = viewport_widget_->viewport())
                    vp->setBackfaceCulling(enabled);
            });

    connect(session_state_, &bonsaiviewer::SessionState::statusMessageChanged,
            this, [this](const QString& mode, const QString& detail) {
        status_mode_label_->setText(mode);
        status_selection_label_->setText(detail);
    });
    connect(session_state_, &bonsaiviewer::SessionState::progressBegan, this, [this](const QString&) {
        // Start in indeterminate mode (spinning bar). The first concrete
        // setProgress(...) call below switches it to a determinate 0-100 bar.
        status_progress_bar_->setRange(0, 0);
        status_progress_bar_->setVisible(true);
    });
    connect(session_state_, &bonsaiviewer::SessionState::progressChanged, this, [this](int percent) {
        if (status_progress_bar_->maximum() == 0) status_progress_bar_->setRange(0, 100);
        status_progress_bar_->setValue(percent);
    });
    connect(session_state_, &bonsaiviewer::SessionState::progressEnded, this, [this]() {
        status_progress_bar_->setVisible(false);
    });
    session_state_->setStatusMessage("Ready", "No selection");
}

void MainWindow::setupLoader() {
    session_state_->createLoader(viewport_widget_->viewport());
    viewport_view_ = new modules::viewport::ViewportView(
        session_state_, viewport_widget_->viewport(), this);

    // Load errors surface through SessionState as a session-level signal; the
    // status text + progress are already cleared there, we only show the modal.
    connect(session_state_, &bonsaiviewer::SessionState::loadError, this,
            [this](const QString& message) {
        QMessageBox::warning(this, "Bonsai Viewer", message);
    });

    connect(viewport_widget_->viewport(), &ViewportWindow::frameStatsUpdated, this,
            [this](const ViewportWindow::FrameStats& stats) {
        if (!status_perf_label_->isVisible()) return;
        const double mb = 1.0 / (1024.0 * 1024.0);
        QString text =
            QString("%1 fps | %2 ms | %3/%4 obj | %5/%6 tri | %7 draws | VRAM %8/%9 MB")
                .arg(stats.fps, 0, 'f', 1)
                .arg(stats.frame_time_ms, 0, 'f', 1)
                .arg(stats.visible_objects)
                .arg(stats.total_objects)
                .arg(stats.visible_triangles)
                .arg(stats.total_triangles)
                .arg(stats.gl_draw_calls)
                .arg(double(stats.vram_used_bytes) * mb, 0, 'f', 0)
                // Used against what the cache may grow to; the pool's
                // momentary capacity only until the budget is known.
                .arg(double(stats.vram_budget_bytes > 0
                                ? stats.vram_budget_bytes
                                : stats.vram_capacity_bytes) * mb, 0, 'f', 0);
        // Device total is only known when a driver backend answered.
        if (stats.device_vram_total_bytes > 0) {
            text += QString(" | Device %1/%2 MB")
                .arg(double(stats.device_vram_used_bytes) * mb, 0, 'f', 0)
                .arg(double(stats.device_vram_total_bytes) * mb, 0, 'f', 0);
        }
        status_perf_label_->setText(text);
    });
    connect(viewport_widget_->viewport(), &ViewportWindow::objectPicked,
            this, [this](uint32_t object_id) {
        session_state_->setSelectedObjectId(object_id);
        session_state_->notifySelectionChanged();
    });
}

void MainWindow::updateWindowTitle() {
    auto* federation = session_state_->federation();
    const QString project_path = federation->filePath();
    if (project_path.isEmpty() && federation->models().empty()) {
        setWindowTitle("Bonsai Viewer");
    } else if (project_path.isEmpty()) {
        setWindowTitle("untitled[*] - Bonsai Viewer");
    } else {
        setWindowTitle(QFileInfo(project_path).fileName() + "[*] - Bonsai Viewer");
    }
}

} // namespace bonsaiviewer::shell
