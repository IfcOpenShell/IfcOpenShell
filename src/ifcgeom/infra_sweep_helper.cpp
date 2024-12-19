#include "profile_helper.h"
#include "infra_sweep_helper.h"
#include "function_item_evaluator.h"

#include <boost/range/combine.hpp>

using namespace ifcopenshell::geometry;

namespace {
	// std::lerp when upgrading to C++ 20
	template <typename T>
	T lerp(const T& a, const T& b, double t) {
		return a + t * (b - a);
	}
}

taxonomy::loft::ptr ifcopenshell::geometry::make_loft(const Settings& settings_, const IfcUtil::IfcBaseClass* inst, const taxonomy::function_item::ptr& fn, std::vector<cross_section>& cross_sections)
{
	std::sort(cross_sections.begin(), cross_sections.end());

	auto loft = taxonomy::make<taxonomy::loft>();
	// @todo intialize as default
	loft->axis = nullptr;

	// @todo currently only the case is handled where directrix returns a function_item
	// @todo this "if" statement is not really required because the function returns at the start if the Directrix is not a function_item function
	if (fn) {
		function_item_evaluator evaluator(settings_,fn);
		double start = std::max(0., cross_sections.front().dist_along);
		double end = std::min(fn->length(), cross_sections.back().dist_along);

		if (end - start < 1.e-9) {
			Logger::Warning("Empty sweep domain with start at " + std::to_string(cross_sections.front().dist_along) + " end at " + std::to_string(cross_sections.back().dist_along) + " and curve domain length " + std::to_string(fn->length()), inst);
			return nullptr;
		}

		auto curve_length = end - start;
		auto param_type = settings_.get<ifcopenshell::geometry::settings::FunctionStepType>().get();
		auto param = settings_.get<ifcopenshell::geometry::settings::FunctionStepParam>().get();
		size_t num_steps = 0;
		if (param_type == ifcopenshell::geometry::settings::FunctionStepMethod::MAXSTEPSIZE) {
			// parameter is max step size
			num_steps = (size_t)std::ceil(curve_length / param);
		} else {
			// parameter is minimum number of steps
			num_steps = (size_t)std::ceil(param);
		}
		std::vector<double> longitudes;
		for (auto& x : cross_sections) {
			longitudes.push_back(x.dist_along);
		}
		longitudes.push_back(std::numeric_limits<double>::infinity());
		auto profile_index = longitudes.begin();
		for (size_t i = 0; i <= num_steps; ++i) {
			auto dist_along = start + curve_length / num_steps * i;
			while (dist_along > *(profile_index + 1)) {
				profile_index++;
				if (profile_index == longitudes.end()) {
					// @todo handle this? 
				}
			}

			auto relative_dist_along = (dist_along - *profile_index) / (*(profile_index + 1) - *profile_index);
			const auto& profile_a = cross_sections[std::distance(longitudes.begin(), profile_index)].section_geometry;
			const auto& offset_a = cross_sections[std::distance(longitudes.begin(), profile_index)].offset;

			taxonomy::geom_item::ptr interpolated = nullptr;

			// Only interpolate if:
			//  - there is a profile ahead of us, and
			//  - we're not exactly at the location of the current profile or whether there is an offset involved.
			bool should_interpolate =
				(profile_index + 1 < longitudes.end()) &&
				(relative_dist_along >= 1.e-9 || offset_a.cwiseAbs().maxCoeff() > 0.);

			if (should_interpolate) {
				taxonomy::geom_item::ptr profile_b;
				Eigen::Vector3d offset_b;
				if ((profile_index + 1 < longitudes.end())) {
					profile_b = cross_sections[std::distance(longitudes.begin(), profile_index) + 1].section_geometry;
					offset_b = cross_sections[std::distance(longitudes.begin(), profile_index) + 1].offset;
				} else {
					profile_b = profile_a;
					offset_b = offset_a;
				}

				// Only interpolate if the profiles are different or either of the offsets is non-zero
				bool should_interpolate2 =
					(profile_a->instance != profile_b->instance) ||
					(offset_a.cwiseAbs().maxCoeff() > 0. || offset_b.cwiseAbs().maxCoeff() > 0.);

				if (should_interpolate2) {

					std::vector<taxonomy::loop::ptr> loops_a, loops_b;

					if (profile_a->kind() == taxonomy::FACE) {
						interpolated = taxonomy::make<taxonomy::face>();

						auto profile_a_f = std::static_pointer_cast<taxonomy::face>(profile_a);
						auto profile_b_f = std::static_pointer_cast<taxonomy::face>(profile_b);

						if (profile_a_f->children.size() != profile_b_f->children.size()) {
							Logger::Warning("Mismatching number of face boundaries: " +
								std::to_string(profile_a_f->children.size()) + " vs " +
								std::to_string(profile_b_f->children.size()),
								inst
							);
							return nullptr;
						}
						loops_a = profile_a_f->children;
						loops_b = profile_b_f->children;
					} else {
						loops_a = { std::static_pointer_cast<taxonomy::loop>(profile_a) };
						loops_b = { std::static_pointer_cast<taxonomy::loop>(profile_b) };
						interpolated = taxonomy::make<taxonomy::loop>();
					}

					// @todo should_interpolate should also be informed based by different face matrices.
					if (profile_a->matrix || profile_b->matrix) {
						interpolated->matrix = taxonomy::make<taxonomy::matrix4>();
						Eigen::Matrix4d m4a = Eigen::Matrix4d::Identity();
						Eigen::Matrix4d m4b = Eigen::Matrix4d::Identity();
						if (profile_a->matrix) {
							m4a = profile_a->matrix->ccomponents();
						}
						if (profile_b->matrix) {
							m4b = profile_b->matrix->ccomponents();
						}
						interpolated->matrix->components() = lerp(m4a, m4b, relative_dist_along);
					}
					
					auto interpolated_offset = lerp(offset_a, offset_b, relative_dist_along);
					taxonomy::loop::ptr w1, w2;
					taxonomy::edge::ptr e1, e2;
					for (auto tmp_ : boost::combine(loops_a, loops_b)) {
						boost::tie(w1, w2) = tmp_;
						if (w1->children.size() != w2->children.size()) {
							Logger::Warning("Mismatching number of edges: " +
								std::to_string(w1->children.size()) + " vs " +
								std::to_string(w2->children.size()),
								inst
							);
							return nullptr;
						}
						std::vector<taxonomy::point3::ptr> points;
						for (auto tmp__ : boost::combine(w1->children, w2->children)) {
							boost::tie(e1, e2) = tmp__;
							auto& p1 = boost::get<taxonomy::point3::ptr>(e1->start);
							auto& p2 = boost::get<taxonomy::point3::ptr>(e2->start);

							auto p3 = (lerp(p1->ccomponents(), p2->ccomponents(), relative_dist_along) + interpolated_offset).eval();
							points.push_back(taxonomy::make<taxonomy::point3>(p3));
						}
						if (!points.empty()) {
							// close polygon by referencing first point
							// @todo add a closed=true|false to polygon_from_points()?
							points.push_back(points.front());
						}

						auto interpolated_loop = polygon_from_points(points);
						if (interpolated->kind() == taxonomy::FACE) {
							std::static_pointer_cast<taxonomy::face>(interpolated)->children.push_back(interpolated_loop);
						} else {
							std::static_pointer_cast<taxonomy::loop>(interpolated)->children = interpolated_loop->children;
						}
					}
				}
			}

			auto m4 = evaluator.evaluate(dist_along);
			/* {
				std::wcout << "#" << pwf->instance->data().id() << " " << dist_along << ": " << m4.col(3).row(2).value() << std::endl;
			}*/

			Eigen::Matrix4d m4b = Eigen::Matrix4d::Identity();
			m4b.col(0).head<3>() = m4.col(1).head<3>().normalized();
			m4b.col(1).head<3>() = m4.col(2).head<3>().normalized();
			m4b.col(2).head<3>() = m4.col(0).head<3>().normalized();
			m4b.col(3).head<3>() = m4.col(3).head<3>();

			if (interpolated) {
				loft->children.push_back(interpolated);
			} else {
				if (profile_a->kind() == taxonomy::FACE) {
					loft->children.push_back(std::static_pointer_cast<taxonomy::face>(taxonomy::item::ptr(profile_a->clone_())));
				} else {
					loft->children.push_back(std::static_pointer_cast<taxonomy::loop>(taxonomy::item::ptr(profile_a->clone_())));
				}
				if (profile_a->matrix) {
					loft->children.back()->matrix = taxonomy::matrix4::ptr(profile_a->matrix->clone_());
				}
			}
			if (!loft->children.back()->matrix) {
				// @todo should this not be initialized by default? matrix4 already has a 'lazy identity' mechanism.
				loft->children.back()->matrix = taxonomy::make<taxonomy::matrix4>();
			}
			auto m = (m4b * loft->children.back()->matrix->ccomponents()).eval();
			loft->children.back()->matrix->components() = m;
		}
	}

	return loft;
}
