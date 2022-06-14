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

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Vec2d.hxx>
#include <gp_Dir2d.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Ax1.hxx>
#include <gp_Ax3.hxx>
#include <gp_Ax2d.hxx>
#include <gp_Pln.hxx>
#include <gp_Circ.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <Geom_TrimmedCurve.hxx>
#include <Geom_CylindricalSurface.hxx>
#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepOffsetAPI_MakePipe.hxx>
#include <BRepOffsetAPI_MakePipeShell.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_CompSolid.hxx>
#include <TopExp.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepPrimAPI_MakeRevol.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCone.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRepPrimAPI_MakeSphere.hxx>
#include <BRepPrimAPI_MakeWedge.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepAlgoAPI_Fuse.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <ShapeFix_Edge.hxx>
#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>
#include <TopLoc_Location.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepClass3d_SolidClassifier.hxx>
#include <Standard_Version.hxx>
#include <TopTools_ListIteratorOfListOfShape.hxx>
#include <ShapeAnalysis_Surface.hxx>
#include "../ifcgeom/IfcGeom.h"
#include <memory>
#include <Geom_ToroidalSurface.hxx>

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
			if (triangulate_wire(ws, fs)) {
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
