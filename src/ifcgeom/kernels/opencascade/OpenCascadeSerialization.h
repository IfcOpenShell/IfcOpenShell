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

#ifndef OPENCASCADESERIALIZATION_H
#define OPENCASCADESERIALIZATION_H

#include "../../../ifcparse/IfcParse.h"

#include <TopoDS_Shape.hxx>

namespace IfcGeom {

	IfcSchema::IfcProductDefinitionShape* tesselate(const TopoDS_Shape& shape, double deflection);
	IfcSchema::IfcProductDefinitionShape* serialise(const TopoDS_Shape& shape, bool advanced);

}

#endif