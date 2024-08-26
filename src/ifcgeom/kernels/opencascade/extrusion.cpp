#include "OpenCascadeKernel.h"

#include <BRepPrimAPI_MakePrism.hxx>

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;

bool OpenCascadeKernel::convert(const taxonomy::extrusion::ptr extrusion, TopoDS_Shape& shape) {
	const double& height = extrusion->depth;

	if (height < settings_.get<settings::Precision>().get()) {
		Logger::Error("Non-positive extrusion height encountered for:", extrusion->instance);
		return false;
	}

	TopoDS_Shape face;
	if (!convert(taxonomy::cast<taxonomy::face>(extrusion->basis), face)) {
		return false;
	}

	/*
	// @todo we need to decide whether the matrix is kept on the taxonomy node or
	// move the TopoDS_Shape, but obviously not both.
	gp_GTrsf gtrsf;
	if (!convert(&extrusion->matrix, gtrsf)) {
		Logger::Error("Unable to move extrusion");
	}
	auto trsf = gtrsf.Trsf();
	*/

	const auto& fs = extrusion->direction->ccomponents();
	gp_Dir dir(fs(0), fs(1), fs(2));

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

	/*
	if (!shape.IsNull()) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}
	*/

	return !shape.IsNull();
}

bool OpenCascadeKernel::convert_impl(const taxonomy::extrusion::ptr extrusion, IfcGeom::ConversionResults& results) {
	TopoDS_Shape shape;
	if (!convert(extrusion, shape)) {
		return false;
	}

	results.emplace_back(ConversionResult(
		extrusion->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		extrusion->matrix,
		new OpenCascadeShape(shape),
		extrusion->surface_style
	));
	return true;
}
