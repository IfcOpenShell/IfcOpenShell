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

#include "PropertiesPanelWidget.h"

#include "../../components/KeyValueTable.h"
#include "../../components/Section.h"
#include "../../components/SvgIcon.h"

#include <QFrame>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QVBoxLayout>

namespace {

QWidget* makePropertySetPanel(const ifcinterface::panels::properties::PropertySet& property_set, QWidget* parent = nullptr) {
    auto* group = new QGroupBox(property_set.title, parent);
    group->setObjectName("propertySetCard");
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
    while (auto* item = content_layout_->takeAt(0)) {
        if (auto* widget = item->widget()) widget->deleteLater();
        delete item;
    }

    auto* entity_card = new QFrame(this);
    entity_card->setObjectName("entityClassCard");
    auto* entity_layout = new QHBoxLayout(entity_card);
    entity_layout->setContentsMargins(10, 8, 10, 8);
    entity_layout->setSpacing(10);
    auto* entity_icon = new QLabel(entity_card);
    entity_icon->setPixmap(components::icons::makePanelSvgPixmap(":/icons/cube-dots.svg", QSize(28, 28)));
    entity_icon->setAlignment(Qt::AlignCenter);
    auto* entity_text = new QWidget(entity_card);
    auto* entity_text_layout = new QVBoxLayout(entity_text);
    entity_text_layout->setContentsMargins(0, 0, 0, 0);
    entity_text_layout->setSpacing(2);
    auto* entity_class = new QLabel(state.entity.entity_class, entity_text);
    entity_class->setObjectName("entityClassLabel");
    auto* entity_type = new QLabel(state.entity.predefined_type, entity_text);
    entity_type->setProperty("textRole", "secondary");
    entity_text_layout->addWidget(entity_class);
    entity_text_layout->addWidget(entity_type);
    entity_layout->addWidget(entity_icon, 0, Qt::AlignVCenter);
    entity_layout->addWidget(entity_text, 1, Qt::AlignVCenter);

    QList<QWidget*> property_set_widgets;
    for (const auto& property_set : state.property_sets) {
        property_set_widgets.append(makePropertySetPanel(property_set, this));
    }

    QList<QWidget*> quantity_set_widgets;
    for (const auto& property_set : state.quantity_sets) {
        quantity_set_widgets.append(makePropertySetPanel(property_set, this));
    }

    auto* entity_section = new components::Section("", components::SectionHeaderMode::Hidden, "", this);
    entity_section->addBodyWidget(entity_card);
    auto* attributes_section = new components::Section("Attributes", components::SectionHeaderMode::Visible, "", this);
    attributes_section->addBodyWidget(makeAttributeList(state.attributes, this));
    auto* relationships_section = new components::Section("Relationships", components::SectionHeaderMode::Visible, "", this);
    relationships_section->addBodyWidget(makeRelationshipList(state.relationships, this));
    auto* properties_section = new components::Section("Properties", components::SectionHeaderMode::Visible, "Filter properties or sets", this);
    for (auto* widget : property_set_widgets) properties_section->addBodyWidget(widget);
    auto* quantities_section = new components::Section("Quantities", components::SectionHeaderMode::Visible, "Filter quantities or sets", this);
    for (auto* widget : quantity_set_widgets) quantities_section->addBodyWidget(widget);

    content_layout_->addWidget(entity_section);
    content_layout_->addWidget(attributes_section);
    content_layout_->addWidget(relationships_section);
    content_layout_->addWidget(properties_section);
    content_layout_->addWidget(quantities_section);
    content_layout_->addStretch(1);
}

} // namespace ifcinterface::panels::properties
