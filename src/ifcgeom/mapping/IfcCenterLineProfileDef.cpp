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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCenterLineProfileDef* inst) {
	return nullptr;

	/*
	const double d = inst->Thickness() * length_unit_ / 2.;
	auto f = taxonomy::make<taxonomy::face>();
	auto ofc = taxonomy::make<taxonomy::offset_curve>();
	ofc->basis = map(inst->Curve());
	ofc->offset = d;
	// @todo
	// f->children.push_back(ofc);
	return f;
	*/

	// @todo we still need to handle this in the geometry libraries

	/*
	TopoDS_Wire wire;
	if (!convert_wire(inst->Curve(), wire)) return false;

	// BRepOffsetAPI_MakeOffset insists on creating circular arc
	// segments for joining the curves that constitute the center
	// line. This is probably not in accordance with the IFC spec.
	// Although it does not specify a method to join segments
	// explicitly, it does dictate 'a constant thickness along the
	// curve'. Therefore for simple singular wires a quick
	// alternative is provided that uses a straight join.

	TopExp_Explorer exp(wire, TopAbs_EDGE);
	TopoDS_Edge edge = TopoDS::Edge(exp.Current());
	exp.Next();

	if (!exp.More()) {
		double u1, u2;
		Handle(Geom_Curve) curve = BRep_Tool::Curve(edge, u1, u2);

		Handle(Geom_TrimmedCurve) trim = new Geom_TrimmedCurve(curve, u1, u2);

		Handle(Geom_OffsetCurve) c1 = new Geom_OffsetCurve(trim,  d, gp::DZ());
		Handle(Geom_OffsetCurve) c2 = new Geom_OffsetCurve(trim, -d, gp::DZ());

		gp_Pnt c1a, c1b, c2a, c2b;
		c1->D0(c1->FirstParameter(), c1a);
		c1->D0(c1->LastParameter(), c1b);
		c2->D0(c2->FirstParameter(), c2a);
		c2->D0(c2->LastParameter(), c2b);

		BRepBuilderAPI_MakeWire mw;
		mw.Add(BRepBuilderAPI_MakeEdge(c1));
		mw.Add(BRepBuilderAPI_MakeEdge(c1a, c2a));
		mw.Add(BRepBuilderAPI_MakeEdge(c2));
		mw.Add(BRepBuilderAPI_MakeEdge(c2b, c1b));
		
		face = BRepBuilderAPI_MakeFace(mw.Wire());
	} else {
		BRepOffsetAPI_MakeOffset offset(BRepBuilderAPI_MakeFace(gp_Pln(gp::Origin(), gp::DZ())));
		offset.AddWire(wire);
		offset.Perform(d);
		face = BRepBuilderAPI_MakeFace(TopoDS::Wire(offset));
	}
	return true;
	*/
}
