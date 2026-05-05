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

#include "SvgIcon.h"

#include <QFrame>
#include <QHBoxLayout>
#include <QLineEdit>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcinterface::components {

namespace {

QWidget* makeSectionFilterField(const QString& placeholder, QWidget* parent = nullptr) {
    auto* field = new QLineEdit(parent);
    field->setPlaceholderText(placeholder);
    field->setClearButtonEnabled(true);
    field->addAction(icons::makePanelSvgIcon(":/icons/filter.svg"), QLineEdit::LeadingPosition);
    return field;
}

} // namespace

Section::Section(const QString& title, SectionHeaderMode header_mode,
                 const QString& filter_placeholder, QWidget* parent)
    : QWidget(parent)
{
    setObjectName("panelSection");
    auto* layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(6);

    if (header_mode == SectionHeaderMode::Visible) {
        auto* header = new QFrame(this);
        header->setObjectName("panelSectionHeader");
        auto* header_layout = new QHBoxLayout(header);
        header_layout->setContentsMargins(0, 0, 0, 0);
        header_layout->setSpacing(6);

        auto* toggle = new QToolButton(header);
        toggle->setObjectName("panelSectionHeaderButton");
        toggle->setText(title);
        toggle->setCheckable(true);
        toggle->setChecked(true);
        toggle->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
        toggle->setArrowType(Qt::DownArrow);
        header_layout->addWidget(toggle);
        header_layout->addStretch(1);

        if (!filter_placeholder.isEmpty()) {
            auto* filter_toggle = new QToolButton(header);
            filter_toggle->setObjectName("panelSectionFilterToggle");
            filter_toggle->setCheckable(true);
            filter_toggle->setIcon(icons::makePanelSvgIcon(":/icons/filter.svg"));
            filter_toggle->setAutoRaise(true);
            header_layout->addWidget(filter_toggle);

            filter_field_ = qobject_cast<QLineEdit*>(makeSectionFilterField(filter_placeholder, this));
            filter_field_->setVisible(false);
            connect(filter_toggle, &QToolButton::toggled, filter_field_, [this](bool visible) {
                filter_field_->setVisible(visible);
                if (visible) filter_field_->setFocus();
            });
        }

        layout->addWidget(header);
        if (filter_field_) {
            auto* filter_wrapper = new QWidget(this);
            filter_wrapper->setObjectName("panelSectionFilterWrapper");
            auto* filter_wrapper_layout = new QVBoxLayout(filter_wrapper);
            filter_wrapper_layout->setContentsMargins(10, 0, 10, 0);
            filter_wrapper_layout->setSpacing(0);
            filter_wrapper_layout->addWidget(filter_field_);
            layout->addWidget(filter_wrapper);
        }

        connect(toggle, &QToolButton::toggled, this, [this, toggle](bool expanded) {
            toggle->setArrowType(expanded ? Qt::DownArrow : Qt::RightArrow);
            body_->setVisible(expanded);
            if (filter_field_) {
                auto* wrapper = filter_field_->parentWidget();
                if (wrapper) wrapper->setVisible(expanded && filter_field_->isVisible());
            }
        });
    } else if (!filter_placeholder.isEmpty()) {
        filter_field_ = qobject_cast<QLineEdit*>(makeSectionFilterField(filter_placeholder, this));
        auto* filter_wrapper = new QWidget(this);
        filter_wrapper->setObjectName("panelSectionFilterWrapper");
        auto* filter_wrapper_layout = new QVBoxLayout(filter_wrapper);
        filter_wrapper_layout->setContentsMargins(8, 0, 8, 0);
        filter_wrapper_layout->setSpacing(0);
        filter_wrapper_layout->addWidget(filter_field_);
        layout->addWidget(filter_wrapper);
    }

    body_ = new QWidget(this);
    body_->setObjectName("panelSectionBody");
    body_layout_ = new QVBoxLayout(body_);
    if (header_mode == SectionHeaderMode::Visible) {
        body_layout_->setContentsMargins(10, 6, 10, 0);
    } else {
        body_layout_->setContentsMargins(8, 0, 8, 0);
    }
    body_layout_->setSpacing(6);
    layout->addWidget(body_);
}

void Section::addBodyWidget(QWidget* widget) {
    body_layout_->addWidget(widget);
}

} // namespace ifcinterface::components
