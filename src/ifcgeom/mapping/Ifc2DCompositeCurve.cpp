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

#ifdef SCHEMA_HAS_Ifc2DCompositeCurve
// Ifc2DCompositeCurve is an IfcCompositeCurve constrained to 2D (IFC2X3 only).
// It inherits from IfcCompositeCurve and has the same attributes.
// The implementation delegates to the IfcCompositeCurve mapping since
// the underlying geometry processing is identical.
taxonomy::ptr mapping::map_impl(const IfcSchema::Ifc2DCompositeCurve* inst) {
	// Delegate to the IfcCompositeCurve implementation via upcasting
	// Ifc2DCompositeCurve is semantically identical to IfcCompositeCurve
	// but constrained to be defined in 2D coordinate space
	auto loop = taxonomy::make<taxonomy::loop>();

	IfcSchema::IfcCompositeCurveSegment::list::ptr segments = inst->Segments();

	for (auto& segment : *segments) {
		if (segment->ParentCurve()->as<IfcSchema::IfcLine>()) {
			Logger::Notice("Infinite IfcLine used as ParentCurve of segment, treating as a segment", segment);
			double u0 = 0.0;
			double u1 = segment->ParentCurve()->as<IfcSchema::IfcLine>()->Dir()->Magnitude() * length_unit_;
			if (u1 < settings_.get<settings::Precision>().get()) {
				Logger::Warning("Segment length below tolerance", segment);
			}

			auto e = taxonomy::make<taxonomy::edge>();
			e->basis = map(segment->ParentCurve());
			e->start = u0;
			e->end = u1;
			e->curve_sense.reset(segment->SameSense());

			loop->children.push_back(e);
		}
		else {
			auto crv = map(segment->ParentCurve());
			if (crv) {
				if (!segment->SameSense()) {
					crv->reverse();
				}
				if (crv->kind() == taxonomy::EDGE) {
					auto ecrv = taxonomy::cast<taxonomy::edge>(crv);
					loop->children.push_back(ecrv);
				} else if (crv->kind() == taxonomy::LOOP) {
					for (auto& s : taxonomy::cast<taxonomy::loop>(crv)->children) {
						loop->children.push_back(s);
					}
				} else if ((crv->kind() == taxonomy::CIRCLE || crv->kind() == taxonomy::ELLIPSE) && segments->size() == 1) {
					// A circle or ellipse segment is a full circle/ellipse, only possible when it is the only segment
					std::shared_ptr<taxonomy::edge> e = std::make_shared<taxonomy::edge>();
					e->basis = crv;
					e->start = 0.0;
					e->end = 2.0 * boost::math::constants::pi<double>();
					loop->children.push_back(e);
				} else {
					Logger::Warning("Unexpected segment type", segment);
					return nullptr;
				}
			}
		}
	}

	aggregate_of_instance::ptr profile = inst->file_->getInverse(inst->id(), &IfcSchema::IfcProfileDef::Class(), -1);
	const bool force_close = profile && profile->size() > 0;
	loop->closed = force_close;
	loop->instance = inst;
	return loop;
}
#endif
