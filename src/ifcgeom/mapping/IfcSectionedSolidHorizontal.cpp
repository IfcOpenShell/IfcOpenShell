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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#include "../../ifcgeom/profile_helper.h"

#include <boost/range/combine.hpp>

#ifdef SCHEMA_HAS_IfcSectionedSolidHorizontal

namespace {
	// std::lerp when upgrading to C++ 20
	template <typename T>
	T lerp(const T& a, const T& b, double t) {
		return a + t * (b - a);
	}

	struct cross_section {
		double dist_along;
		taxonomy::face::ptr section_geometry;
		Eigen::Vector3d offset;

		bool operator <(const cross_section& other) const {
			return dist_along < other.dist_along;
		}
	};
}

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcSectionedSolidHorizontal* inst) {
	std::vector<cross_section> cross_sections;

	auto dir = map(inst->Directrix());
	auto pwf = taxonomy::dcast<taxonomy::piecewise_function>(dir);
	if (!pwf) {
		// Only implement on alignment curves
        Logger::Warning("IfcSectionedSolidHorizontal is only implemented for piecewise function Directrix curves", inst);
        return nullptr;
	}

	{	
	auto css = inst->CrossSections();
	auto csps = inst->CrossSectionPositions();
	std::vector<taxonomy::face::ptr> faces;

	// The PointByDistanceExpressesions are factored out into (a) a cartesian offset relative to the
	// reference frame along a certain curve location (b) the longitude.

	// The longitudes determine the range of the sweep and the offsets are interpolated in between
	// sweep segments. 
	std::vector<Eigen::Vector3d> profile_offsets;
	std::vector<double> longitudes;

	for (auto& cs : *css) {
		faces.push_back(std::move(taxonomy::cast<taxonomy::face>(map(cs))));
	}
#ifdef SCHEMA_HAS_IfcPointByDistanceExpression
	for (auto& csp : *csps) {
		auto pbde = csp->Location()->as<IfcSchema::IfcPointByDistanceExpression>(true);

		longitudes.push_back(*pbde->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>(true) * length_unit_);

		// Corresponds to the profile X, Y directions (hopefully).
		Eigen::Vector3d po(
			pbde->OffsetLateral().get_value_or(0.),
			// @todo I don't understand whether vertical is an offset relative to the tangent plane or to the global XY plane
			pbde->OffsetVertical().get_value_or(0.),
			0.
		);

		profile_offsets.push_back(po);
	}
#else
	return nullptr;
#endif
	if (faces.size() != profile_offsets.size()) {
		Logger::Warning("Expected CrossSections and CrossSectionPositions to be equal length, but got " + std::to_string(faces.size()) + " and " + std::to_string(profile_offsets.size()) + " respectively", inst);
		return nullptr;
	}
	if (faces.size() < 2) {
		Logger::Warning("Expected at least two cross sections, but got " + std::to_string(faces.size()), inst);
		return nullptr;
	}

	for (size_t i = 0; i < faces.size(); ++i) {
		cross_sections.push_back({ longitudes[i], faces[i], profile_offsets[i] });
	}
	}

	std::sort(cross_sections.begin(), cross_sections.end());

	auto loft = taxonomy::make<taxonomy::loft>();
	// @todo intialize as default
	loft->axis = nullptr;

	// @todo currently only the case is handled where directrix returns a piecewise_function
	// @todo this "if" statement is not really required because the function returns at the start if the Directrix is not a piecewise function
	if (pwf) {
		double start = std::max(0., cross_sections.front().dist_along);
		double end = std::min(pwf->length(), cross_sections.back().dist_along);

		if (end - start < 1.e-9) {
			Logger::Warning("Empty sweep domain with start at " + std::to_string(cross_sections.front().dist_along) + " end at " + std::to_string(cross_sections.back().dist_along) + " and curve domain length " + std::to_string(pwf->length()), inst);
			return nullptr;
		}

		auto curve_length = end - start;
		auto param_type = settings_.get<ifcopenshell::geometry::settings::PiecewiseStepType>().get();
		auto param = settings_.get<ifcopenshell::geometry::settings::PiecewiseStepParam>().get();
		size_t num_steps = 0;
		if (param_type == ifcopenshell::geometry::settings::PiecewiseStepMethod::MAXSTEPSIZE) {
			// parameter is max step size
			num_steps = (size_t) std::ceil(curve_length / param);
		} else {
			// parameter is minimum number of steps
			num_steps = (size_t) std::ceil(param);
		}
		std::vector<double> longitudes;
		for (auto& x : cross_sections) {
			longitudes.push_back(x.dist_along);
		}
		longitudes.push_back(std::numeric_limits<double>::infinity());
		auto profile_index = longitudes.begin();
		for (size_t i = 0; i <= num_steps; ++i) {
			auto dist_along = start + curve_length / num_steps * i;
			while (dist_along > *(profile_index+1)) {
				profile_index++;
				if (profile_index == longitudes.end()) {
					// @todo handle this? 
				}
			}
			
			auto relative_dist_along = (dist_along - *profile_index) / (*(profile_index+1) - *profile_index);
			const auto& profile_a = cross_sections[std::distance(longitudes.begin(), profile_index)].section_geometry;
			const auto& offset_a = cross_sections[std::distance(longitudes.begin(), profile_index)].offset;
			
			taxonomy::face::ptr interpolated = nullptr;

			// Only interpolate if:
			//  - there is a profile ahead of us, and
			//  - we're not exactly at the location of the current profile or whether there is an offset involved.
			bool should_interpolate =
				(profile_index + 1 < longitudes.end()) &&
				(relative_dist_along >= 1.e-9 || offset_a.cwiseAbs().maxCoeff() > 0.);

			if (should_interpolate) {
				taxonomy::face::ptr profile_b;
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
					if (profile_a->children.size() != profile_b->children.size()) {
						Logger::Warning("Mismatching number of face boundaries: " +
							std::to_string(profile_a->children.size()) + " vs " +
							std::to_string(profile_b->children.size()),
							inst
						);
						return nullptr;
					}
					interpolated = taxonomy::make<taxonomy::face>();
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
					for (auto tmp_ : boost::combine(profile_a->children, profile_b->children)) {
						boost::tie(w1, w2) = tmp_;
						if (w1->children.size() != w2->children.size()) {
							Logger::Warning("Mismatching number of edges for face boundary: " +
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
						interpolated->children.push_back(polygon_from_points(points));
					}
				}
			}

			auto m4 = pwf->evaluate(dist_along);
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
				loft->children.push_back(taxonomy::face::ptr(profile_a->clone_()));
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

#endif
