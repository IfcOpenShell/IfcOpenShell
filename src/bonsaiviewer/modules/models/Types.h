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

#ifndef IFCINTERFACE_PANELS_MODELSPANELTYPES_H
#define IFCINTERFACE_PANELS_MODELSPANELTYPES_H

#include <QList>
#include <QString>

namespace bonsaiviewer::modules::models {

enum class ItemKind {
    Group,
    Model,
};

struct TreeNode {
    QString id;
    QString name;
    ItemKind kind = ItemKind::Group;
    bool visible = true;
    QList<TreeNode> children;
};

// One entry in a "move to..." menu. Computed by the View from federation state
// and passed into the Panel so menu construction has no domain knowledge.
struct GroupOption {
    QString id;
    QString display_name;
};

struct SelectedModelGeorefState {
    QString georef_present;
    QString coordinate_operation_type;
    QString project_unit;
    QString map_unit;
    QString easting;
    QString northing;
    QString height;
    QString x_axis_abscissa;
    QString x_axis_ordinate;
    QString rotation_dd;
    QString rotation_dms;
    QString scale;
    QString factor_x;
    QString factor_y;
    QString factor_z;
};

} // namespace bonsaiviewer::modules::models

#endif
