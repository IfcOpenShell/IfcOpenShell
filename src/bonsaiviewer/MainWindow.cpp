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
#include "components/SvgIcon.h"
#include "components/Tabs.h"
#include "modules/models/Commands.h"
#include "modules/todo/Panel.h"
#include "modules/display/Commands.h"
#include "modules/display/DisplayState.h"
#include "modules/display/Search.h"
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
#include <QFont>
#include <QHBoxLayout>
#include <QIcon>
#include <QLabel>
#include <QLineEdit>
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
    // Display-tools state (Box, category filters, manual colour/transparency).
    display_state_ = new modules::display::DisplayState(session_state_, this);
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
        // Disabled categories can never come back, even via a global show.
        display_state_->applyAllCategoryFilters(*viewport_widget_->viewport());
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
        // Disabled categories can never come back, even via a global show.
        display_state_->applyAllCategoryFilters(*viewport_widget_->viewport());
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
            makePanelToggle("Properties", properties_panel_),
            makePanelToggle("Display Tools", display_tools_panel_)
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

QWidget* MainWindow::buildDisplayRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(2, 4, 2, 4);
    row->setSpacing(0);

    const DisplayToolButtons tools = makeDisplayToolButtons();

    // Left cluster: ZOOM + BOX, flush at the band's left edge.
    auto* left_cluster = new QWidget(page);
    auto* left_layout = new QHBoxLayout(left_cluster);
    left_layout->setContentsMargins(0, 0, 0, 0);
    left_layout->setSpacing(0);
    components::buttons::addButtonGroups(left_layout, {
        components::buttons::makeButtonGroup("ZOOM", tools.zoom, this),
        components::buttons::makeButtonGroup("BOX", tools.box, this),
    });

    // Mid-left cluster: SECTION + COLOR, centred between the left cluster
    // and the DISPLAY group.
    auto* mid_cluster = new QWidget(page);
    auto* mid_layout = new QHBoxLayout(mid_cluster);
    mid_layout->setContentsMargins(0, 0, 0, 0);
    mid_layout->setSpacing(0);
    components::buttons::addButtonGroups(mid_layout, {
        components::buttons::makeButtonGroup("SECTION", tools.section, this),
        components::buttons::makeButtonGroup("COLOR", tools.color, this),
    });

    // ZOOM+BOX at the left, SECTION+COLOR centred on the left, DISPLAY
    // centred in the band's remaining space.
    row->addWidget(left_cluster);
    row->addStretch(1);
    row->addWidget(mid_cluster);
    row->addStretch(1);
    components::buttons::addButtonGroups(row, {
        components::buttons::makeButtonGroup("DISPLAY", tools.display, this),
    });
    row->addStretch(1);
    return page;
}

MainWindow::DisplayToolButtons MainWindow::makeDisplayToolButtons() {
    namespace commands = bonsaiviewer::modules::display::commands;
    namespace display = bonsaiviewer::modules::display;

    DisplayToolButtons tools;

    // Compact variant: smaller icon and tighter minimum so all the tools
    // fit on a single ribbon line (and stay compact in the dock panel).
    auto make_display_button = [this](const QString& text, const QString& icon) {
        auto* button = components::buttons::makeButton(text, icon, this,
                                                       /*icon_size=*/16,
                                                       /*min_width=*/46,
                                                       /*min_height=*/50);
        // Smaller text too: the long labels ("Perpendicular View", …) must
        // not be truncated by Qt on the packed single-line row.
        QFont font = button->font();
        font.setPointSizeF(std::max(7.0, font.pointSizeF() - 2.0));
        button->setFont(font);
        return button;
    };

    // ---- Section ------------------------------------------------------------
    auto* add_cut = make_display_button("Add Section", ":/icons/knife.svg");
    add_cut->setToolTip("Click a surface to add a section plane perpendicular to it. The tool deactivates after one plane.");
    connect(add_cut, &QToolButton::clicked, this, [this]() {
        commands::activateCutPlaneTool(*session_state_, *viewport_widget_->viewport());
    });
    auto* remove_cuts = make_display_button("Remove Sections", ":/icons/xmark-circle.svg");
    remove_cuts->setToolTip("Remove every section plane in the view.");
    connect(remove_cuts, &QToolButton::clicked, this, [this]() {
        commands::removeAllCutPlanes(*session_state_, *viewport_widget_->viewport());
    });
    auto* hide_cut_planes = make_display_button("Hide Planes", ":/icons/eye-closed.svg");
    hide_cut_planes->setToolTip("Hide the section planes; the cuts stay active.");
    hide_cut_planes->setCheckable(true);
    connect(hide_cut_planes, &QToolButton::toggled, this, [this](bool checked) {
        commands::setCutPlanesVisible(*session_state_, *viewport_widget_->viewport(), !checked);
    });
    auto* suspend_cuts = make_display_button("Suspend Sections", ":/icons/section-pause.svg");
    suspend_cuts->setToolTip("Suspend the cuts and hide the planes. Click again to reactivate and show them.");
    suspend_cuts->setCheckable(true);
    connect(suspend_cuts, &QToolButton::toggled, this, [this](bool checked) {
        commands::setCutSuspension(*session_state_, *viewport_widget_->viewport(), checked);
    });
    tools.section = {add_cut, remove_cuts, hide_cut_planes, suspend_cuts};

    // ---- Colour --------------------------------------------------------------
    auto* paint = make_display_button("Paint", ":/icons/paint-bucket.svg");
    paint->setToolTip("Pick a colour and apply it to the selected elements.");
    connect(paint, &QToolButton::clicked, this, [this]() {
        commands::paintSelectionWithDialog(*session_state_, *viewport_widget_->viewport(), *display_state_, this);
    });
    auto* remove_paint = make_display_button("Remove Color", ":/icons/minus-square.svg");
    remove_paint->setToolTip("Restore the original colour of the selected elements.");
    connect(remove_paint, &QToolButton::clicked, this, [this]() {
        commands::resetSelectionColor(*session_state_, *viewport_widget_->viewport(), *display_state_);
    });
    auto* transparency = make_display_button("Transparency", ":/icons/ghost.svg");
    transparency->setToolTip("Set the opacity of the selected elements (100 / 75 / 50 / 25 %).");
    connect(transparency, &QToolButton::clicked, this, [this]() {
        commands::applyTransparencyWithDialog(*session_state_, *viewport_widget_->viewport(), *display_state_, this);
    });
    tools.color = {paint, remove_paint, transparency};

    // ---- Box ----------------------------------------------------------------
    auto* box_set = make_display_button("Selection → Box", ":/icons/box.svg");
    box_set->setToolTip("Replace the current box with the selection.");
    connect(box_set, &QToolButton::clicked, this, [this]() {
        commands::boxFromSelection(*session_state_, *viewport_widget_->viewport(), *display_state_);
    });
    auto* box_add = make_display_button("Add to Box", ":/icons/plus-square.svg");
    box_add->setToolTip("Add the selected elements to the current box.");
    connect(box_add, &QToolButton::clicked, this, [this]() {
        commands::boxAddSelection(*session_state_, *viewport_widget_->viewport(), *display_state_);
    });
    auto* box_remove = make_display_button("Remove from Box", ":/icons/minus-square.svg");
    box_remove->setToolTip("Remove the selected elements from the current box.");
    connect(box_remove, &QToolButton::clicked, this, [this]() {
        commands::boxRemoveSelection(*session_state_, *viewport_widget_->viewport(), *display_state_);
    });
    auto* box_isolate = make_display_button("Isolate Box", ":/icons/eye-solid.svg");
    box_isolate->setToolTip("Isolate the view on the current box.");
    connect(box_isolate, &QToolButton::clicked, this, [this]() {
        commands::isolateCurrentBox(*session_state_, *viewport_widget_->viewport(), *display_state_);
    });
    auto* box_hide = make_display_button("Hide Box", ":/icons/eye-closed.svg");
    box_hide->setToolTip("Hide the current box objects in the active view.");
    connect(box_hide, &QToolButton::clicked, this, [this]() {
        commands::hideCurrentBox(*session_state_, *viewport_widget_->viewport(), *display_state_);
    });
    auto* box_save = make_display_button("Box Storage", ":/icons/floppy-disk.svg");
    box_save->setToolTip("Save the current box to a slot, or show a saved box.");
    auto* box_menu = new QMenu(box_save);
    for (int slot = 1; slot <= 3; ++slot) {
        QAction* save = box_menu->addAction(QString("Save Box to Slot %1").arg(slot));
        connect(save, &QAction::triggered, this, [this, slot]() {
            display_state_->saveBoxToSlot(slot);
            session_state_->setStatusMessage("Box", QString("Box saved to Slot %1").arg(slot));
        });
        QAction* show = box_menu->addAction(QString("Show Box %1").arg(slot));
        connect(show, &QAction::triggered, this, [this, slot]() {
            commands::isolateBoxSlot(*session_state_, *viewport_widget_->viewport(), *display_state_, slot);
        });
    }
    box_save->setMenu(box_menu);
    box_save->setPopupMode(QToolButton::InstantPopup);
    tools.box = {box_set, box_add, box_remove, box_isolate, box_hide, box_save};

    // ---- Display ------------------------------------------------------------
    auto* show_selection = make_display_button("Show Selection", ":/icons/eye.svg");
    show_selection->setToolTip("Show the selected elements.");
    connect(show_selection, &QToolButton::clicked, this, [this]() {
        commands::showSelection(*viewport_widget_->viewport(), *display_state_);
    });
    auto* hide_selection = make_display_button("Hide Selection", ":/icons/eye-closed.svg");
    hide_selection->setToolTip("Hide the selected elements.");
    connect(hide_selection, &QToolButton::clicked, this, [this]() {
        commands::hideSelection(*viewport_widget_->viewport());
    });
    auto* show_all = make_display_button("Show All", ":/icons/eye.svg");
    show_all->setToolTip("Show all elements. Disabled categories stay hidden.");
    connect(show_all, &QToolButton::clicked, this, [this]() {
        commands::showEverything(*session_state_, *viewport_widget_->viewport(), *display_state_);
    });

    // ---- Categories: dropdown menu (infrequent actions, kept out of the row) --
    // Two sections: "Show / Hide" per category (temporary visual effect) and
    // "Enable / Disable" for spaces/openings (durable for the session,
    // re-applied at each model load).
    auto* categories_button = make_display_button("Categories", ":/icons/filter.svg");
    categories_button->setToolTip("Show / hide categories, and enable / disable spaces and openings for the session.");
    auto* categories_menu = new QMenu(categories_button);
    categories_menu->setToolTipsVisible(true);

    struct CategoryAction {
        QAction* action;
        display::DisplayState::Category category;
        bool enabled_toggle;
    };
    QList<CategoryAction> category_actions;
    auto add_category_action = [this, categories_menu, &category_actions](
            const QString& label, const QString& tooltip,
            display::DisplayState::Category category, bool enabled_toggle) {
        QAction* action = categories_menu->addAction(label);
        action->setCheckable(true);
        action->setToolTip(tooltip);
        action->setChecked(enabled_toggle ? display_state_->categoryEnabled(category)
                                          : display_state_->categoryShown(category));
        connect(action, &QAction::toggled, this, [this, category, enabled_toggle](bool checked) {
            if (enabled_toggle) {
                display_state_->setCategoryEnabled(category, checked, *viewport_widget_->viewport());
            } else {
                display_state_->setCategoryShown(category, checked, *viewport_widget_->viewport());
            }
        });
        category_actions.append({action, category, enabled_toggle});
    };

    QAction* show_header = categories_menu->addAction("Show / Hide");
    show_header->setEnabled(false);
    add_category_action("Walls", "IfcWall, IfcWallStandardCase",
                        display::DisplayState::Category::Walls, false);
    add_category_action("Slabs", "IfcSlab",
                        display::DisplayState::Category::Slabs, false);
    add_category_action("Roofs", "IfcRoof",
                        display::DisplayState::Category::Roofs, false);
    add_category_action("Ceilings", "IfcCovering with CEILING predefined type",
                        display::DisplayState::Category::Ceilings, false);
    add_category_action("Spaces", "IfcSpace",
                        display::DisplayState::Category::Spaces, false);
    add_category_action("Openings", "IfcOpeningElement",
                        display::DisplayState::Category::Reservations, false);
    categories_menu->addSeparator();
    QAction* enable_header = categories_menu->addAction("Enable / Disable (session)");
    enable_header->setEnabled(false);
    add_category_action("Spaces", "IfcSpace",
                        display::DisplayState::Category::Spaces, true);
    add_category_action("Openings", "IfcOpeningElement",
                        display::DisplayState::Category::Reservations, true);

    categories_button->setMenu(categories_menu);
    categories_button->setPopupMode(QToolButton::InstantPopup);
    tools.display = {show_selection, hide_selection, show_all, categories_button};

    // ---- Zoom ----------------------------------------------------------------
    auto* fit_view = make_display_button("Fit View", ":/icons/cube-scan.svg");
    fit_view->setToolTip("Frame the visible objects; warns when the view is empty or the objects are far away.");
    connect(fit_view, &QToolButton::clicked, this, [this]() {
        commands::fitActiveView(*session_state_, *viewport_widget_->viewport(), this);
    });
    auto* perpendicular_view = make_display_button("Perpendicular View", ":/icons/set-square.svg");
    perpendicular_view->setToolTip("Click a surface to look at it head-on, then fit the view.");
    connect(perpendicular_view, &QToolButton::clicked, this, [this]() {
        commands::activatePerpendicularView(*session_state_, *viewport_widget_->viewport());
    });
    tools.zoom = {fit_view, perpendicular_view};

    // ---- Cross-surface sync ----------------------------------------------------
    // Every surface built from this factory (ribbon, later the Display Tools
    // panel) mirrors the authoritative state: the viewport for the section
    // toggles, DisplayState for the categories.
    connect(viewport_widget_->viewport(), &ViewportWindow::sectionStateChanged, this,
            [hide_cut_planes, suspend_cuts](bool gizmos_visible, bool cuts_enabled) {
        const QSignalBlocker hide_blocker(hide_cut_planes);
        hide_cut_planes->setChecked(!gizmos_visible);
        const QSignalBlocker suspend_blocker(suspend_cuts);
        suspend_cuts->setChecked(!cuts_enabled);
    });
    connect(display_state_, &display::DisplayState::categoriesChanged, this,
            [this, category_actions]() {
        for (const auto& entry : category_actions) {
            const QSignalBlocker blocker(entry.action);
            entry.action->setChecked(entry.enabled_toggle
                ? display_state_->categoryEnabled(entry.category)
                : display_state_->categoryShown(entry.category));
        }
    });

    return tools;
}

QWidget* MainWindow::buildSearchBar() {
    auto* frame = new QFrame(this);
    frame->setObjectName("ribbonSearchBar");
    auto* layout = new QHBoxLayout(frame);
    layout->setContentsMargins(8, 6, 8, 6);
    layout->setSpacing(4);

    search_edit_ = new QLineEdit(frame);
    search_edit_->setPlaceholderText("Search…");
    search_edit_->setToolTip(
        "Search the loaded models (Name, Long Name, GUID, class name, predefined type, storey, materials, model name).\n"
        "Prefixes: -fs all properties, -v visible only, -p current box, "
        "-prop \"Set.Name\" one property, -c case-sensitive.");
    search_edit_->setClearButtonEnabled(true);
    layout->addWidget(search_edit_, 1);

    auto* search_button = new QToolButton(frame);
    search_button->setIcon(components::icons::makeAccentSvgIcon(":/icons/search.svg"));
    search_button->setIconSize(QSize(18, 18));
    search_button->setToolTip("Search");
    layout->addWidget(search_button);

    auto run_search = [this]() {
        QString error;
        const auto options = modules::display::search::parse(search_edit_->text(), &error);
        if (!options.has_value()) {
            QMessageBox::information(this, "Search", error);
            return;
        }
        const std::vector<uint32_t> ids = modules::display::search::run(
            *options, *session_state_, *viewport_widget_->viewport(), *display_state_);
        if (ids.empty()) {
            QMessageBox::information(this, "Search", "No results");
            return;
        }
        modules::display::commands::isolateObjects(*viewport_widget_->viewport(), *display_state_, ids);
        session_state_->setStatusMessage("Search",
            QString("%1 object(s) found").arg(ids.size()));
    };
    connect(search_edit_, &QLineEdit::returnPressed, this, run_search);
    connect(search_button, &QToolButton::clicked, this, run_search);

    frame->setFixedWidth(224);
    return frame;
}

QWidget* MainWindow::buildDisplayToolsPanelContent() {
    const DisplayToolButtons tools = makeDisplayToolButtons();

    auto* content = new QWidget(this);
    content->setObjectName("displayToolsPanel");
    auto* layout = new QVBoxLayout(content);
    layout->setContentsMargins(8, 8, 8, 8);
    layout->setSpacing(6);

    // One titled section per group; buttons flow in rows so a narrow dock
    // stays compact.
    auto add_section = [&layout](const QString& title, const QList<QToolButton*>& buttons) {
        auto* label = new QLabel(title, nullptr);
        label->setObjectName("ribbonGroupLabel");
        label->setProperty("textRole", "secondary");
        layout->addWidget(label);
        auto* row = new QHBoxLayout();
        row->setContentsMargins(0, 0, 0, 0);
        row->setSpacing(4);
        for (auto* button : buttons) {
            row->addWidget(button);
        }
        row->addStretch(1);
        layout->addLayout(row);
    };

    add_section("Section", tools.section);
    add_section("Color", tools.color);
    add_section("Box", tools.box);
    add_section("Display", tools.display);
    add_section("Zoom", tools.zoom);
    layout->addStretch(1);
    return content;
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
    ribbon_tabs_->addTab("Display");
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
    ribbon_pages_->addWidget(buildDisplayRibbonPage());
    ribbon_pages_->addWidget(buildPanelsRibbonPage());

    // The search bar lives in the left corner of the band, on every tab.
    // AlignVCenter keeps it at its own height, vertically centred in the
    // band instead of stretching to the pages' full height.
    auto* band_row = new QHBoxLayout();
    band_row->setContentsMargins(0, 0, 0, 0);
    band_row->setSpacing(0);
    band_row->addWidget(buildSearchBar(), 0, Qt::AlignVCenter);
    band_row->addWidget(ribbon_pages_, 1);
    band_layout->addLayout(band_row);
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

    models_view_ = new modules::models::ModelsPanelView(
        models_panel_, session_state_, viewport_widget_->viewport(), this);
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
    // Display Tools: the same commands as the Display ribbon tab, as a dock
    // under the Properties panel.
    display_tools_panel_ = new components::Panel(
        "Display Tools", buildDisplayToolsPanelContent(), this);

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
    // Stack the Display Tools dock under the Properties stack (not tabbed
    // with it): the two stay visible side by side vertically.
    addDockWidget(Qt::RightDockWidgetArea, display_tools_panel_);
    splitDockWidget(properties_panel_, display_tools_panel_, Qt::Vertical);
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
    status_memory_label_ = new QLabel(this);
    status_memory_label_->setVisible(false);
    status_memory_label_->setToolTip(
        "The geometry in view needs more GPU memory than is available, so the "
        "viewer keeps the largest on-screen parts resident and streams the rest "
        "as you move. Right-click a model in the Models panel and choose "
        "\"Unload Model\" to free its GPU memory for the others.");
    status_progress_bar_ = new QProgressBar(this);
    status_perf_label_->setVisible(AppSettings::instance().showStats());
    status_progress_bar_->setMaximumWidth(200);
    status_progress_bar_->setVisible(false);

    statusBar()->setSizeGripEnabled(false);
    statusBar()->addWidget(status_mode_label_);
    statusBar()->addWidget(status_selection_label_, 1);
    statusBar()->addPermanentWidget(status_memory_label_);
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
        const double mb = 1.0 / (1024.0 * 1024.0);

        // Missing chunks are normal for a moment after every camera move
        // while streaming catches up; only a shortfall that persists means
        // the view does not fit, and only that is worth telling the user.
        constexpr qint64 kShortfallNoticeMs = 3000;
        if (stats.chunks_wanted_missing == 0) {
            memory_shortfall_since_.invalidate();
            status_memory_label_->setVisible(false);
        } else {
            if (!memory_shortfall_since_.isValid()) memory_shortfall_since_.start();
            if (memory_shortfall_since_.elapsed() >= kShortfallNoticeMs) {
                status_memory_label_->setText(
                    QString("GPU memory full: %1 of %2 visible chunks (%3 MB) not loaded")
                        .arg(stats.chunks_wanted_missing)
                        .arg(stats.chunks_wanted)
                        .arg(double(stats.wanted_missing_bytes) * mb, 0, 'f', 0));
                status_memory_label_->setVisible(true);
            }
        }

        if (!status_perf_label_->isVisible()) return;
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
                .arg(double(stats.vram_capacity_bytes) * mb, 0, 'f', 0);
        // The budget is where the pool may grow to; the pool can also sit
        // a sub-buffer above it (a release would undershoot). Show it
        // only when it tells the user something capacity does not.
        if (stats.vram_budget_bytes > 0
            && stats.vram_budget_bytes != stats.vram_capacity_bytes) {
            text += QString(" (budget %1)")
                .arg(double(stats.vram_budget_bytes) * mb, 0, 'f', 0);
        }
        // Device total is only known when a driver backend answered.
        if (stats.device_vram_total_bytes > 0) {
            text += QString(" | Device %1/%2 MB")
                .arg(double(stats.device_vram_used_bytes) * mb, 0, 'f', 0)
                .arg(double(stats.device_vram_total_bytes) * mb, 0, 'f', 0);
        }
        if (stats.chunks_wanted_missing > 0) {
            text += QString(" | %1/%2 chunks waiting")
                .arg(stats.chunks_wanted_missing)
                .arg(stats.chunks_wanted);
        }
        status_perf_label_->setText(text);
    });
    connect(viewport_widget_->viewport(), &ViewportWindow::objectPicked,
            this, [this](uint32_t object_id) {
        session_state_->setSelectedObjectId(object_id);
        session_state_->notifySelectionChanged();
    });

    // Display tools ("Display" tab). The knife / set-square cursors follow
    // the viewport's tool transitions; the single-shot cut tool resets itself.
    connect(viewport_widget_->viewport(), &ViewportWindow::sectionToolChanged,
            this, [this](bool active) {
        auto* viewport = viewport_widget_->viewport();
        if (active) {
            viewport->setCursor(modules::display::commands::knifeCursor());
        } else {
            viewport->setCursor(QCursor(Qt::ArrowCursor));
            viewport->setSectionToolSingleShot(false);
        }
    });
    connect(viewport_widget_->viewport(), &ViewportWindow::perpendicularViewToolChanged,
            this, [this](bool active) {
        auto* viewport = viewport_widget_->viewport();
        viewport->setCursor(active ? modules::display::commands::setSquareCursor()
                                   : QCursor(Qt::ArrowCursor));
    });
    // Right-click on a section-plane gizmo: context menu with Delete.
    connect(viewport_widget_->viewport(),
            &ViewportWindow::sectionPlaneContextMenuRequested,
            this, [this](int plane_index, const QPoint& global_pos) {
        QMenu menu(this);
        QAction* delete_action = menu.addAction("Delete plane");
        if (menu.exec(global_pos) == delete_action) {
            viewport_widget_->viewport()->removeSectionPlane(plane_index);
            session_state_->setStatusMessage("Section", "Section plane deleted");
        }
    });
    // Category filters are session-durable: re-apply them each time a model's
    // geometry / live data source arrives so a disabled category never
    // reappears with a fresh load.
    connect(session_state_, &bonsaiviewer::SessionState::modelGeometryReady,
            this, [this](uint32_t session_model_id) {
        if (viewport_widget_ && viewport_widget_->viewport()) {
            display_state_->applyCategoryFiltersForModel(
                session_model_id, *viewport_widget_->viewport());
        }
    });
    connect(session_state_, &bonsaiviewer::SessionState::modelDataSourceReady,
            this, [this](uint32_t session_model_id) {
        if (viewport_widget_ && viewport_widget_->viewport()) {
            display_state_->applyCategoryFiltersForModel(
                session_model_id, *viewport_widget_->viewport());
        }
    });
    // The Box and the manual appearance map only hold ids the registry knows:
    // purge on every model list change (close / reload / reset).
    connect(session_state_, &bonsaiviewer::SessionState::modelsChanged, this, [this]() {
        display_state_->purgeRemovedObjects();
    });
    connect(session_state_, &bonsaiviewer::SessionState::projectReset, this, [this]() {
        display_state_->purgeRemovedObjects();
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
