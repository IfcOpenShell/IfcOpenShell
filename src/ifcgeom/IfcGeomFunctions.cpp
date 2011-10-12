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
 * Implementations of the various conversion functions defined in IfcGeom.h     *
 *                                                                              *
 ********************************************************************************/

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Vec2d.hxx>
#include <gp_Dir2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Mat.hxx>
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

#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>

#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp_Explorer.hxx>

#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepAlgoAPI_Cut.hxx>

#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>

#include <BRepFilletAPI_MakeFillet2d.hxx>

#include <TopLoc_Location.hxx>

#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>

#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::convert_openings(const Ifc2x3::IfcProduct::ptr entity, 
							   const Ifc2x3::IfcRelVoidsElement::list& openings, TopoDS_Shape& result, const gp_Trsf& trsf2) {
	for ( Ifc2x3::IfcRelVoidsElement::it it = openings->begin(); it != openings->end(); ++ it ) {
		Ifc2x3::IfcRelVoidsElement::ptr v = *it;
		Ifc2x3::IfcFeatureElementSubtraction::ptr fes = v->RelatedOpeningElement();
		if ( fes->is(Ifc2x3::Type::IfcOpeningElement) ) {
			gp_Trsf trsf;
			IfcGeom::convert(fes->ObjectPlacement(),trsf);
			trsf.PreMultiply(trsf2.Inverted());
			Ifc2x3::IfcProductRepresentation::ptr prodrep = fes->Representation();
			if ( prodrep->is(Ifc2x3::Type::IfcProductDefinitionShape) ) {
				Ifc2x3::IfcProductDefinitionShape::ptr pds = reinterpret_pointer_cast<Ifc2x3::IfcProductRepresentation,Ifc2x3::IfcProductDefinitionShape>(prodrep);
				Ifc2x3::IfcRepresentation::list reps = pds->Representations();
				for ( Ifc2x3::IfcRepresentation::it it2 = reps->begin(); it2 != reps->end(); ++ it2 ) {
					TopoDS_Shape s;
					IfcGeom::convert_shape(*it2,s);
					s.Move(trsf);
					const float opening_volume = shape_volume(s);
					if ( opening_volume <= ALMOST_ZERO )
						Ifc::LogMessage("warning","Empty solid for:",fes->entity);
					const float original_shape_volume = shape_volume(result);
					result = BRepAlgoAPI_Cut(result,s);
					const float volume_after_subtraction = shape_volume(result);
					if ( ALMOST_THE_SAME(original_shape_volume,volume_after_subtraction) )
						Ifc::LogMessage("warning","Warning subtraction yields unchanged volume:",entity->entity);
				}
			}
		}
	}
	return true;
}
bool IfcGeom::convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face) {
	BRepBuilderAPI_MakeFace mf(wire, false);
	BRepBuilderAPI_FaceError er = mf.Error();
	if ( er == BRepBuilderAPI_NotPlanar ) {
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire, 0.01, TopAbs_WIRE);
		mf.~BRepBuilderAPI_MakeFace();
		new (&mf) BRepBuilderAPI_MakeFace(wire);
		er = mf.Error();
	}
	if ( er != BRepBuilderAPI_FaceDone ) return false;
	face = mf.Face();
	return true;
}
bool IfcGeom::profile_helper(int numVerts, float* verts, int numFillets, int* filletIndices, float* filletRadii, gp_Trsf2d trsf, TopoDS_Face& face) {
	TopoDS_Vertex* vertices = new TopoDS_Vertex[numVerts];
	
	for ( int i = 0; i < numVerts; i ++ ) {
		gp_XY xy (verts[2*i],verts[2*i+1]);
		trsf.Transforms(xy);
		vertices[i] = BRepBuilderAPI_MakeVertex(gp_Pnt(xy.X(),xy.Y(),0.0f));
	}

	BRepBuilderAPI_MakeWire w;
	for ( int i = 0; i < numVerts; i ++ )
		w.Add(BRepBuilderAPI_MakeEdge(vertices[i],vertices[(i+1)%numVerts]));

	IfcGeom::convert_wire_to_face(w.Wire(),face);

	if ( numFillets ) {
		BRepFilletAPI_MakeFillet2d fillet (face);
		for ( int i = 0; i < numFillets; i ++ ) {
			const float radius = filletRadii[i];
			if ( radius < 1e-7 ) continue;
			fillet.AddFillet(vertices[filletIndices[i]],radius);
		}
		fillet.Build();
		face = TopoDS::Face(fillet.Shape());
	}

	delete[] vertices;
	return true;
}
float IfcGeom::shape_volume(const TopoDS_Shape& s) {
	GProp_GProps System;
	BRepGProp::VolumeProperties(s, System);
	return (float) System.Mass();
}