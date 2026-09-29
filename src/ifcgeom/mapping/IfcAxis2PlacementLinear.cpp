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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#if defined SCHEMA_HAS_IfcAxis2PlacementLinear

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcAxis2PlacementLinear* inst) {

    if (!inst->Location()->as<IfcSchema::IfcPointByDistanceExpression>()) {
        logger_.Error("GEO", 236, std::runtime_error("Location must be IfcPointByDistanceExpression for IfcAxis2PlacementLinear"));
    }

    taxonomy::matrix4::ptr m = taxonomy::cast<taxonomy::matrix4>(map(inst->Location()));
    Eigen::Vector3d o = m->components().col(3).head<3>();

    // From 8.9.3.4 IfcAxis2PlacementLinear there are 4 cases that need to be considered
    // 1) Axis is given but not RefDirection
    // 2) RefDirection is given but not Axis
    // 3) Neither Axis or RefDirection are provided
    // 4) Both Axis and RefDirection are provided

    Eigen::Vector3d z = inst->Axis() ? *taxonomy::cast<taxonomy::direction3>(map(inst->Axis()))->components_ : Eigen::Vector3d(0,0,1); // Axis is (0,0,1) when omitted
    Eigen::Vector3d rd = inst->RefDirection() ? *taxonomy::cast<taxonomy::direction3>(map(inst->RefDirection()))->components_ : m->components().col(0).head<3>(); // RefDirection is the curve tangent when omitted
    Eigen::Vector3d y = z.cross(rd);
    Eigen::Vector3d x = y.cross(z);

    return taxonomy::make<taxonomy::matrix4>(o, z, x);
}

#endif
