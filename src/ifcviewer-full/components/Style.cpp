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

#include "Style.h"

#include "../ViewerSettings.h"

namespace ifcviewerfull::components::style {

QString buildAppStyleSheet() {
    const auto& theme = ifcviewerfull::ViewerSettings::instance();
    QString stylesheet = QStringLiteral(R"(
        QMainWindow#appWindow {
            background: ${app_background};
            color: ${primary_text};
            selection-background-color: ${selection_background};
            selection-color: ${selection_text};
        }
        QDialog#appDialog {
            background: ${app_background};
            color: ${primary_text};
        }
        QMessageBox,
        QMessageBox QWidget,
        QMessageBox QLabel {
            background: ${app_background};
            color: ${primary_text};
        }
        QFileDialog,
        QFileDialog QWidget,
        QFileDialog QStackedWidget,
        QFileDialog QSplitter {
            background: ${app_background};
            color: ${primary_text};
        }
        QTabBar#appTabBar {
            background: ${tab_bar_background};
        }
        QTabBar#appTabBar::tab {
            background: ${tab_background};
            color: ${secondary_text};
            padding: 8px 14px;
            margin-right: 2px;
            border-bottom: 2px solid transparent;
        }
        QTabBar#appTabBar::tab:selected {
            color: ${primary_text};
            border-bottom: 2px solid ${selection_background};
        }
        QTabBar#appTabBar::tab:hover {
            color: ${hover_text};
        }
        QFrame#ribbonBand {
            background: ${ribbon_background};
            border-top: 1px solid ${border};
        }
        QTabWidget#appTabWidget::pane {
            border: none;
            background: transparent;
        }
        QFrame#ribbonPage {
            background: transparent;
        }
        QFrame#ribbonGroup {
            background: transparent;
            border-right: 1px solid ${border};
        }
        QFrame#ribbonGroup[separator="false"] {
            border-right: none;
        }
        QLabel#ribbonGroupLabel {
            font-size: ${font_small}px;
            font-weight: 600;
        }
        QToolButton#ribbonButton {
            background: transparent;
            border: none;
            padding: 6px 4px 4px 4px;
            color: ${primary_text};
        }
        QToolButton#ribbonButton:hover {
            background: ${ribbon_button_hover};
        }
        QToolButton#ribbonButton:pressed {
            background: ${ribbon_button_pressed};
        }
        QFrame#viewportShell {
            background: ${viewport_shell_background};
            border-top: none;
        }
        QFrame#viewportFrame {
            border: 1px solid ${border};
        }
        QDockWidget {
            color: ${primary_text};
        }
        QLabel {
            color: ${primary_text};
            background: transparent;
        }
        QAbstractItemView,
        QTreeWidget,
        QListWidget,
        QTableWidget,
        QLineEdit,
        QComboBox,
        QSpinBox,
        QDoubleSpinBox,
        QCheckBox,
        QRadioButton,
        QPushButton,
        QToolButton {
            color: ${primary_text};
        }
        QLabel[textRole="secondary"] {
            color: ${secondary_text};
        }
        QLabel[textRole="disabled"] {
            color: ${disabled_text};
        }
        QLabel[textRole="warning"] {
            color: ${warning_text};
        }
        QLabel#panelTitleText {
            color: ${primary_text};
            font-size: ${font_small}px;
            font-weight: 600;
        }
        QToolButton#panelTitleButton {
            border: none;
            background: transparent;
        }
        QToolButton#panelTitleButton:hover {
            color: ${hover_text};
            background: ${ribbon_button_hover};
        }
        QFrame#panel {
            background: ${panel_background};
            border: 1px solid ${border};
            border-radius: ${panel_radius}px;
        }
        QTreeWidget, QListWidget, QTableWidget, QAbstractScrollArea {
            background: ${panel_background};
            border: none;
            outline: none;
            gridline-color: ${border};
        }
        QTableWidget#modelCoordinatesTable {
            font-size: ${font_small}px;
        }
        QTableWidget#modelCoordinatesTable QHeaderView::section {
            font-size: ${font_small}px;
        }
        QTreeWidget::viewport, QListWidget::viewport, QTableWidget::viewport {
            background: ${panel_background};
        }
        QHeaderView::section {
            background: ${control_background};
            color: ${primary_text};
            border: none;
            border-bottom: 1px solid ${border};
            padding: 7px 8px;
            font-weight: 600;
        }
        QTableCornerButton::section {
            background: ${control_background};
            border: none;
        }
        QScrollArea {
            background: ${panel_background};
            border: none;
        }
        QScrollArea > QWidget > QWidget {
            background: ${panel_background};
        }
        QLineEdit {
            background: ${control_background};
            border: 1px solid ${border};
            border-radius: ${panel_radius}px;
            padding: ${padding}px ${padding}px;
            color: ${primary_text};
        }
        QLineEdit:focus {
            border: 1px solid ${control_border_focus};
        }
        QComboBox {
            background: ${control_background};
            border: 1px solid ${border};
            border-radius: ${panel_radius}px;
            padding: ${padding}px 24px ${padding}px ${padding}px;
        }
        QComboBox:focus {
            border: 1px solid ${control_border_focus};
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 18px;
            border: none;
            background: transparent;
        }
        QComboBox::down-arrow {
            width: 0px;
            height: 0px;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid ${secondary_text};
            margin-right: 4px;
        }
        QComboBox QAbstractItemView {
            background: ${panel_background};
            border: 1px solid ${border};
            selection-background-color: ${selection_background};
            selection-color: ${selection_text};
        }
        QSpinBox, QDoubleSpinBox {
            background: ${control_background};
            border: 1px solid ${border};
            border-radius: ${panel_radius}px;
            padding: ${padding}px 24px ${padding}px ${padding}px;
        }
        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid ${control_border_focus};
        }
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            subcontrol-origin: padding;
            width: 18px;
            border: none;
            background: transparent;
        }
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            subcontrol-position: top right;
        }
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            subcontrol-position: bottom right;
        }
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
            width: 0px;
            height: 0px;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 5px solid ${secondary_text};
        }
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
            width: 0px;
            height: 0px;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid ${secondary_text};
        }
        QCheckBox {
            background: transparent;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid ${border};
            border-radius: ${panel_radius}px;
            background: ${control_background};
        }
        QCheckBox::indicator:hover {
            background: ${ribbon_button_hover};
        }
        QCheckBox::indicator:checked {
            border: 1px solid ${selection_background};
            background: ${selection_background};
        }
        QRadioButton {
            background: transparent;
            color: ${primary_text};
            spacing: 8px;
            padding: 2px 0;
        }
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid ${border};
            border-radius: 8px;
            background: ${control_background};
        }
        QRadioButton::indicator:hover {
            background: ${ribbon_button_hover};
        }
        QRadioButton::indicator:checked {
            border: 1px solid ${selection_background};
            background: ${selection_background};
        }
        QRadioButton::indicator:unchecked {
            background: ${control_background};
        }
        QPushButton {
            background: ${control_background};
            border: 1px solid ${border};
            border-radius: ${panel_radius}px;
            padding: ${padding}px ${padding}px;
        }
        QPushButton:hover {
            background: ${ribbon_button_hover};
        }
        QPushButton:pressed {
            background: ${ribbon_button_pressed};
        }
        QMenu {
            background: ${panel_background};
            color: ${primary_text};
            border: 1px solid ${border};
            padding: 4px;
        }
        QMenu::item {
            background: transparent;
            color: ${primary_text};
            padding: 6px 24px 6px 10px;
            border-radius: ${panel_radius}px;
        }
        QMenu::item:selected {
            background: ${selection_background};
            color: ${selection_text};
        }
        QMenu::item:disabled {
            color: ${disabled_text};
        }
        QMenu::separator {
            height: 1px;
            background: ${border};
            margin: 4px 8px;
        }
        QMenu::icon {
            padding-left: 2px;
        }
        QFrame#entityClassBox,
        QGroupBox#propertySetBox {
            background: ${box_background};
            border: 1px solid ${border};
            border-radius: ${panel_radius}px;
        }
        QLabel#entityClassLabel {
            color: ${primary_text};
            font-weight: 700;
            background: transparent;
        }
        QWidget#keyValueTable {
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
            background: ${scroll_handle};
            border-radius: ${panel_radius}px;
            min-height: 24px;
            min-width: 24px;
        }
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
            background: ${scroll_handle_hover};
        }
        QScrollBar::add-line, QScrollBar::sub-line,
        QScrollBar::add-page, QScrollBar::sub-page {
            background: transparent;
            border: none;
        }
        QStatusBar {
            background: ${status_background};
        }
        QStatusBar QLabel {
            color: ${secondary_text};
            background: transparent;
            border: none;
            padding: 2px 8px;
        }
        QGroupBox {
            background: transparent;
            border: 1px solid ${border};
            border-radius: ${panel_radius}px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox#propertySetBox::title {
            subcontrol-origin: margin;
            left: ${padding}px;
            padding: 0 4px;
            color: ${primary_text};
        }
        QGroupBox#propertySetBox > QWidget {
            background: ${box_background};
        }
        QWidget#panelSection {
            background: transparent;
        }
        QWidget#panelSectionFilterWrapper {
            background: transparent;
        }
        QLabel#keyValueTrailingIconLabel {
            background: transparent;
        }
        QWidget#panelScrollBody {
            background: ${panel_background};
        }
        QFrame#panelSectionHeader {
            background: ${section_header_background};
        }
        QToolButton#panelSectionHeaderButton {
            background: transparent;
            border: none;
            color: ${primary_text};
            font-weight: 700;
            text-align: left;
            padding: ${section_header_padding}px;
            margin: 0;
        }
        QToolButton#panelSectionHeaderButton:hover {
            color: ${hover_text};
        }
        QToolButton#panelSectionHeaderButton::menu-indicator {
            image: none;
            width: 0;
        }
        QToolButton#panelSectionFilterToggle {
            background: transparent;
            border: none;
            padding: ${section_header_padding}px;
        }
        QToolButton#panelSectionFilterToggle:hover {
            background: ${ribbon_button_hover};
        }
        QWidget#panelSectionBody {
            background: transparent;
        }
        QLabel#keyValueValueLabel {
            color: ${primary_text};
            background: transparent;
        }
    )");

    stylesheet.replace("${panel_radius}", QString::number(metrics::panel_radius));
    stylesheet.replace("${padding}", QString::number(metrics::padding));
    stylesheet.replace("${section_header_padding}", QString::number(metrics::section_header_padding));
    stylesheet.replace("${font_small}", QString::number(typography::small));

    stylesheet.replace("${app_background}", theme.color("app_background"));
    stylesheet.replace("${border}", theme.color("border"));
    stylesheet.replace("${selection_background}", theme.color("selection_background"));
    stylesheet.replace("${selection_text}", theme.color("selection_text"));
    stylesheet.replace("${tab_bar_background}", theme.color("tab_bar_background"));
    stylesheet.replace("${tab_background}", theme.color("tab_background"));
    stylesheet.replace("${hover_text}", theme.color("hover_text"));
    stylesheet.replace("${ribbon_background}", theme.color("ribbon_background"));
    stylesheet.replace("${ribbon_button_hover}", theme.color("ribbon_button_hover"));
    stylesheet.replace("${ribbon_button_pressed}", theme.color("ribbon_button_pressed"));
    stylesheet.replace("${viewport_shell_background}", theme.color("viewport_shell_background"));
    stylesheet.replace("${viewport_background}", theme.color("viewport_background"));
    stylesheet.replace("${panel_background}", theme.color("panel_background"));
    stylesheet.replace("${control_background}", theme.color("control_background"));
    stylesheet.replace("${control_border_focus}", theme.color("control_border_focus"));
    stylesheet.replace("${box_background}", theme.color("box_background"));
    stylesheet.replace("${scroll_handle}", theme.color("scroll_handle"));
    stylesheet.replace("${scroll_handle_hover}", theme.color("scroll_handle_hover"));
    stylesheet.replace("${status_background}", theme.color("status_background"));
    stylesheet.replace("${section_header_background}", theme.color("section_header_background"));

    stylesheet.replace("${primary_text}", theme.color("primary_text"));
    stylesheet.replace("${secondary_text}", theme.color("secondary_text"));
    stylesheet.replace("${disabled_text}", theme.color("disabled_text"));
    stylesheet.replace("${warning_text}", theme.color("warning_text"));

    return stylesheet;
}

} // namespace ifcviewerfull::components::style
