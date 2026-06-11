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

namespace {
template <typename T, typename Cmp = std::less<T>>
bool has_intersection(const std::set<T, Cmp>& A,
                      const std::set<T, Cmp>& B) {
    auto itA = A.begin();
    auto itB = B.begin();

    while (itA != A.end() && itB != B.end()) {
        if (Cmp()(*itA, *itB)) {
            ++itA;
        } else if (Cmp()(*itB, *itA)) {
            ++itB;
        } else {
            return true;
        }
    }
    return false;
}

}

taxonomy::loft::ptr ifcopenshell::geometry::make_loft(const Settings& settings_, const IfcUtil::IfcBaseClass* inst, const taxonomy::function_item::ptr& fn, std::vector<cross_section>& cross_sections, Logger& logger)
{
	std::sort(cross_sections.begin(), cross_sections.end());

	auto loft = taxonomy::make<taxonomy::loft>();
	// @todo intialize as default
	loft->axis = nullptr;

	// @todo currently only the case is handled where directrix returns a function_item
	// @todo this "if" statement is not really required because the function returns at the start if the Directrix is not a function_item function
	if (fn) {
		function_item_evaluator evaluator(settings_, fn);
		double start = std::max(0., cross_sections.front().dist_along);
		double end = std::min(fn->length(), cross_sections.back().dist_along);

		if (end - start < 1.e-9) {
			Logger::Root().Warning("GEO", 40, "Empty sweep domain with start at " + std::to_string(cross_sections.front().dist_along) + " end at " + std::to_string(cross_sections.back().dist_along) + " and curve domain length " + std::to_string(fn->length()), inst);
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
        auto delta_step = curve_length / num_steps;
		std::vector<double> longitudes;
		for (auto& x : cross_sections) {
			longitudes.push_back(x.dist_along);
		}
		longitudes.push_back(std::numeric_limits<double>::infinity());
		auto profile_index = longitudes.begin();
		for (size_t i = 0; i <= num_steps; ++i) {
            auto dist_along = start + delta_step * i;
			while (dist_along > *(profile_index + 1)) {
				profile_index++;
				if (profile_index == longitudes.end()) {
					// @todo handle this? 
				}
			}

			const bool is_last_placement_of_this_profile = profile_index + 1 >= longitudes.end() ? false : ((start + delta_step * (i+1)) > *(profile_index + 1));

			auto relative_dist_along = (dist_along - *profile_index) / (*(profile_index + 1) - *profile_index);
			const auto& profile_a = cross_sections[std::distance(longitudes.begin(), profile_index)].section_geometry;
			const auto& offset_a = cross_sections[std::distance(longitudes.begin(), profile_index)].offset;
			const auto& rotation_a = cross_sections[std::distance(longitudes.begin(), profile_index)].rotation;

			taxonomy::geom_item::ptr interpolated = nullptr;

			// Only interpolate if:
			//  - there is a profile ahead of us, and
			//  - we're not exactly at the location of the current profile or whether there is an offset involved
			bool should_interpolate =
				(profile_index + 1 < longitudes.end()) &&
				(relative_dist_along >= 1.e-9 || offset_a.cwiseAbs().maxCoeff() > 0. || rotation_a);

			boost::optional<Eigen::Matrix3d> interpolated_rotation;

			if (should_interpolate) {
				taxonomy::geom_item::ptr profile_b;
				Eigen::Vector3d offset_b;
				boost::optional<Eigen::Matrix3d> rotation_b;
				if ((profile_index + 1 < longitudes.end())) {
					profile_b = cross_sections[std::distance(longitudes.begin(), profile_index) + 1].section_geometry;
					offset_b = cross_sections[std::distance(longitudes.begin(), profile_index) + 1].offset;
					rotation_b = cross_sections[std::distance(longitudes.begin(), profile_index) + 1].rotation;
				} else {
					profile_b = profile_a;
					offset_b = offset_a;
					rotation_b = rotation_a;
				}

				// Only interpolate if the profiles are different or either of the offsets is non-zero
				bool should_interpolate2 =
					(profile_a->instance != profile_b->instance) ||
					(offset_a.cwiseAbs().maxCoeff() > 0. || offset_b.cwiseAbs().maxCoeff() > 0. || rotation_b);

				if (should_interpolate2) {

					std::vector<taxonomy::loop::ptr> loops_a, loops_b;

					if (profile_a->kind() == taxonomy::FACE) {
						interpolated = taxonomy::make<taxonomy::face>();

						auto profile_a_f = std::static_pointer_cast<taxonomy::face>(profile_a);
						auto profile_b_f = std::static_pointer_cast<taxonomy::face>(profile_b);

						if (profile_a_f->children.size() != profile_b_f->children.size()) {
							Logger::Root().Warning("GEO", 41, "Mismatching number of face boundaries: " +
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
                    if (rotation_a.has_value() && rotation_b.has_value() ) {
                            // @todo we don't support an overridden rotation on only one of the placements
                        // in which case we would need to lerp with the rotation component below in m4b.
                        interpolated_rotation = lerp(*rotation_a, *rotation_b, relative_dist_along);
                    } else if (rotation_a != rotation_b) {
                        logger.Error("GEO", 42, "Direction vectors on cross section placements only supported when used consistently");
					}

					taxonomy::loop::ptr w1, w2;
					taxonomy::edge::ptr e1, e2;
                    taxonomy::point3::ptr p1, p2;

					for (auto tmp_ : boost::combine(loops_a, loops_b)) {
						boost::tie(w1, w2) = tmp_;

						if (w1->closed != w2->closed) {
							logger.Warning("GEO", 43, "Mismatching closed property on loops", inst);
							return nullptr;
                        }

						if (w1->tags.is_initialized() != w2->tags.is_initialized()) {
							logger.Warning("GEO", 44, "Mismatching availability tags on loops", inst);
							return nullptr;
                        }

						if (w1->tags) {
							// check uniqueness
                            std::set<std::string> tags_seen;
                            for (const auto& t : *w1->tags) {
								if (tags_seen.find(t) != tags_seen.end()) {
									logger.Warning("GEO", 45, "Duplicate tag '" + t + "' on loft profile", inst);
									return nullptr;
								}
								tags_seen.insert(t);
                            }
						}

						if (w2->tags) {
                            // check uniqueness
                            std::set<std::string> tags_seen;
                            for (const auto& t : *w2->tags) {
                                if (tags_seen.find(t) != tags_seen.end()) {
                                    logger.Warning("GEO", 46, "Duplicate tag '" + t + "' on loft profile", inst);
                                    return nullptr;
                                }
                                tags_seen.insert(t);
                            }
                        }

						std::map<std::string, taxonomy::point3::ptr> tag_to_point_on_w1, tag_to_point_on_w2;

						auto loop_to_points = [](const taxonomy::loop::ptr& loop, const boost::optional<std::vector<std::string>>& input_tags) -> std::pair<std::vector<taxonomy::point3::ptr>, std::vector<std::set<std::string>>> {
                            std::vector<taxonomy::point3::ptr> points;
                            std::vector<std::set<std::string>> tags;
                            std::vector<std::string>::const_iterator tag_it;
                            
							if (!loop->closed.get_value_or(false)) {
                                points = {boost::get<taxonomy::point3::ptr>(loop->children[0]->start)};
                                if (input_tags) {
                                    tags = {{input_tags->front()}};
                                    tag_it = ++input_tags->begin();
                                }
							}
							for (auto& e : loop->children) {
								const auto& p1_ = boost::get<taxonomy::point3::ptr>(e->start);
								const auto& p2_ = boost::get<taxonomy::point3::ptr>(e->end);
                                if (input_tags && p1_->ccomponents() == p2_->ccomponents()) {
                                    tags.back().insert(*tag_it);
                                    ++tag_it;
                                } else {
                                    points.push_back(p2_);
                                    if (input_tags) {
                                        tags.emplace_back();
                                        tags.back().insert(*tag_it);
                                        ++tag_it;
                                    }
                                }
							}
                            if (!input_tags) {
                                if (loop->closed.get_value_or(false)) {
									// close polygon by referencing first point
									points.push_back(points.front());
                                }
							}
                            return {points, tags};
                        };

						auto combine_tags = [](const std::vector<std::set<std::string>>& tag_sets) -> std::set<std::string> {
							return std::accumulate(
								tag_sets.begin(), tag_sets.end(), std::set<std::string>{},
								[](std::set<std::string> acc,
								   const std::set<std::string>& m) {
									acc.insert(m.begin(), m.end());
									return acc;
								});
                        };

						auto join_tags = [](const std::set<std::string>& tag_set) -> std::string {
							std::string result;
							for (auto it = tag_set.begin(); it != tag_set.end(); ++it) {
								if (it != tag_set.begin()) {
									result += ", ";
								}
								result += *it;
							}
							return result;
                        };

						auto [w1_points, w1_tags] = loop_to_points(w1, w1->tags);
                        auto [w2_points, w2_tags] = loop_to_points(w2, w2->tags);

						if (w1->tags && w2->tags) {
							{
                                auto it = w1_points.begin();
                                auto jt = w1_tags.begin();
                                while (it != w1_points.end() && jt != w1_tags.end()) {
                                    for (auto& t : *jt) {
                                        tag_to_point_on_w1[t] = *it;
									}
                                    ++it;
                                    ++jt;
                                }
							}

							{
                                auto it = w2_points.begin();
                                auto jt = w2_tags.begin();
                                while (it != w2_points.end() && jt != w2_tags.end()) {
                                    for (auto& t : *jt) {
                                        tag_to_point_on_w2[t] = *it;
                                    }
                                    ++it;
                                    ++jt;
                                }
                            }

							auto w1_tags_combined = combine_tags(w1_tags);
                            auto w2_tags_combined = combine_tags(w2_tags);

							// For every point (which can have multiple tags in case of 0-width edges) there needs to be a corresponding point on the other profile

							for (auto& p1_tags : w1_tags) {
                                if (!has_intersection(p1_tags, w2_tags_combined)) {
                                    logger.Warning("GEO", 47, "No matching tags found on loft profiles: " + join_tags(p1_tags) + " not in " + join_tags(w2_tags_combined), inst);
									return nullptr;
								}
							}

							for (auto& p2_tags : w2_tags) {
                                if (!has_intersection(p2_tags, w1_tags_combined)) {
                                    logger.Warning("GEO", 48, "No matching tags found on loft profiles: " + join_tags(p2_tags) + " not in " + join_tags(w1_tags_combined), inst);
                                    return nullptr;
								}
                            }
						} else {
                            if (w1->children.size() != w2->children.size()) {
                                logger.Warning("GEO", 49, "Mismatching number of edges: " +
                                                    std::to_string(w1->children.size()) + " vs " +
                                                    std::to_string(w2->children.size()),
                                                inst);
                                return nullptr;
                            }
						}

						std::vector<taxonomy::point3::ptr> points;

                        std::vector<std::string> common_tags_vec;
                        if (w1->tags) {
                            std::set<std::string> common_tags;
                            for (const auto& t : *w1->tags) {
                                if (tag_to_point_on_w2.find(t) == tag_to_point_on_w2.end()) {
                                    continue;
                                }

                                const auto& p1_ = tag_to_point_on_w1[t];
                                const auto& p2_ = tag_to_point_on_w2[t];

                                auto p3 = (lerp(p1_->ccomponents(), p2_->ccomponents(), relative_dist_along) + interpolated_offset).eval();

                                std::set<std::string> tags_for_this_point_on_subsequent_profile = {t};

								if (is_last_placement_of_this_profile) {
                                    for (auto& ts : w2_tags) {
                                        if (ts.find(t) != ts.end()) {
                                            tags_for_this_point_on_subsequent_profile = ts;
										}
									}
								}

                                for (auto& x : tags_for_this_point_on_subsequent_profile) {
									points.push_back(taxonomy::make<taxonomy::point3>(p3));
                                    common_tags_vec.push_back(x);
                                }     
                            }
                        } else {
                            for (auto tmp__ : boost::combine(w1_points, w2_points)) {
                                boost::tie(p1, p2) = tmp__;
                                auto p3 = (lerp(p1->ccomponents(), p2->ccomponents(), relative_dist_along) + interpolated_offset).eval();
                                points.push_back(taxonomy::make<taxonomy::point3>(p3));
                            }
                        }

						/*
						// This is handled in the loop_to_points() function above
                        if (!points.empty()) {
							if (!w1->closed.get_value_or(true) && !w2->closed.get_value_or(true)) {
                                // open polygon, add last point
                                auto& p1 = boost::get<taxonomy::point3::ptr>(w1->children.back()->end);
                                auto& p2 = boost::get<taxonomy::point3::ptr>(w2->children.back()->end);
                                auto p3 = (lerp(p1->ccomponents(), p2->ccomponents(), relative_dist_along) + interpolated_offset).eval();
                                points.push_back(taxonomy::make<taxonomy::point3>(p3));
                            } else if (w1->closed.get_value_or(true) && w2->closed.get_value_or(true)) {
                                // close polygon by referencing first point
                                // @todo add a closed=true|false to polygon_from_points()?
                                points.push_back(points.front());
                            }
						}
						*/

						auto interpolated_loop = polygon_from_points(points);
						if (interpolated->kind() == taxonomy::FACE) {
                            interpolated_loop->external = w1->external;
                            std::static_pointer_cast<taxonomy::face>(interpolated)->children.push_back(interpolated_loop);
						} else {
                            if (w1->tags) {
                                std::static_pointer_cast<taxonomy::loop>(interpolated)->tags = common_tags_vec;
							}
                            std::static_pointer_cast<taxonomy::loop>(interpolated)->closed = w1->closed;
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
			if (interpolated_rotation) {
				// direction vectors on the linear placement overwrite the placement otherwise inferred from the tangent
				m4b.col(0).head<3>() = interpolated_rotation->col(1);
				m4b.col(1).head<3>() = interpolated_rotation->col(2);
				m4b.col(2).head<3>() = interpolated_rotation->col(0);
			} else {
				m4b.col(0).head<3>() = m4.col(1).head<3>().normalized();
				m4b.col(1).head<3>() = m4.col(2).head<3>().normalized();
				m4b.col(2).head<3>() = m4.col(0).head<3>().normalized();
			}
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
