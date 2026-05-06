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

} // namespace

namespace ifcinterface::panels::properties {

PropertiesPanelWidget::PropertiesPanelWidget(QWidget* parent)
    : QWidget(parent)
{
    content_layout_ = new QVBoxLayout(this);
    content_layout_->setContentsMargins(0, 0, 0, 0);
    content_layout_->setSpacing(12);

    auto* entity_box = new QFrame(this);
    entity_box->setObjectName("entityClassBox");
    auto* entity_layout = new QHBoxLayout(entity_box);
    entity_layout->setContentsMargins(10, 8, 10, 8);
    entity_layout->setSpacing(10);
    auto* entity_icon = new QLabel(entity_box);
    entity_icon->setPixmap(components::icons::makeSvgPixmap(":/icons/cube-dots.svg", QSize(28, 28)));
    entity_icon->setAlignment(Qt::AlignCenter);
    auto* entity_text = new QWidget(entity_box);
    auto* entity_text_layout = new QVBoxLayout(entity_text);
    entity_text_layout->setContentsMargins(0, 0, 0, 0);
    entity_text_layout->setSpacing(2);
    entity_class_label_ = new QLabel(entity_text);
    entity_class_label_->setObjectName("entityClassLabel");
    entity_type_label_ = new QLabel(entity_text);
    entity_type_label_->setProperty("textRole", "secondary");
    entity_text_layout->addWidget(entity_class_label_);
    entity_text_layout->addWidget(entity_type_label_);
    entity_layout->addWidget(entity_icon, 0, Qt::AlignVCenter);
    entity_layout->addWidget(entity_text, 1, Qt::AlignVCenter);

    entity_section_ = new components::Section("", components::SectionHeaderMode::Hidden, this);
    entity_section_->addBodyWidget(entity_box);
    attributes_section_ = new components::Section("Attributes", components::SectionHeaderMode::Visible, this);
    relationships_section_ = new components::Section("Relationships", components::SectionHeaderMode::Visible, this);
    properties_section_ = new components::Section("Properties", components::SectionHeaderMode::Visible, this);
    quantities_section_ = new components::Section("Quantities", components::SectionHeaderMode::Visible, this);

    properties_filter_toggle_ = new QToolButton(properties_section_);
    properties_filter_toggle_->setObjectName("panelSectionFilterToggle");
    properties_filter_toggle_->setCheckable(true);
    properties_filter_toggle_->setIcon(components::icons::makeSvgIcon(":/icons/filter.svg"));
    properties_filter_toggle_->setAutoRaise(true);
    properties_section_->addHeaderWidget(properties_filter_toggle_);

    quantities_filter_toggle_ = new QToolButton(quantities_section_);
    quantities_filter_toggle_->setObjectName("panelSectionFilterToggle");
    quantities_filter_toggle_->setCheckable(true);
    quantities_filter_toggle_->setIcon(components::icons::makeSvgIcon(":/icons/filter.svg"));
    quantities_filter_toggle_->setAutoRaise(true);
    quantities_section_->addHeaderWidget(quantities_filter_toggle_);

    properties_filter_wrapper_ = makeFilterWrapper(&properties_filter_field_, properties_section_);
    properties_filter_field_->setPlaceholderText("Filter properties or sets");
    quantities_filter_wrapper_ = makeFilterWrapper(&quantities_filter_field_, quantities_section_);
    quantities_filter_field_->setPlaceholderText("Filter quantities or sets");

    connect(properties_filter_toggle_, &QToolButton::toggled, properties_filter_field_, [this](bool visible) {
        properties_filter_field_->setVisible(visible);
        properties_filter_wrapper_->setVisible(visible);
        if (visible) properties_filter_field_->setFocus();
    });
    connect(quantities_filter_toggle_, &QToolButton::toggled, quantities_filter_field_, [this](bool visible) {
        quantities_filter_field_->setVisible(visible);
        quantities_filter_wrapper_->setVisible(visible);
        if (visible) quantities_filter_field_->setFocus();
    });

    properties_filter_wrapper_->setVisible(false);
    quantities_filter_wrapper_->setVisible(false);

    content_layout_->addWidget(entity_section_);
    content_layout_->addWidget(attributes_section_);
    content_layout_->addWidget(relationships_section_);
    content_layout_->addWidget(properties_section_);
    content_layout_->addWidget(quantities_section_);
    content_layout_->addStretch(1);
}

void PropertiesPanelWidget::render(const PropertiesPanelState& state) {
    const bool attributes_expanded = attributes_section_->isExpanded();
    const bool relationships_expanded = relationships_section_->isExpanded();
    const bool properties_expanded = properties_section_->isExpanded();
    const bool quantities_expanded = quantities_section_->isExpanded();
    const bool properties_filter_visible = properties_filter_toggle_->isChecked();
    const bool quantities_filter_visible = quantities_filter_toggle_->isChecked();
    const QString properties_filter_text = properties_filter_field_->text();
    const QString quantities_filter_text = quantities_filter_field_->text();

    entity_class_label_->setText(state.entity.entity_class);
    entity_type_label_->setText(state.entity.predefined_type);

    attributes_section_->clearBody();
    relationships_section_->clearBody();
    properties_section_->clearBody();
    quantities_section_->clearBody();

    QList<QWidget*> property_set_widgets;
    for (const auto& property_set : state.property_sets) {
        property_set_widgets.append(makePropertySetPanel(property_set, this));
    }

    QList<QWidget*> quantity_set_widgets;
    for (const auto& property_set : state.quantity_sets) {
        quantity_set_widgets.append(makePropertySetPanel(property_set, this));
    }

    attributes_section_->addBodyWidget(makeAttributeList(state.attributes, this));
    relationships_section_->addBodyWidget(makeRelationshipList(state.relationships, this));
    properties_section_->addBodyWidget(properties_filter_wrapper_);
    for (auto* widget : property_set_widgets) properties_section_->addBodyWidget(widget);
    quantities_section_->addBodyWidget(quantities_filter_wrapper_);
    for (auto* widget : quantity_set_widgets) quantities_section_->addBodyWidget(widget);

    attributes_section_->setExpanded(attributes_expanded);
    relationships_section_->setExpanded(relationships_expanded);
    properties_section_->setExpanded(properties_expanded);
    quantities_section_->setExpanded(quantities_expanded);
    properties_filter_field_->setText(properties_filter_text);
    quantities_filter_field_->setText(quantities_filter_text);
    properties_filter_toggle_->setChecked(properties_filter_visible);
    quantities_filter_toggle_->setChecked(quantities_filter_visible);
}

} // namespace ifcinterface::panels::properties
