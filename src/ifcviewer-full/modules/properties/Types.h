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

#ifndef IFCINTERFACE_PANELS_PROPERTIESPANELTYPES_H
#define IFCINTERFACE_PANELS_PROPERTIESPANELTYPES_H

#include <QList>
#include <QPair>
#include <QString>

namespace ifcviewerfull::modules::properties {

struct KeyValueRow {
    QString key;
    QString value;
};

struct RelationshipRow {
    QString key;
    QString value;
};

struct PropertySet {
    QString title;
    QList<KeyValueRow> rows;
};

struct EntitySummary {
    QString entity_class;
    QString predefined_type;
};

struct PropertiesPanelState {
    EntitySummary entity;
    QList<KeyValueRow> attributes;
    QList<RelationshipRow> relationships;
    QList<PropertySet> property_sets;
    QList<PropertySet> quantity_sets;
};

} // namespace ifcviewerfull::modules::properties

#endif
