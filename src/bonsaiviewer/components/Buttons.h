// This file was generated with the assistance of an AI coding tool.
/********************************************************************************
 *                                                                              *
 * This file is part of Bonsai.                                                 *
 *                                                                              *
 * Bonsai is free software: you can redistribute it and/or modify               *
 * it under the terms of the GNU General Public License as published by         *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * Bonsai is distributed in the hope that it will be useful,                    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * GNU General Public License for more details.                                 *
 *                                                                              *
 * You should have received a copy of the GNU General Public License            *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCINTERFACE_COMPONENTS_BUTTONS_H
#define IFCINTERFACE_COMPONENTS_BUTTONS_H

#include <QList>

class QBoxLayout;
class QToolButton;
class QWidget;

namespace bonsaiviewer::components::buttons {

QToolButton* makeButton(const QString& text,
                        const QString& icon_path,
                        QWidget* parent);

QWidget* makeButtonGroup(const QString& title,
                         const QList<QToolButton*>& buttons,
                         QWidget* parent,
                         int vertical_spacing = 4);

// Adds button groups to a ribbon row, drawing a vertical divider between
// adjacent groups but never after the last one. Centralising the decision
// here means a row can't end up with a dangling trailing separator.
void addButtonGroups(QBoxLayout* row, const QList<QWidget*>& groups);

} // namespace bonsaiviewer::components::buttons

#endif
