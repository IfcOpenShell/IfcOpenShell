#include "opencascade_kernel.h"

#include <BRepAlgoAPI_Fuse.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <ShapeUpgrade_UnifySameDomain.hxx>
#include <TopTools_ListOfShape.hxx>

using namespace ifcopenshell::geom;
using namespace ifcopenshell::geom::kernels;

bool open_cascade_kernel::convert(const taxonomy::extrusion::ptr extrusion, TopoDS_Shape& shape) {
	const double& height = extrusion->depth;

	if (height < settings_.get<settings::Precision>().get()) {
		ifcopenshell::logger::root().error("GEO", 89, "Non-positive extrusion height encountered for:", extrusion->instance);
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
		ifcopenshell::logger::root().error("Unable to move extrusion");
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

bool open_cascade_kernel::convert_impl(const taxonomy::extrusion::ptr extrusion, std::vector<ifcopenshell::geom::conversion_result>& results) {
    return handle_occt_exception([&]() -> bool {

	TopoDS_Shape shape;
	if (!convert(extrusion, shape)) {
		return false;
	}

	results.emplace_back(conversion_result(
		extrusion->instance.id(),
		extrusion->matrix,
		new open_cascade_shape(shape),
		extrusion->surface_style
	));
	return true;

	});
}

bool open_cascade_kernel::convert_impl(const taxonomy::collection::ptr collection, std::vector<ifcopenshell::geom::conversion_result>& results) {
	// An IfcCompositeProfileDef is mapped to one extrusion per profile. Extruded
	// separately, touching profiles become solids with coincident faces, which
	// later boolean operations handle poorly. When the collection consists of
	// extrusions of the same swept area solid, fuse their profiles first so that
	// touching or overlapping profiles extrude into a single solid. Profiles that
	// remain disjoint still extrude into a compound of solids.
	std::vector<taxonomy::extrusion::ptr> extrusions;
	for (auto& c : collection->children) {
		auto e = taxonomy::dcast<taxonomy::extrusion>(c);
		if (!e || !e->matrix) {
			extrusions.clear();
			break;
		}
		if (!extrusions.empty()) {
			const auto& f = extrusions.front();
			if (e->instance != f->instance || e->depth != f->depth ||
				e->direction->ccomponents() != f->direction->ccomponents() ||
				e->matrix->ccomponents() != f->matrix->ccomponents())
			{
				extrusions.clear();
				break;
			}
		}
		extrusions.push_back(e);
	}

	if (extrusions.size() < 2) {
		return abstract_kernel::convert_impl(collection, results);
	}

	return handle_occt_exception([&]() -> bool {

	TopTools_ListOfShape arguments, tools;
	for (auto& e : extrusions) {
		TopoDS_Shape face;
		if (!convert(taxonomy::cast<taxonomy::face>(e->basis), face)) {
			return abstract_kernel::convert_impl(collection, results);
		}
		for (TopExp_Explorer exp(face, TopAbs_FACE); exp.More(); exp.Next()) {
			(arguments.IsEmpty() ? arguments : tools).Append(exp.Current());
		}
	}

	// Profiles are authored to touch, but their seams can be off by more than
	// the model precision. The same bound the wire builder uses for closing
	// gaps between segments is applied, so that a seam does not leave behind
	// a sliver face that later limits the fuzziness of boolean operations.
	BRepAlgoAPI_Fuse fuse;
	fuse.SetArguments(arguments);
	fuse.SetTools(tools);
	fuse.SetFuzzyValue(settings_.get<settings::Precision>().get() * 1000.);
	fuse.SetRunParallel(false);
	fuse.Build();
	if (!fuse.IsDone() || fuse.HasErrors()) {
		return abstract_kernel::convert_impl(collection, results);
	}

	ShapeUpgrade_UnifySameDomain unify(fuse.Shape(), true, true, false);
	unify.Build();

	const auto& first = extrusions.front();
	const auto& fs = first->direction->ccomponents();
	const gp_Vec vec = gp_Vec(fs(0), fs(1), fs(2)) * first->depth;

	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	TopoDS_Shape shape;
	int num_faces_extruded = 0;
	for (TopExp_Explorer exp(unify.Shape(), TopAbs_FACE); exp.More(); exp.Next(), ++num_faces_extruded) {
		shape = BRepPrimAPI_MakePrism(exp.Current(), vec);
		builder.Add(compound, shape);
	}

	if (num_faces_extruded == 0) {
		return abstract_kernel::convert_impl(collection, results);
	} else if (num_faces_extruded > 1) {
		shape = compound;
	}

	results.emplace_back(conversion_result(
		first->instance.id(),
		first->matrix,
		new open_cascade_shape(shape),
		first->surface_style
	));
	if (collection->matrix) {
		results.back().prepend(collection->matrix);
	}
	if (!results.back().hasStyle() && collection->surface_style) {
		results.back().setStyle(collection->surface_style);
	}
	return true;

	});
}
