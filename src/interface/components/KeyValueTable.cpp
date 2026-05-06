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

#include "KeyValueTable.h"

#include "SvgIcon.h"

#include <QHBoxLayout>
#include <QLabel>
#include <QVBoxLayout>

namespace ifcinterface::components {

KeyValueTable::KeyValueTable(const QList<KeyValueTableRow>& rows, QWidget* parent)
    : QWidget(parent)
{
    setObjectName("attributeList");

    auto* layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(6);

    for (const auto& row_data : rows) {
        auto* row = new QWidget(this);
        if (!row_data.trailing_icon_path.isEmpty()) {
            row->setObjectName("relationshipRow");
        } else {
            row->setObjectName("keyValueRow");
        }

        auto* row_layout = new QHBoxLayout(row);
        row_layout->setContentsMargins(0, 0, 0, 0);
        row_layout->setSpacing(12);

        auto* key = new QLabel(row_data.key, row);
        key->setObjectName("propertyKeyLabel");
        if (row_data.key_minimum_width > 0) {
            key->setMinimumWidth(row_data.key_minimum_width);
        }

        auto* value = new QLabel(row_data.value, row);
        value->setObjectName(row_data.value_object_name.isEmpty()
                                 ? "propertyValueLabel"
                                 : row_data.value_object_name);
        value->setWordWrap(true);
        value->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);

        row_layout->addWidget(key);
        row_layout->addWidget(value, 1);

        if (!row_data.trailing_icon_path.isEmpty()) {
            auto* icon = new QLabel(row);
            icon->setObjectName(row_data.trailing_icon_object_name.isEmpty()
                                    ? "relationshipIconLabel"
                                    : row_data.trailing_icon_object_name);
            icon->setPixmap(icons::makePanelSvgPixmap(row_data.trailing_icon_path, QSize(14, 14)));
            icon->setAlignment(Qt::AlignRight | Qt::AlignVCenter);
            row_layout->addWidget(icon, 0, Qt::AlignRight | Qt::AlignVCenter);
        }

        layout->addWidget(row);
    }
}

} // namespace ifcinterface::components
