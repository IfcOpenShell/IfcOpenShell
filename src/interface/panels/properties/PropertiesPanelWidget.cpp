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

#include "../../components/CollapsibleSection.h"
#include "../../components/SvgIcon.h"

#include <QFormLayout>
#include <QFrame>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QScrollArea>
#include <QVBoxLayout>

namespace {

QWidget* makePropertySetPanel(const ifcinterface::panels::properties::PropertySet& property_set, QWidget* parent = nullptr) {
    auto* group = new QGroupBox(property_set.title, parent);
    group->setObjectName("propertySetCard");
    auto* form = new QFormLayout(group);
    form->setContentsMargins(10, 10, 10, 10);
    form->setHorizontalSpacing(16);
    form->setVerticalSpacing(6);
    form->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    for (const auto& row : property_set.rows) {
        auto* key = new QLabel(row.key, group);
        key->setObjectName("propertyKeyLabel");
        auto* value = new QLabel(row.value, group);
        value->setObjectName("propertyValueLabel");
        value->setWordWrap(true);
        form->addRow(key, value);
    }

    return group;
}

QWidget* makeAttributeList(const QList<ifcinterface::panels::properties::KeyValueRow>& rows, QWidget* parent = nullptr) {
    auto* panel = new QWidget(parent);
    panel->setObjectName("attributeList");
    auto* form = new QFormLayout(panel);
    form->setContentsMargins(0, 0, 0, 0);
    form->setHorizontalSpacing(16);
    form->setVerticalSpacing(6);
    form->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    for (const auto& row : rows) {
        auto* key = new QLabel(row.key, panel);
        key->setObjectName("propertyKeyLabel");
        auto* value = new QLabel(row.value, panel);
        value->setObjectName("propertyValueLabel");
        value->setWordWrap(true);
        form->addRow(key, value);
    }

    return panel;
}

QWidget* makeRelationshipList(const QList<ifcinterface::panels::properties::RelationshipRow>& rows, QWidget* parent = nullptr) {
    auto* panel = new QWidget(parent);
    panel->setObjectName("attributeList");
    auto* layout = new QVBoxLayout(panel);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(6);

    for (const auto& row_data : rows) {
        auto* row = new QWidget(panel);
        row->setObjectName("relationshipRow");
        auto* row_layout = new QHBoxLayout(row);
        row_layout->setContentsMargins(0, 0, 0, 0);
        row_layout->setSpacing(12);

        auto* key = new QLabel(row_data.key, row);
        key->setObjectName("propertyKeyLabel");
        key->setMinimumWidth(72);

        auto* target = new QLabel(row_data.value, row);
        target->setObjectName("relationshipValueLabel");
        target->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);

        auto* icon = new QLabel(row);
        icon->setObjectName("relationshipIconLabel");
        icon->setPixmap(ifcinterface::components::icons::makePanelSvgPixmap(":/icons/cursor-pointer.svg", QSize(14, 14)));
        icon->setAlignment(Qt::AlignRight | Qt::AlignVCenter);

        row_layout->addWidget(key);
        row_layout->addWidget(target, 1);
        row_layout->addWidget(icon, 0, Qt::AlignRight | Qt::AlignVCenter);
        layout->addWidget(row);
    }

    return panel;
}

} // namespace

namespace ifcinterface::panels::properties {

PropertiesPanelWidget::PropertiesPanelWidget(QWidget* parent)
    : QWidget(parent)
{
    auto* root = new QVBoxLayout(this);
    root->setContentsMargins(0, 0, 0, 0);
    root->setSpacing(0);
}

void PropertiesPanelWidget::setState(const PropertiesPanelState& state) {
    auto* root = qobject_cast<QVBoxLayout*>(layout());
    while (auto* item = root->takeAt(0)) {
        if (auto* widget = item->widget()) widget->deleteLater();
        delete item;
    }

    auto* content = new QWidget(this);
    content->setObjectName("inspectorPanel");
    auto* content_layout = new QVBoxLayout(content);
    content_layout->setContentsMargins(0, 0, 0, 0);
    content_layout->setSpacing(12);

    auto* entity_card = new QFrame(content);
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
    entity_type->setObjectName("entityTypeLabel");
    entity_text_layout->addWidget(entity_class);
    entity_text_layout->addWidget(entity_type);
    entity_layout->addWidget(entity_icon, 0, Qt::AlignVCenter);
    entity_layout->addWidget(entity_text, 1, Qt::AlignVCenter);

    auto* entity_wrapper = new QWidget(content);
    entity_wrapper->setObjectName("inspectorSectionBody");
    auto* entity_wrapper_layout = new QVBoxLayout(entity_wrapper);
    entity_wrapper_layout->setContentsMargins(10, 0, 10, 0);
    entity_wrapper_layout->setSpacing(0);
    entity_wrapper_layout->addWidget(entity_card);

    QList<QWidget*> property_set_widgets;
    for (const auto& property_set : state.property_sets) {
        property_set_widgets.append(makePropertySetPanel(property_set, content));
    }

    QList<QWidget*> quantity_set_widgets;
    for (const auto& property_set : state.quantity_sets) {
        quantity_set_widgets.append(makePropertySetPanel(property_set, content));
    }

    auto* attributes_section = new components::inspector::CollapsibleSection("Attributes", "", content);
    attributes_section->addBodyWidget(makeAttributeList(state.attributes, content));
    auto* relationships_section = new components::inspector::CollapsibleSection("Relationships", "", content);
    relationships_section->addBodyWidget(makeRelationshipList(state.relationships, content));
    auto* properties_section = new components::inspector::CollapsibleSection("Properties", "Filter properties or sets", content);
    for (auto* widget : property_set_widgets) properties_section->addBodyWidget(widget);
    auto* quantities_section = new components::inspector::CollapsibleSection("Quantities", "Filter quantities or sets", content);
    for (auto* widget : quantity_set_widgets) quantities_section->addBodyWidget(widget);

    content_layout->addWidget(entity_wrapper);
    content_layout->addWidget(attributes_section);
    content_layout->addWidget(relationships_section);
    content_layout->addWidget(properties_section);
    content_layout->addWidget(quantities_section);
    content_layout->addStretch(1);

    auto* scroll = new QScrollArea(this);
    scroll->setWidgetResizable(true);
    scroll->setFrameShape(QFrame::NoFrame);
    scroll->setWidget(content);
    root->addWidget(scroll);
}

} // namespace ifcinterface::panels::properties
