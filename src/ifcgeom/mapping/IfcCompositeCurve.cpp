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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCompositeCurve* inst) {
	auto loop = taxonomy::make<taxonomy::loop>();
	std::vector<taxonomy::piecewise_function::ptr> pwfs;

#ifdef SCHEMA_HAS_IfcSegment
	// 4x3
	IfcSchema::IfcSegment::list::ptr segments = inst->Segments();
#else
	IfcSchema::IfcCompositeCurveSegment::list::ptr segments = inst->Segments();
#endif
	
	for (auto& segment : *segments) {
		if (segment->as<IfcSchema::IfcCompositeCurveSegment>() && segment->as<IfcSchema::IfcCompositeCurveSegment>()->ParentCurve()->as<IfcSchema::IfcLine>()) {
			Logger::Notice("Infinite IfcLine used as ParentCurve of segment, treating as a segment", segment);
			double u0 = 0.0;
			double u1 = segment->as<IfcSchema::IfcCompositeCurveSegment>()->ParentCurve()->as<IfcSchema::IfcLine>()->Dir()->Magnitude() * length_unit_;
			if (u1 < settings_.get<settings::Precision>().get()) {
				Logger::Warning("Segment length below tolerance", segment);
			}

			auto e = taxonomy::make<taxonomy::edge>();
			e->basis = map(segment->as<IfcSchema::IfcCompositeCurveSegment>()->ParentCurve());
			e->start = u0;
			e->end = u1;
			e->curve_sense.reset(segment->as<IfcSchema::IfcCompositeCurveSegment>()->SameSense());

			loop->children.push_back(e);
		}
		else if (segment->as<IfcSchema::IfcCompositeCurveSegment>()) {
			auto crv = map(segment->as<IfcSchema::IfcCompositeCurveSegment>()->ParentCurve());
			if (crv) {
				if (!segment->as<IfcSchema::IfcCompositeCurveSegment>()->SameSense()) {
					crv->reverse();
				}
				if (crv->kind() == taxonomy::EDGE) {
					auto ecrv = taxonomy::cast<taxonomy::edge>(crv);
					loop->children.push_back(ecrv);
				}
				else if (crv->kind() == taxonomy::LOOP) {
					for (auto& s : taxonomy::cast<taxonomy::loop>(crv)->children) {
						loop->children.push_back(s);
					}
				}
			}
		}
#ifdef SCHEMA_HAS_IfcCurveSegment
		else if (segment->as<IfcSchema::IfcCurveSegment>()) {
			// @todo check that we don't get a mixture of implicit and explicit definitions
			auto crv = map(segment->as<IfcSchema::IfcCurveSegment>());
			if (crv && crv->kind() == taxonomy::LOOP) {
				for (auto& s : taxonomy::cast<taxonomy::loop>(crv)->children) {
					loop->children.push_back(s);
				}
			}
			else if (crv && crv->kind() == taxonomy::PIECEWISE_FUNCTION) {
            pwfs.push_back(taxonomy::cast<taxonomy::piecewise_function>(crv));
			} else if (!crv) {
				return nullptr;
			}
		}
#endif
	}

	if (pwfs.empty()) {
		aggregate_of_instance::ptr profile = inst->file_->getInverse(inst->id(), &IfcSchema::IfcProfileDef::Class(), -1);
		const bool force_close = profile && profile->size() > 0;
		loop->closed = force_close;
		loop->instance = inst;
		return loop;
	}
	else {
      auto pwf = taxonomy::make<taxonomy::piecewise_function>(0.0,pwfs,&settings_,inst);
		return pwf;
	}
}

/*

#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <TopoDS_Wire.hxx>
#include <TopTools_ListOfShape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include "mapping.h"
#include "../ifcgeom_schema_agnostic/wire_builder.h"

#define _USE_MATH_DEFINES
#define mapping POSTFIX_SCHEMA(mapping)

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCompositeCurve* l, TopoDS_Wire& wire) {


	TopTools_ListOfShape converted_segments;

	for (auto it = segments->begin(); it != segments->end(); ++it) {

		if (!(*it)->declaration().is(IfcSchema::IfcCompositeCurveSegment::Class())) {
			Logger::Error("Not implemented", *it);
			return false;
		}

		IfcSchema::IfcCurve* curve = ((IfcSchema::IfcCompositeCurveSegment*)(*it))->ParentCurve();

		// The type of ParentCurve is IfcCurve, but the documentation says:
		// ParentCurve: The *bounded curve* which defines the geometry of the segment.
		// At least let's exclude IfcLine as an infinite linear segment
		// definitely does not make any sense.
		TopoDS_Wire segment;

		if (curve->as<IfcSchema::IfcLine>()) {
			Logger::Notice("Infinite IfcLine used as ParentCurve of segment, treating as a segment", *it);
			Handle_Geom_Curve handle;
			convert_curve(curve, handle);
			double u0 = 0.0;
			double u1 = curve->as<IfcSchema::IfcLine>()->Dir()->Magnitude() * length_unit_;
			if (u1 < getValue(GV_PRECISION)) {
				Logger::Warning("Segment length below tolerance", *it);
			}
			BRepBuilderAPI_MakeEdge me(handle, u0, u1);
			if (me.IsDone()) {
				BRep_Builder B;
				B.MakeWire(segment);
				B.Add(segment, me.Edge());
			}
		} else if (!convert_wire(curve, segment)) {
			const bool failed_on_purpose = curve->as<IfcSchema::IfcPolyline>() && !segment.IsNull();
			Logger::Message(failed_on_purpose ? Logger::LOG_WARNING : Logger::LOG_ERROR, "Failed to convert curve:", curve);
			continue;
		}

		if (!((IfcSchema::IfcCompositeCurveSegment*)(*it))->SameSense()) {
			segment.Reverse();
		}

		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(segment, getValue(GV_PRECISION), TopAbs_WIRE);

		converted_segments.Append(segment);

	}

	if (converted_segments.Extent() == 0) {
		Logger::Message(Logger::LOG_ERROR, "No segment successfully converted:", l);
		return false;
	}

	BRepBuilderAPI_MakeWire w;
	TopoDS_Vertex wire_first_vertex, wire_last_vertex, edge_first_vertex, edge_last_vertex;

	TopTools_ListIteratorOfListOfShape it(converted_segments);

	aggregate_of_instance::ptr profile = inst->data().getInverse(&IfcSchema::IfcProfileDef::Class(), -1);
	const bool force_close = profile && profile->size() > 0;

	util::wire_builder bld(getValue(GV_PRECISION), l);
	util::shape_pair_enumerate(it, bld, force_close);
	wire = bld.wire();

	return true;
}

*/