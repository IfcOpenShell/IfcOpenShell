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
using namespace ifcopenshell::geom;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCompositeCurve& inst) {
	auto loop = taxonomy::make<taxonomy::loop>();
	taxonomy::piecewise_function::span_list spans;

#ifdef SCHEMA_HAS_IfcSegment
	// 4x3
	std::vector<IfcSchema::IfcSegment> segments = inst.Segments();
#else
	std::vector<IfcSchema::IfcCompositeCurveSegment> segments = inst.Segments();
#endif

	for (auto& segment : segments) {
		if (segment.as<IfcSchema::IfcCompositeCurveSegment>() && segment.as<IfcSchema::IfcCompositeCurveSegment>().ParentCurve().as<IfcSchema::IfcLine>()) {
			logger_.notice("GEO", 238, "Infinite IfcLine used as ParentCurve of segment, treating as a segment", segment);
			double u0 = 0.0;
			double u1 = segment.as<IfcSchema::IfcCompositeCurveSegment>().ParentCurve().as<IfcSchema::IfcLine>().Dir().Magnitude() * length_unit_;
			if (u1 < settings_.get<settings::Precision>().get()) {
				logger_.warning("GEO", 239, "Segment length below tolerance", segment);
			}

			auto e = taxonomy::make<taxonomy::edge>();
			e->basis = map(segment.as<IfcSchema::IfcCompositeCurveSegment>().ParentCurve());
			e->start = u0;
			e->end = u1;
			e->curve_sense.emplace(segment.as<IfcSchema::IfcCompositeCurveSegment>().SameSense());

			loop->children.push_back(e);
		}
		else if (segment.as<IfcSchema::IfcCompositeCurveSegment>()) {
			auto crv = map(segment.as<IfcSchema::IfcCompositeCurveSegment>().ParentCurve());
			if (crv) {
				if (!segment.as<IfcSchema::IfcCompositeCurveSegment>().SameSense()) {
					crv->reverse();
				}
				if (crv->kind() == taxonomy::EDGE) {
					auto ecrv = taxonomy::cast<taxonomy::edge>(crv);
					loop->children.push_back(ecrv);
				} else if (crv->kind() == taxonomy::LOOP) {
					for (auto& s : taxonomy::cast<taxonomy::loop>(crv)->children) {
						loop->children.push_back(s);
					}
				} else if ((crv->kind() == taxonomy::CIRCLE || crv->kind() == taxonomy::ELLIPSE) && segments.size() == 1) {
					// A circle or ellipse segment is a full circle/ellipse, only possible when it is the only segment
					std::shared_ptr<taxonomy::edge> e = std::make_shared<taxonomy::edge>();
					e->basis = crv;
					e->start = 0.0;
					e->end = 2.0 * boost::math::constants::pi<double>();
					loop->children.push_back(e);
				} else {
					logger_.warning("GEO", 240, "Unexpected segment type", segment);
					return nullptr;
				}
			}
		}
#ifdef SCHEMA_HAS_IfcCurveSegment
		else if (segment.as<IfcSchema::IfcCurveSegment>()) {
			// @todo check that we don't get a mixture of implicit and explicit definitions
			auto crv = map(segment.as<IfcSchema::IfcCurveSegment>());
			if (crv && crv->kind() == taxonomy::LOOP) {
				for (auto& s : taxonomy::cast<taxonomy::loop>(crv)->children) {
					loop->children.push_back(s);
				}
			} else if (auto fi = taxonomy::dcast<taxonomy::function_item>(crv); crv && fi /*crv->kind() == taxonomy::FUNCTION_ITEM*/) {
				// crv->kind() is polymorphic and the kind of the actual function_item is returned. PWF can have spans of any FUNCTION_ITEM
				// for this reason, a dynamic cast is used and if crv is a function_item it is added to the span
            spans.push_back(fi);
         } else if (!crv) {
				return nullptr;
			}
		}
#endif
	}

	if (spans.empty()) {
		std::vector<express::entity> profile = inst.file()->get_inverse(inst.id(), &IfcSchema::IfcProfileDef::Class(), -1);
        const bool force_close = !profile.empty();
		loop->closed = force_close;
		loop->instance = inst;
		return loop;
	}
	else {
      auto pwf = taxonomy::make<taxonomy::piecewise_function>(0.0,spans,inst);
		return pwf;
	}
}
