#include "opencascade_kernel.h"

#include "boolean_utils.h"
#include "base_utils.h"

#include <IntAna_QuadQuadGeo.hxx>
#include <Precision.hxx>

using namespace ifcopenshell::geom;
using namespace ifcopenshell::geom::kernels;

namespace {
	BOPAlgo_Operation op_to_occt(taxonomy::boolean_result::operation_type t) {
		switch (t) {
		case taxonomy::boolean_result::UNION: return BOPAlgo_FUSE;
		case taxonomy::boolean_result::INTERSECTION: return BOPAlgo_COMMON;
		case taxonomy::boolean_result::SUBTRACTION: return BOPAlgo_CUT;
		}
		throw std::invalid_argument("Unsupported boolean operation");
	}

	bool get_single_child(const TopoDS_Shape& s, TopoDS_Shape& child) {
		TopoDS_Iterator it(s);
		if (!it.More()) {
			return false;
		}
		child = it.Value();
		it.Next();
		return !it.More();
	}

	bool is_unbounded_halfspace(const TopoDS_Shape& solid) {
		if (solid.ShapeType() != TopAbs_SOLID) {
			return false;
		}
		TopoDS_Shape shell;
		if (!get_single_child(solid, shell)) {
			return false;
		}
		TopoDS_Shape face;
		if (!get_single_child(shell, face)) {
			return false;
		}
		TopoDS_Iterator it(face);
		return !it.More();
	}
}

void open_cascade_kernel::align_polygonal_halfspace(const TopoDS_Shape& first_operand, const taxonomy::solid::ptr& solid, const gp_Trsf& placement, TopoDS_Shape& tool) {
	// The polygonal bound of a half-space is extruded along its Position axis. When that
	// axis is rounded a little off, a side of the bound touches a face of the first operand
	// on one stretch and crosses it on the rest, which OpenCASCADE resolves into a wrong
	// solid (#349). Turn the bound about the line where the two planes meet so the side
	// coincides with the face; the clipping plane itself is left where the file puts it.
	const double tol = settings_.get<settings::Precision>().get();
	// Faces this close to parallel are taken as meant to coincide (0.057 degrees)
	const double drift_angle = 1.e-3;
	const auto& plane = taxonomy::cast<taxonomy::plane>(solid->children[0]->children[0]->basis)->matrix->ccomponents();
	const gp_Dir clipping_normal = convert_xyz2<gp_Dir>(plane.col(2)).Transformed(placement);
	gp_Trsf correction;
	// The bound may drift on two faces at once; one turn usually settles both.
	for (int attempt = 0; attempt < 2; ++attempt) {
		gp_Pln face_a, face_b;
		double drift;
		if (!util::drifting_contact(first_operand, tool, tol, face_a, face_b, drift) || drift > tol * 100.) {
			return;
		}
		const gp_Dir na = face_a.Axis().Direction();
		gp_Dir nb = face_b.Axis().Direction();
		if (na.Dot(nb) < 0.) {
			nb.Reverse();
		}
		const double angle = na.Angle(nb);
		IntAna_QuadQuadGeo meet(face_a, face_b, Precision::Angular(), Precision::Confusion());
		// Only a side of the bound is turned, not the clipping plane, and only onto a face
		// it was meant to share: a tilt beyond the drift angle is a design decision
		if (std::abs(nb.Dot(clipping_normal)) > 0.5 || angle < Precision::Angular() || angle > drift_angle || !meet.IsDone() || meet.TypeInter() != IntAna_Line) {
			return;
		}
		gp_Trsf turn;
		turn.SetRotation(gp_Ax1(meet.Line(1).Location(), nb.Crossed(na)), angle);
		// The bound is built in the half-space's own frame
		correction = placement.Inverted() * turn * placement * correction;
		tool = halfspace_solid(solid, correction);
		tool.Location(tool.Location() * placement);
		logger_.warning("GEO", 404, "Polygonal bound drifts " + std::to_string(drift) + " from a face of the first operand, turned " + std::to_string(angle) + " rad onto it:", solid->instance);
	}
}

bool open_cascade_kernel::convert_impl(const taxonomy::boolean_result::ptr br, std::vector<conversion_result>& results) {
    return handle_occt_exception([&]() -> bool {
	bool valid_result = false;
	bool first = true;
	const double tol = settings_.get<settings::Precision>().get();

	TopoDS_Shape a;
	NCollection_List<TopoDS_Shape> b;

	taxonomy::style::ptr first_item_style;

	for (auto& c : br->children) {
		std::vector<ifcopenshell::geom::conversion_result> cr;
		abstract_kernel::convert(c, cr);
		if (first && br->operation == taxonomy::boolean_result::SUBTRACTION) {
			// @todo A will be null on union/intersection, intended?
			ifcopenshell::geom::util::flatten_shape_list(cr, a, false, true, settings_.get<settings::Precision>().get());
			first_item_style = c->surface_style;
			if (!first_item_style && c->kind() == taxonomy::COLLECTION) {
				// @todo recursively right?
				first_item_style = taxonomy::cast<taxonomy::geom_item>(taxonomy::cast<taxonomy::collection>(c)->children[0])->surface_style;
			}

			if (settings_.get<settings::DisableBooleanResult>().get()) {
				results.emplace_back(ifcopenshell::geom::conversion_result(
					br->instance.id(),
					br->matrix,
					new open_cascade_shape(a),
					br->surface_style ? br->surface_style : first_item_style
				));
				return true;
			}

			const double first_operand_volume = util::shape_volume(a);
			if (first_operand_volume <= ALMOST_ZERO) {
				logger_.message(ifcopenshell::logger::LOG_WARNING, "GEO", 119, "Empty solid for:", c->instance);
			}
		} else {

			for (auto& r : cr) {
				auto S = std::static_pointer_cast<open_cascade_shape>(r.shape())->shape();
				if (S.IsNull()) {
					logger_.error("GEO", 120, "Null operand");
					continue;
				}
				gp_GTrsf trsf;
				convert(r.placement(), trsf);
				// @todo it really confuses me why I cannot use Moved() here instead
				S.Location(S.Location() * trsf.Trsf());

				if (is_unbounded_halfspace(S)) {
					double d;
					TopoDS_Shape result;
					util::fit_halfspace(a, S, result, d, tol * 1e3);
					// #2665 we also set a precision-independent threshold, because in the boolean op routine
					// the working fuzziness might still be increased.
					if (d < tol * 20. || d < 0.00002) {
						logger_.message(ifcopenshell::logger::LOG_WARNING, "GEO", 121, "Halfspace subtraction yields unchanged volume:", c->instance);
						continue;
					} else {
						S = result;
					}
				} else {
					S = util::ensure_fit_for_subtraction(S, tol);
				}

				if (br->operation == taxonomy::boolean_result::SUBTRACTION && !a.IsNull() && c->kind() == taxonomy::SOLID && c->instance && c->instance.declaration().is("IfcPolygonalBoundedHalfSpace")) {
					align_polygonal_halfspace(a, taxonomy::cast<taxonomy::solid>(c), trsf.Trsf(), S);
				}
				b.Append(S);
			}
		}
		first = false;
	}

	util::boolean_settings bst;
	bst.attempt_2d = settings_.get<settings::BooleanAttempt2d>().get();
	bst.debug = settings_.get<settings::DebugBooleanOperations>().get();
	bst.precision = settings_.get<settings::Precision>().get();
	bst.logger = &logger_;

	TopoDS_Shape r;

	if (br->operation == taxonomy::boolean_result::SUBTRACTION && !a.IsNull() && a.ShapeType() == TopAbs_COMPOUND && TopoDS_Iterator(a).More() && util::is_nested_compound_of_solid(a)) {
		TopoDS_Compound C;
		BRep_Builder B;
		B.MakeCompound(C);
		TopoDS_Iterator it(a);
		valid_result = true;
		for (; it.More(); it.Next()) {
			TopoDS_Shape part;
			if (util::boolean_operation(bst, it.Value(), b, op_to_occt(br->operation), part)) {
				B.Add(C, part);
			} else {
				valid_result = false;
			}
		}
		r = C;
	} else {
		if (br->operation != taxonomy::boolean_result::SUBTRACTION && a.IsNull()) {
			a = b.First();
			b.RemoveFirst();
		}
		valid_result = util::boolean_operation(bst, a, b, op_to_occt(br->operation), r);
	}

	if (valid_result) {
		std::swap(r, a);
	}

	results.emplace_back(ifcopenshell::geom::conversion_result(
		br->instance.id(),
		br->matrix,
		new open_cascade_shape(a),
		br->surface_style ? br->surface_style : first_item_style
	));

	return true;
    });
}
