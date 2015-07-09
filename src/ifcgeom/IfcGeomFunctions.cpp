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

#include <set>
#include <cassert>
#include <algorithm>

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
#include <BRepAlgoAPI_Fuse.hxx>

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

#include <BRepMesh_IncrementalMesh.hxx>
#include <BRepTools.hxx>

#include <Poly_Triangulation.hxx>
#include <Poly_Array1OfTriangle.hxx>

#include <TopExp.hxx>
#include <TopTools_IndexedMapOfShape.hxx>
#include <TopTools_IndexedDataMapOfShapeListOfShape.hxx>
#include <TopTools_ListIteratorOfListOfShape.hxx>

#include "../ifcparse/IfcSIPrefix.h"
#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::Kernel::create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& shape) {
	BRepOffsetAPI_Sewing builder;
	builder.SetTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
	builder.SetMaxTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
	builder.SetMinTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
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
	sf_solid.LimitTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
	shape = sf_solid.SolidFromShell(TopoDS::Shell(shape));
	} catch(...) {}
	return true;
}

bool IfcGeom::Kernel::is_compound(const TopoDS_Shape& shape) {
	bool has_solids = TopExp_Explorer(shape,TopAbs_SOLID).More() != 0;
	bool has_shells = TopExp_Explorer(shape,TopAbs_SHELL).More() != 0;
	bool has_compounds = TopExp_Explorer(shape,TopAbs_COMPOUND).More() != 0;
	bool has_faces = TopExp_Explorer(shape,TopAbs_FACE).More() != 0;
	return has_compounds && has_faces && !has_solids && !has_shells;
}

const TopoDS_Shape& IfcGeom::Kernel::ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid) {
	const bool is_comp = is_compound(shape);
	if (!is_comp) {
		return solid = shape;
	}
	create_solid_from_compound(shape, solid);
	
	// If the SEW_SHELLS option had been set this precision had been applied
	// at the end of the generic convert_shape() call.
	const double precision = getValue(GV_PRECISION);
	apply_tolerance(solid, precision);
	
	return solid;
}

bool IfcGeom::Kernel::convert_openings(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, 
							   const IfcGeom::IfcRepresentationShapeItems& entity_shapes, const gp_Trsf& entity_trsf, IfcGeom::IfcRepresentationShapeItems& cut_shapes) {

	// TODO: Refactor convert_openings() convert_openings_fast() and convert(IfcBooleanResult) to use
	// the same code base and conform to the same checks and logging messages.

	// Iterate over IfcOpeningElements
	IfcGeom::IfcRepresentationShapeItems opening_shapes;
	unsigned int last_size = 0;
	for ( IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++ it ) {
		IfcSchema::IfcRelVoidsElement* v = *it;
		IfcSchema::IfcFeatureElementSubtraction* fes = v->RelatedOpeningElement();
		if ( fes->is(IfcSchema::Type::IfcOpeningElement) ) {

			// Convert the IfcRepresentation of the IfcOpeningElement
			gp_Trsf opening_trsf;
			IfcGeom::Kernel::convert(fes->ObjectPlacement(),opening_trsf);

			// Move the opening into the coordinate system of the IfcProduct
			opening_trsf.PreMultiply(entity_trsf.Inverted());

			IfcSchema::IfcProductRepresentation* prodrep = fes->Representation();
			IfcSchema::IfcRepresentation::list::ptr reps = prodrep->Representations();
						
			for ( IfcSchema::IfcRepresentation::list::it it2 = reps->begin(); it2 != reps->end(); ++ it2 ) {
				convert_shapes(*it2,opening_shapes);
			}

			const unsigned int current_size = (const unsigned int) opening_shapes.size();
			for ( unsigned int i = last_size; i < current_size; ++ i ) {
				opening_shapes[i].prepend(opening_trsf);
			}
			last_size = current_size;
		}
	}

	// Iterate over the shapes of the IfcProduct
	for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it3 = entity_shapes.begin(); it3 != entity_shapes.end(); ++ it3 ) {
		TopoDS_Shape entity_shape_solid;
		const TopoDS_Shape& entity_shape_unlocated = ensure_fit_for_subtraction(it3->Shape(),entity_shape_solid);
		const gp_GTrsf& entity_shape_gtrsf = it3->Placement();
		TopoDS_Shape entity_shape;
		if ( entity_shape_gtrsf.Form() == gp_Other ) {
			Logger::Message(Logger::LOG_WARNING,"Applying non uniform transformation to:",entity->entity);
			entity_shape = BRepBuilderAPI_GTransform(entity_shape_unlocated,entity_shape_gtrsf,true).Shape();
		} else {
			entity_shape = entity_shape_unlocated.Moved(entity_shape_gtrsf.Trsf());
		}

		// Iterate over the shapes of the IfcOpeningElements
		for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it4 = opening_shapes.begin(); it4 != opening_shapes.end(); ++ it4 ) {
			TopoDS_Shape opening_shape_solid;
			const TopoDS_Shape& opening_shape_unlocated = ensure_fit_for_subtraction(it4->Shape(),opening_shape_solid);
			const gp_GTrsf& opening_shape_gtrsf = it4->Placement();
			if ( opening_shape_gtrsf.Form() == gp_Other ) {
				Logger::Message(Logger::LOG_WARNING,"Applying non uniform transformation to opening of:",entity->entity);
			}
			const TopoDS_Shape& opening_shape = opening_shape_gtrsf.Form() == gp_Other
				? BRepBuilderAPI_GTransform(opening_shape_unlocated,opening_shape_gtrsf,true).Shape()
				: opening_shape_unlocated.Moved(opening_shape_gtrsf.Trsf());
					
			double opening_volume, original_shape_volume;
			if ( Logger::Verbosity() >= Logger::LOG_WARNING ) {
				opening_volume = shape_volume(opening_shape);
				if ( opening_volume <= ALMOST_ZERO )
					Logger::Message(Logger::LOG_WARNING,"Empty opening for:",entity->entity);
				original_shape_volume = shape_volume(entity_shape);
			}

			if (entity_shape.ShapeType() == TopAbs_COMPSOLID) {

				// For compound solids process the subtraction for the constituent
				// solids individually and write the result back as a compound solid.

				TopoDS_CompSolid compound;
				BRep_Builder builder;
				builder.MakeCompSolid(compound);

				TopExp_Explorer exp(entity_shape, TopAbs_SOLID);

				for (; exp.More(); exp.Next()) {
					BRepAlgoAPI_Cut brep_cut(exp.Current(), opening_shape);
					bool added = false;
					if ( brep_cut.IsDone() ) {
						TopoDS_Shape brep_cut_result = brep_cut;
						BRepCheck_Analyzer analyser(brep_cut_result);
						bool is_valid = analyser.IsValid() != 0;
						if (is_valid) {
							TopExp_Explorer exp(brep_cut_result, TopAbs_SOLID);
							for (; exp.More(); exp.Next()) {
								builder.Add(compound, exp.Current());
								added = true;
							}
						}
					}
					if (!added) {
						// Add the original in case subtraction fails
						builder.Add(compound, exp.Current());
					} else {
						Logger::Message(Logger::LOG_ERROR,"Failed to process subtraction:",entity->entity);
					}
				}

				entity_shape = compound;

			} else {
				BRepAlgoAPI_Cut brep_cut(entity_shape,opening_shape);

				if ( brep_cut.IsDone() ) {
					TopoDS_Shape brep_cut_result = brep_cut;

					ShapeFix_Shape fix(brep_cut_result);
					try {
						fix.Perform();
						brep_cut_result = fix.Shape();
					} catch (...) {
						Logger::Message(Logger::LOG_WARNING, "Shape healing failed on opening subtraction result", entity->entity);
					}
					
					BRepCheck_Analyzer analyser(brep_cut_result);
					bool is_valid = analyser.IsValid() != 0;
					if ( is_valid ) {
						entity_shape = brep_cut_result;
						if ( Logger::Verbosity() >= Logger::LOG_WARNING ) {
							const double volume_after_subtraction = shape_volume(entity_shape);
					
							if ( ALMOST_THE_SAME(original_shape_volume,volume_after_subtraction) )
								Logger::Message(Logger::LOG_WARNING,"Subtraction yields unchanged volume:",entity->entity);
						}
					} else {
						Logger::Message(Logger::LOG_ERROR,"Invalid result from subtraction:",entity->entity);
					}
				} else {
					Logger::Message(Logger::LOG_ERROR,"Failed to process subtraction:",entity->entity);
				}
			}

		}
		cut_shapes.push_back(IfcGeom::IfcRepresentationShapeItem(entity_shape, &it3->Style()));
	}

	return true;
}

bool IfcGeom::Kernel::convert_openings_fast(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, 
							   const IfcGeom::IfcRepresentationShapeItems& entity_shapes, const gp_Trsf& entity_trsf, IfcGeom::IfcRepresentationShapeItems& cut_shapes) {
	
	// Create a compound of all opening shapes in order to speed up the boolean operations
	TopoDS_Compound opening_compound;
	BRep_Builder builder;
	builder.MakeCompound(opening_compound);

	for ( IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++ it ) {
		IfcSchema::IfcRelVoidsElement* v = *it;
		IfcSchema::IfcFeatureElementSubtraction* fes = v->RelatedOpeningElement();
		if ( fes->is(IfcSchema::Type::IfcOpeningElement) ) {

			// Convert the IfcRepresentation of the IfcOpeningElement
			gp_Trsf opening_trsf;
			IfcGeom::Kernel::convert(fes->ObjectPlacement(),opening_trsf);

			// Move the opening into the coordinate system of the IfcProduct
			opening_trsf.PreMultiply(entity_trsf.Inverted());

			IfcSchema::IfcProductRepresentation* prodrep = fes->Representation();
			IfcSchema::IfcRepresentation::list::ptr reps = prodrep->Representations();

			IfcGeom::IfcRepresentationShapeItems opening_shapes;
						
			for ( IfcSchema::IfcRepresentation::list::it it2 = reps->begin(); it2 != reps->end(); ++ it2 ) {
				convert_shapes(*it2,opening_shapes);
			}

			for ( unsigned int i = 0; i < opening_shapes.size(); ++ i ) {
				gp_GTrsf gtrsf = opening_shapes[i].Placement();
				gtrsf.PreMultiply(opening_trsf);
				const TopoDS_Shape& opening_shape = gtrsf.Form() == gp_Other
					? BRepBuilderAPI_GTransform(opening_shapes[i].Shape(),gtrsf,true).Shape()
					: (opening_shapes[i].Shape()).Moved(gtrsf.Trsf());
				builder.Add(opening_compound,opening_shape);
			}

		}
	}

	// Iterate over the shapes of the IfcProduct
	for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it3 = entity_shapes.begin(); it3 != entity_shapes.end(); ++ it3 ) {
		TopoDS_Shape entity_shape_solid;
		const TopoDS_Shape& entity_shape_unlocated = ensure_fit_for_subtraction(it3->Shape(),entity_shape_solid);
		const gp_GTrsf& entity_shape_gtrsf = it3->Placement();
		TopoDS_Shape entity_shape;
		if ( entity_shape_gtrsf.Form() == gp_Other ) {
			Logger::Message(Logger::LOG_WARNING,"Applying non uniform transformation to:",entity->entity);
			entity_shape = BRepBuilderAPI_GTransform(entity_shape_unlocated,entity_shape_gtrsf,true).Shape();
		} else {
			entity_shape = entity_shape_unlocated.Moved(entity_shape_gtrsf.Trsf());
		}

		BRepAlgoAPI_Cut brep_cut(entity_shape,opening_compound);
		bool is_valid = false;
		if ( brep_cut.IsDone() ) {
			TopoDS_Shape brep_cut_result = brep_cut;
				
			BRepCheck_Analyzer analyser(brep_cut_result);
			is_valid = analyser.IsValid() != 0;
			if ( is_valid ) {
				cut_shapes.push_back(IfcGeom::IfcRepresentationShapeItem(brep_cut_result, &it3->Style()));
			}
		}
		if ( !is_valid ) {
			// Apparently processing the boolean operation failed or resulted in an invalid result
			// in which case the original shape without the subtractions is returned instead
			// we try convert the openings in the original way, one by one.
			Logger::Message(Logger::LOG_WARNING,"Subtracting combined openings compound failed:",entity->entity);
			return false;
		}
		
	}
	return true;
}

bool IfcGeom::Kernel::convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face) {
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

bool IfcGeom::Kernel::convert_curve_to_wire(const Handle(Geom_Curve)& curve, TopoDS_Wire& wire) {
	try {
		wire = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(curve));
	} catch(...) { return false; }
	return true;
}

bool IfcGeom::Kernel::profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Shape& face_shape) {
	TopoDS_Vertex* vertices = new TopoDS_Vertex[numVerts];
	
	for ( int i = 0; i < numVerts; i ++ ) {
		gp_XY xy (verts[2*i],verts[2*i+1]);
		trsf.Transforms(xy);
		vertices[i] = BRepBuilderAPI_MakeVertex(gp_Pnt(xy.X(),xy.Y(),0.0f));
	}

	BRepBuilderAPI_MakeWire w;
	for ( int i = 0; i < numVerts; i ++ )
		w.Add(BRepBuilderAPI_MakeEdge(vertices[i],vertices[(i+1)%numVerts]));

	TopoDS_Face face;
	convert_wire_to_face(w.Wire(),face);

	if ( numFillets && *std::max_element(filletRadii, filletRadii + numFillets) > ALMOST_ZERO ) {
		BRepFilletAPI_MakeFillet2d fillet (face);
		for ( int i = 0; i < numFillets; i ++ ) {
			const double radius = filletRadii[i];
			if ( radius <= ALMOST_ZERO ) continue;
			fillet.AddFillet(vertices[filletIndices[i]],radius);
		}
		fillet.Build();
		if (fillet.IsDone()) {
			face = TopoDS::Face(fillet.Shape());
		} else {
			Logger::Message(Logger::LOG_WARNING, "Failed to process profile fillets");
		}
	}

	face_shape = face;

	delete[] vertices;
	return true;
}
double IfcGeom::Kernel::shape_volume(const TopoDS_Shape& s) {
	GProp_GProps prop;
	BRepGProp::VolumeProperties(s, prop);
	return prop.Mass();
}
double IfcGeom::Kernel::face_area(const TopoDS_Face& f) {
	GProp_GProps prop;
	BRepGProp::SurfaceProperties(f,prop);
	return prop.Mass();
}
bool IfcGeom::Kernel::is_convex(const TopoDS_Wire& wire) {
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
			if ( edge_points[0].IsEqual(P1,getValue(GV_POINT_EQUALITY_TOLERANCE))) neighbors.push_back(edge_points[1]);
			else if ( edge_points[1].IsEqual(P1, getValue(GV_POINT_EQUALITY_TOLERANCE))) neighbors.push_back(edge_points[0]);
		}
		// There should be two of these
		if ( neighbors.size() != 2 ) return false;
		// Now find the non neighboring points
		std::vector<gp_Pnt> non_neighbors;
		for ( TopExp_Explorer exp2(wire,TopAbs_VERTEX); exp2.More(); exp2.Next() ) {
			TopoDS_Vertex V2 = TopoDS::Vertex(exp2.Current());
			gp_Pnt P2 = BRep_Tool::Pnt(V2);
			if ( P1.IsEqual(P2,getValue(GV_POINT_EQUALITY_TOLERANCE)) ) continue;
			bool found = false;
			for( std::vector<gp_Pnt>::const_iterator it = neighbors.begin(); it != neighbors.end(); ++ it ) {
				if ( (*it).IsEqual(P2,getValue(GV_POINT_EQUALITY_TOLERANCE)) ) { found = true; break; }
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
TopoDS_Shape IfcGeom::Kernel::halfspace_from_plane(const gp_Pln& pln,const gp_Pnt& cent) {
	TopoDS_Face face = BRepBuilderAPI_MakeFace(pln).Face();
	return BRepPrimAPI_MakeHalfSpace(face,cent).Solid();
}
gp_Pln IfcGeom::Kernel::plane_from_face(const TopoDS_Face& face) {
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
gp_Pnt IfcGeom::Kernel::point_above_plane(const gp_Pln& pln, bool agree) {
	if ( agree ) {
		return pln.Location().Translated(pln.Axis().Direction());
	} else {
		return pln.Location().Translated(-pln.Axis().Direction());
	}
}

void IfcGeom::Kernel::apply_tolerance(TopoDS_Shape& s, double t) {
	ShapeFix_ShapeTolerance tol;
	tol.SetTolerance(s, t);
}

static double deflection_tolerance = 0.001;
static double wire_creation_tolerance = 0.0001;
static double minimal_face_area = 0.000001;
static double point_equality_tolerance = 0.00001;
static double max_faces_to_sew = -1.0;
static double ifc_length_unit = 1.0;
static double ifc_planeangle_unit = -1.0;
static double modelling_precision = 0.00001;
static double dimensionality = 1;

void IfcGeom::Kernel::setValue(GeomValue var, double value) {
	switch (var) {
	case GV_DEFLECTION_TOLERANCE:
		deflection_tolerance = value;
		break;
	case GV_WIRE_CREATION_TOLERANCE:
		wire_creation_tolerance = value;
		break;
	case GV_MINIMAL_FACE_AREA:
		minimal_face_area = value;
		break;
	case GV_POINT_EQUALITY_TOLERANCE:
		point_equality_tolerance = value;
		break;
	case GV_MAX_FACES_TO_SEW:
		max_faces_to_sew = value;
		break;
	case GV_LENGTH_UNIT:
		ifc_length_unit = value;
		break;
	case GV_PLANEANGLE_UNIT:
		ifc_planeangle_unit = value;
		break;
	case GV_PRECISION:
		modelling_precision = value;
		break;
	case GV_DIMENSIONALITY:
		dimensionality = value;
		break;
	default:
		assert(!"never reach here");
	}
}

double IfcGeom::Kernel::getValue(GeomValue var) {
	switch (var) {
	case GV_DEFLECTION_TOLERANCE:
		return deflection_tolerance;
	case GV_WIRE_CREATION_TOLERANCE:
		return wire_creation_tolerance;
	case GV_MINIMAL_FACE_AREA:
		return minimal_face_area;
	case GV_POINT_EQUALITY_TOLERANCE:
		return point_equality_tolerance;
	case GV_MAX_FACES_TO_SEW:
		return max_faces_to_sew;
	case GV_LENGTH_UNIT:
		return ifc_length_unit;
		break;
	case GV_PLANEANGLE_UNIT:
		return ifc_planeangle_unit;
		break;
	case GV_PRECISION:
		return modelling_precision;
		break;
	case GV_DIMENSIONALITY:
		return dimensionality;
		break;
	}
	assert(!"never reach here");
	return 0;
}

IfcSchema::IfcProductDefinitionShape* IfcGeom::tesselate(TopoDS_Shape& shape, double deflection, IfcEntityList::ptr es) {
	BRepMesh_IncrementalMesh(shape, deflection);

	IfcSchema::IfcFace::list::ptr faces (new IfcSchema::IfcFace::list);

	for (TopExp_Explorer exp(shape, TopAbs_FACE); exp.More(); exp.Next()) {
		const TopoDS_Face& face = TopoDS::Face(exp.Current());
		TopLoc_Location loc;
		Handle(Poly_Triangulation) tri = BRep_Tool::Triangulation(face, loc);

		if (! tri.IsNull()) {
			const TColgp_Array1OfPnt& nodes = tri->Nodes();
			std::vector<IfcSchema::IfcCartesianPoint*> vertices;
			for (int i = 1; i <= nodes.Length(); ++i) {
				gp_Pnt pnt = nodes(i).Transformed(loc);
				std::vector<double> xyz; xyz.push_back(pnt.X()); xyz.push_back(pnt.Y()); xyz.push_back(pnt.Z());
				IfcSchema::IfcCartesianPoint* cpnt = new IfcSchema::IfcCartesianPoint(xyz);
				vertices.push_back(cpnt);
				es->push(cpnt);
			}
			const Poly_Array1OfTriangle& triangles = tri->Triangles();			
			for (int i = 1; i <= triangles.Length(); ++ i) {
				int n1, n2, n3;
				triangles(i).Get(n1, n2, n3);
				IfcSchema::IfcCartesianPoint::list::ptr points (new IfcSchema::IfcCartesianPoint::list);
				points->push(vertices[n1-1]);
				points->push(vertices[n2-1]);
				points->push(vertices[n3-1]);
				IfcSchema::IfcPolyLoop* loop = new IfcSchema::IfcPolyLoop(points);
				IfcSchema::IfcFaceOuterBound* bound = new IfcSchema::IfcFaceOuterBound(loop, face.Orientation() != TopAbs_REVERSED);
				IfcSchema::IfcFaceBound::list::ptr bounds (new IfcSchema::IfcFaceBound::list);
				bounds->push(bound);
				IfcSchema::IfcFace* face = new IfcSchema::IfcFace(bounds);
				es->push(loop);
				es->push(bound);
				es->push(face);
				faces->push(face);
			}
		}
	}
	IfcSchema::IfcOpenShell* shell = new IfcSchema::IfcOpenShell(faces);
	IfcSchema::IfcConnectedFaceSet::list::ptr shells (new IfcSchema::IfcConnectedFaceSet::list);
	shells->push(shell);
	IfcSchema::IfcFaceBasedSurfaceModel* surface_model = new IfcSchema::IfcFaceBasedSurfaceModel(shells);

	IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list);
	IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list);

	items->push(surface_model);

	IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
		0, std::string("Facetation"), std::string("SurfaceModel"), items);

	reps->push(rep);
	IfcSchema::IfcProductDefinitionShape* shapedef = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, reps);

	es->push(shell);
	es->push(surface_model);
	es->push(rep);
	es->push(shapedef);

	return shapedef;
}

// Returns the vertex part of an TopoDS_Edge edge that is not TopoDS_Vertex vertex
TopoDS_Vertex find_other(const TopoDS_Edge& edge, const TopoDS_Vertex& vertex) {
	TopExp_Explorer exp(edge, TopAbs_VERTEX);
	while (exp.More()) {
		if (!exp.Current().IsSame(vertex)) {
			return TopoDS::Vertex(exp.Current());
		}
		exp.Next();
	}
	return TopoDS_Vertex();
}

TopoDS_Edge find_next(const TopTools_IndexedMapOfShape& edge_set, const TopTools_IndexedDataMapOfShapeListOfShape& vertex_to_edges, const TopoDS_Vertex& current, const TopoDS_Edge& previous_edge) {
	const TopTools_ListOfShape& edges = vertex_to_edges.FindFromKey(current);
	TopTools_ListIteratorOfListOfShape eit;
	for (eit.Initialize(edges); eit.More(); eit.Next()) {
		const TopoDS_Edge& edge = TopoDS::Edge(eit.Value());
		if (edge.IsSame(previous_edge)) continue;
		if (edge_set.Contains(edge)) {
			return edge;
		}
	}
	return TopoDS_Edge();
}

bool IfcGeom::Kernel::fill_nonmanifold_wires_with_planar_faces(TopoDS_Shape& shape) {
	BRepOffsetAPI_Sewing sew;
	sew.Add(shape);

	TopTools_IndexedDataMapOfShapeListOfShape edge_to_faces;
	TopTools_IndexedDataMapOfShapeListOfShape vertex_to_edges;
	std::set<int> visited;
	TopTools_IndexedMapOfShape edge_set;

	TopExp::MapShapesAndAncestors (shape, TopAbs_EDGE, TopAbs_FACE, edge_to_faces);

	const int num_edges = edge_to_faces.Extent();
	for (int i = 1; i <= num_edges; ++i) {
		const TopTools_ListOfShape& faces = edge_to_faces.FindFromIndex(i);
		const int count = faces.Extent();
		// Find only the non-manifold edges: Edges that are only part of a
		// single face and therefore part of the wire(s) we want to fill.
		if (count == 1) {
			const TopoDS_Shape& edge = edge_to_faces.FindKey(i);
			TopExp::MapShapesAndAncestors (edge, TopAbs_VERTEX, TopAbs_EDGE, vertex_to_edges);
			edge_set.Add(edge);
		}
	}

	const int num_verts = vertex_to_edges.Extent();
	TopoDS_Vertex first, current;
	TopoDS_Edge previous_edge;

	// Now loop over all the vertices that are part of the wire(s) to be filled
	for (int i = 1; i <= num_verts; ++i) {
		first = current = TopoDS::Vertex(vertex_to_edges.FindKey(i));
		const bool isSame = first.IsSame(current);
		// We keep track of the vertices we already used
		if (visited.find(vertex_to_edges.FindIndex(current)) != visited.end()) {
			continue;
		}
		// Given these vertices, try to find closed loops and create new
		// wires out of them.
		BRepBuilderAPI_MakeWire w;
		while (true) {
			visited.insert(vertex_to_edges.FindIndex(current));
			// Find the edge that the current vertex is part of and points
			// away from the previous vertex (null for the first vertex).
			TopoDS_Edge edge = find_next(edge_set, vertex_to_edges, current, previous_edge);
			if (edge.IsNull()) {
				return false;
			}
			TopoDS_Vertex other = find_other(edge, current);
			if (other.IsNull()) {
				// Dealing with a conical edge probably, for some reason
				// this works better than adding the edge directly.
				double u1, u2;
				Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u1, u2);
				w.Add(BRepBuilderAPI_MakeEdge(crv, u1, u2));
				break;
			} else {
				w.Add(edge);
			}
			// See if the starting point of this loop has been reached. Note that
			// additional wires after this one potentially will be created.
			if (other.IsSame(first)) {
				break;
			}
			previous_edge = edge;
			current = other;
		}
		sew.Add(BRepBuilderAPI_MakeFace(w));
		previous_edge.Nullify();
	}
		
	sew.Perform();
	shape = sew.SewedShape();

	try {
		ShapeFix_Solid solid;
		solid.LimitTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
		shape = solid.SolidFromShell(TopoDS::Shell(shape));
	} catch(...) {}

	return true;
}

bool IfcGeom::Kernel::flatten_shape_list(const IfcGeom::IfcRepresentationShapeItems& shapes, TopoDS_Shape& result, bool fuse) {
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	result = TopoDS_Shape();
			
	for ( IfcGeom::IfcRepresentationShapeItems::const_iterator it = shapes.begin(); it != shapes.end(); ++ it ) {
		TopoDS_Shape merged;
		const TopoDS_Shape& s = it->Shape();
		if (fuse) {
			ensure_fit_for_subtraction(s, merged);
		} else {
			merged = s;
		}
		const gp_GTrsf& trsf = it->Placement();
		bool trsf_valid = false;
		gp_Trsf _trsf;
		try {
			_trsf = trsf.Trsf();
			trsf_valid = true;
		} catch (...) {}
		const TopoDS_Shape moved_shape = trsf_valid ? merged.Moved(_trsf) :
			BRepBuilderAPI_GTransform(merged,trsf,true).Shape();

		if (shapes.size() == 1) {
			result = moved_shape;
			const double precision = getValue(GV_PRECISION);
			apply_tolerance(result, precision);
			return true;
		}

		if (fuse) {
			if (result.IsNull()) {
				result = moved_shape;
			} else {
				BRepAlgoAPI_Fuse brep_fuse(result, moved_shape);
				if ( brep_fuse.IsDone() ) {
					TopoDS_Shape fused = brep_fuse;

					ShapeFix_Shape fix(result);
					fix.Perform();
					result = fix.Shape();
		
					bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
					if ( is_valid ) {
						result = fused;
					} 
				}
			}
		} else {
			builder.Add(compound,moved_shape);
		}
	}

	const bool success = !result.IsNull();
	if (success) {
		const double precision = getValue(GV_PRECISION);
		apply_tolerance(result, precision);
	}

	return success;
}
	
void IfcGeom::Kernel::remove_redundant_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol) {
	if (tol <= 0.) tol = getValue(GV_POINT_EQUALITY_TOLERANCE);
	tol *= tol;

	while (true) {
		bool removed = false;
		int n = polygon.Length() - (closed ? 0 : 1);
		for (int i = 1; i <= n; ++i) {
			// wrap around to the first point in case of a closed loop
			int j = (i % polygon.Length()) + 1;
			double dist = polygon.Value(i).SquareDistance(polygon.Value(j));
			if (dist < tol) {
				// do not remove the first or last point to
				// maintain connectivity with other wires
				if ((closed && j == 1) || (!closed && j == n)) polygon.Remove(i);
				else polygon.Remove(j);
				removed = true;
				break;
			}
		}
		if (!removed) break;
	}
}

template <typename P>
IfcGeom::BRepElement<P>* IfcGeom::Kernel::create_brep_for_representation_and_product(const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product) {
	IfcGeom::Representation::BRep* shape;
	IfcGeom::IfcRepresentationShapeItems shapes;

	if ( !convert_shapes(representation,shapes) ) {
		return 0;
	}

	int parent_id = -1;
	try {
		IfcSchema::IfcObjectDefinition* parent_object = get_decomposing_entity(product);
		if (parent_object) {
			parent_id = parent_object->entity->id();
		}
	} catch (...) {}
		
	const std::string name = product->hasName() ? product->Name() : "";
	const std::string guid = product->GlobalId();
		
	gp_Trsf trsf;
	try {
		convert(product->ObjectPlacement(),trsf);
	} catch (...) {}

	// Does the IfcElement have any IfcOpenings?
	// Note that openings for IfcOpeningElements are not processed
	IfcSchema::IfcRelVoidsElement::list::ptr openings;
	if ( product->is(IfcSchema::Type::IfcElement) && !product->is(IfcSchema::Type::IfcOpeningElement) ) {
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
		openings = element->HasOpenings();
	}
	// Is the IfcElement a decomposition of an IfcElement with any IfcOpeningElements?
	if ( product->is(IfcSchema::Type::IfcBuildingElementPart ) ) {
		IfcSchema::IfcBuildingElementPart* part = (IfcSchema::IfcBuildingElementPart*)product;
#ifdef USE_IFC4
		IfcSchema::IfcRelAggregates::list::ptr decomposes = part->Decomposes();
		for ( IfcSchema::IfcRelAggregates::list::it it = decomposes->begin(); it != decomposes->end(); ++ it ) {
#else
		IfcSchema::IfcRelDecomposes::list::ptr decomposes = part->Decomposes();
		for ( IfcSchema::IfcRelDecomposes::list::it it = decomposes->begin(); it != decomposes->end(); ++ it ) {
#endif
			IfcSchema::IfcObjectDefinition* obdef = (*it)->RelatingObject();
			if ( obdef->is(IfcSchema::Type::IfcElement) ) {
				IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)obdef;
				openings->push(element->HasOpenings());
			}
		}
	}

	const std::string product_type = IfcSchema::Type::ToString(product->type());
	ElementSettings element_settings(settings, getValue(GV_LENGTH_UNIT), product_type);

	if ( !settings.disable_opening_subtractions() && openings && openings->size() ) {
		IfcGeom::IfcRepresentationShapeItems opened_shapes;
		try {
			if ( settings.faster_booleans() ) {
				bool succes = convert_openings_fast(product,openings,shapes,trsf,opened_shapes);
				if ( ! succes ) {
					opened_shapes.clear();
					convert_openings(product,openings,shapes,trsf,opened_shapes);
				}
			} else {
				convert_openings(product,openings,shapes,trsf,opened_shapes);
			}
		} catch(...) { 
			Logger::Message(Logger::LOG_ERROR,"Error processing openings for:",product->entity); 
		}
		if ( settings.use_world_coords() ) {
			for ( IfcGeom::IfcRepresentationShapeItems::iterator it = opened_shapes.begin(); it != opened_shapes.end(); ++ it ) {
				it->prepend(trsf);
			}
			trsf = gp_Trsf();
		}
		shape = new IfcGeom::Representation::BRep(element_settings, representation->entity->id(), opened_shapes);
	} else if ( settings.use_world_coords() ) {
		for ( IfcGeom::IfcRepresentationShapeItems::iterator it = shapes.begin(); it != shapes.end(); ++ it ) {
			it->prepend(trsf);
		}
		trsf = gp_Trsf();
		shape = new IfcGeom::Representation::BRep(element_settings, representation->entity->id(), shapes);
	} else {
		shape = new IfcGeom::Representation::BRep(element_settings, representation->entity->id(), shapes);
	}

	std::string context_string = "";
	if (representation->hasRepresentationIdentifier()) {
		context_string = representation->RepresentationIdentifier();
	} else if (representation->ContextOfItems()->hasContextType()) {
		context_string = representation->ContextOfItems()->ContextType();
	}

	return new BRepElement<P>(
		product->entity->id(),
		parent_id,
		name, 
		product_type,
		guid,
		context_string,
		trsf,
		shape
	);
}

IfcSchema::IfcObjectDefinition* IfcGeom::Kernel::get_decomposing_entity(IfcSchema::IfcProduct* product) {
	IfcSchema::IfcObjectDefinition* parent = 0;

	// In case of an opening element, parent to the RelatingBuildingElement
	if ( product->is(IfcSchema::Type::IfcOpeningElement ) ) {
		IfcSchema::IfcOpeningElement* opening = (IfcSchema::IfcOpeningElement*)product;
		IfcSchema::IfcRelVoidsElement::list::ptr voids = opening->VoidsElements();
		if ( voids->size() ) {
			IfcSchema::IfcRelVoidsElement* ifc_void = *voids->begin();
			parent = ifc_void->RelatingBuildingElement();
		}
	} else if ( product->is(IfcSchema::Type::IfcElement ) ) {
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
		IfcSchema::IfcRelFillsElement::list::ptr fills = element->FillsVoids();
		// Incase of a RelatedBuildingElement parent to the opening element
		if ( fills->size() ) {
			for ( IfcSchema::IfcRelFillsElement::list::it it = fills->begin(); it != fills->end(); ++ it ) {
				IfcSchema::IfcRelFillsElement* fill = *it;
				IfcSchema::IfcObjectDefinition* ifc_objectdef = fill->RelatingOpeningElement();
				if ( product == ifc_objectdef ) continue;
				parent = ifc_objectdef;
			}
		} 
		// Else simply parent to the containing structure
		if (!parent) {
			IfcSchema::IfcRelContainedInSpatialStructure::list::ptr parents = element->ContainedInStructure();
			if ( parents->size() ) {
				IfcSchema::IfcRelContainedInSpatialStructure* container = *parents->begin();
				parent = container->RelatingStructure();
			}
		}
	}
	// Parent decompositions to the RelatingObject
	if (!parent) {
		IfcEntityList::ptr parents = product->entity->getInverse(IfcSchema::Type::IfcRelAggregates, -1);
		parents->push(product->entity->getInverse(IfcSchema::Type::IfcRelNests, -1));
		for ( IfcEntityList::it it = parents->begin(); it != parents->end(); ++ it ) {
			IfcSchema::IfcRelDecomposes* decompose = (IfcSchema::IfcRelDecomposes*)*it;
			IfcSchema::IfcObjectDefinition* ifc_objectdef;
#ifdef USE_IFC4
			if (decompose->is(IfcSchema::Type::IfcRelAggregates)) {
				ifc_objectdef = ((IfcSchema::IfcRelAggregates*)decompose)->RelatingObject();
			} else {
				continue;
			}
#else
			ifc_objectdef = decompose->RelatingObject();
#endif
			if ( product == ifc_objectdef ) continue;
			parent = ifc_objectdef;
		}
	}
	return parent;
}

template IfcGeom::BRepElement<float>* IfcGeom::Kernel::create_brep_for_representation_and_product<float>(const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);
template IfcGeom::BRepElement<double>* IfcGeom::Kernel::create_brep_for_representation_and_product<double>(const IteratorSettings& settings, IfcSchema::IfcRepresentation* representation, IfcSchema::IfcProduct* product);

std::pair<std::string, double> IfcGeom::Kernel::initializeUnits(IfcSchema::IfcUnitAssignment* unit_assignment) {
	// Set default units, set length to meters, angles to undefined
	setValue(IfcGeom::Kernel::GV_LENGTH_UNIT, 1.0);
	setValue(IfcGeom::Kernel::GV_PLANEANGLE_UNIT, -1.0);

	std::string unit_name = "METER";
	double unit_magnitude = 1.;

	try {
		IfcEntityList::ptr units = unit_assignment->Units();
		if (!units || !units->size()) {
			Logger::Message(Logger::LOG_ERROR, "No unit information found");
		} else {
			for ( IfcEntityList::it it = units->begin(); it != units->end(); ++ it ) {
				std::string current_unit_name = "";
				IfcUtil::IfcBaseClass* base = *it;
				IfcSchema::IfcSIUnit* unit = 0;
				double value = 1.f;
				if ( base->is(IfcSchema::Type::IfcConversionBasedUnit) ) {
					IfcSchema::IfcConversionBasedUnit* u = (IfcSchema::IfcConversionBasedUnit*)base;
					current_unit_name = u->Name();
					IfcSchema::IfcMeasureWithUnit* u2 = u->ConversionFactor();
					IfcSchema::IfcUnit* u3 = u2->UnitComponent();
					if ( u3->is(IfcSchema::Type::IfcSIUnit) ) {
						unit = (IfcSchema::IfcSIUnit*) u3;
					}
					IfcSchema::IfcValue* v = u2->ValueComponent();
					// Quick hack to get the numeric value from an IfcValue:
					const double f = *v->entity->getArgument(0);
					value *= f;
				} else if ( base->is(IfcSchema::Type::IfcSIUnit) ) {
					unit = (IfcSchema::IfcSIUnit*)base;
				}
				if ( unit ) {
					if ( unit->hasPrefix() ) {
						value *= IfcParse::IfcSIPrefixToValue(unit->Prefix());
					}
					IfcSchema::IfcUnitEnum::IfcUnitEnum type = unit->UnitType();
					if ( type == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT ) {
						setValue(IfcGeom::Kernel::GV_LENGTH_UNIT,value);
						if (current_unit_name.empty()) {
							if (unit->hasPrefix()) {
								current_unit_name = IfcSchema::IfcSIPrefix::ToString(unit->Prefix());
							}
							current_unit_name += IfcSchema::IfcSIUnitName::ToString(unit->Name());
						}
						unit_magnitude = value;
						unit_name = current_unit_name;
					} else if ( type == IfcSchema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT ) {
						setValue(IfcGeom::Kernel::GV_PLANEANGLE_UNIT, value);
					}
				}
			}
		}
	} catch (const IfcParse::IfcException& ex) {
		std::stringstream ss;
		ss << "Failed to determine unit information '" << ex.what() << "'";
		Logger::Message(Logger::LOG_ERROR, ss.str());
	}

	return std::pair<std::string, double>(unit_name, unit_magnitude);
}