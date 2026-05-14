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

#include "Dialog.h"

#include "Style.h"
#include "Tabs.h"

#include <QDialog>
#include <QFrame>
#include <QScrollArea>
#include <QVBoxLayout>

namespace ifcviewerfull::components {

Dialog::Dialog(QWidget* parent, bool scrollable)
    : QDialog(parent)
{
    auto* outer_layout = new QVBoxLayout(this);
    outer_layout->setContentsMargins(style::metrics::padding,
                                     style::metrics::padding,
                                     style::metrics::padding,
                                     style::metrics::padding);
    outer_layout->setSpacing(0);

    auto* frame = new QFrame(this);
    frame->setObjectName("panel");
    auto* frame_layout = new QVBoxLayout(frame);
    frame_layout->setContentsMargins(0,
                                     style::metrics::section_body_padding,
                                     0,
                                     style::metrics::section_body_padding);
    frame_layout->setSpacing(0);

    auto* scroll = new QScrollArea(frame);
    scroll->setWidgetResizable(true);
    scroll->setFrameShape(QFrame::NoFrame);

    auto* scroll_body = new QWidget(scroll);
    scroll_body->setObjectName("panelScrollBody");
    body_layout_ = new QVBoxLayout(scroll_body);
    body_layout_->setContentsMargins(0, 0, 0, 0);
    body_layout_->setSpacing(style::metrics::section_body_padding);
    body_layout_->setAlignment(Qt::AlignTop);

    scroll->setWidget(scroll_body);
    frame_layout->addWidget(scroll, scrollable ? 1 : 0);

    auto* footer = new QWidget(frame);
    footer_layout_ = new QVBoxLayout(footer);
    footer_layout_->setContentsMargins(style::metrics::section_body_padding,
                                       style::metrics::section_body_padding,
                                       style::metrics::section_body_padding,
                                       0);
    footer_layout_->setSpacing(style::metrics::section_body_padding);
    footer_layout_->setAlignment(Qt::AlignTop);
    frame_layout->addWidget(footer);

    outer_layout->addWidget(frame);
}

void Dialog::addBodyWidget(QWidget* widget) {
    body_layout_->addWidget(widget);
}

void Dialog::addFooterWidget(QWidget* widget) {
    footer_layout_->addWidget(widget);
}

TabbedDialog::TabbedDialog(QWidget* parent)
    : QDialog(parent)
{
    auto* outer_layout = new QVBoxLayout(this);
    outer_layout->setContentsMargins(style::metrics::padding,
                                     style::metrics::padding,
                                     style::metrics::padding,
                                     style::metrics::padding);
    outer_layout->setSpacing(0);

    auto* frame = new QFrame(this);
    frame->setObjectName("panel");
    auto* frame_layout = new QVBoxLayout(frame);
    frame_layout->setContentsMargins(0,
                                     style::metrics::section_body_padding,
                                     0,
                                     style::metrics::section_body_padding);
    frame_layout->setSpacing(0);

    tabs_ = new TabWidget(frame);
    frame_layout->addWidget(tabs_, 1);

    auto* footer = new QWidget(frame);
    footer_layout_ = new QVBoxLayout(footer);
    footer_layout_->setContentsMargins(style::metrics::section_body_padding,
                                       style::metrics::section_body_padding,
                                       style::metrics::section_body_padding,
                                       0);
    footer_layout_->setSpacing(style::metrics::section_body_padding);
    footer_layout_->setAlignment(Qt::AlignTop);
    frame_layout->addWidget(footer);

    outer_layout->addWidget(frame);
}

void TabbedDialog::addTab(const QString& title, QWidget* widget) {
    auto* scroll = new QScrollArea(tabs_);
    scroll->setWidgetResizable(true);
    scroll->setFrameShape(QFrame::NoFrame);

    auto* scroll_body = new QWidget(scroll);
    scroll_body->setObjectName("panelScrollBody");
    auto* layout = new QVBoxLayout(scroll_body);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(style::metrics::section_body_padding);
    layout->setAlignment(Qt::AlignTop);
    layout->addWidget(widget);

    scroll->setWidget(scroll_body);
    tabs_->addTab(scroll, title);
}

void TabbedDialog::addFooterWidget(QWidget* widget) {
    footer_layout_->addWidget(widget);
}

} // namespace ifcviewerfull::components
