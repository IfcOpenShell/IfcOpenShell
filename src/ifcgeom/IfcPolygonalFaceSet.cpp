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
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom_schema_agnostic/wire_utils.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

#ifdef SCHEMA_HAS_IfcPolygonalFaceSet

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPolygonalFaceSet* pfs, TopoDS_Shape& shape) {
	IfcSchema::IfcCartesianPointList3D* point_list = pfs->Coordinates();
	auto coord_list = point_list->CoordList();
	auto polygonal_faces = pfs->Faces();

	std::vector<std::vector<int>> indices;
	indices.reserve(polygonal_faces->size() * 2);

	std::vector<std::vector<int>> loop_grouping;
	loop_grouping.reserve(polygonal_faces->size());
	
	for (auto& f : *polygonal_faces) {
		loop_grouping.emplace_back();
		loop_grouping.back().push_back(indices.size());
		indices.push_back(f->CoordIndex());
		if (f->as<IfcSchema::IfcIndexedPolygonalFaceWithVoids>()) {
			auto inner_coordinates = f->as<IfcSchema::IfcIndexedPolygonalFaceWithVoids>()->InnerCoordIndices();
			for (auto& x : inner_coordinates) {
				loop_grouping.back().push_back(indices.size());
				indices.push_back(x);
			}
		}
	}

	faceset_helper<
		std::vector<double>,
		std::vector<int>
	> helper(this, coord_list, indices, pfs->Closed().get_value_or(false));

	TopTools_ListOfShape faces;

	for (auto& f : loop_grouping) {
		bool not_planar = false;
		
		TopoDS_Wire w;
		if (!helper.wire(indices[f[0]], w)) {
			continue;
		}

		TopoDS_Face face;
		std::vector<TopoDS_Wire> ws = { w };

		// @todo triangulate
		BRepBuilderAPI_MakeFace mf(w);
		if (mf.Error() == BRepBuilderAPI_NotPlanar) {
			not_planar = true;
		} else if (mf.IsDone()) {
			face = mf.Face();
		} else {
			// todo log
			continue;
		}

		if (f.size() > 1) {

			if (not_planar) {
				for (auto it = f.begin() + 1; it != f.end(); ++it) {
					TopoDS_Wire w2;
					if (helper.wire(indices[*it], w2)) {
						ws.push_back(w2);
					}
				}
			} else {
				BRepBuilderAPI_MakeFace mf2(face);
				for (auto it = f.begin() + 1; it != f.end(); ++it) {
					TopoDS_Wire w2;
					if (helper.wire(indices[*it], w2)) {
						mf2.Add(w2);
						ws.push_back(w2);
					}

				}
				
				if (mf2.Error() == BRepBuilderAPI_NotPlanar) {
					not_planar = true;
				} else if (mf2.IsDone()) {
					face = mf2.Face();
				}
			}	
			
		}

		if (not_planar) {
			TopTools_ListOfShape fs;
			if (util::triangulate_wire(ws, fs)) {
				Logger::Warning("Triangulated face boundary:", pfs);
				TopTools_ListIteratorOfListOfShape it(fs);
				for (; it.More(); it.Next()) {
					const TopoDS_Face& tri = TopoDS::Face(it.Value());
					if (face_area(tri) > getValue(GV_MINIMAL_FACE_AREA)) {
						faces.Append(tri);
					}
				}
			}
		} else {
			faces.Append(face);
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
