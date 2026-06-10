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
        Logger::Error(std::runtime_error("Location must be IfcPointByDistanceExpression for IfcAxis2PlacementLinear"));
    }

    taxonomy::matrix4::ptr m = taxonomy::cast<taxonomy::matrix4>(map(inst->Location()));
    Eigen::Vector3d o = m->components().col(3).head<3>();

    // From 8.9.3.4 IfcAxis2PlacementLinear there are 4 cases that need to be considered
    // 1) Axis is given but not RefDirection
    // 2) RefDirection is given but not Axis
    // 3) Neither Axis or RefDirection are provided
    // 4) Both Axis and RefDirection are provided
    // When Axis or RefDirection are not provided explicitly in the IfcAxis2PlacementLinear,
    // they are taken from the context of curve by evaluating the Location, which is an IfcPointByDistanceExpression on a curve.
    // The curve tangent is used as RefDirection and the curve normal is used as Axis.

    const bool hasAxis = inst->Axis() != nullptr;
    const bool hasRef = inst->RefDirection() != nullptr;

    Eigen::Vector3d axis, refDirection;
    if (hasAxis && !hasRef) {
        taxonomy::direction3::ptr a = taxonomy::cast<taxonomy::direction3>(map(inst->Axis()));
        axis = *a->components_;
        refDirection = m->components().col(0).head<3>(); // RefDirection is the curve tangent when omitted
    } else if (!hasAxis && hasRef) {
        taxonomy::direction3::ptr r = taxonomy::cast<taxonomy::direction3>(map(inst->RefDirection()));
        refDirection = *r->components_;
        axis = m->components().col(2).head<3>(); // Axis is the curve normal when omitted
    } else if (!hasAxis && !hasRef) {
        refDirection = m->components().col(0).head<3>(); // RefDirection is the curve tangent when omitted
        axis = m->components().col(2).head<3>(); // Axis is the curve normal when omitted
    } else {
        taxonomy::direction3::ptr a = taxonomy::cast<taxonomy::direction3>(map(inst->Axis()));
        axis = *a->components_;
        taxonomy::direction3::ptr r = taxonomy::cast<taxonomy::direction3>(map(inst->RefDirection()));
        refDirection = *r->components_;
    }

    return taxonomy::make<taxonomy::matrix4>(o, axis, refDirection);
}

#endif
