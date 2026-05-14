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

#include "Buttons.h"

#include "SvgIcon.h"

#include <QFrame>
#include <QHBoxLayout>
#include <QLabel>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcviewerfull::components::buttons {

QToolButton* makeButton(const QString& text,
                        const QString& icon_path,
                        QWidget* parent) {
    auto* button = new QToolButton(parent);
    button->setObjectName("ribbonButton");
    button->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
    button->setIcon(components::icons::makeAccentSvgIcon(icon_path));
    button->setIconSize(QSize(20, 20));
    button->setText(text);
    button->setMinimumSize(QSize(90, 68));
    button->setAutoRaise(false);
    return button;
}

QWidget* makeButtonGroup(const QString& title,
                         const QList<QToolButton*>& buttons,
                         QWidget* parent,
                         bool trailing_separator,
                         int vertical_spacing) {
    auto* group = new QFrame(parent);
    group->setObjectName("ribbonGroup");
    group->setProperty("separator", trailing_separator);

    auto* group_layout = new QVBoxLayout(group);
    group_layout->setContentsMargins(8, 6, 8, 4);
    group_layout->setSpacing(vertical_spacing);

    auto* button_row = new QHBoxLayout();
    button_row->setContentsMargins(0, 0, 0, 0);
    button_row->setSpacing(4);
    for (auto* button : buttons) {
        button_row->addWidget(button);
    }

    auto* label = new QLabel(title, group);
    label->setObjectName("ribbonGroupLabel");
    label->setProperty("textRole", "secondary");
    label->setAlignment(Qt::AlignCenter);

    group_layout->addLayout(button_row);
    group_layout->addWidget(label);
    return group;
}

} // namespace ifcviewerfull::components::buttons
