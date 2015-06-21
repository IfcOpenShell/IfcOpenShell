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

#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::Kernel::convert(const IfcSchema::IfcExtrudedAreaSolid* l, TopoDS_Shape& shape) {
	TopoDS_Shape face;
	if ( !convert_face(l->SweptArea(),face) ) return false;

	const double height = l->Depth() * getValue(GV_LENGTH_UNIT);
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);

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

	shape.Move(trsf);
	return ! shape.IsNull();
}

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
	IfcGeom::Kernel::convert(l->Position(),trsf);

	gp_Dir dir;
	convert(l->ExtrudedDirection(),dir);

	shape = BRepPrimAPI_MakePrism(wire, height*dir);
	shape.Move(trsf);
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
	IfcGeom::Kernel::convert(l->Position(),trsf);
	
	shape = BRepPrimAPI_MakeRevol(wire, ax1);

	shape.Move(trsf);
	return !shape.IsNull();
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRevolvedAreaSolid* l, TopoDS_Shape& shape) {
	const double ang = l->Angle() * getValue(GV_PLANEANGLE_UNIT);

	TopoDS_Face face;
	if ( ! convert_face(l->SweptArea(),face) ) return false;

	gp_Ax1 ax1;
	IfcGeom::Kernel::convert(l->Axis(), ax1);

	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);

	if (ang >= M_PI * 2. - ALMOST_ZERO) {
		shape = BRepPrimAPI_MakeRevol(face, ax1);
	} else {
		shape = BRepPrimAPI_MakeRevol(face, ax1, ang);
	}

	shape.Move(trsf);
	return !shape.IsNull();
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcFacetedBrep* l, IfcRepresentationShapeItems& shape) {
	TopoDS_Shape s;
	const SurfaceStyle* collective_style = get_style(l);
	if (convert_shape(l->Outer(),s) ) {
		const SurfaceStyle* indiv_style = get_style(l->Outer());
		shape.push_back(IfcRepresentationShapeItem(s, indiv_style ? indiv_style : collective_style));
		return true;
	}
	return false;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcFaceBasedSurfaceModel* l, IfcRepresentationShapeItems& shapes) {
	IfcSchema::IfcConnectedFaceSet::list::ptr facesets = l->FbsmFaces();
	const SurfaceStyle* collective_style = get_style(l);
	for( IfcSchema::IfcConnectedFaceSet::list::it it = facesets->begin(); it != facesets->end(); ++ it ) {
		TopoDS_Shape s;
		const SurfaceStyle* shell_style = get_style(*it);
		if (convert_shape(*it,s)) {
			shapes.push_back(IfcRepresentationShapeItem(s, shell_style ? shell_style : collective_style));
		}
	}
	return true;
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
	convert(l->Position(),trsf);
	TopoDS_Shape prism = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire),gp_Vec(0,0,200));
	gp_Trsf down; down.SetTranslation(gp_Vec(0,0,-100.0));
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

	if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {

		bool valid_cut = false;
		BRepAlgoAPI_Cut brep_cut(s1,s2);
		if ( brep_cut.IsDone() ) {
			TopoDS_Shape result = brep_cut;

			ShapeFix_Shape fix(result);
			try {
				fix.Perform();
				result = fix.Shape();
			} catch (...) {
				Logger::Message(Logger::LOG_WARNING, "Shape healing failed on boolean result", l->entity);
			}
		
			bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
			if ( is_valid ) {
				shape = result;
				valid_cut = true;
			} 
		}

		if ( valid_cut ) {
			const double volume_after_subtraction = shape_volume(shape);
			if ( ALMOST_THE_SAME(first_operand_volume,volume_after_subtraction) )
				Logger::Message(Logger::LOG_WARNING,"Subtraction yields unchanged volume:",l->entity);
		} else {
			Logger::Message(Logger::LOG_ERROR,"Failed to process subtraction:",l->entity);
			shape = s1;
		}

		return true;

	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION) {

		BRepAlgoAPI_Fuse brep_fuse(s1,s2);
		if ( brep_fuse.IsDone() ) {
			TopoDS_Shape result = brep_fuse;

			ShapeFix_Shape fix(result);
			fix.Perform();
			result = fix.Shape();
		
			bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
			if ( is_valid ) {
				shape = result;
				return true;
			} 
		}	

	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_INTERSECTION) {

		BRepAlgoAPI_Common brep_common(s1,s2);
		if ( brep_common.IsDone() ) {
			TopoDS_Shape result = brep_common;

			ShapeFix_Shape fix(result);
			fix.Perform();
			result = fix.Shape();
		
			bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
			if ( is_valid ) {
				shape = result;
				return true;
			} 
		}

	}
	return false;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcConnectedFaceSet* l, TopoDS_Shape& shape) {
	IfcSchema::IfcFace::list::ptr faces = l->CfsFaces();
	bool facesAdded = false;
	const unsigned int num_faces = faces->size();
	bool valid_shell = false;
	if ( num_faces < getValue(GV_MAX_FACES_TO_SEW) ) {
		BRepOffsetAPI_Sewing builder;
		builder.SetTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
		builder.SetMaxTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
		builder.SetMinTolerance(getValue(GV_POINT_EQUALITY_TOLERANCE));
		for( IfcSchema::IfcFace::list::it it = faces->begin(); it != faces->end(); ++ it ) {
			TopoDS_Face face;
			bool converted_face = false;
			try {
				converted_face = convert_face(*it,face);
			} catch (...) {}
			if ( converted_face && face_area(face) > getValue(GV_MINIMAL_FACE_AREA) ) {
				builder.Add(face);
				facesAdded = true;
			} else {
				Logger::Message(Logger::LOG_WARNING,"Invalid face:",(*it)->entity);
			}
		}
		if ( ! facesAdded ) return false;
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
			Logger::Message(Logger::LOG_WARNING,"Failed to sew faceset:",l->entity);
		}
	}
	if (!valid_shell) {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);
		for( IfcSchema::IfcFace::list::it it = faces->begin(); it != faces->end(); ++ it ) {
			TopoDS_Face face;
			bool converted_face = false;
			try {
				converted_face = convert_face(*it,face);
			} catch (...) {}
			if ( converted_face && face_area(face) > getValue(GV_MINIMAL_FACE_AREA) ) {
				builder.Add(compound,face);
				facesAdded = true;
			} else {
				Logger::Message(Logger::LOG_WARNING,"Invalid face:",(*it)->entity);
			}
		}
		if ( ! facesAdded ) return false;
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
	const unsigned int previous_size = (const unsigned int) shapes.size();
	bool b = convert_shapes(map->MappedRepresentation(),shapes);
	for ( unsigned int i = previous_size; i < shapes.size(); ++ i ) {
		shapes[i].append(gtrsf);
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
	shape = builder.Solid().Moved(trsf);
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRightCircularCone* l, TopoDS_Shape& shape) {
	const double r = l->BottomRadius() * getValue(GV_LENGTH_UNIT);
	const double h = l->Height() * getValue(GV_LENGTH_UNIT);

	BRepPrimAPI_MakeCone builder(r, 0., h);
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);
	shape = builder.Solid().Moved(trsf);
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSphere* l, TopoDS_Shape& shape) {
	const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
	
	BRepPrimAPI_MakeSphere builder(r);
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);
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

	IfcSchema::IfcCurve::list::ptr inner = l->InnerBoundaries();

	for (IfcSchema::IfcCurve::list::it it = inner->begin(); it != inner->end(); ++it) {
		TopoDS_Wire inner;
		convert_wire(*it, inner);
		
		mf.Add(inner);
	}

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();
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
	
	if (!IfcGeom::Kernel::convert(l->Position(), position)   || 
		!convert_face(l->SweptArea(), face) || 
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
	shape.Move(position);

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
			Handle(Geom_Circle) circle = new Geom_Circle(directrix, r2);
			section2 = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circle));
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
	
	face = BRepBuilderAPI_MakeFace(new Geom_CylindricalSurface(gp::XOY(), l->Radius()), getValue(GV_PRECISION)).Face().Moved(trsf);
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

		if (min_index < 1 || max_index > points.size()) {
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
	
	const unsigned int num_faces = indices.size();
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
