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

#include <string>
#include <fstream>
#include <cstdio>

#include <BRepBuilderAPI_GTransform.hxx>
#include <BRepBuilderAPI_Transform.hxx>

#include "OpenCascadeBasedSerializer.h"

bool OpenCascadeBasedSerializer::ready() {
	std::ofstream test_file(out_filename.c_str(), std::ios_base::binary);
	bool succeeded = test_file.is_open();
	test_file.close();
	remove(out_filename.c_str());
	return succeeded;
}

void OpenCascadeBasedSerializer::writeShapeModel(const IfcGeomObjects::IfcGeomShapeModelObject* o) {		
	for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = o->mesh().begin(); it != o->mesh().end(); ++ it) {
		gp_GTrsf gtrsf = it->Placement();
		
		// TODO:
		gp_GTrsf o_trsf;
		int k = 0;
		for( int i = 1; i < 5; ++ i )
			for ( int j = 1; j < 4; ++ j )
				o_trsf.SetValue(j, i, o->matrix()[k++]);
		
		gtrsf.PreMultiply(o_trsf);
		const TopoDS_Shape& s = it->Shape();			
			
		bool trsf_valid = false;
		gp_Trsf trsf;
		try {
			trsf = gtrsf.Trsf();
			trsf_valid = true;
		} catch (...) {}
			
		const TopoDS_Shape moved_shape = trsf_valid
			? BRepBuilderAPI_Transform(s, trsf, true).Shape()
			: BRepBuilderAPI_GTransform(s, gtrsf, true).Shape();
			
		writeShape(moved_shape);
	}
}
