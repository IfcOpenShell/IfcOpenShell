#include "profile_helper.h"
#include "infra_sweep_helper.h"
#include "function_item_evaluator.h"

#include <algorithm>
#include <boost/range/combine.hpp>
#include <cassert>

using namespace ifcopenshell::geom;

namespace {
	// std::lerp when upgrading to C++ 20
	template <typename T>
	T lerp(const T& a, const T& b, double t) {
		return a + t * (b - a);
	}
}

namespace {
taxonomy::loop::ptr interpolate_edges(const taxonomy::loop::ptr& a, const taxonomy::loop::ptr& b,
    const Eigen::Matrix3d& basis_a, const Eigen::Matrix3d& basis_b, const Eigen::Vector3d& offset,
    double fraction, const settings& settings) {
    if (a->children.size() != b->children.size()) {
        throw std::runtime_error("Loft interpolation requires corresponding edge counts");
    }
    Eigen::Matrix4d frame_a = Eigen::Matrix4d::Identity(), frame_b = frame_a;
    frame_a.block<3, 3>(0, 0) = basis_a;
    frame_b.block<3, 3>(0, 0) = basis_b;
    if (a->matrix) frame_a = (frame_a * a->matrix->ccomponents()).eval();
    if (b->matrix) frame_b = (frame_b * b->matrix->ccomponents()).eval();
    auto frame = lerp(frame_a, frame_b, fraction).eval();
    frame.col(3).head<3>() += offset;
    auto result = taxonomy::make<taxonomy::loop>(*a);
    result->instance = a->instance;
    result->surface_style = a->surface_style;
    result->orientation = a->orientation;
    result->matrix = nullptr;
    result->children.clear();
    for (size_t i = 0; i < a->children.size(); ++i) {
        const auto& ea = a->children[i];
        const auto& eb = b->children[i];
        if (taxonomy::equal_functor{}(ea, eb)) {
            // Copy the whole trimmed edge, retaining its basis, trims and senses.
            auto copy = taxonomy::make<taxonomy::edge>(*ea);
            copy->matrix = taxonomy::make<taxonomy::matrix4>(ea->matrix ?
                (frame * ea->matrix->ccomponents()).eval() : frame);
            result->children.push_back(copy);
        } else {
            const auto pa = ea->to_polygon(settings), pb = eb->to_polygon(settings);
            if (pa.size() != pb.size()) {
                throw std::runtime_error("Loft edge sampling counts differ at edge " + std::to_string(i + 1));
            }
            std::vector<taxonomy::point3::ptr> points;
            for (size_t j = 0; j < pa.size(); ++j) {
                const Eigen::Vector3d p = (frame_a * pa[j].ccomponents().homogeneous()).head<3>();
                const Eigen::Vector3d q = (frame_b * pb[j].ccomponents().homogeneous()).head<3>();
                points.push_back(taxonomy::make<taxonomy::point3>(lerp(p, q, fraction) + offset));
            }
            for (size_t j = 1; j < points.size(); ++j) {
                auto edge = taxonomy::make<taxonomy::edge>(points[j - 1], points[j]);
                edge->polygon_segments = 1;
                result->children.push_back(edge);
            }
        }
    }
    return result;
}

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

std::vector<std::vector<Eigen::Vector3d>> ifcopenshell::geom::section_points(const taxonomy::geom_item::ptr& section) {
	// to_polygon follows curved edges and applies the edges' and the loop's own matrices
	ifcopenshell::geom::settings settings;
	std::vector<taxonomy::loop::ptr> loops;
	Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
	if (section->kind() == taxonomy::FACE) {
		loops = std::static_pointer_cast<taxonomy::face>(section)->children;
		if (section->matrix) {
			m = section->matrix->ccomponents();
		}
	} else if (section->kind() == taxonomy::LOOP) {
		loops = {std::static_pointer_cast<taxonomy::loop>(section)};
	}

	std::vector<std::vector<Eigen::Vector3d>> result;
	for (const auto& loop : loops) {
		std::vector<Eigen::Vector3d> points;
		for (const auto& p : loop->to_polygon(settings)) {
			points.push_back((m * p.ccomponents().homogeneous()).head<3>());
		}
		if (points.empty()) {
			continue;
		}
		// the loops of a face are closed unless they say otherwise
		if (!loop->closed.has_value() && section->kind() == taxonomy::FACE && (points.front() - points.back()).norm() > 1.e-9) {
			points.push_back(points.front());
		}
		result.push_back(std::move(points));
	}
	return result;
}

taxonomy::loft::ptr ifcopenshell::geom::make_loft(const ifcopenshell::geom::settings& settings, const express::base inst, const taxonomy::function_item::ptr& fn, std::vector<cross_section>& input_sections, logger& logger)
{
	auto cross_sections = input_sections;
	std::sort(cross_sections.begin(), cross_sections.end());
	if (cross_sections.size() < 2) throw std::runtime_error("Loft requires at least two cross sections");
	auto authored = taxonomy::make<taxonomy::loft>();
	for (const auto& section : cross_sections) authored->children.push_back(section.section_geometry);
	auto compatible = authored->make_compatible_sections(settings);
	for (size_t i = 0; i < cross_sections.size(); ++i) cross_sections[i].section_geometry = compatible->children[i];

	auto loft = taxonomy::make<taxonomy::loft>();
	// @todo intialize as default
	loft->axis = nullptr;

	// @todo currently only the case is handled where directrix returns a function_item
	// @todo this "if" statement is not really required because the function returns at the start if the Directrix is not a function_item function
	if (fn) {
		function_item_evaluator evaluator(settings, fn);
		double start = std::max(0., cross_sections.front().dist_along);
		double end = std::min(fn->length(), cross_sections.back().dist_along);

		if (end - start < 1.e-9) {
			logger.warning("GEO", 40, "Empty sweep domain with start at " + std::to_string(cross_sections.front().dist_along) + " end at " + std::to_string(cross_sections.back().dist_along) + " and curve domain length " + std::to_string(fn->length()), inst);
			return nullptr;
		}

		std::vector<double> longitudes;
		for (auto& x : cross_sections) {
			longitudes.push_back(x.dist_along);
		}
		longitudes.push_back(std::numeric_limits<double>::infinity());

		// Directrix frame (col0 = tangent, col1 = lateral, col2 = up, col3 = position) at
		// every cross section station. Only needed to reconcile a cross section's own
		// Axis / RefDirection against the curve; skip the work when no placement has one.
		std::vector<Eigen::Matrix4d> section_directrix_frames;
		if (std::any_of(cross_sections.begin(), cross_sections.end(),
				[](const cross_section& cs) { return cs.rotation.has_value(); })) {
			section_directrix_frames.reserve(cross_sections.size());
			for (const auto& cs : cross_sections) {
				section_directrix_frames.push_back(evaluator.evaluate(std::min(std::max(cs.dist_along, start), end)));
			}
		}

		// The frame a cross section is placed in, given the directrix frame at its station
		// and its own IfcAxis2PlacementLinear: profile X, profile Y = Axis, profile normal
		// = RefDirection -- or, when RefDirection was not authored, the curve tangent, so
		// the section stays perpendicular to the path (buildingSMART IFC4.x-IF #147). When
		// the placement carries no direction vectors the section just follows the curve
		// (lateral, up, tangent).
		const auto profile_basis =
			[](const std::optional<Eigen::Matrix3d>& rotation,
			   const std::optional<Eigen::Vector3d>& ref_direction,
			   const Eigen::Matrix4d& directrix_frame) -> Eigen::Matrix3d {
			const Eigen::Vector3d tangent = directrix_frame.col(0).head<3>().normalized();
			const Eigen::Vector3d lateral = directrix_frame.col(1).head<3>().normalized();
			const Eigen::Vector3d up = directrix_frame.col(2).head<3>().normalized();
			Eigen::Matrix3d B;
			if (!rotation) {
				B.col(0) = lateral;
				B.col(1) = up;
				B.col(2) = tangent;
				return B;
			}
			const Eigen::Vector3d axis = rotation->col(2).normalized();
			const Eigen::Vector3d normal = ref_direction ? ref_direction->normalized() : tangent;
			Eigen::Vector3d x = axis.cross(normal);
			if (x.norm() < 1.e-9) {
				// Axis parallel to the normal: fall back to the curve's own lateral.
				x = lateral - lateral.dot(axis) * axis;
			}
			x.normalize();
			B.col(0) = x;
			B.col(1) = axis;
			B.col(2) = x.cross(axis);
			return B;
		};

		// The section at dist_along: interpolated between the authored sections around it and
		// placed on the directrix. next_dist_along is where the next section will be placed, which
		// decides how tags carry over at the last section before an authored one. Returns nullptr,
		// after logging why, when the authored sections can't be interpolated.
		const auto make_section = [&](double dist_along, double next_dist_along) -> taxonomy::geom_item::ptr {
			// the authored section before dist_along, or at it when it is the first: the one whose
			// successor is the first at or after dist_along (longitudes ends with infinity)
			const auto profile_index = std::lower_bound(longitudes.begin() + 1, longitudes.end(), dist_along) - 1;

			const bool is_last_placement_of_this_profile = profile_index + 1 >= longitudes.end() ? false : (next_dist_along > *(profile_index + 1));

			auto relative_dist_along = (dist_along - *profile_index) / (*(profile_index + 1) - *profile_index);
			const auto& profile_a = cross_sections[std::distance(longitudes.begin(), profile_index)].section_geometry;
			const auto& offset_a = cross_sections[std::distance(longitudes.begin(), profile_index)].offset;
			const auto& rotation_a = cross_sections[std::distance(longitudes.begin(), profile_index)].rotation;
			const auto& ref_direction_a = cross_sections[std::distance(longitudes.begin(), profile_index)].ref_direction;

			taxonomy::geom_item::ptr interpolated = nullptr;

			// Only interpolate if:
			//  - there is a profile ahead of us, and
			//  - we're not exactly at the location of the current profile or whether there is an offset involved
			bool should_interpolate =
				(profile_index + 1 < longitudes.end()) &&
				(relative_dist_along >= 1.e-9 || offset_a.cwiseAbs().maxCoeff() > 0. || rotation_a);

			// When both bracketing placements ask for the same orientation, drive the sweep
			// frame from it directly (relative to the curve). When they disagree, keep the
			// sweep frame on the curve and fold each section's own orientation into its
			// profile points via section_basis_a / section_basis_b so the ends still land
			// exactly as authored without twisting the body between them.
			std::optional<Eigen::Matrix3d> interpolated_rotation;
			std::optional<Eigen::Vector3d> interpolated_ref_direction;
			Eigen::Matrix3d section_basis_a = Eigen::Matrix3d::Identity();
			Eigen::Matrix3d section_basis_b = Eigen::Matrix3d::Identity();

			if (should_interpolate) {
				taxonomy::geom_item::ptr profile_b;
				Eigen::Vector3d offset_b;
				std::optional<Eigen::Matrix3d> rotation_b;
				std::optional<Eigen::Vector3d> ref_direction_b;
				if ((profile_index + 1 < longitudes.end())) {
					profile_b = cross_sections[std::distance(longitudes.begin(), profile_index) + 1].section_geometry;
					offset_b = cross_sections[std::distance(longitudes.begin(), profile_index) + 1].offset;
					rotation_b = cross_sections[std::distance(longitudes.begin(), profile_index) + 1].rotation;
					ref_direction_b = cross_sections[std::distance(longitudes.begin(), profile_index) + 1].ref_direction;
				} else {
					profile_b = profile_a;
					offset_b = offset_a;
					rotation_b = rotation_a;
					ref_direction_b = ref_direction_a;
				}

				{
					std::vector<taxonomy::loop::ptr> loops_a, loops_b;

					if (profile_a->kind() == taxonomy::FACE) {
						interpolated = taxonomy::make<taxonomy::face>();

						auto profile_a_f = std::static_pointer_cast<taxonomy::face>(profile_a);
						auto profile_b_f = std::static_pointer_cast<taxonomy::face>(profile_b);

						if (profile_a_f->children.size() != profile_b_f->children.size()) {
							logger.warning("GEO", 41, "Mismatching number of face boundaries: " +
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
					if (rotation_a == rotation_b) {
						// Same orientation on both placements (including both absent): the
						// sweep frame carries it, built against the curve just below.
						interpolated_rotation = rotation_a;
						interpolated_ref_direction = ref_direction_a;
					} else if (rotation_a || rotation_b) {
						// The two placements disagree -- in practice they share an Axis but
						// only one carries a RefDirection (a raked end against a square run).
						// Drive the sweep frame from the shared Axis with the profile normal
						// on the curve tangent -- identical to the neighbouring consistent
						// segments, so m4b stays continuous across the boundary and the body
						// never flips -- then fold each section's *own* authored orientation
						// into its profile points through section_basis_a / section_basis_b,
						// so each end cap still lands exactly as authored.
						const auto ia = static_cast<std::size_t>(std::distance(longitudes.begin(), profile_index));
						assert(ia + 1 < section_directrix_frames.size());
						const std::optional<Eigen::Vector3d> no_ref;
						const auto base_a = profile_basis(rotation_a, no_ref, section_directrix_frames[ia]);
						const auto base_b = profile_basis(rotation_b, no_ref, section_directrix_frames[ia + 1]);
						section_basis_a =
							base_a.transpose() *
							profile_basis(rotation_a, ref_direction_a, section_directrix_frames[ia]);
						section_basis_b =
							base_b.transpose() *
							profile_basis(rotation_b, ref_direction_b, section_directrix_frames[ia + 1]);
						interpolated_rotation = rotation_a ? rotation_a : rotation_b;
						interpolated_ref_direction = no_ref;
					}

					taxonomy::loop::ptr w1, w2;

					for (auto tmp_ : boost::combine(loops_a, loops_b)) {
						boost::tie(w1, w2) = tmp_;
						if (w1->closed != w2->closed) {
							logger.warning("GEO", 43, "Mismatching closed property on loops", inst);
							return nullptr;
                        }

						if (w1->tags.has_value() != w2->tags.has_value()) {
							logger.warning("GEO", 44, "Mismatching availability tags on loops", inst);
							return nullptr;
                        }

						if (w1->tags) {
							// check uniqueness
                            std::set<std::string> tags_seen;
                            for (const auto& t : *w1->tags) {
								if (tags_seen.find(t) != tags_seen.end()) {
									logger.warning("GEO", 45, "Duplicate tag '" + t + "' on loft profile", inst);
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
                                    logger.warning("GEO", 46, "Duplicate tag '" + t + "' on loft profile", inst);
                                    return nullptr;
                                }
                                tags_seen.insert(t);
                            }
                        }

						if (!w1->tags) {
							auto loop = interpolate_edges(w1, w2, section_basis_a, section_basis_b,
								interpolated_offset, relative_dist_along, settings);
							if (auto face = std::dynamic_pointer_cast<taxonomy::face>(interpolated)) {
								face->children.push_back(loop);
							} else {
								loop->matrix = interpolated->matrix;
								interpolated = loop;
							}
							continue;
						}

						// Tagged linear profiles keep their existing vertex/tag correspondence.
						std::map<std::string, taxonomy::point3::ptr> tag_to_point_on_w1, tag_to_point_on_w2;

						auto loop_to_points = [](const taxonomy::loop::ptr& loop, const std::optional<std::vector<std::string>>& input_tags) -> std::pair<std::vector<taxonomy::point3::ptr>, std::vector<std::set<std::string>>> {
                            std::vector<taxonomy::point3::ptr> points;
                            std::vector<std::set<std::string>> tags;
                            std::vector<std::string>::const_iterator tag_it;

							if (!loop->closed.value_or(false)) {
                                points = {std::get<taxonomy::point3::ptr>(loop->children[0]->start)};
                                if (input_tags) {
                                    tags = {{input_tags->front()}};
                                    tag_it = ++input_tags->begin();
                                }
							}
							for (auto& e : loop->children) {
								const auto& p1 = std::get<taxonomy::point3::ptr>(e->start);
								const auto& p2 = std::get<taxonomy::point3::ptr>(e->end);
                                if (input_tags && p1->ccomponents() == p2->ccomponents()) {
                                    tags.back().insert(*tag_it);
                                    ++tag_it;
                                } else {
                                    points.push_back(p2);
                                    if (input_tags) {
                                        tags.emplace_back();
                                        tags.back().insert(*tag_it);
                                        ++tag_it;
                                    }
                                }
							}
                            if (!input_tags) {
                                if (loop->closed.value_or(false)) {
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
                                    logger.warning("GEO", 47, "No matching tags found on loft profiles: " + join_tags(p1_tags) + " not in " + join_tags(w2_tags_combined), inst);
									return nullptr;
								}
							}

							for (auto& p2_tags : w2_tags) {
                                if (!has_intersection(p2_tags, w1_tags_combined)) {
                                    logger.warning("GEO", 48, "No matching tags found on loft profiles: " + join_tags(p2_tags) + " not in " + join_tags(w1_tags_combined), inst);
                                    return nullptr;
								}
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

                                const auto& tagged_point_on_w1 = tag_to_point_on_w1[t];
                                const auto& tagged_point_on_w2 = tag_to_point_on_w2[t];

                                const Eigen::Vector3d rebased_w1 = section_basis_a * tagged_point_on_w1->ccomponents();
                                const Eigen::Vector3d rebased_w2 = section_basis_b * tagged_point_on_w2->ccomponents();
                                auto p3 = (lerp(rebased_w1, rebased_w2, relative_dist_along) + interpolated_offset).eval();

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
                        }

						/*
						// This is handled in the loop_to_points() function above
                        if (!points.empty()) {
							if (!w1->closed.value_or(true) && !w2->closed.value_or(true)) {
                                // open polygon, add last point
                                auto& p1 = std::get<taxonomy::point3::ptr>(w1->children.back()->end);
                                auto& p2 = std::get<taxonomy::point3::ptr>(w2->children.back()->end);
                                auto p3 = (lerp(p1->ccomponents(), p2->ccomponents(), relative_dist_along) + interpolated_offset).eval();
                                points.push_back(taxonomy::make<taxonomy::point3>(p3));
                            } else if (w1->closed.value_or(true) && w2->closed.value_or(true)) {
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
				std::wcout << "#" << pwf->instance.data().id() << " " << dist_along << ": " << m4.col(3).row(2).value() << std::endl;
			}*/

			// Sweep frame at this station: the profile orientation asked for by the
			// (consistent) placements, built against the curve here so it follows the
			// directrix. Falls back to the plain curve frame (lateral, up, tangent) when
			// no placement carries direction vectors. Inconsistent placements keep this
			// on the curve and are reconciled through section_basis_a / section_basis_b.
			Eigen::Matrix4d m4b = Eigen::Matrix4d::Identity();
			m4b.block<3, 3>(0, 0) = profile_basis(interpolated_rotation, interpolated_ref_direction, m4);
			m4b.col(3).head<3>() = m4.col(3).head<3>();

			taxonomy::geom_item::ptr section = interpolated;
			if (!section) {
				if (profile_a->kind() == taxonomy::FACE) {
					section = std::static_pointer_cast<taxonomy::face>(taxonomy::item::ptr(profile_a->clone_()));
				} else {
					section = std::static_pointer_cast<taxonomy::loop>(taxonomy::item::ptr(profile_a->clone_()));
				}
				if (profile_a->matrix) {
					section->matrix = taxonomy::matrix4::ptr(profile_a->matrix->clone_());
				}
			}
			section->instance = profile_a->instance;
			section->surface_style = profile_a->surface_style;
			section->orientation = profile_a->orientation;
			if (!section->matrix) {
				// @todo should this not be initialized by default? matrix4 already has a 'lazy identity' mechanism.
				section->matrix = taxonomy::make<taxonomy::matrix4>();
			}
			auto m = (m4b * section->matrix->ccomponents()).eval();
			section->matrix->components() = m;
			return section;
		};

		// Sections go at every span boundary of the directrix and every authored section, and are
		// added between them until the loft follows the interpolated sections within the deflection
		// settings (see deflection_samples): a straight between sections that differ at most by
		// their offset needs only its ends, a changing profile or a bend needs more.
		std::vector<double> boundaries{start, end};
		for (double u : evaluator.boundaries()) {
			if (start < u && u < end) {
				boundaries.push_back(u);
			}
		}
		for (const auto& cs : cross_sections) {
			if (start < cs.dist_along && cs.dist_along < end) {
				boundaries.push_back(cs.dist_along);
			}
		}
		bool failed = false;
		const auto samples = deflection_samples(
			boundaries,
			[&](double u) {
				sampled_section sampled{evaluator.evaluate(u).col(3).head<3>(), {}};
				if (!failed) {
					if (auto section = make_section(u, std::numeric_limits<double>::infinity())) {
						sampled.loops = section_points(section);
					} else {
						failed = true;
					}
				}
				return sampled;
			},
			settings.get<ifcopenshell::geom::settings::MesherLinearDeflection>().get(),
			settings.get<ifcopenshell::geom::settings::MesherAngularDeflection>().get(),
			settings.get<ifcopenshell::geom::settings::Precision>().get());
		if (failed) {
			return nullptr;
		}

		for (size_t i = 0; i < samples.size(); ++i) {
			auto section = make_section(samples[i], i + 1 < samples.size() ? samples[i + 1] : std::numeric_limits<double>::infinity());
			if (!section) {
				return nullptr;
			}
			loft->children.push_back(section);
		}
	}

	return loft;
}
