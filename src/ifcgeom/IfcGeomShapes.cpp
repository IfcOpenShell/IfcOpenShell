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

#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>

#include <TopLoc_Location.hxx>

#include <BRepCheck_Analyzer.hxx>
#include <BRepClass3d_SolidClassifier.hxx>

#include <Standard_Version.hxx>

#include <TopTools_ListIteratorOfListOfShape.hxx>

#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::Kernel::convert(const IfcSchema::IfcExtrudedAreaSolid* l, TopoDS_Shape& shape) {
	const double height = l->Depth() * getValue(GV_LENGTH_UNIT);
	if (height < getValue(GV_PRECISION)) {
		Logger::Message(Logger::LOG_ERROR, "Non-positive extrusion height encountered for:", l->entity);
		return false;
	}

	TopoDS_Shape face;
	if ( !convert_face(l->SweptArea(),face) ) return false;

	gp_Trsf trsf;
	bool has_position = true;
#ifdef USE_IFC4
	has_position = l->hasPosition();
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}

	gp_Dir dir;
	convert(l->ExtrudedDirection(),dir);

	shape.Nullify();

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

#ifdef USE_IFC4
bool IfcGeom::Kernel::convert(const IfcSchema::IfcExtrudedAreaSolidTapered* l, TopoDS_Shape& shape) {
	const double height = l->Depth() * getValue(GV_LENGTH_UNIT);
	if (height < getValue(GV_PRECISION)) {
		Logger::Message(Logger::LOG_ERROR, "Non-positive extrusion height encountered for:", l->entity);
		return false;
	}

	TopoDS_Shape face1, face2;
	if (!convert_face(l->SweptArea(), face1)) return false;
	if (!convert_face(l->EndSweptArea(), face2)) return false;

	gp_Trsf trsf;
	bool has_position = true;
#ifdef USE_IFC4
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

		BRepOffsetAPI_Sewing sewer;
		sewer.SetTolerance(getValue(GV_PRECISION));
		sewer.SetMaxTolerance(getValue(GV_PRECISION));
		sewer.SetMinTolerance(getValue(GV_PRECISION));

		sewer.Add(result);
		sewer.Add(BRepBuilderAPI_MakeFace(w1).Face());
		sewer.Add(BRepBuilderAPI_MakeFace(w2).Face().Moved(end_profile));

		sewer.Perform();

		result = sewer.SewedShape();

		if (shell.IsNull()) {
			shell = result;
		} else if (l->SweptArea()->is(IfcSchema::Type::IfcCircleHollowProfileDef) ||
			l->SweptArea()->is(IfcSchema::Type::IfcRectangleHollowProfileDef))
		{
			/// @todo a bit of of a hack, should be sufficient
			shell = BRepAlgoAPI_Cut(shell, result).Shape();
			break;
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
		Logger::Message(Logger::LOG_ERROR, "Inconsistent profiles encountered for:", l->entity);
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
#ifdef USE_IFC4
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
#ifdef USE_IFC4
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

	TopoDS_Face face;
	if ( ! convert_face(l->SweptArea(),face) ) return false;

	gp_Ax1 ax1;
	IfcGeom::Kernel::convert(l->Axis(), ax1);

	gp_Trsf trsf;
	bool has_position = true;
#ifdef USE_IFC4
	has_position = l->hasPosition();
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
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
		if (l->is(IfcSchema::Type::IfcFacetedBrepWithVoids)) {
			voids = l->as<IfcSchema::IfcFacetedBrepWithVoids>()->Voids();
		}
#ifdef USE_IFC4
		if (l->is(IfcSchema::Type::IfcAdvancedBrepWithVoids)) {
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

		shape.push_back(IfcRepresentationShapeItem(s, indiv_style ? indiv_style : collective_style));
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
			shapes.push_back(IfcRepresentationShapeItem(s, shell_style ? shell_style : collective_style));
			part_success |= true;
		}
	}
	return part_success;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcHalfSpaceSolid* l, TopoDS_Shape& shape) {
	IfcSchema::IfcSurface* surface = l->BaseSurface();
	if ( ! surface->is(IfcSchema::Type::IfcPlane) ) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BaseSurface:", surface->entity);
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
			Logger::Message(Logger::LOG_ERROR, "Not enough points retained from:", l->PolygonalBoundary()->entity);
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
		if ((*it)->is(IfcSchema::Type::IfcRepresentationItem)) {
			shell_style = get_style((IfcSchema::IfcRepresentationItem*)*it);
		}
		if (convert_shape(*it,s)) {
			shapes.push_back(IfcRepresentationShapeItem(s, shell_style ? shell_style : collective_style));
		}
	}
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcBooleanResult* l, TopoDS_Shape& shape) {

	TopoDS_Shape s1, s2;
	IfcRepresentationShapeItems items1, items2;
	TopoDS_Wire boundary_wire;
	IfcSchema::IfcBooleanOperand* operand1 = l->FirstOperand();
	IfcSchema::IfcBooleanOperand* operand2 = l->SecondOperand();
	bool is_halfspace = operand2->is(IfcSchema::Type::IfcHalfSpaceSolid);

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
		Logger::Message(Logger::LOG_ERROR, "Invalid representation item for boolean operation", operand1->entity);
		return false;
	}

	const double first_operand_volume = shape_volume(s1);
	if ( first_operand_volume <= ALMOST_ZERO )
		Logger::Message(Logger::LOG_WARNING,"Empty solid for:",l->FirstOperand()->entity);

	bool shape2_processed = false;
	if ( shape_type(operand2) == ST_SHAPELIST ) {
		shape2_processed = convert_shapes(operand2, items2) && flatten_shape_list(items2, s2, true);
	} else if ( shape_type(operand2) == ST_SHAPE ) {
		shape2_processed = convert_shape(operand2,s2);
		if (shape2_processed && !is_halfspace) {
			TopoDS_Solid temp_solid;
			s2 = ensure_fit_for_subtraction(s2, temp_solid);
		}
	} else {
		Logger::Message(Logger::LOG_ERROR, "Invalid representation item for boolean operation", operand2->entity);
	}

	if (!shape2_processed) {
		shape = s1;
		Logger::Message(Logger::LOG_ERROR,"Failed to convert SecondOperand of:",l->entity);
		return true;
	}

	if (!is_halfspace) {
		const double second_operand_volume = shape_volume(s2);
		if ( second_operand_volume <= ALMOST_ZERO )
			Logger::Message(Logger::LOG_WARNING,"Empty solid for:",operand2->entity);
	}

	const IfcSchema::IfcBooleanOperator::IfcBooleanOperator op = l->Operator();

	/*
	// TK: A little debugging trick to output both operands for visual inspection
	
	BRep_Builder builder;
	TopoDS_Compound compound;
	builder.MakeCompound(compound);
	builder.Add(compound, s1);
	builder.Add(compound, s2);
	shape = compound;
	return true;
	*/

	BOPAlgo_Operation occ_op;
	if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {
		occ_op = BOPAlgo_CUT;
	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_INTERSECTION) {
		occ_op = BOPAlgo_COMMON;
	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION) {
		occ_op = BOPAlgo_FUSE;
	} else {
		return false;
	}

	bool valid_result = boolean_operation(s1, s2, occ_op, shape);

	if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {
		// In case of a subtraction, a check on volume is performed.
		if (valid_result) {
			const double volume_after_subtraction = shape_volume(shape);
			if ( ALMOST_THE_SAME(first_operand_volume,volume_after_subtraction) )
				Logger::Message(Logger::LOG_WARNING,"Subtraction yields unchanged volume:",l->entity);
		} else {
			Logger::Message(Logger::LOG_ERROR,"Failed to process subtraction:",l->entity);
			shape = s1;
		}
		// NB: After issuing error the first operand is returned!
		return true;
	} else {
		return valid_result;
	}
	return false;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcConnectedFaceSet* l, TopoDS_Shape& shape) {
	IfcSchema::IfcFace::list::ptr faces = l->CfsFaces();

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
			Logger::Message(Logger::LOG_WARNING, "Failed to convert face:", (*it)->entity);
			continue;
		}

		if (face_area(face) > getValue(GV_MINIMAL_FACE_AREA)) {
			face_list.Append(face);
		} else {
			Logger::Message(Logger::LOG_WARNING, "Invalid face:", (*it)->entity);
		}
	}

	if (face_list.Extent() == 0) {
		return false;
	}

	if (face_list.Extent() > getValue(GV_MAX_FACES_TO_SEW) || !create_solid_from_faces(face_list, shape)) {
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
	if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator3DnonUniform) ) {
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator3DnonUniform*)transform,gtrsf);
	} else if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator2DnonUniform) ) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported MappingTarget:", transform->entity);
		return false;
	} else if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator3D) ) {
		gp_Trsf trsf;
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator3D*)transform,trsf);
		gtrsf = trsf;
	} else if ( transform->is(IfcSchema::Type::IfcCartesianTransformationOperator2D) ) {
		gp_Trsf2d trsf_2d;
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator2D*)transform,trsf_2d);
		gtrsf = (gp_Trsf) trsf_2d;
	}
	IfcSchema::IfcRepresentationMap* map = l->MappingSource();
	IfcSchema::IfcAxis2Placement* placement = map->MappingOrigin();
	gp_Trsf trsf;
	if (placement->is(IfcSchema::Type::IfcAxis2Placement3D)) {
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
					shapes.push_back(IfcRepresentationShapeItem(s, get_style(representation_item)));
					part_succes |= true;
				}
			}
		}
	}
	return part_succes;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcGeometricSet* l, IfcRepresentationShapeItems& shapes) {
	IfcEntityList::ptr elements = l->Elements();
	if ( !elements->size() ) return false;
	bool part_succes = false;
	const IfcGeom::SurfaceStyle* parent_style = get_style(l);
	for ( IfcEntityList::it it = elements->begin(); it != elements->end(); ++ it ) {
		IfcSchema::IfcGeometricSetSelect* element = *it;
		TopoDS_Shape s;
		if (convert_shape(element, s)) {
			part_succes = true;
			const IfcGeom::SurfaceStyle* style = 0;
			if (element->is(IfcSchema::Type::IfcPoint)) {
				style = get_style((IfcSchema::IfcPoint*) element);
			} else if (element->is(IfcSchema::Type::IfcCurve)) {
				style = get_style((IfcSchema::IfcCurve*) element);
			} else if (element->is(IfcSchema::Type::IfcSurface)) {
				style = get_style((IfcSchema::IfcSurface*) element);
			}
			shapes.push_back(IfcRepresentationShapeItem(s, style ? style : parent_style));
		}
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
	IfcGeom::Kernel::convert(l->BasisSurface(), pln);

	gp_Trsf trsf;
	trsf.SetTransformation(pln.Position(), gp::XOY());
	
	TopoDS_Wire outer;
	convert_wire(l->OuterBoundary(), outer);
	
	BRepBuilderAPI_MakeFace mf (outer);
	mf.Add(outer);

	IfcSchema::IfcCurve::list::ptr boundaries = l->InnerBoundaries();

	for (IfcSchema::IfcCurve::list::it it = boundaries->begin(); it != boundaries->end(); ++it) {
		TopoDS_Wire inner;
		convert_wire(*it, inner);
		
		mf.Add(inner);
	}

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();

	// `trsf` consitutes the placement of the plane and therefore has unit scale factor
	face = TopoDS::Face(sfs.Shape()).Moved(trsf);
	
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRectangularTrimmedSurface* l, TopoDS_Shape& face) {
	if (!l->BasisSurface()->is(IfcSchema::Type::IfcPlane)) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BasisSurface:", l->BasisSurface()->entity);
		return false;
	}
	gp_Pln pln;
	IfcGeom::Kernel::convert((IfcSchema::IfcPlane*) l->BasisSurface(), pln);

	BRepBuilderAPI_MakeFace mf(pln, l->U1(), l->U2(), l->V1(), l->V2());

	face = mf.Face();

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSurfaceCurveSweptAreaSolid* l, TopoDS_Shape& shape) {
	gp_Trsf directrix, position;
	TopoDS_Shape face;
	TopoDS_Wire wire, section;

	if (!l->ReferenceSurface()->is(IfcSchema::Type::IfcPlane)) {
		Logger::Message(Logger::LOG_WARNING, "Reference surface not supported", l->ReferenceSurface()->entity);
		return false;
	}
	
	gp_Trsf trsf;
	bool has_position = true;
#ifdef USE_IFC4
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
	bool directrix_on_plane = true;
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
				Logger::Message(Logger::LOG_WARNING, "The Directrix does not lie on the ReferenceSurface", l->entity);
				break;
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

	if (pln.Axis().Direction().IsNormal(directrix_tangent, Precision::Approximation()) && directrix_on_plane) {
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent, pln.Axis().Direction()), gp::XOY());
	} else {
		directrix.SetTransformation(gp_Ax3(directrix_origin, directrix_tangent), gp::XOY());
	}
	face = BRepBuilderAPI_Transform(face, directrix);

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
	}
	builder.Build();
	builder.MakeSolid();
	shape = builder.Shape();

	if (has_position) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(position);
	}

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSweptDiskSolid* l, TopoDS_Shape& shape) {
	TopoDS_Wire wire, section1, section2;

	bool hasInnerRadius = l->hasInnerRadius();

	if (!convert_wire(l->Directrix(), wire)) {
		return false;
	}
	
	gp_Ax2 directrix;
	{
		gp_Pnt directrix_origin;
		gp_Vec directrix_tangent;
		TopExp_Explorer exp(wire, TopAbs_EDGE);
		TopoDS_Edge edge = TopoDS::Edge(exp.Current());
		double u0, u1;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u0, u1);
		crv->D1(u0, directrix_origin, directrix_tangent);
		directrix = gp_Ax2(directrix_origin, directrix_tangent);
	}

	const double r1 = l->Radius() * getValue(GV_LENGTH_UNIT);
	Handle(Geom_Circle) circle = new Geom_Circle(directrix, r1);
	section1 = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circle));

	if (hasInnerRadius) {
		const double r2 = l->InnerRadius() * getValue(GV_LENGTH_UNIT);
		if (r2 < getValue(GV_PRECISION)) {
			// Subtraction of pipes with small radii is unstable.
			hasInnerRadius = false;
		} else {
			Handle(Geom_Circle) circle2 = new Geom_Circle(directrix, r2);
			section2 = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circle2));
		}
	}

	// NB: Note that StartParam and EndParam param are ignored and the assumption is
	// made that the parametric range over which to be swept matches the IfcCurve in
	// its entirety.
	// NB2: Contrary to IfcSurfaceCurveSweptAreaSolid the transition mode has been
	// set to create round corners as this has proven to work better with the types
	// of directrices encountered, which do not necessarily conform to a surface.
	{ BRepOffsetAPI_MakePipeShell builder(wire);
	builder.Add(section1);
	builder.SetTransitionMode(BRepBuilderAPI_RoundCorner);
	builder.Build();
	builder.MakeSolid();
	shape = builder.Shape(); }

	if (hasInnerRadius) {
		BRepOffsetAPI_MakePipeShell builder(wire);
		builder.Add(section2);
		builder.SetTransitionMode(BRepBuilderAPI_RoundCorner);
		builder.Build();
		builder.MakeSolid();
		TopoDS_Shape inner = builder.Shape();

		BRepAlgoAPI_Cut brep_cut(shape, inner);
		bool is_valid = false;
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

		if (!is_valid) {
			Logger::Message(Logger::LOG_WARNING, "Failed to subtract inner radius void for:", l->entity);
		}
	}

	return true;
}

#ifdef USE_IFC4

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCylindricalSurface* l, TopoDS_Shape& face) {
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);
	
	// IfcElementarySurface.Position has unit scale factor
#if OCC_VERSION_HEX < 0x60502
	face = BRepBuilderAPI_MakeFace(new Geom_CylindricalSurface(gp::XOY(), l->Radius())).Face().Moved(trsf);
#else
	face = BRepBuilderAPI_MakeFace(new Geom_CylindricalSurface(gp::XOY(), l->Radius()), getValue(GV_PRECISION)).Face().Moved(trsf);
#endif
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcAdvancedBrep* l, TopoDS_Shape& shape) {
	return convert(l->Outer(), shape);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTriangulatedFaceSet* l, TopoDS_Shape& shape) {
	IfcSchema::IfcCartesianPointList3D* point_list = l->Coordinates();
	const std::vector< std::vector<double> > coordinates = point_list->CoordList();
	std::vector<gp_Pnt> points;
	points.reserve(coordinates.size());
	for (std::vector< std::vector<double> >::const_iterator it = coordinates.begin(); it != coordinates.end(); ++it) {
		const std::vector<double>& coords = *it;
		if (coords.size() != 3) {
			Logger::Message(Logger::LOG_ERROR, "Invalid dimensions encountered on Coordinates", l->entity);
			return false;
		}
		points.push_back(gp_Pnt(coords[0] * getValue(GV_LENGTH_UNIT),
		                        coords[1] * getValue(GV_LENGTH_UNIT),
		                        coords[2] * getValue(GV_LENGTH_UNIT)));
	}

	std::vector< std::vector<int> > indices = l->CoordIndex();
	
	std::vector<TopoDS_Face> faces;
	faces.reserve(indices.size());

	for(std::vector< std::vector<int> >::const_iterator it = indices.begin(); it != indices.end(); ++ it) {
		const std::vector<int>& tri = *it;
		if (tri.size() != 3) {
			Logger::Message(Logger::LOG_ERROR, "Invalid dimensions encountered on CoordIndex", l->entity);
			return false;
		}

		const int min_index = *std::min_element(tri.begin(), tri.end());
		const int max_index = *std::max_element(tri.begin(), tri.end());

		if (min_index < 1 || max_index > (int) points.size()) {
			Logger::Message(Logger::LOG_ERROR, "Contents of CoordIndex out of bounds", l->entity);
			return false;
		}

		const gp_Pnt& a = points[tri[0] - 1]; // account for zero- vs
		const gp_Pnt& b = points[tri[1] - 1]; // one-based indices in
		const gp_Pnt& c = points[tri[2] - 1]; // c++ and express

		TopoDS_Wire wire = BRepBuilderAPI_MakePolygon(a, b, c, true).Wire();
		TopoDS_Face face = BRepBuilderAPI_MakeFace(wire).Face();

		TopoDS_Iterator face_it(face, false);
		const TopoDS_Wire& w = TopoDS::Wire(face_it.Value());
		const bool reversed = w.Orientation() == TopAbs_REVERSED;
		if (reversed) {
			face.Reverse();
		}

		if (face_area(face) > getValue(GV_MINIMAL_FACE_AREA)) {
			faces.push_back(face);
		}
	}

	if (faces.empty()) return false;
	
	bool valid_shell = false;

	if (faces.size() < getValue(GV_MAX_FACES_TO_SEW)) {
		BRepOffsetAPI_Sewing builder;
		builder.SetTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
		builder.SetMaxTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
		builder.SetMinTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
		
		for (std::vector<TopoDS_Face>::const_iterator it = faces.begin(); it != faces.end(); ++it) {
			builder.Add(*it);
		}

		try {
			builder.Perform();
			shape = builder.SewedShape();
			valid_shell = BRepCheck_Analyzer(shape).IsValid();
		} catch(...) {}

		if (valid_shell) {
			try {
				ShapeFix_Solid solid;
				solid.LimitTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
				TopoDS_Solid solid_shape = solid.SolidFromShell(TopoDS::Shell(shape));
				if (!solid_shape.IsNull()) {
					try {
						BRepClass3d_SolidClassifier classifier(solid_shape);
						shape = solid_shape;
					} catch (...) {}
				}
			} catch(...) {}
		} else {
			Logger::Message(Logger::LOG_WARNING, "Failed to sew faceset:", l->entity);
		}
	}

	if (!valid_shell) {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);
		
		for (std::vector<TopoDS_Face>::const_iterator it = faces.begin(); it != faces.end(); ++it) {
			builder.Add(compound, *it);
		}

		shape = compound;
	}

	return true;
}

#endif
