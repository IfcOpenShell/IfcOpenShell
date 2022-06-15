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

#include <BRepBuilderAPI_MakeFace.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

#ifdef SCHEMA_HAS_IfcTriangulatedFaceSet

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTriangulatedFaceSet* l, TopoDS_Shape& shape) {
	IfcSchema::IfcCartesianPointList3D* point_list = l->Coordinates();
	auto coord_list = point_list->CoordList();
	std::vector<std::vector<int>> indices = l->CoordIndex();

	faceset_helper<
		std::vector<double>,
		std::vector<int>
	> helper(this, coord_list, indices, l->Closed().get_value_or(false));

	TopTools_ListOfShape faces;

	for (auto it = indices.begin(); it != indices.end(); ++it) {
		TopoDS_Wire w;
		if (helper.wire(*it, w)) {
			BRepBuilderAPI_MakeFace mf(w);
			if (mf.IsDone()) {
				faces.Append(mf.Face());
			}
		}
	}
	
	if (faces.Extent() > getValue(GV_MAX_FACES_TO_ORIENT) || !create_solid_from_faces(faces, shape)) {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);

		TopTools_ListIteratorOfListOfShape face_iterator;
		for (face_iterator.Initialize(faces); face_iterator.More(); face_iterator.Next()) {
			builder.Add(compound, face_iterator.Value());
		}
		shape = compound;
	}
	
	return true;
}

#endif