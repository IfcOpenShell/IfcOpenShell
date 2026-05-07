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

#include "Widget.h"

#include "../../components/KeyValueTable.h"
#include "../../components/Section.h"
#include "../../components/Style.h"
#include "../../components/SvgIcon.h"

#include <QFrame>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QToolButton>
#include <QVBoxLayout>

namespace {

void clearLayout(QVBoxLayout* layout) {
    while (auto* item = layout->takeAt(0)) {
        if (auto* widget = item->widget()) widget->deleteLater();
        delete item;
    }
}

QWidget* makePropertySetPanel(const ifcinterface::panels::properties::PropertySet& property_set, QWidget* parent = nullptr) {
    auto* group = new QGroupBox(property_set.title, parent);
    group->setObjectName("propertySetBox");
    auto* layout = new QVBoxLayout(group);
    layout->setContentsMargins(10, 10, 10, 10);
    layout->setSpacing(0);

    QList<ifcinterface::components::KeyValueTableRow> rows;
    for (const auto& row : property_set.rows) {
        rows.append({row.key, row.value, "keyValueValueLabel", "", "", 0});
    }
    layout->addWidget(new ifcinterface::components::KeyValueTable(rows, group));
    return group;
}

QWidget* makeAttributeList(const QList<ifcinterface::panels::properties::KeyValueRow>& rows, QWidget* parent = nullptr) {
    QList<ifcinterface::components::KeyValueTableRow> table_rows;
    for (const auto& row : rows) {
        table_rows.append({row.key, row.value, "keyValueValueLabel", "", "", 0});
    }
    return new ifcinterface::components::KeyValueTable(table_rows, parent);
}

QWidget* makeRelationshipList(const QList<ifcinterface::panels::properties::RelationshipRow>& rows, QWidget* parent = nullptr) {
    QList<ifcinterface::components::KeyValueTableRow> table_rows;
    for (const auto& row_data : rows) {
        table_rows.append({row_data.key,
                           row_data.value,
                           "keyValueValueLabel",
                           ":/icons/cursor-pointer.svg",
                           "keyValueTrailingIconLabel",
                           72});
    }
    return new ifcinterface::components::KeyValueTable(table_rows, parent);
}

QWidget* makeFilterWrapper(QLineEdit** field_out, QWidget* parent = nullptr) {
    auto* wrapper = new QWidget(parent);
    wrapper->setObjectName("panelSectionFilterWrapper");
    auto* layout = new QVBoxLayout(wrapper);
    layout->setContentsMargins(ifcinterface::components::style::metrics::section_body_padding,
                               0,
                               ifcinterface::components::style::metrics::section_body_padding,
                               0);
    layout->setSpacing(0);

    auto* field = new QLineEdit(wrapper);
    field->setClearButtonEnabled(true);
    field->addAction(ifcinterface::components::icons::makeSvgIcon(":/icons/filter.svg"), QLineEdit::LeadingPosition);
    field->setVisible(false);
    layout->addWidget(field);

    if (field_out) *field_out = field;
    return wrapper;
}

QFrame* makeEntityBox(const ifcinterface::panels::properties::EntitySummary& entity, QWidget* parent = nullptr) {
    auto* entity_box = new QFrame(parent);
    entity_box->setObjectName("entityClassBox");
    auto* entity_layout = new QHBoxLayout(entity_box);
    entity_layout->setContentsMargins(10, 8, 10, 8);
    entity_layout->setSpacing(10);

    auto* entity_icon = new QLabel(entity_box);
    entity_icon->setPixmap(ifcinterface::components::icons::makeSvgPixmap(":/icons/cube-dots.svg", QSize(28, 28)));
    entity_icon->setAlignment(Qt::AlignCenter);

    auto* entity_text = new QWidget(entity_box);
    auto* entity_text_layout = new QVBoxLayout(entity_text);
    entity_text_layout->setContentsMargins(0, 0, 0, 0);
    entity_text_layout->setSpacing(2);

    auto* entity_class_label = new QLabel(entity.entity_class, entity_text);
    entity_class_label->setObjectName("entityClassLabel");
    auto* entity_type_label = new QLabel(entity.predefined_type, entity_text);
    entity_type_label->setProperty("textRole", "secondary");

    entity_text_layout->addWidget(entity_class_label);
    entity_text_layout->addWidget(entity_type_label);
    entity_layout->addWidget(entity_icon, 0, Qt::AlignVCenter);
    entity_layout->addWidget(entity_text, 1, Qt::AlignVCenter);
    return entity_box;
}

} // namespace

namespace ifcinterface::panels::properties {

PropertiesPanelWidget::PropertiesPanelWidget(QWidget* parent)
    : QWidget(parent)
{
    content_layout_ = new QVBoxLayout(this);
    content_layout_->setContentsMargins(0, 0, 0, 0);
    content_layout_->setSpacing(12);
}

void PropertiesPanelWidget::render(const PropertiesPanelState& state) {
    clearLayout(content_layout_);

    QList<QWidget*> property_set_widgets;
    for (const auto& property_set : state.property_sets) {
        property_set_widgets.append(makePropertySetPanel(property_set, this));
    }

    QList<QWidget*> quantity_set_widgets;
    for (const auto& property_set : state.quantity_sets) {
        quantity_set_widgets.append(makePropertySetPanel(property_set, this));
    }

    auto* entity_section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    entity_section->addBodyWidget(makeEntityBox(state.entity, this));

    auto* attributes_section = new components::Section("Attributes", components::SectionHeaderMode::Visible, this);
    attributes_section->addBodyWidget(makeAttributeList(state.attributes, this));
    attributes_section->setExpanded(attributes_expanded_);

    auto* relationships_section = new components::Section("Relationships", components::SectionHeaderMode::Visible, this);
    relationships_section->addBodyWidget(makeRelationshipList(state.relationships, this));
    relationships_section->setExpanded(relationships_expanded_);

    auto* properties_section = new components::Section("Properties", components::SectionHeaderMode::Visible, this);
    auto* properties_filter_toggle = new QToolButton(properties_section);
    properties_filter_toggle->setObjectName("panelSectionFilterToggle");
    properties_filter_toggle->setCheckable(true);
    properties_filter_toggle->setIcon(components::icons::makeSvgIcon(":/icons/filter.svg"));
    properties_filter_toggle->setAutoRaise(true);
    properties_section->addHeaderWidget(properties_filter_toggle);
    QLineEdit* properties_filter_field = nullptr;
    auto* properties_filter_wrapper = makeFilterWrapper(&properties_filter_field, properties_section);
    properties_filter_field->setPlaceholderText("Filter properties or sets");
    properties_filter_field->setText(properties_filter_text_);
    properties_filter_wrapper->setVisible(properties_filter_visible_);
    properties_filter_field->setVisible(properties_filter_visible_);
    connect(properties_filter_toggle, &QToolButton::toggled, properties_filter_field, [this, properties_filter_field, properties_filter_wrapper](bool visible) {
        properties_filter_visible_ = visible;
        properties_filter_field->setVisible(visible);
        properties_filter_wrapper->setVisible(visible);
        if (visible) properties_filter_field->setFocus();
    });
    connect(properties_filter_field, &QLineEdit::textChanged, this, [this](const QString& text) {
        properties_filter_text_ = text;
    });
    properties_section->addBodyWidget(properties_filter_wrapper);
    for (auto* widget : property_set_widgets) properties_section->addBodyWidget(widget);
    properties_section->setExpanded(properties_expanded_);
    properties_filter_toggle->setChecked(properties_filter_visible_);

    auto* quantities_section = new components::Section("Quantities", components::SectionHeaderMode::Visible, this);
    auto* quantities_filter_toggle = new QToolButton(quantities_section);
    quantities_filter_toggle->setObjectName("panelSectionFilterToggle");
    quantities_filter_toggle->setCheckable(true);
    quantities_filter_toggle->setIcon(components::icons::makeSvgIcon(":/icons/filter.svg"));
    quantities_filter_toggle->setAutoRaise(true);
    quantities_section->addHeaderWidget(quantities_filter_toggle);
    QLineEdit* quantities_filter_field = nullptr;
    auto* quantities_filter_wrapper = makeFilterWrapper(&quantities_filter_field, quantities_section);
    quantities_filter_field->setPlaceholderText("Filter quantities or sets");
    quantities_filter_field->setText(quantities_filter_text_);
    quantities_filter_wrapper->setVisible(quantities_filter_visible_);
    quantities_filter_field->setVisible(quantities_filter_visible_);
    connect(quantities_filter_toggle, &QToolButton::toggled, quantities_filter_field, [this, quantities_filter_field, quantities_filter_wrapper](bool visible) {
        quantities_filter_visible_ = visible;
        quantities_filter_field->setVisible(visible);
        quantities_filter_wrapper->setVisible(visible);
        if (visible) quantities_filter_field->setFocus();
    });
    connect(quantities_filter_field, &QLineEdit::textChanged, this, [this](const QString& text) {
        quantities_filter_text_ = text;
    });
    quantities_section->addBodyWidget(quantities_filter_wrapper);
    for (auto* widget : quantity_set_widgets) quantities_section->addBodyWidget(widget);
    quantities_section->setExpanded(quantities_expanded_);
    quantities_filter_toggle->setChecked(quantities_filter_visible_);

    if (auto* button = attributes_section->findChild<QToolButton*>("panelSectionHeaderButton")) {
        connect(button, &QToolButton::toggled, this, [this](bool expanded) {
            attributes_expanded_ = expanded;
        });
    }
    if (auto* button = relationships_section->findChild<QToolButton*>("panelSectionHeaderButton")) {
        connect(button, &QToolButton::toggled, this, [this](bool expanded) {
            relationships_expanded_ = expanded;
        });
    }
    if (auto* button = properties_section->findChild<QToolButton*>("panelSectionHeaderButton")) {
        connect(button, &QToolButton::toggled, this, [this](bool expanded) {
            properties_expanded_ = expanded;
        });
    }
    if (auto* button = quantities_section->findChild<QToolButton*>("panelSectionHeaderButton")) {
        connect(button, &QToolButton::toggled, this, [this](bool expanded) {
            quantities_expanded_ = expanded;
        });
    }

    content_layout_->addWidget(entity_section);
    content_layout_->addWidget(attributes_section);
    content_layout_->addWidget(relationships_section);
    content_layout_->addWidget(properties_section);
    content_layout_->addWidget(quantities_section);
    content_layout_->addStretch(1);
}

} // namespace ifcinterface::panels::properties
