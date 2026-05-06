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
    return QString(R"(
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
        QFrame#panel {
            background: #2b2f36;
            border: 1px solid #3e444e;
            border-radius: %1px;
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
            border-radius: %1px;
            padding: %2px %3px;
            color: #d9dfeb;
        }
        QLineEdit:focus {
            border: 1px solid #5b6472;
        }
        QFrame#entityClassCard {
            background: #26292f;
            border: 1px solid #404650;
            border-radius: %1px;
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
            background: #525a67;
            border-radius: %1px;
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
            border-radius: %1px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox#propertySetCard {
            background: #26292f;
            border: 1px solid #404650;
            border-radius: %1px;
        }
        QGroupBox#propertySetCard::title {
            subcontrol-origin: margin;
            left: %4px;
            padding: 0 4px;
            color: #d5dbe5;
        }
        QGroupBox#propertySetCard > QWidget {
            background: #26292f;
        }
        QWidget#panelSection {
            background: transparent;
        }
        QWidget#panelSectionFilterWrapper {
            background: transparent;
        }
        QWidget#relationshipRow {
            background: transparent;
        }
        QLabel#relationshipIconLabel {
            background: transparent;
        }
        QWidget#panelScrollBody {
            background: #2b2f36;
        }
        QFrame#panelSectionHeader {
            background: #26292f;
        }
        QToolButton#panelSectionHeaderButton {
            background: transparent;
            border: none;
            color: #e1e7f0;
            font-weight: 700;
            text-align: left;
            padding: %5px;
            margin: 0;
        }
        QToolButton#panelSectionHeaderButton:hover {
            color: #ffffff;
        }
        QToolButton#panelSectionHeaderButton::menu-indicator {
            image: none;
            width: 0;
        }
        QToolButton#panelSectionFilterToggle {
            background: transparent;
            border: none;
            padding: %5px;
        }
        QToolButton#panelSectionFilterToggle:hover {
            background: #353a42;
        }
        QWidget#panelSectionBody {
            background: transparent;
        }
        QLabel#propertyKeyLabel {
            color: #9aa4b3;
            background: transparent;
        }
        QLabel#keyValueValueLabel {
            color: #dce2eb;
            background: transparent;
        }
    )")
        .arg(metrics::panel_radius)
        .arg(metrics::control_padding_y)
        .arg(metrics::control_padding_x)
        .arg(metrics::card_padding)
        .arg(metrics::section_header_padding);
}

} // namespace ifcinterface::components::style
