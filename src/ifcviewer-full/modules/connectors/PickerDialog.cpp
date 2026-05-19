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

#include "PickerDialog.h"

#include "../../components/Buttons.h"
#include "../../components/Section.h"
#include "../../components/Style.h"

#include <QHBoxLayout>
#include <QLabel>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcviewerfull::modules::connectors {

ConnectorPickerDialog::ConnectorPickerDialog(const std::vector<ConnectorManifest>& manifests,
                                             const QString& title,
                                             const QString& description,
                                             QWidget* parent)
    : components::Dialog(parent)
{
    setObjectName("appDialog");
    setWindowTitle(title);
    setModal(true);

    if (auto* root = qobject_cast<QVBoxLayout*>(layout())) {
        root->setSizeConstraint(QLayout::SetFixedSize);
    }

    auto* description_section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    auto* description_label = new QLabel(description, description_section);
    description_label->setProperty("textRole", "secondary");
    description_label->setWordWrap(true);
    description_label->setAlignment(Qt::AlignCenter);
    description_label->setMinimumWidth((90 * 3) + (components::style::metrics::padding * 2));
    description_section->addBodyWidget(description_label);

    auto* choices_section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    auto* choices = new QWidget(choices_section);
    auto* row = new QHBoxLayout(choices);
    row->setContentsMargins(0, 0, 0, 0);
    row->setSpacing(components::style::metrics::padding);

    QList<QToolButton*> buttons;
    for (const auto& m : manifests) {
        auto* button = components::buttons::makeButton(m.name, ":/icons/cloud-square.svg", choices);
        const QString id = m.id;
        connect(button, &QToolButton::clicked, this, [this, id]() {
            selected_id_ = id;
            accept();
        });
        buttons.push_back(button);
    }
    row->addWidget(components::buttons::makeButtonGroup("CONNECTORS", buttons, choices, true, 8));
    choices_section->addBodyWidget(choices);

    addBodyWidget(description_section);
    addBodyWidget(choices_section);
}

} // namespace ifcviewerfull::modules::connectors
