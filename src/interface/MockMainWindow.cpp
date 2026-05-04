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

#include "MockMainWindow.h"

#include "AppSettings.h"
#include "SceneLoader.h"
#include "ViewportWindow.h"

#include <QDockWidget>
#include <QFileDialog>
#include <QFile>
#include <QFormLayout>
#include <QFrame>
#include <QGroupBox>
#include <QHeaderView>
#include <QHBoxLayout>
#include <QIcon>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QMenu>
#include <QMessageBox>
#include <QPainter>
#include <QPixmap>
#include <QRegularExpression>
#include <QScrollArea>
#include <QSvgRenderer>
#include <QSignalBlocker>
#include <QStackedWidget>
#include <QStatusBar>
#include <QTableWidget>
#include <QTabBar>
#include <QToolButton>
#include <QTreeWidget>
#include <QVBoxLayout>

namespace {

QPixmap renderTintedSvgPixmap(const QString& icon_path, const QString& color, const QSize& size) {
    QFile file(icon_path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return QIcon(icon_path).pixmap(size);
    }

    QString svg = QString::fromUtf8(file.readAll());
    QString tinted = svg;
    tinted.replace("currentColor", color, Qt::CaseSensitive);
    tinted.replace(QRegularExpression(R"(stroke="[^"]*")"), QString("stroke=\"%1\"").arg(color));
    tinted.replace(QRegularExpression(R"(fill="none")"), "fill=\"none\"");
    QByteArray data = tinted.toUtf8();
    QSvgRenderer renderer(data);
    QPixmap pixmap(size);
    pixmap.fill(Qt::transparent);
    QPainter painter(&pixmap);
    renderer.render(&painter);
    return pixmap;
}

QIcon makeTintedSvgIcon(const QString& icon_path, const QString& normal = "#39b54a",
                        const QString& active = "#53c763", const QString& disabled = "#6f7988") {
    QFile file(icon_path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return QIcon(icon_path);
    }

    QIcon icon;
    icon.addPixmap(renderTintedSvgPixmap(icon_path, normal, QSize(20, 20)), QIcon::Normal, QIcon::Off);
    icon.addPixmap(renderTintedSvgPixmap(icon_path, active, QSize(20, 20)), QIcon::Active, QIcon::Off);
    icon.addPixmap(renderTintedSvgPixmap(icon_path, active, QSize(20, 20)), QIcon::Selected, QIcon::Off);
    icon.addPixmap(renderTintedSvgPixmap(icon_path, disabled, QSize(20, 20)), QIcon::Disabled, QIcon::Off);
    return icon;
}

QIcon makePanelSvgIcon(const QString& icon_path) {
    return makeTintedSvgIcon(icon_path, "#e7ebf2", "#ffffff", "#6f7988");
}

QPixmap makePanelSvgPixmap(const QString& icon_path, const QSize& size) {
    return renderTintedSvgPixmap(icon_path, "#e7ebf2", size);
}

class DockTitleBar : public QWidget {
public:
    explicit DockTitleBar(const QString& title, bool has_settings = false, QWidget* parent = nullptr)
        : QWidget(parent)
    {
        auto* layout = new QHBoxLayout(this);
        layout->setContentsMargins(10, 6, 6, 6);
        layout->setSpacing(6);

        auto* text = new QLabel(title.toUpper(), this);
        text->setObjectName("dockTitleText");

        layout->addWidget(text);
        layout->addStretch(1);
        if (has_settings) {
            auto* settings = new QToolButton(this);
            settings->setIcon(makePanelSvgIcon(":/icons/settings.svg"));
            settings->setAutoRaise(true);
            settings->setCursor(Qt::ArrowCursor);
            settings->setFixedSize(18, 18);
            settings->setObjectName("dockTitleButton");
            settings->setToolTip(QString("%1 settings").arg(title));
            connect(settings, &QToolButton::clicked, this, [this, title]() {
                auto* anchor = parentWidget();
                QMenu menu(anchor);
                menu.addAction(QString("%1 settings coming soon").arg(title));
                menu.exec(QCursor::pos());
            });
            layout->addWidget(settings);
        }
    }
};

QDockWidget* makeDock(const QString& title, QWidget* content, QWidget* parent, bool has_settings = false) {
    auto* dock = new QDockWidget(title, parent);
    dock->setObjectName(title);
    dock->setFeatures(QDockWidget::DockWidgetMovable |
                      QDockWidget::DockWidgetFloatable |
                      QDockWidget::DockWidgetClosable);
    dock->setTitleBarWidget(new DockTitleBar(title, has_settings, dock));
    dock->setWidget(content);
    return dock;
}

QFrame* wrapPanel(QWidget* inner) {
    auto* outer = new QFrame();
    auto* outer_layout = new QVBoxLayout(outer);
    outer_layout->setContentsMargins(6, 6, 6, 6);
    outer_layout->setSpacing(0);

    auto* frame = new QFrame(outer);
    frame->setObjectName("panelFrame");
    auto* layout = new QVBoxLayout(frame);
    layout->setContentsMargins(8, 8, 8, 8);
    layout->setSpacing(0);
    layout->addWidget(inner);

    outer_layout->addWidget(frame);
    return outer;
}

QFrame* wrapInspectorPanel(QWidget* inner) {
    auto* outer = new QFrame();
    auto* outer_layout = new QVBoxLayout(outer);
    outer_layout->setContentsMargins(6, 6, 6, 6);
    outer_layout->setSpacing(0);

    auto* frame = new QFrame(outer);
    frame->setObjectName("panelFrame");
    auto* layout = new QVBoxLayout(frame);
    layout->setContentsMargins(0, 8, 0, 8);
    layout->setSpacing(0);
    layout->addWidget(inner);

    outer_layout->addWidget(frame);
    return outer;
}

QWidget* makeInspectorFilterField(const QString& placeholder, QWidget* parent = nullptr) {
    auto* field = new QLineEdit(parent);
    field->setPlaceholderText(placeholder);
    field->setClearButtonEnabled(true);
    field->addAction(makePanelSvgIcon(":/icons/filter.svg"), QLineEdit::LeadingPosition);
    return field;
}

QWidget* makePropertySetPanel(const QString& title,
                              const QList<QPair<QString, QString>>& rows,
                              QWidget* parent = nullptr) {
    auto* group = new QGroupBox(title, parent);
    group->setObjectName("propertySetCard");
    auto* form = new QFormLayout(group);
    form->setContentsMargins(10, 10, 10, 10);
    form->setHorizontalSpacing(16);
    form->setVerticalSpacing(6);
    form->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    for (const auto& [name, value] : rows) {
        auto* key = new QLabel(name, group);
        key->setObjectName("propertyKeyLabel");
        auto* val = new QLabel(value, group);
        val->setObjectName("propertyValueLabel");
        val->setWordWrap(true);
        form->addRow(key, val);
    }

    return group;
}

QWidget* makeInspectorSection(const QString& title,
                              const QString& filter_placeholder,
                              const QList<QWidget*>& groups,
                              QWidget* parent = nullptr) {
    auto* section = new QWidget(parent);
    section->setObjectName("inspectorSection");
    auto* layout = new QVBoxLayout(section);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(6);

    auto* header = new QFrame(section);
    header->setObjectName("inspectorSectionHeader");
    auto* header_layout = new QHBoxLayout(header);
    header_layout->setContentsMargins(0, 0, 0, 0);
    header_layout->setSpacing(6);

    auto* toggle = new QToolButton(header);
    toggle->setObjectName("inspectorSectionButton");
    toggle->setText(title);
    toggle->setCheckable(true);
    toggle->setChecked(true);
    toggle->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    toggle->setArrowType(Qt::DownArrow);
    header_layout->addWidget(toggle);
    header_layout->addStretch(1);

    QLineEdit* filter_field = nullptr;
    if (!filter_placeholder.isEmpty()) {
        auto* filter_toggle = new QToolButton(header);
        filter_toggle->setObjectName("inspectorFilterToggle");
        filter_toggle->setCheckable(true);
        filter_toggle->setChecked(false);
        filter_toggle->setIcon(makePanelSvgIcon(":/icons/filter.svg"));
        filter_toggle->setAutoRaise(true);
        filter_toggle->setToolTip(QString("Filter %1").arg(title.toLower()));
        header_layout->addWidget(filter_toggle);

        filter_field = qobject_cast<QLineEdit*>(makeInspectorFilterField(filter_placeholder, section));
        filter_field->setVisible(false);
        QObject::connect(filter_toggle, &QToolButton::toggled, filter_field, [filter_field](bool visible) {
            filter_field->setVisible(visible);
            if (visible) filter_field->setFocus();
        });
    }

    auto* body = new QWidget(section);
    body->setObjectName("inspectorSectionBody");
    auto* body_layout = new QVBoxLayout(body);
    body_layout->setContentsMargins(10, 6, 10, 0);
    body_layout->setSpacing(6);
    for (auto* group : groups) body_layout->addWidget(group);

    QObject::connect(toggle, &QToolButton::toggled, body, [toggle, body](bool expanded) {
        toggle->setArrowType(expanded ? Qt::DownArrow : Qt::RightArrow);
        body->setVisible(expanded);
    });

    layout->addWidget(header);
    if (filter_field) {
        auto* filter_wrapper = new QWidget(section);
        filter_wrapper->setObjectName("inspectorFilterWrapper");
        auto* filter_wrapper_layout = new QVBoxLayout(filter_wrapper);
        filter_wrapper_layout->setContentsMargins(10, 0, 10, 0);
        filter_wrapper_layout->setSpacing(0);
        filter_wrapper_layout->addWidget(filter_field);
        layout->addWidget(filter_wrapper);
    }
    layout->addWidget(body);
    return section;
}

QWidget* makeAttributeList(const QList<QPair<QString, QString>>& rows, QWidget* parent = nullptr) {
    auto* panel = new QWidget(parent);
    panel->setObjectName("attributeList");
    auto* form = new QFormLayout(panel);
    form->setContentsMargins(0, 0, 0, 0);
    form->setHorizontalSpacing(16);
    form->setVerticalSpacing(6);
    form->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    for (const auto& [name, value] : rows) {
        auto* key = new QLabel(name, panel);
        key->setObjectName("propertyKeyLabel");
        auto* val = new QLabel(value, panel);
        val->setObjectName("propertyValueLabel");
        val->setWordWrap(true);
        form->addRow(key, val);
    }

    return panel;
}

QWidget* makeRelationshipList(const QList<QPair<QString, QString>>& rows, QWidget* parent = nullptr) {
    auto* panel = new QWidget(parent);
    panel->setObjectName("attributeList");
    auto* layout = new QVBoxLayout(panel);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(6);

    for (const auto& [name, value] : rows) {
        auto* row = new QWidget(panel);
        row->setObjectName("relationshipRow");
        auto* row_layout = new QHBoxLayout(row);
        row_layout->setContentsMargins(0, 0, 0, 0);
        row_layout->setSpacing(12);

        auto* key = new QLabel(name, row);
        key->setObjectName("propertyKeyLabel");
        key->setMinimumWidth(72);

        auto* target = new QLabel(value, row);
        target->setObjectName("relationshipValueLabel");
        target->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);

        auto* icon = new QLabel(row);
        icon->setObjectName("relationshipIconLabel");
        icon->setPixmap(makePanelSvgPixmap(":/icons/cursor-pointer.svg", QSize(14, 14)));
        icon->setAlignment(Qt::AlignRight | Qt::AlignVCenter);

        row_layout->addWidget(key);
        row_layout->addWidget(target, 1);
        row_layout->addWidget(icon, 0, Qt::AlignRight | Qt::AlignVCenter);
        layout->addWidget(row);
    }

    return panel;
}

} // namespace

MockMainWindow::MockMainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    setupChrome();
    setupViewport();
    setupDocks();
    setupStatus();
    setupLoader();
    setupRibbon();
    resize(1720, 980);
}

void MockMainWindow::setupChrome() {
    setWindowTitle("IfcOpenShell Interface");
    setDockOptions(QMainWindow::AllowNestedDocks |
                   QMainWindow::AllowTabbedDocks |
                   QMainWindow::GroupedDragging);

    setStyleSheet(R"(
        QMainWindow {
            background: #26292f;
        }
        QWidget {
            color: #d0d5dd;
            background: #26292f;
            selection-background-color: #39b54a;
            selection-color: #14161a;
        }
        QFrame#ribbonShell {
            background: #2d3138;
            border-bottom: 1px solid #1b1d22;
        }
        QTabBar::tab {
            background: transparent;
            color: #8d97a7;
            padding: 8px 14px;
            margin-right: 2px;
            border-bottom: 2px solid transparent;
        }
        QTabBar::tab:selected {
            color: #f2f5fa;
            border-bottom: 2px solid #39b54a;
        }
        QTabBar::tab:hover {
            color: #ffffff;
        }
        QFrame#ribbonBand {
            background: #31353d;
            border-top: 1px solid #3b4048;
        }
        QFrame#ribbonPage {
            background: transparent;
        }
        QFrame#ribbonGroup {
            background: transparent;
            border-right: 1px solid #434852;
        }
        QLabel#ribbonGroupLabel {
            color: #7f8796;
            font-size: 9px;
            font-weight: 600;
            letter-spacing: 0.08em;
        }
        QToolButton#ribbonButton {
            background: transparent;
            border: none;
            padding: 6px 4px 4px 4px;
            font-size: 11px;
            color: #d6dce6;
        }
        QToolButton#ribbonButton:hover {
            background: #3a3f48;
        }
        QToolButton#ribbonButton:pressed {
            background: #24282f;
        }
        QFrame#viewportShell {
            background: #202329;
            border-top: 1px solid #1d2025;
        }
        QFrame#viewportFrame {
            background: #1a1d22;
            border: 1px solid #333942;
        }
        QDockWidget {
            color: #d0d5dd;
        }
        QLabel#dockTitleText {
            color: #dfe4ec;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.08em;
        }
        QToolButton#dockTitleButton {
            color: #8e97a5;
            border: none;
            background: transparent;
        }
        QToolButton#dockTitleButton:hover {
            color: #ffffff;
            background: #353a42;
        }
        QFrame#panelFrame {
            background: #2b2f36;
            border: 1px solid #3e444e;
            border-radius: 3px;
        }
        QTreeWidget, QListWidget, QTableWidget, QAbstractScrollArea {
            background: #2b2f36;
            border: none;
            outline: none;
            gridline-color: #333842;
        }
        QTreeWidget::viewport, QListWidget::viewport, QTableWidget::viewport {
            background: #2b2f36;
        }
        QHeaderView::section {
            background: #31353d;
            color: #b5becc;
            border: none;
            border-bottom: 1px solid #434a55;
            padding: 7px 8px;
            font-weight: 600;
        }
        QTableCornerButton::section {
            background: #31353d;
            border: none;
        }
        QScrollArea {
            background: #2b2f36;
            border: none;
        }
        QScrollArea > QWidget > QWidget {
            background: #2b2f36;
        }
        QLineEdit {
            background: #31353d;
            border: 1px solid #434a55;
            border-radius: 3px;
            padding: 6px 8px;
            color: #d9dfeb;
        }
        QLineEdit:focus {
            border: 1px solid #5b6472;
        }
        QFrame#entityClassCard {
            background: #26292f;
            border: 1px solid #404650;
            border-radius: 3px;
        }
        QLabel#entityClassLabel {
            color: #eef2f8;
            font-weight: 700;
            background: transparent;
        }
        QLabel#entityTypeLabel {
            color: #9aa4b3;
            background: transparent;
        }
        QWidget#attributeList {
            background: transparent;
        }
        QTreeView::item, QListView::item, QTableView::item {
            padding: 4px;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 10px;
            margin: 2px 2px 2px 0;
        }
        QScrollBar:horizontal {
            background: transparent;
            height: 10px;
            margin: 0 2px 2px 2px;
        }
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: #525a67;
            border-radius: 3px;
            min-height: 24px;
            min-width: 24px;
        }
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
            background: #697385;
        }
        QScrollBar::add-line, QScrollBar::sub-line,
        QScrollBar::add-page, QScrollBar::sub-page {
            background: transparent;
            border: none;
        }
        QStatusBar {
            background: #24272c;
            border-top: 1px solid #1a1c20;
        }
        QStatusBar QLabel {
            color: #97a1af;
            background: transparent;
            border: none;
            padding: 2px 8px;
        }
        QGroupBox {
            background: transparent;
            border: 1px solid #404650;
            border-radius: 3px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox#propertySetCard {
            background: #26292f;
            border: 1px solid #404650;
            border-radius: 3px;
        }
        QGroupBox#propertySetCard::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
            color: #d5dbe5;
        }
        QGroupBox#propertySetCard > QWidget {
            background: #26292f;
        }
        QWidget#inspectorSection {
            background: transparent;
        }
        QWidget#inspectorFilterWrapper {
            background: transparent;
        }
        QWidget#relationshipRow {
            background: transparent;
        }
        QLabel#relationshipIconLabel {
            background: transparent;
        }
        QWidget#inspectorPanel {
            background: #2b2f36;
        }
        QToolButton#inspectorSectionButton {
            background: transparent;
            border: none;
            color: #e1e7f0;
            font-weight: 700;
            text-align: left;
            padding: 2px;
            margin: 0;
        }
        QToolButton#inspectorSectionButton:hover {
            color: #ffffff;
        }
        QToolButton#inspectorSectionButton::menu-indicator {
            image: none;
            width: 0;
        }
        QFrame#inspectorSectionHeader {
            background: #26292f;
        }
        QToolButton#inspectorFilterToggle {
            background: transparent;
            border: none;
            padding: 2px;
        }
        QToolButton#inspectorFilterToggle:hover {
            background: #353a42;
        }
        QWidget#inspectorSectionBody {
            background: transparent;
        }
        QLabel#propertyKeyLabel {
            color: #9aa4b3;
            background: transparent;
        }
        QLabel#propertyValueLabel {
            color: #dce2eb;
            background: transparent;
        }
        QLabel#relationshipValueLabel {
            color: #dce2eb;
            background: transparent;
        }
    )");
}

QToolButton* MockMainWindow::makeRibbonAction(const QString& text, const QString& icon_path) {
    auto* button = new QToolButton(this);
    button->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    button->setIcon(icon_path.endsWith(".svg")
        ? makeTintedSvgIcon(icon_path)
        : QIcon(icon_path));
    button->setIconSize(QSize(20, 20));
    button->setText(text);
    button->setMinimumSize(QSize(68, 54));
    button->setObjectName("ribbonButton");
    button->setAutoRaise(false);
    return button;
}

QWidget* MockMainWindow::makeRibbonGroup(const QString& title, const QList<QToolButton*>& buttons) {
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
    label->setAlignment(Qt::AlignCenter);
    group_layout->addLayout(button_row);
    group_layout->addWidget(label);
    return group;
}

QWidget* MockMainWindow::makeComingSoonPanel(const QString& title) {
    auto* widget = new QWidget(this);
    auto* layout = new QVBoxLayout(widget);
    layout->setContentsMargins(12, 12, 12, 12);
    auto* heading = new QLabel(title, widget);
    heading->setStyleSheet("font-size:14px; font-weight:600; color:#e1e6ee;");
    auto* body = new QLabel("Coming soon", widget);
    body->setAlignment(Qt::AlignCenter);
    body->setStyleSheet("color:#8f98a6;");
    layout->addWidget(heading);
    layout->addStretch(1);
    layout->addWidget(body);
    layout->addStretch(1);
    return widget;
}

void MockMainWindow::setStatusMessage(const QString& mode, const QString& detail) {
    status_mode_label_->setText(mode);
    status_selection_label_->setText(detail);
}

QToolButton* MockMainWindow::makePanelToggle(const QString& text, QDockWidget* dock) {
    auto* button = makeRibbonAction(text, ":/icons/dm_toggle_openings.png");
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

QWidget* MockMainWindow::buildHomeRibbonPage() {
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
    connect(add_model, &QToolButton::clicked, this, &MockMainWindow::onAddFiles);
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

QWidget* MockMainWindow::buildNavigateRibbonPage() {
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

QWidget* MockMainWindow::buildInspectRibbonPage() {
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

QWidget* MockMainWindow::buildPanelsRibbonPage() {
    auto* page = new QFrame(this);
    page->setObjectName("ribbonPage");
    auto* row = new QHBoxLayout(page);
    row->setContentsMargins(2, 4, 2, 4);
    row->setSpacing(0);

    row->addWidget(makeRibbonGroup("DATA", {
        makePanelToggle("Models", models_dock_),
        makePanelToggle("Spatial", spatial_dock_),
        makePanelToggle("Layers", layers_dock_),
        makePanelToggle("Properties", properties_dock_)
    }));
    row->addWidget(makeRibbonGroup("QUERY", {
        makePanelToggle("Views", stored_views_dock_),
        makePanelToggle("Search", search_dock_),
        makePanelToggle("Sheets", spreadsheet_dock_)
    }));
    row->addWidget(makeRibbonGroup("COLLABORATE", {
        makePanelToggle("Clash", clash_dock_),
        makePanelToggle("Issues", issues_dock_)
    }));
    row->addStretch(1);
    return page;
}

void MockMainWindow::setupRibbon() {
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

void MockMainWindow::setupViewport() {
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

void MockMainWindow::setupDocks() {
    auto* models_panel = new QWidget(this);
    auto* models_panel_layout = new QVBoxLayout(models_panel);
    models_panel_layout->setContentsMargins(0, 0, 0, 0);
    models_panel_layout->setSpacing(0);

    auto* models_tree = new QTreeWidget(this);
    models_tree->setColumnCount(2);
    models_tree->setHeaderLabels({"Model", ""});
    models_tree->setIconSize(QSize(16, 16));
    models_tree->setSelectionMode(QAbstractItemView::ExtendedSelection);
    models_tree->setContextMenuPolicy(Qt::CustomContextMenu);
    models_tree->setUniformRowHeights(true);
    models_tree->header()->setStretchLastSection(false);
    models_tree->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    models_tree->header()->setSectionResizeMode(1, QHeaderView::Fixed);
    models_tree->header()->resizeSection(1, 28);
    models_tree->header()->hide();

    auto* local_group = new QTreeWidgetItem(models_tree, {"Local Models", ""});
    local_group->setIcon(0, makePanelSvgIcon(":/icons/folder.svg"));
    local_group->setIcon(1, makePanelSvgIcon(":/icons/eye.svg"));
    local_group->setData(1, Qt::UserRole, true);
    local_group->setSizeHint(0, QSize(0, 24));
    auto* linked_group = new QTreeWidgetItem(models_tree, {"Linked Models", ""});
    linked_group->setIcon(0, makePanelSvgIcon(":/icons/folder.svg"));
    linked_group->setIcon(1, makePanelSvgIcon(":/icons/eye.svg"));
    linked_group->setData(1, Qt::UserRole, true);
    linked_group->setSizeHint(0, QSize(0, 24));

    auto make_model_item = [this](QTreeWidgetItem* parent, const QString& name, bool visible) {
        auto* item = new QTreeWidgetItem(parent, {name, ""});
        item->setIcon(0, makePanelSvgIcon(":/icons/cube.svg"));
        item->setIcon(1, makePanelSvgIcon(visible ? ":/icons/eye-solid.svg" : ":/icons/eye.svg"));
        item->setData(1, Qt::UserRole, visible);
        item->setSizeHint(0, QSize(0, 24));
        return item;
    };

    make_model_item(local_group, "Architecture.ifc", true);
    make_model_item(local_group, "Structure.ifc", true);
    make_model_item(linked_group, "MEP.ifc", false);
    models_tree->expandAll();

    models_panel_layout->addWidget(models_tree);

    connect(models_tree, &QTreeWidget::itemClicked, this, [this](QTreeWidgetItem* item, int column) {
        if (!item || column != 1) return;
        const bool visible = item->data(1, Qt::UserRole).toBool();
        const bool next_visible = !visible;
        item->setData(1, Qt::UserRole, next_visible);
        if (item->childCount() > 0) {
            item->setIcon(1, makePanelSvgIcon(next_visible ? ":/icons/eye.svg" : ":/icons/eye-closed.svg"));
        } else {
            item->setIcon(1, makePanelSvgIcon(next_visible ? ":/icons/eye-solid.svg" : ":/icons/eye-closed.svg"));
        }
        setStatusMessage("Models", next_visible ? "Item shown" : "Item hidden");
    });

    connect(models_tree, &QTreeWidget::customContextMenuRequested, this, [this, models_tree](const QPoint& pos) {
        auto* item = models_tree->itemAt(pos);
        QMenu menu(models_tree);
        if (item && item->childCount() > 0) {
            menu.addAction(makePanelSvgIcon(":/icons/folder-plus.svg"), "Add Group", [this]() {
                setStatusMessage("Models", "Add Group coming soon");
            });
            menu.addAction(makePanelSvgIcon(":/icons/folder-minus.svg"), "Remove Group", [this]() {
                setStatusMessage("Models", "Remove Group coming soon");
            });
        }
        if (item && item->childCount() == 0) {
            menu.addAction(makePanelSvgIcon(":/icons/minus-square.svg"), "Remove Model", [this]() {
                setStatusMessage("Models", "Remove Model coming soon");
            });
        }
        menu.addAction(makePanelSvgIcon(":/icons/intersect.svg"), "Invert Visibility", [this]() {
            setStatusMessage("Models", "Invert visibility coming soon");
        });
        if (!menu.actions().isEmpty()) menu.exec(models_tree->viewport()->mapToGlobal(pos));
    });

    auto* spatial_tree = new QTreeWidget(this);
    spatial_tree->setColumnCount(2);
    spatial_tree->setHeaderLabels({"Spatial Item", ""});
    spatial_tree->setIconSize(QSize(16, 16));
    spatial_tree->setSelectionMode(QAbstractItemView::ExtendedSelection);
    spatial_tree->setUniformRowHeights(true);
    spatial_tree->header()->setStretchLastSection(false);
    spatial_tree->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    spatial_tree->header()->setSectionResizeMode(1, QHeaderView::Fixed);
    spatial_tree->header()->resizeSection(1, 28);
    spatial_tree->header()->hide();

    auto make_spatial_item = [this](QTreeWidgetItem* parent, const QString& name, const QString& icon_path) {
        auto* item = new QTreeWidgetItem(parent, {name, ""});
        item->setIcon(0, makePanelSvgIcon(icon_path));
        item->setIcon(1, makePanelSvgIcon(":/icons/eye.svg"));
        item->setData(1, Qt::UserRole, true);
        item->setSizeHint(0, QSize(0, 24));
        return item;
    };

    auto* site = make_spatial_item(spatial_tree->invisibleRootItem(), "Site A", ":/icons/frame-alt.svg");
    auto* building = make_spatial_item(site, "Building 01", ":/icons/city.svg");
    auto* storey = make_spatial_item(building, "Level 02", ":/icons/planimetry.svg");
    make_spatial_item(storey, "Lobby", ":/icons/square3d-from-center.svg");
    make_spatial_item(storey, "Core", ":/icons/square3d-from-center.svg");
    spatial_tree->expandAll();

    connect(spatial_tree, &QTreeWidget::itemClicked, this, [this](QTreeWidgetItem* item, int column) {
        if (!item || column != 1) return;
        const bool visible = item->data(1, Qt::UserRole).toBool();
        const bool next_visible = !visible;
        item->setData(1, Qt::UserRole, next_visible);
        item->setIcon(1, makePanelSvgIcon(next_visible ? ":/icons/eye.svg" : ":/icons/eye-closed.svg"));
        setStatusMessage("Spatial", next_visible ? "Item shown" : "Item hidden");
    });

    auto* properties_content = new QWidget(this);
    properties_content->setObjectName("inspectorPanel");
    auto* properties_layout = new QVBoxLayout(properties_content);
    properties_layout->setContentsMargins(0, 0, 0, 0);
    properties_layout->setSpacing(12);

    auto* entity_card = new QFrame(properties_content);
    entity_card->setObjectName("entityClassCard");
    auto* entity_layout = new QHBoxLayout(entity_card);
    entity_layout->setContentsMargins(10, 8, 10, 8);
    entity_layout->setSpacing(10);
    auto* entity_icon = new QLabel(entity_card);
    entity_icon->setPixmap(makePanelSvgPixmap(":/icons/cube-dots.svg", QSize(28, 28)));
    entity_icon->setAlignment(Qt::AlignCenter);
    auto* entity_text = new QWidget(entity_card);
    auto* entity_text_layout = new QVBoxLayout(entity_text);
    entity_text_layout->setContentsMargins(0, 0, 0, 0);
    entity_text_layout->setSpacing(2);
    auto* entity_class = new QLabel("IfcWall", entity_text);
    entity_class->setObjectName("entityClassLabel");
    auto* entity_type = new QLabel("SOLIDWALL", entity_text);
    entity_type->setObjectName("entityTypeLabel");
    entity_text_layout->addWidget(entity_class);
    entity_text_layout->addWidget(entity_type);
    entity_layout->addWidget(entity_icon, 0, Qt::AlignVCenter);
    entity_layout->addWidget(entity_text, 1, Qt::AlignVCenter);

    auto* attributes_section = makeInspectorSection(
        "Attributes", "",
        {
            makeAttributeList({{"GlobalId", "2Q$n5SLPP9Q8B7wQKjKfUQ"},
                               {"Name", "Core-EXT-204"},
                               {"Description", "External load-bearing wall"}}, properties_content)
        },
        properties_content);

    auto* properties_section = makeInspectorSection(
        "Properties", "Filter properties or sets",
        {
            makePropertySetPanel("Pset_WallCommon",
                                 {{"Reference", "Core-EXT-204"},
                                  {"Status", "Reviewed"},
                                  {"Fire Rating", "120 min"},
                                  {"LoadBearing", "True"}},
                                 properties_content),
            makePropertySetPanel("Identity Data",
                                 {{"Type", "IfcWall"},
                                  {"Name", "Core-EXT-204"},
                                  {"Owner", "Architecture"},
                                  {"Phase", "Construction"}},
                                 properties_content),
            makePropertySetPanel("BIM Collaboration",
                                 {{"Issue Count", "2 open"},
                                  {"Last Review", "2026-04-30"},
                                  {"Assigned To", "Design Coordination"}},
                                 properties_content)
        },
        properties_content);

    qobject_cast<QVBoxLayout*>(attributes_section->layout())->setSpacing(8);

    auto* relationships_section = makeInspectorSection(
        "Relationships", "",
        {
            makeRelationshipList({{"Type", "Basic Wall: Exterior - 200mm"},
                                  {"Container", "Level 02"}}, properties_content)
        },
        properties_content);

    auto* quantities_section = makeInspectorSection(
        "Quantities", "Filter quantities or sets",
        {
            makePropertySetPanel("BaseQuantities",
                                 {{"Length", "6.20 m"},
                                  {"Height", "3.45 m"},
                                  {"Width", "0.30 m"},
                                  {"Volume", "6.42 m3"}},
                                 properties_content),
            makePropertySetPanel("Finish Quantities",
                                 {{"NetSideArea", "21.39 m2"},
                                  {"GrossArea", "22.10 m2"},
                                  {"Paint Coverage", "42.78 m2"}},
                                 properties_content)
        },
        properties_content);

    auto* entity_wrapper = new QWidget(properties_content);
    entity_wrapper->setObjectName("inspectorSectionBody");
    auto* entity_wrapper_layout = new QVBoxLayout(entity_wrapper);
    entity_wrapper_layout->setContentsMargins(10, 0, 10, 0);
    entity_wrapper_layout->setSpacing(0);
    entity_wrapper_layout->addWidget(entity_card);

    properties_layout->addWidget(entity_wrapper);
    properties_layout->addWidget(attributes_section);
    properties_layout->addWidget(relationships_section);
    properties_layout->addWidget(properties_section);
    properties_layout->addWidget(quantities_section);
    properties_layout->addStretch(1);

    auto* properties_scroll = new QScrollArea(this);
    properties_scroll->setWidgetResizable(true);
    properties_scroll->setFrameShape(QFrame::NoFrame);
    properties_scroll->setWidget(properties_content);

    models_dock_ = makeDock("Models", wrapPanel(models_panel), this, true);
    spatial_dock_ = makeDock("Spatial Hierarchy", wrapPanel(spatial_tree), this);
    properties_dock_ = makeDock("Properties", wrapInspectorPanel(properties_scroll), this);
    layers_dock_ = makeDock("Layers", wrapPanel(makeComingSoonPanel("Layers")), this);
    stored_views_dock_ = makeDock("Stored Views", wrapPanel(makeComingSoonPanel("Stored Views")), this);
    search_dock_ = makeDock("Search and Query", wrapPanel(makeComingSoonPanel("Search and Query")), this);
    spreadsheet_dock_ = makeDock("Spreadsheet", wrapPanel(makeComingSoonPanel("Spreadsheet")), this);
    clash_dock_ = makeDock("Clash", wrapPanel(makeComingSoonPanel("Clash")), this);
    issues_dock_ = makeDock("Issues", wrapPanel(makeComingSoonPanel("Issues")), this);

    addDockWidget(Qt::LeftDockWidgetArea, models_dock_);
    addDockWidget(Qt::LeftDockWidgetArea, spatial_dock_);
    splitDockWidget(models_dock_, spatial_dock_, Qt::Vertical);

    addDockWidget(Qt::RightDockWidgetArea, properties_dock_);
    addDockWidget(Qt::RightDockWidgetArea, layers_dock_);
    addDockWidget(Qt::RightDockWidgetArea, stored_views_dock_);
    addDockWidget(Qt::RightDockWidgetArea, search_dock_);
    addDockWidget(Qt::RightDockWidgetArea, spreadsheet_dock_);
    addDockWidget(Qt::RightDockWidgetArea, clash_dock_);
    addDockWidget(Qt::RightDockWidgetArea, issues_dock_);

    tabifyDockWidget(properties_dock_, layers_dock_);
    tabifyDockWidget(layers_dock_, stored_views_dock_);
    tabifyDockWidget(stored_views_dock_, search_dock_);
    tabifyDockWidget(search_dock_, spreadsheet_dock_);
    tabifyDockWidget(spreadsheet_dock_, clash_dock_);
    tabifyDockWidget(clash_dock_, issues_dock_);
    properties_dock_->raise();

    layers_dock_->hide();
    stored_views_dock_->hide();
    search_dock_->hide();
    spreadsheet_dock_->hide();
    clash_dock_->hide();
    issues_dock_->hide();

    resizeDocks({models_dock_, properties_dock_}, {290, 330}, Qt::Horizontal);
    resizeDocks({models_dock_, spatial_dock_}, {280, 240}, Qt::Vertical);
}

void MockMainWindow::setupStatus() {
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

void MockMainWindow::setupLoader() {
    AppSettings::instance().setLoadDataSource(false);
    loader_ = new SceneLoader(viewport_, this);
    connect(loader_, &SceneLoader::loadStarted, this, &MockMainWindow::onLoadStarted);
    connect(loader_, &SceneLoader::loadedFromSidecar, this, &MockMainWindow::onLoadedFromSidecar);
    connect(loader_, &SceneLoader::loadedFromStream, this, &MockMainWindow::onLoadedFromStream);
    connect(loader_, &SceneLoader::loadCancelled, this, &MockMainWindow::onLoadCancelled);
    connect(loader_, &SceneLoader::loadError, this, &MockMainWindow::onLoadError);
    connect(loader_, &SceneLoader::allLoadsFinished, this, &MockMainWindow::onAllLoadsFinished);

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

void MockMainWindow::addFiles(const QStringList& paths) {
    if (paths.isEmpty()) return;
    loader_->addFiles(paths);
}

QString MockMainWindow::formatElapsed(qint64 ms) const {
    return (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
}

void MockMainWindow::onAddFiles() {
    const QStringList paths = QFileDialog::getOpenFileNames(
        this, "Add IFC Files", QString(),
        "IFC Viewer Cache (*.ifcview)");
    addFiles(paths);
}

void MockMainWindow::onLoadStarted(uint32_t /*mid*/, QString display_name) {
    status_mode_label_->setText("Loading");
    status_selection_label_->setText(display_name);
}

void MockMainWindow::onLoadedFromSidecar(uint32_t mid, qint64 elapsed_ms) {
    status_mode_label_->setText("Loaded");
    status_selection_label_->setText(
        QString("%1 from cache in %2")
            .arg(loader_->displayName(mid))
            .arg(formatElapsed(elapsed_ms)));
}

void MockMainWindow::onLoadedFromStream(uint32_t mid, qint64 elapsed_ms) {
    status_mode_label_->setText("Loaded");
    status_selection_label_->setText(
        QString("%1 streamed in %2")
            .arg(loader_->displayName(mid))
            .arg(formatElapsed(elapsed_ms)));
}

void MockMainWindow::onLoadCancelled(uint32_t mid) {
    status_mode_label_->setText("Cancelled");
    status_selection_label_->setText(loader_->displayName(mid));
}

void MockMainWindow::onLoadError(uint32_t /*mid*/, QString message) {
    status_mode_label_->setText("Error");
    status_selection_label_->setText(message);
    QMessageBox::warning(this, "IfcInterfaceMockup", message);
}

void MockMainWindow::onAllLoadsFinished() {
    status_mode_label_->setText("Loaded");
    status_selection_label_->setText(QString("%1 model(s)").arg(loader_->modelCount()));
}
