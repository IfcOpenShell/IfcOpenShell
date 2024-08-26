#include "OpenCascadeKernel.h"

#include "boolean_utils.h"
#include "base_utils.h"

using namespace IfcGeom;
using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;

// @todo should we reapply the technique to apply openings in batches?
namespace {
	struct opening_sorter {
		bool operator()(const std::pair<double, TopoDS_Shape>& a, const std::pair<double, TopoDS_Shape>& b) const {
			return a.first > b.first;
		}
	};
 
	bool apply_in_batches(IfcGeom::util::boolean_settings bst, const TopoDS_Shape& first_operand, std::vector< std::pair<double, TopoDS_Shape> >& opening_vector, BOPAlgo_Operation occ_op, TopoDS_Shape& result) {
		auto it = opening_vector.begin();
		auto jt = it;
 
		result = first_operand;
		for (;; ++it) {
			if (it == opening_vector.end() || jt->first / it->first > 10.) {
 
				TopTools_ListOfShape opening_list;
				for (auto kt = jt; kt < it; ++kt) {
					opening_list.Append(kt->second);
				}
 
				TopoDS_Shape intermediate_result;
				if (IfcGeom::util::boolean_operation(bst, result, opening_list, occ_op, intermediate_result)) {
					result = intermediate_result;
				} else {
					return false;
				}
 
				jt = it;
			}
 
			if (it == opening_vector.end()) {
				break;
			}
		}
 
		return true;
	}
} 

namespace {
	BOPAlgo_Operation op_to_occt(taxonomy::boolean_result::operation_t t) {
		switch (t) {
		case taxonomy::boolean_result::UNION: return BOPAlgo_FUSE;
		case taxonomy::boolean_result::INTERSECTION: return BOPAlgo_COMMON;
		case taxonomy::boolean_result::SUBTRACTION: return BOPAlgo_CUT;
		}
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

bool OpenCascadeKernel::convert_impl(const taxonomy::boolean_result::ptr br, ConversionResults& results) {
	bool valid_result = false;
	bool first = true;
	const double tol = settings_.get<settings::Precision>().get();

	TopoDS_Shape a;
	TopTools_ListOfShape b;

	taxonomy::style::ptr first_item_style;

	for (auto& c : br->children) {
		IfcGeom::ConversionResults cr;
		AbstractKernel::convert(c, cr);
		if (first && br->operation == taxonomy::boolean_result::SUBTRACTION) {
			// @todo A will be null on union/intersection, intended?
			IfcGeom::util::flatten_shape_list(cr, a, false, true, settings_.get<settings::Precision>().get());
			first_item_style = c->surface_style;
			if (!first_item_style && c->kind() == taxonomy::COLLECTION) {
				// @todo recursively right?
				first_item_style = taxonomy::cast<taxonomy::geom_item>(taxonomy::cast<taxonomy::collection>(c)->children[0])->surface_style;
			}

			if (settings_.get<settings::DisableBooleanResult>().get()) {
				results.emplace_back(IfcGeom::ConversionResult(
					br->instance->as<IfcUtil::IfcBaseEntity>()->id(),
					br->matrix,
					new OpenCascadeShape(a),
					br->surface_style ? br->surface_style : first_item_style
				));
				return true;
			}

			const double first_operand_volume = util::shape_volume(a);
			if (first_operand_volume <= ALMOST_ZERO) {
				Logger::Message(Logger::LOG_WARNING, "Empty solid for:", c->instance);
			}
		} else {

			for (auto& r : cr) {
				auto S = std::static_pointer_cast<OpenCascadeShape>(r.Shape())->shape();
				if (S.IsNull()) {
					Logger::Error("Null operand");
					continue;
				}
				gp_GTrsf trsf;
				convert(r.Placement(), trsf);
				// @todo it really confuses me why I cannot use Moved() here instead
				S.Location(S.Location() * trsf.Trsf());

				if (is_unbounded_halfspace(S)) {
					double d;
					TopoDS_Shape result;
					util::fit_halfspace(a, S, result, d, tol * 1e3);
					// #2665 we also set a precision-independent threshold, because in the boolean op routine
					// the working fuzziness might still be increased.
					if (d < tol * 20. || d < 0.00002) {
						Logger::Message(Logger::LOG_WARNING, "Halfspace subtraction yields unchanged volume:", c->instance);
						continue;
					} else {
						S = result;
					}
				} else {
					S = util::ensure_fit_for_subtraction(S, tol);
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

	results.emplace_back(IfcGeom::ConversionResult(
		br->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		br->matrix,
		new OpenCascadeShape(a),
		br->surface_style ? br->surface_style : first_item_style
	));

	return true;
}
