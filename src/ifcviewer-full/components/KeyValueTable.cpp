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

#include <QGridLayout>
#include <QLabel>

namespace ifcviewerfull::components {

KeyValueTable::KeyValueTable(const QList<KeyValueTableRow>& rows, QWidget* parent)
    : QWidget(parent)
{
    setObjectName("keyValueTable");

    auto* layout = new QGridLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setHorizontalSpacing(12);
    layout->setVerticalSpacing(6);
    layout->setColumnStretch(1, 1);

    int row_index = 0;
    for (const auto& row_data : rows) {
        auto* key = new QLabel(row_data.key, this);
        key->setProperty("textRole", "secondary");
        if (row_data.key_minimum_width > 0) {
            key->setMinimumWidth(row_data.key_minimum_width);
        }

        auto* value = new QLabel(row_data.value, this);
        value->setObjectName(row_data.value_object_name.isEmpty()
                                 ? "keyValueValueLabel"
                                 : row_data.value_object_name);
        value->setWordWrap(true);
        value->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);

        layout->addWidget(key, row_index, 0, Qt::AlignLeft | Qt::AlignTop);
        layout->addWidget(value, row_index, 1);

        if (!row_data.trailing_icon_path.isEmpty()) {
            auto* icon = new QLabel(this);
            icon->setObjectName(row_data.trailing_icon_object_name.isEmpty()
                                    ? "keyValueTrailingIconLabel"
                                    : row_data.trailing_icon_object_name);
            icon->setPixmap(icons::makeSvgPixmap(row_data.trailing_icon_path, QSize(14, 14)));
            icon->setAlignment(Qt::AlignRight | Qt::AlignVCenter);
            layout->addWidget(icon, row_index, 2, Qt::AlignRight | Qt::AlignTop);
        }
        ++row_index;
    }
}

} // namespace ifcviewerfull::components
