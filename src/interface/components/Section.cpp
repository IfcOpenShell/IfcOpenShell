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

#include "Section.h"

#include "Style.h"

#include <QFrame>
#include <QHBoxLayout>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcinterface::components {

Section::Section(const QString& title, SectionHeaderMode header_mode, QWidget* parent)
    : QWidget(parent)
{
    setObjectName("panelSection");
    auto* layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(style::metrics::padding);

    if (header_mode == SectionHeaderMode::Visible) {
        auto* header = new QFrame(this);
        header->setObjectName("panelSectionHeader");
        header_layout_ = new QHBoxLayout(header);
        header_layout_->setContentsMargins(0, 0, 0, 0);
        header_layout_->setSpacing(style::metrics::padding);

        toggle_button_ = new QToolButton(header);
        toggle_button_->setObjectName("panelSectionHeaderButton");
        toggle_button_->setText(title);
        toggle_button_->setCheckable(true);
        toggle_button_->setChecked(true);
        toggle_button_->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
        toggle_button_->setArrowType(Qt::DownArrow);
        header_layout_->addWidget(toggle_button_);
        header_layout_->addStretch(1);

        layout->addWidget(header);

        connect(toggle_button_, &QToolButton::toggled, this, [this](bool expanded) {
            toggle_button_->setArrowType(expanded ? Qt::DownArrow : Qt::RightArrow);
            body_->setVisible(expanded);
        });
    }

    body_ = new QWidget(this);
    body_->setObjectName("panelSectionBody");
    body_layout_ = new QVBoxLayout(body_);
    body_layout_->setContentsMargins(style::metrics::section_body_padding,
                                     0,
                                     style::metrics::section_body_padding,
                                     0);
    body_layout_->setSpacing(style::metrics::padding);
    layout->addWidget(body_);
}

void Section::addBodyWidget(QWidget* widget) {
    body_layout_->addWidget(widget);
}

void Section::clearBody() {
    while (auto* item = body_layout_->takeAt(0)) {
        if (auto* widget = item->widget()) widget->deleteLater();
        delete item;
    }
}

void Section::addHeaderWidget(QWidget* widget) {
    if (!header_layout_) return;
    header_layout_->addWidget(widget);
}

bool Section::isExpanded() const {
    return !toggle_button_ || toggle_button_->isChecked();
}

void Section::setExpanded(bool expanded) {
    if (!toggle_button_) return;
    toggle_button_->setChecked(expanded);
}

} // namespace ifcinterface::components
