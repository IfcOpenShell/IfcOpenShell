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

namespace ifcinterface::components::style {

QString buildAppStyleSheet() {
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
        QFrame#ribbonShell {
            background: ${ribbon_shell_background};
            border-bottom: 1px solid ${border};
        }
        QTabBar::tab {
            background: transparent;
            color: ${secondary_text};
            padding: 8px 14px;
            margin-right: 2px;
            border-bottom: 2px solid transparent;
        }
        QTabBar::tab:selected {
            color: ${primary_text};
            border-bottom: 2px solid ${selection_background};
        }
        QTabBar::tab:hover {
            color: ${ribbon_tab_hover_text};
        }
        QFrame#ribbonBand {
            background: ${ribbon_band_background};
            border-top: 1px solid ${border};
        }
        QTabWidget::pane {
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
        QLabel#ribbonGroupLabel {
            font-size: 9px;
            font-weight: 600;
            letter-spacing: 0.08em;
        }
        QToolButton#ribbonButton {
            background: transparent;
            border: none;
            padding: 6px 4px 4px 4px;
            font-size: 11px;
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
            background: ${viewport_background};
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
        QSpinBox,
        QDoubleSpinBox,
        QCheckBox,
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
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.08em;
        }
        QToolButton#panelTitleButton {
            color: ${panel_title_button};
            border: none;
            background: transparent;
        }
        QToolButton#panelTitleButton:hover {
            color: ${ribbon_tab_hover_text};
            background: ${panel_title_button_hover};
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
        QSpinBox, QDoubleSpinBox {
            background: ${control_background};
            border: 1px solid ${border};
            border-radius: ${panel_radius}px;
            padding: ${padding}px ${padding}px;
        }
        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid ${control_border_focus};
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
            color: ${ribbon_tab_hover_text};
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
            background: ${panel_title_button_hover};
        }
        QWidget#panelSectionBody {
            background: transparent;
        }
        QLabel#keyValueValueLabel {
            color: ${key_value_value_text};
            background: transparent;
        }
    )");

    stylesheet.replace("${panel_radius}", QString::number(metrics::panel_radius));
    stylesheet.replace("${padding}", QString::number(metrics::padding));
    stylesheet.replace("${section_header_padding}", QString::number(metrics::section_header_padding));

    stylesheet.replace("${app_background}", palette::app_background);
    stylesheet.replace("${border}", palette::border);
    stylesheet.replace("${selection_background}", palette::selection_background);
    stylesheet.replace("${selection_text}", palette::selection_text);
    stylesheet.replace("${ribbon_shell_background}", palette::ribbon_shell_background);
    stylesheet.replace("${ribbon_tab_hover_text}", palette::ribbon_tab_hover_text);
    stylesheet.replace("${ribbon_band_background}", palette::ribbon_band_background);
    stylesheet.replace("${ribbon_button_hover}", palette::ribbon_button_hover);
    stylesheet.replace("${ribbon_button_pressed}", palette::ribbon_button_pressed);
    stylesheet.replace("${viewport_shell_background}", palette::viewport_shell_background);
    stylesheet.replace("${viewport_background}", palette::viewport_background);
    stylesheet.replace("${panel_title_button}", palette::panel_title_button);
    stylesheet.replace("${panel_title_button_hover}", palette::panel_title_button_hover);
    stylesheet.replace("${panel_background}", palette::panel_background);
    stylesheet.replace("${control_background}", palette::control_background);
    stylesheet.replace("${control_border_focus}", palette::control_border_focus);
    stylesheet.replace("${box_background}", palette::box_background);
    stylesheet.replace("${scroll_handle}", palette::scroll_handle);
    stylesheet.replace("${scroll_handle_hover}", palette::scroll_handle_hover);
    stylesheet.replace("${status_background}", palette::status_background);
    stylesheet.replace("${section_header_background}", palette::section_header_background);
    stylesheet.replace("${key_value_value_text}", palette::key_value_value_text);

    stylesheet.replace("${primary_text}", palette::primary_text);
    stylesheet.replace("${secondary_text}", palette::secondary_text);
    stylesheet.replace("${disabled_text}", palette::disabled_text);
    stylesheet.replace("${warning_text}", palette::warning_text);

    return stylesheet;
}

} // namespace ifcinterface::components::style
