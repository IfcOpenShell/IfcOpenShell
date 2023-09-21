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

#ifdef SCHEMA_HAS_IfcCurveSegment

#include "../profile_helper.h"

#include <boost/mpl/vector.hpp>
#include <boost/mpl/for_each.hpp>

typedef boost::mpl::vector<
	IfcSchema::IfcLine
#ifdef SCHEMA_HAS_IfcClothoid
	, IfcSchema::IfcClothoid
#endif
> curve_seg_types;

class curve_segment_evaluator {
private:
	double length_unit_;
	double start_;
	double length_;
	IfcSchema::IfcCurve* curve_;

	std::optional<std::function<Eigen::Vector3d(double)>> eval_;

public:
	// First constructor, takes parameters from IfcCurveSegment
	curve_segment_evaluator(double length_unit, IfcSchema::IfcCurve* curve, IfcSchema::IfcCurveMeasureSelect* st, IfcSchema::IfcCurveMeasureSelect* le)
		: length_unit_(length_unit)
		, curve_(curve)
	{
		// @todo in IFC4X3_ADD2 this needs to be length measure
		
		if (!st->as<IfcSchema::IfcLengthMeasure>() || !le->as<IfcSchema::IfcLengthMeasure>()) {
			// @nb Parameter values are forbidden in the specification until parametrization is provided for all spirals
			throw std::runtime_error("Unsupported curve measure type");
		}
		
		start_ = *st->as<IfcSchema::IfcLengthMeasure>() * length_unit;
		length_ = *le->as<IfcSchema::IfcLengthMeasure>() * length_unit;
	}

#ifdef SCHEMA_HAS_IfcClothoid
	// Then initialize Function(double) -> Vector3, by means of IfcCurve subtypes
	void operator()(IfcSchema::IfcClothoid* c) {
		// @todo verify
		auto L = start_ + length_;
		auto A = c->ClothoidConstant();
		auto R = A * A / L;
		auto RL = R * L;

		eval_ = [RL](double u) {
			auto xterm_1 = u;
			auto xterm_2 = std::pow(u, 5) / (40 * std::pow(RL, 2));
			auto xterm_3 = std::pow(u, 9) / (3456 * std::pow(RL, 4));
			auto xterm_4 = std::pow(u, 13) / (599040 * std::pow(RL, 6));
			auto x = xterm_1 - xterm_2 + xterm_3 - xterm_4;

			auto yterm_1 = std::pow(u, 3) / (6 * RL);
			auto yterm_2 = std::pow(u, 7) / (336 * std::pow(RL, 3));
			auto yterm_3 = std::pow(u, 11) / (42240 * std::pow(RL, 5));
			auto yterm_4 = std::pow(u, 15) / (9676800 * std::pow(RL, 7));
			auto y = yterm_1 - yterm_2 + yterm_3 - yterm_4;

			return Eigen::Vector3d(x, y, 0.);
		};
	}
#endif

	// Another IfcCurve subtype
	void operator()(IfcSchema::IfcLine*) {
		throw std::runtime_error("not implemented");
	}

	// Take the boost::type value from mpl::for_each and test it against our curve instance
	template <typename T>
	void operator()(boost::type<T>) {
		if (curve_->as<T>()) {
			(*this)(curve_->as<T>());
		}
	}

	// Then, with function populated based on IfcCurve subtype, we can evaluate to points
	Eigen::Vector3d operator()(double u) {
		if (eval_) {
			return (*eval_)((u + start_) * length_unit_);
		} else {
			throw std::runtime_error(curve_->declaration().name() + " not implemented");
		}
	}

	double length() const {
		return length_;
	}
};

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCurveSegment* inst) {
	// @todo fixed number of segments or fixed interval?
	// @todo placement

	static int NUM_SEGMENTS = 64;
	curve_segment_evaluator cse(length_unit_, inst->ParentCurve(), inst->SegmentStart(), inst->SegmentLength());
	boost::mpl::for_each<curve_seg_types, boost::type<boost::mpl::_>>(std::ref(cse));

	std::vector<taxonomy::point3::ptr> polygon;

	for (int i = 0; i <= NUM_SEGMENTS; ++i) {
		auto p = cse(cse.length() * i / NUM_SEGMENTS);
		polygon.push_back(taxonomy::make<taxonomy::point3>(p(0), p(1), p(2)));
	}

	return polygon_from_points(polygon);
}

#endif