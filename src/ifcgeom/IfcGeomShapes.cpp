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
 * Implementations of the various conversion functions defined in IfcRegister.h *
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

#ifdef SCHEMA_HAS_IfcToroidalSurface
#include <Geom_ToroidalSurface.hxx>
#endif

#define Kernel MAKE_TYPE_NAME(Kernel)

// uncomment if you'd like negative or close to zero extrusion depths to succeed
// #define PERMISSIVE_EXTRUSION

bool IfcGeom::Kernel::convert(const IfcSchema::IfcExtrudedAreaSolid* l, TopoDS_Shape& shape) {
	const double height = l->Depth() * getValue(GV_LENGTH_UNIT);
	if (height < getValue(GV_PRECISION)) {
		Logger::Message(Logger::LOG_ERROR, "Non-positive extrusion height encountered for:", l);
#ifndef PERMISSIVE_EXTRUSION
		return false;
#endif
	}

	TopoDS_Shape face;
	if ( !convert_face(l->SweptArea(),face) ) return false;

#ifdef PERMISSIVE_EXTRUSION
	if (abs(height) < getValue(GV_PRECISION)) {
		shape = face;
		return true;
	}
#endif

	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = l->hasPosition();
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}

	gp_Dir dir;
	convert(l->ExtrudedDirection(),dir);

	shape.Nullify();

	/*
	// @nb This logic was probably flawed always as this does not by itself result in a valid compsolid...
	if (face.ShapeType() == TopAbs_COMPOUND) {
		
		// For compounds (most likely the result of a IfcCompositeProfileDef) 
		// create a compound solid shape.
		
		TopExp_Explorer exp(face, TopAbs_FACE);
		
		TopoDS_CompSolid compound;
		BRep_Builder builder;
		builder.MakeCompSolid(compound);
		
		int num_faces_extruded = 0;
		for (; exp.More(); exp.Next(), ++num_faces_extruded) {
			builder.Add(compound, BRepPrimAPI_MakePrism(exp.Current(), height*dir));
		}

		if (num_faces_extruded) {
			shape = compound;
		}

	}
	*/
	
	if (shape.IsNull()) {	
		shape = BRepPrimAPI_MakePrism(face, height*dir);
	}

	if (has_position && !shape.IsNull()) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}

	return !shape.IsNull();
}

#ifdef SCHEMA_HAS_IfcExtrudedAreaSolidTapered
bool IfcGeom::Kernel::convert(const IfcSchema::IfcExtrudedAreaSolidTapered* l, TopoDS_Shape& shape) {
	const double height = l->Depth() * getValue(GV_LENGTH_UNIT);
	if (height < getValue(GV_PRECISION)) {
		Logger::Message(Logger::LOG_ERROR, "Non-positive extrusion height encountered for:", l);
		return false;
	}

	TopoDS_Shape face1, face2;
	if (!convert_face(l->SweptArea(), face1)) return false;
	if (!convert_face(l->EndSweptArea(), face2)) return false;

	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = l->hasPosition();
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}

	gp_Dir dir;
	convert(l->ExtrudedDirection(), dir);

	gp_Trsf end_profile;
	end_profile.SetTranslation(height * dir);

	TopoDS_Edge spine_edge = BRepBuilderAPI_MakeEdge(gp_Pnt(), gp_Pnt((height * dir).XYZ())).Edge();
	TopoDS_Wire wire = BRepBuilderAPI_MakeWire(spine_edge).Wire();

	shape.Nullify();

	TopExp_Explorer exp1(face1, TopAbs_WIRE);
	TopExp_Explorer exp2(face2, TopAbs_WIRE);

	TopoDS_Vertex v1, v2;
	TopExp::Vertices(wire, v1, v2);

	TopoDS_Shape shell;
	TopoDS_Compound compound;
	BRep_Builder compound_builder;

	for (; exp1.More() && exp2.More(); exp1.Next(), exp2.Next()) {
		const TopoDS_Wire& w1 = TopoDS::Wire(exp1.Current());
		const TopoDS_Wire& w2 = TopoDS::Wire(exp2.Current());

		BRepOffsetAPI_MakePipeShell builder(wire);
		builder.Add(w1, v1);
		builder.Add(w2.Moved(end_profile), v2);

		TopoDS_Shape result = builder.Shape();

		TopTools_ListOfShape li;
		shape_to_face_list(result, li);
		li.Append(BRepBuilderAPI_MakeFace(w1).Face().Reversed());
		li.Append(BRepBuilderAPI_MakeFace(w2).Face().Moved(end_profile));
		
		create_solid_from_faces(li, result, true);

		// @todo ugly hack

		// The reason for this distinction is that at this point of the loop we're not sure anymore
		// whether this was constructed from an inner or outer bound. So rather than iterating over
		// wires of `face1` and `face2` we should iterate over the faces and then properly check with
		// BRepTools::OuterBound().
		// Currently this distinction happens based on profile type which is not robust and probably
		// not complete.
		if (shell.IsNull()) {
			shell = result;
		} else if (l->SweptArea()->declaration().is(IfcSchema::IfcCircleHollowProfileDef::Class()) ||
			l->SweptArea()->declaration().is(IfcSchema::IfcRectangleHollowProfileDef::Class()) ||
			l->SweptArea()->declaration().is(IfcSchema::IfcArbitraryProfileDefWithVoids::Class()))
		{
			// @todo properly check for failure and all.
			shell = BRepAlgoAPI_Cut(shell, result).Shape();
		} else {
			if (compound.IsNull()) {
				compound_builder.MakeCompound(compound);
				compound_builder.Add(compound, shell);
			}
			compound_builder.Add(compound, result);
		}
	}

	if (!compound.IsNull()) {
		shell = compound;
	}

	shape = shell;

	if (exp1.More() != exp2.More()) {
		Logger::Message(Logger::LOG_ERROR, "Inconsistent profiles encountered for:", l);
	}

	if (has_position && !shape.IsNull()) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}

	return !shape.IsNull();
}
#endif

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSurfaceOfLinearExtrusion* l, TopoDS_Shape& shape) {
	TopoDS_Wire wire;
	if ( !convert_wire(l->SweptCurve(), wire) ) {
		TopoDS_Face face;
		if ( !convert_face(l->SweptCurve(),face) ) return false;
		TopExp_Explorer exp(face, TopAbs_WIRE);
		wire = TopoDS::Wire(exp.Current());
	}
	const double height = l->Depth() * getValue(GV_LENGTH_UNIT);
	
	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptSurface_Position_IS_OPTIONAL
	has_position = l->hasPosition();
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}

	gp_Dir dir;
	convert(l->ExtrudedDirection(),dir);

	shape = BRepPrimAPI_MakePrism(wire, height*dir);
	
	if (has_position) {
		// IfcSweptSurface.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}
	
	return !shape.IsNull();
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSurfaceOfRevolution* l, TopoDS_Shape& shape) {
	TopoDS_Wire wire;
	if ( !convert_wire(l->SweptCurve(), wire) ) {
		TopoDS_Face face;
		if ( !convert_face(l->SweptCurve(),face) ) return false;
		TopExp_Explorer exp(face, TopAbs_WIRE);
		wire = TopoDS::Wire(exp.Current());
	}

	gp_Ax1 ax1;
	IfcGeom::Kernel::convert(l->AxisPosition(), ax1);

	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptSurface_Position_IS_OPTIONAL
	has_position = l->hasPosition();
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}
	
	shape = BRepPrimAPI_MakeRevol(wire, ax1);

	if (has_position) {
		// IfcSweptSurface.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}

	return !shape.IsNull();
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRevolvedAreaSolid* l, TopoDS_Shape& shape) {
	const double ang = l->Angle() * getValue(GV_PLANEANGLE_UNIT);

	TopoDS_Shape face;
	if ( ! convert_face(l->SweptArea(),face) ) return false;

	gp_Ax1 ax1;
	IfcGeom::Kernel::convert(l->Axis(), ax1);

	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = l->hasPosition();
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}


	{
		// https://github.com/IfcOpenShell/IfcOpenShell/issues/1030
		// Check whether Axis does not intersect SweptArea

		double min_dot = +std::numeric_limits<double>::infinity();
		double max_dot = -std::numeric_limits<double>::infinity();

		gp_Ax2 ax(ax1.Location(), gp::DZ(), ax1.Direction());

		TopExp_Explorer exp(face, TopAbs_EDGE);
		for (; exp.More(); exp.Next()) {
			BRepAdaptor_Curve crv(TopoDS::Edge(exp.Current()));
			GCPnts_QuasiUniformDeflection tessellater(crv, getValue(GV_PRECISION));

			int n = tessellater.NbPoints();
			for (int i = 1; i <= n; ++i) {
				double d = ax.YDirection().XYZ().Dot(tessellater.Value(i).XYZ());
				if (d < min_dot) {
					min_dot = d;
				}
				if (d > max_dot) {
					max_dot = d;
				}
			}
		}

		bool intersecting;
		if (std::abs(min_dot) > std::abs(max_dot)) {
			intersecting = max_dot > + getValue(GV_PRECISION);
		} else {
			intersecting = min_dot < - getValue(GV_PRECISION);
		}

		if (intersecting) {
			Logger::Warning("Warning Axis and SweptArea intersecting", l);
		}
	}

	if (ang >= M_PI * 2. - ALMOST_ZERO) {
		shape = BRepPrimAPI_MakeRevol(face, ax1);
	} else {
		shape = BRepPrimAPI_MakeRevol(face, ax1, ang);
	}

	if (has_position) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}

	return !shape.IsNull();
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcManifoldSolidBrep* l, IfcRepresentationShapeItems& shape) {
	TopoDS_Shape s;
	const SurfaceStyle* collective_style = get_style(l);
	if (convert_shape(l->Outer(),s) ) {
		const SurfaceStyle* indiv_style = get_style(l->Outer());

		IfcSchema::IfcClosedShell::list::ptr voids(new IfcSchema::IfcClosedShell::list);
		if (l->declaration().is(IfcSchema::IfcFacetedBrepWithVoids::Class())) {
			voids = l->as<IfcSchema::IfcFacetedBrepWithVoids>()->Voids();
		}
#ifdef SCHEMA_HAS_IfcAdvancedBrepWithVoids
		if (l->declaration().is(IfcSchema::IfcAdvancedBrepWithVoids::Class())) {
			voids = l->as<IfcSchema::IfcAdvancedBrepWithVoids>()->Voids();
		}
#endif

		for (IfcSchema::IfcClosedShell::list::it it = voids->begin(); it != voids->end(); ++it) {
			TopoDS_Shape s2;
			/// @todo No extensive shapefixing since shells should be disjoint.
			/// @todo Awaiting generalized boolean ops module with appropriate checking
			if (convert_shape(l->Outer(), s2)) {
				s = BRepAlgoAPI_Cut(s, s2).Shape();
			}
		}

		shape.push_back(IfcRepresentationShapeItem(l->data().id(), s, indiv_style ? indiv_style : collective_style));
		return true;
	}
	return false;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcFaceBasedSurfaceModel* l, IfcRepresentationShapeItems& shapes) {
	bool part_success = false;
	IfcSchema::IfcConnectedFaceSet::list::ptr facesets = l->FbsmFaces();
	const SurfaceStyle* collective_style = get_style(l);
	for( IfcSchema::IfcConnectedFaceSet::list::it it = facesets->begin(); it != facesets->end(); ++ it ) {
		TopoDS_Shape s;
		const SurfaceStyle* shell_style = get_style(*it);
		if (convert_shape(*it,s)) {
			shapes.push_back(IfcRepresentationShapeItem(l->data().id(), s, shell_style ? shell_style : collective_style));
			part_success |= true;
		}
	}
	return part_success;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcHalfSpaceSolid* l, TopoDS_Shape& shape) {
	IfcSchema::IfcSurface* surface = l->BaseSurface();
	if ( ! surface->declaration().is(IfcSchema::IfcPlane::Class()) ) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BaseSurface:", surface);
		return false;
	}
	gp_Pln pln;
	IfcGeom::Kernel::convert((IfcSchema::IfcPlane*)surface,pln);
	const gp_Pnt pnt = pln.Location().Translated( l->AgreementFlag() ? -pln.Axis().Direction() : pln.Axis().Direction());
	shape = BRepPrimAPI_MakeHalfSpace(BRepBuilderAPI_MakeFace(pln),pnt).Solid();
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPolygonalBoundedHalfSpace* l, TopoDS_Shape& shape) {
	TopoDS_Shape halfspace;
	if ( ! IfcGeom::Kernel::convert((IfcSchema::IfcHalfSpaceSolid*)l,halfspace) ) return false;	
	
	TopoDS_Wire wire;
	if ( ! convert_wire(l->PolygonalBoundary(),wire) || ! wire.Closed() ) return false;
	
	gp_Trsf trsf;
	if ( ! convert(l->Position(),trsf) ) return false;

	TColgp_SequenceOfPnt points;
	if (wire_to_sequence_of_point(wire, points)) {
		// Boolean subtractions not very robust for narrow operands, 
		// increase minimal point spacing to eliminate such shapes.
		const double t = getValue(GV_PRECISION) * 10.;
		remove_duplicate_points_from_loop(points, wire.Closed() != 0, t); // Note: wire always closed, as per if statement above
		remove_collinear_points_from_loop(points, wire.Closed() != 0, t);
		if (points.Length() < 3) {
			Logger::Message(Logger::LOG_ERROR, "Not enough points retained from:", l->PolygonalBoundary());
			return false;
		}
		sequence_of_point_to_wire(points, wire, wire.Closed() != 0);
	}

	TopoDS_Shape prism = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire),gp_Vec(0,0,200));
	gp_Trsf down; down.SetTranslation(gp_Vec(0,0,-100.0));
	
	// `trsf` and `down` both have a unit scale factor
	prism.Move(trsf*down);	
	
	shape = BRepAlgoAPI_Common(halfspace,prism);
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcShellBasedSurfaceModel* l, IfcRepresentationShapeItems& shapes) {
	IfcEntityList::ptr shells = l->SbsmBoundary();
	const SurfaceStyle* collective_style = get_style(l);
	for( IfcEntityList::it it = shells->begin(); it != shells->end(); ++ it ) {
		TopoDS_Shape s;
		const SurfaceStyle* shell_style = 0;
		if ((*it)->declaration().is(IfcSchema::IfcRepresentationItem::Class())) {
			shell_style = get_style((IfcSchema::IfcRepresentationItem*)*it);
		}
		if (convert_shape(*it,s)) {
			shapes.push_back(IfcRepresentationShapeItem(l->data().id(), s, shell_style ? shell_style : collective_style));
		}
	}
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcBooleanResult* l, TopoDS_Shape& shape) {

	TopoDS_Shape s1;
	IfcRepresentationShapeItems items1;
	TopoDS_Wire boundary_wire;
	IfcSchema::IfcBooleanOperand* operand1 = l->FirstOperand();
	IfcSchema::IfcBooleanOperand* operand2 = l->SecondOperand();
	bool has_halfspace_operand = false;
	
	BOPAlgo_Operation occ_op;

	const IfcSchema::IfcBooleanOperator::Value op = l->Operator();
	if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {
		occ_op = BOPAlgo_CUT;
	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_INTERSECTION) {
		occ_op = BOPAlgo_COMMON;
	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION) {
		occ_op = BOPAlgo_FUSE;
	} else {
		return false;
	}

	std::vector<IfcSchema::IfcBooleanOperand*> second_operands;
	second_operands.push_back(operand2);

	if (occ_op == BOPAlgo_CUT) {
		int n_half_space_operands = 0;
		bool process_as_list = false;
		while (true) {
			auto res1 = operand1->as<IfcSchema::IfcBooleanResult>();
			if (res1 && res1->SecondOperand()->as<IfcSchema::IfcHalfSpaceSolid>() && ++n_half_space_operands > 8) {
				// There is something peculiar about many half space subtraction operands that OCCT does not like.
				// Often these are used to create a semi-curved arch, as is the case in 693. Supplying all these
				// operands at once apparently leads to too many edge-edge interference checks.
				process_as_list = false;
				break;
			}
			if (res1) {
				if (res1->Operator() == op) {
					operand1 = res1->FirstOperand();
					second_operands.push_back(res1->SecondOperand());
				} else {
					process_as_list = false;
					break;
				}
			} else {
				break;
			}
		}

		if (!process_as_list) {
			operand1 = l->FirstOperand();
			second_operands = { operand2 };
		}
	}

	if ( shape_type(operand1) == ST_SHAPELIST ) {
		if (!(convert_shapes(operand1, items1) && flatten_shape_list(items1, s1, true))) {
			return false;
		}
	} else if ( shape_type(operand1) == ST_SHAPE ) {
		if ( ! convert_shape(operand1, s1) ) {
			return false;
		}
		{ TopoDS_Solid temp_solid;
		s1 = ensure_fit_for_subtraction(s1, temp_solid); }
	} else {
		Logger::Message(Logger::LOG_ERROR, "Invalid representation item for boolean operation", operand1);
		return false;
	}

	if (getValue(GV_DISABLE_BOOLEAN_RESULT) > 0.0) {
		shape = s1;
		return true;
	}

	const double first_operand_volume = shape_volume(s1);
	if (first_operand_volume <= ALMOST_ZERO) {
		Logger::Message(Logger::LOG_WARNING, "Empty solid for:", l->FirstOperand());
	}

	TopTools_ListOfShape second_operand_shapes;

	for (auto& op2 : second_operands) {
		TopoDS_Shape s2;

		bool shape2_processed = false;

		bool is_halfspace = op2->declaration().is(IfcSchema::IfcHalfSpaceSolid::Class());
		bool is_unbounded_halfspace = is_halfspace && !op2->declaration().is(IfcSchema::IfcPolygonalBoundedHalfSpace::Class());
		has_halfspace_operand |= is_halfspace;

		{
			if (shape_type(op2) == ST_SHAPELIST) {
				IfcRepresentationShapeItems items2;
				shape2_processed = convert_shapes(op2, items2) && flatten_shape_list(items2, s2, true);
			} else if (shape_type(op2) == ST_SHAPE) {
				shape2_processed = convert_shape(op2, s2);
				if (shape2_processed) {
					TopoDS_Solid temp_solid;
					s2 = ensure_fit_for_subtraction(s2, temp_solid);
				}
			} else {
				Logger::Message(Logger::LOG_ERROR, "Invalid representation item for boolean operation", op2);
			}
		}

		if (is_unbounded_halfspace) {
			TopoDS_Shape temp;
			double d;
			if (fit_halfspace(s1, s2, temp, d)) {
				if (d < getValue(GV_PRECISION)) {
					Logger::Message(Logger::LOG_WARNING, "Halfspace subtraction yields unchanged volume:", l);
					continue;
				} else {
					s2 = temp;
				}
			}
		}

		if (!shape2_processed) {
			Logger::Message(Logger::LOG_ERROR, "Failed to convert SecondOperand:", op2);
			continue;
		}

		if (op2->declaration().is(IfcSchema::IfcHalfSpaceSolid::Class())) {
			const double second_operand_volume = shape_volume(s2);
			if (second_operand_volume <= ALMOST_ZERO) {
				Logger::Message(Logger::LOG_WARNING, "Empty solid for:", op2);
			}
		}

		second_operand_shapes.Append(s2);
	}

	/*
	// TK: A little debugging trick to output both operands for visual inspection
	
	BRep_Builder builder;
	TopoDS_Compound compound;
	builder.MakeCompound(compound);
	builder.Add(compound, s1);
	for (const auto& s2 : second_operand_shapes) {
		builder.Add(compound, s2);
	}
	shape = compound;
	return true;
	*/	

#if OCC_VERSION_HEX < 0x60900
	// @todo: this currently does not compile anymore, do we still need this?
	bool valid_result = boolean_operation(s1, s2, occ_op, shape);
#else
	bool valid_result = boolean_operation(s1, second_operand_shapes, occ_op, shape);
#endif

	if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {
		// In case of a subtraction, a check on volume is performed.
		if (valid_result) {
			const double volume_after_subtraction = shape_volume(shape);
			if ( ALMOST_THE_SAME(first_operand_volume,volume_after_subtraction) )
				Logger::Message(Logger::LOG_WARNING,"Subtraction yields unchanged volume:",l);
		} else {
			Logger::Message(Logger::LOG_ERROR,"Failed to process subtraction:",l);
			shape = s1;
		}
		// NB: After issuing error the first operand is returned!
		return true;
	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION && !valid_result) {
		BRep_Builder B;
		TopoDS_Compound C;
		B.MakeCompound(C);
		B.Add(C, s1);
		TopTools_ListIteratorOfListOfShape it(second_operand_shapes);
		for (; it.More(); it.Next()) {
			B.Add(C, it.Value());
		}
		Logger::Message(Logger::LOG_ERROR, "Failed to process union, creating compound:", l);
		shape = C;
		return true;
	} else {
		return valid_result;
	}
	return false;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcConnectedFaceSet* l, TopoDS_Shape& shape) {
	std::unique_ptr<faceset_helper<>> helper_scope;

	IfcSchema::IfcCartesianPoint::list::ptr points = IfcParse::traverse((IfcUtil::IfcBaseClass*) l)->as<IfcSchema::IfcCartesianPoint>();
	std::vector<const IfcSchema::IfcCartesianPoint*> points_(points->begin(), points->end());

	IfcSchema::IfcPolyLoop::list::ptr loops = IfcParse::traverse((IfcUtil::IfcBaseClass*)l)->as<IfcSchema::IfcPolyLoop>();
	std::vector<const IfcSchema::IfcPolyLoop*> loops_(loops->begin(), loops->end());

	helper_scope.reset(new faceset_helper<>(
		this,
		points_,
		loops_,
		l->declaration().is(IfcSchema::IfcClosedShell::Class())
	));

	faceset_helper_ = helper_scope.get();

	IfcSchema::IfcFace::list::ptr faces = l->CfsFaces();

	double min_face_area = faceset_helper_
		? (faceset_helper_->epsilon() * faceset_helper_->epsilon() / 20.)
		: getValue(GV_MINIMAL_FACE_AREA);

	TopTools_ListOfShape face_list;
	for (IfcSchema::IfcFace::list::it it = faces->begin(); it != faces->end(); ++it) {
		bool success = false;
		TopoDS_Face face;
		
		try {
			success = convert_face(*it, face);
		} catch (const std::exception& e) {
			Logger::Error(e);
		} catch (const Standard_Failure& e) {
			if (e.GetMessageString() && strlen(e.GetMessageString())) {
				Logger::Error(e.GetMessageString());
			} else {
				Logger::Error("Unknown error creating face");
			}
		} catch (...) {
			Logger::Error("Unknown error creating face");
		}

		if (!success) {
			Logger::Message(Logger::LOG_WARNING, "Failed to convert face:", (*it));
			continue;
		}

		if (face.ShapeType() == TopAbs_COMPOUND) {
			TopoDS_Iterator face_it(face, false);
			for (; face_it.More(); face_it.Next()) {
				if (face_it.Value().ShapeType() == TopAbs_FACE) {
					// This should really be the case. This is not asserted.
					const TopoDS_Face& triangle = TopoDS::Face(face_it.Value());
					if (face_area(triangle) > min_face_area) {
						face_list.Append(triangle);
					} else {
						Logger::Message(Logger::LOG_WARNING, "Degenerate face:", (*it));
					}
				}
			}
		} else {
			if (face_area(face) > min_face_area) {
				face_list.Append(face);
			} else {
				Logger::Message(Logger::LOG_WARNING, "Degenerate face:", (*it));
			}
		}
	}

	if (face_list.Extent() == 0) {
		return false;
	}

	if (face_list.Extent() > getValue(GV_MAX_FACES_TO_ORIENT) || !create_solid_from_faces(face_list, shape)) {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);
		
		TopTools_ListIteratorOfListOfShape face_iterator;
		for (face_iterator.Initialize(face_list); face_iterator.More(); face_iterator.Next()) {
			builder.Add(compound, face_iterator.Value());
		}
		shape = compound;
	}

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcMappedItem* l, IfcRepresentationShapeItems& shapes) {
	gp_GTrsf gtrsf;
	IfcSchema::IfcCartesianTransformationOperator* transform = l->MappingTarget();
	if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator3DnonUniform::Class()) ) {
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator3DnonUniform*)transform,gtrsf);
	} else if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator2DnonUniform::Class()) ) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported MappingTarget:", transform);
		return false;
	} else if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator3D::Class()) ) {
		gp_Trsf trsf;
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator3D*)transform,trsf);
		gtrsf = trsf;
	} else if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator2D::Class()) ) {
		gp_Trsf2d trsf_2d;
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator2D*)transform,trsf_2d);
		gtrsf = (gp_Trsf) trsf_2d;
	}
	IfcSchema::IfcRepresentationMap* map = l->MappingSource();
	IfcSchema::IfcAxis2Placement* placement = map->MappingOrigin();
	gp_Trsf trsf;
	if (placement->declaration().is(IfcSchema::IfcAxis2Placement3D::Class())) {
		IfcGeom::Kernel::convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
	} else {
		gp_Trsf2d trsf_2d;
		IfcGeom::Kernel::convert((IfcSchema::IfcAxis2Placement2D*)placement,trsf_2d);
		trsf = trsf_2d;
	}
	gtrsf.Multiply(trsf);

	const IfcGeom::SurfaceStyle* mapped_item_style = get_style(l);
	
	const size_t previous_size = shapes.size();
	bool b = convert_shapes(map->MappedRepresentation(), shapes);
	
	for (size_t i = previous_size; i < shapes.size(); ++ i ) {
		shapes[i].prepend(gtrsf);

		// Apply styles assigned to the mapped item only if on
		// a more granular level no styles have been applied
		if (!shapes[i].hasStyle()) {
			shapes[i].setStyle(mapped_item_style);
		}
	}

	return b;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRepresentation* l, IfcRepresentationShapeItems& shapes) {
	IfcSchema::IfcRepresentationItem::list::ptr items = l->Items();
	bool part_succes = false;
	if ( items->size() ) {
		for ( IfcSchema::IfcRepresentationItem::list::it it = items->begin(); it != items->end(); ++ it ) {
			IfcSchema::IfcRepresentationItem* representation_item = *it;
			if ( shape_type(representation_item) == ST_SHAPELIST ) {
				part_succes |= convert_shapes(*it, shapes);
			} else {
				TopoDS_Shape s;
				if (convert_shape(representation_item,s)) {
					shapes.push_back(IfcRepresentationShapeItem(representation_item->data().id(), s, get_style(representation_item)));
					part_succes |= true;
				}
			}
		}
	}
	return part_succes;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcGeometricSet* l, IfcRepresentationShapeItems& shapes) {
	// @nb the selection is partly duplicated from convert_curves() but it's needed as a
	// geometric set by it's static class definition does not inform us of the type of elements.
	// @todo handle this better so that this doesn't log an error.
	const bool include_curves = getValue(GV_DIMENSIONALITY) != +1;
	const bool include_solids_and_surfaces = getValue(GV_DIMENSIONALITY) != -1;

	IfcEntityList::ptr elements = l->Elements();
	if ( !elements->size() ) return false;
	bool part_succes = false;
	const IfcGeom::SurfaceStyle* parent_style = get_style(l);
	for (IfcEntityList::it it = elements->begin(); it != elements->end(); ++it) {
		IfcSchema::IfcGeometricSetSelect* element = *it;
		TopoDS_Shape s;
		if (shape_type(element) == ST_SHAPELIST) {
			IfcRepresentationShapeItems items;
			if (!(convert_shapes(element, items) && flatten_shape_list(items, s, false))) {
				continue;
			}
		} else if (shape_type(element) == ST_SHAPE && include_solids_and_surfaces) {
			if (!convert_shape(element, s)) {
				continue;
			}
		} else if (shape_type(element) == ST_WIRE && include_curves) {
			TopoDS_Wire w;
			if (!convert_wire(element, w)) {
				continue;
			}
			s = w;
		} else {
			continue;
		}

		part_succes = true;
		const IfcGeom::SurfaceStyle* style = 0;
		if (element->declaration().is(IfcSchema::IfcPoint::Class())) {
			style = get_style((IfcSchema::IfcPoint*) element);
		}
		else if (element->declaration().is(IfcSchema::IfcCurve::Class())) {
			style = get_style((IfcSchema::IfcCurve*) element);
		}
		else if (element->declaration().is(IfcSchema::IfcSurface::Class())) {
			style = get_style((IfcSchema::IfcSurface*) element);
		}
		shapes.push_back(IfcRepresentationShapeItem(l->data().id(), s, style ? style : parent_style));
	}
	return part_succes;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcBlock* l, TopoDS_Shape& shape) {
	const double dx = l->XLength() * getValue(GV_LENGTH_UNIT);
	const double dy = l->YLength() * getValue(GV_LENGTH_UNIT);
	const double dz = l->ZLength() * getValue(GV_LENGTH_UNIT);

	BRepPrimAPI_MakeBox builder(dx, dy, dz);
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);

	// IfcCsgPrimitive3D.Position has unit scale factor
	shape = builder.Solid().Moved(trsf);

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRectangularPyramid* l, TopoDS_Shape& shape) {
	const double dx = l->XLength() * getValue(GV_LENGTH_UNIT);
	const double dy = l->YLength() * getValue(GV_LENGTH_UNIT);
	const double dz = l->Height() * getValue(GV_LENGTH_UNIT);
	
	BRepPrimAPI_MakeWedge builder(dx, dz, dy, dx / 2., dy / 2., dx / 2., dy / 2.);
	
	gp_Trsf trsf1, trsf2;
	trsf2.SetValues(
		1, 0, 0, 0,
		0, 0, 1, 0,
		0, 1, 0, 0
#if OCC_VERSION_HEX < 0x60800
		, Precision::Angular(), Precision::Confusion()
#endif			
	);
	
	IfcGeom::Kernel::convert(l->Position(), trsf1);
	shape = BRepBuilderAPI_Transform(builder.Solid(), trsf1 * trsf2);
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRightCircularCylinder* l, TopoDS_Shape& shape) {
	const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
	const double h = l->Height() * getValue(GV_LENGTH_UNIT);

	BRepPrimAPI_MakeCylinder builder(r, h);
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);
	
	// IfcCsgPrimitive3D.Position has unit scale factor
	shape = builder.Solid().Moved(trsf);

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRightCircularCone* l, TopoDS_Shape& shape) {
	const double r = l->BottomRadius() * getValue(GV_LENGTH_UNIT);
	const double h = l->Height() * getValue(GV_LENGTH_UNIT);

	BRepPrimAPI_MakeCone builder(r, 0., h);
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);

	// IfcCsgPrimitive3D.Position has unit scale factor
	shape = builder.Solid().Moved(trsf);

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSphere* l, TopoDS_Shape& shape) {
	const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
	
	BRepPrimAPI_MakeSphere builder(r);
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);
	
	// IfcCsgPrimitive3D.Position has unit scale factor
	shape = builder.Solid().Moved(trsf);

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCsgSolid* l, TopoDS_Shape& shape) {
	return convert_shape(l->TreeRootExpression(), shape);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCurveBoundedPlane* l, TopoDS_Shape& face) {
	gp_Pln pln;
	if (!IfcGeom::Kernel::convert(l->BasisSurface(), pln)) {
		return false;
	}

	gp_Trsf trsf;
	trsf.SetTransformation(pln.Position(), gp::XOY());
	
	TopoDS_Wire outer;
	if (!convert_wire(l->OuterBoundary(), outer)) {
		return false;
	}
	
	BRepBuilderAPI_MakeFace mf(outer);

	if (!mf.IsDone() || mf.Shape().IsNull()) {
		Logger::Error("Invalid outer boundary:", l->OuterBoundary());
		return false;
	}
	
	IfcSchema::IfcCurve::list::ptr boundaries = l->InnerBoundaries();

	for (IfcSchema::IfcCurve::list::it it = boundaries->begin(); it != boundaries->end(); ++it) {
		TopoDS_Wire inner;
		if (convert_wire(*it, inner)) {
			mf.Add(inner);
		}
	}

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();

	// `trsf` consitutes the placement of the plane and therefore has unit scale factor
	face = TopoDS::Face(sfs.Shape()).Moved(trsf);
	
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRectangularTrimmedSurface* l, TopoDS_Shape& face) {
	if (!l->BasisSurface()->declaration().is(IfcSchema::IfcPlane::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BasisSurface:", l->BasisSurface());
		return false;
	}
	gp_Pln pln;
	IfcGeom::Kernel::convert((IfcSchema::IfcPlane*) l->BasisSurface(), pln);

	BRepBuilderAPI_MakeFace mf(pln, l->U1(), l->U2(), l->V1(), l->V2());

	face = mf.Face();

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSurfaceCurveSweptAreaSolid* l, TopoDS_Shape& shape) {
	gp_Trsf directrix;
	TopoDS_Shape face;
	TopoDS_Face surface_face;
	TopoDS_Wire wire, section;

	const bool is_plane = l->ReferenceSurface()->declaration().is(IfcSchema::IfcPlane::Class());

	if (!is_plane) {
		TopoDS_Shape surface_shell;
		if (!convert_shape(l->ReferenceSurface(), surface_shell)) {
			Logger::Error("Failed to convert reference surface", l);
			return false;
		}
		if (count(surface_shell, TopAbs_FACE) != 1) {
			Logger::Error("Non-continuous reference surface", l);
			return false;
		}
		surface_face = TopoDS::Face(TopExp_Explorer(surface_shell, TopAbs_FACE).Current());
	}
	
	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = l->hasPosition();
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}

	if (!convert_face(l->SweptArea(), face) || 
		!convert_wire(l->Directrix(), wire)    ) {
		return false;
	}

	gp_Pln pln;
	gp_Pnt directrix_origin;
	gp_Vec directrix_tangent;
	bool directrix_on_plane = is_plane;

	if (is_plane) {
		IfcGeom::Kernel::convert((IfcSchema::IfcPlane*) l->ReferenceSurface(), pln);

		// As per Informal propositions 2: The Directrix shall lie on the ReferenceSurface.
		// This is not always the case with the test files in the repository. I am not sure
		// how to deal with this and whether my interpretation of the propositions is
		// correct. However, if it has been asserted that the vertices of the directrix do
		// not conform to the ReferenceSurface, the ReferenceSurface is ignored.
		{
			for (TopExp_Explorer exp(wire, TopAbs_VERTEX); exp.More(); exp.Next()) {
				if (pln.Distance(BRep_Tool::Pnt(TopoDS::Vertex(exp.Current()))) > ALMOST_ZERO) {
					directrix_on_plane = false;
					Logger::Message(Logger::LOG_WARNING, "The Directrix does not lie on the ReferenceSurface", l);
					break;
				}
			}
		}
	}

	{
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		TopoDS_Edge edge = TopoDS::Edge(exp.Current());
		double u0, u1;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u0, u1);
		crv->D1(u0, directrix_origin, directrix_tangent);
	}

	if (is_plane && pln.Axis().Direction().IsNormal(directrix_tangent, Precision::Approximation()) && directrix_on_plane) {
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent, pln.Axis().Direction()), gp::XOY());
	} else if (!is_plane) {
		ShapeAnalysis_Surface sas(BRep_Tool::Surface(surface_face));
		auto pnt2d = sas.ValueOfUV(directrix_origin, getValue(GV_PRECISION) * 10.);
		BRepGProp_Face prop(surface_face);
		gp_Pnt _;
		gp_Vec surface_normal;
		prop.Normal(pnt2d.X(), pnt2d.Y(), _, surface_normal);
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent, surface_normal), gp::XOY());
	} else {
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent), gp::XOY());
	}
	face = BRepBuilderAPI_Transform(face, directrix);

	if (!is_plane) {
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		for (; exp.More(); exp.Next()) {
			ShapeFix_Edge sfe;
			sfe.FixAddPCurve(TopoDS::Edge(exp.Current()), surface_face, false, getValue(GV_PRECISION));
		}
	}

	// NB: Note that StartParam and EndParam param are ignored and the assumption is
	// made that the parametric range over which to be swept matches the IfcCurve in
	// its entirety.
	BRepOffsetAPI_MakePipeShell builder(wire);

	{ TopExp_Explorer exp(face, TopAbs_WIRE);
	section = TopoDS::Wire(exp.Current()); }

	builder.Add(section);
	builder.SetTransitionMode(BRepBuilderAPI_RightCorner);
	if (directrix_on_plane) {
		builder.SetMode(pln.Axis().Direction());
	} else if (!is_plane) {
		builder.SetMode(surface_face);
	}
	builder.Build();
	builder.MakeSolid();
	shape = builder.Shape();

	if (has_position) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}

	return true;
}

namespace {
	bool wire_is_c1_continuous(const TopoDS_Wire& w, double tol) {
		// NB Note that c0 continuity is NOT checked!

		TopTools_IndexedDataMapOfShapeListOfShape map;
		TopExp::MapShapesAndAncestors(w, TopAbs_VERTEX, TopAbs_EDGE, map);
		for (int i = 1; i <= map.Extent(); ++i) {
			const auto& li = map.FindFromIndex(i);
			if (li.Extent() == 2) {
				const TopoDS_Vertex& v = TopoDS::Vertex(map.FindKey(i));

				const TopoDS_Edge& e0 = TopoDS::Edge(li.First());
				const TopoDS_Edge& e1 = TopoDS::Edge(li.Last());

				double u0 = BRep_Tool::Parameter(v, e0);
				double u1 = BRep_Tool::Parameter(v, e1);

				double _, __;
				Handle(Geom_Curve) c0 = BRep_Tool::Curve(e0, _, __);
				Handle(Geom_Curve) c1 = BRep_Tool::Curve(e1, _, __);

				gp_Pnt p;
				gp_Vec v0, v1;
				c0->D1(u0, p, v0);
				c1->D1(u1, p, v1);

				if (1. - std::abs(v0.Normalized().Dot(v1.Normalized())) > tol) {
					return false;
				}
			}
		}
		return true;
	}
}

namespace {
	bool wire_to_ax(const TopoDS_Wire& wire, gp_Ax2& directrix) {
		gp_Pnt directrix_origin;
		gp_Vec directrix_tangent;

		TopoDS_Edge edge;

		// Find first edge
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(wire, v0, v1);
		TopTools_IndexedDataMapOfShapeListOfShape map;
		TopExp::MapShapesAndAncestors(wire, TopAbs_VERTEX, TopAbs_EDGE, map);
		if (v0.IsSame(v1) && map.Contains(v0) && map.FindFromKey(v0).Extent() == 2) {
			// Closed wire, with more than 1 edges
			auto es = map.FindFromKey(v0);
			auto e1 = TopoDS::Edge(es.First());
			auto e2 = TopoDS::Edge(es.Last());
			
			double u0, u1;

			gp_Vec accum;
			
			Handle(Geom_Curve) crv = BRep_Tool::Curve(e1, u0, u1);
			crv->D1(TopExp::FirstVertex(e1).IsSame(v0) ? u0 : u1, directrix_origin, directrix_tangent);

			accum += directrix_tangent;

			crv = BRep_Tool::Curve(e2, u0, u1);
			crv->D1(TopExp::FirstVertex(e2).IsSame(v0) ? u0 : u1, directrix_origin, directrix_tangent);

			accum += directrix_tangent;

			directrix_tangent = accum;

		} else if (map.Contains(v0) && map.FindFromKey(v0).Extent() == 1) {
			edge = TopoDS::Edge(map.FindFromKey(v0).First());

			double u0, u1;
			Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u0, u1);
			crv->D1(u0, directrix_origin, directrix_tangent);
		} else {
			Logger::Error("Unable to locate first edge");
			return false;
		}
		
		directrix = gp_Ax2(directrix_origin, directrix_tangent);

		return true;
	}

	bool is_single_linear_edge(const TopoDS_Wire& wire) {
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		if (!exp.More()) {
			return false;
		}
		TopoDS_Edge e = TopoDS::Edge(exp.Current());
		exp.Next();
		if (exp.More()) {
			return false;
		}
		double u, v;
		Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
		return crv->DynamicType() == STANDARD_TYPE(Geom_Line);
	}

	bool is_single_circular_edge(const TopoDS_Wire& wire) {
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		if (!exp.More()) {
			return false;
		}
		TopoDS_Edge e = TopoDS::Edge(exp.Current());
		exp.Next();
		if (exp.More()) {
			return false;
		}
		double u, v;
		Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
		return crv->DynamicType() == STANDARD_TYPE(Geom_Circle);
	}

	void process_sweep_as_extrusion(const TopoDS_Wire& wire, const TopoDS_Wire& section, TopoDS_Shape& result) {
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		TopoDS_Edge e = TopoDS::Edge(exp.Current());
		double u, v;
		Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
		const auto& dir = Handle(Geom_Line)::DownCast(crv)->Position().Direction();
		// OCCT line is normalized so diff in parametric coords equals length
		const double depth = std::abs(u - v);
		// @todo we could be extruding the wire only when we know this is an intermediate edge.
		TopoDS_Face face = BRepBuilderAPI_MakeFace(section).Face();
		result = BRepPrimAPI_MakePrism(face, depth*dir).Shape();
	}

	void process_sweep_as_revolution(const TopoDS_Wire& wire, const TopoDS_Wire& section, TopoDS_Shape& result) {
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		TopoDS_Edge e = TopoDS::Edge(exp.Current());
		double u, v;
		Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
		auto circ = Handle(Geom_Circle)::DownCast(crv);
		// @todo we could be extruding the wire only when we know this is an intermediate edge.
		const double depth = std::abs(u - v);
		TopoDS_Face face = BRepBuilderAPI_MakeFace(section).Face();
		result = BRepPrimAPI_MakeRevol(face, circ->Axis(), depth).Shape();
	}

	void process_sweep_as_pipe(const TopoDS_Wire& wire, const TopoDS_Wire& section, TopoDS_Shape& result, bool force_transformed=false) {
		// This tolerance is fairly high due to the linear edge substitution for small (or large radii) conical curves.
		const bool is_continuous = wire_is_c1_continuous(wire, 1.e-2);
		BRepOffsetAPI_MakePipeShell builder(wire);
		builder.Add(section);
		builder.SetTransitionMode(is_continuous || force_transformed ? BRepBuilderAPI_Transformed : BRepBuilderAPI_RightCorner);
		try {
			builder.Build();
		} catch (Standard_Failure& e) {
			// We fallback to BRepBuilderAPI_Transformed, but likely with visual artefacts.
			if (!(is_continuous || force_transformed)) {
				return process_sweep_as_pipe(wire, section, result, true);
			} else {
				throw e;
			}
		}
		builder.MakeSolid();
		result = builder.Shape();
	}

	void sort_edges(const TopoDS_Wire& wire, std::vector<TopoDS_Edge>& sorted_edges) {
		TopTools_IndexedDataMapOfShapeListOfShape map;
		TopExp::MapShapesAndAncestors(wire, TopAbs_VERTEX, TopAbs_EDGE, map);

		for (int i = 1; i <= map.Extent(); ++i) {
			if (map.FindFromIndex(i).Extent() > 2) {
				Logger::Warning("Self-intersecting Directrix");
			}
		}

		std::set<TopoDS_TShape*> seen;

		auto num_edges = IfcGeom::Kernel::count(wire, TopAbs_EDGE);

		TopoDS_Vertex v0, v1;
		// @todo this creates the ancestor map twice
		TopExp::Vertices(wire, v0, v1);

		bool ignore_first_equality_because_closed = v0.IsSame(v1);

		// @todo this probably still does not work on a closed wire consisting of one (circular) edge.
		
		while ((int) sorted_edges.size() < num_edges && 
			(!v0.IsSame(v1) || ignore_first_equality_because_closed)) 
		{
			ignore_first_equality_because_closed = false;
			if (!map.Contains(v0)) {
				throw std::runtime_error("Disconnected vertex");
			}
			const TopTools_ListOfShape& es = map.FindFromKey(v0);
			TopoDS_Vertex ve0, ve1;
			TopTools_ListIteratorOfListOfShape it(es);
			bool added = false;
			for (; it.More(); it.Next()) {
				const TopoDS_Edge& e = TopoDS::Edge(it.Value());
				TopExp::Vertices(e, ve0, ve1, true);
				if (ve0.IsSame(v0) && seen.find(&*e.TShape()) == seen.end()) {
					sorted_edges.push_back(e);
					v0 = ve1;
					added = true;
					seen.insert(&*e.TShape());
					break;
				}
			}
			if (!added) {
				throw std::runtime_error("Disconnected edge");
			}
		}
	}


	// #939: a closed loop causes failed triangulation in 7.3 and artefacts
	// in 7.4 so we break up a closed wire into two equal parts.
	void break_closed(const TopoDS_Wire& wire, std::vector<TopoDS_Wire>& wires) {
		std::vector<TopoDS_Edge> sorted_edges;
		sort_edges(wire, sorted_edges);

		if (sorted_edges.size() == 1) {
			wires.push_back(wire);
			return;
		}

		BRep_Builder B;

		wires.emplace_back();
		B.MakeWire(wires.back());

		for (size_t i = 0; i < sorted_edges.size(); ++i) {
			if (i == sorted_edges.size() / 2) {
				wires.emplace_back();
				B.MakeWire(wires.back());
			}

			const auto& e = sorted_edges[i];
			B.Add(wires.back(), e);
		}
	}

	void segment_adjacent_non_linear(const TopoDS_Wire& wire, std::vector<TopoDS_Wire>& wires) {
		std::vector<TopoDS_Edge> sorted_edges;
		sort_edges(wire, sorted_edges);
		
		BRep_Builder B;
		double u, v;

		wires.emplace_back();
		B.MakeWire(wires.back());

		for (int i = 0; i < (int) sorted_edges.size() - 1; ++i) {
			const auto& e = sorted_edges[i];
			Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
			const bool is_linear = crv->DynamicType() == STANDARD_TYPE(Geom_Line);

			const auto& f = sorted_edges[i+1];
			crv = BRep_Tool::Curve(f, u, v);
			const bool next_is_linear = crv->DynamicType() == STANDARD_TYPE(Geom_Line);
			
			B.Add(wires.back(), e);

			if (!is_linear && !next_is_linear) {
				wires.emplace_back();
				B.MakeWire(wires.back());
			}
		}

		if (!sorted_edges.empty()) {
			B.Add(wires.back(), sorted_edges.back());
		}
	}

	// @todo make this generic for other sweeps not just swept disk
	void process_sweep(const TopoDS_Wire& wire, double radius, TopoDS_Shape& result) {
		std::vector<TopoDS_Wire> wires, wires_tmp;
		segment_adjacent_non_linear(wire, wires_tmp);
		for (auto& w : wires_tmp) {
			break_closed(w, wires);
		}
		
		TopoDS_Compound C;
		BRep_Builder B;
		if (wires.size() > 1) {
			B.MakeCompound(C);
		}

		for (auto& w : wires) {
			TopoDS_Shape part;

			gp_Ax2 directrix;
			if (!wire_to_ax(w, directrix)) {
				continue;
			}
			Handle(Geom_Circle) circle = new Geom_Circle(directrix, radius);
			TopoDS_Wire section = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circle));

			if (is_single_circular_edge(w)) {
				process_sweep_as_revolution(w, section, part);
			} else if (is_single_linear_edge(w)) {
				process_sweep_as_extrusion(w, section, part);
			} else {
				process_sweep_as_pipe(w, section, part);
			}
			if (wires.size() > 1) {
				B.Add(C, part);
			} else {
				result = part;
			}
		}

		if (wires.size() > 1) {
			result = C;
		}

		/*
		// Eliminate Swept Surfaces?
		result = ShapeCustom::SweptToElementary(result);

		// Eliminate Trimmed Surfaces?
		ShapeBuild_ReShape sbrs;
		BRep_Builder b;
		TopExp_Explorer exp(result, TopAbs_FACE);
		for (; exp.More(); exp.Next()) {
			const TopoDS_Face& f = TopoDS::Face(exp.Current());
			auto S = BRep_Tool::Surface(f);
			if (S->IsKind(STANDARD_TYPE(Geom_RectangularTrimmedSurface))) {
				auto RTS = Handle(Geom_RectangularTrimmedSurface)::DownCast(S);
				auto B = RTS->BasisSurface();
				TopoDS_Shape newf = f.EmptyCopied();
				// @todo Is it ok to assume no location?
				b.MakeFace(TopoDS::Face(newf), B, BRep_Tool::Tolerance(f));
				sbrs.Replace(f, newf);
			}
		}
		result = sbrs.Apply(result);
		*/
	}
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSweptDiskSolid* l, TopoDS_Shape& shape) {
	TopoDS_Wire wire, section1, section2;

	bool hasInnerRadius = l->hasInnerRadius();

	if (!convert_wire(l->Directrix(), wire)) {
		return false;
	}

	if (count(wire, TopAbs_EDGE) == 1) {
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(wire, v0, v1);
		if (v0.IsSame(v1)) {
			TopExp_Explorer exp(wire, TopAbs_EDGE);
			auto& e = TopoDS::Edge(exp.Current());
			double a, b;
			auto crv = BRep_Tool::Curve(e, a, b);
			if ((crv->DynamicType() == STANDARD_TYPE(Geom_Circle)) ||
				(crv->DynamicType() == STANDARD_TYPE(Geom_Ellipse))) 
			{
				BRepBuilderAPI_MakeEdge me(crv, l->StartParam(), l->EndParam());
				if (me.IsDone()) {
					auto e2 = me.Edge();
					BRep_Builder B;
					wire.Nullify();
					B.MakeWire(wire);
					B.Add(wire, e2);
				}
			}
		}
	}

	// NB: Note that StartParam and EndParam param are ignored and the assumption is
	// made that the parametric range over which to be swept matches the IfcCurve in
	// its entirety.
	
	process_sweep(wire, l->Radius() * getValue(GV_LENGTH_UNIT), shape);

	if (shape.IsNull()) {
		return false;
	}

	double r2 = 0.;

	if (hasInnerRadius) {
		// Subtraction of pipes with small radii is unstable.
		r2 = l->InnerRadius() * getValue(GV_LENGTH_UNIT);
	}

	if (r2 > getValue(GV_PRECISION) * 10.) {
		TopoDS_Shape inner;
		process_sweep(wire, r2, inner);

		bool is_valid = false;

		// Boolean op on the compound of separately processed sweeps
		// is not attempted.
		// @todo iterate over compound subshapes and process boolean
		// separately.
		// @todo don't process as boolean op at all, since we know
		// only the start and end faces intersect and we know they
		// are co-planar and we know they are circles.
		if (shape.ShapeType() != TopAbs_COMPOUND) {
			BRepAlgoAPI_Cut brep_cut(shape, inner);
			if (brep_cut.IsDone()) {
				TopoDS_Shape result = brep_cut;

				ShapeFix_Shape fix(result);
				fix.Perform();
				result = fix.Shape();

				is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
				if (is_valid) {
					shape = result;
				}
			}
		}

		if (!is_valid) {
			Logger::Message(Logger::LOG_WARNING, "Failed to subtract inner radius void for:", l);
		}
	}

	return true;
}

#ifdef SCHEMA_HAS_IfcCylindricalSurface

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCylindricalSurface* l, TopoDS_Shape& face) {
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);
	
	// IfcElementarySurface.Position has unit scale factor
	face = BRepBuilderAPI_MakeFace(new Geom_CylindricalSurface(gp::XOY(), l->Radius() * getValue(GV_LENGTH_UNIT)), getValue(GV_PRECISION)).Face().Moved(trsf);
	return true;
}

#endif

#ifdef SCHEMA_HAS_IfcSphericalSurface

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSphericalSurface* l, TopoDS_Shape& face) {
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(), trsf);

	// IfcElementarySurface.Position has unit scale factor
	face = BRepBuilderAPI_MakeFace(new Geom_SphericalSurface(gp::XOY(), l->Radius() * getValue(GV_LENGTH_UNIT)), getValue(GV_PRECISION)).Face().Moved(trsf);
	return true;
}

#endif

#ifdef SCHEMA_HAS_IfcToroidalSurface

bool IfcGeom::Kernel::convert(const IfcSchema::IfcToroidalSurface* l, TopoDS_Shape& face) {
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(), trsf);

	// IfcElementarySurface.Position has unit scale factor
	face = BRepBuilderAPI_MakeFace(new Geom_ToroidalSurface(gp::XOY(), l->MajorRadius() * getValue(GV_LENGTH_UNIT), l->MinorRadius() * getValue(GV_LENGTH_UNIT)), getValue(GV_PRECISION)).Face().Moved(trsf);
	return true;
}

#endif

#ifdef SCHEMA_HAS_IfcAdvancedBrep

bool IfcGeom::Kernel::convert(const IfcSchema::IfcAdvancedBrep* l, TopoDS_Shape& shape) {
	return convert(l->Outer(), shape);
}

#endif

#ifdef SCHEMA_HAS_IfcTriangulatedFaceSet

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTriangulatedFaceSet* l, TopoDS_Shape& shape) {
	IfcSchema::IfcCartesianPointList3D* point_list = l->Coordinates();
	auto coord_list = point_list->CoordList();
	std::vector<std::vector<int>> indices = l->CoordIndex();

	faceset_helper<
		std::vector<double>,
		std::vector<int>
	> helper(this, coord_list, indices, l->hasClosed() ? l->Closed() : false);

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
	> helper(this, coord_list, indices, pfs->hasClosed() ? pfs->Closed() : false);

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
