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

#include "OpenCascadeKernel.h"

#include "boolean_utils.h"
#include "base_utils.h"

#include <BRepPrimAPI_MakeRevol.hxx>
#include <BOPAlgo_MakerVolume.hxx>

namespace {
	struct opening_sorter {
		bool operator()(const std::pair<double, TopoDS_Shape>& a, const std::pair<double, TopoDS_Shape>& b) const {
			return a.first > b.first;
		}
	};
}

using namespace ifcopenshell::geometry;

bool IfcGeom::OpenCascadeKernel::convert_openings(const IfcUtil::IfcBaseEntity* entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geometry::taxonomy::matrix4>>& openings,
	const IfcGeom::ConversionResults& entity_shapes, const ifcopenshell::geometry::taxonomy::matrix4& entity_trsf, IfcGeom::ConversionResults& cut_shapes) {

	util::boolean_settings bst;
	bst.attempt_2d = settings_.get<settings::BooleanAttempt2d>().get();
	bst.debug = settings_.get<settings::DebugBooleanOperations>().get();
	bst.precision = settings_.get<settings::Precision>().get();

	std::vector< std::pair<double, TopoDS_Shape> > opening_vector;

	for (auto& op : openings) {
		/*
		// Not yet implemented and tested, process opening placement up to parent wall
		// placement so that the matrix inverse can be eliminated.
		// @todo property check and handle the decomposition into parts (where element
		// carying geom and opening are in different branches).
		// @todo properly check whether opening correctly references wall placement
		// and fallback to matrix inverse when not the case.
		auto relative = entity;
		{
			auto ds = relative->Decomposes();
			if (ds->size() == 1) {
				relative = (*ds->begin())->RelatingObject()->as<IfcSchema::IfcProduct>();
			}
		}
		set_conversion_placement_rel_to_instance(relative);
		*/

		// Convert the IfcRepresentation of the IfcOpeningElement
		auto opening_trsf = op.second;

		// set_conversion_placement_rel_to_instance(nullptr);

		// Move the opening into the coordinate system of the IfcProduct

		// @todo
		Eigen::Matrix4d relative = entity_trsf.ccomponents().inverse() * opening_trsf.ccomponents();
		// opening_trsf = relative;

		IfcGeom::ConversionResults opening_shapes;
		
		// @todo
		AbstractKernel::convert(op.first, opening_shapes);

		for (unsigned int i = 0; i < opening_shapes.size(); ++i) {
			auto opening_shape_i = std::static_pointer_cast<OpenCascadeShape>(opening_shapes[i].Shape())->shape();
			const TopoDS_Shape& opening_shape_unlocated = util::ensure_fit_for_subtraction(opening_shape_i, settings_.get<settings::Precision>().get());

			auto gtrsf = opening_shapes[i].Placement();
			// @todo check
			Eigen::Matrix4d m = relative * gtrsf->ccomponents();
			gp_Trsf trsf;
			trsf.SetValues(
				m(0, 0), m(0, 1), m(0, 2), m(0, 3),
				m(1, 0), m(1, 1), m(1, 2), m(1, 3),
				m(2, 0), m(2, 1), m(2, 2), m(2, 3)
			);
			TopoDS_Shape opening_shape = util::apply_transformation(opening_shape_unlocated, trsf);
			opening_vector.push_back(std::make_pair(util::min_edge_length(opening_shape), opening_shape));
		}

	}

	std::sort(opening_vector.begin(), opening_vector.end(), opening_sorter());

	// Iterate over the shapes of the IfcProduct
	for (IfcGeom::ConversionResults::const_iterator it3 = entity_shapes.begin(); it3 != entity_shapes.end(); ++it3) {

		TopoDS_Compound C;
		BRep_Builder B;
		B.MakeCompound(C);
		TopoDS_Shape combined_result;

		std::list<TopoDS_Shape> parts;

		auto it3_shape = std::static_pointer_cast<OpenCascadeShape>(it3->Shape())->shape();
		if (it3_shape.IsNull()) {
			Logger::Root().Error("GEO", 187, "Null operand");
			continue;
		}

		bool is_multiple = it3_shape.ShapeType() == TopAbs_COMPOUND && TopoDS_Iterator(it3_shape).More() && util::is_nested_compound_of_solid(it3_shape);

		if (is_multiple) {
			TopoDS_Iterator sit(it3_shape);
			for (; sit.More(); sit.Next()) {
				parts.push_back(sit.Value());
			}
		} else {
			parts.push_back(it3_shape);
		}

		for (auto entity_part : parts) {
			bool is_manifold = util::is_manifold(entity_part);

			if (!is_manifold) {
				// force sewing, edge identity might have been mudied by FixAdvFace.FixOrientation.MSG5 to fix interior loop winding order
                NCollection_List<TopoDS_Shape> list;
                IfcGeom::util::shape_to_face_list(entity_part, list);
                IfcGeom::util::create_solid_from_faces(list, entity_part, settings_.get<settings::Precision>().get(), true);
                is_manifold = util::is_manifold(entity_part);
                if (is_manifold) {
					Logger::Root().Warning("GEO", 188, "Successfully sewed non-manifold first operand");
                }
			}

			if (!is_manifold) {
                if (settings_.get<settings::MakeVolume>().get()) {
                    BOPAlgo_MakerVolume mv;
                    mv.AddArgument(entity_part);
                    mv.SetAvoidInternalShapes(true);
                    // mv.SetFuzzyValue(settings_.get<settings::Precision>().get());
                    std::optional<std::string> failure;
                    try {
                        mv.Perform();
                        auto entity_part_2 = mv.Shape();
                        if (IfcGeom::util::count(entity_part_2, TopAbs_FACE) == 0) {
                            failure = "Empty result (no faces) for BOPAlgo_MakerVolume; original was " + std::to_string(IfcGeom::util::count(entity_part, TopAbs_FACE));
						} else {
                            is_manifold = util::is_manifold(entity_part_2);
                            Logger::Root().Warning("GEO", 189, std::string("Sucessfully detected exterior volume to non-manifold first operand; shape is now ") + (is_manifold ? std::string("manifold") : std::string("non-manifold")));
                            entity_part = entity_part_2;
						}
                    } catch (const Standard_Failure& e) {
                        failure.emplace(e.GetMessageString());
                    }
                    if (failure) {
                        Logger::Root().Warning("GEO", 190, "MakeVolume failed: " + *failure, entity);
                    }
                } else {
                    Logger::Root().Warning("GEO", 191, "Non-manifold first operand, use --make-volume to try and make manifold");
				}
			}

			TopoDS_Shape entity_part_result;

			for (int as_shell = 0; as_shell < 2; ++as_shell) {
				TopoDS_Shape entity_shape_unlocated;
				if (as_shell) {
					entity_shape_unlocated = entity_part;
				} else {
					entity_shape_unlocated = util::ensure_fit_for_subtraction(entity_part, settings_.get<settings::Precision>().get());
				}
				const auto& m = it3->Placement()->ccomponents();
				// @todo
				// if (entity_shape_gtrsf.Form() == gp_Other) {
				// 	Logger::Message(Logger::LOG_WARNING, "Applying non uniform transformation to:", entity);
				// }
				gp_Trsf entity_shape_gtrsf;
				entity_shape_gtrsf.SetValues(
					m(0, 0), m(0, 1), m(0, 2), m(0, 3),
					m(1, 0), m(1, 1), m(1, 2), m(1, 3),
					m(2, 0), m(2, 1), m(2, 2), m(2, 3)
				);
				TopoDS_Shape entity_shape = util::apply_transformation(entity_shape_unlocated, entity_shape_gtrsf);

				TopoDS_Shape result = entity_shape;

				auto it = opening_vector.begin();
				auto jt = it;

				for (;; ++it) {
					if (it == opening_vector.end() || jt->first / it->first > 10.) {

						NCollection_List<TopoDS_Shape> opening_list;
						for (auto kt = jt; kt < it; ++kt) {
							opening_list.Append(kt->second);
						}

						TopoDS_Shape intermediate_result;
						if (util::boolean_operation(bst, result, opening_list, BOPAlgo_CUT, intermediate_result)) {
							result = intermediate_result;
						} else {
							Logger::Root().Message(Logger::LOG_ERROR, "GEO", 192, "Opening subtraction failed for " + boost::lexical_cast<std::string>(std::distance(jt, it)) + " openings", entity);
						}

						jt = it;
					}

					if (it == opening_vector.end()) {
						break;
					}
				}

				int result_n_faces = util::count(result, TopAbs_FACE);

				if (!is_manifold && as_shell == 0 && result_n_faces == 0) {
					// If we have a non-manifold first operand and our first attempt
					// on a Solid-Solid subtraction yielded a empty result (no faces)
					// or a strange result, a larger number of faces with the original input
					// included. Then retry (another iteration on the for-loop on as-shell)
					// where we keep the first operand as is (a compound of faces probably,
					// unless --orient-shells was activated in which case we're already lost).
					if (!is_manifold) {
						Logger::Root().Warning("GEO", 193, "Retrying boolean operation on individual faces");
					}
					continue;
				}

				entity_part_result = result;

				// For manifold first operands we're not even going to try if processing
				// as loose faces gives a better result.
				break;
			}

			if (is_multiple) {
				B.Add(C, entity_part_result);
			} else {
				combined_result = entity_part_result;
			}

		}

		if (is_multiple) {
			combined_result = C;
		}

		cut_shapes.push_back(IfcGeom::ConversionResult(it3->ItemId(), new OpenCascadeShape(combined_result), it3->StylePtr()));
	}
	return true;
}

bool IfcGeom::OpenCascadeKernel::unify_shapes(const IfcGeom::ConversionResults& input, IfcGeom::ConversionResults& output) {
	std::transform(input.begin(), input.end(), std::back_inserter(output), [this](auto v) {
		auto& s = std::static_pointer_cast<OpenCascadeShape>(v.Shape())->shape();
		return IfcGeom::ConversionResult(
			v.ItemId(),
			v.Placement(),
			new OpenCascadeShape(util::unify(s, settings_.get<ifcopenshell::geometry::settings::Precision>().get())),
			v.StylePtr());
	});
	return true;
}

bool IfcGeom::OpenCascadeKernel::convert_impl(const taxonomy::revolve::ptr r, IfcGeom::ConversionResults& results) {
    return handle_occt_exception([&]() -> bool {
        gp_Ax1 ax(
            convert_xyz<gp_Pnt>(*r->axis_origin),
            convert_xyz<gp_Dir>(*r->direction));

        TopoDS_Shape face;
        if (!convert(taxonomy::cast<taxonomy::face>(r->basis), face)) {
            return false;
        }

        TopoDS_Shape shape;
        if (r->angle) {
            shape = BRepPrimAPI_MakeRevol(face, ax, *r->angle);
        } else {
            shape = BRepPrimAPI_MakeRevol(face, ax);
        }

        results.emplace_back(ConversionResult(
            r->instance->as<IfcUtil::IfcBaseEntity>()->id(),
            r->matrix,
            new OpenCascadeShape(shape),
            r->surface_style));
        return true;
    });
}
