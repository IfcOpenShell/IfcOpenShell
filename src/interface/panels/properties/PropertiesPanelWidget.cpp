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

#include <QFile>
#include <QFormLayout>
#include <QFrame>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPainter>
#include <QPixmap>
#include <QRegularExpression>
#include <QScrollArea>
#include <QSvgRenderer>
#include <QToolButton>
#include <QVBoxLayout>

namespace {

QPixmap renderPanelSvgPixmap(const QString& icon_path, const QString& color, const QSize& size) {
    QFile file(icon_path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return QIcon(icon_path).pixmap(size);
    }

    QString svg = QString::fromUtf8(file.readAll());
    svg.replace("currentColor", color, Qt::CaseSensitive);
    svg.replace(QRegularExpression(R"(stroke="[^"]*")"), QString("stroke=\"%1\"").arg(color));
    svg.replace(QRegularExpression(R"(fill="none")"), "fill=\"none\"");

    QSvgRenderer renderer(svg.toUtf8());
    QPixmap pixmap(size);
    pixmap.fill(Qt::transparent);
    QPainter painter(&pixmap);
    renderer.render(&painter);
    return pixmap;
}

QIcon makePanelSvgIcon(const QString& icon_path) {
    QIcon icon;
    icon.addPixmap(renderPanelSvgPixmap(icon_path, "#e7ebf2", QSize(20, 20)), QIcon::Normal, QIcon::Off);
    icon.addPixmap(renderPanelSvgPixmap(icon_path, "#ffffff", QSize(20, 20)), QIcon::Active, QIcon::Off);
    icon.addPixmap(renderPanelSvgPixmap(icon_path, "#ffffff", QSize(20, 20)), QIcon::Selected, QIcon::Off);
    icon.addPixmap(renderPanelSvgPixmap(icon_path, "#6f7988", QSize(20, 20)), QIcon::Disabled, QIcon::Off);
    return icon;
}

QPixmap makePanelSvgPixmap(const QString& icon_path, const QSize& size) {
    return renderPanelSvgPixmap(icon_path, "#e7ebf2", size);
}

QWidget* makeInspectorFilterField(const QString& placeholder, QWidget* parent = nullptr) {
    auto* field = new QLineEdit(parent);
    field->setPlaceholderText(placeholder);
    field->setClearButtonEnabled(true);
    field->addAction(makePanelSvgIcon(":/icons/filter.svg"), QLineEdit::LeadingPosition);
    return field;
}

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

QWidget* makeInspectorSection(const QString& title,
                              const QString& filter_placeholder,
                              const QList<QWidget*>& groups,
                              QWidget* parent = nullptr) {
    auto* section = new QWidget(parent);
    section->setObjectName("inspectorSection");
    auto* layout = new QVBoxLayout(section);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(6);

    auto* header = new QFrame(section);
    header->setObjectName("inspectorSectionHeader");
    auto* header_layout = new QHBoxLayout(header);
    header_layout->setContentsMargins(0, 0, 0, 0);
    header_layout->setSpacing(6);

    auto* toggle = new QToolButton(header);
    toggle->setObjectName("inspectorSectionButton");
    toggle->setText(title);
    toggle->setCheckable(true);
    toggle->setChecked(true);
    toggle->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    toggle->setArrowType(Qt::DownArrow);
    header_layout->addWidget(toggle);
    header_layout->addStretch(1);

    QLineEdit* filter_field = nullptr;
    if (!filter_placeholder.isEmpty()) {
        auto* filter_toggle = new QToolButton(header);
        filter_toggle->setObjectName("inspectorFilterToggle");
        filter_toggle->setCheckable(true);
        filter_toggle->setIcon(makePanelSvgIcon(":/icons/filter.svg"));
        filter_toggle->setAutoRaise(true);
        header_layout->addWidget(filter_toggle);

        filter_field = qobject_cast<QLineEdit*>(makeInspectorFilterField(filter_placeholder, section));
        filter_field->setVisible(false);
        QObject::connect(filter_toggle, &QToolButton::toggled, filter_field, [filter_field](bool visible) {
            filter_field->setVisible(visible);
            if (visible) filter_field->setFocus();
        });
    }

    auto* body = new QWidget(section);
    body->setObjectName("inspectorSectionBody");
    auto* body_layout = new QVBoxLayout(body);
    body_layout->setContentsMargins(10, 6, 10, 0);
    body_layout->setSpacing(6);
    for (auto* group : groups) body_layout->addWidget(group);

    QObject::connect(toggle, &QToolButton::toggled, body, [toggle, body](bool expanded) {
        toggle->setArrowType(expanded ? Qt::DownArrow : Qt::RightArrow);
        body->setVisible(expanded);
    });

    layout->addWidget(header);
    if (filter_field) {
        auto* filter_wrapper = new QWidget(section);
        filter_wrapper->setObjectName("inspectorFilterWrapper");
        auto* filter_wrapper_layout = new QVBoxLayout(filter_wrapper);
        filter_wrapper_layout->setContentsMargins(10, 0, 10, 0);
        filter_wrapper_layout->setSpacing(0);
        filter_wrapper_layout->addWidget(filter_field);
        layout->addWidget(filter_wrapper);
    }
    layout->addWidget(body);
    return section;
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
        icon->setPixmap(makePanelSvgPixmap(":/icons/cursor-pointer.svg", QSize(14, 14)));
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
    entity_icon->setPixmap(makePanelSvgPixmap(":/icons/cube-dots.svg", QSize(28, 28)));
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

    auto* attributes_section = makeInspectorSection(
        "Attributes", "", {makeAttributeList(state.attributes, content)}, content);
    auto* relationships_section = makeInspectorSection(
        "Relationships", "", {makeRelationshipList(state.relationships, content)}, content);
    auto* properties_section = makeInspectorSection(
        "Properties", "Filter properties or sets", property_set_widgets, content);
    auto* quantities_section = makeInspectorSection(
        "Quantities", "Filter quantities or sets", quantity_set_widgets, content);

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
