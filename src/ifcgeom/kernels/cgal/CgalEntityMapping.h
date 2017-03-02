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
 * This file registers function prototypes for all supported IFC geometrical    *
 * entities. For entities of type CLASS an std::map is also created to cache    *
 * the output of the conversion functions                                       *
 *                                                                              *
 ********************************************************************************/

#include "../../../ifcparse/IfcUtil.h"
#include "../../../ifcparse/IfcParse.h"

SHAPES(IfcRepresentation);
// IfcFacetedBrep included
// IfcAdvancedBrep included
// IfcFacetedBrepWithVoids included
// IfcAdvancedBrepWithVoids included
SHAPES(IfcManifoldSolidBrep);

SHAPE(IfcExtrudedAreaSolid);
SHAPE(IfcConnectedFaceSet);
SHAPE(IfcCsgSolid);
SHAPE(IfcBlock);

FACE(IfcFace);
FACE(IfcRectangleProfileDef);

WIRE(IfcPolyLoop);

CLASS(IfcCartesianPoint,cgal_point_t);
CLASS(IfcDirection,cgal_direction_t);
CLASS(IfcAxis2Placement2D,cgal_placement_t);
CLASS(IfcAxis2Placement3D,cgal_placement_t);
CLASS(IfcObjectPlacement,cgal_placement_t);
