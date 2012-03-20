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
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
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

#include <BRepBuilderAPI_GTransform.hxx>

#include <BRepCheck_Analyzer.hxx>

#include <BRepGProp_Face.hxx>

#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& shape) {
	BRepOffsetAPI_Sewing builder;
	builder.SetTolerance(0.01);
	TopExp_Explorer exp(compound,TopAbs_FACE);
	if ( ! exp.More() ) return false;
	for ( ; exp.More(); exp.Next() ) {
		TopoDS_Face face = TopoDS::Face(exp.Current());
		builder.Add(face);
	}
	builder.Perform();
	shape = builder.SewedShape();
	try {
	ShapeFix_Solid sf_solid;
	sf_solid.LimitTolerance(0.01);
	shape = sf_solid.SolidFromShell(TopoDS::Shell(shape));
	} catch(...) {}
	return true;
}

bool IfcGeom::is_compound(const TopoDS_Shape& shape) {
	bool has_solids = TopExp_Explorer(shape,TopAbs_SOLID).More() != 0;
	bool has_shells = TopExp_Explorer(shape,TopAbs_SHELL).More() != 0;
	bool has_compounds = TopExp_Explorer(shape,TopAbs_COMPOUND).More() != 0;
	bool has_faces = TopExp_Explorer(shape,TopAbs_FACE).More() != 0;
	return has_compounds && has_faces && !has_solids && !has_shells;
}

const TopoDS_Shape& IfcGeom::ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid) {
	const bool is_comp = IfcGeom::is_compound(shape);
	if ( ! is_comp ) return shape;
	IfcGeom::create_solid_from_compound(shape,solid);
	return solid;
}

bool IfcGeom::convert_openings(const Ifc2x3::IfcProduct::ptr entity, const Ifc2x3::IfcRelVoidsElement::list& openings, 
							   const ShapeList& entity_shapes, const gp_Trsf& entity_trsf, ShapeList& cut_shapes) {
	// Iterate over IfcOpeningElements
	IfcGeom::ShapeList opening_shapes;
	unsigned int last_size = 0;
	for ( Ifc2x3::IfcRelVoidsElement::it it = openings->begin(); it != openings->end(); ++ it ) {
		Ifc2x3::IfcRelVoidsElement::ptr v = *it;
		Ifc2x3::IfcFeatureElementSubtraction::ptr fes = v->RelatedOpeningElement();
		if ( fes->is(Ifc2x3::Type::IfcOpeningElement) ) {

			// Convert the IfcRepresentation of the IfcOpeningElement
			gp_Trsf opening_trsf;
			IfcGeom::convert(fes->ObjectPlacement(),opening_trsf);

			// Move the opening into the coordinate system of the IfcProduct
			opening_trsf.PreMultiply(entity_trsf.Inverted());

			Ifc2x3::IfcProductRepresentation::ptr prodrep = fes->Representation();
			Ifc2x3::IfcRepresentation::list reps = prodrep->Representations();
						
			for ( Ifc2x3::IfcRepresentation::it it2 = reps->begin(); it2 != reps->end(); ++ it2 ) {
				IfcGeom::convert_shapes(*it2,opening_shapes);
			}

			const unsigned int current_size = (const unsigned int) opening_shapes.size();
			for ( unsigned int i = last_size; i < current_size; ++ i ) {
				opening_shapes[i].first->PreMultiply(opening_trsf);
			}
			last_size = current_size;
		}
	}

	// Iterate over the shapes of the IfcProduct
	for ( IfcGeom::ShapeList::const_iterator it3 = entity_shapes.begin(); it3 != entity_shapes.end(); ++ it3 ) {
		TopoDS_Shape entity_shape_solid;
		const TopoDS_Shape& entity_shape_unlocated = IfcGeom::ensure_fit_for_subtraction(*(it3->second),entity_shape_solid);
		const gp_GTrsf& entity_shape_gtrsf = *(it3->first);
		TopoDS_Shape entity_shape;
		if ( entity_shape_gtrsf.Form() == gp_Other ) {
			Ifc::LogMessage("Warning","Applying non uniform transformation to:",entity->entity);
			entity_shape = BRepBuilderAPI_GTransform(entity_shape_unlocated,entity_shape_gtrsf,true).Shape();
		} else {
			entity_shape = entity_shape_unlocated.Moved(entity_shape_gtrsf.Trsf());
		}

		// Iterate over the shapes of the IfcOpeningElements
		for ( IfcGeom::ShapeList::const_iterator it4 = opening_shapes.begin(); it4 != opening_shapes.end(); ++ it4 ) {
			TopoDS_Shape opening_shape_solid;
			const TopoDS_Shape& opening_shape_unlocated = IfcGeom::ensure_fit_for_subtraction(*(it4->second),opening_shape_solid);
			const gp_GTrsf& opening_shape_gtrsf = *(it4->first);
			if ( opening_shape_gtrsf.Form() == gp_Other ) {
				Ifc::LogMessage("Warning","Applying non uniform transformation to opening of:",entity->entity);
			}
			const TopoDS_Shape& opening_shape = opening_shape_gtrsf.Form() == gp_Other
				? BRepBuilderAPI_GTransform(opening_shape_unlocated,opening_shape_gtrsf,true).Shape()
				: opening_shape_unlocated.Moved(opening_shape_gtrsf.Trsf());
					
			const double opening_volume = shape_volume(opening_shape);
			if ( opening_volume <= ALMOST_ZERO )
				Ifc::LogMessage("Warning","Empty opening for:",entity->entity);

			const double original_shape_volume = shape_volume(entity_shape);

			BRepAlgoAPI_Cut brep_cut(entity_shape,opening_shape);

			if ( brep_cut.IsDone() ) {
				TopoDS_Shape brep_cut_result = brep_cut;
				
				BRepCheck_Analyzer analyser(brep_cut_result);
				bool is_valid = analyser.IsValid() != 0;
				if ( is_valid ) {
					entity_shape = brep_cut;
					const double volume_after_subtraction = shape_volume(entity_shape);
					
					if ( ALMOST_THE_SAME(original_shape_volume,volume_after_subtraction) )
						Ifc::LogMessage("Warning","Subtraction yields unchanged volume:",entity->entity);

				} else {
					Ifc::LogMessage("Error","Invalid result from subtraction:",entity->entity);
				}
			} else {
				Ifc::LogMessage("Error","Failed to process subtraction:",entity->entity);
			}

		}
		cut_shapes.push_back(IfcGeom::LocationShape(new gp_GTrsf(),new TopoDS_Shape(entity_shape)));
	}

	// Delete references to opening transformations, but keep shapes in the cache
	for ( IfcGeom::ShapeList::const_iterator it5 = opening_shapes.begin(); it5 != opening_shapes.end(); ++ it5 ) {
		delete it5->first;
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
bool IfcGeom::profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Face& face) {
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
			const double radius = filletRadii[i];
			if ( radius < 1e-7 ) continue;
			fillet.AddFillet(vertices[filletIndices[i]],radius);
		}
		fillet.Build();
		face = TopoDS::Face(fillet.Shape());
	}

	delete[] vertices;
	return true;
}
double IfcGeom::shape_volume(const TopoDS_Shape& s) {
	GProp_GProps System;
	BRepGProp::VolumeProperties(s, System);
	return (double) System.Mass();
}
bool IfcGeom::is_convex(const TopoDS_Wire& wire) {
	for ( TopExp_Explorer exp1(wire,TopAbs_VERTEX); exp1.More(); exp1.Next() ) {
		TopoDS_Vertex V1 = TopoDS::Vertex(exp1.Current());
		gp_Pnt P1 = BRep_Tool::Pnt(V1);
		// Store the neighboring points
		std::vector<gp_Pnt> neighbors;
		for ( TopExp_Explorer exp3(wire,TopAbs_EDGE); exp3.More(); exp3.Next() ) {
			TopoDS_Edge edge = TopoDS::Edge(exp3.Current());
			std::vector<gp_Pnt> edge_points;
			for ( TopExp_Explorer exp2(edge,TopAbs_VERTEX); exp2.More(); exp2.Next() ) {
				TopoDS_Vertex V2 = TopoDS::Vertex(exp2.Current());
				gp_Pnt P2 = BRep_Tool::Pnt(V2);
				edge_points.push_back(P2);
			}
			if ( edge_points.size() != 2 ) continue;
			if ( edge_points[0].IsEqual(P1,POINT_EQUALITY_TOLERANCE)) neighbors.push_back(edge_points[1]);
			else if ( edge_points[1].IsEqual(P1,POINT_EQUALITY_TOLERANCE)) neighbors.push_back(edge_points[0]);
		}
		// There should be two of these
		if ( neighbors.size() != 2 ) return false;
		// Now find the non neighboring points
		std::vector<gp_Pnt> non_neighbors;
		for ( TopExp_Explorer exp2(wire,TopAbs_VERTEX); exp2.More(); exp2.Next() ) {
			TopoDS_Vertex V2 = TopoDS::Vertex(exp2.Current());
			gp_Pnt P2 = BRep_Tool::Pnt(V2);
			if ( P1.IsEqual(P2,POINT_EQUALITY_TOLERANCE) ) continue;
			bool found = false;
			for( std::vector<gp_Pnt>::const_iterator it = neighbors.begin(); it != neighbors.end(); ++ it ) {
				if ( (*it).IsEqual(P2,POINT_EQUALITY_TOLERANCE) ) { found = true; break; }
			}
			if ( ! found ) non_neighbors.push_back(P2);
		}
		// Calculate the angle between the two edges of the vertex
		gp_Dir dir1(neighbors[0].XYZ() - P1.XYZ());
		gp_Dir dir2(neighbors[1].XYZ() - P1.XYZ());
		const double angle = acos(dir1.Dot(dir2)) + 0.0001;
		// Now for the non-neighbors see whether a greater angle can be found with one of the edges
		for ( std::vector<gp_Pnt>::const_iterator it = non_neighbors.begin(); it != non_neighbors.end(); ++ it ) {
			gp_Dir dir3((*it).XYZ() - P1.XYZ());
			const double angle2 = acos(dir3.Dot(dir1));
			const double angle3 = acos(dir3.Dot(dir2));
			if ( angle2 > angle || angle3 > angle ) return false;
		}
	}
	return true;
}
TopoDS_Shape IfcGeom::halfspace_from_plane(const gp_Pln& pln,const gp_Pnt& cent) {
	TopoDS_Face face = BRepBuilderAPI_MakeFace(pln).Face();
	return BRepPrimAPI_MakeHalfSpace(face,cent).Solid();
}
gp_Pln IfcGeom::plane_from_face(const TopoDS_Face& face) {
	BRepGProp_Face prop(face);
	Standard_Real u1,u2,v1,v2;
	prop.Bounds(u1,u2,v1,v2);
	Standard_Real u = (u1+u2)/2.0;
	Standard_Real v = (v1+v2)/2.0;
	gp_Pnt p;
	gp_Vec n;
	prop.Normal(u,v,p,n);
	return gp_Pln(p,n);
}
gp_Pnt IfcGeom::point_above_plane(const gp_Pln& pln, bool agree) {
	if ( agree ) {
		return pln.Location().Translated(pln.Axis().Direction());
	} else {
		return pln.Location().Translated(-pln.Axis().Direction());
	}
}