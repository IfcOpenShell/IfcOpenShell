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

#include "Panel.h"

#include "../../components/Section.h"

#include <QLabel>
#include <QVBoxLayout>

namespace bonsaiviewer::modules::todo {

TodoPanel::TodoPanel(const QString& title, QWidget* parent)
    : QWidget(parent)
{
    auto* layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(0);

    auto* section = new components::Section("", components::SectionHeaderMode::Hidden, this);

    auto* body = new QWidget(section);
    auto* body_layout = new QVBoxLayout(body);
    body_layout->setContentsMargins(0, 12, 0, 12);
    body_layout->setSpacing(12);

    auto* heading = new QLabel(title, body);

    auto* content = new QLabel("Coming soon", body);
    content->setProperty("textRole", "disabled");
    content->setAlignment(Qt::AlignCenter);

    body_layout->addWidget(heading);
    body_layout->addStretch(1);
    body_layout->addWidget(content);
    body_layout->addStretch(1);

    section->addBodyWidget(body);
    layout->addWidget(section);
}

} // namespace bonsaiviewer::modules::todo
