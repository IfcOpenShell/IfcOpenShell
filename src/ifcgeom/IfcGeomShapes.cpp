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

#include <TopLoc_Location.hxx>

#include <BRepCheck_Analyzer.hxx>
#include <BRepAlgoAPI_Common.hxx>

#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::convert(const Ifc2x3::IfcExtrudedAreaSolid::ptr l, TopoDS_Shape& shape) {
	TopoDS_Face face;
	if ( ! IfcGeom::convert_face(l->SweptArea(),face) ) return false;
	const double height = l->Depth() * IfcGeom::GetValue(GV_LENGTH_UNIT);
	gp_Trsf trsf;
	IfcGeom::convert(l->Position(),trsf);

	gp_Dir dir;
	convert(l->ExtrudedDirection(),dir);

	shape = BRepPrimAPI_MakePrism(face,height*dir);
	shape.Move(trsf);
	return ! shape.IsNull();
}
bool IfcGeom::convert(const Ifc2x3::IfcFacetedBrep::ptr l, IfcRepresentationShapeItems& shape) {
	TopoDS_Shape s;
	if (IfcGeom::convert_shape(l->Outer(),s) ) {
		shape.push_back(IfcRepresentationShapeItem(s, get_style(l->Outer())));
		return true;
	}
	return false;
}
bool IfcGeom::convert(const Ifc2x3::IfcFaceBasedSurfaceModel::ptr l, IfcRepresentationShapeItems& shapes) {
	Ifc2x3::IfcConnectedFaceSet::list facesets = l->FbsmFaces();
	const SurfaceStyle* collective_style = get_style(l);
	for( Ifc2x3::IfcConnectedFaceSet::it it = facesets->begin(); it != facesets->end(); ++ it ) {
		TopoDS_Shape s;
		const SurfaceStyle* shell_style = get_style(*it);
		if (IfcGeom::convert_shape(*it,s)) {
			shapes.push_back(IfcRepresentationShapeItem(s, shell_style ? shell_style : collective_style));
		}
	}
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcHalfSpaceSolid::ptr l, TopoDS_Shape& shape) {
	Ifc2x3::IfcSurface::ptr surface = l->BaseSurface();
	if ( ! surface->is(Ifc2x3::Type::IfcPlane) ) {
		// Not implemented
		return false;
	}
	gp_Pln pln;
	IfcGeom::convert(reinterpret_pointer_cast<Ifc2x3::IfcSurface,Ifc2x3::IfcPlane>(surface),pln);
	const gp_Pnt pnt = pln.Location().Translated( l->AgreementFlag() ? -pln.Axis().Direction() : pln.Axis().Direction());
	shape = BRepPrimAPI_MakeHalfSpace(BRepBuilderAPI_MakeFace(pln),pnt).Solid();
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcPolygonalBoundedHalfSpace::ptr l, TopoDS_Shape& shape) {
	TopoDS_Shape halfspace;
	if ( ! IfcGeom::convert(reinterpret_pointer_cast<Ifc2x3::IfcPolygonalBoundedHalfSpace,Ifc2x3::IfcHalfSpaceSolid>(l),halfspace) ) return false;	
	TopoDS_Wire wire;
	if ( ! IfcGeom::convert_wire(l->PolygonalBoundary(),wire) || ! wire.Closed() ) return false;	
	gp_Trsf trsf;
	convert(l->Position(),trsf);
	TopoDS_Shape prism = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire),gp_Vec(0,0,200));
	gp_Trsf down; down.SetTranslation(gp_Vec(0,0,-100.0));
	prism.Move(down*trsf);
	shape = BRepAlgoAPI_Common(halfspace,prism);
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcShellBasedSurfaceModel::ptr l, IfcRepresentationShapeItems& shapes) {
	IfcUtil::IfcAbstractSelect::list shells = l->SbsmBoundary();
	const SurfaceStyle* collective_style = get_style(l);
	for( IfcUtil::IfcAbstractSelect::it it = shells->begin(); it != shells->end(); ++ it ) {
		TopoDS_Shape s;
		const SurfaceStyle* shell_style = 0;
		if ((*it)->is(Ifc2x3::Type::IfcRepresentationItem)) {
			shell_style = get_style((Ifc2x3::IfcRepresentationItem*)*it);
		}
		if (IfcGeom::convert_shape(*it,s)) {
			shapes.push_back(IfcRepresentationShapeItem(s, shell_style ? shell_style : collective_style));
		}
	}
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcBooleanClippingResult::ptr l, TopoDS_Shape& shape) {
	TopoDS_Shape s1, s2;
	TopoDS_Wire boundary_wire;
	Ifc2x3::IfcBooleanOperand operand2 = l->SecondOperand();
	bool is_halfspace = operand2->is(Ifc2x3::Type::IfcHalfSpaceSolid);
	bool is_bounded = operand2->is(Ifc2x3::Type::IfcPolygonalBoundedHalfSpace);
	bool is_convex_bound = false;

	if ( ! IfcGeom::convert_shape(l->FirstOperand(),s1) )
		return false;

	const double first_operand_volume = shape_volume(s1);
	if ( first_operand_volume <= ALMOST_ZERO )
		Logger::Message(Logger::LOG_WARNING,"Empty solid for:",l->FirstOperand()->entity);

	if ( !IfcGeom::convert_shape(l->SecondOperand(),s2) ) {
		shape = s1;
		Logger::Message(Logger::LOG_ERROR,"Failed to convert SecondOperand of:",l->entity);
		return true;
	}

	if ( is_bounded ) {
		Ifc2x3::IfcPolygonalBoundedHalfSpace::ptr ifc_bounded_halfspace = 
			(Ifc2x3::IfcPolygonalBoundedHalfSpace::ptr) operand2;		
		IfcGeom::convert_wire(ifc_bounded_halfspace->PolygonalBoundary(),boundary_wire);
		is_convex_bound = is_convex(boundary_wire);
	}

	if ( ! is_halfspace ) {
		const double second_operand_volume = shape_volume(s2);
		if ( second_operand_volume <= ALMOST_ZERO )
			Logger::Message(Logger::LOG_WARNING,"Empty solid for:",operand2->entity);
	}

	bool valid_cut = false;
	if ( !is_bounded || !is_convex_bound ) {
		BRepAlgoAPI_Cut brep_cut(s1,s2);
		if ( brep_cut.IsDone() ) {
			TopoDS_Shape result = brep_cut;
			bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
			if ( is_valid ) {
				shape = result;
				valid_cut = true;
			} 
		}
		if ( !valid_cut && !is_bounded ) {
			Ifc2x3::IfcHalfSpaceSolid::ptr ifc_halfspace = (Ifc2x3::IfcHalfSpaceSolid::ptr) operand2;
			Ifc2x3::IfcSurface::ptr surface = ifc_halfspace->BaseSurface();
			if ( surface->is(Ifc2x3::Type::IfcPlane) ) {
				gp_Pln pln;
				IfcGeom::convert(reinterpret_pointer_cast<Ifc2x3::IfcSurface,Ifc2x3::IfcPlane>(surface),pln);
				gp_Pnt pnt = pln.Location();
				bool reverse = ifc_halfspace->AgreementFlag();
				gp_Vec direction = pln.Axis().Direction();
				if ( reverse ) direction *= -1;
				pnt.Translate(direction);
				pln.SetLocation(pln.Location().Translated(direction * -0.0001));
				TopoDS_Shape halfspace = BRepPrimAPI_MakeHalfSpace(BRepBuilderAPI_MakeFace(pln),pnt).Solid();

				BRepAlgoAPI_Cut brep_cut(s1,halfspace);
				if ( brep_cut.IsDone() ) {
					TopoDS_Shape result = brep_cut;
					bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
					if ( is_valid ) {
						shape = result;
						valid_cut = true;
						Logger::Message(Logger::LOG_WARNING,"Slightly nudged the SecondOperand of:",l->entity);
					} 
				}
			}
		}
	} else {
		Ifc2x3::IfcPolygonalBoundedHalfSpace::ptr ifc_bounded_halfspace = 
			(Ifc2x3::IfcPolygonalBoundedHalfSpace::ptr) operand2;
		gp_Trsf trsf;
		convert(ifc_bounded_halfspace->Position(),trsf);
		TopoDS_Shape face = BRepBuilderAPI_MakeFace(boundary_wire).Face();
		TopoDS_Shape prism = BRepPrimAPI_MakePrism (boundary_wire,gp_Vec(0,0,1),1);
		prism.Move(trsf);
		face.Move(trsf);

		gp_Pln pln = plane_from_face(TopoDS::Face(face));
		gp_Pnt pnt = point_above_plane(pln,ifc_bounded_halfspace->AgreementFlag());

		TopoDS_Shape halfspace;
		Ifc2x3::IfcHalfSpaceSolid::ptr ifc_halfspace = (Ifc2x3::IfcHalfSpaceSolid::ptr) operand2;
		if ( ! IfcGeom::convert(ifc_halfspace,halfspace) ) return false;

		TopoDS_Shape subtraction_volume = s1;
		double subtraction_volume_volume = shape_volume(subtraction_volume);

		const double minimal_substraction_difference = subtraction_volume_volume * 0.0001;

		BRepAlgoAPI_Common brep_common(subtraction_volume,halfspace);
		if ( brep_common.IsDone() ) {
			TopoDS_Shape brep_common_shape = brep_common;
			bool is_valid = BRepCheck_Analyzer(brep_common_shape).IsValid() != 0;
			double new_subtraction_volume_volume = shape_volume(brep_common_shape);
			double subtraction_volume_difference = subtraction_volume_volume - new_subtraction_volume_volume;
			if ( is_valid && subtraction_volume_difference > minimal_substraction_difference ) {
				subtraction_volume = brep_common_shape;
				subtraction_volume_volume = new_subtraction_volume_volume;
			}
		}

		TopExp_Explorer exp(prism,TopAbs_FACE);
		while ( exp.More() ) {
			TopoDS_Shape halfspace = halfspace_from_plane(plane_from_face(TopoDS::Face(exp.Current())),pnt);
			BRepAlgoAPI_Common brep_common(subtraction_volume,halfspace);
			if ( brep_common.IsDone() ) {
				TopoDS_Shape brep_common_shape = brep_common;
				bool is_valid = BRepCheck_Analyzer(brep_common_shape).IsValid() != 0;
				double new_subtraction_volume_volume = shape_volume(brep_common_shape);
				double subtraction_volume_difference = subtraction_volume_volume - new_subtraction_volume_volume;
				if ( is_valid && subtraction_volume_difference > minimal_substraction_difference ) {
					subtraction_volume = brep_common_shape;
					subtraction_volume_volume = new_subtraction_volume_volume;
				}
			}
			exp.Next();
		}

		BRepAlgoAPI_Cut brep_cut(s1,subtraction_volume);
		if ( brep_cut.IsDone() ) {
			TopoDS_Shape result = brep_cut;
			bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
			if ( is_valid ) {
				shape = result;
				valid_cut = true;
			} 
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

}
bool IfcGeom::convert(const Ifc2x3::IfcConnectedFaceSet::ptr l, TopoDS_Shape& shape) {
	Ifc2x3::IfcFace::list faces = l->CfsFaces();
	bool facesAdded = false;
	const unsigned int num_faces = faces->Size();
	if ( num_faces < GetValue(GV_MAX_FACES_TO_SEW) ) {
		BRepOffsetAPI_Sewing builder;
		builder.SetTolerance(GetValue(GV_POINT_EQUALITY_TOLERANCE));
		builder.SetMaxTolerance(GetValue(GV_POINT_EQUALITY_TOLERANCE));
		builder.SetMinTolerance(GetValue(GV_POINT_EQUALITY_TOLERANCE));
		for( Ifc2x3::IfcFace::it it = faces->begin(); it != faces->end(); ++ it ) {
			TopoDS_Face face;
			if ( IfcGeom::convert_face(*it,face) && face_area(face) > GetValue(GV_MINIMAL_FACE_AREA) ) {
				builder.Add(face);
				facesAdded = true;
			} else {
				Logger::Message(Logger::LOG_WARNING,"Invalid face:",(*it)->entity);
			}
		}
		if ( ! facesAdded ) return false;
		builder.Perform();
		shape = builder.SewedShape();
		try {
			ShapeFix_Solid solid;
			solid.LimitTolerance(GetValue(GV_POINT_EQUALITY_TOLERANCE));
			shape = solid.SolidFromShell(TopoDS::Shell(shape));
		} catch(...) {}
	} else {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);
		for( Ifc2x3::IfcFace::it it = faces->begin(); it != faces->end(); ++ it ) {
			TopoDS_Face face;
			if ( IfcGeom::convert_face(*it,face) && face_area(face) > GetValue(GV_MINIMAL_FACE_AREA) ) {
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
bool IfcGeom::convert(const Ifc2x3::IfcMappedItem::ptr l, IfcRepresentationShapeItems& shapes) {
	gp_GTrsf gtrsf;
	Ifc2x3::IfcCartesianTransformationOperator::ptr transform = l->MappingTarget();
	if ( transform->is(Ifc2x3::Type::IfcCartesianTransformationOperator3DnonUniform) ) {
		IfcGeom::convert(reinterpret_pointer_cast<Ifc2x3::IfcCartesianTransformationOperator,
			Ifc2x3::IfcCartesianTransformationOperator3DnonUniform>(transform),gtrsf);
	} else if ( transform->is(Ifc2x3::Type::IfcCartesianTransformationOperator2DnonUniform) ) {
		return false;
	} else if ( transform->is(Ifc2x3::Type::IfcCartesianTransformationOperator3D) ) {
		gp_Trsf trsf;
		IfcGeom::convert(reinterpret_pointer_cast<Ifc2x3::IfcCartesianTransformationOperator,
			Ifc2x3::IfcCartesianTransformationOperator3D>(transform),trsf);
		gtrsf = trsf;
	} else if ( transform->is(Ifc2x3::Type::IfcCartesianTransformationOperator2D) ) {
		gp_Trsf2d trsf_2d;
		IfcGeom::convert(reinterpret_pointer_cast<Ifc2x3::IfcCartesianTransformationOperator,
			Ifc2x3::IfcCartesianTransformationOperator2D>(transform),trsf_2d);
		gtrsf = (gp_Trsf) trsf_2d;
	}
	Ifc2x3::IfcRepresentationMap::ptr map = l->MappingSource();
	Ifc2x3::IfcAxis2Placement placement = map->MappingOrigin();
	gp_Trsf trsf;
	if (placement->is(Ifc2x3::Type::IfcAxis2Placement3D)) {
		IfcGeom::convert((Ifc2x3::IfcAxis2Placement3D*)placement,trsf);
	} else {
		gp_Trsf2d trsf_2d;
		IfcGeom::convert((Ifc2x3::IfcAxis2Placement2D*)placement,trsf_2d);
		trsf = trsf_2d;
	}
	gtrsf.Multiply(trsf);
	const unsigned int previous_size = (const unsigned int) shapes.size();
	bool b = IfcGeom::convert_shapes(map->MappedRepresentation(),shapes);
	for ( unsigned int i = previous_size; i < shapes.size(); ++ i ) {
		shapes[i].move(gtrsf);
	}
	return b;
}

bool IfcGeom::convert(const Ifc2x3::IfcShapeRepresentation::ptr l, IfcRepresentationShapeItems& shapes) {
	Ifc2x3::IfcRepresentationItem::list items = l->Items();
	if ( ! items->Size() ) return false;
	for ( Ifc2x3::IfcRepresentationItem::it it = items->begin(); it != items->end(); ++ it ) {
		Ifc2x3::IfcRepresentationItem* representation_item = *it;
		if ( IfcGeom::is_shape_collection(representation_item) ) IfcGeom::convert_shapes(*it,shapes);
		else {
			TopoDS_Shape s;
			if (IfcGeom::convert_shape(representation_item,s)) {
				shapes.push_back(IfcRepresentationShapeItem(s, get_style(representation_item)));
			}
		}
	}
	return true;
}