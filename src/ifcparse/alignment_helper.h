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

/********************************************************************************
 *                                                                              *
 * Implements convenience functions for alignments                              *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCALIGNMENTHELPER_H
#define IFCALIGNMENTHELPER_H

#include "ifc_parse_api.h"
#include "logger.h"

#include "hierarchy_helper.h"
#include "schemas/Ifc4x3_add2.h"

//
// alignment helper methods
//

// creates a horizontal alignment from a list of PI points and curve radii. if include_geometry is true, the geometric representations are created, otherwise only business logic is created
IFC_SCHEMA_API Ifc4x3_add2::IfcAlignment addHorizontalAlignment(hierarchy_helper<Ifc4x3_add2>& model, const std::string& alignment_name, const std::vector<std::pair<double, double>>& points, const std::vector<double>& radii, bool include_geometry = true);

// creates a horizontal and vertical alignment from a list of PI points, curve radii, and VPI points and vertical curve lengths. if include_geometry is true, the geometric representations are created, otherwise only business logic is created
IFC_SCHEMA_API Ifc4x3_add2::IfcAlignment addAlignment(hierarchy_helper<Ifc4x3_add2>& model, const std::string& alignment_name, const std::vector<std::pair<double, double>>& points, const std::vector<double>& radii, const std::vector<std::pair<double, double>>& vertical_points, const std::vector<double>& vertical_curve_lengths, bool include_geometry = true);

// Maps horizontal alignment business logic to geometry.
// Bloss curves have two geometry elements for one horizontal alignment segment. That is the reason for returning a pair.
// Typically the first element of the pair will have the geometry and the second element will be nullptr
IFC_SCHEMA_API std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> mapAlignmentSegment(hierarchy_helper<Ifc4x3_add2>& model, const Ifc4x3_add2::IfcAlignmentSegment& segment, logger& logger = ::logger::root());
IFC_SCHEMA_API std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> mapAlignmentHorizontalSegment(hierarchy_helper<Ifc4x3_add2>& model, const Ifc4x3_add2::IfcAlignmentHorizontalSegment& segment, logger& logger = ::logger::root());
IFC_SCHEMA_API std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> mapAlignmentVerticalSegment(hierarchy_helper<Ifc4x3_add2>& model, const Ifc4x3_add2::IfcAlignmentVerticalSegment& segment, logger& logger = ::logger::root());
IFC_SCHEMA_API std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> mapAlignmentCantSegment(hierarchy_helper<Ifc4x3_add2>& model, const Ifc4x3_add2::IfcAlignmentCantSegment& segment, logger& logger = ::logger::root());


#endif
